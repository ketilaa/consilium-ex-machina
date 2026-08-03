# PoC Learning: Does RACI Participation Scoping Lose Signal, and Does a Cold Concur Gate Add Value?

Parent context: [docs/design/decision-making.md](../design/decision-making.md)'s "Authority: ownership
vs. veto" section, which frames the category-owner table as RACI's "Accountable" and describes veto as
"cross-cutting, blocking authority" deliberately modeled separately from ownership — real design surface
CLAUDE.md explicitly defers pending a PoC, the same way question-gating was validated before being
built. This PoC tests two distinct claims raised while designing that mechanism, not the ownership table
itself (unchanged, untested here).

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
Concur holder deliberately *not* already in the Responsible/Consulted set:

- `audit-log-retention` — Accountable: Release Manager. Responsible: Backend Developer. Consulted:
  Architect. **Informed: Performance Reviewer** — expected *safe* to exclude (retention policy has
  little to do with runtime performance). Concur: Security Reviewer, on compliance/audit grounds.
- `llm-inference-hosting` — Accountable: Architect. Responsible: Backend Developer. Consulted:
  Performance Reviewer. **Informed: Security Reviewer** — a deliberate stress case: self-hosted vs.
  third-party API has real data-handling implications, so this Informed assignment was chosen expecting
  it might *not* be safe. Concur: Release Manager, on deployability/rollback-safety grounds.

**Mechanism** (`lifecycle.py`): one proposal per scenario, then one round of live contest from
Responsible + Consulted + Informed together, shared identically between both conditions below so the
only variable is which reactions get fed into the lifecycle:

- **Mechanism A — baseline.** The already-validated propose/3-way-classify/revise/targeted-per-raiser-
  recheck lifecycle (`classifier_system_3way`, `issue_react_system`, `question_react_system`, carried
  over unmodified from question-gating), run over all three of R+C+I as challengers — today's world,
  no RACI concept.
- **Mechanism B — raci.** The identical lifecycle, run over R+C only. Informed's reaction is withheld
  entirely.

Then, regardless of raci's outcome: a neutral judge (`redundancy_judge_system`) compares Informed's
withheld reaction against what R+C actually raised, answering `NEW` or `REDUNDANT`. Separately, the
Concur-holder is shown *only* raci's final decision text — not the transcript, not the classification —
and asked to `CONCUR` or `DO NOT CONCUR` strictly on its own named grounds, repeated 3 times to check
consistency.

**Model.** Single model throughout (`bartowski/mistralai_Mistral-Small-3.1-24B-Instruct-2503-GGUF`),
same as every prior PoC in this series. Full transcripts under `proof-of-concept/raci-veto/runs/<slug>.md`.

## Results

| Scenario | Baseline (R+C+I) | Raci (R+C) | Terminal state | Informed's reaction | Concur (3x, cold) |
|---|---|---|---|---|---|
| audit-log-retention | escalated_to_human | escalated_to_human | SAME | **NEW** | DO NOT CONCUR ×3 (consistent, but raci was already escalated — not decisive) |
| llm-inference-hosting | escalated_to_human | **converged** | **DIFFERS** | **NEW** | DO NOT CONCUR ×3 (consistent, and **diverged from a clean converge**) |

## Findings

**1. In both scenarios, the role formally excluded from having a voice had something real to say.**
The redundancy judge called Informed's withheld reaction `NEW` — not a restatement of what
Responsible/Consulted already raised — in both trials, including the "expected-safe" one. That's 2 for
2 against the premise that Informed's silence costs nothing.

**2. In the deliberately stress-tested scenario, that lost concern was also decisive.** With Security
Reviewer excluded from `llm-inference-hosting`'s contest round, the same proposal and revision that
escalated when Security Reviewer participated instead converged cleanly. The withheld concern — "the
platform loses direct control over the infrastructure, making it harder to implement and audit security
measures" — was real (judged `NEW`) and its absence flipped the terminal outcome, not just theoretically
reduced coverage.

**3. The "expected-safe" scenario is not actually evidence that exclusion is safe — it's inconclusive.**
`audit-log-retention`'s terminal state didn't change when Performance Reviewer was excluded, but not
because their concern was redundant (the judge called it `NEW` there too) — only because two unrelated
items (an immutability/operational-burden objection from Backend Developer and a GDPR/compliance
Question from Architect) were already enough to escalate regardless. Across both scenarios, this PoC
found one clear case of participation restriction causing harm, and zero cases that actually
demonstrated it was safe — the second scenario just failed to test the question cleanly, because other
blocking items masked whether the excluded concern would have mattered on its own.

