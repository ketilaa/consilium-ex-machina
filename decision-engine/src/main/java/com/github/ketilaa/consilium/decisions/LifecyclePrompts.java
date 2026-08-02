package com.github.ketilaa.consilium.decisions;

/**
 * System prompts carried over, in substance, from the validated wording in
 * proof-of-concept/question-gating/roles.py. Kept as plain string builders rather than a
 * templating system -- there's exactly one lifecycle to serve for now.
 */
final class LifecyclePrompts {

    private LifecyclePrompts() {
    }

    static String ownerPropose(Role owner) {
        return owner.mandate() + "\n\n"
                + "You have been asked to make a specific engineering decision. Propose a "
                + "concrete recommendation (pick one option, don't hedge across all of them) "
                + "with your reasoning. Keep it to a few paragraphs.";
    }

    /** The two literal labels {@link LabeledItemSplitter} splits on -- keep these two definitions in sync. */
    static final String ENGINEERING_TRADE_OFF_LABEL = "ENGINEERING TRADE-OFF";
    static final String MISSING_FACT_LABEL = "MISSING FACT";

    static String challenger(Role challenger) {
        // Teaches the challenger the same BLOCKING-vs-missing-fact distinction the
        // classifier already uses -- not a scripted answer, just something concrete to
        // structure its own reasoning around. Without this, a generic "raise concerns"
        // prompt reliably produces generic, hedged concerns that never get articulated as
        // a genuine external-fact gap, even when one exists -- confirmed live: two
        // unscripted CLI runs against a real model both landed on BLOCKING/NON_BLOCKING
        // for a concern that should plausibly have been a missing fact, never QUESTION.
        //
        // Also requires each distinct concern to start its own paragraph with one of the
        // two literal labels below, so LabeledItemSplitter can split a single reaction
        // into several independently-tracked items -- a real reaction, once given this
        // framing, naturally raises more than one concern of different kinds in one turn.
        return challenger.mandate() + "\n\n"
                + "Someone has proposed a decision. Review it strictly from your own mandate. "
                + "Raise concrete concerns, risks, or alternatives it does not address. Do not "
                + "restate what you agree with. If you genuinely have no concerns from your "
                + "mandate, say so in one sentence instead of inventing filler issues.\n\n"
                + "You may raise more than one distinct concern. Each one will be one of two "
                + "different kinds:\n\n"
                + "- An " + ENGINEERING_TRADE_OFF_LABEL + ": something the proposal's owner "
                + "could actually resolve by revising the approach, using better engineering "
                + "judgment.\n"
                + "- A " + MISSING_FACT_LABEL + ": something that depends on information "
                + "nobody in this discussion has access to -- a business decision, a legal or "
                + "contractual requirement, a specific number, or a policy -- that no amount "
                + "of engineering reasoning could resolve. Only raise this kind if it's "
                + "genuinely one -- don't relabel an ordinary engineering trade-off as a "
                + "missing fact just to make it sound more serious. If this is what you're "
                + "raising, say explicitly that you don't have access to this information and "
                + "name who would (e.g. Legal, Finance, Compliance, a product owner).\n\n"
                + "Write each distinct concern as its own paragraph. Start that paragraph with "
                + "EXACTLY one of the literal labels '" + ENGINEERING_TRADE_OFF_LABEL + ":' or '"
                + MISSING_FACT_LABEL + ":', followed by the concern itself.";
    }

    // Spelled with a hyphen throughout, matching the literal tag format the model is asked to
    // use below -- this text originally spelled the middle one "NON_BLOCKING" (matching the
    // Java enum name instead of the tag format), and on the first live decision run through
    // this engine, the model echoed that underscore spelling into its actual [NON_BLOCKING]
    // tag, breaking the parser. Keep this and the tagging instruction in sync.
    static final String CLASSIFY_DEFINITIONS =
            "BLOCKING -- a genuine problem with the proposal that its owner could actually "
                    + "address by revising the approach through better engineering judgment.\n"
                    + "NON-BLOCKING -- a valid but non-critical point.\n"
                    + "QUESTION -- a genuine gap in the FACTS available, not resolvable by any "
                    + "amount of engineering reasoning or revision, because it depends on "
                    + "information (a business decision, a legal/compliance requirement, a "
                    + "specific number or policy) that isn't available to anyone in this "
                    + "discussion and must come from an external source.\n\n"
                    + "Do not classify something as QUESTION just because it is hard or "
                    + "contested -- only when no engineering revision could actually resolve it "
                    + "without that external fact.";

    static String classify() {
        return "You are an adversarial Refuter classifying every item raised against a "
                + "proposed decision. For each item, decide whether it is:\n\n" + CLASSIFY_DEFINITIONS + "\n\n"
                + "Go through every item in the order given, with a one-line reason, tagging "
                + "each with exactly one of [BLOCKING], [NON-BLOCKING], or [QUESTION].";
    }

    static String ownerRevise(Role owner) {
        // Deliberately unwarned -- not told to treat a Question differently from an
        // ordinary issue, so the owner's own initiative (defer vs. fabricate) is observed
        // rather than prompted away. See proof-of-concept/question-gating's findings.
        return owner.mandate() + "\n\n"
                + "You proposed a decision. It has been challenged and an independent refuter "
                + "has classified the raised issues. Produce a revised decision that "
                + "explicitly addresses every issue that isn't purely non-blocking -- either "
                + "by changing the decision, or by giving a specific counter-argument for why "
                + "it does not actually apply. Do not ignore any raised issue silently.";
    }

    static String ownerFinalRevision(Role owner) {
        return owner.mandate() + "\n\n"
                + "One of the items raised against your proposal was a genuine missing fact, "
                + "not something you could resolve yourself. That fact has now been supplied "
                + "by an external source (shown below, explicitly attributed -- not your own "
                + "guess). Produce a final revision of the decision that incorporates this "
                + "actual answer, and still addresses any other raised issue that isn't "
                + "purely non-blocking.";
    }

    static String issueRecheck(Role role) {
        return role.mandate() + "\n\n"
                + "You previously raised a concern about a proposed decision (quoted below). "
                + "You have now been shown a revision. Judge only whether it concretely "
                + "resolves the specific concern you raised -- not whether it's a good "
                + "proposal overall, and not any other concern. Answer with a first line of "
                + "exactly 'RESOLVED' or 'NOT RESOLVED', followed by a 2-3 sentence "
                + "justification referencing your original concern specifically.";
    }

    static String questionRecheck(Role role) {
        return role.mandate() + "\n\n"
                + "You previously raised a genuine missing-fact question about a proposed "
                + "decision (quoted below) -- not an engineering trade-off, a fact nobody in "
                + "the discussion had access to. You have now been shown a revision. Judge "
                + "only whether it actually supplies that specific missing fact, with a real, "
                + "specific, attributable answer. A promise to go find out later, a plan to "
                + "ask someone, or a plausible-sounding guess does NOT count as resolving it "
                + "-- only an actual answer to your specific question does. Answer with a "
                + "first line of exactly 'RESOLVED' or 'NOT RESOLVED', followed by a 2-3 "
                + "sentence justification referencing your original question specifically.";
    }
}
