package com.github.ketilaa.consilium.decisions;

/**
 * The result of asking the specific role that raised an item whether a revision resolves
 * ITS OWN item -- not a generalist reclassifying every item from scratch. This is the fix
 * for the "anchoring" bug found in poc-decision-making.md and reproduced (then fixed again)
 * in poc-question-gating.md.
 */
public enum RecheckVerdict {
    RESOLVED,
    NOT_RESOLVED
}
