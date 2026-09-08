"""
db.py — SQLite execution layer for FinSight.

Deliberately kept separate from the LLM layer so it's easy to swap the
database engine later (e.g., move from SQLite to PostgreSQL) without
touching any AI-related code.
"""

import sqlite3
from pathlib import Path

import sqlparse

# Resolve the DB path relative to this file so the script works from any
# working directory.
_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finsight.db"


# ── Custom exceptions ────────────────────────────────────────────────────────

class UnsafeQueryError(Exception):
    """Raised when a SQL string fails the safety guard in is_safe_select()."""


# ── Safety guard ─────────────────────────────────────────────────────────────

def is_safe_select(sql: str) -> bool:
    """
    Return True only if sql is a single, well-formed SELECT statement.

    Uses sqlparse to parse the SQL string before any execution occurs.
    The check rejects:
      - Empty or whitespace-only input
      - Multiple statements (e.g. stacked queries separated by semicolons)
      - Any statement type other than SELECT (INSERT, UPDATE, DELETE, DROP …)
      - Input that sqlparse cannot identify as a known statement type

    Args:
        sql: The SQL string to inspect.

    Returns:
        True if the query is a single SELECT statement, False otherwise.
    """
    if not sql or not sql.strip():
        return False

    statements = sqlparse.parse(sql)

    # sqlparse.parse always returns a tuple; filter out empty/whitespace-only
    # "ghost" statements that appear when the input ends with a semicolon.
    non_empty = [s for s in statements if s.value.strip()]

    # Reject multiple statements (catches stacked-query injection attempts).
    if len(non_empty) != 1:
        return False

    stmt_type = non_empty[0].get_type()

    # get_type() returns None for statements it cannot classify.
    return stmt_type == "SELECT"


# ── Query execution ──────────────────────────────────────────────────────────

def execute_sql(sql: str) -> list[dict]:
    """
    Run a SELECT statement against finsight.db and return rows as dicts.

    Calls is_safe_select() before execution. If the query is not a single
    SELECT statement, raises UnsafeQueryError immediately without touching
    the database.

    Using sqlite3.Row as the row_factory means each row behaves like a dict
    (column-name access) without any extra conversion step. The connection
    is managed with a context manager so it is always closed, even if an
    exception is raised.

    Args:
        sql: A valid SQLite SELECT statement.

    Returns:
        A list of dicts, one per row, with column names as keys.

    Raises:
        UnsafeQueryError: If the SQL is not a single SELECT statement.
        sqlite3.Error: If the SQL is malformed or execution fails.
    """
    if not is_safe_select(sql):
        raise UnsafeQueryError(
            f"Query rejected by safety guard — only single SELECT statements are "
            f"permitted. Received: {sql!r}"
        )

    with sqlite3.connect(_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # rows accessible by column name
        cursor = conn.execute(sql)
        rows = cursor.fetchall()

    # Convert sqlite3.Row objects to plain dicts for easy serialisation
    # and compatibility with the rest of the pipeline.
    return [dict(row) for row in rows]
