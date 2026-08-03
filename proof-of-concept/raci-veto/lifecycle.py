"""Three things run against the same proposal:

`run_mechanism` is the already-validated propose/contest/classify/revise/
targeted-recheck lifecycle from question-gating and decision-engine, unchanged
in mechanics -- generalized only so it can run over an arbitrary set of
challenger roles instead of a fixed pair. Called twice per scenario:

- "baseline": challengers = Responsible + Consulted + Informed (today's
  world -- no RACI concept, whoever was manually invited gets a voice).
- "raci": challengers = Responsible + Consulted only. Informed is excluded
  from contest/classify/revise/recheck entirely.

`_shadow_reaction` gets the Informed role's reaction anyway, live, but never
feeds it into the raci mechanism -- purely a side channel, then judged by
`_judge_redundancy` against what raci's Responsible/Consulted already raised.
This is question 1: does excluding Informed lose a real, non-redundant
concern? Comparing `baseline` and `raci`'s final states is a second,
independent signal for the same question -- if excluding Informed's item
never changes the terminal state either, that's two lines of evidence
participation restriction is safe, not one.

`run_concur_check` (and its repeated variant) is question 2: a role that
never participated in contest/classify/revise, shown ONLY raci's final
decision, cold, asked a single yes/no question strictly on its own named
grounds. Recorded against raci's own outcome, not baseline's -- Concur is
being tested as an addition to the RACI mechanism, not to the pre-RACI one.
"""

import re

from llm_client import OWNER_MODEL, SUPPORT_MODEL, chat
from roles import (
    challenger_react_system,
    classifier_system_3way,
    concur_system,
    issue_react_system,
    owner_propose_system,
    owner_revise_system,
    question_react_system,
    redundancy_judge_system,
)

TAG_RE = re.compile(r"\[(BLOCKING|NON[-_]BLOCKING|QUESTION)\b", re.IGNORECASE)


def _brief(scenario):
    return f"Decision: {scenario['title']}\n\nContext: {scenario['context']}"


def _propose(scenario):
    return chat(OWNER_MODEL, owner_propose_system(scenario["owner_role"]), _brief(scenario), max_tokens=600)["content"]


def _contest(scenario, proposal, roles):
    raised = {}
    for role in roles:
        raised[role] = chat(
            SUPPORT_MODEL,
            challenger_react_system(role),
            f"{_brief(scenario)}\n\nProposed decision:\n{proposal}",
            max_tokens=400,
        )["content"]
    return raised


def _items_text(raised):
    return "\n\n".join(f"Challenger ({role}):\n{text}" for role, text in raised.items())


def _parse_tags_positional(classification_text, roles_in_order):
    # Same lesson as decision-engine's TagScanningVerdictParser: a model asked for
    # [NON-BLOCKING] will sometimes write [NON_BLOCKING] instead; tolerate both.
    # Attribution is positional (tags in the order roles were presented) -- same
    # structural limitation as the Java parser, accepted for the same reason.
    tags = [t.upper().replace("_", "-") for t in TAG_RE.findall(classification_text)]
    if len(tags) < len(roles_in_order):
        raise ValueError(
            f"Expected at least {len(roles_in_order)} tags, found {len(tags)} in: {classification_text}"
        )
    return dict(zip(roles_in_order, tags[: len(roles_in_order)]))


def _is_resolved(recheck_text):
    stripped = re.sub(r"^[\s*_#>-]+", "", recheck_text).upper()
    return stripped.startswith("RESOLVED")


def _recheck(role, raised_text, scenario, revision, is_question):
    system = question_react_system(role) if is_question else issue_react_system(role)
    label = "question" if is_question else "concern"
    return chat(
        SUPPORT_MODEL,
        system,
        f"{_brief(scenario)}\n\nYour original {label}:\n{raised_text}\n\nRevised decision:\n{revision}",
        max_tokens=300,
    )["content"]


