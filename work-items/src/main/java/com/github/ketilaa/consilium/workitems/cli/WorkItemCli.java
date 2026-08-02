package com.github.ketilaa.consilium.workitems.cli;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.Question;
import com.github.ketilaa.consilium.decisions.adapter.FileDecisionRepository;
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
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

/**
 * {@code create <kind> <title>} makes a new Work Item; {@code show <id>} prints it plus every
 * Decision related to it and their still-open Questions -- the concrete proof that "related
 * decisions" and "open questions" (docs/high-level-architecture.md) are real, queryable facts,
 * not just prose. Pair with {@code DecisionEngineCli run --origin work-item:<id>} to attach a
 * real decision to a work item created here.
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
        for (int i = 1; i < args.length - 1; i++) {
            if (args[i].equals("--parent")) {
                return new WorkItemId(args[i + 1]);
            }
        }
        return null;
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
        System.out.println("To attach a real decision to it:");
        System.out.println("  DecisionEngineCli run --origin " + WorkItemDecisionsView.originReferenceFor(workItemId));
    }

    private static void reparent(WorkItemRepository repository, String idValue, String newParentValue) {
        WorkItemId id = new WorkItemId(idValue);
        Optional<WorkItem> found = repository.findById(id);
        if (found.isEmpty()) {
            System.err.println("No work item found with id " + idValue);
            System.exit(1);
            return;
        }
        WorkItem workItem = found.get();
        workItem.apply(new WorkItemEvent.Reparented(new WorkItemId(newParentValue)));
        repository.save(workItem);
        System.out.println(id + " reparented under " + newParentValue);
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

    private static void printUsage() {
        System.out.println(
                "Usage: WorkItemCli create <kind> <title> [--parent <id>]   (kind: " + List.of(WorkItemKind.values()) + ")"
        );
        System.out.println("       WorkItemCli reparent <work-item-id> <new-parent-id>");
        System.out.println("       WorkItemCli show <work-item-id>");
    }
}
