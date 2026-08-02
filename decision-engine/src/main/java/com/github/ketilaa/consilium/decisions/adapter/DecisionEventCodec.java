package com.github.ketilaa.consilium.decisions.adapter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.ItemId;
import com.github.ketilaa.consilium.decisions.RecheckVerdict;
import com.github.ketilaa.consilium.decisions.Verdict;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * Manual mapping between {@link DecisionEvent} and JSON, kept in the adapter layer instead of
 * annotating the domain records -- the domain shouldn't need to know a JSON library exists.
 */
final class DecisionEventCodec {

    private final ObjectMapper mapper;

    DecisionEventCodec(ObjectMapper mapper) {
        this.mapper = mapper;
    }

    ObjectNode toJson(DecisionEvent event) {
        ObjectNode node = mapper.createObjectNode();
        if (event instanceof DecisionEvent.Proposed e) {
            node.put("type", "Proposed");
            node.put("proposalText", e.proposalText());
        } else if (event instanceof DecisionEvent.Contested e) {
            node.put("type", "Contested");
            ObjectNode items = node.putObject("items");
            e.items().forEach((id, text) -> items.put(id.toString(), text));
        } else if (event instanceof DecisionEvent.Classified e) {
            node.put("type", "Classified");
            ObjectNode verdicts = node.putObject("verdicts");
            e.verdicts().forEach((id, verdict) -> verdicts.put(id.toString(), verdict.name()));
        } else if (event instanceof DecisionEvent.Revised e) {
            node.put("type", "Revised");
            node.put("revisionText", e.revisionText());
        } else if (event instanceof DecisionEvent.Rechecked e) {
            node.put("type", "Rechecked");
            ObjectNode verdicts = node.putObject("verdicts");
            e.verdicts().forEach((id, verdict) -> verdicts.put(id.toString(), verdict.name()));
        } else if (event instanceof DecisionEvent.QuestionAnsweredExternally e) {
            node.put("type", "QuestionAnsweredExternally");
            node.put("itemId", e.itemId().toString());
            node.put("answerText", e.answerText());
            node.put("source", e.source());
        } else {
            throw new IllegalStateException("Unhandled event type: " + event.getClass());
        }
        return node;
    }

    DecisionEvent fromJson(JsonNode node) {
        String type = node.get("type").asText();
        return switch (type) {
            case "Proposed" -> new DecisionEvent.Proposed(node.get("proposalText").asText());
            case "Contested" -> new DecisionEvent.Contested(readItemKeyed(node.get("items"), JsonNode::asText));
            case "Classified" -> new DecisionEvent.Classified(readItemKeyed(node.get("verdicts"), n -> Verdict.valueOf(n.asText())));
            case "Revised" -> new DecisionEvent.Revised(node.get("revisionText").asText());
            case "Rechecked" -> new DecisionEvent.Rechecked(
                    readItemKeyed(node.get("verdicts"), n -> RecheckVerdict.valueOf(n.asText()))
            );
            case "QuestionAnsweredExternally" -> new DecisionEvent.QuestionAnsweredExternally(
                    ItemId.parse(node.get("itemId").asText()),
                    node.get("answerText").asText(),
                    node.get("source").asText()
            );
            default -> throw new IllegalStateException("Unknown event type: " + type);
        };
    }

    private static <V> Map<ItemId, V> readItemKeyed(JsonNode node, Function<JsonNode, V> valueReader) {
        Map<ItemId, V> result = new LinkedHashMap<>();
        node.fields().forEachRemaining(entry -> result.put(ItemId.parse(entry.getKey()), valueReader.apply(entry.getValue())));
        return result;
    }
}
