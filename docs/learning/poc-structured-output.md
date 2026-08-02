# PoC Learning: Does Forced Structured Output Eliminate the Tag-Parsing Bug Class?

Parent context: [poc-question-gating.md](poc-question-gating.md) found two independent
tag-parsing bugs of the same shape (`[BLOCKING: reason]` breaking an exact-substring match,
`**RESOLVED.**` breaking a strict prefix match) and proposed, as the next candidate in
`CLAUDE.md`, replacing free-text tag scanning with forced JSON-schema/tool-call output for
these classify/recheck steps.

## Objective

The specific claim to test, stated plainly: does forcing a model to emit schema-validated
JSON instead of a tagged string eliminate the format-fragility bug class entirely, rather
than requiring parsers to be hardened one format variant at a time? A fair test has to
compare structured output against the *already-hardened* free-text parser — the permissive,
markup-tolerant version that came out of `poc-question-gating.md`'s fixes — not the original,
naive parser those bugs were found in. Comparing against the broken version would prove
nothing except that the broken version was broken.

## Method

**Fixtures** (`fixtures.py`): the exact classify and recheck inputs already used and
committed in `proof-of-concept/question-gating/runs/*.md` — 2 classify fixtures (one
Issue + one Question each, ground truth `BLOCKING`/`QUESTION`) and 4 recheck fixtures (the
self-answer-attempt stage, ground truth `NOT_RESOLVED`, and the final stage after a real
external answer, ground truth `RESOLVED`, for both scenarios). Reusing committed content
means this PoC isolates response *format* as the only variable — the same input, classified
or rechecked repeatedly, under two conditions.

**Two conditions**, same model, same prompts in substance:

1. **Freetext** — the fixed parser from `poc-question-gating.md`: prefix-tolerant regex
   matching (`\[BLOCKING\b`, markup-stripped `RESOLVED`/`NOT RESOLVED`), not the original
   exact-substring version that broke twice.
2. **Structured** — `response_format: {"type": "json_schema", ...}`, verified beforehand
   against this repo's local llama.cpp server to genuinely compile the schema into a grammar
   and constrain decoding (not just prompt the model and hope) — confirmed empirically before
   building anything further. Schema requires a `reason` field before the `verdict` enum field
   per item, preserving a chain-of-thought-like scaffold rather than forcing a bare verdict.

**Repeated sampling**: each of the 6 fixtures run **8 times per condition** at the same
nonzero temperature (0.3) used throughout every PoC — unlike prior PoCs' single run per
condition, this one needed actual repetition, since the bugs it's testing for are about
run-to-run *format variance*, which a single sample can't measure at all.

