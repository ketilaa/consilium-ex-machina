package com.github.ketilaa.consilium.decisions;

/**
 * Identifies one distinct raised concern: the role that raised it, and its position among
 * that role's concerns in this round (0-based). A role is not limited to raising exactly one
 * concern -- a single reaction can contain several distinct concerns of different kinds
 * (see {@link ItemSplitter}), each tracked, classified, and rechecked independently.
 */
public record ItemId(Role role, int index) {

    public ItemId {
        if (index < 0) {
            throw new IllegalArgumentException("index must not be negative");
        }
    }

    @Override
    public String toString() {
        return role.name() + "#" + index;
    }

    /** Parses the {@code toString()} format back -- used by the persistence codec. */
    public static ItemId parse(String text) {
        int separator = text.lastIndexOf('#');
        if (separator < 0) {
            throw new IllegalArgumentException("Not a valid ItemId: " + text);
        }
        String roleName = text.substring(0, separator);
        int index = Integer.parseInt(text.substring(separator + 1));
        return new ItemId(Roles.byName(roleName), index);
    }
}
