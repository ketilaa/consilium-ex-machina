package com.github.ketilaa.consilium.decisions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * End-to-end through the real service, using a scripted fake model so no network/local
 * server is required. Recreates the audit-log-retention scenario shape validated in
 * proof-of-concept/question-gating -- the same Issue/Question pair, the same self-answer
 * deferral, the same eventual convergence -- but exercised through real, kept orchestration
 * code instead of a one-off script.
 */
class DecisionLifecycleServiceTest {

    private static final Role OWNER = Roles.RELEASE_MANAGER;
    private static final Role ISSUE_ROLE = Roles.BACKEND_DEVELOPER;
    private static final Role QUESTION_ROLE = Roles.SECURITY_REVIEWER;
    private static final ItemId ISSUE_ITEM = new ItemId(ISSUE_ROLE, 0);
    private static final ItemId QUESTION_ITEM = new ItemId(QUESTION_ROLE, 0);

    private static Decision newDecision() {
        return new Decision(
                "d-test",
                "How long should the platform retain its audit log?",
                "Compliance / data retention",
                OWNER,
                new OriginReference("test:audit-log-retention")
        );
    }

    @Test
    void fullLifecycleConvergesOnceTheQuestionIsAnsweredExternallyAndReconfirmed() {
        ScriptedChatModel model = new ScriptedChatModel(
                "Retain for seven years, store in S3.",                                 // propose
                "No archiving strategy -- the table will grow without bound.",          // contest: issue
                "What's the actual minimum retention period? I don't have access.",     // contest: question
                "1. [BLOCKING] no archiving strategy.\n2. [QUESTION] retention period requires Legal.", // classify
                "Added a one-year archiving policy. Assuming 7 years until Legal confirms.", // self-answer attempt
                "RESOLVED. Archiving policy addresses my concern.",                      // recheck issue (round 1)
                "NOT RESOLVED. Still just an assumption, not a real answer.",            // recheck question (round 1)
                "Legal confirmed 3 years. Final: retain 3 years, archive after 1 year.", // final revision
                "RESOLVED. Archiving policy still present.",                            // recheck issue (round 2)
                "RESOLVED. The revision now cites Legal's confirmed answer of 3 years."  // recheck question (round 2)
        );
        DecisionLifecycleService service = new DecisionLifecycleService(model);
        Decision decision = newDecision();

        service.propose(decision);
        service.contest(decision, List.of(ISSUE_ROLE, QUESTION_ROLE));
        service.classify(decision);
        assertThat(decision.state().status()).isEqualTo(DecisionStatus.CONTESTED);

        service.reviseSelfAnswerAttempt(decision);
        service.recheck(decision);
        assertThat(decision.state().status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);

        service.resolveQuestionExternally(decision, QUESTION_ITEM, "Legal confirmed 3 years", "Legal");
        service.reviseFinal(decision);
        service.recheck(decision);

        assertThat(decision.state().status()).isEqualTo(DecisionStatus.CONVERGED);
    }

    @Test
    void gateHoldsThroughTheServiceEvenWhenTheRaiserIsFooledByASelfAnswer() {
        // The recheck script deliberately claims RESOLVED after nothing but a self-answer --
        // simulating a raiser fooled by a confident guess. The gate must still hold, because
        // resolveQuestionExternally is never called.
        ScriptedChatModel model = new ScriptedChatModel(
                "Retain for seven years, store in S3.",
                "No archiving strategy.",
                "What's the actual minimum retention period?",
                "1. [BLOCKING] no archiving strategy.\n2. [QUESTION] retention period requires Legal.",
                "Assuming 7 years is fine, moving on.",
                "RESOLVED.",
                "RESOLVED." // the question-raiser is fooled here -- no external answer exists
        );
        DecisionLifecycleService service = new DecisionLifecycleService(model);
        Decision decision = newDecision();

        service.propose(decision);
        service.contest(decision, List.of(ISSUE_ROLE, QUESTION_ROLE));
        service.classify(decision);
        service.reviseSelfAnswerAttempt(decision);
        service.recheck(decision);

        assertThat(decision.state().status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);
        assertThat(decision.state().openQuestions()).hasSize(1);
    }

    @Test
    void resolveQuestionExternallyRejectsARoleThatIsNotClassifiedQuestion() {
        ScriptedChatModel model = new ScriptedChatModel(
                "Retain for seven years, store in S3.",
                "No archiving strategy.",
                "What's the actual minimum retention period?",
                "1. [BLOCKING] no archiving strategy.\n2. [QUESTION] retention period requires Legal."
        );
        DecisionLifecycleService service = new DecisionLifecycleService(model);
        Decision decision = newDecision();

        service.propose(decision);
        service.contest(decision, List.of(ISSUE_ROLE, QUESTION_ROLE));
        service.classify(decision);

        assertThatThrownBy(() ->
                service.resolveQuestionExternally(decision, ISSUE_ITEM, "some answer", "Legal")
        ).isInstanceOf(IllegalStateException.class);
    }

    @Test
    void aRoleRaisingTwoDistinctConcernsGetsThemSplitAndAnsweringOneLeavesTheOtherOpen() {
        // Security Reviewer raises two distinct missing facts in one reaction -- exactly the
        // shape a live run against a real model produced once the challenger was taught the
        // ENGINEERING TRADE-OFF / MISSING FACT distinction. Both must be tracked
        // independently: answering the retention-period one must not silently resolve the
        // unrelated cost one.
        ScriptedChatModel model = new ScriptedChatModel(
                "Retain for seven years, store in S3.",
                "ENGINEERING TRADE-OFF: No archiving strategy -- the table will grow without bound.",
                "MISSING FACT: What's the actual minimum retention period? I don't have access.\n\n"
                        + "MISSING FACT: What's the cost implication of long-term storage? Finance would know.",
                "1. [BLOCKING] no archiving strategy.\n2. [QUESTION] retention period requires Legal.\n"
                        + "3. [QUESTION] cost implication requires Finance.",
                "Added a one-year archiving policy. Assuming 7 years and a modest budget for now.",
                "RESOLVED. Archiving policy addresses my concern.",
                "NOT RESOLVED. Still just an assumption about the retention period.",
                "NOT RESOLVED. Still just an assumption about cost, not a real answer from Finance."
        );
        DecisionLifecycleService service = new DecisionLifecycleService(model);
        Decision decision = newDecision();

        service.propose(decision);
        service.contest(decision, List.of(ISSUE_ROLE, QUESTION_ROLE));

        ItemId retentionItem = new ItemId(QUESTION_ROLE, 0);
        ItemId costItem = new ItemId(QUESTION_ROLE, 1);
        assertThat(decision.state().raisedItems()).containsKeys(ISSUE_ITEM, retentionItem, costItem);

        service.classify(decision);
        service.reviseSelfAnswerAttempt(decision);
        service.recheck(decision);

        assertThat(decision.state().openQuestions()).extracting(Question::itemId)
                .containsExactlyInAnyOrder(retentionItem, costItem);

        service.resolveQuestionExternally(decision, retentionItem, "Legal confirmed 3 years", "Legal");

        assertThat(decision.state().openQuestions()).extracting(Question::itemId).containsExactly(costItem);
        assertThat(decision.state().status()).isEqualTo(DecisionStatus.BLOCKED_ON_QUESTION);
    }
}
