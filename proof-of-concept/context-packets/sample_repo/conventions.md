# Engineering Conventions

These are load-bearing conventions for this codebase. Do not deviate without a documented reason.

1. **All outbound HTTP calls MUST go through `http_client.request_with_retry()`.**
   Never call `requests` (or any other HTTP library) directly from application code. See
   `http_client.py` for why this exists — it is not optional.

2. **Money is always represented as an integer number of cents, never a float.**
   `Expense.amount_cents`, `APPROVAL_THRESHOLD_CENTS`, and every other monetary value in this
   codebase is an integer. Floating point money has caused rounding bugs in the past and is
   banned in code review.

3. **Any endpoint that changes approval state must write an audit log entry before returning.**
   See `audit_log.py` for the crash-safety reason this must happen synchronously, in-request —
   not via a background job or queue.

4. **New endpoints should follow the handler pattern already used in `expense_api.py`.**
   Consistency here matters more than any individual handler being "cleaner."

5. **Logging uses the standard `logging` module, never `print()`, in application code.**
   `audit_log.py` and `metrics.py` predate this convention and are grandfathered in; do
   not use them as a template for logging in new code.

6. **Tests live alongside the module they test, named `test_<module>.py`.**
   Regression tests that exist because of a specific past incident should say so in a
   comment or docstring, referencing the incident ID, so nobody "cleans up" a
   test that looks redundant without realizing why it's there.

7. **Currency/amount fields are USD-only for now.**
   Multi-currency is on the roadmap (see config.py) but not implemented anywhere;
   don't add currency-conversion logic speculatively.
