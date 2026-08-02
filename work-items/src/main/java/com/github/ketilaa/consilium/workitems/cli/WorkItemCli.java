package com.github.ketilaa.consilium.workitems.cli;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionRunner;
import com.github.ketilaa.consilium.decisions.Question;
import com.github.ketilaa.consilium.decisions.Role;
import com.github.ketilaa.consilium.decisions.Roles;
import com.github.ketilaa.consilium.decisions.adapter.FileDecisionRepository;
import com.github.ketilaa.consilium.decisions.adapter.LlamaCppChatModel;
import com.github.ketilaa.consilium.decisions.adapter.LoggingEventPublisher;
import com.github.ketilaa.consilium.decisions.port.ChatModel;
import com.github.ketilaa.consilium.decisions.port.DecisionRepository;
import com.github.ketilaa.consilium.workitems.Owner;
import com.github.ketilaa.consilium.workitems.WorkItem;
import com.github.ketilaa.consilium.workitems.WorkItemDecisionsView;
import com.github.ketilaa.consilium.workitems.WorkItemEvent;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import com.github.ketilaa.consilium.workitems.WorkItemKind;
import com.github.ketilaa.consilium.workitems.WorkItemState;
import com.github.ketilaa.consilium.workitems.adapter.FileWorkItemRepository;
import com.github.ketilaa.consilium.workitems.port.WorkItemRepository;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

/**
 * {@code create}/{@code reparent}/{@code update-description} manage a Work Item's own stored
 * fields; {@code show} prints it plus every Decision related to it and their still-open
 * Questions -- the concrete proof that "related decisions" and "open questions"
 * (docs/high-level-architecture.md) are real, queryable facts, not just prose.
 * {@code propose-decision} is the real way to attach a Decision to a Work Item: it reads the
 * work item's own stored title and description and uses THEM as the Decision's title and
 * context, rather than retyping the same information disconnected from the work item's own
 * record. Use {@code DecisionEngineCli answer} afterward to resolve any open Question.
 */
public final class WorkItemCli {

    public static void main(String[] args) {
        if (args.length == 0) {
            printUsage();
            return;
        }

        Path storeDir = Path.of(System.getenv().getOrDefault("WORK_ITEM_STORE_DIR", "platform-dogfooding/work-items"));
        WorkItemRepository repository = new FileWorkItemRepository(storeDir);

        Path decisionsStoreDir = Path.of(
                System.getenv().getOrDefault("DECISION_ENGINE_STORE_DIR", "platform-dogfooding/decisions")
        );
        DecisionRepository decisionRepository = new FileDecisionRepository(decisionsStoreDir);
        WorkItemDecisionsView view = new WorkItemDecisionsView(decisionRepository);

        switch (args[0]) {
            case "create" -> {
                if (args.length < 3) {
                    System.err.println("Usage: create <kind> <title> [--parent <work-item-id>]");
                    System.exit(1);
                    return;
                }
                create(repository, args[1], args[2], parseParentFlag(args));
            }
            case "reparent" -> {
                if (args.length < 3) {
                    System.err.println("Usage: reparent <work-item-id> <new-parent-id>");
                    System.exit(1);
                    return;
                }
                reparent(repository, args[1], args[2]);
            }
            case "update-description" -> {
                if (args.length < 3) {
                    System.err.println("Usage: update-description <work-item-id> <description-text>");
                    System.exit(1);
                    return;
                }
                updateDescription(repository, args[1], args[2]);
            }
            case "propose-decision" -> {
                if (args.length < 2) {
                    printProposeDecisionUsage();
                    System.exit(1);
                    return;
                }
                proposeDecision(repository, decisionRepository, args[1], args);
            }
            case "show" -> {
                if (args.length < 2) {
                    System.err.println("Usage: show <work-item-id>");
                    System.exit(1);
                    return;
                }
                show(repository, view, args[1]);
            }
            default -> printUsage();
        }
    }

