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


def build_retry_prompt(question: str, failed_sql: str, error_message: str) -> str:
    """
    Assemble a follow-up prompt for the retry Gemini call after a failure.

    Provides the full schema and rules as context, then gives the model the
    original question, the SQL it previously generated, and the exact error
    message so it can produce a corrected query.

    Args:
        question:      The original natural-language financial question.
        failed_sql:    The SQL string that caused the error.
        error_message: The exception message from the failed execution attempt.

    Returns:
        A formatted string ready to be used as the Gemini request content.
    """
    return (
        f"SCHEMA:\n{SCHEMA_DESCRIPTION}\n\n"
        f"{RULES}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"PREVIOUS ATTEMPT:\n"
        f"The SQL query you generated previously failed to execute.\n"
        f"Failed SQL:\n{failed_sql}\n\n"
        f"Error message:\n{error_message}\n\n"
        f"Please analyse the error, correct the SQL, and return a valid JSON "
        f"object with the fixed query. Remember: only single SELECT statements "
        f"referencing the schema above are allowed."
    )
