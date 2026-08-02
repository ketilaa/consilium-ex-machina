package com.github.ketilaa.consilium.decisions;

import java.util.List;
import java.util.Map;

/**
 * Turns a classifier's response into a verdict per role. Deliberately an interface: v1's
 * only implementation ({@link TagScanningVerdictParser}) scans free text for tags, the same
 * approach used (and twice found fragile) across the PoCs. Swapping to forced structured
 * output, once proof-of-concept/structured-output's findings are in, is meant to be a new
 * implementation of this interface, not a change to anything that calls it.
 */
public interface VerdictParser {
    /**
     * @param modelResponse raw text from the classifier
     * @param rolesInPresentedOrder the roles whose items were classified, in the order they
     *                              were shown to the model
     * @throws IllegalStateException if the response can't be parsed into exactly one verdict
     *                                per role
     */
    Map<Role, Verdict> parse(String modelResponse, List<Role> rolesInPresentedOrder);
}
