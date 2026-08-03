package com.github.ketilaa.consilium.decisions.cli;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionRunner;
import com.github.ketilaa.consilium.decisions.ItemId;
import com.github.ketilaa.consilium.decisions.OriginReference;
import com.github.ketilaa.consilium.decisions.Question;
import com.github.ketilaa.consilium.decisions.Role;
import com.github.ketilaa.consilium.decisions.Roles;
import com.github.ketilaa.consilium.decisions.adapter.FileDecisionRepository;
import com.github.ketilaa.consilium.decisions.adapter.LlamaCppChatModel;
import com.github.ketilaa.consilium.decisions.adapter.LoggingEventPublisher;
import com.github.ketilaa.consilium.decisions.port.ChatModel;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * {@code run} walks a decision through propose/contest/classify/revise/recheck against a real
 * local model and persists it; {@code answer} resolves one open Question with a real,
 * externally-sourced answer whenever it becomes available; {@code show} reloads a decision from
 * disk; {@code retry} re-runs the final revision and recheck with no new answer, for when the
 * prior attempt failed for a reason unrelated to the decision's own content (see
 * {@link DecisionRunner#retryFinalRevision}). Real content (title, context) should come from a
 * Work Item wherever one exists -- see work-items' {@code WorkItemCli propose-decision}, which
 * sources both from the work item's own stored fields and calls the same {@link DecisionRunner}
 * this CLI uses. {@code run} here is for standalone decisions with no work item behind them (or
 * the original demo scenario, unchanged, when no {@code --title} is given).
 */
public final class DecisionEngineCli {

    public static void main(String[] args) {
        if (args.length == 0) {
            printUsage();
            return;
        }

        Path storeDir = Path.of(
                System.getenv().getOrDefault("DECISION_ENGINE_STORE_DIR", "platform-dogfooding/decisions")
        );
        DecisionRepository repository = new FileDecisionRepository(storeDir);

        switch (args[0]) {
            case "run" -> run(repository, storeDir, parseOriginFlag(args));
            case "answer" -> {
                if (args.length < 5) {
                    System.err.println("Usage: answer <decision-id> <item-id> <answer-text> <source>");
                    System.exit(1);
                    return;
                }
                answer(repository, args[1], args[2], args[3], args[4]);
            }
            case "show" -> {
                if (args.length < 2) {
                    System.err.println("Usage: show <decision-id>");
                    System.exit(1);
                    return;
                }
                show(repository, args[1]);
            }
            case "retry" -> {
                if (args.length < 2) {
                    System.err.println("Usage: retry <decision-id>");
                    System.exit(1);
                    return;
                }
                retry(repository, args[1]);
            }
            default -> printUsage();
        }
    }

    /** {@code run --origin work-item:feat-1} attaches the decision to a real work item; defaults to "cli:demo". */
    private static String parseOriginFlag(String[] args) {
        for (int i = 1; i < args.length - 1; i++) {
            if (args[i].equals("--origin")) {
                return args[i + 1];
            }
        }
        return "cli:demo";
    }

    private static ChatModel buildChatModel() {
        String baseUrl = System.getenv().getOrDefault("DECISION_ENGINE_MODEL_BASE_URL", "http://localhost:8081");
        String modelName = System.getenv().getOrDefault(
                "DECISION_ENGINE_MODEL_NAME", "bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF"
        );
        System.out.println("Using model " + modelName + " at " + baseUrl);
        return new LlamaCppChatModel(baseUrl, modelName);
    }

    private static void run(DecisionRepository repository, Path storeDir, String originValue) {
        DecisionRunner runner = new DecisionRunner(buildChatModel(), new LoggingEventPublisher(), repository);

        Role owner = Roles.RELEASE_MANAGER;
        Role issueRole = Roles.BACKEND_DEVELOPER;
        Role questionRole = Roles.SECURITY_REVIEWER;
        String id = "d-" + UUID.randomUUID().toString().substring(0, 8);

        Decision decision = new Decision(
                id,
                "How long should the platform retain its Decision/Question/Event history (the audit "
                        + "log) before it can be purged or archived, and where should it be stored?",
                "This platform's decisions, questions, and events are meant to be the durable, "
                        + "audited record of engineering choices -- the whole point of making decisions "
                        + "first-class is having a trustworthy history of what was decided and why. "
                        + "Before implementation, decide on a retention policy: how long history is kept "
                        + "before it can be purged or archived, and where it's stored.",
                "Compliance / data retention",
                owner,
                new OriginReference(originValue)
        );

        System.out.println("Decision " + id + " proposed (owner: " + owner + ")");
        runner.run(decision, List.of(issueRole, questionRole));
        reportOutcome(decision, storeDir, id);
    }

    private static void answer(DecisionRepository repository, String decisionId, String itemIdValue, String answerText, String source) {
        Optional<Decision> found = repository.findById(decisionId);
        if (found.isEmpty()) {
            System.err.println("No decision found with id " + decisionId);
            System.exit(1);
            return;
        }

        DecisionRunner runner = new DecisionRunner(buildChatModel(), new LoggingEventPublisher(), repository);
        Decision decision = found.get();
        ItemId itemId = ItemId.parse(itemIdValue);
        runner.answerQuestion(decision, itemId, answerText, source);

        System.out.println("Final state: " + decision.state().status());
        printStillOpen(decision);
    }

    private static void retry(DecisionRepository repository, String decisionId) {
        Optional<Decision> found = repository.findById(decisionId);
        if (found.isEmpty()) {
            System.err.println("No decision found with id " + decisionId);
            System.exit(1);
            return;
        }

        DecisionRunner runner = new DecisionRunner(buildChatModel(), new LoggingEventPublisher(), repository);
        Decision decision = found.get();
        runner.retryFinalRevision(decision);

        System.out.println("Final state: " + decision.state().status());
        printStillOpen(decision);
    }

    private static void reportOutcome(Decision decision, Path storeDir, String id) {
        System.out.println("State: " + decision.state().status());
        for (Question question : decision.state().openQuestions()) {
            System.out.println("Open question (" + question.itemId() + "): " + question.text());
        }
        printStillOpen(decision);
        System.out.println("Persisted to " + storeDir.resolve(id + ".jsonl"));
        System.out.println(
                "To answer an open question: DecisionEngineCli answer " + id + " \"<item-id>\" \"<answer>\" \"<source>\""
        );
    }

    private static void printStillOpen(Decision decision) {
        List<Question> stillOpen = decision.state().openQuestions();
        if (!stillOpen.isEmpty()) {
            System.out.println("Still open:");
            for (Question question : stillOpen) {
                System.out.println("  - " + question.itemId() + ": " + question.text());
            }
        }
    }

    private static void show(DecisionRepository repository, String id) {
        Optional<Decision> found = repository.findById(id);
        if (found.isEmpty()) {
            System.err.println("No decision found with id " + id);
            System.exit(1);
            return;
        }

        Decision decision = found.get();
        System.out.println("Decision " + decision.id() + ": " + decision.title());
        System.out.println("Category: " + decision.category() + " | Owner: " + decision.ownerRole());
        System.out.println("Origin: " + decision.origin());
        System.out.println();

        LoggingEventPublisher printer = new LoggingEventPublisher();
        for (var event : decision.events()) {
            printer.publish(decision.id(), event);
        }

        System.out.println();
        System.out.println("Status: " + decision.state().status());
    }

    private static void printUsage() {
        System.out.println("Usage: DecisionEngineCli run [--origin <origin-reference>]");
        System.out.println("       DecisionEngineCli answer <decision-id> <item-id> <answer-text> <source>");
        System.out.println("       DecisionEngineCli show <decision-id>");
        System.out.println("       DecisionEngineCli retry <decision-id>  (re-runs the final revision + recheck, e.g. after a truncated response)");
    }
}
