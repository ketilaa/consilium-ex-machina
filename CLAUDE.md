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

Next candidate, not yet started: whether agents reliably raise genuine clarifying Questions instead
of guessing under ambiguity (the "Questions are first-class citizens" pillar).

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
