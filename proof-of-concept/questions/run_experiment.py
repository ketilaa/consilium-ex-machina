"""Run the questions-as-first-class-citizens PoC and write transcripts under runs/.

For each ambiguous task: a silent baseline (no permission to ask), a single
generalist reviewer with the question protocol, and a panel of six role-framed
reviewers with the same protocol — each independent, none seeing the others'
output (mirrors the "contest" step in decision-making/lifecycle.py, not a full
back-and-forth). For each unambiguous (control) task: just the generalist and the
role panel, to measure false positives.

Grading (does a response's QUESTION line actually match a pre-registered
ambiguity) is manual — same discipline as the other two PoCs — but the verdict
(asked vs. proceeded) and question count are parsed mechanically here since the
system prompt forces a fixed tag format.
"""

import json
import re
import sys
from pathlib import Path

from llm_client import GENERALIST_MODEL, ROLE_MODEL, chat
from roles import ROLES, generalist_question_system, role_question_system, silent_system
from tasks import AMBIGUOUS_TASKS, UNAMBIGUOUS_TASKS

RUNS_DIR = Path(__file__).parent / "runs"

QUESTION_LINE_RE = re.compile(r"^QUESTION:", re.MULTILINE)


def _call(endpoint, system, spec, label):
    result = chat(endpoint, system, spec)
    if not result["ok"]:
        print(f"  ! {label} failed: {result}", file=sys.stderr)
        return {"content": f"[CALL FAILED: {result}]", "verdict": "error", "question_count": 0, "usage": {}}
    content = result["content"]
    stripped = content.lstrip()
    if stripped.upper().startswith("QUESTION"):
        verdict = "asked"
    elif stripped.upper().startswith("PROCEEDING"):
        verdict = "proceeded"
    else:
        verdict = "unparsed"
    question_count = len(QUESTION_LINE_RE.findall(content)) or (1 if verdict == "asked" else 0)
    return {"content": content, "verdict": verdict, "question_count": question_count, "usage": result["usage"]}


def run_ambiguous_task(task):
    slug = task["slug"]
    print(f"[{slug}] silent baseline...", file=sys.stderr)
    silent = _call(GENERALIST_MODEL, silent_system(), task["spec"], f"{slug}/silent")

    print(f"[{slug}] generalist (question-enabled)...", file=sys.stderr)
    generalist = _call(GENERALIST_MODEL, generalist_question_system(), task["spec"], f"{slug}/generalist")

    panel = {}
    for role in ROLES:
        print(f"[{slug}] role panel: {role}...", file=sys.stderr)
        panel[role] = _call(ROLE_MODEL, role_question_system(role), task["spec"], f"{slug}/{role}")

    return {"slug": slug, "silent": silent, "generalist": generalist, "panel": panel}


def run_unambiguous_task(task):
    slug = task["slug"]
    print(f"[{slug}] generalist (question-enabled)...", file=sys.stderr)
    generalist = _call(GENERALIST_MODEL, generalist_question_system(), task["spec"], f"{slug}/generalist")

    panel = {}
    for role in ROLES:
        print(f"[{slug}] role panel: {role}...", file=sys.stderr)
        panel[role] = _call(ROLE_MODEL, role_question_system(role), task["spec"], f"{slug}/{role}")

    return {"slug": slug, "generalist": generalist, "panel": panel}


def render_ambiguous_md(task, result):
    parts = [
        f"# {task['slug']}\n",
        f"Spec: {task['spec']}\n",
        "\n## Pre-registered ambiguities (ground truth)\n",
    ]
    for a in task["ambiguities"]:
        parts.append(f"- **[{a['intended_role']}]** {a['dimension']}\n")

    parts.append(f"\n## Silent baseline (no permission to ask) — verdict: {result['silent']['verdict']}\n")
    parts.append(f"\n{result['silent']['content']}\n")

    parts.append(
        f"\n## Generalist, question-enabled — verdict: {result['generalist']['verdict']} "
        f"({result['generalist']['question_count']} question(s))\n"
    )
    parts.append(f"\n{result['generalist']['content']}\n")

    parts.append("\n## Role panel, question-enabled\n")
    for role, r in result["panel"].items():
        parts.append(f"\n### {role} — verdict: {r['verdict']} ({r['question_count']} question(s))\n")
        parts.append(f"\n{r['content']}\n")

    return "\n".join(parts)


def render_unambiguous_md(task, result):
    parts = [
        f"# {task['slug']} (control — fully specified, no genuine ambiguity)\n",
        f"Spec: {task['spec']}\n",
        f"\n## Generalist, question-enabled — verdict: {result['generalist']['verdict']} "
        f"({result['generalist']['question_count']} question(s))\n",
        f"\n{result['generalist']['content']}\n",
        "\n## Role panel, question-enabled\n",
    ]
    for role, r in result["panel"].items():
        parts.append(f"\n### {role} — verdict: {r['verdict']} ({r['question_count']} question(s))\n")
        parts.append(f"\n{r['content']}\n")
    return "\n".join(parts)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = {"ambiguous": [], "unambiguous": []}

    for task in AMBIGUOUS_TASKS:
        result = run_ambiguous_task(task)
        (RUNS_DIR / f"{task['slug']}.md").write_text(render_ambiguous_md(task, result))
        summary["ambiguous"].append(
            {
                "slug": task["slug"],
                "silent_verdict": result["silent"]["verdict"],
                "generalist_verdict": result["generalist"]["verdict"],
                "generalist_question_count": result["generalist"]["question_count"],
                "panel_verdicts": {role: r["verdict"] for role, r in result["panel"].items()},
                "panel_question_counts": {role: r["question_count"] for role, r in result["panel"].items()},
            }
        )
        print(f"[{task['slug']}] done", file=sys.stderr)

    for task in UNAMBIGUOUS_TASKS:
        result = run_unambiguous_task(task)
        (RUNS_DIR / f"{task['slug']}.md").write_text(render_unambiguous_md(task, result))
        summary["unambiguous"].append(
            {
                "slug": task["slug"],
                "generalist_verdict": result["generalist"]["verdict"],
                "generalist_question_count": result["generalist"]["question_count"],
                "panel_verdicts": {role: r["verdict"] for role, r in result["panel"].items()},
                "panel_question_counts": {role: r["question_count"] for role, r in result["panel"].items()},
            }
        )
        print(f"[{task['slug']}] done", file=sys.stderr)

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
