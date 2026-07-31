"""Core data models for the expense approval service.

All monetary fields are integer cents, never floats (see conventions.md, rule 2).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExpenseStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass
class Employee:
    employee_id: str
    full_name: str
    email: str
    manager_id: str | None = None


@dataclass
class Expense:
    expense_id: str
    employee_id: str
    amount_cents: int
    description: str
    status: ExpenseStatus = ExpenseStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    approver_ids: list[str] = field(default_factory=list)


@dataclass
class Approval:
    expense_id: str
    approver_id: str
    approved: bool
    note: str = ""
    decided_at: datetime = field(default_factory=datetime.utcnow)


def format_cents_as_display_string(amount_cents: int) -> str:
    """Formats an integer-cents amount for display, e.g. 500000 -> "$5,000.00".

    This is the only place in the codebase that should convert cents to a
    dollar float, and only for display — never store the result of this
    function back into an Expense or Approval field (see conventions.md, rule
    2: money is always integer cents internally).
    """
    dollars = amount_cents / 100
    return f"${dollars:,.2f}"


def validate_expense(expense: Expense) -> list[str]:
    """Returns a list of validation error messages (empty list = valid)."""
    errors = []
    if expense.amount_cents <= 0:
        errors.append("amount_cents must be positive")
    if not expense.description.strip():
        errors.append("description must not be empty")
    if not expense.employee_id:
        errors.append("employee_id is required")
    return errors
