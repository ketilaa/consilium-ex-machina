"""Round 3: isolates specific items from round 2's batches and reclassifies
them ALONE, testing three distinct hypotheses about what actually caused
round 2's failures -- not one blind re-tweak of the same 5-way prompt.

- **Hypothesis 1 (batching):** role-registry-configurability's items 4-6
  (RISK, RISK, WORK_ITEM) got near-identical boilerplate and inconsistent
  tags when classified together with three other, topically-similar items
  about the same roles.yaml artifact. Does isolating each one, away from its
  topically-similar neighbors, fix the confusion? Controls: items from other
  scenarios that were ALREADY correct and consistent in batch (payments-
  webhook-handler's RISK/WORK_ITEM items, internal-analytics-dashboard's
  RISK/WORK_ITEM items that succeeded) -- isolation should not break these.
- **Hypothesis 2 (phrasing, not batching):** internal-analytics-dashboard's
  two flatly-phrased items ("has no rate limiting", "is not encrypted")
  failed in round 1 AND round 2's small, non-clustered batch -- if isolation
  fixes hypothesis 1's items but NOT these, that's evidence the phrasing bug
  and the batching-conflation bug are genuinely different problems, not the
  same thing wearing two faces.
- **Hypothesis 3 (spillover):** pilot-program-customer-portal's item 3
  (support tooling, ground truth WORK_ITEM) was classified BLOCKING in
  batch, using reasoning borrowed from item 1's "already-committed external
  launch" framing. Isolating it -- removing item 1 from the context
  entirely -- directly tests whether that borrowed reasoning was caused by
  the adjacent item's presence, or whether the model reaches the same
  (miscalibrated) conclusion even alone, from the risk profile text itself.

Reuses round 2's exact items and ground truth (`scenarios_round2.py`) and
round 2's exact batch results (`runs/summary_round2.json`) for direct
before/after comparison -- no new items, no new scenarios, only a new
mechanism (isolated single-item classification) applied to already-known
cases.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_classify_5way_isolated
from scenarios_round2 import ROUND2_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"
REPS = 3

# (scenario_slug, item_index, hypothesis_label)
TEST_ITEMS = [
    # Hypothesis 1: batching-induced confusion (the actual failures)
    ("role-registry-configurability", 3, "H1-broken"),  # RISK, got WORK_ITEM/RISK/WORK_ITEM
    ("role-registry-configurability", 4, "H1-broken"),  # RISK, got RISK/RISK/WORK_ITEM
    ("role-registry-configurability", 5, "H1-broken"),  # WORK_ITEM, got WORK_ITEM/WORK_ITEM/RISK
    # Hypothesis 1 controls: already correct+consistent in batch, isolation shouldn't break these
    ("payments-webhook-handler", 2, "H1-control"),  # RISK, got RISK/RISK/RISK
    ("payments-webhook-handler", 4, "H1-control"),  # WORK_ITEM, got WORK_ITEM x3
    ("internal-analytics-dashboard", 3, "H1-control"),  # RISK, got RISK x3
    ("internal-analytics-dashboard", 4, "H1-control"),  # WORK_ITEM, got WORK_ITEM x3
    # Hypothesis 2: the phrasing bug -- is it fixed by isolation, or independent of batching?
    ("internal-analytics-dashboard", 0, "H2-phrasing"),  # RISK, got BLOCKING x3
    ("internal-analytics-dashboard", 1, "H2-phrasing"),  # RISK, got BLOCKING x3
    # Hypothesis 3: spillover from an adjacent item's reasoning
    ("pilot-program-customer-portal", 1, "H3-spillover-context"),  # RISK (ambiguous gt), got WORK_ITEM x3
    ("pilot-program-customer-portal", 2, "H3-spillover"),  # WORK_ITEM, got BLOCKING x3 (the actual spillover case)
]

SCENARIOS_BY_SLUG = {s["slug"]: s for s in ROUND2_SCENARIOS}


def render_md(rows):
    parts = ["# Round 3: isolated single-item classification\n"]
    for row in rows:
        parts.append(f"\n## {row['scenario_slug']} / item {row['item_index'] + 1} ({row['hypothesis']})\n")
        parts.append(f"\nGround truth: **{row['ground_truth'] or 'AMBIGUOUS'}**\n")
        parts.append(f"\nItem text:\n\n{row['item_text']}\n")
        parts.append(f"\nBatch result (round 2, classified alongside its scenario's other items): {row['batch_tags']}\n")
        parts.append("\n### Isolated classifications (3x, alone, no other items present)\n")
        for i, (text, tag) in enumerate(row["isolated_results"], start=1):
            parts.append(f"\n**Repeat {i}: {tag}**\n\n{text}\n")
        parts.append(f"\nIsolated tags: {[t for _, t in row['isolated_results']]}\n")
        parts.append(f"\nIsolation changed the outcome? **{'YES' if row['changed'] else 'NO'}**\n")
    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    batch_summary = json.loads((RUNS_DIR / "summary_round2.json").read_text())
    batch_tags_by_slug = {s["slug"]: s["per_item_tags"] for s in batch_summary["scenarios"]}

    rows = []
    for slug, item_index, hypothesis in TEST_ITEMS:
        scenario = SCENARIOS_BY_SLUG[slug]
        item = scenario["items"][item_index]
        batch_tags = batch_tags_by_slug[slug][item_index]

        print(f"[{slug}] item {item_index + 1} ({hypothesis}): classifying isolated, 3 reps...", file=sys.stderr)
        isolated_results = []
        for rep in range(REPS):
            text, tag = run_classify_5way_isolated(scenario, item)
            isolated_results.append((text, tag))
        isolated_tags = [t for _, t in isolated_results]
        print(f"[{slug}] item {item_index + 1}: batch={batch_tags} isolated={isolated_tags}", file=sys.stderr)

        rows.append(
            {
                "scenario_slug": slug,
                "item_index": item_index,
                "hypothesis": hypothesis,
                "ground_truth": item["ground_truth"],
                "item_text": item["text"],
                "batch_tags": batch_tags,
                "isolated_results": isolated_results,
                "changed": set(batch_tags) != set(isolated_tags) or len(set(batch_tags)) != len(set(isolated_tags)),
            }
        )

    (RUNS_DIR / "round3-isolated-items.md").write_text(render_md(rows))

    summary = []
    for row in rows:
        isolated_tags = [t for _, t in row["isolated_results"]]
        gt = row["ground_truth"]
        summary.append(
            {
                "scenario_slug": row["scenario_slug"],
                "item_index": row["item_index"],
                "hypothesis": row["hypothesis"],
                "ground_truth": gt,
                "batch_tags": row["batch_tags"],
                "batch_correct_count": sum(1 for t in row["batch_tags"] if t == gt) if gt else None,
                "isolated_tags": isolated_tags,
                "isolated_correct_count": sum(1 for t in isolated_tags if t == gt) if gt else None,
                "isolated_consistent": len(set(isolated_tags)) == 1,
            }
        )

    (RUNS_DIR / "summary_round3.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
