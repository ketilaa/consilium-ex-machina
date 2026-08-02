"""Task specs for the questions PoC, each with pre-registered ground truth.

Ambiguity ground truth is written before any model call, same discipline as
decisions.py (dissent objections) and context-packets/tasks.py (required facts).
Each ambiguity names an "intended_role" — the mandate most likely to notice it —
but grading counts an ambiguity as caught if ANY role (or the generalist) raises
it, since the thing under test is whether the panel's union catches more than any
one reviewer, not whether roles hit their "assigned" ambiguity specifically.

Unambiguous tasks are a control: fully specified requests with nothing genuine to
ask about, used to measure false positives (a role or the generalist inventing a
question anyway).
"""

AMBIGUOUS_TASKS = [
    {
        "slug": "cancel-order-endpoint",
        "spec": "Add an endpoint that lets a customer cancel an order they've placed.",
        "ambiguities": [
            {
                "dimension": "Whether cancelling removes the order record entirely (hard delete) or "
                "transitions it to a reversible 'cancelled' status — changes the data model and "
                "whether a cancellation can itself be undone.",
                "intended_role": "Backend Developer",
            },
            {
                "dimension": "Whether an order that has already shipped can still be cancelled, and "
                "if so what happens to the shipment and any refund.",
                "intended_role": "Domain Expert",
            },
            {
                "dimension": "Whether anyone other than the customer (e.g. support staff, an admin) "
                "can cancel on the customer's behalf, and whether that needs different authorization "
                "than the customer cancelling their own order.",
                "intended_role": "Security Reviewer",
            },
        ],
    },
    {
        "slug": "expense-reimbursement-multi-currency",
        "spec": (
            "Add a feature that calculates the total reimbursement amount for a batch of submitted "
            "expenses, where expenses can be in different currencies."
        ),
        "ambiguities": [
            {
                "dimension": "Which currency the total should be reported in.",
                "intended_role": "Domain Expert",
            },
            {
                "dimension": "Which exchange rate to use and when it's locked in (rate at submission "
                "time, at approval time, a fixed daily rate, or live) and the rounding rule — each "
                "produces a materially different total.",
                "intended_role": "Backend Developer",
            },
            {
                "dimension": "What happens if the exchange-rate source is unavailable when the batch "
                "is calculated — fail the whole batch, fall back to a last-known rate, or exclude "
                "that expense.",
                "intended_role": "Release Manager",
            },
        ],
    },
    {
        "slug": "notification-opt-out",
        "spec": "Let users turn off notifications from their account settings.",
        "ambiguities": [
            {
                "dimension": "Whether opting out also suppresses security/account-critical "
                "notifications (password reset, new-device login, payment failure), or only "
                "marketing/informational ones.",
                "intended_role": "Security Reviewer",
            },
            {
                "dimension": "Whether opt-out is global or per-channel (email/SMS/push independently), "
                "which changes how the preference is modeled and surfaced in the UI.",
                "intended_role": "Backend Developer",
            },
            {
                "dimension": "Whether opting out applies retroactively to notifications already queued "
                "or in flight, or only to ones triggered after the change.",
                "intended_role": "Architect",
            },
        ],
    },
    {
        "slug": "bulk-employee-import-duplicates",
        "spec": "Add a CSV bulk-import for employee records into the directory.",
        "ambiguities": [
            {
                "dimension": "What happens when an imported row's employee ID already exists in the "
                "directory — skip it, overwrite the existing record, or reject the whole file.",
                "intended_role": "Backend Developer",
            },
            {
                "dimension": "Whether the import should be restricted to certain roles/permissions "
                "given it can overwrite existing employee records, and whether there's an audit trail "
                "of who ran an import and what changed.",
                "intended_role": "Security Reviewer",
            },
            {
                "dimension": "Whether there's a row/file size limit, and what happens on a failure "
                "partway through the file — all-or-nothing transaction vs. partial commit of the rows "
                "processed so far.",
                "intended_role": "Performance Reviewer",
            },
        ],
    },
    {
        "slug": "session-timeout-reduction",
        "spec": "Reduce the session timeout to improve security.",
        "ambiguities": [
            {
                "dimension": "The actual target timeout value — without a specific number this "
                "isn't implementable at all, only guessable.",
                "intended_role": "Security Reviewer",
            },
            {
                "dimension": "Whether the new timeout applies retroactively to sessions that are "
                "already active, or only to sessions created after the change.",
                "intended_role": "Backend Developer",
            },
            {
                "dimension": "Whether this applies uniformly across all client types (web, mobile, "
                "machine/API tokens) or only to interactive human sessions.",
                "intended_role": "Architect",
            },
        ],
    },
]

UNAMBIGUOUS_TASKS = [
    {
        "slug": "health-check-endpoint",
        "spec": (
            "Add a GET /health endpoint. It must return HTTP 200 with the JSON body "
            '{"status": "ok"} whenever the process is running, requires no authentication, and '
            "must not touch the database or any external service."
        ),
    },
    {
        "slug": "rename-api-field",
        "spec": (
            "In the User API's JSON response, rename the field `full_name` to `display_name`. Keep "
            "the exact same string value and type; do not change any other field, endpoint, or "
            "behavior."
        ),
    },
    {
        "slug": "add-db-index",
        "spec": (
            "Add a database index on the `orders.customer_id` column to speed up the 'view my order "
            "history' query. No changes to the schema's columns and no changes to API behavior — "
            "only the new index."
        ),
    },
]
