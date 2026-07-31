# PoC Learning: Does the Decision-Making Lifecycle Beat a Single Agent?

Parent context: [docs/design/decision-making.md](../design/decision-making.md).

## Objective

The whole "agents collaborate instead of forming a pipeline" pillar of the platform vision only
earns its complexity if structured deliberation produces measurably better engineering decisions
than a single competent agent deciding alone. Before investing in any platform plumbing (event
bus, work-item graph, Context Packets, agent registry), this PoC tests that one claim directly,
using nothing but the lifecycle mechanics from `docs/design/decision-making.md` and two local
models — no platform code involved.

The question: **given the same decision and the same context, does propose → contest → refute →
(revise →) converge surface risks, alternatives, or considerations that a single-agent baseline
misses — and is that worth the extra calls it costs?**

## Method

Three real, concrete decisions about sw-foundry itself were run through both a baseline and the
full lifecycle:

| Decision | Category | Owner | Challengers |
|---|---|---|---|
| In-process pub/sub vs. external broker for agent event coordination | *Integration architecture — no entry in the current owner table, deliberately used to test the mapping gap* | Architect | Backend Developer, Release Manager |
| Relational DB vs. graph DB for the work-item graph | Database strategy | Backend Developer | Architect, Performance Reviewer |
| Session cookies vs. bearer tokens for API auth | Authentication | Security Reviewer | Backend Developer, Architect |

**Models.** Two local models, deliberately assigned to different tiers of the process rather than
used uniformly, to test something more realistic than "throw the biggest model at everything":

- **Qwen2.5-Coder-14B-Instruct** (port 8080) — plays the single-agent baseline, and the Owner role
  in the lifecycle (propose / revise / final call).
- **Qwen2.5-7B-Instruct** (port 8081) — plays every Challenger and the adversarial Refuter in the
  lifecycle.

If a smaller, cheaper model in the challenger/refuter seats can still surface issues the bigger
single model misses when deciding alone, that's a meaningfully stronger result than needing top-tier
capability in every seat.

**Baseline.** One call to the 14B model: given the decision and context, decide directly and
justify it, mentioning risks/alternatives considered. No scaffolding.

**Lifecycle** (implemented in `proof-of-concept/decision-making/lifecycle.py`, following
`docs/design/decision-making.md`):

1. **Propose** — the category owner proposes a concrete recommendation.
2. **Contest** — each challenger role reviews the proposal strictly from its own mandate and
   raises concrete issues (or explicitly says it has none — challengers were told not to invent
   filler objections).
3. **Refute & classify** — an independent adversarial Refuter (not the owner, not a challenger)
   tries to find its own flaw, then classifies every raised issue as `[BLOCKING]` or
   `[NON-BLOCKING]`. This deliberately keeps the blocking/non-blocking call out of the owner's own
   hands — the whole point of decision-making.md's "confidence must be derived, not self-reported"
   principle only holds if the classifier isn't grading its own proposal.
4. **Revise** (bounded to one round) — if any blocking issue exists, the owner must revise the
   decision to address every blocking issue or give an explicit counter-argument for why it
   doesn't apply.
5. **Re-check** — the refuter re-classifies the revised proposal against the same issues.
6. **Converge or escalate** — if no blocking issues remain, the decision `converged` with a
   confidence score computed from the number of issues raised and whether a revision round was
   needed (not self-reported by any agent). If blocking issues survive the one allowed revision
   round, the decision `escalates_to_human` rather than looping — per the bounded-rounds design.

