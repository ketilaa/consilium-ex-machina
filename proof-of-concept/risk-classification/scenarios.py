"""Scenarios for the risk-classification PoC. Each item carries a
pre-registered `ground_truth` ("BLOCKING" or "RISK"), decided by the same
reasoning applied to the real d-22ffab13 review this PoC is grounded in --
not the model's own classification, fixed before any run.

- `role-registry-configurability` is REAL data: the exact five items from
  d-22ffab13 whose ground truth was actually argued through with a human in
  this project's own dogfooding (two judged disproportionate-given-context,
  three judged genuinely necessary regardless of context).
- `payments-webhook-handler` is constructed with a deliberately HIGH risk
  profile -- a stress test in the opposite direction from the real scenario:
  does a demanding risk profile correctly keep the classifier strict, or
  does having a RISK option at all make it defer things it shouldn't just
  because deferring is available? Three of its four items are real,
  current production concerns that must stay BLOCKING regardless of risk
  profile; one (scaling beyond an explicit current traffic estimate) is a
  legitimate RISK case even under a demanding profile, because the harm is
  explicitly conditional on a future, nameable change.
- `internal-analytics-dashboard` is constructed with a deliberately LOW risk
  profile, and includes the sharpest test in this PoC: a plain correctness
  bug (item 3) phrased in the same "X could be a problem" register as the
  legitimate RISK items around it. RISK must never apply to it regardless of
  how low the risk profile is -- a defect is a defect, not a proportionality
  judgment. If the classifier sweeps it into RISK because the profile reads
  as "low stakes," that's the overshoot failure mode, concretely caught.
"""

