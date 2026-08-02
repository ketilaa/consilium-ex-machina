package com.github.ketilaa.consilium.decisions;

/** Read-model view of a raised item classified {@link Verdict#QUESTION}, for display. */
public record Question(Role role, String text, boolean answeredExternally, String answerText) {
}
