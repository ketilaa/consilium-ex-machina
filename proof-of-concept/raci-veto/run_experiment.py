"""Runs, per scenario:

1. One proposal, one round of contest from Responsible + Consulted + Informed
   together (so baseline and raci share identical reactions for the two roles
   they have in common -- the only variable between them is whether Informed's
   reaction is included).
2. `baseline` mechanism: classify/revise/recheck over R+C+I (today's world,
   no RACI concept).
3. `raci` mechanism: classify/revise/recheck over R+C only.
4. Redundancy judgment: does I's reaction (elicited in step 1, fed into
   baseline but withheld from raci) raise a materially new concern beyond what
   R+C already cover?
5. Concur check (single + 3 repeats for consistency) against raci's own final
   decision, cold, from a role that held no pen during 1-4.

Two independent signals for question 1 (participation): does baseline's
terminal state differ from raci's, and does the redundancy judge call I's
reaction NEW. Two independent signals for question 2 (concur): does Concur
ever diverge from a raci outcome of "converged", and is that divergence
consistent across the 3 repeats (question 3) or scattershot.
"""

import json
import sys
from pathlib import Path

from lifecycle import (
    _brief,
    _contest,
    _propose,
    judge_redundancy,
    run_concur_repeats,
    run_mechanism,
    shadow_reaction,
)
from scenarios import SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def render_md(scenario, proposal, baseline, raci, shadow_role, shadow_text, redundancy_verdict, is_new,
              concur_verdicts, concurs):
    parts = [
        f"# {scenario['slug']}\n",
        f"Decision: {scenario['title']}\n",
        f"\n## RACI assignment\n",
        f"\n- Accountable (owner): {scenario['owner_role']}\n",
        f"- Responsible: {scenario['responsible_role']}\n",
        f"- Consulted: {scenario['consulted_role']}\n",
        f"- Informed (excluded from contest under raci): {scenario['informed_role']}\n",
        f"- Concur (cold review, own grounds only): {scenario['concur_role']} -- {scenario['concur_grounds']}\n",
        f"\n## Proposal (owner)\n\n{proposal}\n",
        f"\n## Contest responses (shared between baseline and raci where roles overlap)\n",
    ]
    for role, text in baseline["raised"].items():
        parts.append(f"\n### {role}\n\n{text}\n")

    parts.append("\n## Mechanism A: baseline (Responsible + Consulted + Informed all as challengers)\n")
    parts.append(f"\n### Classification\n\n{baseline['classification_round_1']}\n")
    if baseline.get("rounds", 0) >= 1:
        parts.append(f"\n### Owner revision\n\n{baseline['revised_proposal']}\n")
        parts.append(f"\n### Per-raiser recheck\n\n{json.dumps(baseline['rechecks'], indent=2)}\n")
    parts.append(f"\n### Outcome: **{baseline['state']}**\n")

    parts.append("\n## Mechanism B: raci (Responsible + Consulted only; Informed excluded)\n")
    parts.append(f"\n### Classification\n\n{raci['classification_round_1']}\n")
    if raci.get("rounds", 0) >= 1:
        parts.append(f"\n### Owner revision\n\n{raci['revised_proposal']}\n")
        parts.append(f"\n### Per-raiser recheck\n\n{json.dumps(raci['rechecks'], indent=2)}\n")
    parts.append(f"\n### Outcome: **{raci['state']}**\n")

    parts.append(f"\n## Question 1: Informed role's shadow reaction ({shadow_role})\n")
    parts.append(f"\n{shadow_text}\n")
    parts.append(
        f"\n### Pre-registered expectation: **{scenario['expected_informed_signal'].upper()}**\n"
    )
    parts.append(f"\n### Redundancy judgment: **{'NEW' if is_new else 'REDUNDANT'}**\n\n{redundancy_verdict}\n")
    predicted_new = scenario["expected_informed_signal"] == "novel"
    parts.append(
        f"\n### Prediction matched judgment? **{'YES' if predicted_new == is_new else 'NO'}**\n"
    )
    parts.append(
        f"\n### Did excluding {shadow_role} change the terminal state? "
        f"baseline={baseline['state']} vs raci={raci['state']} -> "
        f"**{'DIFFERS' if baseline['state'] != raci['state'] else 'SAME'}**\n"
    )

    parts.append(f"\n## Question 2 & 3: Concur check on raci's final decision, cold ({scenario['concur_role']})\n")
    parts.append(f"\n(raci outcome being reviewed: **{raci['state']}**)\n")
    for i, (verdict, concurs_flag) in enumerate(zip(concur_verdicts, concurs), start=1):
        parts.append(f"\n### Repeat {i}: {'CONCUR' if concurs_flag else 'DO NOT CONCUR'}\n\n{verdict}\n")
    all_concur = all(concurs)
    parts.append(
        f"\n### Consistency across {len(concurs)} repeats: **{'CONSISTENT' if len(set(concurs)) == 1 else 'INCONSISTENT'}**\n"
    )
    parts.append(
        f"\n### Did Concur ever diverge from a clean raci convergence? "
        f"**{'YES' if raci['state'] == 'converged' and not all_concur else 'NO'}**\n"
    )

    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in SCENARIOS:
        slug = scenario["slug"]
        r, c, i = scenario["responsible_role"], scenario["consulted_role"], scenario["informed_role"]

        print(f"[{slug}] propose...", file=sys.stderr)
        proposal = _propose(scenario)

        print(f"[{slug}] contest (R+C+I)...", file=sys.stderr)
        all_raised = _contest(scenario, proposal, [r, c, i])
        raci_raised = {role: all_raised[role] for role in (r, c)}

        print(f"[{slug}] baseline mechanism...", file=sys.stderr)
        baseline = run_mechanism(scenario, proposal, all_raised, "baseline (R+C+I)")
        print(f"[{slug}] baseline outcome: {baseline['state']}", file=sys.stderr)

        print(f"[{slug}] raci mechanism...", file=sys.stderr)
        raci = run_mechanism(scenario, proposal, raci_raised, "raci (R+C only)")
        print(f"[{slug}] raci outcome: {raci['state']}", file=sys.stderr)

        print(f"[{slug}] informed role shadow reaction + redundancy judgment...", file=sys.stderr)
        shadow_role, shadow_text = i, all_raised[i]
        redundancy_verdict, is_new = judge_redundancy(scenario, raci_raised, shadow_role, shadow_text)
        print(f"[{slug}] redundancy judgment: {'NEW' if is_new else 'REDUNDANT'}", file=sys.stderr)

        print(f"[{slug}] concur check (3 repeats) on raci's final decision...", file=sys.stderr)
        concur_verdicts, concurs = run_concur_repeats(scenario, raci["final_decision"], n=3)
        print(f"[{slug}] concur verdicts: {concurs}", file=sys.stderr)

        (RUNS_DIR / f"{slug}.md").write_text(
            render_md(
                scenario, proposal, baseline, raci, shadow_role, shadow_text, redundancy_verdict, is_new,
                concur_verdicts, concurs,
            )
        )

        summary.append(
            {
                "slug": slug,
                "baseline_state": baseline["state"],
                "raci_state": raci["state"],
                "terminal_state_differs": baseline["state"] != raci["state"],
                "informed_role": shadow_role,
                "expected_informed_signal": scenario["expected_informed_signal"],
                "informed_reaction_judged_new": is_new,
                "prediction_matched_judgment": (scenario["expected_informed_signal"] == "novel") == is_new,
                "concur_role": scenario["concur_role"],
                "concur_verdicts": concurs,
                "concur_consistent": len(set(concurs)) == 1,
                "concur_diverged_from_clean_raci_convergence": raci["state"] == "converged" and not all(concurs),
            }
        )

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
