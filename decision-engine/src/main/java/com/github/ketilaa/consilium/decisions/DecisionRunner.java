package com.github.ketilaa.consilium.decisions;

import com.github.ketilaa.consilium.decisions.port.ChatModel;
import com.github.ketilaa.consilium.decisions.port.DecisionEventPublisher;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import java.util.List;

/**
 * Runs a Decision through propose -> contest -> classify -> (self-answer attempt -> recheck,
 * if anything needs addressing), then persists it. Deliberately stops at whatever state that
 * produces -- {@code BLOCKED_ON_QUESTION} or {@code ESCALATED_TO_HUMAN} included -- rather than
 * forcing a resolution in one call. Answering a Question is a separate, later step
 * ({@link DecisionLifecycleService#resolveQuestionExternally}), because a real answer may not
 * exist yet when this runs.
 *
 * <p>Public, not CLI-specific: both {@code DecisionEngineCli} and work-items' {@code WorkItemCli}
 * call this, so the orchestration isn't duplicated across two CLI classes.
 */
public final class DecisionRunner {

    private final DecisionLifecycleService service;
    private final DecisionRepository repository;

    public DecisionRunner(ChatModel chatModel, DecisionEventPublisher publisher, DecisionRepository repository) {
        this.service = new DecisionLifecycleService(chatModel, publisher);
        this.repository = repository;
    }

    /** Runs the decision, persists it via the repository, and returns it for the caller to report on. */
    public Decision run(Decision decision, List<Role> challengerRoles) {
        service.propose(decision);
        service.contest(decision, challengerRoles);
        service.classify(decision);

        if (decision.state().status() != DecisionStatus.CONVERGED) {
            service.reviseSelfAnswerAttempt(decision);
            service.recheck(decision);
        }

        repository.save(decision);
        return decision;
    }

    /**
     * Resolves one open Question with an externally-sourced answer, has the owner revise
     * accordingly, rechecks, and persists. Callable independently of {@link #run}, any time a
     * real answer becomes available -- which may be well after the initial run.
     */
    public Decision answerQuestion(Decision decision, ItemId itemId, String answerText, String source) {
        service.resolveQuestionExternally(decision, itemId, answerText, source);
        service.reviseFinal(decision);
        service.recheck(decision);
        repository.save(decision);
        return decision;
    }

    /**
     * Re-runs the final revision and recheck with no new external answer -- for when the prior
     * attempt failed for a reason unrelated to the decision's own content (e.g. a response
     * silently truncated by too small a token budget, caught on d-22ffab13 by a human reviewing
     * an escalated decision and noticing the stored text ended mid-sentence). Safe to call any
     * number of times: {@code reviseFinal} always incorporates every external answer recorded so
     * far, not just the most recent one, and {@code recheck} always rechecks against whichever
     * revision was most recently persisted.
     */
    public Decision retryFinalRevision(Decision decision) {
        service.reviseFinal(decision);
        service.recheck(decision);
        repository.save(decision);
        return decision;
    }
}