def run_mechanism(scenario, proposal, raised, label):
    """`raised` is a dict of role -> reaction text, in presentation order --
    supplied by the caller (not elicited here) so that baseline and raci runs
    on the same scenario can share identical Responsible/Consulted reactions,
    isolating the one real variable (whether Informed's reaction is included)
    instead of also introducing fresh sampling variance from re-asking the same
    role twice."""
    challenger_roles = list(raised.keys())
    transcript = {"mechanism": label, "challenger_roles": challenger_roles}
    transcript["raised"] = raised

    classification = chat(
        SUPPORT_MODEL,
        classifier_system_3way(),
        f"{_brief(scenario)}\n\nProposed decision:\n{proposal}\n\nRaised items:\n{_items_text(raised)}",
        max_tokens=700,
    )["content"]
    transcript["classification_round_1"] = classification

    tags = _parse_tags_positional(classification, challenger_roles)
    transcript["tags_round_1"] = tags
    anything_flagged = any(tag != "NON-BLOCKING" for tag in tags.values())

    if not anything_flagged:
        transcript.update(state="converged", final_decision=proposal, rounds=0)
        return transcript

    revised = chat(
        OWNER_MODEL,
        owner_revise_system(scenario["owner_role"]),
        (
            f"{_brief(scenario)}\n\nYour original proposal:\n{proposal}\n\n"
            f"Raised items:\n{_items_text(raised)}\n\nRefuter's classification:\n{classification}"
        ),
        max_tokens=800,
    )["content"]
    transcript["revised_proposal"] = revised
    transcript["rounds"] = 1

    rechecks = {}
    resolved = {}
    for role in challenger_roles:
        is_question = tags[role] == "QUESTION"
        recheck_text = _recheck(role, raised[role], scenario, revised, is_question)
        rechecks[role] = recheck_text
        resolved[role] = _is_resolved(recheck_text)
    transcript["rechecks"] = rechecks
    transcript["resolved"] = resolved

    if all(resolved.values()):
        transcript.update(state="converged", final_decision=revised)
    else:
        transcript.update(state="escalated_to_human", final_decision=revised)
    return transcript


def shadow_reaction(scenario, proposal):
    role = scenario["informed_role"]
    text = _contest(scenario, proposal, [role])[role]
    return role, text


def judge_redundancy(scenario, raci_raised, shadow_role, shadow_text):
    existing = _items_text(raci_raised)
    verdict = chat(
        SUPPORT_MODEL,
        redundancy_judge_system(),
        (
            f"{_brief(scenario)}\n\nAlready-raised concerns:\n{existing}\n\n"
            f"Additional reaction (from {shadow_role}, who did not otherwise participate):\n{shadow_text}"
        ),
        max_tokens=250,
    )["content"]
    is_new = verdict.strip().upper().startswith("NEW")
    return verdict, is_new


def _concurs(verdict_text):
    stripped = re.sub(r"^[\s*_#>-]+", "", verdict_text).upper()
    return stripped.startswith("CONCUR") and not stripped.startswith("DO NOT CONCUR")


def run_concur_check(scenario, final_decision):
    role = scenario["concur_role"]
    grounds = scenario["concur_grounds"]
    verdict = chat(
        SUPPORT_MODEL,
        concur_system(role, grounds),
        f"{_brief(scenario)}\n\nFinal decision as it stands:\n{final_decision}",
        max_tokens=300,
    )["content"]
    return verdict, _concurs(verdict)


def run_concur_repeats(scenario, final_decision, n=3):
    """Question 3: is a Concur divergence principled and repeatable, or noise?
    Reruns the identical cold review n times against the identical final
    decision -- consistent verdicts across reruns is signal, scattershot is not.
    """
    verdicts = []
    concurs = []
    for _ in range(n):
        verdict, concurs_flag = run_concur_check(scenario, final_decision)
        verdicts.append(verdict)
        concurs.append(concurs_flag)
    return verdicts, concurs
