# High-Level Architecture: An Agentic Software Delivery Platform

## Purpose

Most AI-assisted development tools are built around a conversation with a model, or around an
autonomous agent that takes a task and produces code. This platform takes a different central
concept: **the work itself**.

Rather than asking an AI to "implement feature X," the platform models the entire software delivery
process — initiatives, projects, features, stories, tasks, decisions, questions, risks, assumptions,
evidence, and produced artifacts — as a structured, shared graph. Humans and AI agents are both
workers participating in the same engineering process against that shared model. The goal is to
improve software delivery by helping humans and agents make better engineering decisions together,
not to remove humans or to produce another coding assistant.

## Work is the source of truth

Every work item carries:

- goals and business context
- dependencies
- acceptance criteria
- constraints
- produced artifacts
- history
- ownership (human or agent)
- related decisions
- open questions

Agents never operate in isolation on a bare prompt; they always act on a well-defined piece of work
in this graph.

## Agents are specialists, not general assistants

Agents are role-based workers with clearly defined capabilities, permissions, tools,
responsibilities, and decision boundaries. Example roles: Planner, Architect, Domain Expert, Backend
Developer, Frontend Developer, Security Reviewer, Performance Reviewer, QA Engineer, Documentation
Writer, Release Manager.

The platform must be able to register new agent types — including via plugins — without changing
the core architecture. The role registry, not the model, defines what an agent is allowed to do and
decide.

## Collaboration, not a pipeline

The default shape in most systems is linear: *Requirement → Planner → Developer → Finished*. This
platform instead investigates a collaborative model: agents challenge each other's assumptions, ask
questions, identify risks, propose alternatives, and gather evidence *before* implementation begins.
Implementation happens only once the platform has reached sufficient, legible confidence that the
problem is understood — not once an agent has been asked to start.

Unconstrained multi-agent collaboration has real failure modes — false convergence between
correlated agents, no natural termination, self-reported confidence that means nothing, and deadlock
between agents with no defined authority to resolve disagreement. The platform's answer to these is
the decision lifecycle and authority model described in
[docs/design/decision-making.md](design/decision-making.md); this document only asserts that
collaboration, not a pipeline, is the shape being pursued.

## Decisions are first-class citizens

Engineering decisions (API design, database strategy, authentication, deployment architecture,
caching, domain boundaries, ...) are modeled explicitly, each collecting supporting evidence,
assumptions, identified risks, alternatives, participating agents, confidence, and approval state.
Implementation depends on *approved decisions*, not on incomplete requirements. Full lifecycle and
tie-break/authority mechanics: [docs/design/decision-making.md](design/decision-making.md).

## Questions are first-class citizens

Agents are expected to actively surface missing information rather than fill gaps silently:
missing business rules, unstated assumptions, unevaluated risks, unresolved architectural
decisions, missing domain knowledge. Questions may be answered by other agents or by humans, and
block dependent decisions until resolved.

## Humans remain part of the system

Humans are participants in the engineering process, not an external approval layer bolted on
afterward. Organizations configure policy-driven approval gates for critical stages — before
implementation, before architecture approval, before production deployment, or elsewhere. Some
workflows may require human approval; others may be fully autonomous. This is a configuration
choice per organization/category, not a platform-wide constant.

## Context over conversations

Rather than exposing an entire repository to every agent, the platform constructs **Context
Packets** scoped to the specific piece of work: relevant source files, architecture decisions,
related tasks, similar past implementations, coding conventions, dependency information, affected
tests, historical decisions, domain knowledge. Context construction is treated as at least as
important as prompt engineering — it determines whether an agent's reasoning is grounded or
guessing.

## Event-driven collaboration

Agents do not invoke one another directly. They subscribe to events and react independently, which
lets agents evolve without knowing about each other's implementation. Representative event catalog:

- Feature Created
- Task Planned
- Question Raised
- Decision Proposed
- Evidence Added
- Decision Approved
- Human Approval Granted
- Implementation Completed
- Review Requested

## Architectural philosophy

The platform should resemble an engineering organization, not a chatbot. It should continuously
discover missing information, challenge assumptions, gather evidence, improve plans, evaluate risks,
build consensus, coordinate implementation, and verify results. Coding is one activity among many.

## Areas to investigate

- Domain-driven design for the platform's own domain model
- Event-driven coordination between agents
- Agent lifecycle and scheduling
- Decision modeling and consensus mechanisms (see [docs/design/decision-making.md](design/decision-making.md))
- Context Packet generation
- Knowledge indexing and repository understanding
- Prompt and playbook composition per role
- Human approval workflows
- Artifact management
- Extensibility through agent plugins
- Separation of reasoning, planning, implementation, verification, and governance
