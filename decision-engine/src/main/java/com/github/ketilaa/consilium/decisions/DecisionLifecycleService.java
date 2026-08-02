package com.github.ketilaa.consilium.decisions;

import com.github.ketilaa.consilium.decisions.port.ChatModel;
import com.github.ketilaa.consilium.decisions.port.DecisionEventPublisher;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Orchestrates propose -> contest -> classify -> revise -> targeted recheck ->
 * converge/escalate/blocked. Both validated fixes are the only behavior here, not options:
 * {@link #recheck} always asks the specific raising role about its own item, never a
 * generalist reclassifying everything from scratch; and {@link #resolveQuestionExternally}
 * is the one and only path that can clear a Question -- {@link #reviseSelfAnswerAttempt} and
 * {@link #reviseFinal} can never reach it, however confident the owner's text sounds.
 *
 * <p>Every applied event is also published via {@link DecisionEventPublisher} -- the real
 * integration seam for anything built on top of this later (a future event bus, a future
 * work-item graph). This service never needs to know who, if anyone, is listening.
 */
public final class DecisionLifecycleService {

    private final ChatModel chatModel;
    private final VerdictParser verdictParser;
    private final RecheckParser recheckParser;
    private final DecisionEventPublisher publisher;

    public DecisionLifecycleService(ChatModel chatModel) {
        this(chatModel, new TagScanningVerdictParser(), new TagScanningRecheckParser(), (id, event) -> { });
    }

    public DecisionLifecycleService(ChatModel chatModel, DecisionEventPublisher publisher) {
        this(chatModel, new TagScanningVerdictParser(), new TagScanningRecheckParser(), publisher);
    }

    public DecisionLifecycleService(
            ChatModel chatModel, VerdictParser verdictParser, RecheckParser recheckParser, DecisionEventPublisher publisher
    ) {
        this.chatModel = chatModel;
        this.verdictParser = verdictParser;
        this.recheckParser = recheckParser;
        this.publisher = publisher;
    }

    public void propose(Decision decision) {
        String proposal = chatModel.respond(LifecyclePrompts.ownerPropose(decision.ownerRole()), decisionBrief(decision));
        apply(decision, new DecisionEvent.Proposed(proposal));
    }

    /** Challengers react in their own words -- nothing here labels an item Issue or Question; classify() does. */
    public void contest(Decision decision, List<Role> challengerRoles) {
        String proposal = latestProposal(decision);
        Map<Role, String> raised = new LinkedHashMap<>();
        for (Role role : challengerRoles) {
            String reaction = chatModel.respond(
                    LifecyclePrompts.challenger(role),
                    decisionBrief(decision) + "\n\nProposed decision:\n" + proposal
            );
            raised.put(role, reaction);
        }
        apply(decision, new DecisionEvent.Contested(raised));
    }

    public void classify(Decision decision) {
        Map<Role, String> items = decision.state().raisedItems();
        if (items.isEmpty()) {
            apply(decision, new DecisionEvent.Classified(Map.of()));
            return;
        }
        List<Role> rolesInOrder = List.copyOf(items.keySet());
        String response = chatModel.respond(
                LifecyclePrompts.classify(),
                decisionBrief(decision) + "\n\nProposed decision:\n" + latestProposal(decision)
                        + "\n\nRaised items:\n" + itemsText(items)
        );
        apply(decision, new DecisionEvent.Classified(verdictParser.parse(response, rolesInOrder)));
    }

    public void reviseSelfAnswerAttempt(Decision decision) {
        DecisionState state = decision.state();
        String response = chatModel.respond(
                LifecyclePrompts.ownerRevise(decision.ownerRole()),
                decisionBrief(decision) + "\n\nYour original proposal:\n" + latestProposal(decision)
                        + "\n\nRaised items:\n" + itemsText(state.raisedItems())
        );
        apply(decision, new DecisionEvent.Revised(response));
    }

    /** Asks each still-open item's own raiser whether the latest revision resolves ITS item -- never a generalist. */
    public void recheck(Decision decision) {
        DecisionState state = decision.state();
        String latestRevision = latestRevision(decision);
        Map<Role, RecheckVerdict> rechecks = new LinkedHashMap<>();
        for (Map.Entry<Role, Verdict> entry : state.verdicts().entrySet()) {
            Role role = entry.getKey();
            Verdict verdict = entry.getValue();
            if (verdict == Verdict.NON_BLOCKING) {
                continue;
            }
            boolean isQuestion = verdict == Verdict.QUESTION;
            String systemPrompt = isQuestion ? LifecyclePrompts.questionRecheck(role) : LifecyclePrompts.issueRecheck(role);
            String label = isQuestion ? "question" : "concern";
            String response = chatModel.respond(
                    systemPrompt,
                    decisionBrief(decision) + "\n\nYour original " + label + ":\n" + state.raisedItems().get(role)
                            + "\n\nRevised decision:\n" + latestRevision
            );
            rechecks.put(role, recheckParser.parse(response));
        }
        apply(decision, new DecisionEvent.Rechecked(rechecks));
    }

    /**
     * The ONLY method that can construct a {@link DecisionEvent.QuestionAnsweredExternally}
     * event. There is no code path from {@link #reviseSelfAnswerAttempt} or
     * {@link #reviseFinal} to this method -- an owner's own revision text can never satisfy
     * this gate, no matter how the text reads.
     */
    public void resolveQuestionExternally(Decision decision, Role role, String answerText, String source) {
        Verdict verdict = decision.state().verdicts().get(role);
        if (verdict != Verdict.QUESTION) {
            throw new IllegalStateException(role + " is not currently classified QUESTION (was: " + verdict + ")");
        }
        apply(decision, new DecisionEvent.QuestionAnsweredExternally(role, answerText, source));
    }

    /** Only meaningful once at least one Question has been answered externally. */
    public void reviseFinal(Decision decision) {
        DecisionState state = decision.state();
        StringBuilder answers = new StringBuilder();
        for (Map.Entry<Role, String> entry : state.externalAnswers().entrySet()) {
            answers.append(entry.getKey()).append(": ").append(entry.getValue()).append('\n');
        }
        String response = chatModel.respond(
                LifecyclePrompts.ownerFinalRevision(decision.ownerRole()),
                decisionBrief(decision) + "\n\nYour original proposal:\n" + latestProposal(decision)
                        + "\n\nRaised items:\n" + itemsText(state.raisedItems())
                        + "\n\nExternally supplied answer(s) (NOT your own guess -- these came from "
                        + "outside this discussion):\n" + answers
        );
        apply(decision, new DecisionEvent.Revised(response));
    }

    private void apply(Decision decision, DecisionEvent event) {
        decision.apply(event);
        publisher.publish(decision.id(), event);
    }

    private static String decisionBrief(Decision decision) {
        return "Decision: " + decision.title() + "\n\nCategory: " + decision.category();
    }

    private static String itemsText(Map<Role, String> items) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<Role, String> entry : items.entrySet()) {
            sb.append(entry.getKey()).append(": ").append(entry.getValue()).append("\n\n");
        }
        return sb.toString().strip();
    }

    private static String latestProposal(Decision decision) {
        String proposal = null;
        for (DecisionEvent event : decision.events()) {
            if (event instanceof DecisionEvent.Proposed p) {
                proposal = p.proposalText();
            }
        }
        if (proposal == null) {
            throw new IllegalStateException("Decision has not been proposed yet");
        }
        return proposal;
    }

    private static String latestRevision(Decision decision) {
        String revision = null;
        for (DecisionEvent event : decision.events()) {
            if (event instanceof DecisionEvent.Revised r) {
                revision = r.revisionText();
            }
        }
        if (revision == null) {
            throw new IllegalStateException("Decision has not been revised yet");
        }
        return revision;
    }
}
