package com.github.ketilaa.consilium.decisions;

import java.util.List;

/**
 * Splits one challenger's raw reaction into the distinct concerns it contains. A single
 * reaction is not guaranteed to be one atomic concern -- once a challenger is taught the
 * BLOCKING-vs-missing-fact distinction (see {@link LifecyclePrompts#challenger}), it
 * naturally raises several concerns of different kinds in one turn, and each needs its own
 * independent classification and recheck rather than being forced into a single verdict for
 * the whole reaction.
 */
public interface ItemSplitter {
    /** @return at least one item -- never empty, even if nothing splittable was found. */
    List<String> split(String rawResponse);
}
