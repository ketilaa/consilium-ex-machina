# packet — cancel-endpoint

Question: Add a new API endpoint that lets an employee cancel a pending expense before it's approved. What existing pattern must this follow, and what could silently go wrong if it's skipped?

Files included: ['conventions.md', 'expense_api.py', 'CHANGELOG.md', 'README.md', 'expense_repository.py', 'notification_client.py', 'audit_log.py', 'models.py', 'approval_service.py', 'config.py', 'http_client.py']

Wall time: 117.0s

Result ok: True

Usage: {"completion_tokens": 444, "prompt_tokens": 5580, "total_tokens": 6024, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To add a new API endpoint that allows an employee to cancel a pending expense before it's approved, you must follow the established pattern used in `expense_api.py`. This pattern includes:

1. **State-changing work first**: Perform the action that changes the state of the expense.
2. **Audit log entry**: Record an audit log entry synchronously before returning a response.
3. **Return a consistent dict shape**: Return a small, consistent dictionary with relevant information.

### Implementation Steps

1. **Define the Handler Function**: Create a new function in `expense_api.py` to handle the cancellation of an expense.

2. **State-changing Work**: Update the expense status to `CANCELLED`.

3. **Audit Log Entry**: Use `audit_log.record()` to log the cancellation action.

4. **Return a Consistent Response**: Return a dictionary with the expense ID and new status.

### Example Implementation

```python
# expense_api.py

def handle_cancel_expense(expense: Expense, actor_id: str) -> dict:
    if expense.status != ExpenseStatus.PENDING:
        raise ValueError("Only pending expenses can be cancelled")

    expense.status = ExpenseStatus.CANCELLED
    audit_log.record(expense.expense_id, actor_id, "cancelled")
    return {"expense_id": expense.expense_id, "status": expense.status.value}
```

### Potential Issues if Skipped

1. **Audit Log Omission**: If the audit log entry is skipped, there will be no record of who cancelled the expense and when. This could lead to compliance issues and difficulty in reconstructing the expense's history.

2. **Inconsistent State Management**: Not following the established pattern could lead to inconsistencies in how state changes are handled across the codebase. This might make the code harder to maintain and debug.

3. **Security Risks**: If the state-changing work is not done first, it could lead to security vulnerabilities, such as allowing an expense to be cancelled after it has already been approved.

By adhering to the established pattern, you ensure that the new endpoint is consistent with the rest of the codebase and that all necessary actions are performed in a controlled and secure manner.
