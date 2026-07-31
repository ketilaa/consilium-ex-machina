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

Design phase. There is no implementation yet — only the documents under `docs/`. Before proposing
code structure or starting implementation, read the architecture doc; the domain model (work items,
decisions, questions, events) should exist and be well-understood before any agent orchestration is
built on top of it.

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
