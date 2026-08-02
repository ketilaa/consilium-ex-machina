package com.github.ketilaa.consilium.workitems.adapter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.workitems.WorkItem;
import com.github.ketilaa.consilium.workitems.WorkItemEvent;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import com.github.ketilaa.consilium.workitems.port.WorkItemRepository;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Persists each Work Item as a JSON-lines file: one header line (just the id -- everything
 * else is derived from events), then one line per event -- same shape as
 * decisions.adapter.FileDecisionRepository.
 */
public final class FileWorkItemRepository implements WorkItemRepository {

    private final Path directory;
    private final ObjectMapper mapper = new ObjectMapper();
    private final WorkItemEventCodec codec = new WorkItemEventCodec(mapper);

    public FileWorkItemRepository(Path directory) {
        this.directory = directory;
        try {
            Files.createDirectories(directory);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public void save(WorkItem workItem) {
        ObjectNode header = mapper.createObjectNode();
        header.put("type", "Header");
        header.put("id", workItem.id().value());

        StringBuilder content = new StringBuilder();
        content.append(header).append('\n');
        for (WorkItemEvent event : workItem.events()) {
            content.append(codec.toJson(event)).append('\n');
        }

        try {
            Files.writeString(filePath(workItem.id()), content.toString());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public Optional<WorkItem> findById(WorkItemId id) {
        Path path = filePath(id);
        if (!Files.exists(path)) {
            return Optional.empty();
        }
        try {
            List<String> lines = Files.readAllLines(path);
            List<WorkItemEvent> events = new ArrayList<>();
            for (int i = 1; i < lines.size(); i++) {
                if (lines.get(i).isBlank()) {
                    continue;
                }
                events.add(codec.fromJson(mapper.readTree(lines.get(i))));
            }
            return Optional.of(WorkItem.reconstruct(id, events));
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private Path filePath(WorkItemId id) {
        return directory.resolve(id.value() + ".jsonl");
    }
}
