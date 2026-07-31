"""Run baseline vs lifecycle for every decision and write transcripts under runs/."""

import json
import sys
import time
from pathlib import Path

from baseline import run_baseline
from decisions import DECISIONS
from lifecycle import run_lifecycle

RUNS_DIR = Path(__file__).parent / "runs"


def render_baseline_md(decision, result):
    return (
        f"# Baseline — {decision['title']}\n\n"
        f"Model: Qwen2.5-Coder-14B-Instruct (single agent, no lifecycle)\n\n"
        f"## Answer\n\n{result['answer']}\n"
    )


def render_lifecycle_md(decision, t):
    parts = [
        f"# Lifecycle — {decision['title']}\n",
        f"Category: {decision['category']}\n",
        f"Owner role: {decision['owner_role']} (Qwen2.5-Coder-14B-Instruct)\n",
        f"Challenger roles: {', '.join(decision['challenger_roles'])} (Qwen2.5-7B-Instruct)\n",
        f"Refuter: Qwen2.5-7B-Instruct\n",
        f"\n## 1. Proposed (owner)\n\n{t['proposal']}\n",
        "\n## 2. Contested (challengers)\n",
    ]
    for role, text in t["issues"].items():
        parts.append(f"\n### {role}\n\n{text}\n")
    parts.append(f"\n## 3. Refuted / classified (round 1)\n\n{t['classification_round_1']}\n")
    if t["rounds"] == 1:
        parts.append(f"\n## 4. Revised (owner)\n\n{t['revised_proposal']}\n")
        parts.append(f"\n## 5. Re-classified (round 2)\n\n{t['classification_round_2']}\n")
    parts.append(f"\n## Outcome\n\nState: **{t['state']}**\n\nConfidence: {t['confidence']}\n")
    parts.append(f"\n## Final decision text\n\n{t['final_decision']}\n")
    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for decision in DECISIONS:
        slug = decision["slug"]
        out_dir = RUNS_DIR / slug
        out_dir.mkdir(exist_ok=True)
        print(f"[{slug}] baseline...", file=sys.stderr)
        t0 = time.time()
        baseline_result = run_baseline(decision)
        baseline_seconds = time.time() - t0
        (out_dir / "baseline.md").write_text(render_baseline_md(decision, baseline_result))

        print(f"[{slug}] lifecycle...", file=sys.stderr)
        t0 = time.time()
        lifecycle_result = run_lifecycle(decision)
        lifecycle_seconds = time.time() - t0
        (out_dir / "lifecycle.md").write_text(render_lifecycle_md(decision, lifecycle_result))

        record = {
            "slug": slug,
            "state": lifecycle_result["state"],
            "rounds": lifecycle_result["rounds"],
            "confidence": lifecycle_result["confidence"],
            "baseline_seconds": round(baseline_seconds, 1),
            "lifecycle_seconds": round(lifecycle_seconds, 1),
        }
        summary.append(record)
        (out_dir / "summary.json").write_text(json.dumps(record, indent=2))
        print(f"[{slug}] done: {record}", file=sys.stderr)

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
