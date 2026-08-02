package com.github.ketilaa.consilium.decisions.port;

import com.github.ketilaa.consilium.decisions.Decision;
import java.util.Optional;

/**
 * Persists and reloads Decisions. Implementations only need to round-trip the event
 * history faithfully -- state is always re-derived by folding it (see DecisionState), never
 * stored separately.
 */
public interface DecisionRepository {
    void save(Decision decision);

    Optional<Decision> findById(String id);
}
