# PoC Learning: Do Context Packets Beat Full-Dump and No-Context?

Parent context: [docs/high-level-architecture.md](../high-level-architecture.md), which floats
Context Packet construction as possibly more important than prompt engineering, and names
"explicit rule-based selection" as a cheaper alternative to embeddings/RAG.

## Objective

Every other PoC so far handed agents a hand-written context blob. A real platform has to
*construct* that automatically from a repository, and there was no evidence yet on whether a
scoped, automatically-assembled packet gives an agent what it needs, or quietly omits the thing
that mattered. sw-foundry has no code of its own to test against, so this PoC builds a small
synthetic-but-realistic codebase with known ground truth and tests three conditions on the same
model: no context, a full-repo dump, and a rule-based Context Packet.

The question: **does a small, deliberately scoped packet produce answers as good as dumping the
whole codebase — and does "just dump everything" hold up operationally once the codebase is
non-trivial?**

## Method

**Corpus** (`proof-of-concept/context-packets/sample_repo/`): a 17-file synthetic "expense
approval service" — models, API handlers, an HTTP client wrapper, notification/audit/repository
modules, tests, and docs — with real cross-cutting facts deliberately buried in comments,
docstrings, and a regression test rather than stated up front (a retry convention motivated by a
named incident, an inclusive-boundary rule tied to a past bug, a crash-safety reason audit writes
must be synchronous, a hard-delete-vs-soft-cancel distinction). Five files are deliberate
distractors: plausible-sounding by name, not needed for any task (`legacy_importer.py`,
`metrics.py`, `employee_directory_client.py`, `rate_limiter.py`, `notification_templates.py`).

Corpus size was checked empirically against both models' actual tokenizer via llama.cpp's
reported `prompt_tokens`, not estimated: **the full dump measures 7,940–8,046 tokens**, right at
the edge of the 7B model's 8,192-token context window — enough to leave essentially no room for a
real answer once a system prompt, task text, and completion budget are added, while sitting
comfortably inside the 14B model's 16,384-token window.

**Tasks** (`tasks.py`): four engineering questions against the corpus, each with a **required-facts
list and a relevant-files ground truth list, written before any run** — same discipline as the
decision-making PoC. Two ask for an implementation; two ask "why/what already exists."

**Context Packet builder** (`packet_builder.py`): the cheap, explicit, no-embeddings option —
keyword overlap between the task text and each file's own signature (filename words + docstring +
top-level function/class names, via `ast`), plus one hop of local import dependencies from
whatever matched, plus a fixed always-included file (`conventions.md`). No LLM calls involved in
building a packet.

**Conditions, same model held constant per comparison so context is the only variable:**
1. **None** — task only, explicitly told no codebase was shown.
2. **Full dump** — every corpus file concatenated in.
3. **Packet** — the rule-based selection above.

Primary comparison ran all three on **Qwen2.5-Coder-14B-Instruct**. A bonus comparison re-ran
**full dump** and **packet** on **Qwen2.5-7B-Instruct** specifically to test the context-window
claim. Every answer capped at 700 completion tokens; every transcript, including the packet
builder's file selection per task, is committed under
`proof-of-concept/context-packets/runs/<task-slug>/`.

## Results

**Packet-builder selection** (measured before any model call — pure static analysis):

| Metric | Result |
|---|---|
| Required files missed (across all 4 tasks) | 0 |
| Deliberate distractor files ever selected (across all 4 tasks) | 0 of 5 |
| Average packet size vs. full dump | ~59% of full-dump tokens (range 47–70%) |

**Required-facts coverage** (graded by reading every transcript against the pre-registered rubric;
13 required facts total across the 4 tasks):

| Condition | Facts covered | Truncated? |
|---|---|---|
| None (14B) | 0 / 13 | No — but never invented fake specifics either |
| Full dump (14B) | ~11.5 / 13 | No |
| Packet (14B) | ~11.5 / 13 | No |
| Full dump (7B, bonus) | ~5 / 13 | **Yes — 4 of 4 tasks** |
| Packet (7B, bonus) | ~11.5 / 13 | No — 0 of 4 tasks |

Every single full-dump run on the 7B model hit the hard context ceiling: completion stopped at
146, 150, 163, and 178 tokens respectively (requested: 700), with `prompt_tokens + completion_tokens`
landing at exactly 8192 in every case — not a natural stopping point, a wall. Every packet run on
the same model completed naturally (610–631 tokens), and in one task (`silent-notification-failure`)
produced the single most detailed, complete answer of any condition in the whole PoC — including
actual source snippets and the internal function name that names the failure mode.

## Findings

**1. On the model that can actually fit full-dump, the packet matches it — at 41% less context on
average.** Required-facts coverage was statistically indistinguishable between full-dump and
packet on the 14B model across all four tasks. The packet is not a lossy compression of full-dump
here; it's the same signal at meaningfully lower cost.

