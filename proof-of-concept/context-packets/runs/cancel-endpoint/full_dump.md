# full_dump — cancel-endpoint

Question: Add a new API endpoint that lets an employee cancel a pending expense before it's approved. What existing pattern must this follow, and what could silently go wrong if it's skipped?

Wall time: 86.5s

Result ok: True

Usage: {"completion_tokens": 638, "prompt_tokens": 8029, "total_tokens": 8667, "prompt_tokens_details": {"cached_tokens": 7988}}


## Answer

To add a new API endpoint that allows an employee to cancel a pending expense before it's approved, you must follow the existing pattern established in `expense_api.py`. Specifically, the new endpoint should:

1. **Do the state-changing work first.**
2. **Call `audit_log.record(...)` synchronously, before returning.**
3. **Return a small, consistent dict shape: `{"expense_id": ..., "status": ...}`.**

Here's how you can implement this:

### Step 1: Define the New Endpoint in `expense_api.py`

```python
def handle_cancel_expense(expense: Expense, actor_id: str) -> dict:
    if expense.status != ExpenseStatus.PENDING:
        raise ValueError("Only pending expenses can be cancelled.")
    
    # Change the status to CANCELLED
    expense.status = ExpenseStatus.CANCELLED
    
    # Save the updated expense
    save(expense)
    
    # Record the audit log entry
    audit_log.record(expense.expense_id, actor_id, "cancelled")
    
    return {"expense_id": expense.expense_id, "status": expense.status.value}
```

### Step 2: Ensure `ExpenseRepository` Supports Cancellation

Ensure that the `ExpenseRepository` has a method to save the updated expense. In `expense_repository.py`, you can use the existing `save` method:

```python
def save(expense: Expense) -> None:
    _EXPENSES[expense.expense_id] = expense
```

### Step 3: Add a Test in `test_expense_api.py`

To ensure the new endpoint works as expected, add a test in `test_expense_api.py`:

```python
def test_cancel_pending_expense(monkeypatch):
    monkeypatch.setattr("notification_client.send_notification", lambda *a, **k: None)
    expense = _expense(1000)  # $10.00
    save(expense)  # Save the expense to the repository
    
    # Cancel the expense
    result = handle_cancel_expense(expense, "employee@example.com")
    
    assert result == {"expense_id": expense.expense_id, "status": "cancelled"}
    assert expense.status == ExpenseStatus.CANCELLED
```

### What Could Silently Go Wrong if These Steps Are Skipped?

1. **Audit Logging**: If you skip the audit log entry, you lose the ability to trace who cancelled the expense and why. This violates convention 3 and could lead to compliance issues.

2. **Consistent Return Shape**: If you return a different shape or omit the `status` field, it could break client-side code that expects a consistent response structure. This would lead to bugs that are hard to diagnose.

3. **State Change Order**: If you change the status after recording the audit log, the audit log would reflect an incorrect state. This would lead to inconsistent data and make debugging difficult.

By following the established pattern, you ensure that the new endpoint integrates seamlessly with the existing system and adheres to the conventions that have been proven to work.
