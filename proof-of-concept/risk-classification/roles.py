"""Classifier prompts for the risk-classification PoC.

Tests a specific claim raised while reviewing a real, live decision
(d-22ffab13, "make the agent role registry configurable"): two of its raised
concerns (deprecated-role handling, roles.yaml integrity/tamper-detection)
were, on human review, judged real but disproportionate to the work item's
actual current risk profile ("internal, exploratory engineering platform, no
regulated data") -- not blockers, but not dismissible either. Today's
classifier has no vocabulary for that: an item is BLOCKING, NON-BLOCKING, or
QUESTION. This tests adding a fourth option, RISK, and whether a classifier
given it actually uses it to defer genuinely disproportionate concerns
without also sweeping in concerns that should stay BLOCKING regardless of
risk profile -- the same overshoot failure mode found when Concur's
sufficiency-criterion prompt was tested (proof-of-concept/raci-veto):
telling a model to be proportionate doesn't guarantee it discriminates
correctly, it can just as easily rubber-stamp everything as "acceptable
risk" instead of finding fault with everything.
"""


def classifier_system_3way():
    """Verbatim copy of raci-veto/decision-making's classifier_system_3way()
    -- the baseline, unmodified mechanism. Used here to establish what
    happens to a genuinely disproportionate concern TODAY, with no RISK
    option to sort it into."""
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


def classifier_system_4way_with_risk(risk_profile):
    """The new mechanism under test: adds [RISK] as a fourth classification,
    with three explicit guardrails against the overshoot failure mode --
    (1) RISK requires the concern to be real, not merely inconvenient or
    effortful, (2) a plain correctness defect is NEVER RISK regardless of
    risk profile (it's a category error, not a proportionality judgment),
    and (3) classifying something RISK requires naming a concrete trigger
    condition, not a vague "revisit someday". These guardrails are the thing
    actually under test -- Concur's sufficiency criterion had comparably
    careful guardrail language and still overshot in practice, so stating
    the rule here is not assumed to make the model follow it."""
    return (
        "You are an adversarial Refuter classifying every item raised against a "
        "proposed decision. For each item, decide whether it is:\n\n"
        "[BLOCKING] -- a genuine problem with the proposal that its owner could "
        "actually address by revising the approach through better engineering "
        "judgment, and that matters regardless of the work item's current "
        "maturity or risk profile. Any plain correctness defect (something that "
        "is simply wrong, not a matter of proportionate hardening) is always "
        "BLOCKING or NON-BLOCKING, never RISK.\n"
        "[NON-BLOCKING] -- a valid but minor, non-critical point.\n"
        "[QUESTION] -- a genuine gap in the FACTS available, not resolvable by "
        "any amount of engineering reasoning or revision, because it depends on "
        "information that isn't available to anyone in this discussion and must "
        "come from an external source.\n"
        "[RISK] -- a real, legitimate concern -- NOT merely inconvenient or "
        "effortful to address, and NOT dismissible the way a NON-BLOCKING point "
        "is -- where addressing it right now is genuinely disproportionate to "
        "the work's CURRENT, explicitly stated risk profile below. This "
        "platform evolves one validated piece at a time; prefer RISK over "
        "BLOCKING only when the concrete harm described would only actually "
        "materialize if the risk profile changes in a specific, nameable way.\n\n"
        f"The work this decision belongs to has this current, explicitly stated "
        f"risk profile:\n{risk_profile}\n\n"
        "Do not classify something as [QUESTION] just because it is hard or "
        "contested -- only when no engineering revision could resolve it without "
        "an external fact. Do not classify something as [RISK] merely because it "
        "is inconvenient or effortful to address now, and never for a plain "
        "correctness defect regardless of risk profile -- only when addressing "
        "it now is genuinely disproportionate to the stated risk profile. If you "
        "classify an item [RISK], state a concrete trigger condition -- the "
        "specific future change in the risk profile that should cause this to "
        "be revisited -- immediately after your one-line reason.\n\n"
        "Go through every item, in the order given, with a one-line reason, "
        "tagging each with exactly one of [BLOCKING], [NON-BLOCKING], "
        "[QUESTION], or [RISK]."
    )


