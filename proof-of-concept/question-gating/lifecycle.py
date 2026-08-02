"""Two mechanisms run side by side on the identical proposal + raised items:

`run_baseline` replays decision-making/lifecycle.py's already-validated
propose/contest/refute/revise mechanism unmodified (2-way BLOCKING/NON-BLOCKING
classification, LLM-judged convergence) — this is what the platform's decision
lifecycle actually does today, with no concept of a Question at all.

`run_gated` adds a 3-way classification (BLOCKING/NON-BLOCKING/QUESTION) plus a
STRUCTURAL code-level gate: convergence is impossible while any item is tagged
[QUESTION], and that gate can only be cleared by `question_resolved_externally`
being set True — which this code never sets from the owner's own output, no
matter how confidently the owner answers it. Only an explicitly external-sourced
answer (scenarios.py's `external_answer`) can clear it. This is the actual
mechanism under test: does a raised Question structurally block convergence, or
can it be classified away or quietly self-answered.
"""

import re

from llm_client import OWNER_MODEL, SUPPORT_MODEL, chat
from roles import (
    classifier_system_3way,
    issue_raiser_system,
    issue_react_system,
    owner_final_revision_system,
    owner_propose_system,
    owner_revise_system,
    question_raiser_system,
    question_react_system,
    refuter_system_2way,
)


def _brief(scenario):
    return f"Decision: {scenario['title']}\n\nContext: {scenario['context']}"


def _propose(scenario):
    return chat(OWNER_MODEL, owner_propose_system(scenario["owner_role"]), _brief(scenario), max_tokens=600)["content"]


def _contest(scenario, proposal):
    issue = scenario["issue"]
    question = scenario["question"]
    issue_response = chat(
        SUPPORT_MODEL,
        issue_raiser_system(issue["role"], issue["text"]),
        f"{_brief(scenario)}\n\nProposed decision:\n{proposal}",
        max_tokens=400,
    )["content"]
    question_response = chat(
        SUPPORT_MODEL,
        question_raiser_system(question["role"], question["text"]),
        f"{_brief(scenario)}\n\nProposed decision:\n{proposal}",
        max_tokens=400,
    )["content"]
    return {issue["role"]: issue_response, question["role"]: question_response}


def _items_text(raised):
    return "\n\n".join(f"Challenger ({role}):\n{text}" for role, text in raised.items())


def _count_tags_2way(classification):
    # Models don't reliably close the tag right after the word (e.g. "[BLOCKING:
    # reason]" instead of "[BLOCKING] reason") — match on the tag prefix, not an
    # exact "[BLOCKING]" substring, so formatting variance doesn't silently zero
    # out a real blocking count. "[NON-BLOCKING" is excluded by requiring "[" to
    # immediately precede "BLOCKING".
    upper = classification.upper()
    blocking = len(re.findall(r"\[BLOCKING\b", upper))
    non_blocking = len(re.findall(r"\[NON-BLOCKING\b", upper))
    return blocking, non_blocking


def _count_tags_3way(classification):
    upper = classification.upper()
    blocking = len(re.findall(r"\[BLOCKING\b", upper))
    non_blocking = len(re.findall(r"\[NON-BLOCKING\b", upper))
    question = len(re.findall(r"\[QUESTION\b", upper))
    return blocking, non_blocking, question


