package com.github.ketilaa.consilium.workitems;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import org.junit.jupiter.api.Test;

/** Pure fold tests -- no I/O, same discipline as decisions.DecisionStateTest. */
class WorkItemStateTest {

    private static final Owner OWNER = new Owner("human:ketil");

    @Test
    void createdWorkItemDerivesItsInitialFields() {
        WorkItemState state = WorkItemState.fold(List.of(
                new WorkItemEvent.Created(WorkItemKind.FEATURE, "Audit log retention policy", "Decide retention", null, OWNER)
        ));

        assertThat(state.kind()).isEqualTo(WorkItemKind.FEATURE);
        assertThat(state.title()).isEqualTo("Audit log retention policy");
        assertThat(state.description()).isEqualTo("Decide retention");
        assertThat(state.parentId()).isNull();
        assertThat(state.owner()).isEqualTo(OWNER);
    }

    @Test
    void retitledEventUpdatesTheDerivedTitleOnly() {
        WorkItemState state = WorkItemState.fold(List.of(
                new WorkItemEvent.Created(WorkItemKind.FEATURE, "Original title", "Description", null, OWNER),
                new WorkItemEvent.Retitled("Renamed title")
        ));

        assertThat(state.title()).isEqualTo("Renamed title");
        assertThat(state.description()).isEqualTo("Description");
    }

    @Test
    void descriptionUpdatedEventUpdatesTheDerivedDescriptionOnly() {
        WorkItemState state = WorkItemState.fold(List.of(
                new WorkItemEvent.Created(WorkItemKind.FEATURE, "Title", "Original description", null, OWNER),
                new WorkItemEvent.DescriptionUpdated("Updated description")
        ));

        assertThat(state.title()).isEqualTo("Title");
        assertThat(state.description()).isEqualTo("Updated description");
    }

    @Test
    void reparentedEventUpdatesTheDerivedParent() {
        WorkItemId project = new WorkItemId("proj-1");
        WorkItemState state = WorkItemState.fold(List.of(
                new WorkItemEvent.Created(WorkItemKind.FEATURE, "Title", "Description", null, OWNER),
                new WorkItemEvent.Reparented(project)
        ));

        assertThat(state.parentId()).isEqualTo(project);
    }

    @Test
    void reparentedToNullMovesBackToNoParent() {
        WorkItemState state = WorkItemState.fold(List.of(
                new WorkItemEvent.Created(WorkItemKind.FEATURE, "Title", "Description", new WorkItemId("proj-1"), OWNER),
                new WorkItemEvent.Reparented(null)
        ));

        assertThat(state.parentId()).isNull();
    }

    @Test
    void foldingWithNoCreatedEventThrows() {
        assertThatThrownBy(() -> WorkItemState.fold(List.of(new WorkItemEvent.Retitled("Renamed"))))
                .isInstanceOf(IllegalStateException.class);
    }
}
