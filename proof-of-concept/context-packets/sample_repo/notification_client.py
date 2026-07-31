"""Sends notifications to employees about their expenses.

All sends go through `http_client.request_with_retry` (see conventions.md, rule
1) — this module has no retry logic of its own, and it must not grow any,
because the INC-482 mitigation lives in exactly one place by design.
"""

from config import VENDOR_NOTIFICATION_API_BASE_URL
from http_client import request_with_retry


def send_notification(employee_email: str, subject: str, body: str) -> None:
    request_with_retry(
        "POST",
        f"{VENDOR_NOTIFICATION_API_BASE_URL}/messages",
        json={"to": employee_email, "subject": subject, "body": body},
    )


def send_bulk_notification(employee_emails: list[str], subject: str, body: str) -> None:
    """Used by the weekly digest job. Sends one call per recipient rather than a
    single batched vendor call, because the vendor API's batch endpoint has a
    separate, undocumented rate limit that isn't worth the complexity for the
    current notification volume (a few hundred employees at most).
    """
    for email in employee_emails:
        send_notification(email, subject, body)


def notify_expense_approved(employee_email: str, expense_id: str, amount_cents: int) -> None:
    dollars = amount_cents / 100
    send_notification(
        employee_email,
        subject="Your expense was approved",
        body=f"Expense {expense_id} for ${dollars:.2f} has been approved.",
    )


def notify_expense_rejected(employee_email: str, expense_id: str, note: str) -> None:
    send_notification(
        employee_email,
        subject="Your expense was rejected",
        body=f"Expense {expense_id} was rejected: {note}",
    )


def notify_expense_pending_second_approval(employee_email: str, expense_id: str) -> None:
    send_notification(
        employee_email,
        subject="Your expense needs a second approver",
        body=f"Expense {expense_id} exceeds the single-approver threshold and is waiting on a second sign-off.",
    )


def notify_expense_reminder(employee_email: str, expense_id: str, amount_cents: int, hours_pending: int) -> None:
    """Reminder sent when an expense has been pending longer than
    config.REMINDER_AFTER_HOURS. Reuses send_notification like every other
    notification in this module — see conventions.md, rule 1, before adding a
    direct HTTP call here.
    """
    dollars = amount_cents / 100
    send_notification(
        employee_email,
        subject="Reminder: expense pending approval",
        body=(
            f"Expense {expense_id} for ${dollars:.2f} has been pending for "
            f"{hours_pending} hours and still needs approval."
        ),
    )
