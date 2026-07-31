"""HTTP API handlers for expenses. New endpoints should follow this pattern:

  1. Do the state-changing work first.
  2. Call audit_log.record(...) synchronously, before returning — see
     conventions.md rule 3 and audit_log.py for why this can't be deferred to a
     background job.
  3. Return a small, consistent dict shape: {"expense_id": ..., "status": ...}.

This module intentionally has no framework-specific decorators (Flask/FastAPI
routing is wired up elsewhere) so handlers stay easy to unit test directly.
"""

import audit_log
from approval_service import record_approval
from models import Approval, Expense


def handle_submit_expense(expense: Expense, actor_id: str) -> dict:
    audit_log.record(expense.expense_id, actor_id, "submitted")
    return {"expense_id": expense.expense_id, "status": expense.status.value}


def handle_get_expense(expense: Expense) -> dict:
    return {
        "expense_id": expense.expense_id,
        "employee_id": expense.employee_id,
        "amount_cents": expense.amount_cents,
        "description": expense.description,
        "status": expense.status.value,
    }


def handle_decide_expense(expense: Expense, approval: Approval, employee_email: str, actor_id: str) -> dict:
    new_status = record_approval(expense, approval, employee_email)
    audit_log.record(
        expense.expense_id,
        actor_id,
        "approved" if approval.approved else "rejected",
        detail=approval.note,
    )
    return {"expense_id": expense.expense_id, "status": new_status.value}


def handle_list_expenses_for_employee(expenses: list[Expense], employee_id: str) -> dict:
    matching = [e for e in expenses if e.employee_id == employee_id]
    return {
        "expenses": [
            {"expense_id": e.expense_id, "amount_cents": e.amount_cents, "status": e.status.value}
            for e in matching
        ]
    }
