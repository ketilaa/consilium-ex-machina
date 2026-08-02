package com.github.ketilaa.consilium.workitems.adapter;

import com.github.ketilaa.consilium.workitems.WorkItem;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import com.github.ketilaa.consilium.workitems.port.WorkItemRepository;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Stores a snapshot of each Work Item's event history at save time -- not a live reference --
 * so save() is an explicit persistence boundary, same as decisions.adapter.InMemoryDecisionRepository.
 */
public final class InMemoryWorkItemRepository implements WorkItemRepository {

    private final Map<WorkItemId, WorkItem> snapshots = new ConcurrentHashMap<>();

    @Override
    public void save(WorkItem workItem) {
        snapshots.put(workItem.id(), WorkItem.reconstruct(workItem.id(), workItem.events()));
    }

    @Override
    public Optional<WorkItem> findById(WorkItemId id) {
        return Optional.ofNullable(snapshots.get(id));
    }
}
