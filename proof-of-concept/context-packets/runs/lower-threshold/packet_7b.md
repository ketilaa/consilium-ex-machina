# packet — lower-threshold

Question: A finance stakeholder wants to lower the second-approver threshold from $5,000 to $2,000. What do you need to check or change, and what's the risk of just editing the config constant?

Files included: ['conventions.md', 'CHANGELOG.md', 'test_approval_service.py', 'README.md', 'approval_service.py', 'expense_repository.py', 'config.py', 'models.py', 'notification_client.py']

Wall time: 55.7s

Result ok: True

Usage: {"completion_tokens": 621, "prompt_tokens": 4222, "total_tokens": 4843, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To lower the second-approver threshold from $5,000 to $2,000, you need to check and change the `APPROVAL_THRESHOLD_CENTS` constant in `config.py`. Specifically, you would need to change the value from `500_000` to `200_000`.

### What to Change

1. **Edit the `APPROVAL_THRESHOLD_CENTS` Constant:**
   ```python
   APPROVAL_THRESHOLD_CENTS = 200_000
   ```

2. **Update the `requires_second_approver` Function:**
   This function is already correctly implemented to handle the inclusive boundary condition. No changes are needed here.

### Potential Risks of Just Editing the Config Constant

1. **Incorrect Boundary Handling:**
   If you simply change the constant without understanding the existing logic, you might accidentally introduce a bug. The current logic correctly handles the inclusive boundary condition, but if you change it without testing, you could break this behavior.

2. **Testing:**
   You need to ensure that the change does not break any existing functionality. Specifically, you should run the relevant tests to confirm that expenses below $2,000 do not require a second approver, and expenses at or above $2,000 do require a second approver.

3. **Audit Logging:**
   Since the audit logging is synchronous and in-request, you need to ensure that the audit logs are correctly written for all state-changing endpoints. The current implementation should handle this correctly, but you should verify that the logs are being written as expected.

4. **Regression Testing:**
   You should add or update regression tests to cover the new threshold. For example, you might add a test to ensure that an expense exactly at the new threshold requires a second approver.

5. **Documentation:**
   Update any relevant documentation to reflect the new threshold. This might include the README, CHANGELOG, and any internal documentation.

### Example Test to Add

You can add a test to ensure that the new threshold is correctly handled:

```python
def test_approval_threshold_lowered():
    expense = _expense(200000)  # $2,000
    assert requires_second_approver(expense)
    expense = _expense(199999)  # $1,999.99
    assert not requires_second_approver(expense)
```

### Conclusion

To safely lower the second-approver threshold, you should:

1. Change the `APPROVAL_THRESHOLD_CENTS` constant to `200_000`.
2. Run the relevant tests to ensure that the new threshold is correctly handled.
3. Verify that the audit logs are correctly written for all state-changing endpoints.
4. Update any relevant documentation.

Just editing the constant without these checks and tests could introduce bugs, so it's important to follow a thorough process to ensure the change is safe and effective.
