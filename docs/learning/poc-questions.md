# PoC Learning: Do Different Roles Surface More Genuine Ambiguity Than One Generalist?

Parent context: [docs/high-level-architecture.md](../high-level-architecture.md)'s "Questions are
first-class citizens" pillar — agents should surface missing information via an explicit Question
rather than fill gaps silently.

## Objective

The specific claim under test, per the user's framing going in: different role mandates — Architect,
Security Reviewer, Backend Developer, and so on — notice different ambiguities in the same request
because each reads it through a different lens (their "perspective and prompt persona"), so a panel
of role-framed reviewers should surface more genuine ambiguity, in total, than one generalist agent
reading the whole request alone. Two failure modes bound the question on either side: missing a real,
consequential gap (silently guessing wrong), and inventing a question about something that was
already fully specified (crying wolf on easy work). Neither is free to test for in isolation, so both
are measured here on the same task set.

## Method

**Tasks** (`tasks.py`), pre-registered before any model call, same discipline as the other two PoCs:

- **5 ambiguous tasks**, each a short, realistic feature request with 2-3 concrete, materially
  consequential gaps — not stylistic nitpicks — each tagged with an *intended* role (the mandate most
  likely to notice it, e.g. Security Reviewer for "can opting out suppress a password-reset email?").
  Grading counts an ambiguity as caught if *any* role raises it, since the thing under test is the
  panel's union, not whether roles hit their assigned item specifically.
