"""Single-agent baseline: one call, no lifecycle scaffolding."""

from llm_client import OWNER_MODEL, chat
from roles import baseline_system


def run_baseline(decision):
    answer = chat(
        OWNER_MODEL,
        baseline_system(),
        f"Decision: {decision['title']}\n\nContext: {decision['context']}",
        max_tokens=800,
    )
    return {"decision": decision["slug"], "answer": answer}
