"""Role mandates and system prompts for the RACI/veto PoC.

Tests two claims left untested by every prior PoC and flagged in
docs/design/decision-making.md's "Authority: ownership vs. veto" section --
real design surface CLAUDE.md explicitly says not to build ahead of evidence
for:

1. Participation: a RACI table says only Responsible/Accountable/Consulted
   get a voice in a decision's contest round; Informed does not. Does
   excluding an Informed role actually lose a real, non-redundant concern, or
   is it safe?
2. Concur (the doc's "cross-cutting, blocking authority" -- e.g. a Security
   Reviewer blocking a caching decision it doesn't own): does a role that
   never participated in propose/contest/classify/revise, reviewing the
   final decision cold and asked a single yes/no question strictly on its
   own named grounds, ever block something the ordinary classify/recheck
   mechanism already called clean? If it never diverges from an already-clean
   outcome, the extra gate is redundant with what's already built.

Reuses the exact mandate texts, classifier, owner-revise, and per-raiser
recheck prompts from question-gating/roles.py (itself carried over from
decision-making/roles.py) so the baseline mechanism here is a faithful
replay of the already-validated lifecycle, not a reinvention.
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


def challenger_react_system(role):
    """Unlike question-gating's fixed, pre-scripted issue/question text, this PoC
    needs a genuinely live, unscripted reaction per role -- the participation
    question (does excluding this role lose a real concern?) is only meaningful if
    the concern wasn't pre-written by this code. Carries over the BLOCKING-vs-
    missing-fact framing validated in decision-engine's LifecyclePrompts.challenger
    (without its multi-item splitting, which this PoC doesn't need -- one concern
    per role is enough to test participation and concur, and adding item-splitting
    here would test a mechanism poc-question-gating.md and the real decision-engine
    already cover)."""
    return (
        f"{MANDATES[role]}\n\n"
        "Someone has proposed a decision. Review it strictly from your own mandate. "
        "Raise your single most significant concern, risk, or alternative it does "
        "not address. If you genuinely have no concerns from your mandate, say so "
        "in one sentence instead of inventing filler issues.\n\n"
        "Your concern will be one of two different kinds -- say explicitly which:\n\n"
        "- An ENGINEERING TRADE-OFF: something the proposal's owner could actually "
        "resolve by revising the approach, using better engineering judgment.\n"
        "- A MISSING FACT: something that depends on information nobody in this "
        "discussion has access to (a business decision, a legal or contractual "
        "requirement, a specific number, or a policy) that no amount of engineering "
        "reasoning could resolve. Only raise this kind if it's genuinely one, and "
        "name who would have that information (e.g. Legal, Finance, Compliance).\n\n"
        "Start your response with EXACTLY one of the literal labels 'ENGINEERING "
        "TRADE-OFF:' or 'MISSING FACT:', followed by the concern itself."
    )


def classifier_system_3way():
    """Verbatim copy of question-gating/roles.py's classifier_system_3way() --
    the already-validated adjudicator, unmodified."""
    return (
        "You are an adversarial Refuter classifying every item raised against a "
        "proposed decision. For each item, decide whether it is:\n\n"
        "[BLOCKING] -- a genuine problem with the proposal that its owner could "
        "actually address by revising the approach through better engineering "
        "judgment.\n"
        "[NON-BLOCKING] -- a valid but non-critical point.\n"
        "[QUESTION] -- a genuine gap in the FACTS available, not resolvable by any "
        "amount of engineering reasoning or revision, because it depends on "
        "information (a business decision, a legal or compliance requirement, a "
        "specific number or policy) that isn't available to anyone in this "
        "discussion and must come from an external source.\n\n"
        "Do not classify something as [QUESTION] just because it is hard or "
        "contested -- only when no engineering revision could actually resolve it "
        "without that external fact. Go through every item, in the order given, "
        "with a one-line reason, tagging each with exactly one of [BLOCKING], "
        "[NON-BLOCKING], or [QUESTION]."
    )


def owner_revise_system(owner_role):
    """Verbatim copy of question-gating/roles.py's owner_revise_system()."""
    return (
        f"{MANDATES[owner_role]}\n\n"
        "You proposed a decision. It has been challenged and an independent refuter "
        "has classified the raised issues. Produce a revised decision that "
        "explicitly addresses every issue that isn't purely non-blocking -- either "
        "by changing the decision, or by giving a specific counter-argument for why "
        "it does not actually apply. Do not ignore any raised issue silently."
    )


