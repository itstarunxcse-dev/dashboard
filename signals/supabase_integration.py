# -*- coding: utf-8 -*-
"""
Supabase Integration Template
Replace signals/api.py placeholder responses with real database queries
"""

import os
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "clean_market")  # Default matches pipeline output

# Validate credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️  WARNING: Supabase credentials not found in .env file")
    print("   Create a .env file with SUPABASE_URL and SUPABASE_KEY")
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        supabase = None


# --- Helper Functions ---

def test_connection():
    """Test Supabase connection"""
    if not supabase:
        return {"status": "error", "message": "Supabase not configured"}
    
    try:
        result = supabase.table(SUPABASE_TABLE).select("*").limit(1).execute()
        return {
            "status": "success",
            "message": f"Connected to {SUPABASE_TABLE}",
            "records": len(result.data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Data Fetching Functions (Ready to integrate into api.py) ---

def get_recent_ticker_data(ticker: str, days: int = 30):
    """Get recent data for a specific ticker"""
    if not supabase:
        return {"data": [], "error": "Supabase not configured"}
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("ticker", ticker.upper())\
            .gte("date", cutoff_date)\
            .order("date", desc=True)\
            .execute()
        
        return {
            "ticker": ticker.upper(),
            "days": days,
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        return {"data": [], "error": str(e)}


def get_ticker_with_range(ticker: str, start_date: str, limit: int = 100):
    """Get ticker data with date range and limit"""
    if not supabase:
        return {"data": [], "error": "Supabase not configured"}
    
    try:
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("ticker", ticker.upper())\
            .gte("date", start_date)\
            .order("date", desc=True)\
            .limit(limit)\
            .execute()
        
        return {
            "ticker": ticker.upper(),
            "start_date": start_date,
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        return {"data": [], "error": str(e)}


def get_latest_market_data(limit: int = 10):
    """Get latest market data across all tickers"""
    if not supabase:
        return {"data": [], "error": "Supabase not configured"}
    
    try:
        # Get most recent date first
        recent = supabase.table(SUPABASE_TABLE)\
            .select("date")\
            .order("date", desc=True)\
            .limit(1)\
            .execute()
        
        if not recent.data:
            return {"data": [], "message": "No data available"}
        
        latest_date = recent.data[0]["date"]
        
        # Get all tickers for that date
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("date", latest_date)\
            .limit(limit)\
            .execute()
        
        return {
            "date": latest_date,
            "count": len(result.data),
            "data": result.data
        }
    except Exception as e:
        return {"data": [], "error": str(e)}


def get_top_performers(top_n: int = 10, days: int = 30):
    """Get top performing stocks by price change"""
    if not supabase:
        return {"performers": [], "error": "Supabase not configured"}
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Get data for calculation
        result = supabase.table(SUPABASE_TABLE)\
            .select("ticker, date, close")\
            .gte("date", cutoff_date)\
            .order("date", desc=False)\
            .execute()
        
        # Calculate performance per ticker
        performance = {}
        for row in result.data:
            ticker = row["ticker"]
            if ticker not in performance:
                performance[ticker] = {"first": row["close"], "last": row["close"]}
            else:
                performance[ticker]["last"] = row["close"]
        
        # Calculate percentage change
        performers = []
        for ticker, prices in performance.items():
            if prices["first"] > 0:
                pct_change = ((prices["last"] - prices["first"]) / prices["first"]) * 100
                performers.append({
                    "ticker": ticker,
                    "change_pct": round(pct_change, 2),
                    "start_price": prices["first"],
                    "end_price": prices["last"]
                })
        
        # Sort and get top N
        performers.sort(key=lambda x: x["change_pct"], reverse=True)
        
        return {
            "top_n": top_n,
            "period_days": days,
            "performers": performers[:top_n]
        }
    except Exception as e:
        return {"performers": [], "error": str(e)}


def get_ticker_statistics(ticker: str, start_date: str):
    """Get statistical analysis for a ticker"""
    if not supabase:
        return {"stats": {}, "error": "Supabase not configured"}
    
    try:
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("ticker", ticker.upper())\
            .gte("date", start_date)\
            .execute()
        
        if not result.data:
            return {"stats": {}, "message": "No data found"}
        
        # Calculate statistics
        closes = [float(row["close"]) for row in result.data if "close" in row]
        volumes = [int(row["volume"]) for row in result.data if "volume" in row]
        
        stats = {
            "ticker": ticker.upper(),
            "period_start": start_date,
            "period_end": result.data[-1]["date"] if result.data else None,
            "data_points": len(result.data),
            "price_high": max(closes) if closes else 0,
            "price_low": min(closes) if closes else 0,
            "price_avg": sum(closes) / len(closes) if closes else 0,
            "volume_avg": sum(volumes) / len(volumes) if volumes else 0,
        }
        
        return {"stats": stats}
    except Exception as e:
        return {"stats": {}, "error": str(e)}


def search_by_rsi(min_rsi: float = 0, max_rsi: float = 100, limit: int = 50):
    """Search stocks by RSI range (oversold/overbought)"""
    if not supabase:
        return {"results": [], "error": "Supabase not configured"}
    
    try:
        # Get most recent date
        recent = supabase.table(SUPABASE_TABLE)\
            .select("date")\
            .order("date", desc=True)\
            .limit(1)\
            .execute()
        
        if not recent.data:
            return {"results": [], "message": "No data available"}
        
        latest_date = recent.data[0]["date"]
        
        # Search by RSI range
        result = supabase.table(SUPABASE_TABLE)\
            .select("*")\
            .eq("date", latest_date)\
            .gte("rsi", min_rsi)\
            .lte("rsi", max_rsi)\
            .limit(limit)\
            .execute()
        
        return {
            "date": latest_date,
            "min_rsi": min_rsi,
            "max_rsi": max_rsi,
            "count": len(result.data),
            "results": result.data
        }
    except Exception as e:
        return {"results": [], "error": str(e)}


# --- Main Test ---
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING SUPABASE CONNECTION")
    print("="*60 + "\n")
    
    # Test connection
    conn_test = test_connection()
    print(f"Connection Test: {conn_test}")
    print()
    
    if conn_test["status"] == "success":
        print("✅ All functions ready to integrate into signals/api.py")
        print("\nNext steps:")
        print("1. Import these functions in signals/api.py")
        print("2. Replace placeholder returns with function calls")
        print("3. Test with: python test_new_api_endpoints.py")
    else:
        print("⚠️  Setup .env file with Supabase credentials first")
        print("\nCreate .env file with:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_KEY=your-service-role-key")
