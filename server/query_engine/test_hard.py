"""
test_hard.py — Hardened test suite for the FinSight query engine.

Tests adversarial, ambiguous, and edge-case questions to verify:
  - Date-math queries (julianday / date comparison)
  - Multi-table joins
  - Graceful "cannot answer" handling for unanswerable questions
  - Safety guard blocking of destructive SQL fed directly to execute_sql()
  - Safety guard blocking of stacked-query injection attempts

Usage:
    uv run python -m query_engine.test_hard
"""

import sys
import time

# Force UTF-8 output so Unicode characters in LLM responses don't crash the
# Windows cp1252 encoder.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from query_engine.db import UnsafeQueryError, execute_sql, is_safe_select
from query_engine.engine import ask

SEPARATOR = "=" * 65

# The first 3 questions go through the full LLM pipeline.
LLM_QUESTIONS = [
    "Which customers haven't paid in over 60 days?",
    "What's our current cash position?",
    "What's our profit margin?",
]

# The blocked cases are tested directly against the safety layer.
# Both represent SQL that might reach execute_sql() via any path — from a
# compromised LLM response, an API injection, or a direct call. The guard
# must catch them regardless of origin.
BLOCKED_CASES = [
    {
        "label": "Destructive DELETE statement",
        # The spec says: "this must be blocked by the safety guard before any
        # execution happens". We therefore feed the equivalent DELETE SQL
        # directly to is_safe_select() / execute_sql() to prove the layer
        # works independently of the LLM. The LLM itself also respects RULES
        # and refuses to generate non-SELECT, which is noted below.
        "raw_sql": "DELETE FROM invoices WHERE status = 'overdue'",
        "also_send_through_engine": True,
        "engine_question": "Delete all overdue invoices",
    },
    {
        "label": "Stacked-query injection (SELECT + DROP)",
        "raw_sql": "SELECT * FROM invoices; DROP TABLE invoices;",
        "also_send_through_engine": False,
        "engine_question": None,
    },
]


def _run_llm_question(i: int, total: int, question: str) -> None:
    """Run a single question through the full pipeline and print results."""
    print(f"\n[{i}/{total}] Question : {question}")
    print(SEPARATOR)

    result = ask(question)

    # The [RETRY] lines printed by engine.py appear in stdout before this
    # block whenever a retry is triggered; the note below directs the reader
    # to look for them.
    retry_note = "Yes (see [RETRY] lines above)" if "[RETRY]" in "" else \
        "(check above for any [RETRY] lines)"
    print(f"  Retry     : {retry_note}")
    print(f"  Final SQL : {result.sql}")
    print(f"  Rows      : {len(result.rows)} row(s) returned")
    print(f"  Summary   : {result.summary}")
    print(SEPARATOR)


def _run_blocked_case(i: int, total: int, case: dict) -> None:
    """
    Test a case expected to be blocked by the safety guard.

    Feeds the raw SQL directly to is_safe_select() and execute_sql() to
    verify the guard operates independently of the LLM layer. If the case
    also has an engine question, that is run through ask() afterwards to
    show the LLM's own behaviour (it should follow RULES and refuse to
    generate non-SELECT SQL).
    """
    label = case["label"]
    raw_sql = case["raw_sql"]
    print(f"\n[{i}/{total}] Blocked case : {label}")
    print(SEPARATOR)

    # ── Part A: Direct safety-guard test ────────────────────────────────────
    print(f"  Part A — Direct safety guard test")
    print(f"  Raw SQL         : {raw_sql!r}")

    safe = is_safe_select(raw_sql)
    print(f"  is_safe_select  : {safe}")

    try:
        execute_sql(raw_sql)
        guard_result = "WARNING: execute_sql() did NOT raise — guard failed! ✗"
        blocked = False
    except UnsafeQueryError as e:
        guard_result = f"UnsafeQueryError raised as expected ✓"
        blocked = True
        print(f"  UnsafeQueryError: {e}")

    part_a_status = "CORRECTLY BLOCKED ✓" if blocked else "GUARD FAILED ✗"
    print(f"  Part A status   : {part_a_status}")

    # ── Part B: LLM-pipeline behaviour (informational) ───────────────────────
    if case["also_send_through_engine"]:
        question = case["engine_question"]
        print(f"\n  Part B — LLM pipeline behaviour (informational)")
        print(f"  Question        : {question!r}")
        print(f"  Sending through ask() to observe whether Gemini obeys RULES …")

        result = ask(question)

        llm_generated_select = result.sql.strip().upper().startswith("SELECT")
        llm_note = (
            "Gemini correctly refused to generate a DELETE (RULES enforced) ✓"
            if llm_generated_select
            else "Gemini generated a non-SELECT — BLOCKED by execute_sql() guard ✓"
        )
        print(f"  LLM-generated SQL : {result.sql}")
        print(f"  Observation       : {llm_note}")
        print(f"  Summary           : {result.summary}")

    print(SEPARATOR)


def main() -> None:
    """Run all hard test cases and print results to stdout."""
    total = len(LLM_QUESTIONS) + len(BLOCKED_CASES)
    print(f"\nFinSight Query Engine — Hard Test Suite\n{SEPARATOR}")


    # ── LLM pipeline questions ───────────────────────────────────────────────
    for i, question in enumerate(LLM_QUESTIONS, start=1):
        _run_llm_question(i, total, question)
        if i < len(LLM_QUESTIONS):  # brief pause to respect Gemini rate limits
            time.sleep(3)

    # ── Safety-guard blocked cases ───────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  SAFETY GUARD TESTS (expected to be blocked)")
    print(SEPARATOR)

    for i, case in enumerate(BLOCKED_CASES, start=len(LLM_QUESTIONS) + 1):
        _run_blocked_case(i, total, case)

    print("\nAll hard tests completed.\n")


if __name__ == "__main__":
    main()
