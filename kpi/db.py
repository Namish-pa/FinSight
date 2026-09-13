"""
db.py — SQLite connection manager for the KPI layer.

This module provides a helper function to connect to the central FinSight database.
It is kept completely independent of query_engine to ensure the KPI layer operates
without any dependencies on the LLM or natural language query logic.
"""

import sqlite3
from pathlib import Path

# Resolve the path to data/finsight.db
_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "finsight.db"

def get_connection() -> sqlite3.Connection:
    """
    Open and return a new sqlite3 connection to the FinSight database.
    
    The connection has row_factory set to sqlite3.Row so that records can
    be accessed by column name, making data manipulation easier.
    
    Returns:
        sqlite3.Connection: A database connection object.
    """
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
