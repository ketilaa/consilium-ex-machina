"""Follow-up to lifecycle.py: one challenger holds a fixed, non-negotiable objection.

The first dissent run found the refuter's post-revision re-check anchors on its own
round-1 verdict instead of re-deriving it from the actual revision — it restated the
original objection almost verbatim and re-blocked even when its own text described a
resolution. This version fixes that by asking each role that raised a concern to
judge, for itself, whether the revision resolves *its own* concern — the same thing
that already worked correctly for the dissenter in the first run — instead of routing
the re-check back through a generalist refuter reprocessing every issue from scratch.
The old refuter re-check is still run and recorded, purely for side-by-side
comparison against this fix.
"""

from llm_client import SUPPORT_MODEL, chat
from lifecycle import _confidence, _count_tags, _decision_brief, _propose, _refute, _revise
from roles import challenger_react_system, challenger_system, dissenter_system


def _contest_with_dissent(decision, proposal):
    dissent = decision["dissent"]
    issues = {}
    for role in decision["challenger_roles"]:
        brief = f"{_decision_brief(decision)}\n\nProposed decision:\n{proposal}"
        if role == dissent["role"]:
            issues[f"Dissenter ({role})"] = chat(SUPPORT_MODEL, dissenter_system(role, dissent["objection"]), brief, max_tokens=500)
        else:
            issues[role] = chat(SUPPORT_MODEL, challenger_system(role), brief, max_tokens=500)
    return issues


def _react(decision, role, original_issue_text, revised_proposal):
    return chat(
        SUPPORT_MODEL,
        challenger_react_system(role),
        (
            f"{_decision_brief(decision)}\n\nYour original concern:\n{original_issue_text}"
            f"\n\nRevised proposal:\n{revised_proposal}"
        ),
        max_tokens=300,
    )


def run_dissent_lifecycle(decision):
    transcript = {"decision": decision["slug"], "rounds": 0}
    dissent = decision["dissent"]

    proposal = _propose(decision)
    transcript["proposal"] = proposal

    issues = _contest_with_dissent(decision, proposal)
    transcript["issues"] = issues

    classification = _refute(decision, proposal, issues)
    transcript["classification_round_1"] = classification
    blocking, non_blocking = _count_tags(classification)
    total_issues = blocking + non_blocking

    if blocking == 0:
        transcript.update(
            state="converged",
            final_decision=proposal,
            confidence=_confidence(total_issues, needed_revision=False),
            reactions=None,
            refuter_reaction_agree=None,
        )
        return transcript

    revised = _revise(decision, proposal, issues, classification)
    transcript["revised_proposal"] = revised
    transcript["rounds"] = 1

    reactions = {}
    for role in decision["challenger_roles"]:
        label = f"Dissenter ({role})" if role == dissent["role"] else role
        reactions[label] = _react(decision, role, issues[label], revised)
    transcript["reactions"] = reactions
    all_resolved = all(r.strip().upper().startswith("CONCERN RESOLVED") for r in reactions.values())

    # Old (anchoring) mechanism, kept only for side-by-side comparison — not authoritative.
    reclassification = _refute(decision, revised, issues)
    transcript["classification_round_2"] = reclassification
    blocking_final, _ = _count_tags(reclassification)
    refuter_says_converged = blocking_final == 0
    transcript["refuter_says_converged"] = refuter_says_converged
    transcript["refuter_reaction_agree"] = refuter_says_converged == all_resolved

    if all_resolved:
        transcript.update(
            state="converged",
            final_decision=revised,
            confidence=_confidence(total_issues, needed_revision=True),
        )
    else:
        transcript.update(state="escalated_to_human", final_decision=revised, confidence=None)
    return transcript
