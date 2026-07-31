"""Tasks against sample_repo/, each with a pre-registered grading rubric.

required_facts are written before any run and graded by reading the transcript
manually — not by an automated judge — same methodology as the decision-making
PoC. relevant_files is the ground truth used to score the packet builder's
selection precision/recall; distractor_bait is documented for the writeup, not
used mechanically.
"""

TASKS = [
    {
        "slug": "reminder-job",
        "question": (
            "Implement a function `send_reminders_for_stale_expenses()` that finds "
            "every pending expense older than the configured reminder threshold and "
            "sends a reminder notification for each one. What must you reuse from "
            "the existing codebase, and what could go wrong if you don't?"
        ),
        "relevant_files": [
            "config.py",
            "approval_service.py",
            "expense_repository.py",
            "notification_client.py",
            "http_client.py",
            "conventions.md",
        ],
        "distractor_bait": [
            "notification_templates.py",  # sounds directly relevant, is unused/not wired in
            "rate_limiter.py",  # sounds relevant to "sending many", is deprecated/unused
        ],
        "required_facts": [
            "Uses config.REMINDER_AFTER_HOURS (or equivalent existing constant) as the staleness "
            "threshold rather than a hardcoded number",
            "Reuses approval_service.is_stale() and/or expense_repository.list_pending() rather "
            "than reimplementing the staleness/filtering check",
            "Sends via notification_client (e.g. notify_expense_reminder), which routes through "
            "http_client.request_with_retry — does not call an HTTP library directly",
            "Explains why this matters specifically for reminders: the vendor API silently drops "
            "requests under load (INC-482), so a direct call would silently lose reminders",
        ],
    },
    {
        "slug": "lower-threshold",
        "question": (
            "A finance stakeholder wants to lower the second-approver threshold from "
            "$5,000 to $2,000. What do you need to check or change, and what's the "
            "risk of just editing the config constant?"
        ),
        "relevant_files": ["config.py", "approval_service.py", "test_approval_service.py", "conventions.md"],
        "distractor_bait": ["legacy_importer.py", "CHANGELOG.md"],
        "required_facts": [
            "APPROVAL_THRESHOLD_CENTS is in integer cents, so $2,000 is 200_000, not 2_000 — flags "
            "the order-of-magnitude risk of forgetting the cents convention",
            "The boundary check in requires_second_approver is inclusive (>=), specifically because "
            "of a past bug (INC-510) — must not simplify it to a strict >",
            "Notes that test_approval_service.py has a regression test tied to the boundary value "
            "that needs to stay correct (or be updated consistently) after the threshold changes",
        ],
    },
    {
        "slug": "cancel-endpoint",
        "question": (
            "Add a new API endpoint that lets an employee cancel a pending expense "
            "before it's approved. What existing pattern must this follow, and what "
            "could silently go wrong if it's skipped?"
        ),
        "relevant_files": [
            "audit_log.py",
            "expense_api.py",
            "expense_repository.py",
            "models.py",
            "conventions.md",
        ],
        "distractor_bait": ["metrics.py", "rate_limiter.py"],
        "required_facts": [
            "Calls audit_log.record(..., action=\"cancelled\", ...) synchronously before returning, "
            "per the crash-safety reasoning in audit_log.py / conventions.md rule 3",
            "Follows the existing handler pattern in expense_api.py (do the work, then audit, then "
            "return the small consistent dict shape)",
            "Sets the expense's status to CANCELLED via expense_repository.save(), and explicitly "
            "does NOT call expense_repository.delete() — delete is hard-delete for admin/support "
            "tooling only and would break the audit trail's history guarantee",
        ],
    },
    {
        "slug": "silent-notification-failure",
        "question": (
            "Why might expense notifications fail silently under load, and what "
            "already exists in this codebase to prevent that?"
        ),
        "relevant_files": ["http_client.py", "notification_client.py"],
        "distractor_bait": ["metrics.py", "rate_limiter.py"],
        "required_facts": [
            "Identifies that the vendor notification API silently drops requests under load "
            "(returns an empty/ambiguous response rather than an error) — incident INC-482",
            "Identifies that http_client.request_with_retry already mitigates this via retry with "
            "backoff/jitter and explicit detection of empty/5xx responses as failures",
            "Notes that notification_client.py already routes everything through it, and that "
            "bypassing it (e.g. a direct requests call) would reintroduce the bug",
        ],
    },
]
