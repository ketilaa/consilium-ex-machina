package com.github.ketilaa.consilium.workitems.adapter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.workitems.Owner;
import com.github.ketilaa.consilium.workitems.WorkItemEvent;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import com.github.ketilaa.consilium.workitems.WorkItemKind;

/**
 * Manual mapping between {@link WorkItemEvent} and JSON, kept in the adapter layer instead of
 * annotating the domain records -- same rationale as decisions.adapter.DecisionEventCodec.
 */
final class WorkItemEventCodec {

    private final ObjectMapper mapper;

    WorkItemEventCodec(ObjectMapper mapper) {
        this.mapper = mapper;
    }

    ObjectNode toJson(WorkItemEvent event) {
        ObjectNode node = mapper.createObjectNode();
        if (event instanceof WorkItemEvent.Created e) {
            node.put("type", "Created");
            node.put("kind", e.kind().name());
            node.put("title", e.title());
            node.put("description", e.description());
            node.put("parentId", e.parentId() == null ? null : e.parentId().value());
            node.put("owner", e.owner().value());
        } else if (event instanceof WorkItemEvent.Retitled e) {
            node.put("type", "Retitled");
            node.put("newTitle", e.newTitle());
        } else if (event instanceof WorkItemEvent.DescriptionUpdated e) {
            node.put("type", "DescriptionUpdated");
            node.put("newDescription", e.newDescription());
        } else if (event instanceof WorkItemEvent.Reparented e) {
            node.put("type", "Reparented");
            node.put("newParentId", e.newParentId() == null ? null : e.newParentId().value());
        } else {
            throw new IllegalStateException("Unhandled event type: " + event.getClass());
        }
        return node;
    }

    WorkItemEvent fromJson(JsonNode node) {
        String type = node.get("type").asText();
        return switch (type) {
            case "Created" -> new WorkItemEvent.Created(
                    WorkItemKind.valueOf(node.get("kind").asText()),
                    node.get("title").asText(),
                    node.get("description").asText(),
                    readOptionalWorkItemId(node.get("parentId")),
                    new Owner(node.get("owner").asText())
            );
            case "Retitled" -> new WorkItemEvent.Retitled(node.get("newTitle").asText());
            case "DescriptionUpdated" -> new WorkItemEvent.DescriptionUpdated(node.get("newDescription").asText());
            case "Reparented" -> new WorkItemEvent.Reparented(readOptionalWorkItemId(node.get("newParentId")));
            default -> throw new IllegalStateException("Unknown event type: " + type);
        };
    }

    private static WorkItemId readOptionalWorkItemId(JsonNode node) {
        return node == null || node.isNull() ? null : new WorkItemId(node.asText());
    }
}
