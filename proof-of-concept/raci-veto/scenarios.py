"""Scenarios for the RACI/veto PoC. Each assigns all five roles to a distinct
RACI letter (one Responsible, one Accountable/owner, one Consulted, one
Informed) plus a Concur holder -- deliberately a role NOT already in the R/A/C
set, matching docs/design/decision-making.md's veto example (Security Reviewer
blocking a decision it doesn't own). One Responsible per decision only --
co-ownership is out of scope for this PoC, same as the platform code itself.

Second batch (schema-migration-gate, dependency-upgrade-policy,
api-rate-limiting-policy): the first run's two scenarios left both open
questions under-tested -- Concur's sharp claim (does it ever block an
already-clean raci convergence) only got one decisive trial, because the
other scenario's Responsible/Consulted items never resolved cleanly on their
own, for reasons unrelated to Informed's exclusion. These three are written
with concrete, closeable engineering concerns (rollback plans, dry-run modes,
review gates) rather than open-ended architectural or compliance framing, to
give raci a real chance to converge cleanly and make both questions decisive
more often -- not a guarantee (still emergent model behavior), but a
deliberate bias in that direction, same discipline as pre-registering ground
truth in question-gating/scenarios.py.

Every scenario now carries a pre-registered `expected_informed_signal`
("redundant" or "novel") -- a prediction of what the redundancy judge should
say about the excluded Informed role's withheld reaction, made before running
anything. The first run's two trials were both, in fact, judged "novel" --
suspicious on its own: either every Informed role genuinely always has
something to add, or the judge is systematically biased toward "novel" and
never actually returns "redundant". schema-migration-gate is a deliberate
sanity check on the judge itself: Performed Reviewer's natural angle (does
auto-migration risk locking/downtime under load) substantially overlaps with
Backend Developer's operational-burden framing of the same mechanism -- if
the judge can't call THIS redundant, that's evidence about the judge, not
about participation safety.
"""

SCENARIOS = [
    {
        "slug": "audit-log-retention",
        "title": (
            "How long should the platform retain its Decision/Question/Event history (the audit "
            "log) before it can be purged or archived, and where should it be stored?"
        ),
        "context": (
            "This platform's decisions, questions, and events are meant to be the durable, audited "
            "record of engineering choices -- the whole point of making decisions first-class is "
            "having a trustworthy history of what was decided and why. Before implementation, decide "
            "on a retention policy: how long history is kept before it can be purged or archived, "
            "and where it's stored."
        ),
        "category": "Compliance / data retention",
        "owner_role": "Release Manager",
        "responsible_role": "Backend Developer",
        "consulted_role": "Architect",
        "informed_role": "Performance Reviewer",
        "concur_role": "Security Reviewer",
        "concur_grounds": "whether this retention approach meets security, audit, and compliance requirements",
        "expected_informed_signal": "redundant",
    },
    {
        "slug": "llm-inference-hosting",
        "title": (
            "Should the platform run agent inference against a third-party hosted LLM API, or a "
            "self-hosted model on infrastructure the team operates?"
        ),
        "context": (
            "Every agent role (Architect, Backend Developer, Security Reviewer, etc.) needs an LLM "
            "backing it. Decide, for the pilot phase, whether that's a third-party hosted API "
            "(e.g. a commercial provider) or a self-hosted model on infrastructure the team runs and "
            "operates directly."
        ),
        "category": "Deployment architecture",
        "owner_role": "Architect",
        "responsible_role": "Backend Developer",
        "consulted_role": "Performance Reviewer",
        "informed_role": "Security Reviewer",
        "concur_role": "Release Manager",
        "concur_grounds": "whether this hosting approach is safe to deploy and roll back in production",
        "expected_informed_signal": "novel",
    },
    {
        "slug": "schema-migration-gate",
        "title": (
            "Should schema migrations run automatically on deploy, or require a manual approval "
            "gate before applying to production?"
        ),
        "context": (
            "The platform's event-sourced repositories (Decision Engine, Work Items) currently need "
            "no schema migration at all -- state is always derived by replaying events, and payload "
            "evolution is a codec concern, not a table migration. But as the platform grows, some "
            "future component will eventually need an actual relational schema (e.g. an index or "
            "projection store) that does need real migrations. Decide the execution policy for those "
            "migrations before that need arrives: should migrations run automatically as part of the "
            "normal deploy pipeline, or should they require an explicit manual approval step before "
            "touching a production database?"
        ),
        "category": "Deployment architecture / operational process",
        "owner_role": "Release Manager",
        "responsible_role": "Backend Developer",
        "consulted_role": "Architect",
        "informed_role": "Performance Reviewer",
        "concur_role": "Security Reviewer",
        "concur_grounds": "whether automatic production schema changes preserve an adequate access-control and audit trail",
        "expected_informed_signal": "redundant",
    },
    {
        "slug": "dependency-upgrade-policy",
        "title": (
            "Should the platform pin exact dependency versions and require manual review for every "
            "upgrade, or allow automatic minor/patch upgrades?"
        ),
        "context": (
            "Both platform modules (decision-engine, work-items) currently pin exact dependency "
            "versions, reviewed manually. As the dependency count grows, decide the ongoing policy: "
            "keep exact pinning with manual review for every version bump, or allow automatic "
            "minor/patch upgrades (e.g. via Dependabot-style automation) with only major version "
            "bumps requiring manual review."
        ),
        "category": "Development practice / technical debt",
        "owner_role": "Architect",
        "responsible_role": "Backend Developer",
        "consulted_role": "Release Manager",
        "informed_role": "Security Reviewer",
        "concur_role": "Performance Reviewer",
        "concur_grounds": (
            "whether this policy adequately protects against undetected performance regressions "
            "from automatic upgrades reaching production without being caught first"
        ),
        "expected_informed_signal": "novel",
    },
    {
        "slug": "api-rate-limiting-policy",
        "title": (
            "Should the platform enforce API rate limits per-agent-role at a central gateway layer, "
            "or leave rate limiting to each downstream service to implement independently?"
        ),
        "context": (
            "Each agent role (Architect, Backend Developer, Security Reviewer, etc.) calls the "
            "platform's APIs at its own pace. Decide where rate limiting is enforced: a single "
            "centralized gateway that all requests pass through, or independent rate limiting "
            "implemented separately within each downstream service."
        ),
        "category": "API design",
        "owner_role": "Architect",
        "responsible_role": "Performance Reviewer",
        "consulted_role": "Backend Developer",
        "informed_role": "Release Manager",
        "concur_role": "Security Reviewer",
        "concur_grounds": (
            "whether this rate-limiting approach adequately protects against abuse or a compromised "
            "agent role, and fails safe rather than open during a gateway rollback or outage"
        ),
        "expected_informed_signal": "novel",
    },
]
