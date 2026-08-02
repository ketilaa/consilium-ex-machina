---
name: prompt-engineering
description: Evidence-based rules for writing agent-role prompts and parsing their responses (verdicts, tags, structured decisions) — distilled from this repo's PoC experiments. Use when writing/reviewing a system prompt for an agent role, or writing code that reads a model's response to make a decision (classify, gate, converge, block).
---

# Prompt engineering: PoC-tested rules

Generic, model-agnostic. Each `<when, do>` rule cites the PoC doc it's grounded in, where one applies.

## Writing the prompt

- When defining an agent role, give it a specific, opinionated mandate rather than a generic instruction — framing alone measurably improves output (`poc-decision-making.md`).
- When you need genuine pushback, don't rely on "be adversarial/skeptical" wording — a role told to find flaws defaults to polite hedging unless given something concrete to react to (`poc-decision-making.md`).
- When a check must actually block something, feed it (or require) a concrete, scenario-grounded objection, not a generic concern — vague concerns get waved through regardless of instruction tone (`poc-decision-making.md`).
- When a mechanism must act on a choice between outcomes, force a discrete decision via a small, fixed set of literal leading tokens — don't infer intent from free prose (`poc-questions.md`).
- When rechecking whether something is resolved, ask the specific party that raised it about only its own item — a generalist reprocessing the whole list anchors on the original verdict instead of re-deriving it (`poc-decision-making.md`, `poc-question-gating.md`).
- When a recheck must distinguish a real answer from a deferral, state explicitly that a deferral or plausible guess doesn't count as resolution (`poc-question-gating.md`).
- When one generalist pass might miss things, run the same request through several distinct role mandates — but only above a capability floor, since a weaker model gains nothing from more angles (`poc-questions.md`).
- When a category of concern genuinely matters, name the domain/stakeholder/edge case explicitly in the prompt — no framing invents a category the wording never gestures toward (`poc-questions.md`).
- When an invariant must hold structurally (e.g. "only external confirmation resolves this"), encode it as a flag your code controls, never as "the model's re-classification eventually agreed" (`poc-question-gating.md`).
- When granting permission to raise concerns, bound it explicitly ("only if genuinely missing/material") — this held with no false positives at the model tier tested, so re-validate at whatever tier you deploy (`poc-questions.md`).

## Parsing responses

- When parsing model output for a decision, never gate logic on an exact literal string match — formatting variance (a colon inside a bracket, markdown bold around a verdict) silently breaks it with no error (`poc-question-gating.md`).
- When matching a tag or keyword, match on the prefix, tolerant of surrounding punctuation/markup, not the exact expected substring (`poc-question-gating.md`).
- When you fix a tag-parsing bug, treat it as provisional, not solved — the same bug shape recurred in new code right after being named once already (`poc-question-gating.md`).
- When writing a new tag/verdict parser, add a test with deliberately malformed model output.
- When a decision needs to be trustworthy, prefer forced structured/tool-call output over free-text tag scanning — untested here so far, but motivated directly by the repeated parsing failures above (`poc-question-gating.md`).
- When asking for a resolved/not-resolved verdict, source it from the narrowest possible targeted question, not a generalist reprocessing everything (`poc-decision-making.md`, `poc-question-gating.md`).
- When a response fails the expected protocol, read it before discarding it — protocol failure and being substantively wrong are different problems with different fixes (`poc-questions.md`, `poc-question-gating.md`).
- When trusting a parser, validate it against real transcripts, not just the requested format — reading raw output is what caught every parsing bug found here (`poc-question-gating.md`).
