package com.github.ketilaa.consilium.decisions;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Free-text tag scanning, matching the fixed parser from
 * proof-of-concept/question-gating/lifecycle.py: match on the tag prefix (tolerant of a
 * trailing colon, reason text, or other punctuation inside the brackets), not an exact
 * closing-bracket substring -- the PoC's own bug history is the reason this isn't
 * {@code response.contains("[BLOCKING]")}.
 *
 * <p>Attribution to a specific item is positional: the free-text response has no structural
 * way to say "this tag belongs to item 3" the way a JSON schema's item_number would, so this
 * takes tags in the order they appear and assigns them to items in the order they were
 * presented, exactly as proof-of-concept/structured-output's grading heuristic did. If the
 * model discusses items out of order, this parser can misattribute -- a real, structural
 * limitation of free text, not a bug to paper over.
 *
 * <p>Matches {@code NON-BLOCKING} or {@code NON_BLOCKING} -- caught live on the first real
 * decision run through this engine: {@code LifecyclePrompts}' own definitions text spelled it
 * {@code NON_BLOCKING} (matching the Java enum name) while the tagging instruction asked for
 * {@code [NON-BLOCKING]} (hyphen), and the model echoed the underscore form it had just read in
 * its own prompt. Both the prompt and this regex were fixed; kept tolerant of either here too,
 * since a hyphen/underscore mismatch is exactly the class of formatting variance this parser
 * exists to survive, prompt-side bug or not.
 */
final class TagScanningVerdictParser implements VerdictParser {

    private static final Pattern TAG = Pattern.compile("\\[(BLOCKING|NON[-_]BLOCKING|QUESTION)\\b", Pattern.CASE_INSENSITIVE);

    @Override
    public Map<ItemId, Verdict> parse(String modelResponse, List<ItemId> itemIdsInPresentedOrder) {
        List<Verdict> tagsInOrder = new ArrayList<>();
        Matcher matcher = TAG.matcher(modelResponse);
        while (matcher.find()) {
            tagsInOrder.add(toVerdict(matcher.group(1)));
        }

        if (tagsInOrder.size() < itemIdsInPresentedOrder.size()) {
            throw new IllegalStateException(
                    "Expected at least " + itemIdsInPresentedOrder.size() + " tags, found "
                            + tagsInOrder.size() + " in: " + modelResponse
            );
        }

        Map<ItemId, Verdict> result = new LinkedHashMap<>();
        for (int i = 0; i < itemIdsInPresentedOrder.size(); i++) {
            result.put(itemIdsInPresentedOrder.get(i), tagsInOrder.get(i));
        }
        return result;
    }

    private static Verdict toVerdict(String tag) {
        return switch (tag.toUpperCase().replace("-", "_")) {
            case "BLOCKING" -> Verdict.BLOCKING;
            case "NON_BLOCKING" -> Verdict.NON_BLOCKING;
            case "QUESTION" -> Verdict.QUESTION;
            default -> throw new IllegalStateException("Unrecognized tag: " + tag);
        };
    }
}
