# full_dump — lower-threshold

Question: A finance stakeholder wants to lower the second-approver threshold from $5,000 to $2,000. What do you need to check or change, and what's the risk of just editing the config constant?

Wall time: 65.9s

Result ok: True

Usage: {"completion_tokens": 485, "prompt_tokens": 8042, "total_tokens": 8527, "prompt_tokens_details": {"cached_tokens": 7988}}


## Answer

To lower the second-approver threshold from $5,000 to $2,000, you need to update the `APPROVAL_THRESHOLD_CENTS` constant in the `config.py` file. This constant is used in the `approval_service.py` file to determine if an expense requires a second approver.

Here are the steps and considerations:

1. **Update the Configuration Constant:**
   - Open `config.py`.
   - Locate the `APPROVAL_THRESHOLD_CENTS` constant.
   - Change its value from `500_000` (5,000 cents) to `200_000` (2,000 cents).

   ```python
   # config.py
   APPROVAL_THRESHOLD_CENTS = 200_000
   ```

2. **Review and Test:**
   - Ensure that the `requires_second_approver` function in `approval_service.py` correctly uses this new threshold.
   - Run the existing test suite, particularly the tests in `test_approval_service.py`, to verify that the changes do not break any existing functionality.

3. **Regression Testing:**
   - Add or update tests to cover the new threshold, ensuring that expenses at exactly $2,000 require a second approver and that expenses below $2,000 do not.

4. **Deployment:**
   - Deploy the changes to the staging environment and perform thorough testing there.
   - Once satisfied, deploy to production.

**Risk Considerations:**

- **Boundary Conditions:** The original bug (INC-510) occurred because the boundary condition was incorrectly set to a strict greater-than comparison. Ensure that the new threshold is correctly set to an inclusive boundary (`>=`).
- **Impact on Existing Users:** Lowering the threshold will affect users who currently submit expenses above $2,000 but below $5,000. They will now require a second approver.
- **Audit Logging:** Ensure that the audit logging remains consistent and captures all state changes correctly, including the new threshold logic.
- **Documentation:** Update any relevant documentation, such as the README or conventions, to reflect the new threshold.

By following these steps and considering the risks, you can safely lower the second-approver threshold while minimizing the risk of introducing new issues.
