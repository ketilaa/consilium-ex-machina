package com.github.ketilaa.consilium.decisions;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * The aggregate root. Holds nothing mutable except its event list -- every query (current
 * status, open questions, who raised what) is a fold over that list (see {@link DecisionState}).
 * This is what makes the audit trail real: there is no separate "current state" field that
 * could drift from the history that supposedly produced it.
 *
 * <p>{@code title} is short; {@code context} carries the actual background the owner proposes
 * against -- matching proof-of-concept/decision-making/decisions.py's separate title/context
 * fields, which the first Java port of this aggregate had collapsed into title alone. Restored
 * so a Decision's context can genuinely come from wherever raised it (e.g. a Work Item's own
 * stored description) instead of being re-typed into a short title string.
 */
public final class Decision {

    private final String id;
    private final String title;
    private final String context;
    private final String category;
    private final Role ownerRole;
    private final OriginReference origin;
    private final List<DecisionEvent> events;

    public Decision(String id, String title, String context, String category, Role ownerRole, OriginReference origin) {
        this(id, title, context, category, ownerRole, origin, List.of());
    }

    private Decision(
            String id, String title, String context, String category, Role ownerRole, OriginReference origin,
            List<DecisionEvent> history
    ) {
        this.id = requireNonBlank(id, "id");
        this.title = requireNonBlank(title, "title");
        this.context = requireNonBlank(context, "context");
        this.category = requireNonBlank(category, "category");
        this.ownerRole = Objects.requireNonNull(ownerRole, "ownerRole");
        this.origin = Objects.requireNonNull(origin, "origin");
        this.events = new ArrayList<>(history);
    }

    /** Reconstructs a Decision from its persisted event history -- no new events are added. */
    public static Decision reconstruct(
            String id, String title, String context, String category, Role ownerRole, OriginReference origin,
            List<DecisionEvent> history
    ) {
        return new Decision(id, title, context, category, ownerRole, origin, history);
    }

    public void apply(DecisionEvent event) {
        events.add(Objects.requireNonNull(event));
    }

    public List<DecisionEvent> events() {
        return List.copyOf(events);
    }

    public DecisionState state() {
        return DecisionState.fold(events);
    }

    public String id() {
        return id;
    }

    public String title() {
        return title;
    }

    public String context() {
        return context;
    }

    public String category() {
        return category;
    }

    public Role ownerRole() {
        return ownerRole;
    }

    public OriginReference origin() {
        return origin;
    }

    private static String requireNonBlank(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(fieldName + " must not be blank");
        }
        return value;
    }
}
