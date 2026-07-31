"""Follow-up to lifecycle.py: one challenger holds a fixed, non-negotiable objection.

The original PoC found the refuter never blocked anything because challengers only
raised generic, hedged concerns. This rigs a genuine, concrete, hard-to-dismiss
objection into the contest step to isolate whether the tie-break/resolution
mechanism (revise -> re-check -> converge/escalate) behaves sensibly once a real
conflict actually exists — and whether the refuter's classification agrees with the
dissenter's own judgment of whether its concern was actually addressed.
"""

from llm_client import SUPPORT_MODEL, chat
from lifecycle import _confidence, _count_tags, _decision_brief, _propose, _refute, _revise
from roles import challenger_system, dissenter_react_system, dissenter_system


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
            dissenter_satisfied=None,
            refuter_dissenter_agree=None,
        )
        return transcript

    revised = _revise(decision, proposal, issues, classification)
    transcript["revised_proposal"] = revised
    transcript["rounds"] = 1

    dissenter_reaction = chat(
        SUPPORT_MODEL,
        dissenter_react_system(dissent["role"], dissent["objection"]),
        f"{_decision_brief(decision)}\n\nRevised proposal:\n{revised}",
        max_tokens=300,
    )
    transcript["dissenter_reaction"] = dissenter_reaction
    dissenter_satisfied = dissenter_reaction.strip().upper().startswith("CONCERN RESOLVED")

    reclassification = _refute(decision, revised, issues)
    transcript["classification_round_2"] = reclassification
    blocking_final, _ = _count_tags(reclassification)

    converged = blocking_final == 0
    transcript["dissenter_satisfied"] = dissenter_satisfied
    transcript["refuter_dissenter_agree"] = converged == dissenter_satisfied

    if converged:
        transcript.update(
            state="converged",
            final_decision=revised,
            confidence=_confidence(total_issues, needed_revision=True),
        )
    else:
        transcript.update(state="escalated_to_human", final_decision=revised, confidence=None)
    return transcript
