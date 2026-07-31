# full_dump — cancel-endpoint

Question: Add a new API endpoint that lets an employee cancel a pending expense before it's approved. What existing pattern must this follow, and what could silently go wrong if it's skipped?

Wall time: 59.1s

Result ok: True

Usage: {"completion_tokens": 163, "prompt_tokens": 8029, "total_tokens": 8192, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To add a new API endpoint that lets an employee cancel a pending expense before it's approved, you should follow the handler pattern already used in `expense_api.py`. Specifically, this means:

1. **Do the state-changing work first.**
2. **Call `audit_log.record(...)` synchronously, before returning — see `conventions.md` rule 3 and `audit_log.py` for why this can't be deferred to a background job.**
3. **Return a small, consistent dict shape: `{"expense_id": ..., "status": ...}`.**

Here’s how you can implement this new endpoint:

### expense_api.py

```python
def handle_cancel_expense(expense: Expense, actor_id: str) -> dict:
    if expense.status != ExpenseStatus.PENDING:
