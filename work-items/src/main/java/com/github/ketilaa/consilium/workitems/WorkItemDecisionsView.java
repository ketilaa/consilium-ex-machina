package com.github.ketilaa.consilium.workitems;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.OriginReference;
import com.github.ketilaa.consilium.decisions.Question;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import java.util.List;

/**
 * The composition point between the two modules: given a Work Item and the Decision Engine's
 * own repository, answers "what decisions relate to me" and "what's still open across them" --
 * the two attributes docs/high-level-architecture.md already says every work item carries.
 *
 * <p>Deliberately a read-only view, not new state Work Item stores itself: the Decision Engine
 * already owns this information (each Decision's own origin, each Decision's own
 * {@code openQuestions()}), so re-storing it on the Work Item side would just be a second,
 * driftable copy of the same facts. This is the one place in the {@code work-items} module
 * that depends on {@code decisions} -- the reverse is never true, {@code decisions} has no
 * idea Work Items exist.
 */
public final class WorkItemDecisionsView {

    private final DecisionRepository decisionRepository;

    public WorkItemDecisionsView(DecisionRepository decisionRepository) {
        this.decisionRepository = decisionRepository;
    }

    /** The convention this module owns for how a Work Item is referenced as a Decision's origin. */
    public static OriginReference originReferenceFor(WorkItemId workItemId) {
        return new OriginReference("work-item:" + workItemId.value());
    }

    public List<Decision> relatedDecisions(WorkItemId workItemId) {
        return decisionRepository.findByOrigin(originReferenceFor(workItemId));
    }

    /** Every open Question across every Decision related to this Work Item, flattened. */
    public List<Question> openQuestions(WorkItemId workItemId) {
        return relatedDecisions(workItemId).stream()
                .flatMap(decision -> decision.state().openQuestions().stream())
                .toList();
    }
}
