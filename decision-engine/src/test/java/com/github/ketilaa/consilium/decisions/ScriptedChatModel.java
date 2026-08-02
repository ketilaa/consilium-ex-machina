package com.github.ketilaa.consilium.decisions;

import com.github.ketilaa.consilium.decisions.port.ChatModel;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/** A deterministic test double: returns canned responses in the exact order scripted, and fails loudly if exhausted. */
final class ScriptedChatModel implements ChatModel {

    private final Deque<String> responses;
    private final List<String> systemPromptsSeen = new ArrayList<>();

    ScriptedChatModel(String... responses) {
        this.responses = new ArrayDeque<>(List.of(responses));
    }

    @Override
    public String respond(String systemPrompt, String userMessage) {
        systemPromptsSeen.add(systemPrompt);
        if (responses.isEmpty()) {
            throw new IllegalStateException("ScriptedChatModel exhausted -- unexpected extra call with system prompt: " + systemPrompt);
        }
        return responses.poll();
    }

    List<String> systemPromptsSeen() {
        return List.copyOf(systemPromptsSeen);
    }
}
