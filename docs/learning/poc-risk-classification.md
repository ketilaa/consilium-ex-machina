# PoC Learning: Can a Classifier Add a RISK Category Without Rubber-Stamping Real Blockers?

Parent context: a real, live decision this platform actually produced (`d-22ffab13`, "make the
agent role registry configurable") raised two concerns — deprecated-role handling, `roles.yaml`
tamper-detection — that a human reviewer judged real but disproportionate to the work item's
current risk profile, not blockers. Today's classifier (`decision-engine`'s `Verdict`) has no
vocabulary for that: `BLOCKING`, `NON_BLOCKING`, or `QUESTION`. This PoC tests adding a fourth
option, `RISK`, and asks the one question that matters given this project's own history with
"be proportionate" prompts: does it get used to genuinely defer disproportionate concerns, or
does it become an escape hatch that also waves away real blockers — the same overshoot failure
[poc-raci-veto.md](poc-raci-veto.md) found when Concur's sufficiency-criterion prompt was tested.

## Objective

1. Does a classifier given a `RISK` option, told the work's current risk profile, and given
   explicit guardrails (real not merely inconvenient; never for a plain correctness defect,
   regardless of risk profile; must name a trigger condition) actually sort genuinely
   disproportionate concerns into `RISK` (recall)?
2. Does it also, incorrectly, sweep concerns that must stay `BLOCKING` regardless of risk
   profile into `RISK` (the overshoot/false-defer rate — the more important number, since a
   classifier that never uses `RISK` is merely useless, one that overshoots is actively
   dangerous)?
3. Specifically: can it tell a plain correctness defect apart from a proportionality trade-off
   when the two are phrased in a similar register, under a risk profile that makes deferral
   tempting?

## Method

**Scenarios** (`scenarios.py`), each item carrying a pre-registered ground truth fixed before any
run, no propose/contest/revise loop — only the classify step is under test:

- `role-registry-configurability` — REAL data: the exact five items from `d-22ffab13`, ground
  truth set by the reasoning actually worked through with a human in this project's own
  dogfooding (3 genuinely necessary regardless of context, 2 judged disproportionate).
- `payments-webhook-handler` — constructed, deliberately HIGH risk profile (production payments,
  PCI-DSS scope, public-facing). A stress test in the opposite direction: does a demanding
  profile correctly keep the classifier strict? 3 of 4 items are real, current production risks
  that must stay `BLOCKING` regardless of profile; 1 (scaling beyond an explicit current traffic
  estimate) is legitimately deferrable even here, because the harm is conditional on a specific,
  nameable future change.
- `internal-analytics-dashboard` — constructed, deliberately LOW risk profile (5 internal users,
  already-public anonymized data). Contains the sharpest test in this PoC: a plain correctness
  bug (an aggregation query undercounting monthly totals due to a timestamp mismatch), phrased in
  the same "X could be a problem" register as the legitimately-deferrable items around it. `RISK`
  must never apply to it, regardless of how low the profile reads — a defect is a defect, not a
  proportionality judgment.

**Mechanisms** (`lifecycle.py`), same fixed item set for both, 3 reps each:

- **A — baseline** (`classifier_system_3way`, unmodified) — establishes what a genuinely
  disproportionate item gets classified as today, with no `RISK` option to sort it into.
- **B — 4-way with RISK** (`classifier_system_4way_with_risk`) — adds `[RISK]`, states the work's
  risk profile in the prompt, and carries three explicit guardrails: real not merely
  inconvenient; never for a plain correctness defect; must name a trigger condition.

Scored on `risk_recall` (of true-`RISK` items, fraction classified `RISK`) and `false_defer_rate`
(of true-`BLOCKING` items, fraction incorrectly classified `RISK` — the overshoot metric).

**Model.** Same model as every PoC in this series (`bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF`). Full transcripts under `proof-of-concept/risk-classification/runs/<slug>.md`.

## Results

| Scenario | Risk profile | risk_recall | false_defer_rate | Per-item consistency (3x) |
|---|---|---|---|---|
| role-registry-configurability (real) | low/exploratory | **1.0** | **0.0** | 5/5 items, 3/3 identical |
| payments-webhook-handler | high/production | **1.0** | **0.0** | 4/4 items, 3/3 identical |
| internal-analytics-dashboard | low | **0.33** | **0.0** | 4/4 items, 3/3 identical |

**`false_defer_rate` is 0.0 across all three scenarios — 9 of 9 relevant trials, perfectly
consistent.** No true-`BLOCKING` item was ever swept into `RISK`, including the correctness-bug
trap, which stayed `BLOCKING` in all 3 reps with the stated reason *"this is a plain correctness
defect in data accuracy."* This is the critical safety property this PoC exists to check, and it
held cleanly — a sharp contrast with Concur's sufficiency-criterion prompt, which overshot into
approving 8 of 9 genuinely thin decisions under a similarly-worded "be proportionate" instruction.

`internal-analytics-dashboard`'s recall shortfall (1 of 3 true-`RISK` items correctly deferred) is
not noise — it's a precise, characterizable pattern (Finding 1).

## Findings

