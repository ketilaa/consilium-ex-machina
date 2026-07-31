"""The three real sw-foundry decisions used to test the lifecycle against a single-agent baseline."""

DECISIONS = [
    {
        "slug": "event-coordination",
        "title": "How should agents coordinate for v1: in-process pub/sub, or an external message broker (e.g. NATS)?",
        "context": (
            "sw-foundry's agents are meant to subscribe to events (Decision Proposed, "
            "Question Raised, etc.) rather than invoke each other directly. For the "
            "first working version, running as a single process on one machine, "
            "should event delivery be an in-process pub/sub mechanism, or an external "
            "message broker such as NATS? Consider what an early single-node "
            "deployment actually needs versus what multi-node/production would need."
        ),
        # Not a clean fit for any category in the current owner table (API design /
        # Database strategy / Authentication / Deployment / Caching / Domain
        # boundaries) — used deliberately to test the mapping-gap fallback.
        "category": "Integration architecture (no direct entry in the owner table — mapped to Architect as fallback)",
        "owner_role": "Architect",
        "challenger_roles": ["Backend Developer", "Release Manager"],
    },
    {
        "slug": "work-item-persistence",
        "title": "Should the work-item graph (work items, decisions, questions, events, and their relations) be persisted in a relational database (e.g. Postgres) or a graph database (e.g. Neo4j) for v1?",
        "context": (
            "The core domain model is a graph: work items link to decisions, "
            "decisions link to evidence and risks, questions link to work items and "
            "decisions, and everything has an event history. Query patterns are not "
            "yet well understood since there is no implementation. Choose a storage "
            "approach for the first version."
        ),
        "category": "Database strategy",
        "owner_role": "Backend Developer",
        "challenger_roles": ["Architect", "Performance Reviewer"],
    },
    {
        "slug": "api-authentication",
        "title": "Should the platform's API authenticate callers via session cookies or bearer tokens (e.g. JWT)?",
        "context": (
            "Both humans (via a UI) and agents (via direct API calls, possibly from "
            "other processes or machines) need to authenticate against the platform's "
            "API. Choose one authentication approach for v1, understanding both kinds "
            "of caller."
        ),
        "category": "Authentication",
        "owner_role": "Security Reviewer",
        "challenger_roles": ["Backend Developer", "Architect"],
    },
]
