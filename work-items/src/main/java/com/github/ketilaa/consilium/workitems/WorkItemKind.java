package com.github.ketilaa.consilium.workitems;

/**
 * The five kinds of Work Item already named in CLAUDE.md's terminology and
 * docs/high-level-architecture.md -- Work Item is the umbrella concept, these are its kinds,
 * not sibling entities that each need their own Decision-linking.
 */
public enum WorkItemKind {
    INITIATIVE,
    PROJECT,
    FEATURE,
    STORY,
    TASK
}