**2. On the model that can't fit full-dump, the packet is the only one that works at all.** This is
the sharpest result in the PoC: the *identical* 7B model produced complete, high-quality answers
under the packet condition and truncated, incomplete answers under full-dump — every single time.
This reframes "Context Packets are nice for token efficiency" into "Context Packets are what makes
a cheaper model viable at all" — a materially stronger claim, and the one the architecture doc's
"may be more important than prompt engineering" line was actually gesturing at.

**3. The failure mode is silent unless you check the numbers.** A truncated full-dump answer
doesn't look broken — it reads as a normal, confident, plausible-sounding response that simply
stops. `full_dump_7b`'s answer to `cancel-endpoint` ends mid-code-block with no error, no warning,
nothing that would flag it as incomplete to a human skimming it. Only checking
`completion_tokens` against the requested budget (or noticing `total_tokens` lands exactly on
`n_ctx`) reveals it. A platform that swallows this silently would produce confidently wrong
guidance without any signal that something went wrong.

**4. The rule-based selector's recall is what actually matters here, and it was perfect — its
precision is mediocre, and that's a real, separate finding.** It never missed a required file and
never admitted a deliberate distractor, across all 4 tasks. But the one-hop import expansion
cascades hard in a tightly-coupled codebase: selecting almost any core module pulls in most of the
rest of the core module set via imports, so "scoped" here means "excludes what's genuinely
irrelevant," not "includes only what's minimally needed." Worth naming honestly rather than
reporting the precision number as if it were high.

**5. Having the right file in context doesn't guarantee the model surfaces the specific fact
buried in it — that depends on how directly the question points at it.** Two required facts
(the INC-482 retry rationale in `reminder-job`, the delete-vs-cancel distinction in
`cancel-endpoint`) were present in every context-bearing condition's selected files but went
unmentioned in most answers, even from the 14B model. The one task that asked directly about the
buried fact (`silent-notification-failure`) got it cited explicitly and correctly in every
non-truncated run. Context construction solves "is the information available"; it doesn't by
itself solve "does the model notice and use the specific detail," which is a distinct problem —
this is the same shape of gap the decision-making PoC found between "the file is in the packet"
and "the fact got used."

## Verdict

This doesn't just fail to kill the Context Packets premise — it's the strongest positive result of
any PoC run so far, and on the load-bearing claim rather than a secondary one. The core mechanism
(cheap, explicit, rule-based selection; no embeddings, no LLM calls to build it) worked well enough
to match full-dump quality at meaningfully lower cost on a capable model, and to be the only
condition that kept a cheaper model functional at all. The two honest caveats — mediocre
selection precision in tightly-coupled code, and buried facts not always surfacing even when
present — are real and worth carrying into the platform design, but neither undermines the central
claim: context construction is not just an efficiency nicety, it's what determines whether a given
model can do the task at all.

## Scope limitations of this PoC

- One run per (task, condition) — no variance data on how consistently full-dump truncates or how
  reliably the packet selects well.
- The corpus is synthetic. It was deliberately built with known ground truth so grading could be
  objective, but a real, organically-grown codebase may have messier, less discoverable
  conventions than the ones written into this one.
- Only the explicit rule-based selector was tested. An embeddings/RAG-based builder — the
  alternative the architecture doc names — was out of scope here and would need its own comparison.
- Grading was manual (me reading every transcript against the pre-registered rubric), same as
  prior PoCs — no independent second grader.
- `top_k` and the stopword list in `packet_builder.py` were set once and not tuned against these
  results, to avoid fitting the heuristic to the test set after seeing the outcome.

## Candidate write-ups

- **"The failure mode that looks like success."** A truncated full-dump answer reads as a normal,
  confident response — nothing about it signals it ran out of room. A piece about silent context
  overflow as a class of bug that won't show up in a spot-check, only in the token accounting.
- **"We didn't build Context Packets to save tokens. We built them so the cheap model could work
  at all."** The reframe from efficiency argument to viability argument — the same small model
  went from useless to excellent purely by changing what it was shown, not by changing the model.
- **"A context packet builder that never once let in a red herring — and still wasn't precise."**
  An honest piece about recall vs. precision in retrieval-adjacent systems: perfect at excluding
  the wrong thing, mediocre at including only the right thing, and why that tradeoff is fine for
  this use case specifically (a stray extra file costs tokens; a missing one costs correctness).
  Import-graph cascades in tightly-coupled code as the concrete mechanism behind the imprecision.
- **"Being in the context isn't the same as being used."** The buried facts that were shown to the
  model and still didn't make it into the answer unless the question pointed straight at them — a
  second, distinct problem from context construction that a real Context Packet system would still
  need to solve.
