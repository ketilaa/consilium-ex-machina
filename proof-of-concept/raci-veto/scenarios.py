"""Scenarios for the RACI/veto PoC. Each assigns all five roles to a distinct
RACI letter (one Responsible, one Accountable/owner, one Consulted, one
Informed) plus a Concur holder -- deliberately a role NOT already in the R/A/C
set, matching docs/design/decision-making.md's veto example (Security Reviewer
blocking a decision it doesn't own). One Responsible per decision only --
co-ownership is out of scope for this PoC, same as the platform code itself.

Deliberately contrasting Informed-role assignments, to give the participation
question (question 1) a real chance to fail, not just confirm the design:

- audit-log-retention: Informed = Performance Reviewer. Retention policy has
  little to do with runtime performance -- expected SAFE to exclude.
- llm-inference-hosting: Informed = Security Reviewer. Self-hosted vs.
  third-party API has real data-handling implications -- expected RISKY to
  exclude, a deliberate stress case.
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
    },
]
