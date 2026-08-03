"""Runs all three Concur variants against the same paired fixtures, in one pass:

A. Original (`concur_system`) -- the mechanism the positive control (run 3)
   already tested; re-run fresh here so all three variants are compared under
   identical, freshly-sampled conditions in the same pass rather than mixing
   in older data.
B. Sufficiency criterion (`concur_system_with_sufficiency`) -- one added
   paragraph naming an explicit stopping condition; no structural change.
C. Recheck (`run_concur_recheck`) -- structural, not just an instruction:
   round 1 states a single concrete concern against the thin (negative)
   fixture; round 2 checks ONLY that concern against the thorough (positive)
   fixture, forbidden from raising anything new.

A and B are tested against BOTH fixtures per scenario -- does it ever approve
the thorough one, does it still correctly reject the thin one (a "fix" that
just rubber-stamps everything is the opposite failure mode, equally bad). C is
inherently a before/after pair: the thin fixture is what round 1 reviews, the
thorough fixture stands in for "the revision" round 2 is shown -- a natural
pairing since the thorough fixture already concretely improves on the thin one
on the Concur-holder's own named grounds.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_concur_recheck, run_concur_repeats
from roles import concur_system, concur_system_with_sufficiency
from sufficiency_test_scenarios import SUFFICIENCY_TEST_SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def render_md(scenario, results):
    parts = [
        f"# {scenario['slug']} -- three-way Concur comparison\n",
        f"Decision: {scenario['title']}\n",
        f"\nConcur role (cold, own grounds only): {scenario['concur_role']} -- {scenario['concur_grounds']}\n",
        f"\n## Positive fixture (thorough)\n\n{scenario['positive_fixture']}\n",
        f"\n## Negative fixture (thin, real)\n\n{scenario['negative_fixture']}\n",
    ]
    if "negative_fixture_source" in scenario:
        parts.append(f"\n(Negative fixture source: {scenario['negative_fixture_source']})\n")

    for variant_label, variant_key in [("A: Original prompt", "original"), ("B: Sufficiency criterion", "sufficiency")]:
        parts.append(f"\n## Variant {variant_label}\n")
        for fixture_label in ["positive", "negative"]:
            verdicts = results[variant_key][fixture_label]["verdicts"]
            concurs = results[variant_key][fixture_label]["concurs"]
            parts.append(f"\n### Against {fixture_label} fixture\n")
            for i, (v, c) in enumerate(zip(verdicts, concurs), start=1):
                parts.append(f"\n**Repeat {i}: {'CONCUR' if c else 'DO NOT CONCUR'}**\n\n{v}\n")
            parts.append(
                f"\n**Approved at least once? {'YES' if any(concurs) else 'NO'}** "
                f"(consistency: {'CONSISTENT' if len(set(concurs)) == 1 else 'INCONSISTENT'})\n"
            )

    parts.append(
        "\n## Variant C: Recheck (round 1 on negative fixture, round 2 checks "
        "only that concern against positive fixture)\n"
    )
    for i, r in enumerate(results["recheck"], start=1):
        parts.append(f"\n### Repeat {i}\n")
        parts.append(f"\nRound 1 ({'CONCUR' if r['round1_concurs'] else 'DO NOT CONCUR'}):\n\n{r['round1_verdict']}\n")
        if r["round2_verdict"] is not None:
            parts.append(
                f"\nRound 2 recheck ({'CONCUR' if r['round2_concurs'] else 'DO NOT CONCUR'}):\n\n{r['round2_verdict']}\n"
            )
        else:
            parts.append("\nRound 2: skipped (round 1 already concurred)\n")
    recheck_final = [r["final_concurs"] for r in results["recheck"]]
    parts.append(
        f"\n**Final concurred at least once? {'YES' if any(recheck_final) else 'NO'}** "
        f"(consistency: {'CONSISTENT' if len(set(recheck_final)) == 1 else 'INCONSISTENT'})\n"
    )

    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in SUFFICIENCY_TEST_SCENARIOS:
        slug = scenario["slug"]
        results = {"original": {}, "sufficiency": {}, "recheck": []}

        for variant_key, prompt_fn in [("original", concur_system), ("sufficiency", concur_system_with_sufficiency)]:
            for fixture_label, fixture_key in [("positive", "positive_fixture"), ("negative", "negative_fixture")]:
                print(f"[{slug}] variant={variant_key} fixture={fixture_label}...", file=sys.stderr)
                verdicts, concurs = run_concur_repeats(
                    scenario, scenario[fixture_key], n=3, concur_prompt_fn=prompt_fn
                )
                results[variant_key][fixture_label] = {"verdicts": verdicts, "concurs": concurs}
                print(f"[{slug}] variant={variant_key} fixture={fixture_label} concurs={concurs}", file=sys.stderr)

        for i in range(3):
            print(f"[{slug}] variant=recheck repeat {i + 1}...", file=sys.stderr)
            r = run_concur_recheck(scenario, scenario["negative_fixture"], scenario["positive_fixture"])
            results["recheck"].append(r)
            print(f"[{slug}] variant=recheck repeat {i + 1} final_concurs={r['final_concurs']}", file=sys.stderr)

        (RUNS_DIR / f"{slug}-three-way-concur.md").write_text(render_md(scenario, results))

        summary.append(
            {
                "slug": slug,
                "original_positive_approved_at_least_once": any(results["original"]["positive"]["concurs"]),
                "original_negative_approved_at_least_once": any(results["original"]["negative"]["concurs"]),
                "sufficiency_positive_approved_at_least_once": any(results["sufficiency"]["positive"]["concurs"]),
                "sufficiency_negative_approved_at_least_once": any(results["sufficiency"]["negative"]["concurs"]),
                "recheck_final_concurred_at_least_once": any(r["final_concurs"] for r in results["recheck"]),
                "recheck_final_concurs": [r["final_concurs"] for r in results["recheck"]],
            }
        )

    (RUNS_DIR / "three_way_concur_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
