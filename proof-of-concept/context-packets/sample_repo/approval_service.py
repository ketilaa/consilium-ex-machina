"""Core business logic for approving and rejecting expenses."""

from datetime import datetime, timedelta

from config import APPROVAL_THRESHOLD_CENTS, REMINDER_AFTER_HOURS
from models import Approval, Expense, ExpenseStatus
from notification_client import (
    notify_expense_approved,
    notify_expense_pending_second_approval,
    notify_expense_rejected,
)


class DuplicateApprovalError(Exception):
    pass


def requires_second_approver(expense: Expense) -> bool:
    # Boundary is inclusive: an expense for exactly the threshold amount requires a
    # second approver too. This was a real bug (INC-510) — see
    # test_approval_service.py for the regression test that guards it. Do not
    # "simplify" this to a strict greater-than comparison.
    return expense.amount_cents >= APPROVAL_THRESHOLD_CENTS


def is_stale(expense: Expense, now: datetime | None = None) -> bool:
    """True once an expense has been pending longer than REMINDER_AFTER_HOURS."""
    now = now or datetime.utcnow()
    if expense.status != ExpenseStatus.PENDING:
        return False
    return now - expense.created_at >= timedelta(hours=REMINDER_AFTER_HOURS)


def record_approval(expense: Expense, approval: Approval, employee_email: str) -> ExpenseStatus:
    if expense.status != ExpenseStatus.PENDING:
        raise DuplicateApprovalError(
            f"expense {expense.expense_id} is already {expense.status.value}, cannot record another decision"
        )

    if approval.approver_id in expense.approver_ids:
        raise DuplicateApprovalError(
            f"approver {approval.approver_id} already decided on expense {expense.expense_id}"
        )

    if not approval.approved:
        expense.status = ExpenseStatus.REJECTED
        notify_expense_rejected(employee_email, expense.expense_id, approval.note)
        return expense.status

    expense.approver_ids.append(approval.approver_id)

    if requires_second_approver(expense) and len(expense.approver_ids) < 2:
        # Still pending a second sign-off; do not mark approved or notify of
        # final approval yet — just let the submitter know it's in the
        # second-approval queue.
        notify_expense_pending_second_approval(employee_email, expense.expense_id)
        return expense.status

    expense.status = ExpenseStatus.APPROVED
    notify_expense_approved(employee_email, expense.expense_id, expense.amount_cents)
    return expense.status