**4. Inside baseline's `llm-inference-hosting` run, the per-raiser recheck overrode the classifier's own
initial call.** Round-1 classification tagged both of Security Reviewer's items `[NON-BLOCKING]`, but
the later targeted recheck — the same "ask the specific raiser, not a generalist" mechanism validated in
`poc-decision-making.md` and `poc-question-gating.md` — still returned `NOT RESOLVED` for that role's
concern against the revision, and this contributed to escalation despite the initial non-blocking tag.
Not a new mechanism introduced here, but a property of the inherited lifecycle worth naming: the
per-raiser recheck functions as a real check on the classifier's own judgment, not a rubber stamp of it.

**5. Concur only got a genuinely informative test in one of the two scenarios — and passed it.** The
sharp claim ("does Concur ever block an already-clean outcome") is only testable when raci actually
converges cleanly, which happened in exactly one scenario here. There, Release Manager's cold,
domain-scoped review ("safe to deploy and roll back") consistently said `DO NOT CONCUR` across all 3
reruns, citing a missing rollback-safety and operational-readiness plan — a *different* gap from the one
participation-exclusion had already lost (Security Reviewer's security/blast-radius concern). Two
independently real gaps in the same "converged" decision, caught by two different mechanisms, neither of
which would have caught the other's gap. In `audit-log-retention`, Concur's `DO NOT CONCUR` was
consistent with the mechanism's own already-escalated verdict but added no incremental information —
real, but uninformative about whether Concur earns its keep.

**6. Consistency held in both scenarios: 3/3 identical verdicts each, at this project's standard
temperature (0.3).** No scattershot in this small sample — necessary, not sufficient, for trusting
Concur's verdict as a real signal rather than model noise.

## Verdict

The evidence here leans against restricting contest participation by RACI letter without a safety net:
the one scenario built specifically to stress it showed real harm (a genuine concern silently lost,
changing escalated to converged), and the "control" scenario never actually demonstrated safety — it
just failed to test the question because other issues already forced escalation. Concur, tested sharply
in the one scenario where it could be, caught a second, independent real gap beyond what restoring
participation would have found — promising, but n=1 for the decisive case, nowhere near enough to call
validated.

If this mechanism moves forward, the shape suggested by this PoC's own results is closer to: Informed
still gets asked (a cheap, async reaction, matching what this PoC's shadow-reaction step already does),
just not looped into the classify/revise/recheck cycle — a redundancy check before silence, not silence
by default. And Concur, rather than a blanket addition, should be scoped exactly the way the user's own
framing argued for it before this PoC ran: specific governance gates (architecture approval, security
review, release go/no-go, production deployment, exceptions), not every category.

## Scope limitations of this PoC

- Two scenarios, one trial each for the baseline/raci comparison and the redundancy judgment (Concur
  alone got 3 reruns) — same small-n limitation acknowledged in every prior PoC in this series.
- Single model plays every role; model capability and role-tiering effects on either claim are untested.
- Only one of two scenarios reached the actual precondition for testing Concur's sharp claim (a clean
  raci convergence) — a next run should deliberately engineer more scenarios that reliably converge via
  R+C alone, to get more replicates specifically on Concur's divergence behavior.
- "Did the terminal state differ" is a weak proxy for participation safety, as Finding 3 shows directly
  — it can read `SAME` even when the excluded role held a real, independently-judged-`NEW` concern,
  merely because other items already forced the same outcome. A better design would count how many
  raised items were actually load-bearing for the final state, not just compare the state itself.
- The redundancy judgment (`NEW` vs. `REDUNDANT`) and the Concur verdict are each a single LLM call,
  ungraded by an independent second reviewer — the same manual/single-grader caveat every PoC in this
  project carries.
- The RACI letter assignment per scenario was authored by this PoC's own code, not derived from any
  external authority table (docs/design/decision-making.md's owner table, or the user's proposed
  12-activity governance matrix) — a different assignment could plausibly change which concerns end up
  Informed and whether the same risk surfaces.

## Candidate write-ups

- **"Informed still had something to say — twice."** Both times we asked the role formally excluded
  from having a voice, an independent judge found its reaction genuinely new, not a restatement of what
  the roles with a voice already covered. Only one of the two times did that concern happen to change
  the final outcome — but neither scenario actually showed exclusion was safe.
- **"The clean convergence wasn't clean."** The one time the RACI-restricted mechanism converged without
  any escalation, two separate things it should not have missed were in fact missing — one findable only
  by asking the excluded role anyway, the other findable only by a completely uninvolved reviewer asked
  one cold yes/no question.
- **"Two gaps, two mechanisms, one 'converged' decision."** Neither restoring the excluded role's voice
  nor adding the Concur gate alone would have caught both real gaps in `llm-inference-hosting` — this
  run's evidence is that you needed both checks to see the whole picture, not either one on its own.
