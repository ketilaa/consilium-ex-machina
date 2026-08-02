"""Scenarios for the question-gating PoC, each rigging one fixed engineering
Issue (resolvable by revision) and one fixed genuine Question (a missing fact, not
resolvable by engineering judgment) into the same contest round — same rigging
discipline as decision-making/decisions.py's 'dissent' field. The external_answer
is the pre-registered ground truth a human/domain source would actually supply,
used only once the mechanism has proven it won't accept the owner's own guess.
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
            "record of engineering choices — the whole point of making decisions first-class is "
            "having a trustworthy history of what was decided and why. Before implementation, decide "
            "on a retention policy: how long history is kept before it can be purged or archived, "
            "and where it's stored."
        ),
        "category": "Compliance / data retention (no clean entry in the owner table — mapped to Release Manager as fallback)",
        "owner_role": "Release Manager",
        "issue": {
            "role": "Backend Developer",
            "text": (
                "Keeping every Decision, Question, and Event forever in the primary operational "
                "database means the history table grows without bound and will eventually degrade "
                "query performance on the very system that's supposed to make audits fast. There "
                "needs to be an actual archiving strategy (e.g. move records older than some "
                "threshold to cold storage) rather than 'keep everything in the live database "
                "indefinitely' — this is a real, addressable design gap in the proposal, not a "
                "missing fact."
            ),
        },
        "question": {
            "role": "Security Reviewer",
            "text": (
                "What is the actual minimum retention period this organization is contractually or "
                "legally obligated to meet for this kind of audit history — is there a specific "
                "number required by a customer contract, an industry regulation, or an internal "
                "compliance policy? I don't have access to that information, and it isn't something "
                "engineering can determine through judgment or revision: setting a retention period "
                "below a real legal or contractual minimum is a compliance violation, not a "
                "technical risk, and setting it far longer than required carries its own storage and "
                "liability cost. This needs an answer from whoever actually holds that information "
                "(Legal, Compliance, or the customer contracts themselves) — not an engineering "
                "estimate."
            ),
        },
        "external_answer": (
            "Legal confirmed the minimum contractual retention requirement is 3 years for enterprise "
            "customers under the current MSA; no regulatory floor applies beyond that for the "
            "platform's current customer base. (Source: Legal, contract review, dated.)"
        ),
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
        "issue": {
            "role": "Performance Reviewer",
            "text": (
                "A self-hosted model on infrastructure the team operates directly means we own "
                "GPU capacity planning, and if agent activity spikes (e.g. several decisions being "
                "processed concurrently), self-hosted inference can queue or degrade in latency in "
                "a way a commercial provider's autoscaling absorbs for us. The proposal needs an "
                "actual plan for handling concurrent load — this is a real, addressable "
                "engineering gap, not a missing fact."
            ),
        },
        "question": {
            "role": "Release Manager",
            "text": (
                "What is the actual approved monthly budget ceiling for inference infrastructure "
                "during the pilot phase? Without that number, self-hosted-versus-third-party isn't "
                "an engineering trade-off we can resolve on technical merits alone — it's a real "
                "business constraint neither of us has access to. I don't have that number, and "
                "picking one to make the cost comparison work would be fabricating a business fact, "
                "not making an engineering decision. This needs an answer from whoever actually "
                "approved the pilot's budget (Finance or whoever holds the budget), not a guess."
            ),
        },
        "external_answer": (
            "Finance approved a monthly ceiling of $8,000 for inference infrastructure during the "
            "pilot phase. (Source: Finance, pilot budget approval, dated.)"
        ),
    },
]
