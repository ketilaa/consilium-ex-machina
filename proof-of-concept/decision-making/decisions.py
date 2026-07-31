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
        "dissent": {
            "role": "Release Manager",
            "objection": (
                "In-process pub/sub means the entire agent coordination layer dies with "
                "the process. If one agent's event handler throws an unhandled exception "
                "the process can crash or be left corrupted, and since there is no "
                "persistence layer, every event that hasn't been consumed yet is gone "
                "permanently with no record it ever existed. The platform's own design "
                "depends on events being the durable unit of coordination and history — a "
                "mechanism that can silently and irrecoverably lose events on the very "
                "first unhandled crash is not acceptable for v1, no matter how much "
                "simpler it is to build. 'We can add monitoring later' does not un-lose an "
                "event that is already gone. I will not accept this without either a "
                "persisted event log that survives a process crash, or a concrete argument "
                "for why permanent event loss is actually tolerable for v1's real use case."
            ),
        },
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
        "dissent": {
            "role": "Architect",
            "objection": (
                "Neo4j Community Edition — the only realistically free option for a "
                "bootstrapped v1 — has no built-in clustering or hot backup. A "
                "single-instance deployment with no replication is a single point of data "
                "loss for the platform's entire decision, evidence, and history record — "
                "which is meant to be the durable source of truth for the whole "
                "engineering process. Losing that store isn't like losing a cache, it's "
                "losing the audited history the platform's entire value proposition "
                "depends on. A relational database gets mature, boring, well-understood "
                "backup and replication essentially for free from any hosting provider. I "
                "will not accept graph-native query convenience as sufficient "
                "justification for a materially higher data-loss risk on the system whose "
                "entire job is being the trustworthy record of what was decided and why — "
                "unless there is a concrete, Neo4j-specific backup/replication plan, not a "
                "generic 'backups can be managed'."
            ),
        },
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
        "dissent": {
            "role": "Architect",
            "objection": (
                "If machine agents hold long-lived bearer tokens to call the API from "
                "other processes or machines, then a single compromised agent process — "
                "and this platform's entire premise is running semi-autonomous AI agents "
                "that execute somewhat unpredictable actions — leaks a token that grants "
                "the same access as any other caller, for as long as the token or its "
                "refresh chain remains valid, with no session to invalidate the way a "
                "cookie-based session can be revoked server-side instantly. This "
                "platform's threat model specifically includes the agents themselves, not "
                "just human attackers. I will not accept a bare bearer-token scheme "
                "without a concrete, specific mechanism for immediate, individual token "
                "revocation independent of expiry — 'short-lived tokens with refresh' "
                "still leaves a live window, and 'JWTs can be revoked' is not "
                "automatically true, since that requires a server-side denylist or "
                "equivalent, which reintroduces exactly the statefulness this proposal "
                "claims to avoid."
            ),
        },
    },
]
