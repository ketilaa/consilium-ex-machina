# full_dump — lower-threshold

Question: A finance stakeholder wants to lower the second-approver threshold from $5,000 to $2,000. What do you need to check or change, and what's the risk of just editing the config constant?

Wall time: 58.2s

Result ok: True

Usage: {"completion_tokens": 150, "prompt_tokens": 8042, "total_tokens": 8192, "prompt_tokens_details": {"cached_tokens": 0}}


## Answer

To lower the second-approver threshold from $5,000 to $2,000, you need to check and change the following:

1. **Edit the `APPROVAL_THRESHOLD_CENTS` constant in `config.py`:**
   - Change the value from `500_000` to `200_000`.

2. **Update the `requires_second_approver` function in `approval_service.py`:**
   - Ensure the logic correctly handles the new threshold. The current logic is:
     ```python
     return expense.amount_cents >= APPROVAL_THRESHOLD_CENTS
     ```
   - This logic is already correct for the new threshold, so no changes are needed here.
