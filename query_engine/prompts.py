"""
prompts.py — Prompt construction for the Gemini SQL-generation step.

Keeps the LLM's instructions and the schema description in one place so
they're easy to audit and tweak without touching the rest of the pipeline.
"""

from query_engine.schema import SCHEMA_DESCRIPTION

# ── Behavioral rules injected into every Gemini prompt ──────────────────────

RULES = """
RULES (follow these exactly):
1. Only generate SELECT statements. Never write INSERT, UPDATE, DELETE, DROP, or ALTER.
2. Only reference tables and columns that appear in the SCHEMA section above.
3. Return your answer as a single JSON object — no markdown fences, no extra text.
   The object must have exactly these two keys:
     {
       "sql": "<a valid SQLite SELECT statement>",
       "explanation": "<one sentence describing what the query does>"
     }
4. The SQL must be valid SQLite syntax.
5. Do not include any commentary, apologies, or text outside the JSON object.
"""


def build_prompt(question: str) -> str:
    """
    Assemble the full prompt string that will be sent to Gemini.

    Combines the schema description, behavioral rules, and the user's natural-
    language question so that the model has all context in a single call.

    Args:
        question: The natural-language financial question from the user.

    Returns:
        A formatted string ready to be used as the Gemini request content.
    """
    return (
        f"SCHEMA:\n{SCHEMA_DESCRIPTION}\n\n"
        f"{RULES}\n\n"
        f"USER QUESTION: {question}"
    )
