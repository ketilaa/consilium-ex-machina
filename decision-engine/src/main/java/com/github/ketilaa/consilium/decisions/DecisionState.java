package com.github.ketilaa.consilium.decisions;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The current status and derived detail of a Decision, computed by folding its event
 * history. This is a pure projection -- nothing here is ever stored directly; re-deriving
 * it from the same event list always produces the same result.
 */
public record DecisionState(
        DecisionStatus status,
        Map<ItemId, String> raisedItems,
        Map<ItemId, Verdict> verdicts,
        Map<ItemId, RecheckVerdict> rechecks,
        Map<ItemId, String> externalAnswers,
        int revisionRounds
) {

    public static DecisionState fold(List<DecisionEvent> events) {
        Map<ItemId, String> items = null;
        Map<ItemId, Verdict> verdicts = null;
        Map<ItemId, RecheckVerdict> rechecks = new LinkedHashMap<>();
        Map<ItemId, String> externalAnswers = new LinkedHashMap<>();
        int revisionRounds = 0;

        for (DecisionEvent event : events) {
            if (event instanceof DecisionEvent.Contested contested) {
                items = contested.items();
            } else if (event instanceof DecisionEvent.Classified classified) {
                verdicts = classified.verdicts();
            } else if (event instanceof DecisionEvent.Revised) {
                revisionRounds++;
            } else if (event instanceof DecisionEvent.Rechecked rechecked) {
                rechecks = new LinkedHashMap<>(rechecked.verdicts());
            } else if (event instanceof DecisionEvent.QuestionAnsweredExternally answered) {
                externalAnswers.put(answered.itemId(), answered.answerText());
                // A recheck computed before this answer arrived judged the raiser's own
                // question, not this answer -- it can't count as confirming resolution
                // of an answer it never saw. Clear it until a fresh Rechecked event
                // (which the service always issues right after answering) supersedes it.
                rechecks.remove(answered.itemId());
            }
        }

        DecisionStatus status = deriveStatus(items, verdicts, rechecks, externalAnswers, revisionRounds);
        return new DecisionState(
                status,
                items == null ? Map.of() : items,
                verdicts == null ? Map.of() : verdicts,
                // Collections.unmodifiableMap, not Map.copyOf -- Map.copyOf does not
                // preserve insertion order, which silently broke positional item
                // attribution in TagScanningVerdictParser once already.
                Collections.unmodifiableMap(rechecks),
                Collections.unmodifiableMap(externalAnswers),
                revisionRounds
        );
    }

    private static DecisionStatus deriveStatus(
            Map<ItemId, String> items,
            Map<ItemId, Verdict> verdicts,
            Map<ItemId, RecheckVerdict> rechecks,
            Map<ItemId, String> externalAnswers,
            int revisionRounds
    ) {
        if (items == null) {
            return DecisionStatus.PROPOSED;
        }
        if (verdicts == null) {
            return DecisionStatus.CONTESTED;
        }

        List<ItemId> blocking = itemsWithVerdict(verdicts, Verdict.BLOCKING);
        List<ItemId> questions = itemsWithVerdict(verdicts, Verdict.QUESTION);

        if (blocking.isEmpty() && questions.isEmpty()) {
            return DecisionStatus.CONVERGED;
        }
        if (revisionRounds == 0) {
            return DecisionStatus.CONTESTED;
        }

        boolean anyQuestionUnanswered = questions.stream().anyMatch(id -> !externalAnswers.containsKey(id));
        if (anyQuestionUnanswered) {
            return DecisionStatus.BLOCKED_ON_QUESTION;
        }

        boolean allResolved = concat(blocking, questions).stream()
                .allMatch(id -> rechecks.get(id) == RecheckVerdict.RESOLVED);
        return allResolved ? DecisionStatus.CONVERGED : DecisionStatus.ESCALATED_TO_HUMAN;
    }

    private static List<ItemId> itemsWithVerdict(Map<ItemId, Verdict> verdicts, Verdict target) {
        List<ItemId> ids = new ArrayList<>();
        for (Map.Entry<ItemId, Verdict> entry : verdicts.entrySet()) {
            if (entry.getValue() == target) {
                ids.add(entry.getKey());
            }
        }
        return ids;
    }

    private static List<ItemId> concat(List<ItemId> a, List<ItemId> b) {
        List<ItemId> all = new ArrayList<>(a);
        all.addAll(b);
        return all;
    }

    /** Every item classified {@link Verdict#QUESTION}, with its current answer status. */
    public List<Question> questions() {
        List<Question> result = new ArrayList<>();
        for (Map.Entry<ItemId, Verdict> entry : verdicts.entrySet()) {
            if (entry.getValue() == Verdict.QUESTION) {
                ItemId id = entry.getKey();
                String answer = externalAnswers.get(id);
                result.add(new Question(id, raisedItems.get(id), answer != null, answer));
            }
        }
        return result;
    }

    public List<Question> openQuestions() {
        return questions().stream().filter(q -> !q.answeredExternally()).toList();
    }
}
