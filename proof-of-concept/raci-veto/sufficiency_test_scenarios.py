"""Tests whether an explicit sufficiency criterion (roles.py's
concur_system_with_sufficiency) changes Concur's behavior, following the
positive control's finding that the original prompt has no stopping
condition. Each entry pairs two fixtures against the SAME concur_role/grounds:

- `positive_fixture` -- the same hand-authored, thorough decision from
  positive_control_scenarios.py that the original prompt rejected 9/9 despite
  concretely closing every real objection it had raised. If the sufficiency
  criterion works, this should now get CONCUR at least sometimes.
- `negative_fixture` -- a REAL final decision this PoC actually produced
  (run 2's raci mechanism for audit-log-retention and api-rate-limiting-policy;
  run 1's for llm-inference-hosting, via `git show 8cef25d`), one that only
  addressed Responsible/Consulted's concerns and never touched the
  Concur-holder's specific named grounds in any depth -- the reason it
  originally got DO NOT CONCUR. If the sufficiency criterion has just made
  Concur lenient rather than well-calibrated, this should still be rejected;
  if it now gets CONCUR, the "fix" overshot into rubber-stamping, which is
  the opposite failure mode and equally disqualifying.
"""

SUFFICIENCY_TEST_SCENARIOS = [
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
        "concur_role": "Security Reviewer",
        "concur_grounds": "whether this retention approach meets security, audit, and compliance requirements",
        "positive_fixture": (
            "Final decision: Retain the Decision/Question/Event history for seven years in a tiered "
            "storage strategy (recent data in high-performance storage, older data moved to "
            "cost-effective archival storage), addressing every raised concern as follows.\n\n"
            "Access control and audit trail: Access to the audit log -- at every tier -- is "
            "restricted via role-based access control to three named roles (Security Reviewer, "
            "Release Manager, and an auditor role), enforced at the storage layer with no "
            "exceptions. Every read and write access is itself logged to a separate, append-only "
            "access log, retained for the same period, and reviewed quarterly by the Security "
            "Reviewer.\n\n"
            "Encryption and integrity: All data is encrypted at rest with AES-256 and in transit "
            "with TLS 1.3. The archival tier uses object-lock/write-once-read-many (WORM) storage "
            "so no role, including administrators, can modify or delete a record before its "
            "retention period expires -- directly limiting the blast radius of any single "
            "compromised credential to read-only exposure, never tampering.\n\n"
            "Regulatory compliance: Legal and Compliance completed a jurisdiction-by-jurisdiction "
            "review against GDPR, SOC 2, and the specific regulations of every industry this "
            "platform currently serves; the seven-year period was confirmed as meeting or exceeding "
            "every applicable minimum. Any future customer whose contract requires a longer period "
            "is handled via a documented per-customer retention override, reviewed by Compliance "
            "before onboarding.\n\n"
            "Monitoring: All access-control and integrity events feed into the platform's existing "
            "monitoring, with alerting configured for any anomalous access pattern (e.g. bulk "
            "export, access outside the three named roles)."
        ),
        "negative_fixture": (
            "Revised Decision: Retain the Decision/Question/Event history for a minimum of seven "
            "years before archiving. This period strikes a balance between operational burden, "
            "production risk, and regulatory compliance. While some regulations may require longer "
            "retention periods, seven years is a common standard that ensures the platform can meet "
            "most compliance requirements.\n\n"
            "Storage Strategy -- Tiered Storage Approach: Recent data (0-2 years) is stored in a "
            "high-performance, easily accessible storage solution such as Amazon S3 Standard or "
            "Azure Blob Storage Hot tier. Older data (2-7 years) is moved to a cost-effective, "
            "long-term archival storage solution such as Amazon S3 Glacier or Azure Archive Blob "
            "Storage.\n\n"
            "Data Management and Accessibility: Automated processes periodically move data from the "
            "high-performance tier to the archival tier based on the defined timeframes, and the "
            "archival storage solution provides easy retrieval options for historical data when "
            "needed, albeit with higher retrieval latencies.\n\n"
            "This strategy ensures deployability, operational burden, rollback safety, and "
            "production risk are all considered and managed effectively."
        ),
        "negative_fixture_source": "runs/audit-log-retention.md, run 2, Mechanism B (raci) final revision",
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
        "concur_role": "Release Manager",
        "concur_grounds": "whether this hosting approach is safe to deploy and roll back in production",
        "positive_fixture": (
            "Final decision: Use a third-party hosted LLM API for the pilot phase, with a tested "
            "hybrid fallback to a self-hosted model, addressing every raised concern as follows.\n\n"
            "Rollback strategy and testing: A self-hosted fallback model is kept warm (running, "
            "receiving a small fraction of shadow traffic) at all times, not spun up on demand. "
            "Automatic failover triggers on two independent, pre-defined thresholds (p99 latency "
            "over 2s for 60 consecutive seconds, or error rate over 5% for 30 seconds), verified in "
            "a rehearsed game-day drill that measured full failover completing in under 10 seconds "
            "with zero request loss. Manual rollback is also available via a single documented "
            "runbook command, tested in the same drill.\n\n"
            "State and data consistency during a switch: All agent-role inference calls are "
            "stateless -- no conversation or session state is held by the inference layer itself; "
            "all Decision/Work Item state lives in the platform's own repositories, untouched by "
            "which inference backend served a given call. A switch therefore carries zero risk of "
            "state loss or inconsistency; in-flight requests at the moment of switchover are "
            "retried against the new backend with the same input, not resumed mid-stream.\n\n"
            "Operational implications: On-call is paged automatically on any failover event "
            "(automatic or manual), and the warm self-hosted fallback's capacity is provisioned for "
            "100% of pilot-phase peak load, not a fraction -- verified in the same drill under "
            "synthetic peak-load traffic."
        ),
        "negative_fixture": (
            "Decision: For the pilot phase, use a third-party hosted LLM API with specific "
            "mitigations and fallback strategies.\n\n"
            "Latency and availability risks: We will specify required Service Level Agreements "
            "(SLAs) with the third-party provider to ensure they can meet our latency and "
            "availability requirements, and conduct thorough performance testing to validate these "
            "SLAs in a pilot scenario.\n\n"
            "Fallback plan: We will design a hybrid approach that allows for seamless switching "
            "between the third-party API and a self-hosted model. This will involve developing a "
            "fallback mechanism that can be activated in case of outages or significant latency "
            "issues with the third-party service. We will also ensure that the self-hosted model is "
            "ready to be deployed quickly if needed.\n\n"
            "Costs and scalability: We will conduct a detailed cost analysis based on expected usage "
            "patterns and assess the scalability of the third-party solution under increased load, "
            "with cost management strategies such as rate limiting and optimizing API calls.\n\n"
            "Using a third-party hosted LLM API for the pilot phase remains the recommended "
            "approach, with these mitigations and fallback strategies to address the raised "
            "concerns."
        ),
        "negative_fixture_source": (
            "runs/llm-inference-hosting.md, run 1 (git show 8cef25d), Mechanism B (raci) final revision"
        ),
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
        "concur_role": "Security Reviewer",
        "concur_grounds": (
            "whether this rate-limiting approach adequately protects against abuse or a compromised "
            "agent role, and fails safe rather than open during a gateway rollback or outage"
        ),
        "positive_fixture": (
            "Final decision: Enforce API rate limits at a central gateway layer, addressing every "
            "raised concern as follows.\n\n"
            "Per-role enforcement and abuse detection: Rate limits are configured per agent role "
            "individually (not a single global limit), with tighter limits on roles that don't need "
            "high call volume. Behavioral anomaly detection flags and automatically tightens limits "
            "on any role whose call pattern deviates from its historical baseline (e.g. a "
            "compromised Security Reviewer credential suddenly issuing Architect-role-typical "
            "volume), independent of the static per-role limit.\n\n"
            "Fail-safe on rollback or outage: The gateway is configured fail-closed, not fail-open: "
            "if the gateway itself is unreachable or mid-rollback, downstream services reject all "
            "requests by default rather than allowing unlimited unmetered traffic through. This is "
            "enforced by each downstream service's own minimal local rate limiter, which activates "
            "only as a fallback during a gateway outage -- a deliberate, tested exception to the "
            "\"no per-service logic\" principle, specifically to avoid the fail-open blast-radius "
            "risk.\n\n"
            "Audit and compliance: Every rate-limit adjustment (automatic or manual) is logged with "
            "the role, old limit, new limit, and reason, retained and reviewed by the Security "
            "Reviewer monthly.\n\n"
            "Blast radius: Because rate limits are enforced per-role rather than globally, a single "
            "compromised role is capped at its own limit even if the gateway is otherwise healthy -- "
            "a compromise of one role's credentials cannot exhaust capacity for other roles or bring "
            "down the gateway for everyone."
        ),
        "negative_fixture": (
            "Revised Decision: Enforce API rate limits per-agent-role at a central gateway layer, "
            "with specific engineering solutions to address latency and single points of failure.\n\n"
            "Latency: The gateway can be optimized for low-latency processing using efficient "
            "algorithms for rate limiting, minimizing request-processing overhead, leveraging "
            "in-memory data structures for quick lookups, strategic placement close to downstream "
            "services, asynchronous processing for non-critical operations, and caching.\n\n"
            "Single point of failure: The gateway is designed as a highly available service with "
            "multiple instances running in parallel behind load balancers, automatic failover and "
            "health checks, redundant backup instances, and robust monitoring and alerting.\n\n"
            "These solutions mitigate the risks associated with latency and single points of "
            "failure, while still providing the benefits of consistency, manageability, and "
            "coherence that a centralized gateway offers."
        ),
        "negative_fixture_source": "runs/api-rate-limiting-policy.md, run 2, Mechanism B (raci) final revision",
    },
]
