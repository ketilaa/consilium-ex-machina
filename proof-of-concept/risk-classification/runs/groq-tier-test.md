# Model-tiering test: openai/gpt-oss-120b (Groq-hosted) vs. local ~24B model

Same classifier prompt (`classifier_system_5way_with_work_item`), same scenarios and items
(`scenarios_round2.py`), same scoring. 1 pass per scenario (not the usual 3 reps), given the
Groq API key used for this test was short-lived and rate-limited (8000 tokens/minute on the
`on_demand` tier for `openai/gpt-oss-120b`, hit after 3 of 4 scenarios on the first attempt).

## role-registry-configurability

Groq classification:

```
Item 1: [BLOCKING]
Item 2: [BLOCKING]
Item 3: [BLOCKING]
Item 4: [WORK_ITEM] -- "Define a strategy for handling deprecated or removed roles"
Item 5: [RISK] -- disproportionate to current risk profile; revisit if profile changes
Item 6: [WORK_ITEM] -- tooling for adding/editing roles.yaml
```

- Item 4 (ground truth RISK, deprecated roles): groq said WORK_ITEM -- same wrong answer local
  gave in its majority vote. The one case where the stronger model did not fix a known miss.
- Items 5, 6: correct, matching local's own majority-correct pattern here.

## payments-webhook-handler

Groq classification (full text):

> Item 1: [BLOCKING] – No rate‑limiting or strong authentication allows replay/forgery and DoS;
> a critical security defect that must be fixed before deployment.
>
> Item 2: [BLOCKING] – Duplicate webhook deliveries are guaranteed by the provider; without
> deduplication the system will double‑process payments, a correctness error that must be
> addressed now.
>
> Item 3: [RISK] – If traffic grows to ≈500 req/min (order‑of‑magnitude above the 50 req/min
> estimate), the handler could become a bottleneck; revisit scaling when that traffic threshold
> is reached.
>
> Item 4: [WORK_ITEM] – Add a rollback procedure for the backfill migration script (e.g.,
> transactional batch or compensating script).
>
> Item 5: [WORK_ITEM] – Produce an on‑call runbook describing how to manually replay a missed
> webhook after automated retries are exhausted.

- **Item 4 (ground truth BLOCKING, migration rollback plan): groq said WORK_ITEM.** The local
  model got this right, consistently, 3/3 reps, in round 2. This is a genuine false-defer the
  stronger model introduced that the weaker one never made on this item.

## internal-analytics-dashboard

Groq classification: `[RISK, RISK, BLOCKING, RISK, WORK_ITEM]` — **5/5 correct**, including both
of round 1/3's confirmed phrasing-bug items (rate limiting, encryption), which the local model
got wrong in every single trial across two separate rounds (6 trials total: 3 in round 1's
original test, 3 in round 3's isolation test), always with the same reasoning ("this is a plain
correctness defect"). The stronger model classified both correctly, cold, first try, no prompt
change.

## pilot-program-customer-portal

Groq classification:

> Item 1 – [BLOCKING] – Logging full PII at INFO level is a clear security defect that must be
> fixed before any real customer data is stored or displayed.
>
> Item 2 – [NON-BLOCKING] – Lack of i18n/localisation is a minor usability limitation for the
> pilot and can be deferred.
>
> Item 3 – [WORK_ITEM] – Define and integrate a customer‑support lookup tool (e.g., "add
> support‑tool integration") as a future engineering task.

- Item 1: correct, matching local -- confirms the "already-scheduled future change raises the
  bar now" reasoning holds with a stronger model too.
- Item 2 (pre-registered ground truth RISK, flagged as debatable when the scenario was designed):
  groq said `NON_BLOCKING` -- a third distinct answer, different from both the registered ground
  truth and local's consistent `WORK_ITEM`. Read on its own terms ("minor... can be deferred"),
  it's a reasonable call, and reinforces that this item's ground truth was genuinely underspecified
  rather than there being one clearly right answer three different runs failed to reach.
- **Item 3 (ground truth WORK_ITEM, the round-3 "risk-profile over-application" item): groq got
  it right.** The local model classified this `BLOCKING` in every trial, in both round 2's batch
  and round 3's isolation test (confirming the miscalibration wasn't caused by batching). The
  stronger model correctly separated "this needs to exist by launch" from "this blocks the
  current architecture decision."
