"""Run both mechanisms (baseline vs. gated) on every scenario and write transcripts
under runs/. Proposal and contest are shared between the two mechanisms — same
model calls, same raised items — so the only variable is the classification/gate
mechanism itself.
"""

import json
import sys
from pathlib import Path

from lifecycle import run_baseline, run_gated, _propose, _contest
from scenarios import SCENARIOS

RUNS_DIR = Path(__file__).parent / "runs"


def render_md(scenario, proposal, raised, baseline, gated):
    parts = [
        f"# {scenario['slug']}\n",
        f"Decision: {scenario['title']}\n",
        f"Owner: {scenario['owner_role']}\n",
        f"\n## Raised items (fixed, pre-registered)\n",
        f"\n### Issue ({scenario['issue']['role']}) — engineering trade-off, resolvable by revision\n",
        f"\n{scenario['issue']['text']}\n",
        f"\n### Question ({scenario['question']['role']}) — genuine missing fact\n",
        f"\n{scenario['question']['text']}\n",
        f"\n### External answer (ground truth, held back until the gated mechanism needs it)\n",
        f"\n{scenario['external_answer']}\n",
        f"\n## Proposal (owner)\n\n{proposal}\n",
        f"\n## Contest responses\n",
    ]
    for role, text in raised.items():
        parts.append(f"\n### {role}\n\n{text}\n")

    parts.append("\n## Mechanism A: baseline (today's unmodified 2-way lifecycle)\n")
    parts.append(f"\n### Round 1 classification\n\n{baseline['classification_round_1']}\n")
    if baseline.get("rounds", 0) >= 1:
        parts.append(f"\n### Owner revision\n\n{baseline['revised_proposal']}\n")
        parts.append(f"\n### Round 2 classification\n\n{baseline['classification_round_2']}\n")
    parts.append(f"\n### Outcome: **{baseline['state']}**\n")

    parts.append(
        "\n## Mechanism B: gated (3-way classification round 1 + targeted per-raiser recheck "
        "+ structural question gate)\n"
    )
    parts.append(f"\n### Round 1 classification\n\n{gated['classification_round_1']}\n")
    if gated.get("rounds", 0) >= 1:
        parts.append(f"\n### Owner's self-answer attempt (unwarned revision prompt)\n\n{gated['self_answer_attempt']}\n")
        parts.append(
            f"\n### Old generalist reclassification (comparison only, does not decide the outcome)\n\n"
            f"{gated['old_generalist_reclassification_after_self_answer']}\n"
        )
        parts.append(
            f"\n### NEW: targeted recheck — {scenario['issue']['role']} on the Issue\n\n{gated['issue_recheck_after_self_answer']}\n"
        )
        parts.append(
            f"\n### NEW: targeted recheck — {scenario['question']['role']} on the Question\n\n"
            f"{gated['question_recheck_after_self_answer']}\n"
        )
        parts.append(
            f"\n### Gate check after self-answer attempt: **{gated['state_after_self_answer_attempt']}** "
            f"(question_resolved_externally is still False here — the gate does not accept the owner's own "
            f"answer, regardless of what the Question-raiser's own recheck concluded. "
            f"Question-raiser fooled by the self-answer? {gated['question_raiser_fooled_by_self_answer']})\n"
        )
    if "final_revision_with_external_answer" in gated:
        parts.append(f"\n### Final revision, external answer supplied\n\n{gated['final_revision_with_external_answer']}\n")
        parts.append(
            f"\n### Old generalist reclassification, final (comparison only)\n\n"
            f"{gated['old_generalist_reclassification_final']}\n"
        )
        parts.append(
            f"\n### Old mechanism still flags [QUESTION] after being shown the real answer? "
            f"{gated['old_mechanism_still_flags_question_after_external_answer']}\n"
        )
        parts.append(
            f"\n### NEW: targeted recheck, final — {scenario['issue']['role']} on the Issue\n\n{gated['issue_recheck_final']}\n"
        )
        parts.append(
            f"\n### NEW: targeted recheck, final — {scenario['question']['role']} on the Question\n\n"
            f"{gated['question_recheck_final']}\n"
        )
    parts.append(f"\n### Outcome: **{gated['state']}**\n")

    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []

    for scenario in SCENARIOS:
        slug = scenario["slug"]
        print(f"[{slug}] propose...", file=sys.stderr)
        proposal = _propose(scenario)
        print(f"[{slug}] contest...", file=sys.stderr)
        raised = _contest(scenario, proposal)

        print(f"[{slug}] baseline mechanism...", file=sys.stderr)
        baseline = run_baseline(scenario, proposal, raised)
        print(f"[{slug}] baseline outcome: {baseline['state']}", file=sys.stderr)

        print(f"[{slug}] gated mechanism...", file=sys.stderr)
        gated = run_gated(scenario, proposal, raised)
        print(f"[{slug}] gated outcome: {gated['state']}", file=sys.stderr)

        (RUNS_DIR / f"{slug}.md").write_text(render_md(scenario, proposal, raised, baseline, gated))

        summary.append(
            {
                "slug": slug,
                "baseline_state": baseline["state"],
                "gated_state": gated["state"],
                "gated_has_question_round_1": gated.get("has_question_round_1"),
                "gated_blocked_after_self_answer_attempt": gated.get("state_after_self_answer_attempt"),
                "question_raiser_fooled_by_self_answer": gated.get("question_raiser_fooled_by_self_answer"),
                "old_mechanism_still_flags_question_after_external_answer": gated.get(
                    "old_mechanism_still_flags_question_after_external_answer"
                ),
            }
        )

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