- **3 unambiguous control tasks** — fully specified requests (e.g. "add a `GET /health` endpoint
  returning exactly `{"status": "ok"}`, no auth, no DB access") with nothing genuine left to ask,
  used to measure false positives.

**Conditions** (`roles.py`), same spec text held constant per task so framing is the only variable:

1. **Silent baseline** — told to just produce an implementation plan, no mention that asking is an
   option. Models today's default coding-assistant behavior.
2. **Generalist, question-enabled** — one call, no role mandate, explicitly told (per the
   architecture doc's own framing) to raise a Question instead of guessing on genuine, material gaps.
   Forced into a discrete tag: reply starts with exactly `QUESTION:` (one line per distinct gap) or
   exactly `PROCEEDING:` — the same discrete-verdict trick `decisions.py`'s refuter uses
   (`VERDICT: REFUTED`/`NOT REFUTED`), chosen so the ask/proceed decision is mechanically parseable
   rather than inferred from prose.
3. **Role panel, question-enabled** — the identical protocol, run independently per role (Architect,
   Backend Developer, Security Reviewer, Release Manager, Performance Reviewer, Domain Expert), each
   seeing only the spec and its own mandate — no cross-talk, same "contest" shape as
   `decision-making/lifecycle.py`, not a back-and-forth.

**Models**, deliberately tiered like the decision-making PoC: **Qwen2.5-Coder-14B-Instruct** plays the
silent baseline and the generalist; **Qwen2.5-7B-Instruct** plays the six-role panel. The main run
committed to this split; a follow-up (below) re-ran the panel prompts on the 14B model to isolate
model capability from role framing once the main run's numbers made that confound impossible to
ignore.

Full transcripts under `proof-of-concept/questions/runs/<task-slug>.md` (main run) and
`runs/panel_14b_followup.md` (follow-up); mechanical tag parsing plus raw text in `runs/summary.json`.

## Results

**Ambiguity recall, main run** (15 pre-registered ambiguities across 5 tasks; a catch requires the
literal `QUESTION:` tag):

| Task | Silent baseline | Generalist (14B) | Role panel (7B, any of 6) |
|---|---|---|---|
| cancel-order-endpoint | guessed silently | 0/3 ("no blocking ambiguities") | 0/3 |
| expense-reimbursement-multi-currency | guessed silently | 2/3 | 0/3 |
| notification-opt-out | guessed silently | 0/3 | 0/3 |
| bulk-employee-import-duplicates | guessed silently | 1/3 | 0/3 |
| session-timeout-reduction | guessed silently, no value chosen | 1/3 | 0/3 |
| **Total** | 0/15 | **4/15 (27%)** | **0/15 (0%)** |

The role panel's 0/15 is real but misleading — see Finding 3. Reading the same panel transcripts for
substance rather than tag, roughly 5 of 15 ambiguities are visibly named in hedged prose (e.g. "I need
to know the base currency and the source of exchange rates... using the latest exchange rates" —
still tagged `PROCEEDING:`, still followed by a committed guess).

**False positives** (3 unambiguous control tasks, 21 total calls: 3 generalist + 18 panel): zero. Every
condition correctly used `PROCEEDING:` on every control task.

**Follow-up** — same six role-framed prompts, 14B model instead of 7B, run only on the two tasks the
main run missed completely:

| Task | Roles using `QUESTION:` (of 6) | Ambiguities recovered |
|---|---|---|
| cancel-order-endpoint | 5/6 (all but Performance Reviewer) | 3/3 |
| notification-opt-out | 0/6 | 0/3 |

Full transcripts: `proof-of-concept/questions/runs/panel_14b_followup.md`.

## Findings

**1. Same model, only the framing changed, went from 0/3 to 3/3 on the one task retested — the
cleanest evidence for the hypothesis.** On `cancel-order-endpoint`, the 14B generalist (one call, no
role) declared "the request is clear and specifies adding an endpoint... no blocking ambiguities are
present" — a confident miss on all three pre-registered gaps. The identical 14B model, given the same
spec split across six role-framed calls, correctly used `QUESTION:` in five of six and the union
covered all three ambiguities — including the Security Reviewer landing exactly on its own intended
item ("What level of authorization will be required...", "What kind of audit or compliance logging
will be implemented..."). Nothing changed except how many times the model was asked and from what
angle.

**2. But that gain is gated on a capability floor the panel doesn't clear on its own.** The main run's
7B panel never used the `QUESTION:` tag once, across 30 calls covering all 5 ambiguous tasks — 0%,
against the 14B generalist's 27% using the same tag correctly on its own. Swapping six role prompts
onto a weaker model didn't multiply perspective, it multiplied a fixed failure to commit to a
discrete Question by six, at six times the cost. Whatever "different roles catch different things"
buys, it isn't available for free from any model tier.

**3. The weak model's silence isn't blindness — it's a broken protocol sitting on top of real signal.**
Reading the 7B panel's prose rather than trusting its tag, several roles visibly named the actual gap:
"I plan to calculate the total... converting the total to a single currency (e.g., the company's base
currency)... *the specific currency to which the total should be converted and the source of the
exchange rates need to be clarified*" — then proceeds to implement with a specific currency and rate
source chosen anyway, unflagged as an assumption in the same breath it was just flagged as unclear. A
platform that gates its `Question Raised` event on a discrete signal — a tool call, a tag, anything
more structured than free-text parsing — would get zero signal from this entire condition despite the
model visibly knowing better in its own words.

**4. Role mandate is a reasonable prior for who'll catch what, not a reliable filter.** On
`expense-reimbursement-multi-currency`, the "what if the exchange-rate source is unavailable"
ambiguity was pre-assigned to Release Manager (resilience/ops framing) — but the Release Manager's
own response never mentioned it, asking only about the rate source in the abstract. Performance
Reviewer and Domain Expert, neither assigned that item, both raised the unavailability case
unprompted ("how to handle cases where exchange rates are not available or outdated"; "how to handle
expenses without valid exchange rates"). The panel's value came from asking the same request six
differently-angled times, not from the mandate-to-topic mapping being precise — a useful caveat for
anyone tempted to route "which role should review this" as if it were a reliable filter rather than a
diversity mechanism.

**5. One ambiguity was invisible regardless of model tier, framing, or panel size.**
`notification-opt-out` — "let users turn off notifications" not specifying whether that includes
security-critical notifications (password reset, new-device login) — was missed by the silent
baseline, the 14B generalist, the 7B panel, *and* the 14B panel in the follow-up. The Security
Reviewer role, on both model tiers, explicitly and confidently ruled out any issue "related to attack
surface, authorization and access control, credential handling, blast radius of compromise, or
audit/compliance exposure" — stated with full confidence in exactly the seat meant to catch it. The
other four ambiguous tasks all had a concrete domain state that's naturally salient once you engage
with the topic at all — a shipped order, a stale exchange rate, a duplicate employee ID, an
already-active session. "Turn off notifications" has no comparable lexical hook suggesting there's a
category of notification not being considered. This is the same shape of gap the context-packets PoC
found between "the fact is in context" and "the model notices it" — sharpened here to: role framing
doesn't compensate for an ambiguity the request's own wording gives no foothold toward.

**6. Cost is real, and the payoff is not evenly distributed.** The panel is six calls per task against
one for the generalist — a heavier multiplier than the ~2.5-3x the decision-making PoC measured for
its lighter lifecycle. Here it produced a decisive win in one case (`cancel-order-endpoint`, 14B tier)
and nothing in another (`notification-opt-out`, at any tier) on the same cost. "When is a panel worth
paying for" doesn't have a clean answer yet from this evidence — it looks tied to whether the request
text gives any lexical foothold toward the missing category at all, not to how consequential the gap
actually is.

**7. Zero false positives, for what a 3-task sample is worth.** Both the generalist and the full
six-role panel correctly proceeded on all three fully-specified control tasks, 21 calls total, with no
invented questions anywhere. Whatever this PoC's recall problems are, "crying wolf on easy work" —
the first thing anyone designing a Questions mechanism worries about — was not observed. The sample is
small enough that this should be read as "not yet falsified," not "solved."

## Verdict

Mixed, and more informative for being mixed. The user's hypothesis holds, cleanly, at least once: same
model, only the framing varied, recall went from 0/3 to 3/3. But the gain is conditional on the model
already being capable enough to follow the ask/proceed protocol in the first place — the panel does
not make a weaker model more perceptive, it makes its existing failure to commit six times more
expensive. And neither more perspectives nor a stronger model recovered the one ambiguity that the
request's own wording gave no hint toward — a different, harder problem than "give it more angles,"
one this PoC wasn't built to solve and shouldn't be read as having tested.

## Scope limitations of this PoC

- One run per (task, condition, role), and Qwen was called at nonzero temperature (0.3) — no variance
  data. A standalone smoke-test call on `cancel-order-endpoint`'s generalist prompt, made before the
  committed run with the same system/user text (a lower `max_tokens`, 400 vs. 500, is the one
  difference), returned `QUESTION:` with four concrete questions; the committed run's own call on the
  same prompt returned `PROCEEDING:`. That's suggestive, not conclusive proof of run-to-run
  instability given the parameter difference, but it's consistent with one and should not be ignored.
- The model-vs-framing confound (Finding 2) was isolated for only 2 of the 5 ambiguous tasks — the two
  the main run missed outright. Whether the panel-beats-generalist result generalizes to the other
  three (expense-reimbursement, bulk-import, session-timeout) on the 14B tier is untested.
- The task set and its "genuine ambiguity" / "intended role" labels are this PoC's own invention, built
  with known ground truth for gradability, not drawn from a real backlog.
- Grading of "substantive but mistagged" panel catches (Finding 3) required reading prose, same manual
  discipline as the other two PoCs — no independent second grader.
- This PoC stops at "is the ambiguity raised." Whether a raised Question actually blocks a dependent
  Decision or task — the mechanism half of "Questions are first-class citizens" — is untested here.

## Candidate write-ups

- **"We asked the same model the same question six times, from six angles, and it caught what one
  call missed completely."** The cleanest, most attention-grabbing result in the PoC: identical model,
  identical spec, 0/3 to 3/3 recall purely from role framing — worth leading with, with the honest
  caveat (Finding 2) attached rather than sold as unconditional.
- **"The panel had the right answer in its own words — and buried it under the wrong tag anyway."** A
  piece about a subtler failure mode than "didn't notice": noticing, saying so in plain language, and
  then still proceeding to guess in the same breath — a warning for anyone building a Question
  mechanism on top of free-text parsing instead of a forced, structured decision.
- **"Six specialists agreed unanimously — and were unanimously wrong."** The `notification-opt-out`
  case: every role, every model tier, including the Security Reviewer explicitly clearing "attack
  surface... credential handling," missed that opting out of notifications might silence a
  password-reset email. A concrete example of consensus signaling nothing when every reviewer shares
  the same blind spot, tying back to the "false convergence" failure mode the decision-making PoC
  named for a different mechanism.
- **"Ask the mandate that matches, and it stayed quiet. Ask the one that doesn't, and it caught it
  anyway."** The Release-Manager-assigned exchange-rate-unavailability gap, caught instead by
  Performance Reviewer and Domain Expert. Evidence that panel value comes from diversity of attempts,
  not from correctly routing topics to the "right" specialist.
