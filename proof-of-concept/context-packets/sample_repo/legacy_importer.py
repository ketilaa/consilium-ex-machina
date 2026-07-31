"""One-off script that imported historical expense records from the old system
during the 2023 migration. Kept for reference only — not part of the running
service and not imported by anything else. Safe to ignore for day-to-day work.

The old system stored amounts as floats in dollars, which is exactly the kind
of representation conventions.md rule 2 now forbids — the conversion to
integer cents below is the whole reason this script has to exist rather than
just being a straight copy.
"""

import csv
import logging

from models import Expense, ExpenseStatus

logger = logging.getLogger(__name__)


class LegacyRowError(Exception):
    pass


def _parse_amount_cents(amount_usd_str: str) -> int:
    try:
        dollars = float(amount_usd_str)
    except ValueError as exc:
        raise LegacyRowError(f"unparseable amount: {amount_usd_str!r}") from exc
    # Old system rounded to the nearest cent already, but floating point
    # representation can still leave e.g. 19.999999999998 — round explicitly.
    return round(dollars * 100)


def _parse_status(raw_status: str) -> ExpenseStatus:
    legacy_status_map = {
        "PENDING_APPROVAL": ExpenseStatus.PENDING,
        "APPROVED": ExpenseStatus.APPROVED,
        "DENIED": ExpenseStatus.REJECTED,
        "WITHDRAWN": ExpenseStatus.CANCELLED,
    }
    if raw_status not in legacy_status_map:
        raise LegacyRowError(f"unknown legacy status: {raw_status!r}")
    return legacy_status_map[raw_status]


def import_legacy_csv(path: str) -> list[Expense]:
    expenses = []
    skipped = 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                expenses.append(
                    Expense(
                        expense_id=row["id"],
                        employee_id=row["employee"],
                        amount_cents=_parse_amount_cents(row["amount_usd"]),
                        description=row["memo"],
                        status=_parse_status(row["status"]),
                    )
                )
            except LegacyRowError as exc:
                logger.warning("skipping unparseable legacy row %s: %s", row.get("id"), exc)
                skipped += 1
    logger.info("imported %d legacy expenses, skipped %d", len(expenses), skipped)
    return expenses
