"""
db.py — SQLite execution layer for FinSight.

Deliberately kept separate from the LLM layer so it's easy to swap the
database engine later (e.g., move from SQLite to PostgreSQL) without
touching any AI-related code.
"""

import sqlite3
from pathlib import Path

# Resolve the DB path relative to this file so the script works from any
# working directory.
_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finsight.db"


def execute_sql(sql: str) -> list[dict]:
    """
    Run a SELECT statement against finsight.db and return rows as dicts.

    Using sqlite3.Row as the row_factory means each row behaves like a dict
    (column-name access) without any extra conversion step. The connection
    is managed with a context manager so it is always closed, even if an
    exception is raised.

    Args:
        sql: A valid SQLite SELECT statement.

    Returns:
        A list of dicts, one per row, with column names as keys.

    Raises:
        sqlite3.Error: If the SQL is malformed or execution fails.
    """
    with sqlite3.connect(_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # rows accessible by column name
        cursor = conn.execute(sql)
        rows = cursor.fetchall()

    # Convert sqlite3.Row objects to plain dicts for easy serialisation
    # and compatibility with the rest of the pipeline.
    return [dict(row) for row in rows]
