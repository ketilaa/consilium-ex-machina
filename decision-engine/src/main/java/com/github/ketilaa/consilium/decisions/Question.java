package com.github.ketilaa.consilium.decisions;

/** Read-model view of one item classified {@link Verdict#QUESTION}, for display. */
public record Question(ItemId itemId, String text, boolean answeredExternally, String answerText) {

    public Role role() {
        return itemId.role();
    }
}
