package com.github.ketilaa.consilium.decisions.adapter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.github.ketilaa.consilium.decisions.port.ChatModel;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;

/**
 * HTTP adapter to the same local llama.cpp OpenAI-compatible endpoint (/v1/chat/completions)
 * validated across every proof-of-concept. Nothing in the domain knows this is what's on the
 * other end of {@link ChatModel}.
 */
public final class LlamaCppChatModel implements ChatModel {

    private final String baseUrl;
    private final String model;
    private final double temperature;
    private final int maxTokens;
    private final HttpClient client = HttpClient.newHttpClient();
    private final ObjectMapper mapper = new ObjectMapper();

    public LlamaCppChatModel(String baseUrl, String model) {
        // 700 silently truncated a real revision mid-sentence on d-22ffab13 (12 raised items to
        // address in one response) -- caught only because a human review of the escalated
        // decision noticed the stored text ended at "11" with nothing after it. This interface
        // has no per-call budget (see ChatModel's Javadoc), so the default has to cover the
        // heaviest call, not the lightest.
        this(baseUrl, model, 0.3, 2000);
    }

    public LlamaCppChatModel(String baseUrl, String model, double temperature, int maxTokens) {
        this.baseUrl = baseUrl;
        this.model = model;
        this.temperature = temperature;
        this.maxTokens = maxTokens;
    }

    @Override
    public String respond(String systemPrompt, String userMessage) {
        ObjectNode payload = mapper.createObjectNode();
        payload.put("model", model);
        payload.put("temperature", temperature);
        payload.put("max_tokens", maxTokens);
        var messages = payload.putArray("messages");
        messages.addObject().put("role", "system").put("content", systemPrompt);
        messages.addObject().put("role", "user").put("content", userMessage);

        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/v1/chat/completions"))
                    .header("Content-Type", "application/json")
                    // 180s fit the 700-token default; raising the token budget to 2000 (see the
                    // 2-arg constructor) pushed a real generation past it -- caught live on the
                    // very first retry after that fix. Scaled up with margin, not tuned tightly,
                    // since local-model throughput varies with what else is running.
                    .timeout(Duration.ofSeconds(600))
                    .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(payload)))
                    .build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() != 200) {
                throw new IllegalStateException(
                        "Chat completion failed (HTTP " + response.statusCode() + "): " + response.body()
                );
            }
            JsonNode root = mapper.readTree(response.body());
            return root.at("/choices/0/message/content").asText().strip();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException("Interrupted while waiting for a chat completion", e);
        }
    }
}
