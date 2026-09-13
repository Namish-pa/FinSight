"""
engine.py — The main entry point for the FinSight query pipeline.

Orchestrates the three steps: SQL generation (Gemini) → DB execution
(SQLite) → natural-language summarisation (Groq). Keeping this thin makes
each step independently testable and easy to explain in interviews.

Retry logic: if the first generate_sql → execute_sql attempt fails (due to
a Pydantic validation error, UnsafeQueryError, sqlite3 execution error, or
a Gemini API error such as a 429 rate-limit), the pipeline retries exactly
once by sending the original question, the failed SQL, and the error message
back to Gemini for a corrected query. If the retry also fails, a graceful
QueryResult with empty rows and an explanatory summary is returned instead
of raising.
"""

import json
import sqlite3

import pydantic
from google.genai import errors as _genai_errors

from query_engine.db import UnsafeQueryError, execute_sql
from query_engine.llm import generate_sql, summarize
from query_engine.models import QueryResult
from query_engine.prompts import build_retry_prompt


def ask(question: str) -> QueryResult:
    """
    Run the full text-to-SQL pipeline for a natural-language question.

    Steps:
      1. generate_sql()  — sends the question to Gemini, gets back validated SQL.
      2. execute_sql()   — runs the SQL against finsight.db, returns rows as dicts.
      3. summarize()     — sends the question + rows to Groq for a plain-English answer.

    A single automatic retry is attempted if step 1 or 2 fails with a
    Pydantic ValidationError, UnsafeQueryError, or sqlite3.Error. The retry
    passes the failed SQL and the error message back to Gemini so the model
    can self-correct.

    If the retry also fails, a QueryResult with empty rows and a summary
    describing the failure is returned — the function never raises to callers.

    Args:
        question: A natural-language financial question.

    Returns:
        A QueryResult containing the question, SQL, raw rows, and summary.
    """
    # ── First attempt ────────────────────────────────────────────────────────
    retry_triggered = False
    failed_sql = ""

    try:
        sql_response = generate_sql(question)
        failed_sql = sql_response.sql           # capture in case execute fails
        rows = execute_sql(sql_response.sql)

    except (pydantic.ValidationError, UnsafeQueryError, sqlite3.Error,
            json.JSONDecodeError, _genai_errors.ClientError) as first_err:

        # ── Retry once ───────────────────────────────────────────────────────
        retry_triggered = True
        error_message = str(first_err)
        print(
            f"\n[RETRY] First attempt failed for question: {question!r}\n"
            f"        Error : {error_message}\n"
            f"        SQL   : {failed_sql!r}\n"
            f"        → Sending corrected prompt to Gemini …"
        )

        try:
            retry_prompt = build_retry_prompt(question, failed_sql, error_message)

            # Import the raw Gemini call so we can pass the retry prompt directly.
            from query_engine.llm import _gemini_client, _GEMINI_MODEL

            retry_response = _gemini_client.models.generate_content(
                model=_GEMINI_MODEL,
                contents=retry_prompt,
            )

            raw_text = retry_response.text.strip()
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                raw_text = raw_text.rsplit("```", 1)[0].strip()

            import pydantic as _pydantic
            from query_engine.models import SQLResponse

            parsed = json.loads(raw_text)
            sql_response = SQLResponse.model_validate(parsed)
            failed_sql = sql_response.sql
            rows = execute_sql(sql_response.sql)

        except Exception as retry_err:
            # Retry also failed — return a graceful result, never raise.
            short_reason = str(retry_err)[:200]
            print(
                f"[RETRY] Second attempt also failed: {short_reason}\n"
                f"        Returning empty result."
            )
            return QueryResult(
                question=question,
                sql=failed_sql or "(none)",
                rows=[],
                summary=(
                    f"Sorry, I was unable to answer this question. "
                    f"The query failed on both attempts. Reason: {short_reason}"
                ),
            )

    # ── Step 3: Summarise ────────────────────────────────────────────────────
    if retry_triggered:
        print(f"[RETRY] Retry succeeded — continuing with corrected SQL.")

    summary = summarize(question, sql_response.sql, rows)

    return QueryResult(
        question=question,
        sql=sql_response.sql,
        rows=rows,
        summary=summary,
    )
