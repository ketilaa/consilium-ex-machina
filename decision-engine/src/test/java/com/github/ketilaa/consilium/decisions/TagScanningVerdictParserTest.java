package com.github.ketilaa.consilium.decisions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * This parser had no dedicated test until it broke on the first real decision run through this
 * engine: the model wrote {@code [NON_BLOCKING]} (underscore) instead of the requested
 * {@code [NON-BLOCKING]} (hyphen) -- because {@code LifecyclePrompts}' own definitions text
 * had spelled it with an underscore a few lines earlier in the same prompt. Every case below is
 * either the exact failure or the same class of formatting variance found in prior PoCs.
 */
class TagScanningVerdictParserTest {

    private static final ItemId ITEM_A = new ItemId(Roles.BACKEND_DEVELOPER, 0);
    private static final ItemId ITEM_B = new ItemId(Roles.SECURITY_REVIEWER, 0);

    private final TagScanningVerdictParser parser = new TagScanningVerdictParser();

    @Test
    void parsesTheStandardHyphenatedTags() {
        Map<ItemId, Verdict> result = parser.parse(
                "Item A: [BLOCKING] a real problem.\nItem B: [NON-BLOCKING] minor.",
                List.of(ITEM_A, ITEM_B)
        );

        assertThat(result).containsEntry(ITEM_A, Verdict.BLOCKING).containsEntry(ITEM_B, Verdict.NON_BLOCKING);
    }

    @Test
    void tolerantOfUnderscoreInsteadOfHyphenInNonBlocking() {
        // The exact bug caught live: the model echoed the underscore spelling it saw in its own
        // prompt's definitions text instead of the hyphenated tag format it was asked to use.
        Map<ItemId, Verdict> result = parser.parse(
                "Item A: [BLOCKING] a real problem.\nItem B: [NON_BLOCKING] minor.",
                List.of(ITEM_A, ITEM_B)
        );

        assertThat(result).containsEntry(ITEM_A, Verdict.BLOCKING).containsEntry(ITEM_B, Verdict.NON_BLOCKING);
    }

    @Test
    void tolerantOfReasonTextInsideTheBracket() {
        // The shape of poc-question-gating.md's original bug: "[BLOCKING: reason]" instead of
        // "[BLOCKING] reason" broke an exact-substring match there; this parser must not repeat it.
        Map<ItemId, Verdict> result = parser.parse("[BLOCKING: this is why] [QUESTION: needs Legal]", List.of(ITEM_A, ITEM_B));

        assertThat(result).containsEntry(ITEM_A, Verdict.BLOCKING).containsEntry(ITEM_B, Verdict.QUESTION);
    }

    @Test
    void caseInsensitive() {
        Map<ItemId, Verdict> result = parser.parse("[blocking] one\n[question] two", List.of(ITEM_A, ITEM_B));

        assertThat(result).containsEntry(ITEM_A, Verdict.BLOCKING).containsEntry(ITEM_B, Verdict.QUESTION);
    }

    @Test
    void throwsRatherThanSilentlyMisattributingWhenTooFewTagsAreFound() {
        assertThatThrownBy(() -> parser.parse("[BLOCKING] only one tag here", List.of(ITEM_A, ITEM_B)))
                .isInstanceOf(IllegalStateException.class);
    }
}
