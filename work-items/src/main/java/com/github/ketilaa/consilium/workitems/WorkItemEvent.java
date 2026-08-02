package com.github.ketilaa.consilium.workitems;

/**
 * The append-only history of a Work Item -- same event-sourced shape as
 * {@code decisions.DecisionEvent}: state is always derived by folding this list
 * (see {@link WorkItemState#fold}), never stored directly.
 */
public sealed interface WorkItemEvent {

    /** {@code parentId} is null for a Work Item with no parent (e.g. a top-level Initiative). */
    record Created(WorkItemKind kind, String title, String description, WorkItemId parentId, Owner owner)
            implements WorkItemEvent {
        public Created {
            if (kind == null) {
                throw new IllegalArgumentException("kind must not be null");
            }
            requireNonBlank(title, "title");
            requireNonBlank(description, "description");
            if (owner == null) {
                throw new IllegalArgumentException("owner must not be null");
            }
        }
    }

    record Retitled(String newTitle) implements WorkItemEvent {
        public Retitled {
            requireNonBlank(newTitle, "newTitle");
        }
    }

    record DescriptionUpdated(String newDescription) implements WorkItemEvent {
        public DescriptionUpdated {
            requireNonBlank(newDescription, "newDescription");
        }
    }

    /** {@code newParentId} may be null to move a Work Item back to having no parent. */
    record Reparented(WorkItemId newParentId) implements WorkItemEvent {
    }

    private static void requireNonBlank(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(fieldName + " must not be blank");
        }
    }
}
