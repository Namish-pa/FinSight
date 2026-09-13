"""
models.py — Forecasting models for FinSight.

Provides simple, transparent forecasting capabilities based on historical KPI data.
"""

import numpy as np
from datetime import datetime

def forecast_linear_regression(history: list[dict], months_ahead: int = 3, anchor_date: str = "2026-09-04") -> tuple[list[dict], dict | None]:
    """
    Generate a cash flow forecast using linear regression.
    
    This function fits a straight trend line (y = mx + b) through the historical 
    monthly net cash flow values. It uses this fitted line to extrapolate the 
    expected net cash flow for future months.
    
    Limitation:
        This model assumes the historical trend continues linearly. It does not account
        for seasonality, sudden market shifts, or changes in underlying business patterns.
    
    Args:
        history (list[dict]): Historical data, expected to have "month" (YYYY-MM) and "net".
                              Must be chronologically sorted.
        months_ahead (int): Number of future months to project.
        anchor_date (str): The current date (YYYY-MM-DD) to identify and exclude incomplete months.
        
    Returns:
        tuple[list[dict], dict | None]: Forecasted data with "month", "forecast_net", "method", 
                                        and the excluded partial month data (if any).
    """
    if not history:
        return [], None
        
    anchor_month = anchor_date[:7]
    fit_history = history
    excluded_month = None
    
    # Exclude the anchor month from fitting as it's typically incomplete
    if history and history[-1]['month'] == anchor_month:
        excluded_month = history[-1]
        fit_history = history[:-1]
        
    if len(fit_history) < 2:
        return [], excluded_month
        
    # Prepare x and y arrays for regression
    n_history = len(fit_history)
    x = np.arange(n_history)
    y = np.array([row['net'] for row in fit_history])
    
    # Fit line: y = mx + c (slope and intercept)
    slope, intercept = np.polyfit(x, y, 1)
    
    # Identify the last complete month in history to start projection
    last_month_str = fit_history[-1]['month']
    last_year, last_month = map(int, last_month_str.split('-'))
    
    forecasts = []
    
    # If we excluded a month, we also want to forecast that exact month 
    # to show what the complete month is predicted to be, so we offset.
    # But usually "months_ahead" means from the current point.
    # Let's project sequentially after the last complete month.
    for i in range(1, months_ahead + 1):
        # Calculate future index
        future_x = (n_history - 1) + i
        
        # Extrapolate value
        projected_net = (slope * future_x) + intercept
        
        # Calculate future month label handling year rollover
        total_months = last_month + i - 1
        future_year = last_year + (total_months // 12)
        future_month = (total_months % 12) + 1
        future_month_str = f"{future_year}-{future_month:02d}"
        
        forecasts.append({
            "month": future_month_str,
            "forecast_net": round(float(projected_net), 2),
            "method": "linear_regression",
            "slope": float(slope),
            "intercept": float(intercept)
        })
        
    return forecasts, excluded_month
