package com.github.ketilaa.consilium.decisions;

/**
 * Matches the fixed {@code _is_resolved} from proof-of-concept/question-gating/lifecycle.py:
 * strip leading markdown markup (not just whitespace) before checking the prefix. A response
 * beginning {@code **RESOLVED.**} broke the naive version of this exact check once already.
 */
final class TagScanningRecheckParser implements RecheckParser {

    @Override
    public RecheckVerdict parse(String modelResponse) {
        String stripped = modelResponse.replaceFirst("^[\\s*_#>-]+", "").toUpperCase();
        if (stripped.startsWith("NOT RESOLVED") || stripped.startsWith("NOT_RESOLVED")) {
            return RecheckVerdict.NOT_RESOLVED;
        }
        if (stripped.startsWith("RESOLVED")) {
            return RecheckVerdict.RESOLVED;
        }
        throw new IllegalStateException("Could not parse a RESOLVED/NOT RESOLVED verdict from: " + modelResponse);
    }
}
