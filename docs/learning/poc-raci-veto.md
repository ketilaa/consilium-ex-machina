# PoC Learning: Does RACI Participation Scoping Lose Signal, and Does a Cold Concur Gate Add Value?

Parent context: [docs/design/decision-making.md](../design/decision-making.md)'s "Authority: ownership
vs. veto" section, which frames the category-owner table as RACI's "Accountable" and describes veto as
"cross-cutting, blocking authority" deliberately modeled separately from ownership — real design surface
CLAUDE.md explicitly defers pending a PoC, the same way question-gating was validated before being
built. This PoC tests two distinct claims raised while designing that mechanism, not the ownership table
itself (unchanged, untested here).

**This document reports three runs.** The first run (2 scenarios) produced a confident, cautionary
headline: participation restriction looked risky, and Concur looked like it added real value. The
second run (5 scenarios, including independent re-samples of the first run's own two) does not confirm
that headline — it complicates it in a way that matters more than additional data points alone,
surfacing a design flaw in how Concur was tested and showing the redundancy judge's verdicts are not
stable across independent samples of identical scenario text (Findings 1–2). The third run is a
positive control built directly from the second run's own transcripts — hand-authored decisions
engineered to concretely close every real, quoted objection Concur had raised — and it turns Finding 1
from an open question into a settled, structural one (Finding 1, revised). All three runs' raw results
are kept below rather than silently replaced, because the discrepancy between them is itself the most
important finding this PoC produced.

## Objective

1. **Participation.** A RACI table says a decision's contest round should include only Responsible,
   Accountable, and Consulted — Informed gets no voice, on the premise that Informed has nothing further
   to add. Is that premise actually safe, or does excluding Informed lose a real, non-redundant concern?
2. **Concur.** A role that held no pen during propose/contest/classify/revise, shown only the final
   decision, cold, and asked a single binary question strictly on its own named grounds (matching
   `decision-making.md`'s veto example — a Security Reviewer blocking a caching decision it doesn't own)
   — does it ever block something the ordinary classify/recheck mechanism already called a clean
   converge? And is that verdict repeatable (signal) or scattershot (noise)?

## Method

**Scenarios** (`scenarios.py`), each assigning all five existing roles to a distinct RACI letter plus a
Concur holder deliberately *not* already in the Responsible/Consulted set. First run:

- `audit-log-retention` — Accountable: Release Manager. Responsible: Backend Developer. Consulted:
  Architect. **Informed: Performance Reviewer** — pre-registered expectation: `redundant` (retention
  policy has little to do with runtime performance). Concur: Security Reviewer, on compliance/audit
  grounds.
- `llm-inference-hosting` — Accountable: Architect. Responsible: Backend Developer. Consulted:
  Performance Reviewer. **Informed: Security Reviewer** — pre-registered expectation: `novel` (self-hosted
  vs. third-party API has real data-handling implications). Concur: Release Manager, on
  deployability/rollback-safety grounds.

Second run added three scenarios, written with concrete, closeable engineering concerns (rollback
plans, dry-run modes, review gates) rather than open-ended architectural or compliance framing, to give
raci a real chance to converge cleanly — the first run's `audit-log-retention` scenario never reached
that precondition, so Concur's sharp claim only got one decisive trial:

- `schema-migration-gate` — Accountable: Release Manager. Responsible: Backend Developer. Consulted:
  Architect. **Informed: Performance Reviewer** — expectation: `redundant` (a deliberate sanity check on
  the judge itself — Performance Reviewer's natural angle on migration locking/downtime substantially
  overlaps with Backend Developer's operational-burden framing of the same mechanism).
- `dependency-upgrade-policy` — Accountable: Architect. Responsible: Backend Developer. Consulted: Release
  Manager. **Informed: Security Reviewer** — expectation: `novel` (supply-chain/vulnerability angle,
  distinct from delivery-speed/rollback-safety framing). Concur: Performance Reviewer.
- `api-rate-limiting-policy` — Accountable: Architect. Responsible: Performance Reviewer. Consulted:
  Backend Developer. **Informed: Release Manager** — expectation: `novel` (rollback/failure-mode concern
  distinct from latency/implementation-complexity framing). Concur: Security Reviewer.

**Mechanism** (`lifecycle.py`), unchanged between runs: one proposal per scenario, then one round of live
contest from Responsible + Consulted + Informed together, shared identically between conditions so the
only variable is which reactions get fed into the lifecycle:

- **Mechanism A — baseline.** The already-validated propose/3-way-classify/revise/targeted-per-raiser-
  recheck lifecycle, run over all three of R+C+I as challengers — today's world, no RACI concept.
- **Mechanism B — raci.** The identical lifecycle, run over R+C only. Informed's reaction is withheld
  entirely.

Then, regardless of raci's outcome: a neutral judge (`redundancy_judge_system`) compares Informed's
withheld reaction against what R+C actually raised, answering `NEW` or `REDUNDANT`, checked against the
scenario's pre-registered `expected_informed_signal`. Separately, the Concur-holder is shown *only*
raci's final decision text — not the transcript, not the classification — and asked to `CONCUR` or `DO
NOT CONCUR` strictly on its own named grounds, repeated 3 times to check consistency.

Third run (`positive_control_scenarios.py`, `run_positive_control.py`): three fixtures, one per
Concur-holder/grounds combination from run 2 (`audit-log-retention`'s Security Reviewer, `llm-inference-
hosting`'s Release Manager, `api-rate-limiting-policy`'s Security Reviewer). Each `final_decision_fixture`
is **hand-authored, not owner-generated** — deliberately bypassing `_propose`/`_contest`/`run_mechanism`
entirely, so the noisy propose/revise pipeline can't be blamed for an ambiguous result — and built
directly from that Concur-holder's own quoted `DO NOT CONCUR` justifications in run 2's transcripts,
explicitly and concretely closing every one of them (named access-control roles, AES-256/TLS 1.3,
WORM storage, a rehearsed failover drill with numbers, per-role rate limits with anomaly detection,
fail-closed behavior, audit logging of every adjustment). The Concur check (`run_concur_repeats`) is
run unmodified, 3 times per fixture, against this fixed input.

**Model.** Single model throughout (`bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF`),
confirmed to be the identical, continuously-running server process across all three runs (no restart, no
config change between them) — the discrepancies below are genuine sampling variance and judge behavior,
not a model change. Full transcripts under `proof-of-concept/raci-veto/runs/<slug>.md`.

## Results

| Scenario | Run | Baseline | Raci | Terminal state | Predicted | Judged | Prediction matched | Concur (3x, cold) |
|---|---|---|---|---|---|---|---|---|
| audit-log-retention | 1 | escalated | escalated | SAME | redundant | **NEW** | no | DO NOT CONCUR ×3 (raci not clean — not decisive) |
| llm-inference-hosting | 1 | escalated | **converged** | **DIFFERS** | novel | **NEW** | yes | DO NOT CONCUR ×3 (**diverged from clean**) |
| audit-log-retention | 2 | converged | converged | SAME | redundant | REDUNDANT | yes | DO NOT CONCUR ×3 (**diverged from clean**) |
| llm-inference-hosting | 2 | escalated | escalated | SAME | novel | REDUNDANT | no | DO NOT CONCUR ×3 (raci not clean — not decisive) |
| schema-migration-gate | 2 | converged | converged | SAME | redundant | REDUNDANT | yes | DO NOT CONCUR ×3 (**diverged from clean**) |
| dependency-upgrade-policy | 2 | converged | converged | SAME | novel | REDUNDANT | no | DO NOT CONCUR ×3 (**diverged from clean**) |
| api-rate-limiting-policy | 2 | converged | converged | SAME | novel | REDUNDANT | no | DO NOT CONCUR ×3 (**diverged from clean**) |

Aggregate (runs 1–2): **terminal state differed in 1 of 7 trials.** **Redundancy judge said `NEW` in 2 of 7, `REDUNDANT` in 5 of 7.** **Pre-registered predictions matched the judge in 3 of 7 — worse than chance.** **Concur said `DO NOT CONCUR` in all 21 individual calls (7 scenarios × 3 reruns) — it has never once said `CONCUR`.**

**Run 3 — positive control, Concur only:**

| Fixture | Concur role | Built to close | Verdicts (3x) | Approved at least once? |
|---|---|---|---|---|
| audit-log-retention-positive-control | Security Reviewer | access control, encryption, compliance review, monitoring | DO NOT CONCUR ×3 | No |
| llm-inference-hosting-positive-control | Release Manager | tested failover, stateless design, on-call paging | DO NOT CONCUR ×3 | No |
| api-rate-limiting-policy-positive-control | Security Reviewer | per-role limits, fail-closed, audit logging, blast-radius containment | DO NOT CONCUR ×3 | No |

**All 9 positive-control calls also said `DO NOT CONCUR` — 30 of 30 across the entire PoC.** But the objections are not repeats: none of the 9 re-raises anything the fixture actually closed (access control, encryption, the tested failover drill, fail-closed behavior, and per-role limits are never re-flagged). Each instead finds a genuinely different, deeper follow-on gap — see Finding 1, revised.

## Findings

**1. Concur has never once returned `CONCUR`, across all three runs — and the positive control shows why:
not indifference to content, but no notion of "sufficient."** Runs 1–2 established that Concur said `DO
NOT CONCUR` in all 21 calls, which merely meant its divergence rate couldn't be told apart from a
reflexively negative gate. Run 3 tested that directly: three fixtures, hand-authored to concretely close
every real, quoted objection Concur itself had raised (named access-control roles, AES-256/TLS 1.3,
WORM storage, a rehearsed failover drill with specific numbers, per-role rate limits with anomaly
detection, fail-closed behavior, audit logging). All 9 calls still said `DO NOT CONCUR` — but critically,
**none of the 9 re-raised anything the fixture had actually closed.** Each found a different, deeper
follow-on gap instead: `audit-log-retention`'s fixture specified named-role access control and quarterly
review, and Concur moved to *"there should be a mechanism... to periodically verify the integrity of the
archived data,"* then *"the same role (Security Reviewer) is responsible for reviewing the access logs
and has access to the audit log... separation of duties."* `llm-inference-hosting`'s fixture specified a
drilled, tested failover with numbers, and Concur moved to *"lacks a clear strategy for rolling back to
the third-party hosted LLM API after a failover"* — the reverse direction, never addressed because the
fixture (like the real scenario before it) only specified failing over, not failing back.
`api-rate-limiting-policy`'s fixture specified fail-closed behavior and per-role limits, and Concur moved
to *"how the gateway will handle situations where the rate-limiting configuration itself is
compromised"* — a meta-level attack on the control itself. This is real, content-sensitive reasoning, not
a canned response — each objection is different, specific, and non-trivial. But it means the mechanism
**cannot function as a pass/fail gate as currently designed**: a security-minded critic can always ask
"but what about the security of that control," recursively, and the prompt gives Concur no criterion for
when enough is enough — only an instruction to find fault on its named grounds. No fixture, however
thorough, could satisfy that mandate, because thoroughness just moves the objection up a level rather
than resolving it. The first run's framing of Concur's divergence as "real evidence it isn't redundant"
undersold this: the actual finding is sharper and worse for the mechanism's viability as built — this
isn't a data problem more replicates would fix, it's a prompt design that has no exit condition.

**2. The redundancy judge's own verdicts are not stable across independent samples of identical
scenario text.** Both scenarios repeated from the first run flipped: `audit-log-retention` went `NEW →
REDUNDANT`, `llm-inference-hosting` went `NEW → REDUNDANT` — same code, same scenario text, same model
process, a fresh live sample each time. Pre-registered predictions (domain reasoning about which
exclusions should plausibly be risky vs. safe, made before any run) matched the actual verdict in only 3
of 7 trials, worse than a coin flip. One mismatch is directly checkable against the transcript, not just
statistically suspicious: in `dependency-upgrade-policy`, Security Reviewer's withheld concern was
specifically about **supply-chain attacks** — malicious code injected via an automatic dependency
upgrade, mitigated by security scanning, source whitelisting, and canary rollout — a materially different
risk from Backend Developer's and Release Manager's concern about ordinary **regressions** (mitigated by
testing, staging, rollback). The judge called it `REDUNDANT`, justified by "already covered by concerns
about regressions, testing, and rollback strategies" — conflating a shared surface word (rollback) with
two substantively different risks. That's a concrete instance of the judge being wrong on inspection,
not just inconsistent in aggregate.

**3. The participation-safety signal, once diluted across the full dataset, is much weaker than the
first run suggested.** Only 1 of 7 trials showed excluding Informed changing the terminal state (the
original `llm-inference-hosting` trial); all 5 of the second run's trials showed no difference. Combined
with Finding 2, this PoC's overall evidence that "participation restriction is risky" no longer looks
like a confident finding — it looks like one real instance sitting inside a measurement that can't
currently be trusted to detect the difference reliably either way.

**4. Inside the first run's `llm-inference-hosting` baseline, the per-raiser recheck overrode the
classifier's own initial call** — round-1 classification tagged Security Reviewer's items
`[NON-BLOCKING]`, but the targeted recheck still returned `NOT RESOLVED` against the revision, and this
contributed to escalation despite the initial non-blocking tag. Not a new mechanism, but a property of
the inherited lifecycle worth naming: the per-raiser recheck functions as a real check on the
classifier's own judgment, not a rubber stamp of it. This finding is unaffected by the instability
found above — it concerns the already-validated classify/recheck mechanism, not the new participation or
Concur mechanisms.

## Verdict

On participation: still open, and more cautious than the first run suggested. One real instance of harm
exists (the first run's `llm-inference-hosting` trial), but the redundancy judge that would tell us
whether this generalizes has been shown, on the exact same scenario content, to give the opposite answer
on independent samples — so this PoC cannot currently say whether participation restriction is risky in
general or whether that one trial was itself noise. That still needs the repeated-same-scenario design
described below, not more new scenarios.

On Concur: **settled, and negative, for the mechanism as currently designed.** This is no longer an
open question about insufficient replicates — the positive control shows Concur cannot be satisfied by
content, however thorough, because its prompt has no stopping condition. A cold reviewer instructed to
find fault on narrow security/ops grounds, with no criterion for "this is enough," will always find the
next meta-level gap. That makes it structurally unable to function as an automatic pass/fail gate: it
would block every decision, including ones a reasonable human would approve without hesitation. This
doesn't mean the underlying instinct (a domain specialist's cold sign-off catches things a busy
in-the-loop reviewer misses) is wrong — Finding 1 shows the objections it raises are real and specific,
not noise — it means **an unbounded critical gate can't be the mechanism**. A workable version would need
either an explicit sufficiency criterion in the prompt (e.g. "approve once the named grounds are
concretely addressed; do not require unbounded depth" — untested here), or reframing Concur's output as
advisory input a human weighs, not a hard block a decision must clear.

If this mechanism moves forward, the immediate next step is not "run more scenarios like these" — it's
(a) testing whether an explicit sufficiency criterion changes Concur's behavior (a fourth run, not yet
done), and (b) for participation, repeated trials of the *same* scenario (not just more scenarios) to
establish whether the redundancy judge's verdict is a property of the content or a property of the
sample. Building the current, unbounded version of Concur into the platform would mean building a gate
this PoC has now shown, directly, cannot be passed.

## Scope limitations of this PoC

- **The positive control tests one specific Concur prompt, not the concept of a cold gate in general.**
  Finding 1's "no stopping condition" conclusion is about the prompt actually used
  (`concur_system` in `roles.py`), which never gives the reviewer a sufficiency criterion. A differently
  worded prompt (e.g. explicitly bounding what "enough" looks like) might behave differently — untested
  here, and named as the concrete next step in the Verdict.
- **The redundancy judge's verdict is not shown stable under resampling** — Finding 2's two flipped
  re-runs are the entire evidence base for this claim; a larger repeated-trial design (same scenario, many
  independent samples) would be needed to know whether 2/7 vs. 5/7 reflects real scenario properties or
  is itself just where this particular sample of 7 happened to land.
- Single model plays every role in both runs; model capability and role-tiering effects on either claim
  remain untested.
- "Did the terminal state differ" is a weak proxy for participation safety on its own (unchanged from the
  first run's Finding 3) — it can read `SAME` even when the excluded role held a real, independently
  judged `NEW` concern, merely because other items already forced the same outcome.
- The redundancy judgment and the Concur verdict are each a single LLM call, ungraded by an independent
  second reviewer — the same manual/single-grader caveat every PoC in this project carries. Finding 2's
  transcript-level check (the supply-chain-vs-regression mischaracterization) is the only place this PoC
  did that grading itself; it was not done systematically across all 7 trials.
- The RACI letter assignment per scenario was authored by this PoC's own code, not derived from any
  external authority table (docs/design/decision-making.md's owner table, or the user's proposed
  12-activity governance matrix) — a different assignment could plausibly change which concerns end up
  Informed and whether the same risk surfaces.

## Candidate write-ups

- **"We ran it again and it disagreed with itself."** The exact same two scenarios, same code, same
  model process, independently sampled a second time, flipped both their redundancy verdicts and one of
  their terminal states. That's a more useful finding than either run's numbers alone — it says don't
  trust a single trial here, in either direction.
- **"We built the perfect answer and it still failed — on purpose, that's the finding."** Three fixtures,
  each engineered from Concur's own real complaints to concretely close every one of them. All nine
  reruns still said no — but to a different, deeper objection each time, never a repeat. That's not a
  broken gate reciting the same line; it's a gate with no notion of "enough," which is arguably a more
  useful thing to know before building it.
- **"The judge called two different risks the same risk because they shared a word."** Supply-chain
  compromise and ordinary regression risk both involve "rollback" — the redundancy judge conflated them.
  A concrete, checkable instance of exactly the kind of error an aggregate `NEW`/`REDUNDANT` count can't
  surface on its own.