    /** {@code --parent <work-item-id>} nests the new item under an existing one; unset means top-level (e.g. an Initiative). */
    private static WorkItemId parseParentFlag(String[] args) {
        String value = parseFlag(args, "--parent");
        return value == null ? null : new WorkItemId(value);
    }

    private static String parseFlag(String[] args, String flag) {
        for (int i = 1; i < args.length - 1; i++) {
            if (args[i].equals(flag)) {
                return args[i + 1];
            }
        }
        return null;
    }

    private static List<String> parseRepeatedFlag(String[] args, String flag) {
        List<String> values = new ArrayList<>();
        for (int i = 1; i < args.length - 1; i++) {
            if (args[i].equals(flag)) {
                values.add(args[i + 1]);
            }
        }
        return values;
    }

    private static void create(WorkItemRepository repository, String kindArg, String title, WorkItemId parentId) {
        WorkItemKind kind;
        try {
            kind = WorkItemKind.valueOf(kindArg.toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            System.err.println("Unknown kind '" + kindArg + "' -- expected one of " + List.of(WorkItemKind.values()));
            System.exit(1);
            return;
        }

        String id = kindPrefix(kind) + "-" + UUID.randomUUID().toString().substring(0, 8);
        WorkItemId workItemId = new WorkItemId(id);
        WorkItem workItem = new WorkItem(workItemId);
        workItem.apply(new WorkItemEvent.Created(kind, title, title, parentId, new Owner("human:cli")));
        repository.save(workItem);

        System.out.println("Created " + kind + " " + id + ": " + title + (parentId == null ? "" : " (under " + parentId + ")"));
        System.out.println("Give it real context, then propose a decision from it:");
        System.out.println("  WorkItemCli update-description " + id + " \"<real background/context text>\"");
        System.out.println(
                "  WorkItemCli propose-decision " + id + " --category <category> --owner <role> --challenger <role>"
        );
    }

    private static void reparent(WorkItemRepository repository, String idValue, String newParentValue) {
        WorkItem workItem = requireFound(repository, idValue);
        if (workItem == null) {
            return;
        }
        workItem.apply(new WorkItemEvent.Reparented(new WorkItemId(newParentValue)));
        repository.save(workItem);
        System.out.println(idValue + " reparented under " + newParentValue);
    }

    private static void updateDescription(WorkItemRepository repository, String idValue, String description) {
        WorkItem workItem = requireFound(repository, idValue);
        if (workItem == null) {
            return;
        }
        workItem.apply(new WorkItemEvent.DescriptionUpdated(description));
        repository.save(workItem);
        System.out.println(idValue + " description updated");
    }

    /**
     * The real way to attach a Decision to a Work Item: sources the Decision's title and
     * context from the work item's own stored fields (set via {@code update-description}) --
     * not from flags re-typed at invocation time, disconnected from the work item's own record.
     */
    private static void proposeDecision(
            WorkItemRepository repository, DecisionRepository decisionRepository, String idValue, String[] args
    ) {
        WorkItemId id = new WorkItemId(idValue);
        Optional<WorkItem> found = repository.findById(id);
        if (found.isEmpty()) {
            System.err.println("No work item found with id " + idValue);
            System.exit(1);
            return;
        }
        WorkItemState state = found.get().state();

        String category = parseFlag(args, "--category");
        String ownerName = parseFlag(args, "--owner");
        List<String> challengerNames = parseRepeatedFlag(args, "--challenger");
        if (category == null || ownerName == null || challengerNames.isEmpty()) {
            printProposeDecisionUsage();
            System.exit(1);
            return;
        }

        Role owner;
        List<Role> challengers;
        try {
            owner = Roles.byName(ownerName);
            challengers = challengerNames.stream().map(Roles::byName).toList();
        } catch (IllegalArgumentException e) {
            System.err.println(e.getMessage());
            System.exit(1);
            return;
        }

        String decisionId = "d-" + UUID.randomUUID().toString().substring(0, 8);
        Decision decision = new Decision(
                decisionId, state.title(), state.description(), category, owner,
                WorkItemDecisionsView.originReferenceFor(id)
        );

        DecisionRunner runner = new DecisionRunner(buildChatModel(), new LoggingEventPublisher(), decisionRepository);
        System.out.println("Decision " + decisionId + " proposed (owner: " + owner + ") for work item " + id);
        runner.run(decision, challengers);

        System.out.println("State: " + decision.state().status());
        for (Question question : decision.state().openQuestions()) {
            System.out.println("Open question (" + question.itemId() + "): " + question.text());
        }
        System.out.println(
                "To answer an open question: DecisionEngineCli answer " + decisionId + " \"<item-id>\" \"<answer>\" \"<source>\""
        );
    }

    private static ChatModel buildChatModel() {
        String baseUrl = System.getenv().getOrDefault("DECISION_ENGINE_MODEL_BASE_URL", "http://localhost:8081");
        String modelName = System.getenv().getOrDefault(
                "DECISION_ENGINE_MODEL_NAME", "bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF"
        );
        System.out.println("Using model " + modelName + " at " + baseUrl);
        return new LlamaCppChatModel(baseUrl, modelName);
    }

    private static WorkItem requireFound(WorkItemRepository repository, String idValue) {
        Optional<WorkItem> found = repository.findById(new WorkItemId(idValue));
        if (found.isEmpty()) {
            System.err.println("No work item found with id " + idValue);
            System.exit(1);
            return null;
        }
        return found.get();
    }

    private static void show(WorkItemRepository repository, WorkItemDecisionsView view, String idValue) {
        WorkItemId id = new WorkItemId(idValue);
        Optional<WorkItem> found = repository.findById(id);
        if (found.isEmpty()) {
            System.err.println("No work item found with id " + idValue);
            System.exit(1);
            return;
        }

        WorkItemState state = found.get().state();
        System.out.println("Work Item " + id + " (" + state.kind() + "): " + state.title());
        System.out.println("Description: " + state.description());
        System.out.println("Owner: " + state.owner());
        System.out.println("Parent: " + (state.parentId() == null ? "(none)" : state.parentId()));

        List<Decision> relatedDecisions = view.relatedDecisions(id);
        System.out.println();
        System.out.println("Related decisions: " + relatedDecisions.size());
        for (Decision decision : relatedDecisions) {
            System.out.println("  - " + decision.id() + ": " + decision.title() + " [" + decision.state().status() + "]");
        }

        List<Question> openQuestions = view.openQuestions(id);
        System.out.println();
        System.out.println("Open questions: " + openQuestions.size());
        for (Question question : openQuestions) {
            System.out.println("  - " + question.itemId() + ": " + question.text());
        }
    }

    private static String kindPrefix(WorkItemKind kind) {
        return switch (kind) {
            case INITIATIVE -> "init";
            case PROJECT -> "proj";
            case FEATURE -> "feat";
            case STORY -> "story";
            case TASK -> "task";
        };
    }

    private static void printProposeDecisionUsage() {
        System.err.println(
                "Usage: propose-decision <work-item-id> --category <category> --owner <role> "
                        + "--challenger <role> [--challenger <role> ...]"
        );
        System.err.println("        role: one of " + Roles.all());
    }

    private static void printUsage() {
        System.out.println(
                "Usage: WorkItemCli create <kind> <title> [--parent <id>]   (kind: " + List.of(WorkItemKind.values()) + ")"
        );
        System.out.println("       WorkItemCli reparent <work-item-id> <new-parent-id>");
        System.out.println("       WorkItemCli update-description <work-item-id> <description-text>");
        System.out.println(
                "       WorkItemCli propose-decision <work-item-id> --category <category> --owner <role> "
                        + "--challenger <role> [--challenger <role> ...]"
        );
        System.out.println("       WorkItemCli show <work-item-id>");
    }
}
