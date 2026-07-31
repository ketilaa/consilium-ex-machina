"""Propose -> contest -> refute -> (revise -> re-check) -> converge/escalate lifecycle.

Implements the bounded-round, derived-confidence model from
docs/design/decision-making.md: exactly one revision round is allowed before a
still-blocking decision escalates, rather than looping until agents agree among
themselves.
"""

from llm_client import OWNER_MODEL, SUPPORT_MODEL, chat
from roles import challenger_system, owner_propose_system, owner_revise_system, refuter_system


def _decision_brief(decision):
    return f"Decision: {decision['title']}\n\nContext: {decision['context']}"


def _propose(decision):
    return chat(OWNER_MODEL, owner_propose_system(decision["owner_role"]), _decision_brief(decision), max_tokens=700)


def _contest(decision, proposal):
    issues = {}
    for role in decision["challenger_roles"]:
        issues[role] = chat(
            SUPPORT_MODEL,
            challenger_system(role),
            f"{_decision_brief(decision)}\n\nProposed decision:\n{proposal}",
            max_tokens=500,
        )
    return issues


def _refute(decision, proposal, issues):
    issues_text = "\n\n".join(f"Challenger ({role}):\n{text}" for role, text in issues.items())
    return chat(
        SUPPORT_MODEL,
        refuter_system(),
        f"{_decision_brief(decision)}\n\nProposed decision:\n{proposal}\n\nRaised issues:\n{issues_text}",
        max_tokens=700,
    )


def _revise(decision, proposal, issues, classification):
    issues_text = "\n\n".join(f"Challenger ({role}):\n{text}" for role, text in issues.items())
    return chat(
        OWNER_MODEL,
        owner_revise_system(decision["owner_role"]),
        (
            f"{_decision_brief(decision)}\n\nYour original proposal:\n{proposal}\n\n"
            f"Raised issues:\n{issues_text}\n\nRefuter's classification:\n{classification}"
        ),
        max_tokens=800,
    )


def _count_tags(classification):
    upper = classification.upper()
    blocking = upper.count("[BLOCKING]")
    non_blocking = upper.count("[NON-BLOCKING]")
    return blocking, non_blocking


def _confidence(total_issues, needed_revision):
    base = 0.5 if needed_revision else 0.6
    ceiling = 0.90 if needed_revision else 0.95
    return round(min(ceiling, base + 0.05 * total_issues), 2)


def run_lifecycle(decision):
    transcript = {"decision": decision["slug"], "rounds": 0}

    proposal = _propose(decision)
    transcript["proposal"] = proposal

    issues = _contest(decision, proposal)
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
        )
        return transcript

    revised = _revise(decision, proposal, issues, classification)
    transcript["revised_proposal"] = revised
    transcript["rounds"] = 1

    reclassification = _refute(decision, revised, issues)
    transcript["classification_round_2"] = reclassification
    blocking_final, _ = _count_tags(reclassification)

    if blocking_final == 0:
        transcript.update(
            state="converged",
            final_decision=revised,
            confidence=_confidence(total_issues, needed_revision=True),
        )
    else:
        transcript.update(
            state="escalated_to_human",
            final_decision=revised,
            confidence=None,
        )
    return transcript
