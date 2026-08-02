package com.github.ketilaa.consilium.workitems;

import java.util.List;

/**
 * The current derived detail of a Work Item, computed by folding its event history -- same
 * pure-projection shape as {@code decisions.DecisionState}.
 */
public record WorkItemState(
        WorkItemKind kind,
        String title,
        String description,
        WorkItemId parentId,
        Owner owner
) {

    public static WorkItemState fold(List<WorkItemEvent> events) {
        WorkItemKind kind = null;
        String title = null;
        String description = null;
        WorkItemId parentId = null;
        Owner owner = null;

        for (WorkItemEvent event : events) {
            if (event instanceof WorkItemEvent.Created created) {
                kind = created.kind();
                title = created.title();
                description = created.description();
                parentId = created.parentId();
                owner = created.owner();
            } else if (event instanceof WorkItemEvent.Retitled retitled) {
                title = retitled.newTitle();
            } else if (event instanceof WorkItemEvent.DescriptionUpdated updated) {
                description = updated.newDescription();
            } else if (event instanceof WorkItemEvent.Reparented reparented) {
                parentId = reparented.newParentId();
            }
        }

        if (kind == null) {
            throw new IllegalStateException("Work Item has no Created event");
        }

        return new WorkItemState(kind, title, description, parentId, owner);
    }
}
