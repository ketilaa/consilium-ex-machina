package com.github.ketilaa.consilium.decisions.adapter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.RecheckVerdict;
import com.github.ketilaa.consilium.decisions.Role;
import com.github.ketilaa.consilium.decisions.Roles;
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
            e.items().forEach((role, text) -> items.put(role.name(), text));
        } else if (event instanceof DecisionEvent.Classified e) {
            node.put("type", "Classified");
            ObjectNode verdicts = node.putObject("verdicts");
            e.verdicts().forEach((role, verdict) -> verdicts.put(role.name(), verdict.name()));
        } else if (event instanceof DecisionEvent.Revised e) {
            node.put("type", "Revised");
            node.put("revisionText", e.revisionText());
        } else if (event instanceof DecisionEvent.Rechecked e) {
            node.put("type", "Rechecked");
            ObjectNode verdicts = node.putObject("verdicts");
            e.verdicts().forEach((role, verdict) -> verdicts.put(role.name(), verdict.name()));
        } else if (event instanceof DecisionEvent.QuestionAnsweredExternally e) {
            node.put("type", "QuestionAnsweredExternally");
            node.put("role", e.role().name());
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
            case "Contested" -> new DecisionEvent.Contested(readRoleKeyed(node.get("items"), JsonNode::asText));
            case "Classified" -> new DecisionEvent.Classified(readRoleKeyed(node.get("verdicts"), n -> Verdict.valueOf(n.asText())));
            case "Revised" -> new DecisionEvent.Revised(node.get("revisionText").asText());
            case "Rechecked" -> new DecisionEvent.Rechecked(
                    readRoleKeyed(node.get("verdicts"), n -> RecheckVerdict.valueOf(n.asText()))
            );
            case "QuestionAnsweredExternally" -> new DecisionEvent.QuestionAnsweredExternally(
                    Roles.byName(node.get("role").asText()),
                    node.get("answerText").asText(),
                    node.get("source").asText()
            );
            default -> throw new IllegalStateException("Unknown event type: " + type);
        };
    }

    private static <V> Map<Role, V> readRoleKeyed(JsonNode node, Function<JsonNode, V> valueReader) {
        Map<Role, V> result = new LinkedHashMap<>();
        node.fields().forEachRemaining(entry -> result.put(Roles.byName(entry.getKey()), valueReader.apply(entry.getValue())));
        return result;
    }
}
