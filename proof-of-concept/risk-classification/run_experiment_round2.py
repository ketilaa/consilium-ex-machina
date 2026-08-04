"""Round 2 of the risk-classification PoC. Three things under test, all
continuing directly from round 1's results rather than starting over:

1. Can the classifier tell RISK (conditional -- may never need addressing)
   apart from WORK_ITEM (unconditional -- real work, just not blocking now)?
   Round 1 never had WORK_ITEM to sort into.
2. Does the phrasing-neutral fix (judge the harm, not the sentence's
   grammatical shape) actually close round 1's diagnosed recall gap --
   specifically re-tested on the exact two items that failed it
   (`internal-analytics-dashboard`'s login-rate-limiting and
   unencrypted-transit items, both flatly-phrased and both misread as
   correctness defects in round 1)?
3. Does an explicit, already-scheduled future risk-profile change correctly
   raise the bar now, rather than being waved off with a "revisit later"
   RISK framing that undersells an imminent harm?

Also runs the deliberately ambiguous `consistency-probe` item many times
(not scored for correctness -- there's no fact of the matter) to check
whether RISK-vs-WORK_ITEM judgment is stable on a genuinely hard case, or
scattershot the way poc-raci-veto.md's redundancy judge was.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_classify_4way_with_risk, run_classify_5way_with_work_item
from scenarios_round2 import CONSISTENCY_PROBE, ROUND2_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"
REPS = 3
CONSISTENCY_REPS = 8

# The two round-1 phrasing-sensitivity failures, identified by scenario slug and item text
# prefix, so round 2's summary can call out this exact before/after comparison.
PHRASING_SENSITIVE_ITEMS = {
    "internal-analytics-dashboard": [
        "The dashboard's admin panel has no rate limiting",
        "Data in transit between the dashboard and its database is not encrypted",
    ]
}


def render_md(scenario, baseline_runs, risk_runs):
    items = scenario["items"]
    parts = [
        f"# {scenario['slug']} (round 2)\n",
        f"Decision: {scenario['title']}\n",
        f"\nRisk profile: {scenario['risk_profile']}\n",
        "\n## Items (fixed, pre-registered ground truth)\n",
    ]
    for i, it in enumerate(items, start=1):
        gt = it["ground_truth"] or "AMBIGUOUS (not scored for correctness)"
        parts.append(f"\n### Item {i} ({it['role']}) -- ground truth: **{gt}**\n\n{it['text']}\n")

    parts.append("\n## Mechanism A: round-1's 4-way classifier (no WORK_ITEM option)\n")
    for rep, (text, tags) in enumerate(baseline_runs, start=1):
        parts.append(f"\n### Repeat {rep}\n\n{text}\n\nParsed tags: {tags}\n")

    parts.append("\n## Mechanism B: round-2's 5-way classifier (WORK_ITEM + phrasing-neutral fix + future-plan handling)\n")
    for rep, (text, tags) in enumerate(risk_runs, start=1):
        parts.append(f"\n### Repeat {rep}\n\n{text}\n\nParsed tags: {tags}\n")

    return "\n".join(parts)


def render_consistency_md(verdicts_and_tags):
    parts = [
        f"# {CONSISTENCY_PROBE['slug']}\n",
        f"Decision: {CONSISTENCY_PROBE['title']}\n",
        f"\nRisk profile: {CONSISTENCY_PROBE['risk_profile']}\n",
        f"\n## Item (deliberately ambiguous -- RISK or WORK_ITEM are both defensible)\n\n{CONSISTENCY_PROBE['items'][0]['text']}\n",
        f"\n## {CONSISTENCY_REPS} independent classifications\n",
    ]
    for rep, (text, tag) in enumerate(verdicts_and_tags, start=1):
        parts.append(f"\n### Repeat {rep}: **{tag}**\n\n{text}\n")
    return "\n".join(parts)


def score(scenario, risk_runs):
    items = scenario["items"]
    ground_truth = [it["ground_truth"] for it in items]
    per_item_tags = list(zip(*[tags for _, tags in risk_runs]))

    def indices_for(gt_value):
        return [i for i, gt in enumerate(ground_truth) if gt == gt_value]

    def rate(indices, target_tag):
        if not indices:
            return None
        hits = sum(1 for i in indices for tag in per_item_tags[i] if tag == target_tag)
        total = sum(len(per_item_tags[i]) for i in indices)
        return hits / total

    risk_items = indices_for("RISK")
    work_item_items = indices_for("WORK_ITEM")
    blocking_items = indices_for("BLOCKING")

    result = {
        "risk_recall": rate(risk_items, "RISK"),
        "work_item_recall": rate(work_item_items, "WORK_ITEM"),
        "false_defer_rate": rate(blocking_items, "RISK"),
        "false_work_item_rate": rate(blocking_items, "WORK_ITEM"),
        "correct_blocking_rate": rate(blocking_items, "BLOCKING"),
        "per_item_tags": [list(t) for t in per_item_tags],
        "per_item_consistent": [len(set(per_item_tags[i])) == 1 for i in range(len(items))],
    }

    phrasing_prefixes = PHRASING_SENSITIVE_ITEMS.get(scenario["slug"])
    if phrasing_prefixes:
        carryover = {}
        for i, it in enumerate(items):
            for prefix in phrasing_prefixes:
                if it["text"].startswith(prefix):
                    carryover[prefix] = per_item_tags[i]
        result["phrasing_sensitive_carryover"] = carryover

    return result


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in ROUND2_SCENARIOS:
        slug = scenario["slug"]

        baseline_runs = []
        for rep in range(REPS):
            print(f"[{slug}] round-1 4-way (no WORK_ITEM), repeat {rep + 1}...", file=sys.stderr)
            baseline_runs.append(run_classify_4way_with_risk(scenario))

        risk_runs = []
        for rep in range(REPS):
            print(f"[{slug}] round-2 5-way (with WORK_ITEM), repeat {rep + 1}...", file=sys.stderr)
            risk_runs.append(run_classify_5way_with_work_item(scenario))

        (RUNS_DIR / f"{slug}-round2.md").write_text(render_md(scenario, baseline_runs, risk_runs))

        scored = score(scenario, risk_runs)
        print(
            f"[{slug}] risk_recall={scored['risk_recall']} work_item_recall={scored['work_item_recall']} "
            f"false_defer_rate={scored['false_defer_rate']} false_work_item_rate={scored['false_work_item_rate']}",
            file=sys.stderr,
        )

        summary.append({"slug": slug, **scored})

    print("[consistency-probe] running 8 independent classifications of one ambiguous item...", file=sys.stderr)
    consistency_results = []
    for rep in range(CONSISTENCY_REPS):
        text, tags = run_classify_5way_with_work_item(CONSISTENCY_PROBE)
        consistency_results.append((text, tags[0]))
        print(f"[consistency-probe] repeat {rep + 1}: {tags[0]}", file=sys.stderr)

    (RUNS_DIR / "consistency-probe-round2.md").write_text(render_consistency_md(consistency_results))
    consistency_tags = [tag for _, tag in consistency_results]
    consistency_summary = {
        "slug": "consistency-probe",
        "tags_across_reps": consistency_tags,
        "distinct_tags_used": sorted(set(consistency_tags)),
        "consistent": len(set(consistency_tags)) == 1,
    }
    print(f"[consistency-probe] distribution: {consistency_tags}", file=sys.stderr)

    (RUNS_DIR / "summary_round2.json").write_text(
        json.dumps({"scenarios": summary, "consistency_probe": consistency_summary}, indent=2)
    )
    print(json.dumps({"scenarios": summary, "consistency_probe": consistency_summary}, indent=2))


if __name__ == "__main__":
    main()
