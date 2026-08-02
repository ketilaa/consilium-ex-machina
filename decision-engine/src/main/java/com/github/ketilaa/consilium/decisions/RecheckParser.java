package com.github.ketilaa.consilium.decisions;

/**
 * Turns a targeted recheck response into a {@link RecheckVerdict}. See {@link VerdictParser}
 * for why this is an interface rather than a static method.
 */
public interface RecheckParser {
    /** @throws IllegalStateException if the response doesn't clearly resolve to RESOLVED/NOT_RESOLVED */
    RecheckVerdict parse(String modelResponse);
}
