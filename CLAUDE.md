# consilium-ex-machina

## What this is

consilium-ex-machina is an exploration of an **agentic software delivery platform** — not another coding
assistant or autonomous coding agent. The central concept is the *work itself*: a structured task
graph of initiatives, projects, features, decisions, questions, risks, and evidence, that humans
and specialist AI agents collaborate around. Coding is one activity among many; the larger goal is
better engineering decisions, made visibly and accountably.

Full vision and rationale: [docs/high-level-architecture.md](docs/high-level-architecture.md).
Decision-making / consensus mechanics: [docs/design/decision-making.md](docs/design/decision-making.md).

## Current phase

The riskiest, most load-bearing assumptions behind the design were validated with real
proof-of-concept experiments (under `proof-of-concept/*/`, run against local models) before
any platform code got written, rather than argued from first principles alone. Findings are
written up in `docs/learning/`:

- [poc-decision-making.md](docs/learning/poc-decision-making.md) — the propose/contest/refute/
  converge lifecycle and the ownership/veto authority model. Validated, including a real bug found
  and fixed along the way (the re-check step anchoring on a stale verdict instead of re-deriving it).
- [poc-context-packets.md](docs/learning/poc-context-packets.md) — rule-based Context Packet
  construction vs. full-repo dump vs. no context. Validated decisively: full-dump silently
  truncates on smaller-context models while the packet doesn't, at meaningfully lower token cost
  even on models that can fit the full dump.
- [poc-questions.md](docs/learning/poc-questions.md) — whether role-framed reviewers surface more
  genuine ambiguity than one generalist agent (the "Questions are first-class citizens" pillar).
  Mixed but real: same model, only the framing changed, went from 0/3 to 3/3 ambiguities caught on
  the one task retested both ways — but that gain needed a capability floor the panel didn't clear
  on a weaker model, and no framing or model tier caught the one ambiguity the request's own wording
  gave no lexical hint toward.
- [poc-question-gating.md](docs/learning/poc-question-gating.md) — whether a raised Question actually
  blocks a dependent Decision, the mechanism half poc-questions.md left untested. Validated across two
  runs. First run: a structural, code-enforced gate held in both trials regardless of whether the
  owner deferred to an external source or fabricated a placeholder answer, but the
  "re-check anchors on stale verdict" bug from poc-decision-making.md reappeared and blocked a clean
  convergence in both trials. Second run: fixed the anchoring bug by generalizing
  poc-decision-making.md's per-role targeted recheck (ask the specific raiser whether *its own* item
  is resolved, instead of a generalist reclassifying everything from scratch) — both trials now
  converge cleanly, demonstrated head-to-head against the unfixed mechanism in the same transcripts.
  Also surfaced a second, ironic tag-parsing bug in the fix's own code (markdown formatting broke a
  strict prefix match, the same class of bug the first run's Finding 5 had just named) — fixed, and a
  reminder that naming a bug class doesn't make new code immune to it.
- [poc-structured-output.md](docs/learning/poc-structured-output.md) — does forcing JSON-schema output
  eliminate the tag-parsing bug class poc-question-gating.md found twice? More complicated than the
  framing going in: an *already-hardened* free-text parser (permissive prefix matching,
  markup-stripping) matched structured output's reliability exactly, 100%/100% across 48 trials each,
  at roughly half the token/latency cost. Structured output also isn't truncation-proof — a tight
  token budget broke every structured call in a stress test, and its own higher verbosity makes it
  comparatively more exposed to that than free text. The validated fix was hardening the parser, not
  switching formats; structured output's real remaining case (resilience against a future,
  as-yet-unseen format surprise) is a claim this fixed-fixture test can't settle either way.
- [poc-raci-veto.md](docs/learning/poc-raci-veto.md) — two claims from `docs/design/decision-making.md`'s
  veto/authority section, previously untested: does RACI participation scoping (Informed gets no
  voice in contest) lose real signal, and does a cold Concur gate (a role that held no pen during
  propose/contest/revise, reviewing the final decision and asked a single yes/no question on its
  own named grounds) add anything beyond the existing classify/recheck mechanism? Participation is
  still an open question — a second run's fuller data showed the redundancy judge flipping verdicts
  on identical scenario text between runs, so the one real instance of harm found can't yet be told
  apart from noise. Concur went through three variants, all now settled dead in three different ways:
  the original single-shot prompt has no notion of "sufficient" (a positive control showed every
  fixture, however thorough, gets a different, deeper follow-on objection instead of approval); adding
  a sufficiency instruction backfired into approving genuinely thin decisions almost as often as good
  ones; splitting into a two-step recheck (state one concern, then check only that concern, reusing the
  fix already validated for ordinary challengers) looked promising after one run, but a follow-up
  testing its negative case found it accepts a bad revision 56% of the time, for two distinct, diagnosed
  reasons — accepting a restated promise as an actual answer (a likely-fixable missing prompt safeguard),
  and conflating two different security concepts that share vocabulary (the same shape of error already
  found in the redundancy judge, not obviously fixable by a prompt tweak).
