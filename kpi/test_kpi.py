"""
test_kpi.py — Simple sanity tests for the KPI layer.

This script executes the four primary KPI calculations and prints their
results and corresponding row counts, allowing us to quickly eyeball
if the figures make sense against the generated dummy data.
"""

import pandas as pd
from kpi.db import get_connection
from kpi.metrics import (
    calculate_dso,
    calculate_aging_buckets,
    calculate_cash_runway,
    calculate_monthly_cashflow
)

def print_row_counts():
    """Print the number of rows in key tables for context."""
    print("--- Database Context (Row Counts) ---")
    with get_connection() as conn:
        customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        invoices = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0]
        payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        transactions = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        
    print(f"Customers    : {customers}")
    print(f"Invoices     : {invoices}")
    print(f"Payments     : {payments}")
    print(f"Transactions : {transactions}")
    print("-" * 37)

def main():
    print("=" * 50)
    print("FinSight KPI Module - Manual Test")
    print("=" * 50)
    
    print_row_counts()
    
    # 1. DSO
    dso = calculate_dso()
    print("\n1. Days Sales Outstanding (DSO)")
    print(f"   Result: {dso} days")
    
    # 2. Aging Buckets
    aging = calculate_aging_buckets()
    print("\n2. Accounts Receivable Aging Buckets")
    for bucket, data in aging.items():
        print(f"   {bucket:>12}: {data['count']:>3} invoices | Total: ${data['total_amount']:,.2f}")
        
    # 3. Cash Runway
    runway = calculate_cash_runway()
    print("\n3. Cash Runway")
    print(f"   Result: {runway} months")
    
    # 4. Monthly Cash Flow
    cashflow = calculate_monthly_cashflow()
    print("\n4. Monthly Cash Flow (Net)")
    if cashflow:
        print(f"   Showing {len(cashflow)} months...")
        for row in cashflow:
            print(f"   {row['month']}: In +${row['inflow']:,.2f} | Out -${row['outflow']:,.2f} | Net ${row['net']:,.2f}")
    else:
        print("   No cashflow data available.")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