def run_baseline(scenario, proposal, raised):
    """Today's mechanism, unmodified: 2-way classify -> (revise -> re-classify) -> converge/escalate.
    The Question is fed in exactly like any other challenger issue — there is no
    separate code path for it, because the existing mechanism has none.
    """
    transcript = {"mechanism": "baseline (2-way, unmodified)"}

    classification = chat(
        SUPPORT_MODEL,
        refuter_system_2way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{proposal}\n\nRaised issues:\n{_items_text(raised)}",
        max_tokens=600,
    )["content"]
    transcript["classification_round_1"] = classification
    blocking, _ = _count_tags_2way(classification)

    if blocking == 0:
        transcript.update(state="converged", final_decision=proposal, rounds=0)
        return transcript

    revised = chat(
        OWNER_MODEL,
        owner_revise_system(scenario["owner_role"]),
        (
            f"{_brief(scenario)}\n\nYour original proposal:\n{proposal}\n\n"
            f"Raised issues:\n{_items_text(raised)}\n\nRefuter's classification:\n{classification}"
        ),
        max_tokens=700,
    )["content"]
    transcript["revised_proposal"] = revised
    transcript["rounds"] = 1

    reclassification = chat(
        SUPPORT_MODEL,
        refuter_system_2way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{revised}\n\nRaised issues:\n{_items_text(raised)}",
        max_tokens=600,
    )["content"]
    transcript["classification_round_2"] = reclassification
    blocking_final, _ = _count_tags_2way(reclassification)

    if blocking_final == 0:
        transcript.update(state="converged", final_decision=revised)
    else:
        transcript.update(state="escalated_to_human", final_decision=revised)
    return transcript


def _is_resolved(recheck_text):
    # Same lesson as _count_tags_2way/_count_tags_3way: models don't reliably put
    # the tag at the exact start of the string — markdown emphasis ("**RESOLVED.**")
    # is enough to break a strict .startswith("RESOLVED") check. Strip leading
    # markup, not just whitespace, before matching.
    stripped = re.sub(r"^[\s*_#>-]+", "", recheck_text).upper()
    return stripped.startswith("RESOLVED")


def _recheck(role, react_system_fn, raised_text, scenario, revision, label):
    return chat(
        SUPPORT_MODEL,
        react_system_fn(role),
        (
            f"{_brief(scenario)}\n\nYour original {label}:\n{raised_text}\n\n"
            f"Revised decision:\n{revision}"
        ),
        max_tokens=300,
    )["content"]


