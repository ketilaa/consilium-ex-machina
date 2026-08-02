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

Design phase for the platform itself — no production/platform code yet. But the riskiest,
most load-bearing assumptions behind the design are being validated with real proof-of-concept
experiments (under `proof-of-concept/*/`, run against local models) before any platform code gets
written, rather than argued from first principles alone. Findings are written up in `docs/learning/`:

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

No next PoC candidate queued yet — the validated mechanics (decision lifecycle, context packets,
question surfacing, question gating, and now the parsing-format question) cover the load-bearing
assumptions identified so far.

Before proposing platform code structure, read the architecture doc and the PoC findings above; the
domain model should stay grounded in what's actually been tested, not just what's designed.

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
