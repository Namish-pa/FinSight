"""
llm.py — LLM integration layer for FinSight.

Two different models are used on purpose:
  - Gemini (google-genai) handles SQL generation because it has strong
    reasoning and code-generation capabilities and works well with
    structured JSON output constraints.
  - Groq (llama-3.1-8b-instant) handles the summarisation step because it
    is extremely fast and cheap for short conversational responses — there is
    no need for the heavier model once we already have the result rows.
"""

import json
import os

from dotenv import load_dotenv
from google import genai
from groq import Groq

from query_engine.models import SQLResponse
from query_engine.prompts import build_prompt

# Load API keys from the .env file in the project root.
# load_dotenv() is a no-op if the file doesn't exist, so missing keys will
# surface as clear exceptions when the clients are actually used.
load_dotenv()

# ── Client initialisation ────────────────────────────────────────────────────

_gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
_groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

# Model identifiers — centralised here so they're easy to update.
_GEMINI_MODEL = "gemini-2.5-flash"
_GROQ_MODEL = "openai/gpt-oss-20b"


# ── Public functions ─────────────────────────────────────────────────────────


def generate_sql(question: str) -> SQLResponse:
    """
    Convert a natural-language question into a validated SQL query.

    Sends the assembled prompt (schema + rules + question) to Gemini and
    expects a JSON response containing 'sql' and 'explanation'. The JSON is
    parsed and validated against the SQLResponse pydantic model so any
    malformed output surfaces immediately rather than causing a cryptic error
    later in the pipeline.

    Args:
        question: The natural-language financial question from the user.

    Returns:
        A SQLResponse object with the generated SQL and its explanation.

    Raises:
        json.JSONDecodeError: If Gemini's response is not valid JSON.
        pydantic.ValidationError: If the JSON doesn't match SQLResponse's shape.
        KeyError: If GEMINI_API_KEY is not set in the environment.
    """
    prompt = build_prompt(question)

    response = _gemini_client.models.generate_content(
        model=_GEMINI_MODEL,
        contents=prompt,
    )

    raw_text = response.text.strip()

    # Strip markdown code fences if Gemini adds them despite the instruction.
    if raw_text.startswith("```"):
        # Remove opening fence (```json or ```) and closing fence (```)
        raw_text = raw_text.split("\n", 1)[-1]   # drop first line
        raw_text = raw_text.rsplit("```", 1)[0]   # drop trailing fence
        raw_text = raw_text.strip()

    parsed = json.loads(raw_text)        # raises JSONDecodeError on bad JSON
    return SQLResponse.model_validate(parsed)   # raises ValidationError on bad shape


def summarize(question: str, sql: str, rows: list[dict]) -> str:
    """
    Produce a concise natural-language answer grounded in the query results.

    Sends the original question, the SQL that was run, and the result rows
    to Groq. Groq is used here instead of Gemini because llama-3.1-8b-instant
    is significantly faster and cheaper for short summarisation tasks where
    deep reasoning is not required.

    Rows are truncated to 20 before serialisation to keep the prompt small
    and avoid hitting token limits for large result sets.

    Args:
        question: The original natural-language question.
        sql:      The SQL query that was executed.
        rows:     The list of result dicts from the database.

    Returns:
        A 1–2 sentence plain-text answer to the user's question.

    Raises:
        KeyError: If GROQ_API_KEY is not set in the environment.
    """
    truncated_rows = rows[:20]
    rows_json = json.dumps(truncated_rows, indent=2)

    system_prompt = (
        "You are a financial data assistant. "
        "Answer the user's question in 1-2 sentences using only the data provided. "
        "Do not add information that is not in the rows. Be direct and concise."
    )

    user_message = (
        f"Question: {question}\n\n"
        f"SQL executed:\n{sql}\n\n"
        f"Result rows (JSON):\n{rows_json}\n\n"
        "Give a concise 1-2 sentence natural-language answer to the question."
    )

    chat_completion = _groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message},
        ],
    )

    return chat_completion.choices[0].message.content.strip()
