"""Runs each task under 3 context conditions (none / full-dump / packet) on the
14B model, then a bonus full-dump-vs-packet comparison on the 7B model to test
the context-overflow claim directly. Saves every transcript under runs/.
"""

import json
import sys
import time
from pathlib import Path

from llm_client import REASONING_MODEL, SMALL_MODEL, chat
from packet_builder import build_packet, full_dump
from tasks import TASKS

REPO_DIR = Path(__file__).parent / "sample_repo"
RUNS_DIR = Path(__file__).parent / "runs"

SYSTEM_WITH_CONTEXT = (
    "You are a senior backend engineer working on this codebase. Answer using "
    "specific, concrete details grounded in the code shown below — cite the "
    "actual file, function, or constant names you're relying on. If something "
    "isn't shown to you, say so rather than guessing specifics."
)

SYSTEM_NO_CONTEXT = (
    "You are a senior backend engineer. You have NOT been shown this codebase. "
    "Answer from general engineering best practice only. Do not invent "
    "specific file names, function names, or constant values — you don't have "
    "access to them."
)


def _call(endpoint, question, context_text=None, max_tokens=700):
    if context_text is None:
        return chat(endpoint, SYSTEM_NO_CONTEXT, question, max_tokens=max_tokens)
    user = f"Codebase:\n\n{context_text}\n\n---\n\nTask: {question}"
    return chat(endpoint, SYSTEM_WITH_CONTEXT, user, max_tokens=max_tokens)


def _render(task, condition, selected_files, result, seconds):
    lines = [
        f"# {condition} — {task['slug']}\n",
        f"Question: {task['question']}\n",
    ]
    if selected_files is not None:
        lines.append(f"Files included: {selected_files}\n")
    lines.append(f"Wall time: {seconds:.1f}s\n")
    lines.append(f"Result ok: {result['ok']}\n")
    if result["ok"]:
        lines.append(f"Usage: {json.dumps(result['usage'])}\n")
        lines.append(f"\n## Answer\n\n{result['content']}\n")
    else:
        lines.append(f"\n## Error\n\n```\n{json.dumps(result['raw'], indent=2)[:3000]}\n```\n")
    return "\n".join(lines)


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    summary = []
    full_dump_text = full_dump(REPO_DIR)

    for task in TASKS:
        slug = task["slug"]
        out_dir = RUNS_DIR / slug
        out_dir.mkdir(exist_ok=True)
        packet_files, packet_text = build_packet(task["question"], REPO_DIR)

        conditions = [
            ("none", None, None),
            ("full_dump", None, full_dump_text),
            ("packet", packet_files, packet_text),
        ]

        for condition, files, context_text in conditions:
            print(f"[{slug}] {condition} (14B)...", file=sys.stderr)
            t0 = time.time()
            result = _call(REASONING_MODEL, task["question"], context_text)
            seconds = time.time() - t0
            (out_dir / f"{condition}.md").write_text(_render(task, condition, files, result, seconds))
            record = {
                "slug": slug,
                "condition": condition,
                "model": "14B",
                "ok": result["ok"],
                "prompt_tokens": result.get("usage", {}).get("prompt_tokens"),
                "seconds": round(seconds, 1),
            }
            summary.append(record)
            print(f"[{slug}] {condition} (14B) done: {record}", file=sys.stderr)

        # Bonus: same full_dump / packet conditions on the 7B model, to test
        # whether the smaller context window actually bites.
        for condition, files, context_text in [
            ("full_dump", None, full_dump_text),
            ("packet", packet_files, packet_text),
        ]:
            print(f"[{slug}] {condition} (7B bonus)...", file=sys.stderr)
            t0 = time.time()
            result = _call(SMALL_MODEL, task["question"], context_text)
            seconds = time.time() - t0
            (out_dir / f"{condition}_7b.md").write_text(_render(task, condition, files, result, seconds))
            record = {
                "slug": slug,
                "condition": f"{condition}_7b",
                "model": "7B",
                "ok": result["ok"],
                "prompt_tokens": result.get("usage", {}).get("prompt_tokens"),
                "seconds": round(seconds, 1),
            }
            summary.append(record)
            print(f"[{slug}] {condition} (7B bonus) done: {record}", file=sys.stderr)

    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
