# Platform dogfooding data

Real, version-controlled Work Items and Decisions produced by using `decision-engine` and
`work-items` on this project's own development — not synthetic demo data (that still lives in
the gitignored `.decisions/`/`.work-items/` directories used by ad hoc test runs).

This is the default storage location for both CLIs when run from the repo root:

```
DecisionEngineCli run --origin work-item:<id>   # writes to platform-dogfooding/decisions/
WorkItemCli create <kind> <title>               # writes to platform-dogfooding/work-items/
```

Override with the `DECISION_ENGINE_STORE_DIR` / `WORK_ITEM_STORE_DIR` environment variables if
you need a scratch run that shouldn't be committed.

Each file is a JSON-lines event log for one aggregate — readable, and meant to be diffed in git
like any other source file, not treated as a binary blob.
