from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import traceback

from kpi.metrics import (
    calculate_dso,
    calculate_aging_buckets,
    calculate_cash_runway,
    calculate_monthly_cashflow,
)
from forecasting.models import forecast_linear_regression
from query_engine.engine import ask

app = FastAPI(title="FinSight API")

# Allow requests from the React frontend (Vite's default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str

@app.get("/api/kpis")
def get_kpis():
    try:
        dso = calculate_dso()
        aging_buckets = calculate_aging_buckets()
        cash_runway = calculate_cash_runway()
        monthly_cashflow = calculate_monthly_cashflow()
        
        return {
            "dso": dso,
            "aging_buckets": aging_buckets,
            "cash_runway": cash_runway,
            "monthly_cashflow": monthly_cashflow
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/forecast")
def get_forecast():
    try:
        history = calculate_monthly_cashflow()
        forecasts, excluded_month = forecast_linear_regression(history, months_ahead=3)
        return {
            "historical": history,
            "forecast": forecasts,
            "excluded_month": excluded_month
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask")
def post_ask(request: AskRequest):
    try:
        result = ask(request.question)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
