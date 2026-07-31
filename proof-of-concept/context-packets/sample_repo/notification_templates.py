"""Proposed message templates, written up during a copy-review with Finance ops
so they could suggest wording changes without needing engineering to make
them. Not yet wired into notification_client.py — none of these constants are
imported anywhere in the running service yet. notification_client.py still
builds its message bodies inline for every notify_* function. Leaving this
here for whoever picks up the migration; don't assume it's already in use.
"""

APPROVED_SUBJECT = "Your expense was approved"
APPROVED_BODY_TEMPLATE = "Expense {expense_id} for {amount_display} has been approved."

REJECTED_SUBJECT = "Your expense was rejected"
REJECTED_BODY_TEMPLATE = "Expense {expense_id} was rejected: {note}"

PENDING_SECOND_APPROVAL_SUBJECT = "Your expense needs a second approver"
PENDING_SECOND_APPROVAL_BODY_TEMPLATE = (
    "Expense {expense_id} exceeds the single-approver threshold and is waiting on a second sign-off."
)

REMINDER_SUBJECT = "Reminder: expense pending approval"
REMINDER_BODY_TEMPLATE = (
    "Expense {expense_id} for {amount_display} has been pending for "
    "{hours_pending} hours and still needs approval."
)

CANCELLED_SUBJECT = "Your expense was cancelled"
CANCELLED_BODY_TEMPLATE = "Expense {expense_id} was cancelled before it was approved."


def render(template: str, **kwargs) -> str:
    return template.format(**kwargs)
