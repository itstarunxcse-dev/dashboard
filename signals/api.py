import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Stock Dashboard API",
    description="API for Streamlit Dashboard - Supabase Integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML models
try:
    rf_model = joblib.load("rf_model.pkl")
    xgb_model = joblib.load("xgb_model.pkl")
    print("✅ Models loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Models not loaded: {e}")
    rf_model = None
    xgb_model = None

# --- System Health ---
@app.get("/health")
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": rf_model is not None and xgb_model is not None,
        "version": "2.0.0"
    }

# --- Pipeline Control ---
@app.post("/run-pipeline")
def run_pipeline():
    """Trigger data pipeline execution"""
    return {
        "status": "pipeline_started",
        "timestamp": datetime.now().isoformat(),
        "message": "Data pipeline execution triggered"
    }

# --- Stock Data & Charts ---
@app.get("/supabase/recent/{ticker}")
def get_recent_data(ticker: str, days: int = Query(30, description="Number of days")):
    """Get recent stock data for a ticker"""
    return {
        "ticker": ticker.upper(),
        "days": days,
        "data": [],
        "message": "Connect to Supabase for real data"
    }

@app.get("/supabase/ticker/{ticker}")
def get_ticker_data(
    ticker: str,
    start_date: str = Query("2024-01-01", description="Start date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Max records")
):
    """Get ticker data with date range and limit"""
    return {
        "ticker": ticker.upper(),
        "start_date": start_date,
        "limit": limit,
        "data": [],
        "message": "Connect to Supabase for real data"
    }

# --- Market Overview ---
@app.get("/supabase/latest")
def get_latest_market(limit: int = Query(10, description="Number of latest records")):
    """Get latest market data for all tickers"""
    return {
        "limit": limit,
        "data": [],
        "message": "Connect to Supabase for real data"
    }

@app.get("/supabase/top-performers")
def get_top_performers(top_n: int = Query(10, description="Top N performers")):
    """Get top performing stocks"""
    return {
        "top_n": top_n,
        "performers": [],
        "message": "Connect to Supabase for real data"
    }

# --- Analysis & Filtering ---
@app.get("/supabase/stats/{ticker}")
def get_ticker_stats(
    ticker: str,
    start_date: str = Query("2024-01-01", description="Start date (auto-ends today)")
):
    """Get statistical analysis for a ticker"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    return {
        "ticker": ticker.upper(),
        "start_date": start_date,
        "end_date": end_date,
        "stats": {},
        "message": "Connect to Supabase for real data"
    }

@app.get("/supabase/rsi-search")
def search_by_rsi(
    min_rsi: float = Query(0, description="Minimum RSI"),
    max_rsi: float = Query(30, description="Maximum RSI")
):
    """Search stocks by RSI range"""
    return {
        "min_rsi": min_rsi,
        "max_rsi": max_rsi,
        "results": [],
        "message": "Connect to Supabase for real data"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