def classifier_system_5way_with_work_item(risk_profile):
    """Round 2: adds a fifth classification, [WORK_ITEM], and two fixes to
    round 1's known problems.

    (1) [WORK_ITEM] vs [RISK] is a genuinely new discrimination, not just
    "another bucket" -- RISK is CONDITIONAL (the harm only actually
    materializes if a named condition fires; it may never need addressing at
    all), WORK_ITEM is UNCONDITIONAL (the work is real and will need doing
    regardless, it's a scheduling decision, not a proportionality judgment).
    Round 1 never tested whether a classifier can tell these apart, since it
    only had RISK vs BLOCKING to sort into.

    (2) Round 1's precise, diagnosed bug: items phrased as a flat absence
    ("has no X") got misread as correctness defects and kept BLOCKING, while
    substantively identical items phrased as a conditional scenario ("if X
    exceeds Y") were classified correctly. This adds an explicit instruction
    that phrasing is not the test -- judge the proportionality of the harm,
    not the grammar of the sentence describing it. Whether this actually
    fixes recall, rather than just sounding like it should (the same
    over-trust in stated guardrails that didn't save Concur's sufficiency
    criterion), is what round 2 measures.

    (3) New: if the stated risk profile itself names a concrete, already-
    scheduled future change, concerns tied to that change should NOT be
    treated as distantly conditional -- an imminent, already-committed
    transition is a different thing from a hypothetical one, and RISK's
    "revisit later" framing undersells a harm that's already scheduled to
    materialize soon."""
    return (
        "You are an adversarial Refuter classifying every item raised against a "
        "proposed decision. For each item, decide whether it is:\n\n"
        "[BLOCKING] -- a genuine problem with the proposal that its owner could "
        "actually address by revising the approach through better engineering "
        "judgment, and that matters regardless of the work item's current "
        "maturity or risk profile, and cannot be safely deferred to later work. "
        "Any plain correctness defect (something that is simply wrong, not a "
        "matter of proportionate hardening or scheduling) is always BLOCKING or "
        "NON-BLOCKING, never RISK or WORK_ITEM.\n"
        "[NON-BLOCKING] -- a valid but minor, non-critical point.\n"
        "[QUESTION] -- a genuine gap in the FACTS available, not resolvable by "
        "any amount of engineering reasoning or revision, because it depends on "
        "information that isn't available to anyone in this discussion and must "
        "come from an external source.\n"
        "[RISK] -- a real, legitimate concern -- NOT merely inconvenient or "
        "effortful to address -- where addressing it right now is genuinely "
        "disproportionate to the work's CURRENT, explicitly stated risk "
        "profile below, AND the concern's urgency is CONDITIONAL on that "
        "profile changing in a specific, nameable way -- it may never actually "
        "need addressing if that change never happens. Judge this by the "
        "actual proportionality of the harm described, not by whether the "
        "concern happens to be phrased as a flat statement ('there is no X') "
        "or a conditional scenario ('if X happens, then Y') -- both phrasings "
        "can equally describe a disproportionate concern, and both can "
        "equally describe a genuine one. The wording is not the test.\n"
        "[WORK_ITEM] -- a real, legitimate concern describing concrete "
        "engineering work that should genuinely happen at some point, "
        "UNCONDITIONALLY -- its need does NOT depend on the risk profile "
        "changing, it is simply not required before THIS decision can "
        "proceed. Use this instead of RISK when the work is definitely "
        "needed eventually regardless of risk profile -- a scheduling "
        "decision, not a proportionality judgment.\n\n"
        f"The work this decision belongs to has this current, explicitly "
        f"stated risk profile, including any explicitly stated future plans:\n"
        f"{risk_profile}\n\n"
        "Do not classify something as [QUESTION] just because it is hard or "
        "contested -- only when no engineering revision could resolve it "
        "without an external fact. Never use [RISK] or [WORK_ITEM] for a "
        "plain correctness defect, regardless of risk profile or phrasing. If "
        "you classify an item [RISK], state a concrete trigger condition -- "
        "the specific future change that should cause this to be revisited. "
        "If you classify an item [WORK_ITEM], state what the follow-up "
        "engineering work actually is, in one phrase.\n\n"
        "If the stated risk profile includes an explicit, concrete, already-"
        "scheduled future change (a stated date or milestone), treat concerns "
        "tied to that specific change as already having a known, approaching "
        "trigger, not a distant hypothetical one -- do not classify a concern "
        "as RISK with a casual \"revisit later\" framing when the stated "
        "profile already commits to that change happening soon.\n\n"
        "Go through every item, in the order given, with a one-line reason, "
        "tagging each with exactly one of [BLOCKING], [NON-BLOCKING], "
        "[QUESTION], [RISK], or [WORK_ITEM]."
    )
