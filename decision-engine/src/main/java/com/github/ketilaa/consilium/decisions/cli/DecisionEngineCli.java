package com.github.ketilaa.consilium.decisions.cli;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionLifecycleService;
import com.github.ketilaa.consilium.decisions.DecisionState;
import com.github.ketilaa.consilium.decisions.DecisionStatus;
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
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

/**
 * {@code run} walks one real decision through the full lifecycle against a real local model
 * and persists it; {@code show <id>} reloads it from disk. This is the demo deliverable: the
 * PoC's proof of a Question structurally blocking convergence, but as real, reusable,
 * persisted platform code rather than a script that prints a transcript and exits.
 */
public final class DecisionEngineCli {

    public static void main(String[] args) {
        if (args.length == 0) {
            printUsage();
            return;
        }

        Path storeDir = Path.of(System.getenv().getOrDefault("DECISION_ENGINE_STORE_DIR", ".decisions"));
        DecisionRepository repository = new FileDecisionRepository(storeDir);

        switch (args[0]) {
            case "run" -> run(repository, storeDir);
            case "show" -> {
                if (args.length < 2) {
                    System.err.println("Usage: show <decision-id>");
                    System.exit(1);
                    return;
                }
                show(repository, args[1]);
            }
            default -> printUsage();
        }
    }

    private static void run(DecisionRepository repository, Path storeDir) {
        String baseUrl = System.getenv().getOrDefault("DECISION_ENGINE_MODEL_BASE_URL", "http://localhost:8081");
        String modelName = System.getenv().getOrDefault(
                "DECISION_ENGINE_MODEL_NAME", "bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF"
        );
        System.out.println("Using model " + modelName + " at " + baseUrl);

        ChatModel chatModel = new LlamaCppChatModel(baseUrl, modelName);
        DecisionLifecycleService service = new DecisionLifecycleService(chatModel, new LoggingEventPublisher());

        Role owner = Roles.RELEASE_MANAGER;
        Role issueRole = Roles.BACKEND_DEVELOPER;
        Role questionRole = Roles.SECURITY_REVIEWER;
        String id = "d-" + UUID.randomUUID().toString().substring(0, 8);

        Decision decision = new Decision(
                id,
                "How long should the platform retain its Decision/Question/Event history (the audit "
                        + "log) before it can be purged or archived, and where should it be stored?",
                "Compliance / data retention",
                owner,
                new OriginReference("cli:demo")
        );

        System.out.println("Decision " + id + " proposed (owner: " + owner + ")");
        service.propose(decision);

        service.contest(decision, List.of(issueRole, questionRole));
        service.classify(decision);

        if (decision.state().status() == DecisionStatus.CONVERGED) {
            System.out.println("Converged with nothing blocking.");
            repository.save(decision);
            return;
        }

        service.reviseSelfAnswerAttempt(decision);
        service.recheck(decision);

        DecisionState afterFirstRecheck = decision.state();
        System.out.println("State: " + afterFirstRecheck.status());

        List<Question> openQuestions = afterFirstRecheck.openQuestions();
        if (!openQuestions.isEmpty()) {
            boolean answeredAny = false;
            for (Question question : openQuestions) {
                System.out.println("Open question (" + question.itemId() + "): " + question.text());
                // In a real workflow an answer comes from a human or another system, not
                // this CLI -- a small set of prepared answers is hardcoded here only
                // because this is a scripted demo. Each open item is matched against them
                // independently: answering one never resolves another, even one raised by
                // the same role, and an item matching nothing prepared is left genuinely
                // open rather than forced to a canned answer it doesn't actually fit.
                Optional<PreparedAnswer> match = findPreparedAnswer(question.text());
                if (match.isPresent()) {
                    PreparedAnswer answer = match.get();
                    service.resolveQuestionExternally(decision, question.itemId(), answer.text(), answer.source());
                    answeredAny = true;
                } else {
                    System.out.println("  -- left open: no prepared answer matches this demo's known topics");
                }
            }
            if (answeredAny) {
                service.reviseFinal(decision);
                service.recheck(decision);
            }
        }

        DecisionState finalState = decision.state();
        System.out.println("Final state: " + finalState.status());
        if (!finalState.openQuestions().isEmpty()) {
            System.out.println("Still open:");
            for (Question question : finalState.openQuestions()) {
                System.out.println("  - " + question.itemId() + ": " + question.text());
            }
        }
        repository.save(decision);
        System.out.println("Persisted to " + storeDir.resolve(id + ".jsonl"));
    }

    /** A tiny set of demo-only answers for the fixed scenario this CLI runs -- not a general mechanism. */
    private record PreparedAnswer(List<String> keywords, String text, String source) {
    }

    private static final List<PreparedAnswer> PREPARED_ANSWERS = List.of(
            new PreparedAnswer(
                    List.of("retention period", "retention requirement", "regulatory requirement"),
                    "Legal confirmed the minimum contractual retention requirement is 3 years for "
                            + "enterprise customers under the current MSA.",
                    "Legal"
            ),
            new PreparedAnswer(
                    List.of("cost implication", "cost of storing", "pricing model", "budget"),
                    "Finance approved a budget ceiling that fully covers cold-storage costs for the "
                            + "expected data volume over the full retention period.",
                    "Finance"
            )
    );

    private static Optional<PreparedAnswer> findPreparedAnswer(String questionText) {
        String lower = questionText.toLowerCase(Locale.ROOT);
        return PREPARED_ANSWERS.stream()
                .filter(answer -> answer.keywords().stream().anyMatch(lower::contains))
                .findFirst();
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
        System.out.println("Usage: DecisionEngineCli <run|show> [decision-id]");
    }
}
