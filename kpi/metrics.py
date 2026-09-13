"""
metrics.py — Core financial KPI calculations.

This module provides deterministic, SQL/pandas-backed calculations for key 
financial metrics. It does not use any LLM generation, ensuring that metric 
reporting is 100% accurate and reproducible.
"""

import pandas as pd
from datetime import datetime
from kpi.db import get_connection

def calculate_dso() -> float:
    """
    Calculate Days Sales Outstanding (DSO).
    
    DSO measures the average number of days it takes a company to collect payment
    after a sale has been made. A lower DSO indicates faster collection.
    
    This function computes the average number of days between the invoice date 
    and the payment date for all invoices with status = 'paid'.
    
    Returns:
        float: Average days sales outstanding, rounded to 1 decimal place.
    """
    query = '''
        SELECT 
            i.invoice_date,
            p.payment_date
        FROM invoices i
        JOIN payments p ON i.invoice_id = p.invoice_id
        WHERE i.status = 'paid'
    '''
    
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
        
    if df.empty:
        return 0.0
        
    # Convert string dates to datetime objects
    df['invoice_date'] = pd.to_datetime(df['invoice_date'])
    df['payment_date'] = pd.to_datetime(df['payment_date'])
    
    # Calculate days between invoice and payment
    df['days_to_pay'] = (df['payment_date'] - df['invoice_date']).dt.days
    
    return round(float(df['days_to_pay'].mean()), 1)

def calculate_aging_buckets(anchor_date: str = "2026-09-04") -> dict:
    """
    Calculate Accounts Receivable (AR) Aging Buckets.
    
    AR Aging categorizes unpaid customer invoices by the number of days they are 
    overdue. This helps identify late-paying customers and assess credit risk.
    
    This function computes days overdue relative to the `anchor_date` for 
    invoices with status 'unpaid' or 'overdue'.
    
    Args:
        anchor_date (str): The date to calculate aging against (YYYY-MM-DD).
        
    Returns:
        dict: A mapping of aging buckets (e.g., "0-30", "31-60") to their invoice count and total amount.
    """
    query = '''
        SELECT 
            due_date,
            amount
        FROM invoices
        WHERE status IN ('unpaid', 'overdue')
    '''
    
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
        
    buckets = {
        "not_yet_due": {"count": 0, "total_amount": 0.0},
        "0-30": {"count": 0, "total_amount": 0.0},
        "31-60": {"count": 0, "total_amount": 0.0},
        "61-90": {"count": 0, "total_amount": 0.0},
        "90+": {"count": 0, "total_amount": 0.0}
    }
    
    if df.empty:
        return buckets
        
    anchor = pd.to_datetime(anchor_date)
    df['due_date'] = pd.to_datetime(df['due_date'])
    df['days_overdue'] = (anchor - df['due_date']).dt.days
    
    for _, row in df.iterrows():
        days = row['days_overdue']
        amount = row['amount']
        
        if days < 0:
            bucket_key = "not_yet_due"
        elif 0 <= days <= 30:
            bucket_key = "0-30"
        elif 31 <= days <= 60:
            bucket_key = "31-60"
        elif 61 <= days <= 90:
            bucket_key = "61-90"
        else:
            bucket_key = "90+"
            
        buckets[bucket_key]["count"] += 1
        buckets[bucket_key]["total_amount"] += amount
        
    # Round totals
    for k in buckets:
        buckets[k]["total_amount"] = round(buckets[k]["total_amount"], 2)
        
    return buckets

def calculate_cash_runway(anchor_date: str = "2026-09-04") -> float:
    """
    Calculate Cash Runway in months.
    
    Cash Runway indicates how many months a business can continue operating 
    at its current cash burn rate before running out of money.
    
    This function takes the current total balance of bank and cash accounts and
    divides it by the historical average monthly outflow. The balance is dynamically
    derived from opening_balance + net transaction history, rather than a static value.
    
    Args:
        anchor_date (str): The date used as a reference point (informational here).
        
    Returns:
        float: Estimated months of runway, rounded to 1 decimal place.
               Returns float('inf') if average monthly outflow is 0.
    """
    balance_query = '''
        SELECT SUM(balance) as total_balance 
        FROM accounts 
        WHERE account_type IN ('bank', 'cash')
    '''
    
    outflow_query = '''
        SELECT date, amount 
        FROM transactions 
        WHERE type = 'outflow'
    '''
    
    with get_connection() as conn:
        balance_df = pd.read_sql_query(balance_query, conn)
        outflow_df = pd.read_sql_query(outflow_query, conn)
        
    total_balance = float(balance_df['total_balance'].iloc[0] or 0.0)
    
    if outflow_df.empty:
        return float('inf') # Infinite runway if no outflows
        
    outflow_df['date'] = pd.to_datetime(outflow_df['date'])
    # Group by year and month
    outflow_df['month'] = outflow_df['date'].dt.to_period('M')
    
    monthly_outflows = outflow_df.groupby('month')['amount'].sum()
    avg_monthly_outflow = monthly_outflows.mean()
    
    if avg_monthly_outflow == 0:
        return float('inf') # Infinite runway if outflows sum to 0
        
    runway = total_balance / avg_monthly_outflow
    return round(float(runway), 1)

def calculate_monthly_cashflow() -> list[dict]:
    """
    Calculate Net Monthly Cash Flow.
    
    Cash Flow tracks the total money flowing in and out of the business each month.
    This helps visualize trends in profitability and cash generation over time.
    
    This function groups all transactions by calendar month and type, summing the
    amounts to compute net cash flow (inflow - outflow) per month.
    
    Returns:
        list[dict]: A chronologically sorted list of dictionaries with monthly
                    inflow, outflow, and net amounts.
    """
    query = '''
        SELECT date, type, amount 
        FROM transactions
    '''
    
    with get_connection() as conn:
        df = pd.read_sql_query(query, conn)
        
    if df.empty:
        return []
        
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.strftime('%Y-%m') # Format as YYYY-MM
    
    # Pivot to get inflows and outflows as columns
    pivot_df = df.pivot_table(
        index='month', 
        columns='type', 
        values='amount', 
        aggfunc='sum',
        fill_value=0.0
    ).reset_index()
    
    # Ensure both columns exist even if data is missing one type
    if 'inflow' not in pivot_df.columns:
        pivot_df['inflow'] = 0.0
    if 'outflow' not in pivot_df.columns:
        pivot_df['outflow'] = 0.0
        
    pivot_df['net'] = pivot_df['inflow'] - pivot_df['outflow']
    
    # Sort chronologically
    pivot_df = pivot_df.sort_values('month')
    
    # Format and return as list of dicts
    results = []
    for _, row in pivot_df.iterrows():
        results.append({
            "month": row['month'],
            "inflow": round(float(row['inflow']), 2),
            "outflow": round(float(row['outflow']), 2),
            "net": round(float(row['net']), 2)
        })
        
    return results