Confidence formula used (a deliberately simple heuristic for this PoC, not a proposal for the
platform's real scoring): `min(ceiling, base + 0.05 × total_issues_raised)`, where `base`/`ceiling`
are lower if a revision round was needed than if the proposal converged on the first pass.

Full transcripts for every step, for every decision, are committed under
`proof-of-concept/decision-making/runs/<decision-slug>/` (`baseline.md`, `lifecycle.md`,
`summary.json`) as the evidence trail behind this report.

## Results

All three decisions converged on the *first* pass — the refuter never classified anything as
`[BLOCKING]`, so the one-round revision path was never exercised, and every run reached the
confidence ceiling for a no-revision convergence.

| Decision | State | Rounds | Confidence | Baseline time | Lifecycle time | Final decision changed vs. baseline? |
|---|---|---|---|---|---|---|
| Event coordination | converged | 0 | 0.95 | 43.3s | 106.7s | No — same recommendation, same rationale |
| Work-item persistence | converged | 0 | 0.95 | 36.4s | 112.2s | No — same recommendation, same rationale |
| API authentication | converged | 0 | 0.95 | 36.9s | 109.2s | No — same recommendation, slightly more specific rationale (present in the *first* proposal, before any contest) |

Full transcripts: `proof-of-concept/decision-making/runs/<slug>/{baseline,lifecycle}.md`.

## Findings

**1. The adversarial refuter did not adversarially refute, in 3 for 3 trials.** It was explicitly
instructed to first look for its own flaw, independent of the challengers, then classify every
raised issue as blocking or non-blocking. Across all three decisions and roughly 30 raised
challenger issues combined, it introduced zero flaws of its own and marked every single issue
`[NON-BLOCKING]`, almost always with the same shape of reasoning: *"X is a valid concern, but it
can be addressed with standard practices/mechanisms."* That is the exact false-convergence failure
mode `docs/design/decision-making.md` names — happening inside the mechanism specifically designed
to prevent it. Separating the refuter from the owner (so the proposal wasn't grading itself) was
not sufficient on its own; the refuter still behaved like a reviewer being polite rather than an
adversary being adversarial.

**2. Derived confidence fixed self-report but is still gameable.** The formula (`base + 0.05 ×
issues_raised`, capped) was built specifically so no agent could just assert a confidence number.
In practice it saturated to the ceiling (0.95) in all three runs — not because the decisions were
equally sound, but because all three produced a similar *volume* of non-blocking chatter. A metric
driven by how much discussion happened, rather than by how much of it survived genuine scrutiny, is
not meaningfully different from confidence theater — it's just theater with more steps.

**3. Genuinely useful ideas surfaced, and were then silently dropped.** In `work-item-persistence`,
the Performance Reviewer challenger proposed a hybrid storage approach (relational for some data,
graph for relationship-heavy data) that appears nowhere in the baseline. It's a real alternative
worth weighing. But because it was classified non-blocking, and revision is only triggered by a
blocking verdict, it never reached the final decision text — the lifecycle's own output is
byte-for-byte the owner's original, pre-contest proposal. This is not a prompting weakness like
findings 1–2, it's a gap in the mechanism itself: the current design has no path for "good idea,
not blocking" to influence the outcome at all. Worth fixing regardless of how the refuter's
adversarial behavior improves.

**4. Where the process did add value, it came from role framing, not deliberation.** In
`api-authentication`, the lifecycle's initial proposal (from the Security-Reviewer-framed owner)
was more specific than the baseline — cookies for the login handshake, JWTs for subsequent API
calls, explicitly reasoned through both human and machine callers. That's a better answer than the
baseline's plain "use bearer tokens." But it appeared in step 1, before any contest or refutation —
it's evidence that *giving a specialist role a sharper mandate* produces a better first answer, not
evidence that *challenge-and-refute* improved anything.

**5. Cost was real and one-sided.** The lifecycle used roughly 2.5–3× the wall-clock time of the
baseline in every case, for an unchanged final decision in all three. Six sequential model calls per
decision versus one is the mechanical reason.

**6. The category-mapping gap didn't break anything, but that's a weak result.** `event-coordination`
had no clean entry in the owner table and was deliberately routed to Architect as a fallback. It ran
through the lifecycle without incident — which shows the fallback doesn't crash, not that Architect
was the *right* owner. This decision needs a harder test (one where the "wrong" owner would visibly
produce a worse outcome) to say anything stronger.

## Verdict

This doesn't kill the platform's central premise — the lifecycle mechanics (propose/contest/refute,
category ownership, bounded rounds) ran end-to-end without any structural failure, and one piece
(role-specific framing) clearly earned its keep. But it does falsify the specific, hopeful version
of the claim: *"a nominal adversarial-refuter role plus a derived-confidence formula is enough to
avoid rubber-stamping."* On this evidence, it is not enough — at least not with a 7B model in the
refuter/challenger seats and with decisions that had a fairly uncontroversial best answer going in.

Two variables are confounded here and need to be separated before concluding anything stronger:
weak model behavior in the refuter seat, and an easy decision set with no real controversy to expose
disagreement. The next PoC iteration should isolate them — put a stronger model in the refuter seat
on the *same* decisions, and separately, run the current setup against decisions that have a real,
debatable tradeoff (e.g. two defensible options with different real costs) rather than one obviously
dominant answer.

## Scope limitations of this PoC

- One run per decision, not repeated trials — no variance data on how often false convergence
  happens.
- Challenger max-token limit (500) truncated at least one challenger response mid-sentence
  (`api-authentication`, Backend Developer) — a token-budget artifact, not a finding about the
  mechanism.
- Only one revision round was possible by design (per the bounded-rounds principle); since nothing
  ever blocked, that path is entirely untested by this run.
- The confidence formula, category table, and role mandates are all this PoC's own inventions for
  testing purposes, not settled parts of the platform design.

## Follow-up: rigging a genuine dissent

Finding 1 above left two confounded explanations open: a weak model too agreeable to push back,
or a decision set with no real controversy to expose disagreement. This follow-up isolates the
variable directly: same models, same decisions, same lifecycle code, but one challenger per
decision is now fed a fixed, concrete, non-negotiable objection instead of being asked to raise
its own generic concerns (`proof-of-concept/decision-making/decisions.py`, `dissent` field;
implementation in `lifecycle_dissent.py`). After a revision, the dissenter is also asked directly
whether *its own* objection was resolved, independent of the refuter's re-classification, so the
two judgments can be compared. Full transcripts:
`proof-of-concept/decision-making/runs/<slug>/dissent.md`.

| Decision | Round-1 verdict on the dissent | Revision | Dissenter's own verdict on revision | Refuter's round-2 verdict | Final state |
|---|---|---|---|---|---|
| Event coordination | BLOCKING | Flipped to external broker (NATS) | CONCERN RESOLVED | REFUTED (same objection restated) | escalated_to_human |
| Work-item persistence | BLOCKING | Flipped to relational DB (PostgreSQL) | CONCERN RESOLVED | REFUTED (same objection restated) | escalated_to_human |
| API authentication | BLOCKING | Added server-side denylist + short-lived tokens | CONCERN RESOLVED | REFUTED (same objection restated) | escalated_to_human |

**A concrete, forceful objection does get recognized as blocking.** Unlike the ~30 generic,
hedged concerns in the original PoC — all waved through as non-blocking — the rigged objection was
correctly flagged `[BLOCKING]` in all three trials, on the first pass, while the other (still
generic) challenger's points were still correctly waved through. This means the refuter isn't
categorically incapable of blocking; it was responding rationally to weak input the first time.
**That revises finding 1 from the original PoC**: the honest reading is no longer "the refuter
never refutes," it's "the refuter had never yet been shown anything worth refuting."

**The owner engaged with the substance, not just the form.** All three revisions directly targeted
the stated failure scenario rather than reframing or reassuring: a crash-safe broker for the event
loss scenario, a database with mature backup/replication for the data-loss scenario, an explicit
revocation mechanism for the compromised-agent scenario. The decision substantively changed in two
of three cases and was materially hardened in the third — the first evidence in this whole PoC of
deliberation actually changing an outcome.

**But the refuter's re-check doesn't re-check — it anchors on the original verdict.** In all three
transcripts, the round-2 classification restates the *original* problem statement almost verbatim,
writes out a "Resolution" that describes the fix accurately and favorably, and then tags the same
item `[BLOCKING]` anyway — a direct contradiction inside its own output. All three runs escalated to
a human despite the objection's own author independently judging the fix adequate. This is a
distinct failure mode from the original PoC's leniency: not "won't block anything," but "can't
tell when a real block has actually been resolved," because it re-scans static issue text instead
of judging the specific revision against the specific objection.

**Practical fix implied, not yet built:** route "was blocking issue X resolved?" back to whichever
role raised X, the way this experiment already does for the dissenter — rather than a generic
refuter re-scanning the entire issue list from scratch. The dissenter judged its own resolution
correctly in all three cases; the generalist re-check did not, in any of them.

**Which way this fails matters.** All three false non-convergences erred toward escalating to a
human rather than silently accepting an unresolved risk — the safer direction if a mechanism has to
fail somewhere. But an always-escalate-after-any-block behavior also means the bounded-revision
round never actually saves a human review, which defeats half its purpose. This isn't a reason to
relax the check; it's a reason to fix the specific re-check logic identified above.

## Revised verdict

The original verdict undersold the mechanism. On this second pass: category ownership, the
propose/contest/refute structure, and bounded-round revision all behaved sensibly once a genuine
conflict actually existed — the tie-break/authority question the whole exercise set out to probe
was, in effect, never in doubt, because a real objection with nowhere to hide reliably produced a
real, substantive fix. What's now clearly broken is narrower and more fixable than "add an
adversarial role": the specific step that decides whether a revision actually satisfies a specific
objection needs to ask the party that holds the objection, not a generalist reprocessing everything
from the top.

## Fix: ask the objecting role, not the generalist

The implied fix above was implemented and re-run: the post-revision re-check no longer routes
through the generalist refuter re-scanning every issue from scratch. Instead, each role that raised
a concern (the dissenter, and any other challenger) is shown its own original concern plus the
revision and asked, directly, whether *its own* concern is resolved — the same question that already
worked correctly for the dissenter in the previous run, now applied uniformly
(`challenger_react_system` in `roles.py`; convergence requires every role to answer `CONCERN
RESOLVED`). The old generalist refuter re-check is still run and recorded on every transcript, but
only for side-by-side comparison — it no longer decides the outcome.

Result, all three decisions:

| Decision | Fixed mechanism (per-role reaction) | Old refuter re-check | Confidence |
|---|---|---|---|
| Event coordination | converged — both roles confirm resolved | still says REFUTED / blocking | 0.9 |
| Work-item persistence | converged — both roles confirm resolved | still says REFUTED / blocking | 0.9 |
| API authentication | converged — both roles confirm resolved (including the second, non-dissenter blocking item) | still says REFUTED / blocking | 0.9 |

All three now converge correctly, matching what an objective read of the transcripts already
suggested: each revision genuinely fixed the stated failure scenario. The old refuter mechanism, run
in parallel purely for comparison, disagreed in all three cases — reproducing the anchoring behavior
exactly, which confirms the diagnosis rather than the fix having accidentally "solved" a problem that
wasn't there. Full transcripts: `proof-of-concept/decision-making/runs/<slug>/dissent_fixed.md`
(the earlier, anchoring-mechanism transcripts remain at `dissent.md` for comparison — nothing was
overwritten).

This closes the loop opened by finding 1 in the original PoC: a real, structural weakness was found
(the re-check step), a specific fix was proposed from the evidence rather than guessed at, and the
fix was verified to change the outcome on the same test cases — not just asserted to.

## Candidate write-ups

Flagging these because they're concrete, evidence-backed, and more interesting than "we tried
multi-agent AI and it sort of worked":

- **"We built the textbook anti-rubber-stamp mechanism, and it rubber-stamped anyway."** A
  contrarian, data-backed piece on why an adversarial-agent role doesn't behave adversarially by
  default, what it actually took to make it bite (a concrete, failure-scenario-grounded objection),
  and the second bug that surfaced right behind it once the first one was fixed.
- **"Derived confidence isn't automatically better than self-reported confidence."** The formula
  removed self-report but is still gameable by discussion volume — a caution for anyone building
  agent confidence scoring who assumes "computed, not asserted" is sufficient by itself.
- **"The AI process found a better idea than the human-equivalent baseline — and then ignored it."**
  The hybrid-storage suggestion that never made it past "non-blocking." A concrete example of why
  *surfacing* good input and *acting* on it are different design problems.
- **"3x the cost, the same three answers."** A blunt piece on measuring the actual overhead of
  multi-agent deliberation against what it bought, as a counterweight to multi-agent-hype content
  that doesn't measure anything.
- **"We accused the referee of bias. It turned out we never gave it a foul to call."** The rigged
  dissent flips the first PoC's headline finding: fed a genuinely concrete objection, the same
  refuter that waved through 30 vague concerns blocked correctly every time. A piece about how easy
  it is to blame a judge for leniency when the real problem is the quality of what's put in front of
  it.
- **"The agent that raised the objection was a better judge of whether it was fixed than the agent
  whose job was to judge."** All three re-checks anchored on their own prior verdict instead of
  re-deriving it from the fix; the objecting party got it right all three times. A concrete lesson
  for anyone building a "does this satisfy the concern" check into an agent pipeline: ask the
  stakeholder, not a generalist reviewer.