**1. Recall tracks how a concern is phrased, not just its substance.** The two `RISK` items that
`internal-analytics-dashboard` failed to defer — missing login rate-limiting, unencrypted
data-in-transit — were both classified `BLOCKING`, in all 3 reps, with the identical stated
reason: *"this is a plain correctness defect in security."* That's the model over-extending this
PoC's own guardrail (never `RISK` for a correctness defect) to security absences generally.
Comparing every item across all three scenarios that correctly *did* get deferred to `RISK`, every
one is phrased as a conditional attack or failure scenario — *"if adoption exceeds [estimate] by
an order of magnitude"*, *"if the dataset grows much larger"*, *"an attacker who gains write
access could potentially modify role definitions"*. The two that failed are phrased as flat,
declarative absence statements — *"has no rate limiting"*, *"is not encrypted"* — with no
conditional framing at all, even though the underlying substance (a security-hardening trade-off,
proportional to a stated low-risk profile) is the same shape as the successful cases. The
classifier isn't failing to weigh risk profile against severity; it's pattern-matching "stated
flatly, like a bug report" onto "is a bug," regardless of what the sentence is actually about.

**2. The overshoot direction never happened, in either direction of risk-profile pressure.**
`payments-webhook-handler`'s high-pressure profile didn't make the classifier over-defer (it
correctly kept 3 of 4 items `BLOCKING` despite an explicit, demanding risk profile that might
plausibly have pushed a less careful mechanism toward "everything here is high-stakes, block
everything" just as easily as toward leniency) — and `internal-analytics-dashboard`'s low-pressure
profile didn't make it sweep the correctness bug into `RISK` either. Both directions of possible
failure were tested and neither occurred.

**3. The real `d-22ffab13` items classified exactly as the human review already concluded.** All
5 items from the actual dogfooded decision landed on the same verdict a human reasoned through in
this project's own conversation, 3/3 reps, no variance — the first scenario in this PoC series
where the mechanism under test reproduced a real, already-settled human judgment call precisely,
rather than being compared only against a scenario built to test it.

## Verdict

The core safety property holds cleanly across every trial: this classifier never used `RISK` to
wave away something that should stay `BLOCKING`. That's the property that actually matters for
whether this is safe to build — a mechanism with imperfect recall under-delivers, but a mechanism
with any real false-defer rate would be actively dangerous, quietly converting real gaps into
"acceptable risk." Given the false-defer rate is 0.0 across three scenarios deliberately
engineered to test it from both directions (high-pressure profile tempting over-deferral of real
blockers, low-pressure profile tempting under-recognition of a correctness bug as a defect), that's
real, not incidental, evidence.

The recall gap is real too, and it's specific enough to have an obvious next fix to test rather
than a vague "needs more data": tell the classifier explicitly that a flatly-phrased absence
statement can still be `RISK` if the *harm it would enable* is disproportionate to the stated
risk profile — don't let sentence structure alone push a security absence toward `BLOCKING`. That's
a testable, scoped follow-up, not a reason to distrust the mechanism's core discriminating power.

This is real, if still single-round, evidence that a `RISK` classification is workable — closer to
buildable than any variant of Concur got across five rounds of testing. Consistent with this
project's own discipline, one clean round isn't validation on its own; the recall-phrasing fix
above is the natural next test before this becomes domain code in `decision-engine`.

## Scope limitations of this PoC

- Three scenarios, 3 reps each, single round — the same "one clean run isn't proof" caveat every
  PoC in this series states about itself, especially given how much runs 2 through 5 of
  `poc-raci-veto.md` revised what run 1 alone looked like.
- The phrasing-sensitivity finding (Finding 1) is drawn from 2 failing items out of 13 total across
  all scenarios — real and precisely characterized, but a small base rate to generalize from.
- This tests the classify step in isolation, with fixed, pre-written items — not the live
  propose/contest pipeline that would actually generate item text in production, where phrasing is
  whatever a live challenger role happens to produce, not chosen by this PoC's own author.
- The risk profile text was authored by this PoC, in a form clearly and explicitly stated in the
  prompt — untested whether a less explicit, real Work Item's risk profile (however that ends up
  being captured) would carry enough signal for the same discrimination.
- No test yet of what happens to an item deferred to `RISK` when its stated trigger condition
  later becomes true — whether anything would actually notice and re-surface it is a distinct,
  unaddressed question from whether the initial classification is trustworthy.
- Single model, single grading pass per item (no independent second reviewer of the transcripts
  beyond the two illustrative comparisons quoted in Finding 1).

## Candidate write-ups

- **"The one guardrail that actually held."** Every other proportionality-instruction tested in
  this project's PoC series (Concur's sufficiency criterion) overshot into rubber-stamping real
  gaps. This one, tested from both directions on purpose, didn't rubber-stamp a single one across
  nine relevant trials — the first time "be proportionate" phrasing has held up under adversarial
  testing here.
- **"It's not ignoring risk profile, it's pattern-matching on sentence shape."** The two missed
  deferrals weren't a failure to weigh severity against context — every item phrased as a
  conditional scenario got sorted correctly; the ones phrased as flat "X is missing" statements
  got treated as bugs regardless of context. A precise, fixable finding, not a vague miss.
- **"The real decision's items classified exactly like the human already decided."** Five items
  from an actual, already-argued-through live decision, unprompted with the human's own
  conclusion, landed on it anyway, 3 for 3 reps — a rare case in this project where a PoC
  reproduces a real judgment call rather than only testing a constructed one.