**Bonus stress test**: the same structured recheck call repeated 6 times with a deliberately
tight `max_tokens` (40, too small for the schema's reason + verdict fields) — does grammar
constraint on *what* can be generated next protect against truncation cutting generation off
mid-JSON regardless?

Model: the same single 24B model used throughout `poc-question-gating.md`. Full raw
transcripts: `proof-of-concept/structured-output/runs/results.jsonl` (one line per call);
aggregates: `runs/summary.json`.

## Results

**Parse success and correctness — both conditions, 48 trials each (6 fixtures × 8 reps),
100% and 100%:**

| Metric | Freetext | Structured |
|---|---|---|
| Parse success rate | 48/48 (100%) | 48/48 (100%) |
| Correct verdict rate | 48/48 (100%) | 48/48 (100%) |

Not a single parse failure or incorrect verdict in either condition, across every fixture.

**Cost — structured output consistently costs more, by roughly 1.5-2.6x:**

| Fixture | Freetext tokens / sec | Structured tokens / sec | Token multiplier |
|---|---|---|---|
| classify-audit-log-retention | 66.9 / 8.7s | 137.6 / 18.0s | 2.06x |
| classify-llm-inference-hosting | 59.4 / 8.2s | 142.6 / 19.1s | 2.40x |
| recheck-audit-log-retention (self-answer) | 59.0 / 8.4s | 92.8 / 12.7s | 1.57x |
| recheck-audit-log-retention (final) | 40.9 / 5.5s | 68.9 / 9.2s | 1.68x |
| recheck-llm-inference-hosting (self-answer) | 40.2 / 5.9s | 104.8 / 14.1s | 2.61x |
| recheck-llm-inference-hosting (final) | 54.6 / 7.3s | 85.5 / 11.4s | 1.57x |

Average ≈2x more completion tokens and ≈1.9x more wall-clock time, consistently, across every
single fixture — not a one-off.

**Truncation stress test — 0% success, every time:**

All 6 structured recheck calls at `max_tokens=40` returned `finish_reason: "length"` and
unparseable, truncated JSON. Grammar-constrained decoding controls what the model *can*
generate next; it does not extend how much it's allowed to generate before the completion
budget cuts it off mid-object.

## Findings

**1. On this test, the already-hardened free-text parser matched structured output's
reliability exactly — 100% vs. 100%, zero failures in either condition.** The two tag-parsing
bugs `poc-question-gating.md` found were fixed by hardening the parser (prefix-tolerant
matching, markup-stripping), not by switching formats. Once that hardening was in place, 48
free-text trials produced zero further parse failures — the same result structured output
produced. This PoC does **not** show structured output eliminating a bug class the fixed
free-text parser was still exhibiting, because the fixed parser wasn't exhibiting one anymore
by the time this PoC ran.

**2. Structured output's extra cost is fully explained by generating more tokens, not by
slower constrained decoding.** Computing tokens/second per call rather than raw
completion-token counts: freetext averaged ≈7.28 tokens/sec across all fixtures, structured
averaged ≈7.47 tokens/sec — marginally *faster* per token, within noise. The ~2x wall-clock
cost is not a grammar-compilation tax paid per token; it's that the schema's `reason` field
consistently elicited a fuller, longer justification than the equivalent free-text response
gave for the same task. Concretely: schema-forcing a "reason" slot seems to invite more
complete prose than asking for one line before a tag does.

**3. Structured output is not immune to truncation — and its own extra verbosity (Finding 2)
makes it comparatively *more* exposed to it at a matched token budget.** Every one of 6
stress-test calls with a tight budget came back truncated and unparseable, despite the
schema constraint. A grammar can guarantee the *shape* of what's generated is always valid
JSON-so-far; it cannot guarantee that shape gets *completed* within whatever budget the
caller set. Combined with Finding 2 (structured output needs roughly 2x the tokens for the
same content), a token budget sized correctly for a free-text response is more likely to
truncate a structured one.

**4. The maintainability argument for structured output is real but untested by this specific
design.** This PoC repeated the *same* six fixtures many times — it couldn't discover a novel
future format quirk in free text the way the original two bugs were novel, unplanned
discoveries. The actual case for structured output isn't "it's measurably more reliable on
known inputs" (Finding 1 found no such gap here) — it's "the contract is enforced by the
framework once, instead of a hand-written parser that needs re-hardening every time a model
tries a new formatting variant nobody anticipated," which is a claim about the *unknown
future*, not something a fixed, repeated-fixture test can measure either way.

## Verdict

More complicated than the framing going in. `CLAUDE.md`'s next-candidate note assumed
structured output would "eliminate this whole class of bug" — that's not what this run
shows. What it shows instead: the bug class was already eliminated by hardening the
free-text parser (permissive prefix matching, markup-stripping), and once hardened, free
text held up perfectly across 48 trials, matching structured output's perfect record at
real, measured cost (≈2x tokens and wall-clock time) and a new failure mode of its own
(truncation) that free text is, if anything, less exposed to at a given budget. The honest
takeaway isn't "use structured output" or "don't" — it's that **the actual fix validated by
this whole arc was hardening the parser, not switching formats**, and structured output's
real, still-unproven case is resilience against a *future* format surprise a fixed-fixture
repeated test structurally cannot exercise either way.

## Scope limitations of this PoC

- 48 trials per condition with zero failures either way is not strong evidence the two
  conditions are *equally* reliable — it's only strong evidence neither failed at this
  sample size. The original two bugs this PoC set out to prevent were themselves rare,
  one-off discoveries across many more trials than 8-per-fixture; this sample may simply be
  too small to reproduce a rare failure in either condition.
- Only one model, one temperature setting, and the same six fixtures repeated -- no test of
  whether a different or smaller model shows a reliability gap between conditions that this
  24B model doesn't.
- The truncation stress test used only one fixture and one deliberately-small `max_tokens` --
  a real deployment would rarely set a budget that tight, so the practical frequency of this
  failure mode in normal operation is untested here.
- Cost was measured in tokens and wall-clock seconds only; this PoC didn't measure whether
  the fuller "reason" fields structured output produced were actually *better* reasoning, or
  just longer.

## Candidate write-ups

- **"We built the fix, then accidentally tested whether we still needed it."** The
  free-text parser was already hardened by the time this PoC ran, so it couldn't show
  structured output solving a problem the fixed parser had stopped having. An honest,
  slightly funny story about testing a mechanism after already fixing the thing it was meant
  to fix.
- **"Structured output isn't slower per token -- it just writes more."** The tokens/second
  breakdown ruling out a grammar-compilation tax, isolating the entire cost difference to
  verbosity the schema's own "reason" field invited.
- **"The schema guarantees the shape, not the ending."** Six truncated, unparseable
  structured responses under a tight token budget -- a clean, visual demonstration that
  grammar-constrained decoding is not a truncation-proofing mechanism, and combined with its
  own higher per-call token cost, may need a *larger* safety margin than free text, not a
  smaller one.