SCENARIOS = [
    {
        "slug": "role-registry-configurability",
        "title": "Make the agent role registry configurable instead of hardcoded",
        "category": "Platform architecture / extensibility",
        "context": (
            "Right now, the Decision Engine's agent roles are hardcoded Java constants in "
            "Roles.java -- adding, removing, or changing a role's mandate requires recompiling "
            "the engine. Decide the concrete approach: a shared roles.yaml configuration file, "
            "its schema, validation, and migration path."
        ),
        "risk_profile": (
            "Internal engineering platform, currently in an exploratory/pilot phase. No "
            "regulated data, no external customers, no personal data processed. Small internal "
            "team with existing code-review practices (all config changes go through normal git "
            "PR review)."
        ),
        "items": [
            {
                "role": "Backend Developer",
                "ground_truth": "BLOCKING",
                "text": (
                    "ENGINEERING TRADE-OFF: The proposed approach does not address how the "
                    "system will handle errors or missing values in the `roles.yaml` file. For "
                    "example, if a role is missing a required field or if a category assignment "
                    "is invalid, the system should have a clear strategy for handling these "
                    "errors. This could involve default values, error logging, or fallback "
                    "mechanisms to ensure the system remains operational even if the "
                    "configuration is incomplete or incorrect."
                ),
            },
            {
                "role": "Backend Developer",
                "ground_truth": "BLOCKING",
                "text": (
                    "ENGINEERING TRADE-OFF: The proposal does not address how the system will "
                    "handle role permissions and access control based on the configuration "
                    "file. The `Roles.java` file currently defines the mandates and permissions "
                    "for each role, but the proposal does not specify how these permissions "
                    "will be enforced based on the `roles.yaml` configuration. The proposal "
                    "should include a strategy for mapping the configuration file to the "
                    "system's access control mechanisms."
                ),
            },
            {
                "role": "Security Reviewer",
                "ground_truth": "BLOCKING",
                "text": (
                    "ENGINEERING TRADE-OFF: The proposal does not specify how the system will "
                    "validate the `roles.yaml` file to ensure it conforms to the expected "
                    "schema. Without validation, there is a risk of introducing configuration "
                    "errors that could lead to runtime failures or security vulnerabilities. A "
                    "schema validation step should be added to the configuration loading "
                    "process to catch and report any errors in the `roles.yaml` file before "
                    "the system attempts to use it."
                ),
            },
            {
                "role": "Security Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "ENGINEERING TRADE-OFF: The proposal does not address how the system will "
                    "handle deprecated or removed roles. As the platform evolves, some roles "
                    "may become obsolete and need to be removed from the configuration. The "
                    "system should have a clear strategy for handling such changes, such as "
                    "gracefully degrading functionality or providing clear error messages when "
                    "a deprecated role is referenced."
                ),
            },
            {
                "role": "Security Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "ENGINEERING TRADE-OFF: The proposal does not discuss the security "
                    "implications of allowing the role registry to be configured via an "
                    "external YAML file. This approach introduces a new attack surface, as an "
                    "attacker who gains write access to the `roles.yaml` file could potentially "
                    "modify the role definitions to escalate their privileges or disrupt the "
                    "system's operation. Access controls and integrity checks should be "
                    "implemented to mitigate this risk."
                ),
            },
        ],
    },
    {
        "slug": "payments-webhook-handler",
        "title": "Add a webhook handler for the payment provider's transaction notifications",
        "category": "Payments / webhook processing",
        "context": (
            "The payment provider sends asynchronous webhook notifications when a transaction "
            "completes, fails, or is refunded. Decide the concrete implementation of the "
            "handler that receives and processes these notifications."
        ),
        "risk_profile": (
            "Production payments system processing real customer credit-card transactions and "
            "personal data. In scope for PCI-DSS. The webhook endpoint is public-facing, "
            "reachable from the open internet."
        ),
        "items": [
            {
                "role": "Security Reviewer",
                "ground_truth": "BLOCKING",
                "text": (
                    "The webhook endpoint has no rate limiting and no authentication of the "
                    "calling party beyond a shared secret in the request body. An attacker who "
                    "obtains or guesses this secret can replay or forge transaction "
                    "notifications, and there is no protection against a flood of requests "
                    "overwhelming the endpoint."
                ),
            },
            {
                "role": "Backend Developer",
                "ground_truth": "BLOCKING",
                "text": (
                    "The proposal does not specify how duplicate webhook deliveries -- which "
                    "the payment provider's own documentation explicitly warns can happen -- "
                    "will be deduplicated, risking double-processing a single payment."
                ),
            },
            {
                "role": "Performance Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "The proposal does not address horizontal scaling of the webhook handler "
                    "beyond the initial launch traffic estimate of roughly 50 requests per "
                    "minute; if adoption exceeds that estimate by an order of magnitude, "
                    "response times could degrade under load."
                ),
            },
            {
                "role": "Release Manager",
                "ground_truth": "BLOCKING",
                "text": (
                    "The migration script for backfilling existing transaction records into the "
                    "new webhook processing path has no described rollback plan if it fails "
                    "partway through running against production data."
                ),
            },
        ],
    },
    {
        "slug": "internal-analytics-dashboard",
        "title": "Build an internal dashboard for exploring engagement metrics",
        "category": "Internal tooling",
        "context": (
            "The data team wants a dashboard for exploring engagement metrics computed from an "
            "already-published, anonymized public dataset. Decide the concrete implementation."
        ),
        "risk_profile": (
            "Internal-only tool used by approximately 5 people on the data team. No external "
            "users, not customer-facing. Reads from an already-public, anonymized dataset -- no "
            "customer data, no regulated data."
        ),
        "items": [
            {
                "role": "Security Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "The dashboard's admin panel has no rate limiting on login attempts, which "
                    "could allow a brute-force attack against internal team credentials."
                ),
            },
            {
                "role": "Security Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "Data in transit between the dashboard and its database is not encrypted."
                ),
            },
            {
                "role": "Backend Developer",
                "ground_truth": "BLOCKING",
                "text": (
                    "The monthly aggregation query groups events by calendar month using the "
                    "event's server-received timestamp rather than its original client-side "
                    "event timestamp. Whenever there is any processing delay, this undercounts "
                    "events from the last day of each month, silently and consistently "
                    "underreporting monthly totals by a small but real margin every single "
                    "month."
                ),
            },
            {
                "role": "Performance Reviewer",
                "ground_truth": "RISK",
                "text": (
                    "The dashboard reloads its entire multi-year dataset into memory on every "
                    "page refresh instead of caching it, which is fine at current usage but "
                    "will become painfully slow if the dataset grows much larger or if "
                    "concurrent usage increases significantly."
                ),
            },
        ],
    },
]
