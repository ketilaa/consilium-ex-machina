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
        Map<Role, String> raisedItems,
        Map<Role, Verdict> verdicts,
        Map<Role, RecheckVerdict> rechecks,
        Map<Role, String> externalAnswers,
        int revisionRounds
) {

    public static DecisionState fold(List<DecisionEvent> events) {
        Map<Role, String> items = null;
        Map<Role, Verdict> verdicts = null;
        Map<Role, RecheckVerdict> rechecks = new LinkedHashMap<>();
        Map<Role, String> externalAnswers = new LinkedHashMap<>();
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
                externalAnswers.put(answered.role(), answered.answerText());
                // A recheck computed before this answer arrived judged the raiser's own
                // question, not this answer -- it can't count as confirming resolution
                // of an answer it never saw. Clear it until a fresh Rechecked event
                // (which the service always issues right after answering) supersedes it.
                rechecks.remove(answered.role());
            }
        }

        DecisionStatus status = deriveStatus(items, verdicts, rechecks, externalAnswers, revisionRounds);
        return new DecisionState(
                status,
                items == null ? Map.of() : items,
                verdicts == null ? Map.of() : verdicts,
                // Collections.unmodifiableMap, not Map.copyOf -- Map.copyOf does not
                // preserve insertion order, which silently broke positional role
                // attribution in TagScanningVerdictParser once already.
                Collections.unmodifiableMap(rechecks),
                Collections.unmodifiableMap(externalAnswers),
                revisionRounds
        );
    }

    private static DecisionStatus deriveStatus(
            Map<Role, String> items,
            Map<Role, Verdict> verdicts,
            Map<Role, RecheckVerdict> rechecks,
            Map<Role, String> externalAnswers,
            int revisionRounds
    ) {
        if (items == null) {
            return DecisionStatus.PROPOSED;
        }
        if (verdicts == null) {
            return DecisionStatus.CONTESTED;
        }

        List<Role> blocking = rolesWithVerdict(verdicts, Verdict.BLOCKING);
        List<Role> questions = rolesWithVerdict(verdicts, Verdict.QUESTION);

        if (blocking.isEmpty() && questions.isEmpty()) {
            return DecisionStatus.CONVERGED;
        }
        if (revisionRounds == 0) {
            return DecisionStatus.CONTESTED;
        }

        boolean anyQuestionUnanswered = questions.stream().anyMatch(role -> !externalAnswers.containsKey(role));
        if (anyQuestionUnanswered) {
            return DecisionStatus.BLOCKED_ON_QUESTION;
        }

        boolean allResolved = concat(blocking, questions).stream()
                .allMatch(role -> rechecks.get(role) == RecheckVerdict.RESOLVED);
        return allResolved ? DecisionStatus.CONVERGED : DecisionStatus.ESCALATED_TO_HUMAN;
    }

    private static List<Role> rolesWithVerdict(Map<Role, Verdict> verdicts, Verdict target) {
        List<Role> roles = new ArrayList<>();
        for (Map.Entry<Role, Verdict> entry : verdicts.entrySet()) {
            if (entry.getValue() == target) {
                roles.add(entry.getKey());
            }
        }
        return roles;
    }

    private static List<Role> concat(List<Role> a, List<Role> b) {
        List<Role> all = new ArrayList<>(a);
        all.addAll(b);
        return all;
    }

    /** Every item classified {@link Verdict#QUESTION}, with its current answer status. */
    public List<Question> questions() {
        List<Question> result = new ArrayList<>();
        for (Map.Entry<Role, Verdict> entry : verdicts.entrySet()) {
            if (entry.getValue() == Verdict.QUESTION) {
                Role role = entry.getKey();
                String answer = externalAnswers.get(role);
                result.add(new Question(role, raisedItems.get(role), answer != null, answer));
            }
        }
        return result;
    }

    public List<Question> openQuestions() {
        return questions().stream().filter(q -> !q.answeredExternally()).toList();
    }
}
