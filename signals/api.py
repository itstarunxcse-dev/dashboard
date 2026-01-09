# -*- coding: utf-8 -*-
"""
🤖 ML Signal Service API
Dual-endpoint API for live predictions and historical signals
- Live Signal: For dashboard predictions
- Historical Signals: For backtesting engine
"""

import joblib
import yfinance as yf
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI(
    title="ML Signal Service",
    description="AI-Powered Stock Prediction API with Live & Historical Endpoints",
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

# =================================================
# LOAD MODELS
# =================================================
try:
    rf_model = joblib.load("rf_model.pkl")
    xgb_model = joblib.load("xgb_model.pkl")
    print("✅ Models loaded successfully")
except Exception as e:
    print(f"⚠️ Warning: Models not loaded: {e}")
    rf_model = None
    xgb_model = None

FEATURES = ["Daily_Return", "Volatility", "SMA_ratio", "EMA_ratio", "MACD"]

# =================================================
# FEATURE ENGINEERING
# =================================================
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Fix yfinance multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    close = df["Close"]

    df["Daily_Return"] = close.pct_change()
    df["Volatility"] = df["Daily_Return"].rolling(14).std()

    df["SMA20"] = close.rolling(20).mean()
    df["EMA20"] = close.ewm(span=20, adjust=False).mean()

    df["SMA_ratio"] = close / df["SMA20"]
    df["EMA_ratio"] = close / df["EMA20"]

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26

    df.dropna(inplace=True)
    return df

# =================================================
# REQUEST SCHEMA
# =================================================
class TickerRequest(BaseModel):
    ticker: str

# =================================================
# 1️⃣ LIVE SIGNAL API (Dashboard)
# =================================================
@app.post("/api/v1/ml/signal/live")
def get_live_signal(request: TickerRequest):
    """
    Used by Dashboard → Predict Signal button
    Returns only today's signal
    """
    if not rf_model or not xgb_model:
        raise HTTPException(status_code=503, detail="Models not loaded")
        
    ticker = request.ticker.upper()

    try:
        df = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for ticker")

        df = create_features(df)
        X = df[FEATURES].tail(1)

        rf_pred = rf_model.predict(X)[0]
        xgb_pred = xgb_model.predict(X)[0]
        avg_pred = (rf_pred + xgb_pred) / 2

        signal = "BUY" if avg_pred > 0 else "SELL"

        return {
            "ticker": ticker,
            "signal": signal,
            "expected_return": float(avg_pred),
            "current_price": float(df["Close"].iloc[-1]),
            "confidence": abs(float(avg_pred)) * 100,  # Confidence score
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =================================================
# 2️⃣ HISTORICAL SIGNALS API (Backtesting)
# =================================================
@app.post("/api/v1/ml/signal/historical")
def get_historical_signals(request: TickerRequest):
    """
    Used by Backtesting Engine
    Returns 5 years OHLCV + ML signals
    """
    if not rf_model or not xgb_model:
        raise HTTPException(status_code=503, detail="Models not loaded")
        
    ticker = request.ticker.upper()

    try:
        df = yf.download(ticker, period="5y", interval="1d", auto_adjust=True, progress=False)
        if df.empty:
            raise HTTPException(status_code=404, detail="No historical data")

        df = create_features(df)

        X = df[FEATURES]
        rf_preds = rf_model.predict(X)
        xgb_preds = xgb_model.predict(X)
        avg_preds = (rf_preds + xgb_preds) / 2

        df["Signal"] = np.where(avg_preds > 0, 1, -1)

        # Convert to JSON-safe structure
        records = []
        for date, row in df.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "signal": int(row["Signal"])
            })

        return {
            "ticker": ticker,
            "rows": records,
            "total_rows": len(records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =================================================
# LEGACY ENDPOINTS (Keep for backward compatibility)
# =================================================
@app.get("/health")
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": rf_model is not None and xgb_model is not None,
        "version": "2.0.0",
        "endpoints": {
            "live": "/api/v1/ml/signal/live",
            "historical": "/api/v1/ml/signal/historical"
        }
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

# =================================================
# RUN
# =================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

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
