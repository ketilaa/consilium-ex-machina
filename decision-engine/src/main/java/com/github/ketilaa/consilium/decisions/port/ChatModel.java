package com.github.ketilaa.consilium.decisions.port;

/**
 * A single-turn chat call to an LLM. Deliberately provider-agnostic: one system prompt, one
 * user message, one response string in, nothing else. Nothing in the domain knows what's on
 * the other side of this call -- matches "the role registry, not the model, defines what an
 * agent is allowed to do" from docs/high-level-architecture.md.
 */
public interface ChatModel {
    String respond(String systemPrompt, String userMessage);
}
