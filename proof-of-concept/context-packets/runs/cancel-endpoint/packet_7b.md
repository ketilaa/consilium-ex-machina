# packet — cancel-endpoint

Question: Add a new API endpoint that lets an employee cancel a pending expense before it's approved. What existing pattern must this follow, and what could silently go wrong if it's skipped?

Files included: ['conventions.md', 'expense_api.py', 'CHANGELOG.md', 'README.md', 'expense_repository.py', 'notification_client.py', 'audit_log.py', 'models.py', 'approval_service.py', 'config.py', 'http_client.py']

Wall time: 66.8s

Result ok: True

Usage: {"completion_tokens": 623, "prompt_tokens": 5580, "total_tokens": 6203, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To add a new API endpoint that lets an employee cancel a pending expense before it's approved, you must follow the handler pattern already used in `expense_api.py`. Specifically, you should:

1. **Do the state-changing work first**: This involves marking the expense as cancelled and updating its status.
2. **Call `audit_log.record(...)` synchronously, before returning**: This ensures that the cancellation is logged and can be traced back to the employee who initiated it.

### Concrete Implementation

Here's how you can implement the new endpoint:

1. **Define the new handler function** in `expense_api.py`:

```python
def handle_cancel_expense(expense: Expense, actor_id: str) -> dict:
    if expense.status != ExpenseStatus.PENDING:
        return {"error": "Expense is not in a cancellable state"}

    expense.status = ExpenseStatus.CANCELLED
    audit_log.record(expense.expense_id, actor_id, "cancelled")
    return {"expense_id": expense.expense_id, "status": expense.status.value}
```

2. **Add the new route** in `expense_api.py`:

```python
from flask import Blueprint, request

expense_api = Blueprint('expense_api', __name__)

@expense_api.route('/expenses/<expense_id>/cancel', methods=['POST'])
def cancel_expense(expense_id: str):
    expense = get_expense(expense_id)
    if not expense:
        return {"error": "Expense not found"}, 404

    return handle_cancel_expense(expense, request.actor_id)
```

3. **Ensure the `audit_log` is properly configured**:

```python
from audit_log import record

def handle_cancel_expense(expense: Expense, actor_id: str) -> dict:
    if expense.status != ExpenseStatus.PENDING:
        return {"error": "Expense is not in a cancellable state"}

    expense.status = ExpenseStatus.CANCELLED
    record(expense.expense_id, actor_id, "cancelled")
    return {"expense_id": expense.expense_id, "status": expense.status.value}
```

### What Could Silently Go Wrong if It's Skipped

If the `audit_log.record(...)` call is skipped, the following issues could arise:

1. **Lack of Traceability**: The cancellation of the expense will not be logged, making it impossible to trace back to the employee who initiated the cancellation. This could lead to disputes or compliance issues.
2. **Data Inconsistency**: Without the audit log, there might be no record of the expense being cancelled, which could lead to data inconsistencies if someone tries to query the expense status later.
3. **Compliance Issues**: Many organizations have strict compliance requirements for logging all state changes. Skipping the audit log could result in non-compliance, which could have legal or financial consequences.

By following the existing handler pattern and ensuring the `audit_log.record(...)` call is included, you can avoid these issues and maintain the integrity and traceability of the expense approval process.
