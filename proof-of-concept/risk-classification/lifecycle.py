"""Two classifiers run against the identical, fixed set of pre-registered
items per scenario -- no propose/contest/revise loop, since the thing under
test is purely the classify step's ability to sort items correctly, not the
rest of the lifecycle (already validated elsewhere).

`run_classify_3way` replays today's unmodified classifier -- establishes
what happens to a genuinely disproportionate item with no RISK option to
sort it into (expected: BLOCKING, the actual real-world outcome that
prompted this PoC).

`run_classify_4way_with_risk` is the mechanism under test: the same items,
same order, classified with RISK available and the work's stated risk
profile in context. Scored against each item's pre-registered ground truth
on two axes -- does a true RISK item get classified RISK (recall), and does
a true BLOCKING item get incorrectly swept into RISK (the overshoot rate,
the more important number given what a similar "be proportionate" fix did
to Concur).
"""

import re

from llm_client import SUPPORT_MODEL, chat
from roles import classifier_system_3way, classifier_system_4way_with_risk, classifier_system_5way_with_work_item

TAG_RE_3WAY = re.compile(r"\[(BLOCKING|NON[-_]BLOCKING|QUESTION)\b", re.IGNORECASE)
TAG_RE_4WAY = re.compile(r"\[(BLOCKING|NON[-_]BLOCKING|QUESTION|RISK)\b", re.IGNORECASE)
TAG_RE_5WAY = re.compile(r"\[(BLOCKING|NON[-_]BLOCKING|QUESTION|RISK|WORK[-_]ITEM)\b", re.IGNORECASE)


def _brief(scenario):
    return f"Decision: {scenario['title']}\n\nCategory: {scenario['category']}\n\nContext: {scenario['context']}"


def _items_text(items):
    return "\n\n".join(f"Item {i + 1} ({it['role']}):\n{it['text']}" for i, it in enumerate(items))


def _parse_tags_positional(classification_text, n_items, tag_re, separator="-"):
    # Same lesson as decision-engine's TagScanningVerdictParser and every prior PoC here:
    # tolerant of NON-BLOCKING/NON_BLOCKING (and now WORK-ITEM/WORK_ITEM) variance;
    # attribution is positional. `separator` picks which spelling tags get normalized
    # to, so it can match whichever form a scenario's ground_truth values use.
    other = "_" if separator == "-" else "-"
    tags = [t.upper().replace(other, separator) for t in tag_re.findall(classification_text)]
    if len(tags) < n_items:
        raise ValueError(f"Expected at least {n_items} tags, found {len(tags)} in: {classification_text}")
    return tags[:n_items]


def run_classify_3way(scenario):
    items = scenario["items"]
    text = chat(
        SUPPORT_MODEL,
        classifier_system_3way(),
        f"{_brief(scenario)}\n\nRaised items:\n{_items_text(items)}",
        max_tokens=900,
    )["content"]
    tags = _parse_tags_positional(text, len(items), TAG_RE_3WAY)
    return text, tags


def run_classify_4way_with_risk(scenario):
    items = scenario["items"]
    system = classifier_system_4way_with_risk(scenario["risk_profile"])
    text = chat(
        SUPPORT_MODEL,
        system,
        f"{_brief(scenario)}\n\nRaised items:\n{_items_text(items)}",
        max_tokens=1200,
    )["content"]
    tags = _parse_tags_positional(text, len(items), TAG_RE_4WAY)
    return text, tags


def run_classify_5way_with_work_item(scenario):
    """Round 2's mechanism under test -- ground_truth values in
    scenarios_round2.py use underscore-separated WORK_ITEM/NON_BLOCKING, so
    tags are normalized to that form here (separator="_"), the opposite
    convention from the 3-way/4-way parsers above."""
    items = scenario["items"]
    system = classifier_system_5way_with_work_item(scenario["risk_profile"])
    text = chat(
        SUPPORT_MODEL,
        system,
        f"{_brief(scenario)}\n\nRaised items:\n{_items_text(items)}",
        max_tokens=1400,
    )["content"]
    tags = _parse_tags_positional(text, len(items), TAG_RE_5WAY, separator="_")
    return text, tags
