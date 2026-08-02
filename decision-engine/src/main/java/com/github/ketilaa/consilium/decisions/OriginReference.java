package com.github.ketilaa.consilium.decisions;

/**
 * Opaque provenance metadata for a Decision -- a plain string like {@code "work-item:1234"}
 * or {@code "human:ketil"}. The Decision Engine never resolves, validates, or follows this
 * reference; it exists purely so a future caller (a work-item graph, an issue tracker, a
 * human) can trace a Decision back to whatever created it, without the engine needing to
 * know that caller's schema exists.
 */
public record OriginReference(String value) {

    public OriginReference {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("OriginReference must not be blank");
        }
    }

    @Override
    public String toString() {
        return value;
    }
}
