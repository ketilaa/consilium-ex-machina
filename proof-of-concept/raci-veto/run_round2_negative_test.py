"""Runs round 2 of the recheck variant in isolation (fixed concern, no fresh
round 1 call) against two fixtures per scenario that should NOT satisfy the
concern -- the load-bearing negative case poc-raci-veto.md's Verdict named as
untested. 3 reps per fixture per scenario, the same consistency-check
discipline as every other Concur test in this PoC.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_concur_recheck_round2_repeats
from round2_negative_scenarios import ROUND2_NEGATIVE_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def render_md(scenario, no_attempt_results, vague_results):
    parts = [
        f"# {scenario['slug']} -- round 2 negative-case test\n",
        f"Decision: {scenario['title']}\n",
        f"\nConcur role: {scenario['concur_role']} -- {scenario['concur_grounds']}\n",
        f"\n## Round 1 concern (fixed, reused verbatim from the earlier three-way run)\n\n{scenario['round1_concern']}\n",
    ]

    for label, key, results in [
        ("No-attempt control (unchanged negative fixture)", "no_attempt_revision", no_attempt_results),
        ("Vague-gesture stress test", "vague_gesture_revision", vague_results),
    ]:
        verdicts, concurs = results
        parts.append(f"\n## {label}\n\n{scenario[key]}\n")
        parts.append("\n### Round 2 recheck verdicts (3x)\n")
        for i, (v, c) in enumerate(zip(verdicts, concurs), start=1):
            parts.append(f"\n**Repeat {i}: {'CONCUR' if c else 'DO NOT CONCUR'}**\n\n{v}\n")
        correctly_rejected = not any(concurs)
        parts.append(
            f"\n**Correctly still rejected all 3? {'YES' if correctly_rejected else 'NO -- approved at least once (FALSE POSITIVE)'}** "
            f"(consistency: {'CONSISTENT' if len(set(concurs)) == 1 else 'INCONSISTENT'})\n"
        )

    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in ROUND2_NEGATIVE_SCENARIOS:
        slug = scenario["slug"]

        print(f"[{slug}] round2 vs no-attempt revision...", file=sys.stderr)
        no_attempt_results = run_concur_recheck_round2_repeats(
            scenario, scenario["round1_concern"], scenario["no_attempt_revision"], n=3
        )
        print(f"[{slug}] no-attempt concurs={no_attempt_results[1]}", file=sys.stderr)

        print(f"[{slug}] round2 vs vague-gesture revision...", file=sys.stderr)
        vague_results = run_concur_recheck_round2_repeats(
            scenario, scenario["round1_concern"], scenario["vague_gesture_revision"], n=3
        )
        print(f"[{slug}] vague-gesture concurs={vague_results[1]}", file=sys.stderr)

        (RUNS_DIR / f"{slug}-round2-negative.md").write_text(render_md(scenario, no_attempt_results, vague_results))

        summary.append(
            {
                "slug": slug,
                "no_attempt_concurs": no_attempt_results[1],
                "no_attempt_false_positive": any(no_attempt_results[1]),
                "vague_gesture_concurs": vague_results[1],
                "vague_gesture_false_positive": any(vague_results[1]),
            }
        )

    (RUNS_DIR / "round2_negative_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
