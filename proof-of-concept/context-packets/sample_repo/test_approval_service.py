"""Tests for approval_service.py."""

from approval_service import requires_second_approver, record_approval
from config import APPROVAL_THRESHOLD_CENTS
from models import Approval, Expense, ExpenseStatus


def _expense(amount_cents: int) -> Expense:
    return Expense(
        expense_id="exp-1",
        employee_id="emp-1",
        amount_cents=amount_cents,
        description="test",
    )


def test_below_threshold_does_not_require_second_approver():
    assert not requires_second_approver(_expense(APPROVAL_THRESHOLD_CENTS - 1))


def test_approval_requires_second_approver_at_threshold():
    # Regression test for INC-510: an expense for EXACTLY the threshold amount
    # was being auto-approved with a single approver because the original check
    # used `>` instead of `>=`. The boundary is inclusive — do not "simplify"
    # this back to a strict greater-than comparison.
    assert requires_second_approver(_expense(APPROVAL_THRESHOLD_CENTS))


def test_single_approval_leaves_high_value_expense_pending(monkeypatch):
    monkeypatch.setattr("notification_client.send_notification", lambda *a, **k: None)
    expense = _expense(APPROVAL_THRESHOLD_CENTS)
    approval = Approval(expense_id=expense.expense_id, approver_id="mgr-1", approved=True)
    status = record_approval(expense, approval, "employee@example.com")
    assert status == ExpenseStatus.PENDING


def test_two_approvals_clears_high_value_expense(monkeypatch):
    monkeypatch.setattr("notification_client.send_notification", lambda *a, **k: None)
    expense = _expense(APPROVAL_THRESHOLD_CENTS)
    record_approval(
        expense, Approval(expense_id=expense.expense_id, approver_id="mgr-1", approved=True), "e@example.com"
    )
    status = record_approval(
        expense, Approval(expense_id=expense.expense_id, approver_id="mgr-2", approved=True), "e@example.com"
    )
    assert status == ExpenseStatus.APPROVED


def test_rejection_does_not_require_second_approver(monkeypatch):
    monkeypatch.setattr("notification_client.send_notification", lambda *a, **k: None)
    expense = _expense(APPROVAL_THRESHOLD_CENTS)
    approval = Approval(expense_id=expense.expense_id, approver_id="mgr-1", approved=False, note="not reimbursable")
    status = record_approval(expense, approval, "employee@example.com")
    assert status == ExpenseStatus.REJECTED


def test_low_value_expense_needs_only_one_approval(monkeypatch):
    monkeypatch.setattr("notification_client.send_notification", lambda *a, **k: None)
    expense = _expense(1000)  # $10.00
    approval = Approval(expense_id=expense.expense_id, approver_id="mgr-1", approved=True)
    status = record_approval(expense, approval, "employee@example.com")
    assert status == ExpenseStatus.APPROVED