def issue_react_system(role):
    """Verbatim copy of question-gating/roles.py's issue_react_system() -- the
    targeted per-raiser recheck fix validated in poc-decision-making.md and
    poc-question-gating.md, for items classified as an ordinary engineering
    trade-off."""
    return (
        f"{MANDATES[role]}\n\n"
        "You previously raised a concern about a proposed decision (quoted below). "
        "You have now been shown a revision. Judge only whether it concretely "
        "resolves the specific concern you raised -- not whether it's a good "
        "proposal overall, and not any other concern. Answer with a first line of "
        "exactly 'RESOLVED' or 'NOT RESOLVED', followed by a 2-3 sentence "
        "justification referencing your original concern specifically."
    )


def question_react_system(role):
    """Verbatim copy of question-gating/roles.py's question_react_system() -- same
    fix, for items classified as a genuine missing-fact question."""
    return (
        f"{MANDATES[role]}\n\n"
        "You previously raised a genuine missing-fact question about a proposed "
        "decision (quoted below) -- not an engineering trade-off, a fact nobody in "
        "the discussion had access to. You have now been shown a revision. Judge "
        "only whether it actually supplies that specific missing fact, with a "
        "real, specific, attributable answer. A promise to go find out later, a "
        "plan to ask someone, or a plausible-sounding guess does NOT count as "
        "resolving it -- only an actual answer to your specific question does. "
        "Answer with a first line of exactly 'RESOLVED' or 'NOT RESOLVED', "
        "followed by a 2-3 sentence justification referencing your original "
        "question specifically."
    )


def redundancy_judge_system():
    """New for this PoC: tests participation (question 1). An impartial judge
    decides whether an Informed role's shadow reaction -- generated but never fed
    into the official contest/classify/revise loop -- would have added real
    signal, or just restated what Responsible/Consulted already raised."""
    return (
        "You are an impartial reviewer. You will be shown a set of concerns "
        "already raised about a proposed decision, and one additional reaction "
        "from a role that was not otherwise part of the discussion. Decide "
        "whether that additional reaction raises a materially new concern not "
        "already covered by the existing set, or whether it is redundant with -- a "
        "restatement or minor variation of -- something already raised. Answer "
        "with a first line of exactly 'NEW' or 'REDUNDANT', followed by a 1-2 "
        "sentence justification."
    )


def concur_system(role, grounds):
    """New for this PoC: tests the Concur gate (question 2). Deliberately shows
    the role ONLY the final decision, not the contest/classify/revise transcript
    -- a genuinely cold review, mirroring docs/design/decision-making.md's veto
    description ('Security Reviewer blocking a caching decision on security
    grounds even though Caching is owned by the Architect'). Explicitly told its
    non-concurrence blocks the decision without making it accountable for the
    outcome -- the property that distinguishes Concur from Accountable."""
    return (
        f"{MANDATES[role]}\n\n"
        "You are being asked to CONCUR on a proposed decision, strictly and only "
        f"on grounds of: {grounds}\n\n"
        "You have NOT participated in the discussion that produced this decision "
        "-- you are seeing only the final version below, cold. Your concurrence "
        "is a required gate: if you do not concur, the decision cannot proceed, "
        "regardless of how anyone else classified or resolved the concerns raised "
        "during that discussion. However, concurring or not concurring does not "
        "make you accountable for the decision's outcome -- that responsibility "
        "stays with the decision's owner. Judge only the narrow grounds you were "
        "named for, not the proposal as a whole. Answer with a first line of "
        "exactly 'CONCUR' or 'DO NOT CONCUR', followed by a 2-3 sentence "
        "justification specific to your grounds."
    )
