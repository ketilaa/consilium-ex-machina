"""Compares free-text tag scanning against forced JSON-schema output on the
exact classify/recheck steps that produced two independent parsing bugs in
poc-question-gating.md. Each fixture is repeated N times per condition at
nonzero temperature to get an actual failure-rate estimate, unlike prior PoCs'
single-run-per-condition transcripts — the earlier bugs were about format
*variance*, which a single run can't quantify.

Also runs a small bonus stress test: the same structured recheck call with a
deliberately tight max_tokens, to check whether structured output is immune to
truncation-caused invalid output, or only to the tag-formatting variance that
broke the free-text parsers.
"""

import json
import re
import sys
import time
from pathlib import Path

from fixtures import CLASSIFY_FIXTURES, RECHECK_FIXTURES
from llm_client import MODEL, chat
from prompts import (
    CLASSIFY_SCHEMA,
    RECHECK_SCHEMA,
    classify_user_message,
    freetext_classify_system,
    freetext_recheck_system,
    recheck_user_message,
    structured_classify_system,
    structured_recheck_system,
)

RUNS_DIR = Path(__file__).parent / "runs"
REPEATS = 8
TRUNCATION_REPEATS = 6
TRUNCATION_MAX_TOKENS = 40

TAG_RE = re.compile(r"\[(BLOCKING|NON-BLOCKING|QUESTION)\b", re.IGNORECASE)


def _normalize_tag(tag):
    return tag.upper().replace("-", "_")


def parse_classify_freetext(content, n_items):
    tags_in_order = [_normalize_tag(m.group(1)) for m in TAG_RE.finditer(content)]
    if len(tags_in_order) < n_items:
        return {"parse_ok": False, "verdicts": None, "raw_tag_count": len(tags_in_order)}
    return {"parse_ok": True, "verdicts": tags_in_order[:n_items], "raw_tag_count": len(tags_in_order)}


def parse_classify_structured(content):
    try:
        data = json.loads(content)
        items = data["items"]
        by_number = {item["item_number"]: item["verdict"] for item in items}
        verdicts = [by_number[i + 1] for i in range(len(items))]
        return {"parse_ok": True, "verdicts": verdicts, "raw": data}
    except Exception as e:
        return {"parse_ok": False, "verdicts": None, "error": str(e)}


def parse_recheck_freetext(content):
    stripped = re.sub(r"^[\s*_#>-]+", "", content).upper()
    if stripped.startswith("NOT RESOLVED") or stripped.startswith("NOT_RESOLVED"):
        return {"parse_ok": True, "verdict": "NOT_RESOLVED"}
    if stripped.startswith("RESOLVED"):
        return {"parse_ok": True, "verdict": "RESOLVED"}
    return {"parse_ok": False, "verdict": None}


def parse_recheck_structured(content):
    try:
        data = json.loads(content)
        return {"parse_ok": True, "verdict": data["verdict"], "raw": data}
    except Exception as e:
        return {"parse_ok": False, "verdict": None, "error": str(e)}


