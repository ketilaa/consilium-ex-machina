package com.github.ketilaa.consilium.workitems.port;

import com.github.ketilaa.consilium.workitems.WorkItem;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import java.util.Optional;

/**
 * Persists and reloads Work Items. Implementations only need to round-trip the event
 * history faithfully -- state is always re-derived by folding it (see WorkItemState), never
 * stored separately.
 */
public interface WorkItemRepository {
    void save(WorkItem workItem);

    Optional<WorkItem> findById(WorkItemId id);
}