def run_gated(scenario, proposal, raised):
    """New mechanism: 3-way classify (round 1 only), then a per-raiser targeted
    recheck — not a generalist reclassifying every item from scratch — decides
    whether each item is resolved by a given revision. This is the fix for the
    anchoring bug found in poc-decision-making.md and reproduced by this PoC's
    first run: a generalist asked to reclassify everything restates the original
    problem instead of re-deriving from the new text. Here, the specific role
    that raised an item is shown ONLY its own original item and the new revision,
    and asked whether ITS OWN concern is resolved — same fix, generalized from
    challenger_react_system to also cover the Question side.

    The old generalist reclassification is still run at both checkpoints and
    recorded on the transcript, but purely for side-by-side comparison — it no
    longer decides the outcome, same as poc-decision-making.md's dissent_fixed run.

    The structural gate is unchanged: `question_resolved_externally` is never set
    from the owner's own text or from the Question-raiser's own recheck — only by
    this code explicitly supplying scenario['external_answer'].
    """
    transcript = {"mechanism": "gated (3-way + targeted per-raiser recheck + structural question gate)"}
    question_resolved_externally = False
    issue_role, issue_text = scenario["issue"]["role"], raised[scenario["issue"]["role"]]
    question_role, question_text = scenario["question"]["role"], raised[scenario["question"]["role"]]

    classification = chat(
        SUPPORT_MODEL,
        classifier_system_3way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{proposal}\n\nRaised issues:\n{_items_text(raised)}",
        max_tokens=600,
    )["content"]
    transcript["classification_round_1"] = classification
    blocking, _, question = _count_tags_3way(classification)
    transcript["has_question_round_1"] = question > 0
    transcript["has_blocking_round_1"] = blocking > 0

    if blocking == 0 and question == 0:
        transcript.update(state="converged", final_decision=proposal, rounds=0)
        return transcript

    # Owner revises with the SAME unwarned prompt used in the baseline — deliberately
    # not told to treat [QUESTION] items differently, to observe whether it tries to
    # self-answer the missing fact on its own initiative.
    revised = chat(
        OWNER_MODEL,
        owner_revise_system(scenario["owner_role"]),
        (
            f"{_brief(scenario)}\n\nYour original proposal:\n{proposal}\n\n"
            f"Raised issues:\n{_items_text(raised)}\n\nRefuter's classification:\n{classification}"
        ),
        max_tokens=700,
    )["content"]
    transcript["self_answer_attempt"] = revised
    transcript["rounds"] = 1

    # OLD mechanism, kept only for comparison — does NOT decide the outcome.
    old_reclassification = chat(
        SUPPORT_MODEL,
        classifier_system_3way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{revised}\n\nRaised issues:\n{_items_text(raised)}",
        max_tokens=600,
    )["content"]
    transcript["old_generalist_reclassification_after_self_answer"] = old_reclassification

    # NEW: targeted per-raiser recheck decides the outcome.
    issue_recheck = _recheck(issue_role, issue_react_system, issue_text, scenario, revised, "concern")
    question_recheck = _recheck(question_role, question_react_system, question_text, scenario, revised, "question")
    transcript["issue_recheck_after_self_answer"] = issue_recheck
    transcript["question_recheck_after_self_answer"] = question_recheck
    issue_resolved = _is_resolved(issue_recheck)
    question_recheck_says_resolved = _is_resolved(question_recheck)
    transcript["question_raiser_fooled_by_self_answer"] = question_recheck_says_resolved and not question_resolved_externally

    # STRUCTURAL GATE: question_resolved_externally is still False here, no matter
    # what the owner wrote, how the old generalist reclassification reads, or even
    # what the Question-raiser's own recheck concluded. This is the invariant under
    # test — no LLM judgment, targeted or not, is sufficient on its own to clear it.
    if transcript["has_question_round_1"] and not question_resolved_externally:
        transcript["state_after_self_answer_attempt"] = "blocked_on_question"
    elif not issue_resolved:
        transcript["state_after_self_answer_attempt"] = "escalated_to_human"
    else:
        transcript["state_after_self_answer_attempt"] = "converged"

    if not transcript["has_question_round_1"]:
        transcript.update(state=transcript["state_after_self_answer_attempt"], final_decision=revised)
        return transcript

    # Now supply the actual external answer and let the owner produce a final revision.
    question_resolved_externally = True
    external_answer = scenario["external_answer"]
    final_revision = chat(
        OWNER_MODEL,
        owner_final_revision_system(scenario["owner_role"]),
        (
            f"{_brief(scenario)}\n\nYour original proposal:\n{proposal}\n\n"
            f"Raised issues:\n{_items_text(raised)}\n\n"
            f"Externally supplied answer to the missing fact (NOT your own guess — "
            f"this came from outside this discussion):\n{external_answer}"
        ),
        max_tokens=700,
    )["content"]
    transcript["final_revision_with_external_answer"] = final_revision
    transcript["rounds"] = 2

    # OLD mechanism, kept only for comparison — does NOT decide the outcome.
    old_final_reclassification = chat(
        SUPPORT_MODEL,
        classifier_system_3way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{final_revision}\n\nRaised issues:\n{_items_text(raised)}",
        max_tokens=600,
    )["content"]
    transcript["old_generalist_reclassification_final"] = old_final_reclassification
    _, _, old_question_final = _count_tags_3way(old_final_reclassification)
    transcript["old_mechanism_still_flags_question_after_external_answer"] = old_question_final > 0

    # NEW: targeted per-raiser recheck, again, now against the final revision.
    issue_recheck_final = _recheck(issue_role, issue_react_system, issue_text, scenario, final_revision, "concern")
    question_recheck_final = _recheck(question_role, question_react_system, question_text, scenario, final_revision, "question")
    transcript["issue_recheck_final"] = issue_recheck_final
    transcript["question_recheck_final"] = question_recheck_final
    issue_resolved_final = _is_resolved(issue_recheck_final)
    question_resolved_final = _is_resolved(question_recheck_final)

    if issue_resolved_final and question_resolved_externally and question_resolved_final:
        transcript.update(state="converged", final_decision=final_revision)
    else:
        transcript.update(state="escalated_to_human", final_decision=final_revision)
    return transcript
