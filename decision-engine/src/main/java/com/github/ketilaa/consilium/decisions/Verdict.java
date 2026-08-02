package com.github.ketilaa.consilium.decisions;

/**
 * The classification of a raised item.
 *
 * @see <a href="../../../../../../../docs/design/decision-making.md">docs/design/decision-making.md</a>
 */
public enum Verdict {
    /** A genuine problem the owner could address by revising the approach. */
    BLOCKING,
    /** A valid but non-critical point. */
    NON_BLOCKING,
    /**
     * A genuine gap in the facts available -- not resolvable by engineering revision,
     * because it depends on information that must come from an external source.
     */
    QUESTION
}
