package com.github.ketilaa.consilium.workitems;

/**
 * An opaque reference to whoever owns a Work Item -- a human or an agent, e.g.
 * {@code "human:ketil"} or {@code "agent:architect"}. Deliberately not
 * {@code com.github.ketilaa.consilium.decisions.Role}, which is an agent persona with a
 * mandate -- a different concept from "who owns this piece of work."
 */
public record Owner(String value) {

    public Owner {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("Owner must not be blank");
        }
    }

    @Override
    public String toString() {
        return value;
    }
}
