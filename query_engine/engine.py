"""
engine.py — The main entry point for the FinSight query pipeline.

Orchestrates the three steps: SQL generation (Gemini) → DB execution
(SQLite) → natural-language summarisation (Groq). Keeping this thin makes
each step independently testable and easy to explain in interviews.
"""

from query_engine.db import execute_sql
from query_engine.llm import generate_sql, summarize
from query_engine.models import QueryResult


def ask(question: str) -> QueryResult:
    """
    Run the full text-to-SQL pipeline for a natural-language question.

    Steps:
      1. generate_sql()  — sends the question to Gemini, gets back validated SQL.
      2. execute_sql()   — runs the SQL against finsight.db, returns rows as dicts.
      3. summarize()     — sends the question + rows to Groq for a plain-English answer.

    Errors are intentionally not caught here so that failures surface
    immediately during development and testing (no silent swallowing).

    Args:
        question: A natural-language financial question (e.g. "How many invoices are overdue?").

    Returns:
        A QueryResult containing the question, SQL, raw rows, and summary.
    """
    # Step 1: Turn the natural-language question into validated SQL.
    sql_response = generate_sql(question)

    # Step 2: Execute the SQL against the local SQLite database.
    rows = execute_sql(sql_response.sql)

    # Step 3: Summarise the results in plain English using Groq.
    summary = summarize(question, sql_response.sql, rows)

    return QueryResult(
        question=question,
        sql=sql_response.sql,
        rows=rows,
        summary=summary,
    )
