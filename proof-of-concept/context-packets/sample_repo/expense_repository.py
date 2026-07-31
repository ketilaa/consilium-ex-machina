"""In-memory data-access layer for expenses, standing in for the real
database-backed repository until the service is wired up to Postgres. The
interface here (get/save/list) is the shape the eventual DB-backed repository
should match, so callers don't need to change when that lands.
"""

from models import Expense, ExpenseStatus

_EXPENSES: dict[str, Expense] = {}


def save(expense: Expense) -> None:
    _EXPENSES[expense.expense_id] = expense


def get(expense_id: str) -> Expense | None:
    return _EXPENSES.get(expense_id)


def list_all() -> list[Expense]:
    return list(_EXPENSES.values())


def list_pending() -> list[Expense]:
    return [e for e in _EXPENSES.values() if e.status == ExpenseStatus.PENDING]


def list_for_employee(employee_id: str) -> list[Expense]:
    return [e for e in _EXPENSES.values() if e.employee_id == employee_id]


def delete(expense_id: str) -> None:
    """Hard-deletes an expense record. Not used by any current endpoint — the
    product decision has always been to cancel (soft, keeps the audit trail)
    rather than delete. Kept for admin/support tooling only, and should stay
    that way; a user-facing delete would conflict with audit_log.py's
    assumption that every expense's history is fully reconstructable.
    """
    _EXPENSES.pop(expense_id, None)


def reset_for_tests() -> None:
    _EXPENSES.clear()
