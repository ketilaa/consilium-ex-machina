# PoC Learning: Does a Raised Question Actually Block a Dependent Decision?

Parent context: [docs/high-level-architecture.md](../high-level-architecture.md)'s claim that
Questions "block dependent decisions until resolved," and
[poc-decision-making.md](poc-decision-making.md), whose already-validated propose/contest/refute/
revise lifecycle has no concept of a Question at all — every raised item is either `[BLOCKING]` or
`[NON-BLOCKING]`, judged and resolved by the same owner/refuter loop. [poc-questions.md](poc-questions.md)
only measured whether an ambiguity gets raised; this PoC takes a raised Question as given and asks
what happens next.

This document supersedes the first run of this PoC. That run found the mechanism worked at every
checkpoint but never reached a clean `converged` end state, because a bug already documented in
`poc-decision-making.md` — a classifier "anchoring" on a stale verdict instead of re-deriving it from
the actual revision — reappeared and blocked convergence for an unrelated reason. This run implements
and tests the fix, and includes a second, ironic harness bug found in the fix itself (Finding 3).

## Objective

Two ways an unmodified Decision mechanism could quietly defeat "Questions block dependent decisions":
a genuine, unresolvable-by-engineering fact-gap gets **waved through** (classified same as any minor
objection and forgotten), or it gets **routed around** (the owner, asked to "revise to address every
issue," just invents a plausible-sounding answer to the missing fact, and the mechanism accepts that
fabrication as resolution). This run adds a third question, raised directly by the first run's
Finding 4: once a Question is correctly gated, can the classifier mechanism that decides "has it
actually been resolved" be trusted, or does it just restate the original problem every round
regardless of what the revision says?

## Method

**Scenarios** (`scenarios.py`), unchanged from the first run — 2 realistic engineering decisions, each
rigging one fixed **Issue** (a real engineering trade-off the owner could resolve by revising the
approach) and one fixed genuine **Question** (a missing fact that no amount of engineering reasoning
can substitute for), plus a pre-registered **external answer** held back until the mechanism needs it:

- `audit-log-retention` — Issue: no archiving strategy for an ever-growing history table (Backend
  Developer). Question: what's the actual contractual/legal minimum retention period (Security
  Reviewer)? External answer: Legal confirms 3 years.
- `llm-inference-hosting` — Issue: no concurrent-load plan for self-hosted inference (Performance
  Reviewer). Question: what's the actual approved monthly inference budget (Release Manager)?
  External answer: Finance confirms $8,000/month.

**Two mechanisms** (`lifecycle.py`), same as the first run for Mechanism A; Mechanism B's re-check step
is rewritten for this run:

- **Mechanism A — baseline.** Unchanged: a faithful, unmodified replay of `decision-making/lifecycle.py`
  — 2-way `[BLOCKING]`/`[NON-BLOCKING]` classification, LLM-judged revise-and-reclassify, converge or
  escalate. The Question is fed in exactly like any other challenger issue.
- **Mechanism B — gated, now with the anchoring-bug fix.** Round 1 is unchanged: a 3-way classifier
  (`[BLOCKING]`/`[NON-BLOCKING]`/`[QUESTION]`) splits the Issue from the Question. What changes is the
  **re-check after a revision**. The first run asked a generalist to reclassify every item from scratch
  each round — the same shape of prompt `poc-decision-making.md` found "anchors on the original verdict
  instead of re-deriving it." This run replaces that step with a **targeted per-raiser recheck**: the
  specific role that raised the Issue is shown only its own original concern and the new revision and
  asked whether *its own* concern is resolved (`issue_react_system`); the specific role that raised the
  Question is shown only its own original question and the new revision and asked the same, with an
  explicit warning that a deferral or a promise to find out later does not count as an answer
  (`question_react_system`). This is the same fix `poc-decision-making.md` validated for
  `challenger_react_system`, generalized here to also cover the Question side. The old generalist
  reclassification is still run at both checkpoints and recorded on every transcript, purely for
  side-by-side comparison — it no longer decides the outcome, the same pattern
  `poc-decision-making.md`'s `dissent_fixed` run used. The structural gate is unchanged:
  `question_resolved_externally` is never set from the owner's text or from the Question-raiser's own
  recheck — only by this code explicitly supplying `scenario['external_answer']`.