def run_classify_fixture(fixture, results_fh):
    ground_truth = [item["ground_truth"] for item in fixture["items"]]
    user_message = classify_user_message(fixture)
    records = {"freetext": [], "structured": []}

    for rep in range(REPEATS):
        t0 = time.time()
        result = chat(MODEL, freetext_classify_system(), user_message, max_tokens=500)
        seconds = time.time() - t0
        parsed = parse_classify_freetext(result["content"], len(fixture["items"])) if result["ok"] else {
            "parse_ok": False,
            "verdicts": None,
        }
        correct = parsed["parse_ok"] and parsed["verdicts"] == ground_truth
        record = {
            "fixture": fixture["slug"],
            "condition": "freetext",
            "rep": rep,
            "ok": result["ok"],
            "finish_reason": result.get("finish_reason"),
            "content": result.get("content"),
            "parse_ok": parsed["parse_ok"],
            "verdicts": parsed["verdicts"],
            "ground_truth": ground_truth,
            "correct": correct,
            "seconds": round(seconds, 1),
            "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        }
        records["freetext"].append(record)
        results_fh.write(json.dumps(record) + "\n")
        print(f"  [{fixture['slug']}] freetext rep {rep}: parse_ok={parsed['parse_ok']} correct={correct}", file=sys.stderr)

    for rep in range(REPEATS):
        t0 = time.time()
        result = chat(
            MODEL, structured_classify_system(), user_message, max_tokens=500, response_format=CLASSIFY_SCHEMA
        )
        seconds = time.time() - t0
        parsed = parse_classify_structured(result["content"]) if result["ok"] else {"parse_ok": False, "verdicts": None}
        correct = parsed["parse_ok"] and parsed["verdicts"] == ground_truth
        record = {
            "fixture": fixture["slug"],
            "condition": "structured",
            "rep": rep,
            "ok": result["ok"],
            "finish_reason": result.get("finish_reason"),
            "content": result.get("content"),
            "parse_ok": parsed["parse_ok"],
            "verdicts": parsed.get("verdicts"),
            "ground_truth": ground_truth,
            "correct": correct,
            "seconds": round(seconds, 1),
            "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        }
        records["structured"].append(record)
        results_fh.write(json.dumps(record) + "\n")
        print(f"  [{fixture['slug']}] structured rep {rep}: parse_ok={parsed['parse_ok']} correct={correct}", file=sys.stderr)

    return records


def run_recheck_fixture(fixture, results_fh):
    ground_truth = fixture["ground_truth"]
    user_message = recheck_user_message(fixture)
    records = {"freetext": [], "structured": []}

    for rep in range(REPEATS):
        t0 = time.time()
        result = chat(MODEL, freetext_recheck_system(fixture["role"]), user_message, max_tokens=250)
        seconds = time.time() - t0
        parsed = parse_recheck_freetext(result["content"]) if result["ok"] else {"parse_ok": False, "verdict": None}
        correct = parsed["parse_ok"] and parsed["verdict"] == ground_truth
        record = {
            "fixture": fixture["slug"],
            "condition": "freetext",
            "rep": rep,
            "ok": result["ok"],
            "finish_reason": result.get("finish_reason"),
            "content": result.get("content"),
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed["verdict"],
            "ground_truth": ground_truth,
            "correct": correct,
            "seconds": round(seconds, 1),
            "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        }
        records["freetext"].append(record)
        results_fh.write(json.dumps(record) + "\n")
        print(f"  [{fixture['slug']}] freetext rep {rep}: parse_ok={parsed['parse_ok']} correct={correct}", file=sys.stderr)

    for rep in range(REPEATS):
        t0 = time.time()
        result = chat(
            MODEL, structured_recheck_system(fixture["role"]), user_message, max_tokens=250, response_format=RECHECK_SCHEMA
        )
        seconds = time.time() - t0
        parsed = parse_recheck_structured(result["content"]) if result["ok"] else {"parse_ok": False, "verdict": None}
        correct = parsed["parse_ok"] and parsed["verdict"] == ground_truth
        record = {
            "fixture": fixture["slug"],
            "condition": "structured",
            "rep": rep,
            "ok": result["ok"],
            "finish_reason": result.get("finish_reason"),
            "content": result.get("content"),
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed.get("verdict"),
            "ground_truth": ground_truth,
            "correct": correct,
            "seconds": round(seconds, 1),
            "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        }
        records["structured"].append(record)
        results_fh.write(json.dumps(record) + "\n")
        print(f"  [{fixture['slug']}] structured rep {rep}: parse_ok={parsed['parse_ok']} correct={correct}", file=sys.stderr)

    return records


def run_truncation_stress_test(results_fh):
    """Bonus: does forced structured output survive a token budget too small
    for the schema's reasoning + verdict? Grammar constraints control what CAN
    be generated next, not whether generation gets cut off by max_tokens."""
    fixture = RECHECK_FIXTURES[3]  # recheck-llm-inference-hosting-final, ground truth RESOLVED
    user_message = recheck_user_message(fixture)
    records = []
    for rep in range(TRUNCATION_REPEATS):
        result = chat(
            MODEL,
            structured_recheck_system(fixture["role"]),
            user_message,
            max_tokens=TRUNCATION_MAX_TOKENS,
            response_format=RECHECK_SCHEMA,
        )
        parsed = parse_recheck_structured(result["content"]) if result["ok"] else {"parse_ok": False, "verdict": None}
        record = {
            "fixture": fixture["slug"],
            "condition": "structured_truncated",
            "rep": rep,
            "ok": result["ok"],
            "finish_reason": result.get("finish_reason"),
            "content": result.get("content"),
            "parse_ok": parsed["parse_ok"],
            "verdict": parsed.get("verdict"),
            "completion_tokens": result.get("usage", {}).get("completion_tokens"),
        }
        records.append(record)
        results_fh.write(json.dumps(record) + "\n")
        print(
            f"  [truncation-stress] rep {rep}: finish_reason={result.get('finish_reason')} parse_ok={parsed['parse_ok']}",
            file=sys.stderr,
        )
    return records


def _rate(records, key):
    if not records:
        return None
    return round(sum(1 for r in records if r[key]) / len(records), 2)


def summarize(all_classify, all_recheck, truncation_records):
    summary = {"classify": [], "recheck": [], "truncation_stress": []}
    for slug, records in all_classify.items():
        for condition in ("freetext", "structured"):
            reps = records[condition]
            summary["classify"].append(
                {
                    "fixture": slug,
                    "condition": condition,
                    "parse_success_rate": _rate(reps, "parse_ok"),
                    "correct_rate": _rate(reps, "correct"),
                    "mean_completion_tokens": round(
                        sum(r["completion_tokens"] or 0 for r in reps) / len(reps), 1
                    ),
                    "mean_seconds": round(sum(r["seconds"] for r in reps) / len(reps), 1),
                }
            )
    for slug, records in all_recheck.items():
        for condition in ("freetext", "structured"):
            reps = records[condition]
            summary["recheck"].append(
                {
                    "fixture": slug,
                    "condition": condition,
                    "parse_success_rate": _rate(reps, "parse_ok"),
                    "correct_rate": _rate(reps, "correct"),
                    "mean_completion_tokens": round(
                        sum(r["completion_tokens"] or 0 for r in reps) / len(reps), 1
                    ),
                    "mean_seconds": round(sum(r["seconds"] for r in reps) / len(reps), 1),
                }
            )
    summary["truncation_stress"] = {
        "parse_success_rate": _rate(truncation_records, "parse_ok"),
        "finish_reasons": [r["finish_reason"] for r in truncation_records],
    }
    return summary


def main():
    RUNS_DIR.mkdir(exist_ok=True)
    all_classify = {}
    all_recheck = {}

    with open(RUNS_DIR / "results.jsonl", "w") as results_fh:
        for fixture in CLASSIFY_FIXTURES:
            print(f"[{fixture['slug']}] running {REPEATS} reps x 2 conditions...", file=sys.stderr)
            all_classify[fixture["slug"]] = run_classify_fixture(fixture, results_fh)

        for fixture in RECHECK_FIXTURES:
            print(f"[{fixture['slug']}] running {REPEATS} reps x 2 conditions...", file=sys.stderr)
            all_recheck[fixture["slug"]] = run_recheck_fixture(fixture, results_fh)

        print("[truncation-stress] running...", file=sys.stderr)
        truncation_records = run_truncation_stress_test(results_fh)

    summary = summarize(all_classify, all_recheck, truncation_records)
    (RUNS_DIR / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
