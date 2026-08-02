package com.github.ketilaa.consilium.decisions.port;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.OriginReference;
import java.util.List;
import java.util.Optional;

/**
 * Persists and reloads Decisions. Implementations only need to round-trip the event
 * history faithfully -- state is always re-derived by folding it (see DecisionState), never
 * stored separately.
 */
public interface DecisionRepository {
    void save(Decision decision);

    Optional<Decision> findById(String id);

    /**
     * All Decisions whose {@link OriginReference} equals the given one. This is the seam a
     * caller like a work-item module uses to answer "what decisions relate to me" -- this
     * repository has no idea what a work item is, it just matches on the opaque reference.
     */
    List<Decision> findByOrigin(OriginReference origin);
}
