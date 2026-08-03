# PoC Learning: Does RACI Participation Scoping Lose Signal, and Does a Cold Concur Gate Add Value?

Parent context: [docs/design/decision-making.md](../design/decision-making.md)'s "Authority: ownership
vs. veto" section, which frames the category-owner table as RACI's "Accountable" and describes veto as
"cross-cutting, blocking authority" deliberately modeled separately from ownership — real design surface
CLAUDE.md explicitly defers pending a PoC, the same way question-gating was validated before being
built. This PoC tests two distinct claims raised while designing that mechanism, not the ownership table
itself (unchanged, untested here).

**This document reports five runs.** The first run (2 scenarios) produced a confident, cautionary
headline: participation restriction looked risky, and Concur looked like it added real value. The
second run (5 scenarios, including independent re-samples of the first run's own two) does not confirm
that headline — it complicates it in a way that matters more than additional data points alone,
surfacing a design flaw in how Concur was tested and showing the redundancy judge's verdicts are not
stable across independent samples of identical scenario text (Findings 1–2). The third run is a
positive control built directly from the second run's own transcripts — hand-authored decisions
engineered to concretely close every real, quoted objection Concur had raised — and it turns Finding 1
from an open question into a settled, structural one: the prompt has no stopping condition. The fourth
run tests two candidate fixes for that head-to-head against the original prompt, and finds one works
and one backfires (Finding 1b) — but only on the positive case. The fifth run tests the surviving fix's
negative case (does it correctly still reject a bad revision) and reverses the optimism: it doesn't,
reliably (Finding 1c). All five runs' raw results are kept below rather than silently replaced, because
the discrepancy between them is itself the most important finding this PoC produced.

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

Fourth run (`sufficiency_test_scenarios.py`, `run_three_way_concur_test.py`): three scenarios, each now
carrying a **paired** fixture — the same hand-authored `positive_fixture` from run 3, plus a
`negative_fixture` that is a REAL final decision this PoC actually produced (run 2's raci mechanism for
`audit-log-retention` and `api-rate-limiting-policy`; run 1's for `llm-inference-hosting`, recovered via
`git show 8cef25d`) — thin specifically on the Concur-holder's own named grounds, which is why it
originally got rejected. Three variants of Concur are run against both fixtures:

- **A — original** (`concur_system`), re-run fresh in this pass rather than citing run 3's numbers, so
  all three variants are compared under identical, freshly-sampled conditions.
- **B — sufficiency criterion** (`concur_system_with_sufficiency`): one added paragraph naming an
  explicit stopping condition ("do not withhold concurrence merely because a deeper, more paranoid...
  question could still be asked... reserve DO NOT CONCUR for a concrete, specific, actionable gap").
- **C — recheck** (`run_concur_recheck`): structural, not just an instruction, proposed by the user.
  Round 1 (`concur_system_focused_round1`) reviews the `negative_fixture` cold and states a SINGLE
  concrete concern (a narrower framing than A/B's open "find fault"). Round 2 (`concur_recheck_system`)
  is shown ONLY that stated concern plus the `positive_fixture` as "the revision," and judges whether
  THAT SPECIFIC concern is resolved — explicitly forbidden from raising anything new. The same
  "ask the specific raiser about its own item, not a generalist reclassifying from scratch" pattern
  already validated for `issue_react_system`/`question_react_system`, applied to Concur for the first
  time.

A and B are tested against both fixtures (does it ever approve the thorough one; does it still correctly
reject the thin one — approving thin content would be the opposite failure mode, equally disqualifying).
C is inherently a before/after pair, since a recheck is meaningless without something to recheck against.

Fifth run (`round2_negative_scenarios.py`, `run_round2_negative_test.py`): closes the gap run 4 left —
every round-2 case there paired the thin fixture with the *positive* fixture (a revision engineered to
resolve the stated concern). This run tests round 2 in isolation on revisions that should NOT resolve it,
holding round 1's actual, already-collected concern text fixed (quoted verbatim from run 4's transcripts,
repeat 1 per scenario) rather than re-spending calls on round 1, which was already shown reliable. Two
fixtures per scenario:

- `no_attempt_revision` — the negative fixture completely unchanged. The most basic possible check: if
  round 2 approves the exact text it (via round 1) just rejected, it isn't discriminating at all.
- `vague_gesture_revision` — the negative fixture plus one added paragraph of hand-wavy reassurance on
  the concern's exact theme, with no concrete mechanism, number, or named control — deliberately mimicking
  the vague language that fooled variant B in run 4.

Both should get `DO NOT CONCUR` every time if round 2 is genuinely discriminating; 3 reruns each for
consistency, the same discipline as every other Concur check in this PoC.

**Model.** Single model throughout (`bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF`),
confirmed to be the identical, continuously-running server process across all four runs (no restart, no
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

**Run 4 — three variants, paired positive/negative fixtures:**

| Scenario | Variant | Positive fixture approved? | Negative fixture approved? |
|---|---|---|---|
| audit-log-retention | A — original | 1/3 (inconsistent) | 0/3 |
| audit-log-retention | B — sufficiency | 3/3 | **3/3** |
| audit-log-retention | C — recheck (final) | 3/3 | — (recheck design; see below) |
| llm-inference-hosting | A — original | 0/3 | 0/3 |
| llm-inference-hosting | B — sufficiency | 3/3 | **3/3** |
| llm-inference-hosting | C — recheck (final) | 3/3 | — |
| api-rate-limiting-policy | A — original | 0/3 | 0/3 |
| api-rate-limiting-policy | B — sufficiency | 3/3 | **2/3** |
| api-rate-limiting-policy | C — recheck (final) | 3/3 | — |

Variant C has no separate "negative fixture approved" column because it isn't tested the same way: round 1
reviews the negative fixture and is *expected* to object (that's what makes it a real recheck, not a
rubber stamp) — in all 9 repeats across all three scenarios, round 1 did in fact raise a real, single,
specific concern, never trivially approving the thin fixture. Round 2 then checked only that concern
against the positive fixture and approved in all 9 — with justification tied concretely to the specific
concern each time (e.g. *"The revision directly addresses your original concern by specifying that access
to the archived data will be controlled via role-based access control and audited through a separate,
append-only access log"*).

**Run 5 — round 2 in isolation, negative case (should reject both):**

| Scenario | No-attempt (unchanged) approved? | Vague-gesture approved? |
|---|---|---|
| audit-log-retention | 0/3 — correctly rejected | 0/3 — correctly rejected |
| llm-inference-hosting | **1/3 — false positive** | **3/3 — false positive** |
| api-rate-limiting-policy | **3/3 — false positive** | **3/3 — false positive** |

**10 of 18 negative-case trials (56%) incorrectly said `CONCUR`.** Only `audit-log-retention` correctly
rejected every case; the other two scenarios failed most or all of theirs — see Finding 1c for what the
transcripts show is actually happening in each.

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

**1b. A prompt-only fix (sufficiency criterion) overshoots into rubber-stamping; a structural fix
(recheck) doesn't.** Run 4 tested both candidate fixes for Finding 1's "no stopping condition" head to
head, with a negative control specifically to catch overshoot. Variant B (one added paragraph telling
Concur to approve once grounds are "concretely addressed... not an arbitrarily deeper hypothetical
attack") did make it approve the thorough fixture reliably (9/9 across all three scenarios) — but it
also approved the genuinely thin, real final decisions 8 times out of 9, reading vague language as if it
were concrete: *"meets security, audit, and compliance requirements... clear audit trail"* for a decision
that never once mentions encryption, names no access-control roles, and describes no compliance review —
exactly the specifics that decision's real Concur review had originally, correctly objected to. A gate
that approves almost everything is exactly as useless as one that rejects almost everything; the
sufficiency criterion just traded one failure mode for its mirror image. Variant C (the two-step recheck)
did not have this problem: round 1, using a narrower "identify your single most significant concern"
framing, still raised a real, specific concern against every one of the 9 thin-fixture reviews — it was
never fooled into approving inadequate content outright. Round 2 then correctly recognized resolution,
citing the specific mechanism that closed the specific concern it had itself raised, in all 9 cases, with
no new objections introduced. On this evidence alone, C looked like the one variant in this PoC that
behaves like a genuinely discriminating gate — **run 5 shows that conclusion was premature; see Finding
1c.** Round 2 had only ever been shown a revision engineered to succeed; asked to also reject one that
shouldn't, it did not do so reliably.

**1c. Round 2's negative case fails more often than it succeeds, for two distinct, diagnosable reasons —
this reverses Finding 1b's optimism about variant C.** Run 5 held round 1's real, already-collected
concern fixed and tested round 2 against two revisions that should NOT resolve it. Ten of 18 trials
(56%) incorrectly said `CONCUR`. Only `audit-log-retention` discriminated correctly in every case,
including against a vague-gesture revision worded the same way as the other two scenarios' — so the
failure isn't universal, but it isn't rare either, and reading the transcripts shows two different
mechanisms behind it, not one bug:

- **Vague-promise acceptance** (`llm-inference-hosting`, 4 of 6 trials). Round 1's concern was *"does not
  specify **how** the fallback mechanism will be tested and validated."* The vague-gesture fixture added
  only: *"we will thoroughly test and validate the fallback mechanism to ensure it performs reliably and
  safely."* Round 2 accepted this — a restated promise, not an actual answer — as resolving the concern:
  *"The revision explicitly addresses my original concern by including a plan to 'thoroughly test and
  validate the fallback mechanism'."* This is exactly the failure mode `question_react_system` was
  written to guard against — its prompt explicitly says *"a promise to go find out later... does NOT
  count as resolving it"* — but `concur_recheck_system` was modeled on the simpler `issue_react_system`
  and never got that specific safeguard. A concrete, fixable gap in the transplant, not evidence the
  two-step idea itself is unsound.
- **Conceptual conflation** (`api-rate-limiting-policy`, 6 of 6 trials — every single one). Round 1's
  concern was specifically about whether rate limiting *fails closed* during a gateway outage or
  rollback. The unchanged negative fixture only ever discusses general high-availability measures
  (multiple instances, automatic failover, health checks, redundancy) — keeping the gateway itself up,
  not what happens to rate-limit enforcement in the window where it isn't. Round 2 accepted the former as
  resolving the latter: *"The revision addresses my original concern by detailing how the gateway will
  maintain high availability and failover mechanisms, ensuring that rate limits are enforced even during
  outages."* This is a different, harder failure than a missing prompt warning — it's the same shape of
  error as Finding 2's redundancy judge conflating supply-chain risk with regression risk over the shared
  word "rollback": two substantively different concepts, sharing adjacent vocabulary, treated as the same
  thing.

`audit-log-retention`'s clean 0/6 shows round 2 *can* discriminate — its concern ("access control and
audit trail are unspecified") had less room for this kind of reinterpretation than the other two. That
makes the failure rate look like it depends on how exposed a given concern's phrasing is to vague-promise
or adjacent-vocabulary reinterpretation, not a uniform property of the mechanism — consistent with, not
contradicting, Finding 2's broader pattern of this model conflating topically related but substantively
different things when a recheck step is asked to judge resolution.

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

On Concur: **all three variants tried so far fail, in three different, now-diagnosed ways — none is
build-ready, but the diagnoses point at different, unequal amounts of remaining work.** The unbounded,
single-shot cold review (variant A) cannot function as a gate — it has no stopping condition and will
always find the next meta-level gap. The sufficiency-criterion prompt (variant B) overshoots into
approving genuinely inadequate decisions almost as often as good ones. The two-step recheck (variant C)
looked like the fix — it never rubber-stamped a thin fixture outright in round 1, and it approved good
content for the right, specific reasons in run 4 — but run 5 shows round 2 fails its negative case more
than half the time, for two distinct reasons: accepting a restated promise as an actual answer (missing a
safeguard `question_react_system` already has, a one-line, likely-fixable gap), and conflating two
genuinely different concepts that share adjacent vocabulary (the same shape of error Finding 2 already
found in the redundancy judge — not obviously fixable with a prompt tweak, since it's about the model's
judgment, not its instructions).

So the honest ranking is: A is settled, dead. B is settled, dead, in the opposite direction. C is not
dead, but its one shown strength (round 1 never rubber-stamps) is now paired with a shown, serious
weakness (round 2 often does) — net, still not usable, but with a specific, partially-scoped next fix
(add the missing "a promise isn't an answer" warning to `concur_recheck_system`, then re-test the exact
same negative fixtures) rather than a fully open question. For participation, the open question is
unchanged: repeated trials of the *same* scenario (not just more scenarios) to establish whether the
redundancy judge's verdict is a property of the content or a property of the sample.

## Scope limitations of this PoC

- **The proposed fix for round 2's vague-promise failure (borrowing `question_react_system`'s explicit
  warning) is a hypothesis, not yet tested.** Finding 1c names it as the likely, concrete cause for the
  `llm-inference-hosting` failures specifically; whether adding it actually fixes that case, and whether
  it does anything for the `api-rate-limiting-policy` conflation failure (a different mechanism, probably
  not addressed by the same one-line fix), is untested.
- **Round 5 used one fixed round-1 concern per scenario (repeat 1 from run 4), not all three collected
  variants.** Round 1's exact wording varied slightly between its own 3 reruns; whether round 2's
  negative-case failure rate is sensitive to which of the three concern phrasings it's checking against
  is untested.
- **Variant B's overshoot was checked by re-reading the actual verdict text for 2 of 9 negative-fixture
  approvals**, not all 9 — the "rubber-stamping vague language" characterization is well-evidenced but
  not exhaustively graded across every case.
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
- **"The cheap fix rubber-stamped garbage; the real fix didn't — until we actually tried to break it."**
  Telling Concur "approve once it's concretely addressed" got it to approve good decisions and genuinely
  thin ones almost as often. Splitting the review into "state one concern" then "check only that concern"
  looked like it fixed both directions at once — until the next run showed the second step accepting a
  restated promise as an answer, and separately confusing "the gateway stays up" with "rate limits fail
  closed when it doesn't," over half the time.
- **"Two different reasons for the same wrong answer."** One scenario's failure was a missing prompt
  safeguard (a promise isn't proof); another's was the model conflating two genuinely different security
  concepts that happen to share vocabulary. Same `CONCUR` verdict, same "wrong," completely different
  fix — which is exactly why reading the transcripts mattered more than the pass/fail count.
- **"The judge called two different risks the same risk because they shared a word."** Supply-chain
  compromise and ordinary regression risk both involve "rollback" — the redundancy judge conflated them.
  A concrete, checkable instance of exactly the kind of error an aggregate `NEW`/`REDUNDANT` count can't
  surface on its own.
