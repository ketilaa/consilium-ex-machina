package com.github.ketilaa.consilium.decisions.port;

import com.github.ketilaa.consilium.decisions.DecisionEvent;

/**
 * The real integration seam for everything not built yet -- a future event bus or
 * work-item graph subscribes here, not by calling into the Decision Engine's internals.
 * Matches "agents subscribe to events rather than invoking each other directly" from
 * docs/high-level-architecture.md. The in-process {@code LoggingEventPublisher} adapter is
 * the only implementation for now; nothing about this interface assumes that.
 */
public interface DecisionEventPublisher {
    void publish(String decisionId, DecisionEvent event);
}
