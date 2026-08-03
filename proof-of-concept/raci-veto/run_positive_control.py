"""Runs ONLY the Concur check -- no propose, no contest, no classify/revise --
against hand-authored fixtures engineered to leave nothing for Concur to
object to on its own named grounds (positive_control_scenarios.py). Isolates
one question: can Concur say CONCUR at all, on content that concretely
answers every real objection it raised in run 2, or does it object
regardless of what it's shown?

Deliberately bypasses `run_mechanism`/`_contest`/`_propose` -- those introduce
the exact sampling variance that made the ordinary runs ambiguous. This run
holds the input fixed and repeats only the Concur call, the same 3x
consistency check used everywhere else in this PoC.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_concur_repeats
from positive_control_scenarios import POSITIVE_CONTROL_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def render_md(scenario, verdicts, concurs):
    parts = [
        f"# {scenario['slug']}\n",
        f"Decision: {scenario['title']}\n",
        f"\nConcur role (cold, own grounds only): {scenario['concur_role']} -- {scenario['concur_grounds']}\n",
        f"\n## Grounded in (real objections this fixture is built to close)\n\n{scenario['grounded_in']}\n",
        f"\n## Hand-authored final decision fixture (not owner-generated)\n\n{scenario['final_decision_fixture']}\n",
        f"\n## Concur check (3x, cold)\n",
    ]
    for i, (verdict, concurs_flag) in enumerate(zip(verdicts, concurs), start=1):
        parts.append(f"\n### Repeat {i}: {'CONCUR' if concurs_flag else 'DO NOT CONCUR'}\n\n{verdict}\n")
    parts.append(
        f"\n### Consistency across {len(concurs)} repeats: "
        f"**{'CONSISTENT' if len(set(concurs)) == 1 else 'INCONSISTENT'}**\n"
    )
    parts.append(f"\n### Did Concur approve at least once? **{'YES' if any(concurs) else 'NO'}**\n")
    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in POSITIVE_CONTROL_SCENARIOS:
        slug = scenario["slug"]
        print(f"[{slug}] concur check (3 repeats) on hand-authored fixture...", file=sys.stderr)
        verdicts, concurs = run_concur_repeats(scenario, scenario["final_decision_fixture"], n=3)
        print(f"[{slug}] concur verdicts: {concurs}", file=sys.stderr)

        (RUNS_DIR / f"{slug}.md").write_text(render_md(scenario, verdicts, concurs))

        summary.append(
            {
                "slug": slug,
                "concur_role": scenario["concur_role"],
                "concur_verdicts": concurs,
                "concur_consistent": len(set(concurs)) == 1,
                "concur_approved_at_least_once": any(concurs),
            }
        )

    (RUNS_DIR / "positive_control_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
