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

        if (!afterFirstRecheck.openQuestions().isEmpty()) {
            for (Question question : afterFirstRecheck.openQuestions()) {
                System.out.println("Open question (" + question.role() + "): " + question.text());
            }
            // In a real workflow this answer comes from a human or another system, not this
            // CLI -- hardcoded here only because this is a scripted demo. The point being
            // demonstrated is WHERE it comes from (a call the owner's own text can never
            // reach), not that it's realistic to hardcode it.
            service.resolveQuestionExternally(
                    decision,
                    questionRole,
                    "Legal confirmed the minimum contractual retention requirement is 3 years for "
                            + "enterprise customers under the current MSA.",
                    "Legal"
            );
            service.reviseFinal(decision);
            service.recheck(decision);
        }

        System.out.println("Final state: " + decision.state().status());
        repository.save(decision);
        System.out.println("Persisted to " + storeDir.resolve(id + ".jsonl"));
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
