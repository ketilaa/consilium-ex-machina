"""Follow-up: isolate whether the role panel's behavior in run_experiment.py is a
model-capability limit (7B in the role seats) or persists regardless of model.

run_experiment.py found the 6-role panel (on the 7B ROLE_MODEL) never once used
the 'QUESTION:' tag across 30 calls, even on tasks where the single generalist
(14B GENERALIST_MODEL) did. But two of five ambiguous tasks (cancel-order-endpoint,
notification-opt-out) were missed by EVERYONE, generalist included — so this
re-runs just those two tasks' role panel on the 14B model to see whether a
stronger model in the same role-framed seats catches what the 7B panel and the
14B generalist both missed, and whether it follows the QUESTION/PROCEEDING tag
protocol any more reliably.
"""

import json
import sys
from pathlib import Path

from llm_client import GENERALIST_MODEL, chat
from roles import ROLES, role_question_system
from tasks import AMBIGUOUS_TASKS

RUNS_DIR = Path(__file__).parent / "runs"
TARGET_SLUGS = ["cancel-order-endpoint", "notification-opt-out"]


def main():
    tasks = [t for t in AMBIGUOUS_TASKS if t["slug"] in TARGET_SLUGS]
    out = {}
    for task in tasks:
        out[task["slug"]] = {}
        for role in ROLES:
            print(f"[{task['slug']}] {role} (14B)...", file=sys.stderr)
            result = chat(GENERALIST_MODEL, role_question_system(role), task["spec"], max_tokens=400)
            content = result["content"] if result["ok"] else f"[CALL FAILED: {result}]"
            out[task["slug"]][role] = content
            print(f"  -> {content[:100]}", file=sys.stderr)

    (RUNS_DIR / "panel_14b_followup.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
