package com.github.ketilaa.consilium.decisions.adapter;

import static org.assertj.core.api.Assertions.assertThat;

import com.github.ketilaa.consilium.decisions.Decision;
import com.github.ketilaa.consilium.decisions.DecisionEvent;
import com.github.ketilaa.consilium.decisions.DecisionStatus;
import com.github.ketilaa.consilium.decisions.ItemId;
import com.github.ketilaa.consilium.decisions.OriginReference;
import com.github.ketilaa.consilium.decisions.RecheckVerdict;
import com.github.ketilaa.consilium.decisions.Role;
import com.github.ketilaa.consilium.decisions.Roles;
import com.github.ketilaa.consilium.decisions.Verdict;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class FileDecisionRepositoryTest {

    private static final Role OWNER = Roles.RELEASE_MANAGER;
    private static final Role ISSUE_ROLE = Roles.BACKEND_DEVELOPER;
    private static final Role QUESTION_ROLE = Roles.SECURITY_REVIEWER;
    private static final ItemId ISSUE_ITEM = new ItemId(ISSUE_ROLE, 0);
    private static final ItemId QUESTION_ITEM = new ItemId(QUESTION_ROLE, 0);

    @TempDir
    Path tempDir;

    /**
     * {@code Map.of(...)} makes no iteration-order guarantee -- using it here silently
     * scrambled the very item order this test exists to check, the same class of bug
     * DecisionEvent's compact constructors were fixed for. A LinkedHashMap is required
     * whenever a test cares about order, same as production code.
     */
    private static <K, V> Map<K, V> orderedMap(K k1, V v1, K k2, V v2) {
        Map<K, V> map = new LinkedHashMap<>();
        map.put(k1, v1);
        map.put(k2, v2);
        return map;
    }

    @Test
    void roundTripsAFullDecisionIncludingStatusAndItemOrder() {
        Decision decision = new Decision(
                "d-1", "How long should we retain the audit log?",
                "Compliance / data retention", OWNER, new OriginReference("test:origin")
        );
        decision.apply(new DecisionEvent.Proposed("retain for 7 years"));
        decision.apply(new DecisionEvent.Contested(orderedMap(
                ISSUE_ITEM, "no archiving strategy",
                QUESTION_ITEM, "what's the real minimum?"
        )));
        decision.apply(new DecisionEvent.Classified(orderedMap(
                ISSUE_ITEM, Verdict.BLOCKING,
                QUESTION_ITEM, Verdict.QUESTION
        )));
        decision.apply(new DecisionEvent.Revised("self-answer attempt"));
        decision.apply(new DecisionEvent.Rechecked(orderedMap(
                ISSUE_ITEM, RecheckVerdict.RESOLVED,
                QUESTION_ITEM, RecheckVerdict.NOT_RESOLVED
        )));
        decision.apply(new DecisionEvent.QuestionAnsweredExternally(QUESTION_ITEM, "Legal confirmed 3 years", "Legal"));
        decision.apply(new DecisionEvent.Revised("final revision"));
        decision.apply(new DecisionEvent.Rechecked(orderedMap(
                ISSUE_ITEM, RecheckVerdict.RESOLVED,
                QUESTION_ITEM, RecheckVerdict.RESOLVED
        )));

        FileDecisionRepository repository = new FileDecisionRepository(tempDir);
        repository.save(decision);

        Optional<Decision> reloaded = repository.findById("d-1");

        assertThat(reloaded).isPresent();
        Decision result = reloaded.get();
        assertThat(result.id()).isEqualTo("d-1");
        assertThat(result.title()).isEqualTo("How long should we retain the audit log?");
        assertThat(result.category()).isEqualTo("Compliance / data retention");
        assertThat(result.ownerRole()).isEqualTo(OWNER);
        assertThat(result.origin()).isEqualTo(new OriginReference("test:origin"));
        assertThat(result.events()).hasSize(8);
        assertThat(result.state().status()).isEqualTo(DecisionStatus.CONVERGED);
        // Item order must survive the round trip -- positional tag attribution depends on it.
        assertThat(List.copyOf(result.state().raisedItems().keySet())).containsExactly(ISSUE_ITEM, QUESTION_ITEM);
    }

    @Test
    void findByIdReturnsEmptyWhenNoFileExists() {
        FileDecisionRepository repository = new FileDecisionRepository(tempDir);

        assertThat(repository.findById("does-not-exist")).isEmpty();
    }

    @Test
    void findByOriginReturnsOnlyDecisionsWithThatExactOrigin() {
        OriginReference target = new OriginReference("work-item:feat-1");
        Decision matching = new Decision("d-a", "Decision A", "Category", OWNER, target);
        matching.apply(new DecisionEvent.Proposed("proposal A"));
        Decision otherOrigin = new Decision("d-b", "Decision B", "Category", OWNER, new OriginReference("work-item:feat-2"));
        otherOrigin.apply(new DecisionEvent.Proposed("proposal B"));

        FileDecisionRepository repository = new FileDecisionRepository(tempDir);
        repository.save(matching);
        repository.save(otherOrigin);

        List<Decision> found = repository.findByOrigin(target);

        assertThat(found).extracting(Decision::id).containsExactly("d-a");
    }

    @Test
    void findByOriginReturnsEmptyWhenNothingMatches() {
        FileDecisionRepository repository = new FileDecisionRepository(tempDir);

        assertThat(repository.findByOrigin(new OriginReference("work-item:nothing-here"))).isEmpty();
    }
}
