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

No next PoC candidate queued for a new question. If Concur stays a priority, the next step is testing
whether adding the missing "a promise isn't an answer" safeguard to the recheck's second step actually
fixes the vague-promise failure mode, against the exact same negative fixtures — the conflation failure
mode is a harder, more open problem, not obviously fixable the same way. If participation stays a
priority, repeated trials of the *same* scenario to test whether the redundancy judge's verdict is a
property of content or of the sample.

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