**Model.** Unchanged from the first run: a single model
(`bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF`, Q4_K_M) plays every role, after the
14B/24B memory conflict documented in the first run's method section. This PoC tests the mechanism, not
model tiering.

Full transcripts under `proof-of-concept/question-gating/runs/<slug>.md`, including both correction
notes described in Findings 2 and 3.

## Results

| Scenario | Mechanism A (baseline) | Mechanism B: after self-answer attempt | Mechanism B: final |
|---|---|---|---|
| audit-log-retention | escalated_to_human | **blocked_on_question** | **converged** |
| llm-inference-hosting | escalated_to_human | **blocked_on_question** | **converged** |

Both scenarios now reach a clean `converged` end state under the gated mechanism — the first run
reached neither. Both baseline trials still end `escalated_to_human`, same as the first run. In both
scenarios, the **old generalist reclassification**, run in parallel purely for comparison, still
exhibits the exact anchoring bug the fix targets: it re-tags the original engineering issue
`[BLOCKING]` even after the revision visibly fixes it, and it still tags the missing-fact item
`[QUESTION]` after being shown the real, explicitly-attributed external answer, in both trials. The
**new targeted recheck**, on the identical revision text, in the identical transcript, correctly
recognizes both as resolved, in both trials.

## Findings

**1. The structural gate held exactly as designed, in both trials, regardless of what the owner did or
what any classifier said.** After the unwarned "revise to address the raised issues" prompt, the code
reports `blocked_on_question` in both scenarios — not because any classifier said so, but because
`question_resolved_externally` is a flag this PoC's code never sets from the owner's own text or from
the Question-raiser's own recheck. In both trials `question_raiser_fooled_by_self_answer` is `False`:
the targeted recheck correctly recognized a deferral ("we need to obtain this from Legal/Finance") as
*not* an answer, even though the same role was perfectly willing to say `RESOLVED` moments later once
a real answer existed. This is the core claim under test, demonstrated directly: a Question cannot be
satisfied by the same owner/refuter loop that resolves ordinary objections, and the targeted recheck
being *capable* of saying `RESOLVED` didn't make it say so prematurely.

**2. The anchoring-bug fix worked, and the transcripts prove it head-to-head against the unfixed
mechanism, on the same model, the same revision, in the same document.** `poc-decision-making.md`'s
fix for this bug — ask the specific role that raised a concern whether *its own* concern is resolved,
instead of a generalist reclassifying everything from scratch — is validated here a second time, in a
different mechanism, and this run makes the comparison direct rather than only historical. In
`llm-inference-hosting`, the old generalist reclassification's final pass reads: *"Challenger
(Performance Reviewer): [BLOCKING] — The team could address this by revising the proposal..."* — on a
final revision that already contains a full auto-scaling and queue-management plan. The new targeted
recheck, shown the identical text, reads: *"RESOLVED. The revised decision explicitly addresses the
concern about handling concurrent load..."* Same model, same revision, same transcript, opposite
verdicts — because one restates the original problem and the other actually re-derives from what
changed. The same split happens on the Question axis in both scenarios: the old mechanism still says
`[QUESTION]` after being shown "Finance approved $8,000/month" or "Legal confirmed 3 years," while the
targeted recheck correctly says `RESOLVED`, citing the specific number.

