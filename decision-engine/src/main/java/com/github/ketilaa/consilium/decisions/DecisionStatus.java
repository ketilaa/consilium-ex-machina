package com.github.ketilaa.consilium.decisions;

/** The current status of a Decision, always a pure function of its event history -- see {@link DecisionState#fold}. */
public enum DecisionStatus {
    /** Proposed, not yet contested. */
    PROPOSED,
    /** Contested and either not yet classified, or classified with unresolved items and no revision attempted yet. */
    CONTESTED,
    /**
     * At least one raised item was classified {@link Verdict#QUESTION} and has not been
     * cleared by a {@link DecisionEvent.QuestionAnsweredExternally} event. This is
     * structurally impossible to clear through revision or recheck alone.
     */
    BLOCKED_ON_QUESTION,
    /** No open questions, and every blocking item's targeted recheck says {@link RecheckVerdict#RESOLVED}. */
    CONVERGED,
    /** No open questions, but at least one item's targeted recheck still says {@link RecheckVerdict#NOT_RESOLVED}. */
    ESCALATED_TO_HUMAN
}
