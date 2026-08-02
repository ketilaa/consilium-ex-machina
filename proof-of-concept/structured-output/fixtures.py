"""Fixed fixtures for the structured-output PoC.

Reuses the exact proposal/objection/revision text already committed under
proof-of-concept/question-gating/runs/*.md, so this PoC isolates format
reliability as the only variable: every repeated trial classifies or rechecks
byte-for-byte the same input, under two response-format conditions, rather
than re-running propose/contest and reintroducing content variance on top of
format variance. Ground truth for each fixture was established by that PoC's
own findings, not invented fresh here.
"""

AUDIT_LOG_BRIEF = (
    "Decision: How long should the platform retain its Decision/Question/Event history (the audit "
    "log) before it can be purged or archived, and where should it be stored?"
)

LLM_HOSTING_BRIEF = (
    "Decision: Should the platform run agent inference against a third-party hosted LLM API, or a "
    "self-hosted model on infrastructure the team operates?"
)

CLASSIFY_FIXTURES = [
    {
        "slug": "classify-audit-log-retention",
        "brief": AUDIT_LOG_BRIEF,
        "proposal": (
            "Based on the context provided, I recommend retaining the Decision/Question/Event "
            "history (audit log) for a minimum of seven years before it can be archived, and "
            "storing it in a secure, immutable, and cost-effective object storage solution. The "
            "seven-year retention period aligns with common regulatory requirements and industry "
            "standards for record-keeping. For storage, an object storage solution like Amazon S3, "
            "Google Cloud Storage, or Azure Blob Storage is ideal, with lifecycle policies to "
            "transition older data to cheaper storage classes."
        ),
        "items": [
            {
                "role": "Backend Developer",
                "text": (
                    "There needs to be an actual archiving strategy (e.g. move records older than "
                    "some threshold to cold storage) rather than keeping everything in the live "
                    "database indefinitely — this is a real, addressable design gap, not a missing "
                    "fact."
                ),
                "ground_truth": "BLOCKING",
            },
            {
                "role": "Security Reviewer",
                "text": (
                    "What is the actual minimum retention period this organization is contractually "
                    "or legally obligated to meet for this kind of audit history? I don't have "
                    "access to that information, and it isn't something engineering can determine "
                    "through judgment or revision — this needs an answer from Legal, Compliance, or "
                    "the customer contracts, not an engineering estimate."
                ),
                "ground_truth": "QUESTION",
            },
        ],
    },
    {
        "slug": "classify-llm-inference-hosting",
        "brief": LLM_HOSTING_BRIEF,
        "proposal": (
            "For the pilot phase, I recommend using a third-party hosted LLM API. This decision "
            "aligns with the principles of system-wide consistency, long-term maintainability, and "
            "coherence between components, and lets the team focus on core competencies rather than "
            "model deployment, scaling, and maintenance."
        ),
        "items": [
            {
                "role": "Performance Reviewer",
                "text": (
                    "If we were to self-host, we would be responsible for GPU capacity planning, "
                    "and the proposal lacks a plan for handling concurrent load — this is a real, "
                    "addressable engineering gap, not a missing fact."
                ),
                "ground_truth": "BLOCKING",
            },
            {
                "role": "Release Manager",
                "text": (
                    "What is the actual approved monthly budget ceiling for inference infrastructure "
                    "during the pilot phase? Without that number, self-hosted-versus-third-party "
                    "isn't an engineering trade-off we can resolve on technical merits alone — it's "
                    "a real business constraint neither of us has access to, and needs an answer "
                    "from Finance, not a guess."
                ),
                "ground_truth": "QUESTION",
            },
        ],
    },
]

RECHECK_FIXTURES = [
    {
        "slug": "recheck-audit-log-retention-self-answer",
        "brief": AUDIT_LOG_BRIEF,
        "role": "Security Reviewer",
        "original_question": (
            "What is the actual minimum retention period this organization is contractually or "
            "legally obligated to meet for this kind of audit history? I don't have access to that "
            "information, and it isn't something engineering can determine through judgment or "
            "revision — this needs an answer from Legal, Compliance, or the customer contracts, not "
            "an engineering estimate."
        ),
        "revision": (
            "The actual minimum retention period for archived data should be determined by Legal, "
            "Compliance, or customer contracts. Until this information is obtained, the seven-year "
            "retention period proposed initially will be used as a placeholder. Once the actual "
            "minimum retention period is confirmed, the retention policy will be updated "
            "accordingly. Obtain the actual minimum retention period from Legal, Compliance, or "
            "customer contracts — this is crucial to ensure compliance and avoid potential legal "
            "issues."
        ),
        "ground_truth": "NOT_RESOLVED",
    },
    {
        "slug": "recheck-audit-log-retention-final",
        "brief": AUDIT_LOG_BRIEF,
        "role": "Security Reviewer",
        "original_question": (
            "What is the actual minimum retention period this organization is contractually or "
            "legally obligated to meet for this kind of audit history? I don't have access to that "
            "information, and it isn't something engineering can determine through judgment or "
            "revision — this needs an answer from Legal, Compliance, or the customer contracts, not "
            "an engineering estimate."
        ),
        "revision": (
            "Based on the information provided by Legal, the platform should retain the "
            "Decision/Question/Event history (audit log) for a minimum of three years before it can "
            "be archived. This period aligns with the contractual requirements for enterprise "
            "customers under the current Master Services Agreement (MSA), ensuring compliance with "
            "legal and contractual obligations while minimizing unnecessary storage and liability "
            "costs."
        ),
        "ground_truth": "RESOLVED",
    },
    {
        "slug": "recheck-llm-inference-hosting-self-answer",
        "brief": LLM_HOSTING_BRIEF,
        "role": "Release Manager",
        "original_question": (
            "What is the actual approved monthly budget ceiling for inference infrastructure during "
            "the pilot phase? Without that number, self-hosted-versus-third-party isn't an "
            "engineering trade-off we can resolve on technical merits alone — it's a real business "
            "constraint neither of us has access to, and needs an answer from Finance, not a guess."
        ),
        "revision": (
            "The actual approved monthly budget ceiling for inference infrastructure during the "
            "pilot phase is a critical missing fact. This is a genuine gap in the information "
            "available. To proceed, we need to obtain the exact approved monthly budget ceiling for "
            "inference infrastructure from the budget holder (likely Finance or the relevant budget "
            "approver). This information is essential for evaluating the total cost of ownership and "
            "making an informed decision."
        ),
        "ground_truth": "NOT_RESOLVED",
    },
    {
        "slug": "recheck-llm-inference-hosting-final",
        "brief": LLM_HOSTING_BRIEF,
        "role": "Release Manager",
        "original_question": (
            "What is the actual approved monthly budget ceiling for inference infrastructure during "
            "the pilot phase? Without that number, self-hosted-versus-third-party isn't an "
            "engineering trade-off we can resolve on technical merits alone — it's a real business "
            "constraint neither of us has access to, and needs an answer from Finance, not a guess."
        ),
        "revision": (
            "The approved monthly budget ceiling for inference infrastructure during the pilot "
            "phase is $8,000. This budget constraint is a critical factor in the decision-making "
            "process. Given this budget, the operational burden, production risk, and rollback "
            "safety associated with either option can be more accurately assessed. The budget "
            "allows for the selection of a reliable commercial provider that can offer the necessary "
            "SLAs, updates, and security patches within the approved budget."
        ),
        "ground_truth": "RESOLVED",
    },
]