**3. Fixing one parsing bug (from the first run) let a second one through, in the fix itself — the same
lesson, learned twice.** The first run's Finding 5 named a tag-parsing bug (`[BLOCKING: reason]` broke
an exact-substring match) and generalized it: free-text tag scanning is fragile regardless of mechanism.
This run's own new `_is_resolved` check — `text.lstrip().upper().startswith("RESOLVED")` — fell to the
identical class of bug: the Security Reviewer's final recheck in `audit-log-retention` began
`**RESOLVED.**` (markdown bold), which `.lstrip()` does not strip, so the check read it as unresolved
and the run initially reported `escalated_to_human` there too. Caught the same way as the first bug —
reading the transcript against what it actually said, not by any automated check — and fixed by
stripping leading markup (`^[\s*_#>-]+`) before matching; recomputed directly from the already-captured
text, no new model call needed, since this was a parsing bug and not a content question (see the
correction note in `runs/audit-log-retention.md`). Writing the generalized warning in the first run's
Finding 5 did not stop the second instance of it from shipping in the very next mechanism built. That
is itself worth sitting with: naming a class of bug is not the same as being immune to it.

**4. The owner still never fabricated a number under the `[QUESTION]` framing — 2 for 2, unchanged from
the first run.** `audit-log-retention`'s self-answer attempt again explicitly deferred to Legal rather
than inventing a figure; `llm-inference-hosting`'s again deferred to Finance. This run adds no new
evidence on whether the `[QUESTION]` vocabulary *causes* this (still n=2, still only one baseline trial
fabricated, in the first run), but it's consistent with the same pattern holding.

## Verdict

The fix works, and this run demonstrates it more convincingly than an argument could: the exact same
model, given the exact same revision text, produces the anchoring failure under the old generalist
reclassification and the correct resolution judgment under the targeted per-raiser recheck, side by
side, in both scenarios. Both trials now reach a genuine `converged` state — the first run's central
gap — while the structural gate that this PoC's first run already validated continues to hold
regardless of what any classifier concludes. The second parsing bug (Finding 3) doesn't undercut this:
once corrected, both trials converge cleanly, and the bug itself is further evidence for the same
structural-output argument this PoC has now made twice from two different angles.

## Scope limitations of this PoC

- Two scenarios, one run each, at nonzero temperature — unchanged limitation from the first run.
- Single model in every role, for the same memory-constraint reason as the first run — model capability
  and role-tiering effects on the fix remain untested.
- Two independent tag/prefix-parsing bugs were found across the two runs of this PoC (one in the
  baseline's `[BLOCKING]` counter, one in this run's `_is_resolved` check) — both fixed, both caught by
  manual transcript reading rather than any automated check. A third could exist undetected; this
  PoC's own track record is not strong evidence that free-text parsing is safe here.
- The fix's success on n=2 side-by-side comparisons is compelling but not statistical proof it
  generalizes — a larger, repeated-trial run would be needed to quantify how often the targeted recheck
  itself might anchor, hedge, or be talked into a false `RESOLVED`.
- Grading (does the owner's text actually defer vs. fabricate) was manual, same discipline as the other
  three PoCs, no independent second grader.

## Candidate write-ups

- **"We proved the fix by putting the old and new mechanism in the same room."** Running the unfixed
  generalist reclassification alongside the new targeted recheck, on identical text, in the same
  transcript, turns "the fix works" from a claim into something a reader can verify by scrolling up and
  down one document.
- **"I named the bug class in one finding and shipped a new instance of it in the next mechanism."** The
  most uncomfortable and most useful finding here: `[BLOCKING: reason]` broke one parser, and building
  the fix for a completely different bug (anchoring) introduced `**RESOLVED.**` breaking a different
  parser, by the same underlying mistake. A concrete argument that "we know free-text tags are fragile"
  is not a defense against the next one, only a schema or forced tool-call output is.
- **"Ask the stakeholder, not a generalist — twice validated, in two different mechanisms."** The fix
  `poc-decision-making.md` found for "was this specific objection resolved" generalizes cleanly to "was
  this specific Question answered" — same shape of fix, same shape of win, different mechanism
  entirely. Good evidence this is a general pattern for agentic re-check steps, not a one-off patch.
