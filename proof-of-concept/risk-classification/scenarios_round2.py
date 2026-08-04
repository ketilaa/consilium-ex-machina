"""Scenarios for round 2 of the risk-classification PoC. Extends round 1
(`scenarios.py`, kept unchanged for comparison) rather than replacing it --
the original scenarios' BLOCKING/RISK items are reused verbatim so round 1
vs round 2 results are directly comparable on identical inputs, isolating
what the 5-way classifier and its phrasing-neutral fix actually changed.

Three additions, each testing something round 1 never touched:

1. One new WORK_ITEM item added to each of the three original scenarios --
   real, unconditional follow-up work (not contingent on the risk profile
   changing) that round 1's 4-way classifier had no vocabulary to sort
   correctly (it would have had to force these into RISK or BLOCKING).

2. `pilot-program-customer-portal` -- a new scenario testing whether a
   STATED, already-scheduled future change in risk profile (an external
   pilot launch 6 weeks away, already committed) correctly raises the bar
   NOW for a concern tied to that change, rather than being waved off with
   a "revisit later" RISK framing that undersells an already-imminent harm.
   Contains one item that must stay BLOCKING despite the current low-risk
   state (because the transition is already committed, not hypothetical),
   one item genuinely unrelated to that transition and still fine to defer
   as RISK, and one genuine WORK_ITEM.

3. `consistency-probe` -- a single, deliberately ambiguous item (could
   reasonably be RISK -- conditional on a decision that hasn't been made --
   or WORK_ITEM -- work that's probably worth doing regardless) with no
   pre-registered ground truth. Run many times, not scored for correctness,
   only for whether the classifier's verdict is stable or flip-flops --
   the same kind of stability check the redundancy judge in
   poc-raci-veto.md failed.
"""

WORK_ITEM_ADDITIONS = {
    "role-registry-configurability": {
        "role": "Backend Developer",
        "ground_truth": "WORK_ITEM",
        "text": (
            "The proposal does not specify what tooling or workflow will be used to actually "
            "add or edit a role in `roles.yaml` day to day -- right now someone would hand-edit "
            "YAML with no validation feedback until the application starts and fails. A "
            "dedicated CLI command or editor-integrated schema/autocomplete would make this "
            "much less error-prone, but the platform can adopt the YAML-file approach itself "
            "without that tooling existing yet."
        ),
    },
    "payments-webhook-handler": {
        "role": "Release Manager",
        "ground_truth": "WORK_ITEM",
        "text": (
            "The proposal does not include a runbook for on-call engineers describing how to "
            "manually replay a specific missed webhook if the automated retry path is "
            "exhausted. This should exist before the team is ever paged for a real incident, "
            "but doesn't need to exist before the webhook handler itself can be built and "
            "deployed."
        ),
    },
    "internal-analytics-dashboard": {
        "role": "Backend Developer",
        "ground_truth": "WORK_ITEM",
        "text": (
            "The proposal does not specify what testing framework or CI setup will be used for "
            "the dashboard's own codebase. Some automated testing should exist eventually, but "
            "the dashboard can be built and used by the data team without it existing on day "
            "one."
        ),
    },
}


NEW_SCENARIOS = [
    {
        "slug": "pilot-program-customer-portal",
        "title": "Build a self-service customer portal for the upcoming pilot program",
        "category": "Customer-facing / pilot program",
        "context": (
            "The team is building a self-service portal where users can view and manage their "
            "own account settings. Decide the concrete implementation of authentication and "
            "data handling for the initial version."
        ),
        "risk_profile": (
            "Currently used only by 4 internal test accounts during development. However, the "
            "team has already committed to onboarding the first cohort of 10 external pilot "
            "customers on March 1st, six weeks away, at which point the portal will store and "
            "display those customers' real names, email addresses, and billing history."
        ),
        "items": [
            {
                "role": "Security Reviewer",
                "ground_truth": "BLOCKING",
                "text": (
                    "The proposal logs full account details, including billing history, at INFO "
                    "level for debugging, with no redaction of personal information such as "
                    "names, emails, or billing history."
                ),
            },
            {
                "role": "Backend Developer",
                "ground_truth": "RISK",
                "text": (
                    "The proposal does not address how the portal would handle being accessed "
                    "in multiple languages or locales; right now all interface text is "
                    "hardcoded in English."
                ),
            },
            {
                "role": "Release Manager",
                "ground_truth": "WORK_ITEM",
                "text": (
                    "The proposal does not specify what customer support tooling will be used "
                    "to look up a specific pilot customer's account when they call in with an "
                    "issue."
                ),
            },
        ],
    },
]


CONSISTENCY_PROBE = {
    "slug": "consistency-probe",
    "title": "Add dark mode support to the internal analytics dashboard",
    "category": "Internal tooling / UI",
    "context": (
        "The data team has asked whether the internal analytics dashboard should support a "
        "dark color theme in addition to its current light-only theme."
    ),
    "risk_profile": (
        "Internal-only tool used by approximately 5 people on the data team. The team has "
        "mentioned wanting dark mode 'at some point' but it is not currently scheduled or "
        "prioritized, and no one has said it is urgent."
    ),
    "items": [
        {
            "role": "Backend Developer",
            "ground_truth": None,  # deliberately ambiguous -- scored for consistency, not correctness
            "text": (
                "The proposal does not specify how or when a dark theme would be implemented, "
                "or whether the current CSS architecture would need to be restructured to "
                "support theming at all."
            ),
        },
    ],
}


def build_round2_scenarios():
    """Original scenarios (from scenarios.py), each with its WORK_ITEM addition
    appended, plus the new scenarios. Kept as a function rather than a bare
    import-time list so scenarios.py stays untouched and independently
    re-runnable for round 1."""
    from scenarios import SCENARIOS as ROUND1_SCENARIOS

    scenarios = []
    for scenario in ROUND1_SCENARIOS:
        updated = dict(scenario)
        updated["items"] = list(scenario["items"]) + [WORK_ITEM_ADDITIONS[scenario["slug"]]]
        scenarios.append(updated)

    scenarios.extend(NEW_SCENARIOS)
    return scenarios


ROUND2_SCENARIOS = build_round2_scenarios()
