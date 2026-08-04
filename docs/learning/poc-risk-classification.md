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

**This document reports two rounds.** Round 1 (below, unchanged) held cleanly on the one property
that matters most — it never used `RISK` to wave away a real blocker — and found one precise,
fixable-looking recall gap. Round 2 tested that fix, added a fifth classification (`WORK_ITEM`),
and added real adversarial pressure the way Concur's testing eventually did. The results are
substantially more mixed than round 1's clean run: the proposed recall fix did not work at all,
a new overshoot channel opened up through the new category, and `RISK` vs. `WORK_ITEM` turned out
to be a genuinely unreliable discrimination on realistic, topically-clustered items — while one
new fix (an already-scheduled future risk-profile change correctly raising the bar now) worked
cleanly on its intended target, then over-generalized past it. See §Round 2 below.

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

## Verdict (round 1 only — revised below)

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

*(Round 2 tested this fix directly — see below. It did not work, which is itself the kind of
finding round 1's own framing here warned against getting ahead of: "one clean round isn't
validation on its own" turned out to be exactly the right level of caution.)*

## Round 2: adding WORK_ITEM, testing the recall fix, and real adversarial pressure

**Method.** Extends round 1's scenarios (`scenarios_round2.py`) rather than replacing them — the
original items are reused verbatim so results are directly comparable:

- One new `WORK_ITEM` ground-truth item added to each of round 1's three scenarios — real,
  *unconditional* follow-up work (tooling for editing `roles.yaml`; an on-call runbook for
  replaying a missed webhook; a CI setup for the dashboard's own codebase) that round 1's 4-way
  classifier had no vocabulary to sort correctly.
- The exact two items that failed round 1's recall test (`internal-analytics-dashboard`'s
  rate-limiting and encryption-in-transit items) carried over unchanged, to test round 1's
  proposed fix directly rather than on new items that might not exercise the same bug.
- A new scenario, `pilot-program-customer-portal`: a work item currently low-stakes (4 internal
  test accounts) but with an *already-committed, dated* future risk-profile change (10 external
  pilot customers onboarding in 6 weeks, at which point real names/emails/billing history start
  flowing through it). Tests whether a concern tied to that committed change correctly gets
  treated as urgent now, rather than waved off with `RISK`'s "revisit later" framing.
- A `consistency-probe` scenario: one deliberately ambiguous item (a UI feature request that could
  reasonably be `RISK` — conditional on a decision not yet made — or `WORK_ITEM` — real work
  regardless), no ground truth, run 8 independent times to check whether `RISK` vs. `WORK_ITEM`
  judgment is stable on a genuinely hard case.

The classifier itself (`classifier_system_5way_with_work_item`) adds `[WORK_ITEM]`, an explicit
instruction that phrasing (flat statement vs. conditional scenario) is not the test for `RISK`,
and an instruction that an already-scheduled future risk-profile change should be treated as an
approaching trigger, not a distant hypothetical.

**Results:**

| Scenario | risk_recall | work_item_recall | false_defer_rate | false_work_item_rate | Per-item consistency (3x) |
|---|---|---|---|---|---|
| role-registry-configurability (real) | 0.5 | 0.67 | 0.0 | **0.22** | **5/6 items inconsistent** |
| payments-webhook-handler | 1.0 | 1.0 | 0.0 | 0.0 | 5/5 identical |
| internal-analytics-dashboard | 0.33 (unchanged) | 1.0 | 0.0 | 0.0 | 5/5 identical |
| pilot-program-customer-portal | 0.0 | 0.0 | 0.0 | 0.0 | 3/3 identical |

Consistency probe: **8/8 identical — `BLOCKING`, every time.** Not the RISK/WORK_ITEM split it was
built to measure; see Finding 6.

## Findings (round 2)

**4. The proposed recall fix did not work — the exact carryover items are unchanged.**
`internal-analytics-dashboard`'s rate-limiting and encryption items, told explicitly that
"the wording is not the test," were still classified `BLOCKING` in all 3 reps — identical to
round 1. Stating the guardrail did not change the behavior it was aimed at, the same lesson
Concur's sufficiency criterion already taught: an instruction that sounds like it should fix a
specific failure mode is a hypothesis, not a fix, until it's actually tested against the case it's
meant to fix.

**5. `RISK` vs. `WORK_ITEM` is not a reliable discrimination on realistic, topically-clustered
items — and it opened a new overshoot channel.** `role-registry-configurability` (the real
scenario, all items about the same `roles.yaml` artifact) showed 5 of its 6 items classified
inconsistently across just 3 reps, and 2 of 9 relevant trials incorrectly waved a true-`BLOCKING`
item into `WORK_ITEM` — a new false-defer channel round 1 never had, since `WORK_ITEM` didn't
exist yet. Reading the actual reasoning shows why: asked to classify the genuinely conditional
deprecated-role item (ground truth `RISK`) and the genuinely unconditional tooling item (ground
truth `WORK_ITEM`) in the same pass, the model gave both near-identical boilerplate — *"this is a
legitimate concern that should be addressed, but it does not block the current decision"* — with
neither invoking the actual distinguishing test (a stated trigger condition vs. a description of
definite work) that would tell them apart. `WORK_ITEM` is functioning as a generic "defer,
not urgent" bucket rather than being reserved for the specific, unconditional case it was defined
for.

**6. The consistency probe was rock-solid, for a reason that reveals a different bug than the one
it was built to find.** All 8 reps landed on `BLOCKING`, with the stated reason: *"the proposal is
missing critical implementation details that are necessary to proceed with the decision."* That
treats *any* unspecified implementation detail as blocking, regardless of the underlying feature's
own priority (dark mode, an explicitly low-stakes UI request) — a different, more general pattern
than round 1's "flat absence → correctness defect" bug. The same phrasing shape
(*"the proposal does not specify what X will be used"*) plausibly explains Finding 7 below too.

**7. The "already-scheduled future change" fix worked exactly as intended on its target item — and
then over-generalized past it.** The imminent-pilot scenario's PII-logging item correctly stayed
`BLOCKING` in all 3 reps, explicitly reasoning that the external launch is *"already committed,"*
not hypothetical — a clean, validated win for that specific fix. But the same reasoning pulled a
second item (support tooling to look up a pilot customer's account) into `BLOCKING` too, on the
identical basis (*"they will need this by launch"*) — reasoning that actually describes real,
scheduled, unconditional work, i.e. the model's own stated logic supports `WORK_ITEM`, not
`BLOCKING`, yet it concluded `BLOCKING` anyway. An instruction to weigh one factor more heavily
had a knock-on effect on an adjacent judgment it wasn't aimed at, the same shape of spillover found
in round 1 (Finding 1) and in Concur's sufficiency criterion.

## Verdict (revised)

Round 1's headline — *"real, if still single-round, evidence that RISK classification is
workable"* — does not survive round 2 intact. The core safety property that mattered most in
round 1 (never wave a real blocker into the deferral categories) mostly held: `false_defer_rate`
stayed 0.0 in all four round-2 scenarios. But `WORK_ITEM` opened a second overshoot channel round 1
never tested for, and it fired in the one scenario built from real data. The proposed recall fix
was a plausible-sounding hypothesis that turned out to be simply wrong when actually tested. And
the discrimination this round was specifically built to add — `RISK` vs. `WORK_ITEM` — is not
reliable on realistic, clustered items, even though the underlying reasoning in each individual
case often sounds sensible in isolation.

The one clean, validated result this round — the already-scheduled-future-change fix working on
its target — came bundled with a spillover effect onto an adjacent item, which is the same lesson
Concur's own testing kept relearning: a fix that works on the case it was built for is not the
same claim as a fix that stays scoped to only that case.

Net: this PoC has now had one clean round and one round that complicates it substantially — the
same shape of trajectory `poc-raci-veto.md` went through with Concur, just compressed into two
rounds instead of five. `RISK` alone (round 1's original, two-way discrimination against
`BLOCKING`) still looks solid. Adding a fifth category does not look solid yet, and should not be
treated as a small increment on top of an already-validated mechanism.

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

**Round 2 additions:**

- Findings 5–7 are drawn from 4 scenarios, 3 reps each — the same small-base-rate caveat as
  round 1, now compounded across two rounds of small samples rather than resolved by them.
- The consistency probe (Finding 6) tested stability on one ambiguous item, not correctness — it
  incidentally surfaced a real, differently-shaped bug (implementation-detail-absence read as
  blocking regardless of the feature's priority) rather than the RISK/WORK_ITEM instability it was
  built to measure. Whether that instability exists at all is now untested by this probe and would
  need a differently-worded ambiguous item to actually check.
- Finding 7's spillover (the pilot scenario's support-tooling item) rests on one scenario, one
  item — real and directly quoted, but not yet replicated on a second, differently-worded case.
- No round-2 scenario tested `WORK_ITEM` recall under a demanding, high-pressure risk profile the
  way `payments-webhook-handler` tested `RISK` in round 1 — the one new scenario with a shifting
  profile (`pilot-program-customer-portal`) had 0.0 recall for both `RISK` and `WORK_ITEM`, which
  is itself informative but doesn't establish whether `WORK_ITEM` recall is generally weak or
  specific to that scenario's spillover effect.

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
- **"We told it the wording wasn't the test, and it kept failing the exact same way."** Round 2's
  proposed fix for round 1's precise recall bug was specific, well-targeted, and did nothing —
  the identical two items, told explicitly to judge harm over sentence shape, gave the identical
  wrong answer. A clean instance of the gap between "this instruction should fix it" and "this
  instruction fixed it."
- **"Two items, one boilerplate answer, two different right answers."** Asked to sort a
  conditional concern from an unconditional one in the same breath, the model gave both the same
  sentence — *"should be addressed, but doesn't block"* — and only sometimes bothered to check
  which one actually applied. Adding a fifth bucket didn't add a fifth kind of reasoning to go
  with it.
- **"It got the hard case right and took a bystander down with it."** Told that an already-
  scheduled future change should raise the bar now, it correctly kept the one item that change
  was aimed at blocking — then used the identical logic to block a second, unrelated item whose
  own reasoning actually argued for scheduling it, not blocking it. The fix worked exactly once,
  precisely on target, and then kept going.
