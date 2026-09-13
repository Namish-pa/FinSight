"""
test_forecast.py — Sanity tests for the forecasting module.

Fetches historical cash flow from the KPI module, runs the linear regression
forecast, and prints the results for verification.
"""

from kpi.metrics import calculate_monthly_cashflow
from forecasting.models import forecast_linear_regression

def main():
    print("=" * 50)
    print("FinSight Forecasting Module - Manual Test")
    print("=" * 50)
    
    # Get historical data
    history = calculate_monthly_cashflow()
    
    if not history:
        print("No historical data available. Cannot forecast.")
        return
        
    print(f"\n--- Historical Net Cash Flow (Last {min(6, len(history))} months) ---")
    for row in history[-6:]:
        print(f"   {row['month']}: ${row['net']:,.2f}")
        
    # Run forecast
    forecasts, excluded_month = forecast_linear_regression(history, months_ahead=3)
    
    if excluded_month:
        print(f"\n--- Note on Model Fitting ---")
        print(f"   Month {excluded_month['month']} was excluded from the regression fit.")
        print(f"   Reason: It is an incomplete/partial month (anchor date is 2026-09-04),")
        print(f"           and including its artificially low net (${excluded_month['net']:,.2f}) would skew the trend.")
    
    print("\n--- 3-Month Linear Regression Forecast ---")
    for row in forecasts:
        print(f"   {row['month']}: ${row['forecast_net']:,.2f}")
        
    # Print slope and intercept (available in the dict)
    if forecasts:
        slope = forecasts[0].get('slope', 0.0)
        intercept = forecasts[0].get('intercept', 0.0)
        print(f"\n--- Model Parameters ---")
        print(f"   Slope     : {slope:,.2f} (change per month)")
        print(f"   Intercept : {intercept:,.2f} (starting point)")
        
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
