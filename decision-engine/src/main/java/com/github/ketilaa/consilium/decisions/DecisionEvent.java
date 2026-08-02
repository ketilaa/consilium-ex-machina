package com.github.ketilaa.consilium.decisions;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * The append-only history of a Decision. State is never stored directly -- it's always
 * derived by folding this list (see {@link DecisionState#fold}), so the audit trail is the
 * source of truth, not a side effect of it.
 */
public sealed interface DecisionEvent {

    /** The owner's initial recommendation. */
    record Proposed(String proposalText) implements DecisionEvent {
        public Proposed {
            requireNonBlank(proposalText, "proposalText");
        }
    }

    /**
     * Every item raised against the proposal in one contest round, keyed by the raising
     * role, in presentation order -- {@link TagScanningVerdictParser} attributes free-text
     * tags to roles positionally, so this order must survive intact. {@code Map.copyOf}
     * does NOT preserve insertion order; that silently broke this once already.
     */
    record Contested(Map<Role, String> items) implements DecisionEvent {
        public Contested {
            items = orderPreservingCopy(items);
        }
    }

    /** The classification of every raised item in one round, keyed by the raising role, in the same order. */
    record Classified(Map<Role, Verdict> verdicts) implements DecisionEvent {
        public Classified {
            verdicts = orderPreservingCopy(verdicts);
        }
    }

    /** The owner's revision -- either a self-answer attempt or a final revision. */
    record Revised(String revisionText) implements DecisionEvent {
        public Revised {
            requireNonBlank(revisionText, "revisionText");
        }
    }

    /**
     * The targeted per-raiser recheck for one round: each role that raised an item judges
     * only whether ITS OWN item is resolved by the most recent revision -- never a
     * generalist reclassifying everything from scratch.
     */
    record Rechecked(Map<Role, RecheckVerdict> verdicts) implements DecisionEvent {
        public Rechecked {
            verdicts = orderPreservingCopy(verdicts);
        }
    }

    /**
     * The ONLY event that can clear a {@link Verdict#QUESTION} item. There is deliberately
     * no path from the owner's revision (see {@link Revised}) to this event type -- it is
     * only ever constructed by
     * {@link DecisionLifecycleService#resolveQuestionExternally}, a method entirely separate
     * from the revise/self-answer path, so an owner's own text -- however confident -- can
     * never satisfy this structural gate. Mirrors the {@code question_resolved_externally}
     * flag validated in proof-of-concept/question-gating.
     */
    record QuestionAnsweredExternally(Role role, String answerText, String source) implements DecisionEvent {
        public QuestionAnsweredExternally {
            requireNonBlank(answerText, "answerText");
            requireNonBlank(source, "source");
        }
    }

    private static void requireNonBlank(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(fieldName + " must not be blank");
        }
    }

    private static <K, V> Map<K, V> orderPreservingCopy(Map<K, V> source) {
        return Collections.unmodifiableMap(new LinkedHashMap<>(source));
    }
}
