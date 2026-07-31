# Expense Approval Service

Internal service that lets employees submit expenses and routes them through an
approval workflow.

## Running locally

```
pip install -r requirements.txt
python -m expense_api
```

## Deployment

Deployed via the internal platform pipeline to the `expenses` namespace. See the
platform team's runbook for rollback steps. Scaled to 3 replicas behind the
internal load balancer; no service-specific scaling config is needed.

## Owning team

Finance Engineering. Slack channel `#finance-eng`.

## Environment variables

| Variable | Purpose |
|---|---|
| `EXPENSE_DB_URL` | Connection string for the primary datastore |
| `VENDOR_API_KEY` | Auth key for the vendor notification API |
| `DIRECTORY_API_KEY` | Auth key for the internal employee directory |
| `LOG_LEVEL` | Standard Python logging level, defaults to `INFO` |

## Testing

`pytest` is used for all tests. Run the full suite with `pytest -q` from the
repo root. CI runs the same command on every pull request; a red CI check
blocks merge regardless of who approves the review.

## Architecture overview

This is a straightforward layered service: HTTP handlers in `expense_api.py`
call into `approval_service.py` for business logic, which in turn touches
`models.py` for data shapes and `notification_client.py` for outbound
notifications. There is no message queue or event bus in this service today —
everything is synchronous, in-request. A queue-based redesign has been
discussed for the reporting features but is out of scope for the core
approval flow.

## Data layer

`expense_repository.py` is currently an in-memory stand-in for what will
eventually be a Postgres-backed repository. The public functions (`save`,
`get`, `list_all`, `list_pending`, `list_for_employee`) are the intended
long-term interface; avoid reaching into module internals from new code so the
eventual swap to a real database doesn't require touching every call site.

## Known gaps / backlog

- No multi-currency support (see config.DEFAULT_CURRENCY).
- No self-service third-party submission API; `rate_limiter.py` was written
  for that proposal but the API itself was deprioritized.
- No circuit breaker in `http_client.py`, just retry-with-backoff; `CallStats`
  is observational only.
- Reporting/org-chart features (via `employee_directory_client.py`) are
  planned to move to an async queue eventually; not urgent.
