package com.github.ketilaa.consilium.decisions;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Splits on the literal labels {@link LifecyclePrompts#challenger} teaches the model to
 * start each distinct concern with ("ENGINEERING TRADE-OFF:" / "MISSING FACT:"). If the
 * model doesn't use the format at all -- ignoring the instruction, or genuinely having only
 * one concern that happens not to be labeled -- the whole response is kept as a single item
 * rather than failing; this is a fallback to the pre-splitting behavior, not a silent loss
 * of the response.
 */
final class LabeledItemSplitter implements ItemSplitter {

    private static final Pattern LABEL = Pattern.compile("(ENGINEERING TRADE-OFF|MISSING FACT):", Pattern.CASE_INSENSITIVE);

    @Override
    public List<String> split(String rawResponse) {
        List<Integer> starts = new ArrayList<>();
        Matcher matcher = LABEL.matcher(rawResponse);
        while (matcher.find()) {
            starts.add(matcher.start());
        }

        if (starts.isEmpty()) {
            return List.of(rawResponse.strip());
        }

        List<String> items = new ArrayList<>();
        for (int i = 0; i < starts.size(); i++) {
            int from = starts.get(i);
            int to = i + 1 < starts.size() ? starts.get(i + 1) : rawResponse.length();
            String item = rawResponse.substring(from, to).strip();
            if (!item.isBlank()) {
                items.add(item);
            }
        }
        return items;
    }
}
