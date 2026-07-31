"""Writes audit trail entries for state-changing actions on expenses.

IMPORTANT: `record(...)` must be called synchronously, in-request, before the
handler returns a response — not handed off to a background job or queue. If the
process crashes between returning a response and an async audit write landing, we
end up with an approval/rejection that took effect but has no audit record of who
did it or why, which has already caused a compliance finding once (an auditor
could not reconstruct who approved a specific high-value expense because the
async writer's queue was lost during a deploy). See conventions.md, rule 3.

This module deliberately has no batching, buffering, or async queue for that
reason — every call to `record` hits the store before returning.
"""

from datetime import datetime

_ENTRIES: list[dict] = []

VALID_ACTIONS = {"submitted", "approved", "rejected", "cancelled", "reminder_sent"}


def record(expense_id: str, actor_id: str, action: str, detail: str = "") -> None:
    if action not in VALID_ACTIONS:
        raise ValueError(f"unknown audit action: {action!r}, expected one of {VALID_ACTIONS}")
    entry = {
        "expense_id": expense_id,
        "actor_id": actor_id,
        "action": action,
        "detail": detail,
        "at": datetime.utcnow().isoformat(),
    }
    _write_entry(entry)


def entries_for_expense(expense_id: str) -> list[dict]:
    """Used by the internal support tool to reconstruct an expense's history."""
    return [e for e in _ENTRIES if e["expense_id"] == expense_id]


def _write_entry(entry: dict) -> None:
    # In production this appends to an append-only audit store (a dedicated,
    # replicated table — separate from the main application database so a
    # rollback of application data can never silently roll back audit history
    # too). Stubbed here as an in-memory list for the sample repo.
    _ENTRIES.append(entry)
    print(f"[audit] {entry}")