- [poc-risk-classification.md](docs/learning/poc-risk-classification.md) — grounded in a real, live
  decision this platform produced (d-22ffab13): two of its raised concerns were, on human review,
  judged real but disproportionate to the work item's current risk profile — not blockers, but not
  dismissible either. Round 1: adding a fourth classification, RISK, held the critical safety
  property cleanly (0% false-defer across three scenarios, including a correctness-bug trap and a
  high-pressure profile testing both overshoot directions) and reproduced the real d-22ffab13
  judgment call exactly — the cleanest single round in this whole PoC series. Round 2 complicated
  that considerably: the proposed recall fix (tell the classifier phrasing isn't the test) did
  nothing, the exact same two items failed the exact same way; adding a fifth classification,
  WORK_ITEM (unconditional follow-up work, vs. RISK's conditional deferral), turned out to be
  unreliable on realistic, topically-clustered items (5 of 6 items inconsistent across 3 reps in
  the real scenario, and a new false-defer channel opened through WORK_ITEM itself, 22% on
  BLOCKING items); and a fix for treating an already-scheduled future risk-profile change as
  urgent now worked exactly on its target item, then spilled over into wrongly blocking an
  unrelated one on the same borrowed reasoning. Round 3 tested the leading hypothesis for that
  confusion — that batching topically-similar items together caused it — by reclassifying the
  same items alone. Refuted: isolation fixed one item, left one wrong-but-now-consistent, and
  made a third strictly worse with a tag that never appeared in batch. It also sharpened round 2's
  "spillover" finding into something more precise: the support-tooling item stayed wrongly blocked
  even with the adjacent item removed entirely, reasoning straight off the risk-profile text
  itself rather than off any neighboring item — the future-change fix over-applies to anything
  thematically connected to a stated transition, not to whatever happens to be nearby in a batch.
  RISK alone (round 1's original two-way split) still looks solid; the fifth category's problem is
  now known not to be about batching, but what actually causes it is still open. Round 4 finally
  controlled for the other variable this PoC had flagged since round 1 and never tested: model
  tier (Groq-hosted openai/gpt-oss-120b, ~120B params, vs. the local ~24B quantized model used
  everywhere else). Genuine mixed evidence, single-pass given a short-lived API key: two of round
  2-3's confirmed, twice-unfixed-by-prompting bugs (the phrasing bug, the risk-profile
  over-application bug) were classified correctly on the first try, no prompt change — but the
  same run also produced a false-defer (a real, current blocker waved into WORK_ITEM) that the
  local model never made in any round. Model tier is a real lever, not a substitute for validating
  the false-defer property specifically on whatever model ends up running this — that validation
  doesn't get cheaper just because the model is stronger.

Next PoC candidate queued: a structured, mandatory threat analysis (STRIDE-style categories, gated
behind a cheap trigger step that flags only whether a decision has real attack surface at all) as
an alternative to Security Reviewer's free-text critique, which has been the recurring source of
unbounded escalation across Concur and now the WORK_ITEM/RISK confusion in risk-classification.
Untested in both directions: does the trigger step reliably fire on real attack surface even when
not obviously phrased, and does it correctly stay quiet on decisions with no real security
relevance. If RISK/WORK_ITEM stays a priority instead, round 3 ruled out batching as the cause but
didn't find the real one — casual isolation isn't a safe fix either, since it measurably
destabilized a previously-stable item.

Other open threads, lower priority right now: if Concur stays a priority, test the missing "a
promise isn't an answer" safeguard on the recheck's second step (the conflation failure mode is
harder, not obviously fixable the same way). If participation stays a priority, repeated trials of
the *same* scenario to test whether the redundancy judge's verdict is a property of content or of
the sample. If the WORK_ITEM classification stays a priority despite round 2's results, it needs a
differently-designed round, not a third minor prompt tweak — round 2 already showed that adding
one more explicit instruction to an already-complicated 5-way prompt doesn't reliably fix the
specific thing it's aimed at and can spill onto adjacent judgments instead.

## Platform code

Multi-module Gradle build at the repo root (`settings.gradle.kts` includes both modules;
root `gradlew` builds and tests everything).

**`decision-engine/`** — the first real, kept platform component, not another PoC script. It
implements the validated Decision lifecycle (propose/contest/classify/revise/recheck) as an
event-sourced domain model, with both validated fixes as unconditional domain rules: the
targeted per-raiser recheck (never a generalist reclassifying from scratch), and a Question
that can only be cleared by an externally-sourced answer (a code-level gate the owner's own
text can never satisfy, not just a convention). Package `com.github.ketilaa.consilium.decisions`;
`DecisionLifecycleService` is the orchestrator; `DecisionEngineCli` (`run [--origin <ref>]` /
`show <id>`) is the demo entry point. A role can raise more than one distinct concern per
reaction (`ItemId`, `ItemSplitter`) — a real gap a live run against a real model exposed and
this codebase now handles, not something invented ahead of evidence.

**`work-items/`** — the second real component, and the reason `OriginReference` needed no
changes to accept it: Work Item is the umbrella concept `docs/high-level-architecture.md` and
this file's own terminology already named (initiative/project/feature/story/task are its
*kinds*, not sibling entities). Package `com.github.ketilaa.consilium.workitems`, same
event-sourced/ports-and-adapters shape as `decisions` for consistency. `WorkItemDecisionsView`
is the one place this module depends on `decisions` (via the new
`DecisionRepository.findByOrigin`) — the reverse is never true, `decisions` still has no idea
Work Items exist. "Related decisions" and "open questions" are **derived views**, not state
Work Item stores itself, to avoid a second, driftable copy of facts the Decision Engine already
owns. `WorkItemCli` (`create <kind> <title>` / `show <id>`) is the demo entry point; pair with
`DecisionEngineCli run --origin work-item:<id>` to attach a real decision to a real work item —
verified live, including the case where a Decision converges and the work item's open-questions
count correctly drops to zero.

Deliberately deferred until a further real need justifies them: an event bus/message broker
(both modules' repositories are queried in-process/synchronously; `DecisionEventPublisher`
still has no subscriber beyond logging), a network/HTTP API (still a library + CLI per module),
strict Work Item kind-hierarchy validation (Task must be under Story, etc. — nothing has
demanded it yet), and the category→owner authority table, veto mechanics, and human approval
gates from `docs/design/decision-making.md`. The category→owner table and human approval gates
remain untested by any PoC. Veto now has five PoC runs' worth of evidence
([poc-raci-veto.md](docs/learning/poc-raci-veto.md)) and all three Concur variants tried are settled
dead: the original single-shot prompt has no stopping condition (a positive control got rejected every
time, on a genuinely different follow-on gap each time); a sufficiency-instruction fix backfired into
rubber-stamping thin decisions; a two-step recheck fix (state one concern, then check only that
concern) looked clean on its positive case but a follow-up found it accepts a bad revision 56% of the
time, for two distinct, diagnosed reasons (accepting a restated promise as an answer; conflating two
different security concepts sharing vocabulary). Participation is still unresolved either way (the
redundancy judge flipped its verdict on identical scenarios between runs). Nowhere near build-ready;
don't build ahead of evidence, the same discipline that held before question-gating was validated.

Before proposing further platform code structure, read the architecture doc and the PoC findings
above; the domain model should stay grounded in what's actually been tested, not just what's
designed.

## Core terminology

- **Work item** — a unit of work (initiative, project, feature, story, task) with goals, context,
  dependencies, acceptance criteria, constraints, artifacts, history, and ownership.
- **Decision** — a first-class engineering decision (e.g. API design, auth, deployment) with
  evidence, assumptions, risks, alternatives, confidence, and approval state. See
  [docs/design/decision-making.md](docs/design/decision-making.md) for lifecycle and authority model.
- **Question** — a first-class, explicitly raised gap in understanding, answerable by an agent or a
  human.
- **Agent** — a role-based specialist worker (Planner, Architect, Backend Developer, Security
  Reviewer, etc.) with defined capabilities, permissions, tools, and decision boundaries. Humans are
  workers too, not external overseers.
- **Context Packet** — the constructed slice of context (source files, decisions, related tasks,
  conventions, history) handed to an agent for a specific piece of work, in place of full-repo
  exposure.
- **Event** — the unit of coordination between agents (e.g. `Decision Proposed`, `Question Raised`,
  `Human Approval Granted`); agents subscribe to events rather than invoking each other directly.
