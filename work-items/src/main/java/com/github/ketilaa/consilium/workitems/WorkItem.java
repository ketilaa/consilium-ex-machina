package com.github.ketilaa.consilium.workitems;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * The aggregate root. Holds nothing mutable except its event list -- same shape as
 * {@code decisions.Decision}: every query is a fold over the history (see {@link WorkItemState}),
 * so there's no separate "current state" that could drift from the events that produced it.
 */
public final class WorkItem {

    private final WorkItemId id;
    private final List<WorkItemEvent> events;

    public WorkItem(WorkItemId id) {
        this(id, List.of());
    }

    private WorkItem(WorkItemId id, List<WorkItemEvent> history) {
        this.id = Objects.requireNonNull(id, "id");
        this.events = new ArrayList<>(history);
    }

    /** Reconstructs a Work Item from its persisted event history -- no new events are added. */
    public static WorkItem reconstruct(WorkItemId id, List<WorkItemEvent> history) {
        return new WorkItem(id, history);
    }

    public void apply(WorkItemEvent event) {
        events.add(Objects.requireNonNull(event));
    }

    public List<WorkItemEvent> events() {
        return List.copyOf(events);
    }

    public WorkItemState state() {
        return WorkItemState.fold(events);
    }

    public WorkItemId id() {
        return id;
    }
}
