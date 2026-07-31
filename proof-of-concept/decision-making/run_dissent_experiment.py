"""Run the rigged-dissent lifecycle for every decision and write transcripts under runs/."""

import json
import sys
import time
from pathlib import Path

from decisions import DECISIONS
from lifecycle_dissent import run_dissent_lifecycle

RUNS_DIR = Path(__file__).parent / "runs"


def render_dissent_md(decision, t):
    dissent = decision["dissent"]
    parts = [
        f"# Rigged dissent — {decision['title']}\n",
        f"Dissenting role: {dissent['role']} (Qwen2.5-7B-Instruct)\n",
        f"\n## Fixed non-negotiable objection given to {dissent['role']}\n\n{dissent['objection']}\n",
        f"\n## 1. Proposed (owner)\n\n{t['proposal']}\n",
        "\n## 2. Contested (challengers, one rigged)\n",
    ]
    for role, text in t["issues"].items():
        parts.append(f"\n### {role}\n\n{text}\n")
    parts.append(f"\n## 3. Refuted / classified (round 1)\n\n{t['classification_round_1']}\n")
    if t["rounds"] == 1:
        parts.append(f"\n## 4. Revised (owner)\n\n{t['revised_proposal']}\n")
        parts.append(f"\n## 5. Dissenter's own reaction to the revision\n\n{t['dissenter_reaction']}\n")
        parts.append(f"\n## 6. Refuter re-classification (round 2)\n\n{t['classification_round_2']}\n")
        parts.append(
            f"\n## Refuter vs. dissenter agreement\n\n"
            f"Dissenter satisfied: {t['dissenter_satisfied']} | "
            f"Refuter says converged: {t['state'] == 'converged'} | "
            f"Agree: {t['refuter_dissenter_agree']}\n"
        )
    parts.append(f"\n## Outcome\n\nState: **{t['state']}**\n\nConfidence: {t['confidence']}\n")
    parts.append(f"\n## Final decision text\n\n{t['final_decision']}\n")
    return "\n".join(parts)


def main():
    summary = []
    for decision in DECISIONS:
        slug = decision["slug"]
        out_dir = RUNS_DIR / slug
        out_dir.mkdir(exist_ok=True)
        print(f"[{slug}] dissent lifecycle...", file=sys.stderr)
        t0 = time.time()
        result = run_dissent_lifecycle(decision)
        seconds = time.time() - t0
        (out_dir / "dissent.md").write_text(render_dissent_md(decision, result))

        record = {
            "slug": slug,
            "state": result["state"],
            "rounds": result["rounds"],
            "confidence": result["confidence"],
            "dissenter_satisfied": result.get("dissenter_satisfied"),
            "refuter_dissenter_agree": result.get("refuter_dissenter_agree"),
            "seconds": round(seconds, 1),
        }
        summary.append(record)
        (out_dir / "dissent_summary.json").write_text(json.dumps(record, indent=2))
        print(f"[{slug}] done: {record}", file=sys.stderr)

    (RUNS_DIR / "dissent_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
