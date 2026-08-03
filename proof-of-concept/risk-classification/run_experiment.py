"""Runs both classifiers against every scenario's fixed, pre-registered item
set, 3 reps each for consistency, and scores the 4-way classifier against
ground truth on the two axes that matter:

- risk_recall: of items truly disproportionate (ground truth RISK), what
  fraction get classified RISK?
- false_defer_rate: of items that must stay BLOCKING regardless of risk
  profile (ground truth BLOCKING), what fraction get incorrectly swept into
  RISK? This is the overshoot failure mode and the more important number --
  a classifier that never uses RISK is merely useless; one with a high
  false-defer rate is actively dangerous, letting real gaps go untracked as
  mere "acceptable risk".

The 3-way baseline is run too, to show what a genuinely disproportionate
item is classified as TODAY, with no RISK option available.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_classify_3way, run_classify_4way_with_risk
from scenarios import SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"
REPS = 3


def render_md(scenario, baseline_runs, risk_runs):
    items = scenario["items"]
    parts = [
        f"# {scenario['slug']}\n",
        f"Decision: {scenario['title']}\n",
        f"\nRisk profile: {scenario['risk_profile']}\n",
        "\n## Items (fixed, pre-registered ground truth)\n",
    ]
    for i, it in enumerate(items, start=1):
        parts.append(f"\n### Item {i} ({it['role']}) -- ground truth: **{it['ground_truth']}**\n\n{it['text']}\n")

    parts.append("\n## Mechanism A: baseline 3-way classifier (no RISK option)\n")
    for rep, (text, tags) in enumerate(baseline_runs, start=1):
        parts.append(f"\n### Repeat {rep}\n\n{text}\n\nParsed tags: {tags}\n")

    parts.append("\n## Mechanism B: 4-way classifier with RISK option + risk profile\n")
    for rep, (text, tags) in enumerate(risk_runs, start=1):
        parts.append(f"\n### Repeat {rep}\n\n{text}\n\nParsed tags: {tags}\n")

    return "\n".join(parts)


def score(scenario, risk_runs):
    items = scenario["items"]
    ground_truth = [it["ground_truth"] for it in items]

    per_item_tags = list(zip(*[tags for _, tags in risk_runs]))  # tags across reps, per item

    risk_items = [i for i, gt in enumerate(ground_truth) if gt == "RISK"]
    blocking_items = [i for i, gt in enumerate(ground_truth) if gt == "BLOCKING"]

    def rate(indices, target_tag):
        if not indices:
            return None
        hits = sum(1 for i in indices for tag in per_item_tags[i] if tag == target_tag)
        total = sum(len(per_item_tags[i]) for i in indices)
        return hits / total

    risk_recall = rate(risk_items, "RISK")
    false_defer_rate = rate(blocking_items, "RISK")
    correct_blocking_rate = rate(blocking_items, "BLOCKING")

    per_item_consistency = [len(set(per_item_tags[i])) == 1 for i in range(len(items))]

    return {
        "risk_recall": risk_recall,
        "false_defer_rate": false_defer_rate,
        "correct_blocking_rate": correct_blocking_rate,
        "per_item_tags": [list(t) for t in per_item_tags],
        "per_item_consistent": per_item_consistency,
    }


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in SCENARIOS:
        slug = scenario["slug"]

        baseline_runs = []
        for rep in range(REPS):
            print(f"[{slug}] baseline 3-way, repeat {rep + 1}...", file=sys.stderr)
            baseline_runs.append(run_classify_3way(scenario))

        risk_runs = []
        for rep in range(REPS):
            print(f"[{slug}] 4-way with risk, repeat {rep + 1}...", file=sys.stderr)
            risk_runs.append(run_classify_4way_with_risk(scenario))

        (RUNS_DIR / f"{slug}.md").write_text(render_md(scenario, baseline_runs, risk_runs))

        scored = score(scenario, risk_runs)
        print(f"[{slug}] risk_recall={scored['risk_recall']} false_defer_rate={scored['false_defer_rate']}", file=sys.stderr)

        summary.append({"slug": slug, **scored})

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
