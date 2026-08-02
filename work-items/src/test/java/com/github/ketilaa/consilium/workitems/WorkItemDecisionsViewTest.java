package com.github.ketilaa.consilium.workitems;

import static org.assertj.core.api.Assertions.assertThat;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.ItemId;
import com.github.ketilaa.consilium.decisions.OriginReference;
import com.github.ketilaa.consilium.decisions.Roles;
import com.github.ketilaa.consilium.decisions.Verdict;
import com.github.ketilaa.consilium.decisions.adapter.InMemoryDecisionRepository;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Exercises the actual cross-module composition: a real decisions.Decision, saved via a real
 * decisions.adapter.InMemoryDecisionRepository, found and interpreted through
 * WorkItemDecisionsView -- not a mock standing in for either side.
 */
class WorkItemDecisionsViewTest {

    private static final ItemId QUESTION_ITEM = new ItemId(Roles.SECURITY_REVIEWER, 0);

    @Test
    void relatedDecisionsOnlyReturnsDecisionsWithThisWorkItemsOrigin() {
        WorkItemId workItemId = new WorkItemId("feat-1");
        OriginReference thisWorkItem = WorkItemDecisionsView.originReferenceFor(workItemId);

        Decision related = new Decision("d-1", "Retention period", "Compliance", Roles.RELEASE_MANAGER, thisWorkItem);
        related.apply(new DecisionEvent.Proposed("retain for 7 years"));

        Decision unrelated = new Decision(
                "d-2", "Unrelated decision", "Compliance", Roles.RELEASE_MANAGER,
                new OriginReference("work-item:feat-2")
        );
        unrelated.apply(new DecisionEvent.Proposed("something else"));

        InMemoryDecisionRepository decisionRepository = new InMemoryDecisionRepository();
        decisionRepository.save(related);
        decisionRepository.save(unrelated);

        WorkItemDecisionsView view = new WorkItemDecisionsView(decisionRepository);

        assertThat(view.relatedDecisions(workItemId)).extracting(Decision::id).containsExactly("d-1");
    }

    @Test
    void openQuestionsFlattensAcrossAllRelatedDecisions() {
        WorkItemId workItemId = new WorkItemId("feat-1");
        OriginReference thisWorkItem = WorkItemDecisionsView.originReferenceFor(workItemId);

        Decision decision = new Decision("d-1", "Retention period", "Compliance", Roles.RELEASE_MANAGER, thisWorkItem);
        decision.apply(new DecisionEvent.Proposed("retain for 7 years"));
        decision.apply(new DecisionEvent.Contested(Map.of(QUESTION_ITEM, "what's the real minimum?")));
        decision.apply(new DecisionEvent.Classified(Map.of(QUESTION_ITEM, Verdict.QUESTION)));

        InMemoryDecisionRepository decisionRepository = new InMemoryDecisionRepository();
        decisionRepository.save(decision);

        WorkItemDecisionsView view = new WorkItemDecisionsView(decisionRepository);

        assertThat(view.openQuestions(workItemId)).extracting(q -> q.itemId()).containsExactly(QUESTION_ITEM);
    }

    @Test
    void relatedDecisionsIsEmptyWhenNothingMatches() {
        WorkItemId workItemId = new WorkItemId("feat-with-no-decisions");
        WorkItemDecisionsView view = new WorkItemDecisionsView(new InMemoryDecisionRepository());

        assertThat(view.relatedDecisions(workItemId)).isEmpty();
        assertThat(view.openQuestions(workItemId)).isEmpty();
    }
}
