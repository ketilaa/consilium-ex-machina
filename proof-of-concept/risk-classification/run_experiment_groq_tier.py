"""Model-tiering test: does a genuinely stronger model (Groq-hosted
openai/gpt-oss-120b, ~120B params) fix the RISK/WORK_ITEM classification
failures found in rounds 2-3 against our local ~24B quantized model, or do
they persist regardless of model?

Same classifier prompt (`classifier_system_5way_with_work_item`), same
scenarios and items (`scenarios_round2.py`), same scoring -- only the model
differs. This is the direct test for whether round 2-3's open failures are
a model-capability limit or a mechanism limit, a question this PoC has
flagged as untested from its very first round.

Economical on purpose: 1 pass per scenario, not the usual 3 reps, given the
Groq key used for this test is short-lived. A single pass can't establish
consistency the way the rest of this PoC series does, but it can establish
direction -- does the stronger model land on the right answer at all, even
once, where the local model consistently didn't across 3 reps.
"""

import json
import sys
import time
from pathlib import Path

from lifecycle import TAG_RE_5WAY, _brief, _items_text, _parse_tags_positional
from llm_client import GROQ_MODEL, chat
from roles import classifier_system_5way_with_work_item
from scenarios_round2 import ROUND2_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def classify_with_groq(scenario, retries=2):
    items = scenario["items"]
    system = classifier_system_5way_with_work_item(scenario["risk_profile"])
    # gpt-oss-120b spends substantial tokens on hidden reasoning before any visible
    # output -- a smoke test needed 50 reasoning tokens just to answer "OK" -- so the
    # budget here is generously oversized relative to the local model's 1400, to avoid
    # the exact silent-truncation failure mode already found once in this project
    # (d-22ffab13's revision cut off mid-sentence from too small a max_tokens).
    last_error = None
    for attempt in range(retries + 1):
        result = chat(
            GROQ_MODEL,
            system,
            f"{_brief(scenario)}\n\nRaised items:\n{_items_text(items)}",
            max_tokens=4000,
            timeout=120,
        )
        if result.get("ok"):
            tags = _parse_tags_positional(result["content"], len(items), TAG_RE_5WAY, separator="_")
            return result["content"], tags
        last_error = result
        print(f"  (attempt {attempt + 1} failed: {result}; retrying)", file=sys.stderr)
        time.sleep(3)
    raise RuntimeError(f"Groq call failed after {retries + 1} attempts: {last_error}")


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    batch_summary = json.loads((RUNS_DIR / "summary_round2.json").read_text())
    local_tags_by_slug = {s["slug"]: s["per_item_tags"] for s in batch_summary["scenarios"]}

    summary = []
    transcript_parts = [f"# Model-tiering test: {GROQ_MODEL['model']} vs. local model\n"]

    for scenario in ROUND2_SCENARIOS:
        slug = scenario["slug"]
        print(f"[{slug}] classifying with {GROQ_MODEL['model']}...", file=sys.stderr)
        text, groq_tags = classify_with_groq(scenario)
        print(f"[{slug}] groq_tags={groq_tags}", file=sys.stderr)

        local_tags_per_item = local_tags_by_slug[slug]
        ground_truths = [it["ground_truth"] for it in scenario["items"]]

        transcript_parts.append(f"\n## {slug}\n")
        transcript_parts.append(f"\nRisk profile: {scenario['risk_profile']}\n")
        transcript_parts.append(f"\n### Groq classification\n\n{text}\n")

        item_rows = []
        for i, item in enumerate(scenario["items"]):
            gt = item["ground_truth"]
            groq_tag = groq_tags[i]
            local_majority = max(set(local_tags_per_item[i]), key=local_tags_per_item[i].count)
            row = {
                "item_index": i,
                "ground_truth": gt,
                "local_tags_3x": local_tags_per_item[i],
                "groq_tag_1x": groq_tag,
                "local_majority_correct": (local_majority == gt) if gt else None,
                "groq_correct": (groq_tag == gt) if gt else None,
            }
            item_rows.append(row)
            transcript_parts.append(
                f"\n- Item {i + 1}: ground truth **{gt or 'AMBIGUOUS'}** | "
                f"local (3x): {local_tags_per_item[i]} | groq (1x): **{groq_tag}**\n"
            )

        summary.append({"slug": slug, "items": item_rows})

    (RUNS_DIR / "groq-tier-test.md").write_text("\n".join(transcript_parts))
    (RUNS_DIR / "summary_groq_tier.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
