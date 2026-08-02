package com.github.ketilaa.consilium.decisions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * The structural invariant proof-of-concept/question-gating exists to validate: a Question
 * can ONLY be cleared by a {@link DecisionEvent.QuestionAnsweredExternally} event. No amount
 * of revising, reclassifying, or even a targeted recheck saying RESOLVED can clear it on its
 * own -- confidence in the owner's own text is never sufficient.
 */
class QuestionGateTest {

    private static final Role QUESTION_ROLE = Roles.SECURITY_REVIEWER;

    private static List<DecisionEvent> baseEventsWithOpenQuestion() {
        return List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(QUESTION_ROLE, "what's the real minimum?")),
                new DecisionEvent.Classified(Map.of(QUESTION_ROLE, Verdict.QUESTION))
        );
    }

    @Test
    void aRecheckSayingResolvedDoesNotClearTheQuestionOnItsOwn() {
        var events = new java.util.ArrayList<>(baseEventsWithOpenQuestion());
        events.add(new DecisionEvent.Revised("self-answer attempt: confidently assuming 7 years"));
        events.add(new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.RESOLVED)));

        DecisionState state = DecisionState.fold(events);

        assertThat(state.openQuestions()).hasSize(1);
        assertThat(state.status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);
    }

    @Test
    void repeatedRevisionsAloneNeverClearTheQuestion() {
        var events = new java.util.ArrayList<>(baseEventsWithOpenQuestion());
        for (int round = 0; round < 5; round++) {
            events.add(new DecisionEvent.Revised("revision attempt " + round));
            events.add(new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.RESOLVED)));
        }

        DecisionState state = DecisionState.fold(events);

        assertThat(state.status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);
    }

    @Test
    void onlyAnExternalAnswerEventClearsTheQuestion() {
        var events = new java.util.ArrayList<>(baseEventsWithOpenQuestion());
        events.add(new DecisionEvent.Revised("self-answer attempt"));
        events.add(new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.NOT_RESOLVED)));
        events.add(new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, "Legal confirmed 3 years", "Legal"));
        events.add(new DecisionEvent.Revised("final revision incorporating the real answer"));
        events.add(new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.RESOLVED)));

        DecisionState state = DecisionState.fold(events);

        assertThat(state.openQuestions()).isEmpty();
        assertThat(state.status()).isEqualTo(DecisionStatus.CONVERGED);
    }

    @Test
    void externalAnswerEventRejectsBlankSource() {
        assertThatThrownBy(() ->
                new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, "Legal confirmed 3 years", " ")
        ).isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void externalAnswerEventRejectsBlankAnswerText() {
        assertThatThrownBy(() ->
                new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, " ", "Legal")
        ).isInstanceOf(IllegalArgumentException.class);
    }
}
