package com.github.ketilaa.consilium.decisions.adapter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.OriginReference;
import com.github.ketilaa.consilium.decisions.Roles;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

/**
 * Persists each Decision as a JSON-lines file: one header line (id/title/context/category/owner/origin),
 * then one line per event, in order -- a real, readable audit trail on disk. Overwritten in
 * full on every save(); {@link Decision#events()} always returns the complete history, so
 * there's no need for incremental appends in v1.
 */
public final class FileDecisionRepository implements DecisionRepository {

    private final Path directory;
    private final ObjectMapper mapper = new ObjectMapper();
    private final DecisionEventCodec codec = new DecisionEventCodec(mapper);

    public FileDecisionRepository(Path directory) {
        this.directory = directory;
        try {
            Files.createDirectories(directory);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public void save(Decision decision) {
        ObjectNode header = mapper.createObjectNode();
        header.put("type", "Header");
        header.put("id", decision.id());
        header.put("title", decision.title());
        header.put("context", decision.context());
        header.put("category", decision.category());
        header.put("ownerRole", decision.ownerRole().name());
        header.put("origin", decision.origin().value());

        StringBuilder content = new StringBuilder();
        content.append(header).append('\n');
        for (DecisionEvent event : decision.events()) {
            content.append(codec.toJson(event)).append('\n');
        }

        try {
            Files.writeString(filePath(decision.id()), content.toString());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    @Override
    public Optional<Decision> findById(String id) {
        Path path = filePath(id);
        if (!Files.exists(path)) {
            return Optional.empty();
        }
        return Optional.of(load(path));
    }

    /**
     * A full directory scan -- v1 doesn't need an index, there's no volume yet to justify one.
     * Revisit if a real work-item module ever needs this to be fast, not just correct.
     */
    @Override
    public List<Decision> findByOrigin(OriginReference origin) {
        if (!Files.isDirectory(directory)) {
            return List.of();
        }
        try (Stream<Path> files = Files.list(directory)) {
            return files
                    .filter(path -> path.toString().endsWith(".jsonl"))
                    .map(this::load)
                    .filter(decision -> decision.origin().equals(origin))
                    .toList();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private Decision load(Path path) {
        try {
            List<String> lines = Files.readAllLines(path);
            JsonNode header = mapper.readTree(lines.get(0));
            List<DecisionEvent> events = new ArrayList<>();
            for (int i = 1; i < lines.size(); i++) {
                if (lines.get(i).isBlank()) {
                    continue;
                }
                events.add(codec.fromJson(mapper.readTree(lines.get(i))));
            }
            return Decision.reconstruct(
                    header.get("id").asText(),
                    header.get("title").asText(),
                    header.get("context").asText(),
                    header.get("category").asText(),
                    Roles.byName(header.get("ownerRole").asText()),
                    new OriginReference(header.get("origin").asText()),
                    events
            );
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private Path filePath(String id) {
        return directory.resolve(id + ".jsonl");
    }
}
