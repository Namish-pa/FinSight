"""
test_manual.py — Manual smoke-test for the FinSight query engine.

Run this script directly to verify the full pipeline (Gemini → SQLite → Groq)
is working end-to-end. Each question exercises a different part of the schema.

Usage:
    python -m query_engine.test_manual
    # or from the project root:
    uv run python -m query_engine.test_manual
"""

import sys

# Force UTF-8 output so Unicode characters in LLM responses (e.g. narrow
# no-break spaces in number formatting) don't crash the Windows cp1252 encoder.
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

from query_engine.engine import ask

TEST_QUESTIONS = [
    "How many invoices are overdue?",
    "What's the total unpaid amount for Enterprise customers?",
    "List the top 5 customers by outstanding balance",
    "Which payment method is used most often?",
    "What's our total cash balance across all accounts?",
    "How many customers are based in Mumbai?",
]

SEPARATOR = "-" * 60


def main() -> None:
    """Run all test questions and print results to stdout."""
    print(f"\nFinSight Query Engine - Manual Test\n{SEPARATOR}")

    for i, question in enumerate(TEST_QUESTIONS, start=1):
        print(f"\n[{i}/{len(TEST_QUESTIONS)}] Question: {question}")
        print(SEPARATOR)

        result = ask(question)

        print(f"  SQL       : {result.sql}")
        print(f"  Rows      : {len(result.rows)} row(s) returned")
        print(f"  Summary   : {result.summary}")
        print(SEPARATOR)

    print("\nAll tests completed.\n")


if __name__ == "__main__":
    main()
