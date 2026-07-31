# packet — lower-threshold

Question: A finance stakeholder wants to lower the second-approver threshold from $5,000 to $2,000. What do you need to check or change, and what's the risk of just editing the config constant?

Files included: ['conventions.md', 'CHANGELOG.md', 'test_approval_service.py', 'README.md', 'approval_service.py', 'expense_repository.py', 'config.py', 'models.py', 'notification_client.py']

Wall time: 113.0s

Result ok: True

Usage: {"completion_tokens": 603, "prompt_tokens": 4222, "total_tokens": 4825, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To lower the second-approver threshold from $5,000 to $2,000, you need to update the `APPROVAL_THRESHOLD_CENTS` constant in `config.py`. Here are the steps and considerations:

### Steps to Update the Threshold

1. **Modify `APPROVAL_THRESHOLD_CENTS` in `config.py`:**
   - Open `config.py`.
   - Locate the `APPROVAL_THRESHOLD_CENTS` constant.
   - Change its value from `500_000` (5,000 cents) to `200_000` (2,000 cents).

   ```python
   # config.py
   APPROVAL_THRESHOLD_CENTS = 200_000  # $2,000.00 -> 200000 cents
   ```

2. **Ensure Consistency Across Tests:**
   - Check the test cases in `test_approval_service.py` to ensure they reflect the new threshold.
   - Update any test cases that assume the old threshold value.

   ```python
   # test_approval_service.py
   def test_below_threshold_does_not_require_second_approver():
       assert not requires_second_approver(_expense(200_000 - 1))  # Updated to reflect new threshold

   def test_approval_requires_second_approver_at_threshold():
       assert requires_second_approver(_expense(200_000))  # Updated to reflect new threshold
   ```

3. **Review and Update Documentation:**
   - Update any relevant documentation, such as `README.md` or `conventions.md`, to reflect the new threshold.
   - Ensure that any changelog entries or release notes mention the change.

### Risks of Editing the Config Constant

1. **Impact on Existing Logic:**
   - The change might affect existing logic that relies on the threshold value. Ensure that all parts of the codebase that use this constant are correctly updated.
   - For example, the `requires_second_approver` function in `approval_service.py` directly uses this constant.

2. **Testing:**
   - Without proper testing, there is a risk of introducing bugs. Ensure that all related tests are updated and run to verify the change.
   - Consider adding new test cases to cover the new threshold value.

3. **Deployment:**
   - Ensure that the change is properly tested in a staging environment before deploying to production.
   - Consider the impact on user experience and any potential for confusion or frustration if the threshold changes unexpectedly.

4. **Compliance and Policy:**
   - Verify that the new threshold aligns with any existing compliance requirements or internal policies.
   - Ensure that stakeholders are aware of the change and its implications.

By following these steps and considering the risks, you can safely update the second-approver threshold to $2,000.
