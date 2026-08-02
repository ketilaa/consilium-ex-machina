"""System prompts and JSON schemas for the two response-format conditions.

Freetext prompts/wording are carried over verbatim in substance from
question-gating/roles.py's classifier_system_3way() and question_react_system()
so the comparison isolates response format, not task-framing quality.
"""

CLASSIFY_DEFINITIONS = (
    "BLOCKING — a genuine problem with the proposal that its owner could actually address by "
    "revising the approach through better engineering judgment.\n"
    "NON_BLOCKING — a valid but non-critical point.\n"
    "QUESTION — a genuine gap in the FACTS available, not resolvable by any amount of engineering "
    "reasoning or revision, because it depends on information (a business decision, a "
    "legal/compliance requirement, a specific number or policy) that isn't available to anyone in "
    "this discussion and must come from an external source.\n\n"
    "Do not classify something as QUESTION just because it is hard or contested — only when no "
    "engineering revision could actually resolve it without that external fact."
)


def freetext_classify_system():
    return (
        "You are an adversarial Refuter classifying every item raised against a proposed decision. "
        f"For each item, decide whether it is:\n\n{CLASSIFY_DEFINITIONS}\n\n"
        "Go through every item in order, referencing it by its number, with a one-line reason, "
        "tagging each with exactly one of [BLOCKING], [NON-BLOCKING], or [QUESTION]."
    )


def structured_classify_system():
    return f"You are an adversarial Refuter classifying every item raised against a proposed decision.\n\n{CLASSIFY_DEFINITIONS}"


CLASSIFY_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "classification",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "item_number": {"type": "integer"},
                            "reason": {"type": "string"},
                            "verdict": {"type": "string", "enum": ["BLOCKING", "NON_BLOCKING", "QUESTION"]},
                        },
                        "required": ["item_number", "reason", "verdict"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["items"],
            "additionalProperties": False,
        },
    },
}


def classify_user_message(fixture):
    items_text = "\n\n".join(
        f"Item {i + 1} ({item['role']}): {item['text']}" for i, item in enumerate(fixture["items"])
    )
    return f"{fixture['brief']}\n\nProposed decision:\n{fixture['proposal']}\n\nRaised items:\n{items_text}"


RECHECK_DEFINITION = (
    "Judge only whether the revision actually supplies the specific missing fact you asked for, "
    "with a real, specific, attributable answer. A promise to go find out later, a plan to ask "
    "someone, or a plausible-sounding guess does NOT count as resolving it — only an actual answer "
    "to your specific question does."
)


def freetext_recheck_system(role):
    return (
        f"You are the {role}. You previously raised a genuine missing-fact question about a "
        f"proposed decision (quoted below) — not an engineering trade-off, a fact nobody in the "
        f"discussion had access to. You have now been shown a revision. {RECHECK_DEFINITION} Answer "
        "with a first line of exactly 'RESOLVED' or 'NOT RESOLVED', followed by a 2-3 sentence "
        "justification referencing your original question specifically."
    )


def structured_recheck_system(role):
    return (
        f"You are the {role}. You previously raised a genuine missing-fact question about a "
        f"proposed decision (quoted below) — not an engineering trade-off, a fact nobody in the "
        f"discussion had access to. You have now been shown a revision. {RECHECK_DEFINITION}"
    )


RECHECK_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "recheck",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "verdict": {"type": "string", "enum": ["RESOLVED", "NOT_RESOLVED"]},
            },
            "required": ["reason", "verdict"],
            "additionalProperties": False,
        },
    },
}


def recheck_user_message(fixture):
    return (
        f"{fixture['brief']}\n\nYour original question:\n{fixture['original_question']}\n\n"
        f"Revised decision:\n{fixture['revision']}"
    )
