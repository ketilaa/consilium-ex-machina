package com.github.ketilaa.consilium.workitems;

/** Opaque identifier for a Work Item. */
public record WorkItemId(String value) {

    public WorkItemId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("WorkItemId must not be blank");
        }
    }

    @Override
    public String toString() {
        return value;
    }
}
