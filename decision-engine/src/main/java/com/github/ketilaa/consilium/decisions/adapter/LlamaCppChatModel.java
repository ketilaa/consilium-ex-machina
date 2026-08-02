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
        this(baseUrl, model, 0.3, 700);
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
                    .timeout(Duration.ofSeconds(180))
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
