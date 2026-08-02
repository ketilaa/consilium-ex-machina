package com.github.ketilaa.consilium.decisions;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Pure fold tests -- no LLM, no I/O. These lock in the exact state-derivation invariants
 * that proof-of-concept/question-gating's run_gated() implemented in Python, now as real,
 * regression-tested platform code.
 */
class DecisionStateTest {

    private static final Role OWNER = Roles.RELEASE_MANAGER;
    private static final Role ISSUE_ROLE = Roles.BACKEND_DEVELOPER;
    private static final Role QUESTION_ROLE = Roles.SECURITY_REVIEWER;

    @Test
    void proposedWithNoContestIsProposed() {
        DecisionState state = DecisionState.fold(List.of(new DecisionEvent.Proposed("retain for 7 years")));

        assertThat(state.status()).isEqualTo(DecisionStatus.PROPOSED);
    }

    @Test
    void contestedWithNoItemsRaisedConvergesTriviallyOnceClassified() {
        // The service always emits a Classified event after Contested, even a trivially
        // empty one -- the fold deliberately doesn't special-case "no items raised" so
        // there's exactly one rule for "nothing blocking, nothing to ask" everywhere.
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of()),
                new DecisionEvent.Classified(Map.of())
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONVERGED);
    }

    @Test
    void contestedWithNoItemsRaisedButNotYetClassifiedStaysContested() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of())
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONTESTED);
    }

    @Test
    void contestedButNotYetClassifiedIsContested() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(ISSUE_ROLE, "no archiving strategy"))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONTESTED);
    }

    @Test
    void classifiedWithOnlyNonBlockingItemsConverges() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(ISSUE_ROLE, "minor style nit")),
                new DecisionEvent.Classified(Map.of(ISSUE_ROLE, Verdict.NON_BLOCKING))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONVERGED);
    }

    @Test
    void classifiedBlockingButNotYetRevisedStaysContested() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(ISSUE_ROLE, "no archiving strategy")),
                new DecisionEvent.Classified(Map.of(ISSUE_ROLE, Verdict.BLOCKING))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONTESTED);
    }

    @Test
    void revisedAndResolvedIssueConverges() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(ISSUE_ROLE, "no archiving strategy")),
                new DecisionEvent.Classified(Map.of(ISSUE_ROLE, Verdict.BLOCKING)),
                new DecisionEvent.Revised("added a one-year archiving policy"),
                new DecisionEvent.Rechecked(Map.of(ISSUE_ROLE, RecheckVerdict.RESOLVED))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONVERGED);
    }

    @Test
    void revisedButStillUnresolvedIssueEscalates() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(ISSUE_ROLE, "no archiving strategy")),
                new DecisionEvent.Classified(Map.of(ISSUE_ROLE, Verdict.BLOCKING)),
                new DecisionEvent.Revised("restated the original proposal"),
                new DecisionEvent.Rechecked(Map.of(ISSUE_ROLE, RecheckVerdict.NOT_RESOLVED))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.ESCALATED_TO_HUMAN);
    }

    @Test
    void openQuestionBlocksRegardlessOfRevisionOrRecheck() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(QUESTION_ROLE, "what's the real minimum?")),
                new DecisionEvent.Classified(Map.of(QUESTION_ROLE, Verdict.QUESTION)),
                new DecisionEvent.Revised("self-answer attempt: assuming 7 years for now"),
                // Even if a recheck somehow said RESOLVED, an open Question must still block --
                // this is the exact invariant proof-of-concept/question-gating validated.
                new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.RESOLVED))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);
        assertThat(state.openQuestions()).hasSize(1);
    }

    @Test
    void answeringExternallyClearsTheStalePreAnswerRecheck() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(QUESTION_ROLE, "what's the real minimum?")),
                new DecisionEvent.Classified(Map.of(QUESTION_ROLE, Verdict.QUESTION)),
                new DecisionEvent.Revised("self-answer attempt: assuming 7 years for now"),
                new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.NOT_RESOLVED)),
                new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, "Legal confirmed 3 years", "Legal")
                // deliberately no fresh Rechecked event yet
        ));

        // Answered, but not yet reconfirmed -- must not silently read as converged.
        assertThat(state.status()).isEqualTo(DecisionStatus.ESCALATED_TO_HUMAN);
        assertThat(state.openQuestions()).isEmpty();
        assertThat(state.questions().get(0).answeredExternally()).isTrue();
    }

    @Test
    void fullyConvergesOnceAnsweredAndReconfirmed() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(
                        ISSUE_ROLE, "no archiving strategy",
                        QUESTION_ROLE, "what's the real minimum?"
                )),
                new DecisionEvent.Classified(Map.of(
                        ISSUE_ROLE, Verdict.BLOCKING,
                        QUESTION_ROLE, Verdict.QUESTION
                )),
                new DecisionEvent.Revised("self-answer attempt"),
                new DecisionEvent.Rechecked(Map.of(
                        ISSUE_ROLE, RecheckVerdict.RESOLVED,
                        QUESTION_ROLE, RecheckVerdict.NOT_RESOLVED
                )),
                new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, "Legal confirmed 3 years", "Legal"),
                new DecisionEvent.Revised("final revision incorporating the real answer"),
                new DecisionEvent.Rechecked(Map.of(
                        ISSUE_ROLE, RecheckVerdict.RESOLVED,
                        QUESTION_ROLE, RecheckVerdict.RESOLVED
                ))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.CONVERGED);
        assertThat(state.revisionRounds()).isEqualTo(2);
    }

    @Test
    void answeredButFinalRecheckStillNotResolvedEscalates() {
        DecisionState state = DecisionState.fold(List.of(
                new DecisionEvent.Proposed("retain for 7 years"),
                new DecisionEvent.Contested(Map.of(QUESTION_ROLE, "what's the real minimum?")),
                new DecisionEvent.Classified(Map.of(QUESTION_ROLE, Verdict.QUESTION)),
                new DecisionEvent.Revised("self-answer attempt"),
                new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.NOT_RESOLVED)),
                new DecisionEvent.QuestionAnsweredExternally(QUESTION_ROLE, "Legal confirmed 3 years", "Legal"),
                new DecisionEvent.Revised("final revision, but somehow still unconvincing"),
                new DecisionEvent.Rechecked(Map.of(QUESTION_ROLE, RecheckVerdict.NOT_RESOLVED))
        ));

        assertThat(state.status()).isEqualTo(DecisionStatus.ESCALATED_TO_HUMAN);
    }
}
