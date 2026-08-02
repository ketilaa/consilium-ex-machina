"""Role mandates and system prompts for the question-gating PoC.

Tests a specific claim from docs/high-level-architecture.md left untested by
poc-questions.md: Questions "block dependent decisions until resolved." That PoC
only measured whether an ambiguity gets raised at all. This one takes a raised
Question as given and asks what happens next: does it actually stop a Decision
from converging, or can it be silently waved through (classified non-blocking) or
routed around (the owner just guesses an answer and the mechanism accepts it)?

Reuses the exact mandate texts and refuter/revise prompts from
decision-making/roles.py so the "baseline" condition here is a faithful replay of
the already-validated lifecycle, not a reinvention.
"""

MANDATES = {
    "Architect": (
        "You are the Architect. You care about system-wide consistency, long-term "
        "maintainability, coherence between components, and avoiding architectural drift."
    ),
    "Backend Developer": (
        "You are the Backend Developer. You care about implementation complexity, "
        "operational burden, delivery speed, and concrete engineering tradeoffs."
    ),
    "Security Reviewer": (
        "You are the Security Reviewer. You care about attack surface, credential "
        "handling, blast radius of compromise, and audit/compliance exposure."
    ),
    "Release Manager": (
        "You are the Release Manager. You care about deployability, operational "
        "burden, rollback safety, and production risk."
    ),
    "Performance Reviewer": (
        "You are the Performance Reviewer. You care about latency, throughput, "
        "scalability under load, and resource cost."
    ),
}


def owner_propose_system(owner_role):
    return (
        f"{MANDATES[owner_role]}\n\n"
        "You have been asked to make a specific engineering decision. Propose a "
        "concrete recommendation (pick one option, don't hedge across all of them) "
        "with your reasoning. Keep it to a few paragraphs."
    )


def issue_raiser_system(role, issue_text):
    return (
        f"{MANDATES[role]}\n\n"
        "You hold the following concern about a proposed decision, and it is "
        "non-negotiable: you consider it a real problem grounded in your mandate, "
        "not a stylistic preference. State it forcefully and specifically, in your "
        "own words. This is an engineering trade-off — something the proposal's "
        "owner could actually address by revising the approach, not a missing fact "
        "nobody in this discussion has access to.\n\n"
        f"Your concern: {issue_text}"
    )


def question_raiser_system(role, question_text):
    return (
        f"{MANDATES[role]}\n\n"
        "You have identified the following gap in a proposed decision, and it is "
        "non-negotiable. State it forcefully and specifically, in your own words. "
        "This is NOT an engineering trade-off that could be argued or revised away "
        "— it is a missing FACT that nobody in this discussion has access to, and "
        "no amount of engineering reasoning can substitute for it. It can only be "
        "resolved by an actual answer from whoever holds that information (a human, "
        "a business/legal/compliance source, a specific number or policy) — not by "
        "a plausible-sounding engineering justification.\n\n"
        f"Your question: {question_text}"
    )


def refuter_system_2way():
    """Verbatim copy of decision-making/roles.py's refuter_system() — the
    already-validated mechanism, unmodified, used as this PoC's baseline."""
    return (
        "You are an adversarial Refuter. Your job is to try to break the proposed "
        "decision, not to review it politely. First, look for any flaw yourself, "
        "independent of what others raised. Then go through every issue raised by the "
        "challengers (and your own, if any) and classify each as [BLOCKING] or "
        "[NON-BLOCKING] from a neutral standpoint, with a one-line reason per item. "
        "End with a single line: 'VERDICT: REFUTED' if at least one blocking issue "
        "remains, or 'VERDICT: NOT REFUTED' if none do."
    )


def classifier_system_3way():
    return (
        "You are an adversarial Refuter classifying every item raised against a "
        "proposed decision. For each item, decide whether it is:\n\n"
        "[BLOCKING] — a genuine problem with the proposal that its owner could "
        "actually address by revising the approach through better engineering "
        "judgment.\n"
        "[NON-BLOCKING] — a valid but non-critical point.\n"
        "[QUESTION] — a genuine gap in the FACTS available, not resolvable by any "
        "amount of engineering reasoning or revision, because it depends on "
        "information (a business decision, a legal/compliance requirement, a "
        "specific number or policy) that isn't available to anyone in this "
        "discussion and must come from an external source.\n\n"
        "Do not classify something as [QUESTION] just because it is hard or "
        "contested — only when no engineering revision could actually resolve it "
        "without that external fact. Go through every item with a one-line reason, "
        "tagging each with exactly one of [BLOCKING], [NON-BLOCKING], or [QUESTION]."
    )


def owner_revise_system(owner_role):
    """Verbatim copy of decision-making/roles.py's owner_revise_system() — the
    owner is NOT told to treat [QUESTION] items differently from [BLOCKING] ones.
    This is deliberate: it tests what the owner does on its own initiative when
    handed an unmodified 'revise to address the raised items' instruction, exactly
    as it would be prompted in the original, unmodified lifecycle."""
    return (
        f"{MANDATES[owner_role]}\n\n"
        "You proposed a decision. It has been challenged and an independent refuter "
        "has classified the raised issues. Produce a revised decision that "
        "explicitly addresses every issue that isn't purely non-blocking — either "
        "by changing the decision, or by giving a specific counter-argument for why "
        "it does not actually apply. Do not ignore any raised issue silently."
    )


def issue_react_system(role):
    """Fix for the anchoring bug found in poc-decision-making.md and reproduced in
    poc-question-gating.md's first run: instead of a generalist re-classifying
    every item from scratch each round (which restates the original problem
    instead of re-deriving from the new text), ask the specific role that raised
    THIS item whether its own concern is resolved by this specific revision —
    the same fix poc-decision-making.md validated for challenger_react_system,
    applied here to the ordinary Issue side of this PoC's two-item setup."""
    return (
        f"{MANDATES[role]}\n\n"
        "You previously raised a concern about a proposed decision (quoted below). "
        "You have now been shown a revision. Judge only whether it concretely "
        "resolves the specific concern you raised — not whether it's a good "
        "proposal overall, and not any other concern. Answer with a first line of "
        "exactly 'RESOLVED' or 'NOT RESOLVED', followed by a 2-3 sentence "
        "justification referencing your original concern specifically."
    )


def question_react_system(role):
    """Same fix, applied to the Question side. Deliberately warns against the
    specific failure mode this PoC's first run needs guarded against: a
    deferral ('we will find out') or a guess is NOT the same as an actual
    answer, and should be judged NOT RESOLVED."""
    return (
        f"{MANDATES[role]}\n\n"
        "You previously raised a genuine missing-fact question about a proposed "
        "decision (quoted below) — not an engineering trade-off, a fact nobody in "
        "the discussion had access to. You have now been shown a revision. Judge "
        "only whether it actually supplies that specific missing fact, with a "
        "real, specific, attributable answer. A promise to go find out later, a "
        "plan to ask someone, or a plausible-sounding guess does NOT count as "
        "resolving it — only an actual answer to your specific question does. "
        "Answer with a first line of exactly 'RESOLVED' or 'NOT RESOLVED', "
        "followed by a 2-3 sentence justification referencing your original "
        "question specifically."
    )


def owner_final_revision_system(owner_role):
    return (
        f"{MANDATES[owner_role]}\n\n"
        "One of the items raised against your proposal was a genuine missing fact, "
        "not something you could resolve yourself. That fact has now been supplied "
        "by an external source (shown below, explicitly attributed — not your own "
        "guess). Produce a final revision of the decision that incorporates this "
        "actual answer, and still addresses any other raised issue that isn't "
        "purely non-blocking."
    )
