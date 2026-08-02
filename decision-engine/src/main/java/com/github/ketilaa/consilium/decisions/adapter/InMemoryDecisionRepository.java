package com.github.ketilaa.consilium.decisions.adapter;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Stores a snapshot of each Decision's event history at save time -- not a live reference --
 * so save() is an explicit persistence boundary, not just "the object happens to be shared."
 */
public final class InMemoryDecisionRepository implements DecisionRepository {

    private final Map<String, Decision> snapshots = new ConcurrentHashMap<>();

    @Override
    public void save(Decision decision) {
        snapshots.put(decision.id(), Decision.reconstruct(
                decision.id(), decision.title(), decision.category(), decision.ownerRole(),
                decision.origin(), decision.events()
        ));
    }

    @Override
    public Optional<Decision> findById(String id) {
        return Optional.ofNullable(snapshots.get(id));
    }
}
