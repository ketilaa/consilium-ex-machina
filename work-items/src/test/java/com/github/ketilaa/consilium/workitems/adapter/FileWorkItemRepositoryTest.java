package com.github.ketilaa.consilium.workitems.adapter;

import static org.assertj.core.api.Assertions.assertThat;

import com.github.ketilaa.consilium.workitems.Owner;
import com.github.ketilaa.consilium.workitems.WorkItem;
import com.github.ketilaa.consilium.workitems.WorkItemEvent;
import com.github.ketilaa.consilium.workitems.WorkItemId;
import com.github.ketilaa.consilium.workitems.WorkItemKind;
import java.nio.file.Path;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class FileWorkItemRepositoryTest {

    @TempDir
    Path tempDir;

    @Test
    void roundTripsAWorkItemIncludingReparentingAndNullParent() {
        WorkItemId id = new WorkItemId("feat-1");
        WorkItemId project = new WorkItemId("proj-1");
        Owner owner = new Owner("human:ketil");

        WorkItem workItem = new WorkItem(id);
        workItem.apply(new WorkItemEvent.Created(
                WorkItemKind.FEATURE, "Audit log retention policy", "Decide retention", null, owner
        ));
        workItem.apply(new WorkItemEvent.Reparented(project));
        workItem.apply(new WorkItemEvent.Retitled("Audit log retention policy (v2)"));

        FileWorkItemRepository repository = new FileWorkItemRepository(tempDir);
        repository.save(workItem);

        Optional<WorkItem> reloaded = repository.findById(id);

        assertThat(reloaded).isPresent();
        WorkItem result = reloaded.get();
        assertThat(result.id()).isEqualTo(id);
        assertThat(result.events()).hasSize(3);
        assertThat(result.state().kind()).isEqualTo(WorkItemKind.FEATURE);
        assertThat(result.state().title()).isEqualTo("Audit log retention policy (v2)");
        assertThat(result.state().description()).isEqualTo("Decide retention");
        assertThat(result.state().parentId()).isEqualTo(project);
        assertThat(result.state().owner()).isEqualTo(owner);
    }

    @Test
    void findByIdReturnsEmptyWhenNoFileExists() {
        FileWorkItemRepository repository = new FileWorkItemRepository(tempDir);

        assertThat(repository.findById(new WorkItemId("does-not-exist"))).isEmpty();
    }
}
