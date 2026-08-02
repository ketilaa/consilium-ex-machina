package com.github.ketilaa.consilium.decisions;

import java.util.List;
import java.util.Map;

/**
 * Turns a classifier's response into a verdict per item. Deliberately an interface: v1's
 * only implementation ({@link TagScanningVerdictParser}) scans free text for tags, the same
 * approach used (and twice found fragile) across the PoCs. Swapping to forced structured
 * output, once proof-of-concept/structured-output's findings are in, is meant to be a new
 * implementation of this interface, not a change to anything that calls it.
 */
public interface VerdictParser {
    /**
     * @param modelResponse raw text from the classifier
     * @param itemIdsInPresentedOrder the items classified, in the order they were shown to the model
     * @throws IllegalStateException if the response can't be parsed into exactly one verdict
     *                                per item
     */
    Map<ItemId, Verdict> parse(String modelResponse, List<ItemId> itemIdsInPresentedOrder);
}
