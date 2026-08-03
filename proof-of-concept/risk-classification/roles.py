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
