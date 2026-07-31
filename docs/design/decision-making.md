# Decision-Making: Consensus, Authority, and Lifecycle

Parent context: [docs/high-level-architecture.md](../high-level-architecture.md). This document
covers how a `Decision` moves from proposed to approved without either rubber-stamping or
deadlocking — the mechanics behind "Decisions are first-class citizens."

## The problem with plain multi-agent consensus

Multi-agent "collaboration" is not distributed-systems consensus (Raft/quorum agreeing on one true
value across replicas). It is agents reasoning under genuine uncertainty, and naive designs fail in
ways that look like agreement but aren't:

- **False convergence** — agents agree quickly because they are correlated (same model, similar
  prompts), not because the decision is sound. This looks like consensus but carries no more signal
  than a single agent's opinion.
- **No termination** — "keep raising questions and risks" has no natural stopping point without an
  explicit one; decisions can stay "under discussion" indefinitely.
- **Confidence theater** — an agent self-reporting "85% confident" is not evidence. It is a plausible
  sounding number, not a calibrated one.
- **Deadlock with no tiebreaker** — two agents with genuinely different mandates (e.g. Architect vs.
  Security Reviewer) disagree, and nothing resolves it without escalating to a human every time.

The mechanisms below exist specifically to counter these four failure modes.

## Decision lifecycle

A `Decision` moves through explicit states with hard transition criteria — not agent judgment calls:

```
proposed → contested → converged → approved
                                  → rejected
```

- **proposed** — a decision has been raised, with an initial recommendation and category (see
  Categorization below).
- **contested** — one or more agents have raised blocking questions, unresolved risks, or
  alternatives. A decision can move back to `contested` from `converged` if new evidence or a veto
  arrives before human approval.
- **converged** — transition requires: zero open *blocking* questions, a minimum number of
  independent supporting evidence items, no unresolved risk above the configured severity
  threshold, and a passed adversarial refuter gate (below). These thresholds are configuration per
  decision category, not hardcoded.
- **approved / rejected** — set by the decision's owner (see Authority below), subject to any
  organization-configured human approval gate for that category.

Confidence is a **derived** value computed from the same inputs that gate the `converged`
transition (evidence count, open risk severity, unresolved questions) — never a number an agent
reports about itself. This directly addresses confidence theater: if it isn't computed from
something legible, it isn't confidence, it's a claim.

## Adversarial refuter gate

Before a decision can move to `converged`, one agent is explicitly tasked with trying to refute it —
find the hole, argue the alternative, attack the weakest assumption — rather than being asked to
review and rubber-stamp. If a dedicated skeptic, working within a bounded effort budget, cannot
produce a blocking objection, that is stronger evidence than several agents independently agreeing.
This directly addresses false convergence: agreement between a proposer and a deliberate opponent
means more than agreement between similar agents.

## Bounded rounds and escalation

Discussion between `proposed` and `converged` is capped at a configured number of rounds. If a
decision has not converged within that budget, it escalates automatically to a human approval gate
rather than continuing indefinitely. This directly addresses the no-termination failure mode: the
platform never relies on agents deciding among themselves when to stop arguing.

## Authority: ownership vs. veto

Once a decision is contested, something has to break the tie. Two distinct mechanisms are needed
here, and they must not be conflated into one "who decides" field:

### Ownership (tie-break authority, scoped to a category)

Each decision **category** has one accountable role with final call over non-blocking disagreement
within that category — this is RACI's "Accountable," not a vote:

| Category              | Owner role            |
|------------------------|------------------------|
| API design             | Architect              |
| Database strategy      | Backend Developer / Domain Expert |
| Authentication         | Security Reviewer      |
| Deployment architecture| Release Manager        |
| Caching                | Architect              |
| Domain boundaries      | Domain Expert           |

This mapping is platform/organization configuration, read by the platform — not something agents
negotiate at decision time. Re-litigating "who decides" during every disagreement is exactly the
deadlock this is meant to prevent.

### Veto (cross-cutting, blocking authority)

Some roles can block *any* decision on their concern regardless of who owns the category — the
canonical case is a Security Reviewer blocking a caching decision on security grounds even though
Caching is owned by the Architect. Veto is deliberately modeled separately from ownership: if
"security always wins" is hardcoded into the ownership table instead, the platform loses the ability
to grant the same cross-cutting power to a future role (e.g. Compliance) without reshaping every
category mapping.

A veto forces a decision back to `contested` regardless of its current state, including after
`approved`, if raised before implementation is complete.

## Categorization: who assigns the category

Category determines the owner, so mis-categorization silently reassigns authority. Two approaches:

1. **Human safety net (default)** — a human sets or confirms the category, at least whenever it's
   ambiguous or contested. This is the chosen starting point: it's the cheapest way to avoid
   authority being decided implicitly by whichever agent happens to categorize the decision.
2. **Dedicated categorization role** — a specialist agent assigns category, with the human safety
   net retained for ambiguous or cross-cutting cases. Treated as a later optimization once enough
   real decisions exist to know what "ambiguous" looks like in practice, not a starting requirement.

## Resolved: re-categorization, unavailability, mapping scope, thresholds

- **Re-categorization** — reuses existing primitives rather than adding a new mechanism. Any agent
  can flag suspected mis-categorization via a `Question`. The change itself is only enacted by
  whoever holds categorization authority (the human safety net, today). If the decision was already
  `approved` under the old owner, recategorizing forces it back to `contested` — the new owner
  hasn't signed off on anything yet. If it's still `proposed`/`contested`, the category simply
  changes going forward. `Decision Recategorized` belongs in the event catalog: it changes who has
  authority, so it must be visible history, not a silent field update.

- **Owner unavailability** — split by owner type rather than solved as one mechanism. An *agent*
  owner not responding is an infra/reliability concern (timeout, retry, dead-letter), not a
  decision-design question. A *human* owner not responding within the round budget escalates to
  whoever configured the approval gate for that category. A per-category deputy is a possible later
  refinement, deliberately not designed now — no evidence yet that unavailability is a real problem
  worth a second authority layer.

- **Mapping scope** — global category → owner mapping by default, overridable per project. Plain
  configuration data; not modeled as a Decision itself.

- **Threshold tuning** — no fixed numbers yet, and intentionally so: a guessed threshold ("3 evidence
  items," "block on high severity") would carry false precision. Ships with a conservative default
  (≥1 independent evidence item, zero unresolved blocking risk, refuter gate passed) per category,
  tuned from real decisions as they flow through the system rather than fixed in advance.

Kept deliberately simple everywhere a mechanism (deputies, exact thresholds, override approval flow)
isn't yet justified by evidence — add it when a real case demands it, not ahead of one.
