import joblib  # Using joblib to match your training script
import yfinance as yf
import pandas as pd
from fastapi import FastAPI
import uvicorn

app = FastAPI()

# Load models using joblib (safer for sklearn/xgboost)
try:
    rf_model = joblib.load("rf_model.pkl")
    xgb_model = joblib.load("xgb_model.pkl")
except Exception as e:
    print(f"Error loading models: {e}. Make sure .pkl files exist in this folder.")

FEATURES = ["Daily_Return", "Volatility", "SMA_ratio", "EMA_ratio", "MACD"]

def create_features(df):
    df = df.copy()
    
    # --- CRITICAL FIX FOR YFINANCE MULTI-INDEX ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Force 'Close' to be a Series
    close_series = df["Close"].squeeze()

    df["Daily_Return"] = close_series.pct_change()
    df["Volatility"] = df["Daily_Return"].rolling(14).std()
    df["SMA20"] = close_series.rolling(20).mean()
    df["EMA20"] = close_series.ewm(span=20, adjust=False).mean()
    df["SMA_ratio"] = close_series / df["SMA20"]
    df["EMA_ratio"] = close_series / df["EMA20"]

    ema12 = close_series.ewm(span=12, adjust=False).mean()
    ema26 = close_series.ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26

    df.dropna(inplace=True)
    return df

@app.get("/signal/{ticker}")
def get_signal(ticker: str):
    # period="6mo" ensures enough data for the 20-day SMA/EMA
    df = yf.download(ticker, period="6mo", auto_adjust=True, progress=False)
    
    if df.empty:
        return {"error": "Ticker not found or no data available"}

    processed_df = create_features(df)
    
    # Get the very last row for features
    latest_features = processed_df[FEATURES].tail(1)
    current_price = float(processed_df["Close"].iloc[-1])

    # Predict
    rf_pred = float(rf_model.predict(latest_features)[0])
    xgb_pred = float(xgb_model.predict(latest_features)[0])
    
    # Your target was 'Daily_Return'. 
    # To get a price prediction: current_price * (1 + predicted_return)
    rf_price = current_price * (1 + rf_pred)
    xgb_price = current_price * (1 + xgb_pred)
    avg_price = (rf_price + xgb_price) / 2

    signal = "BUY" if avg_price > current_price else "SELL"

    return {
        "ticker": ticker.upper(),
        "current_price": round(current_price, 2),
        "predicted_price_next_day": round(avg_price, 2),
        "expected_return": f"{round(((avg_price/current_price)-1)*100, 2)}%",
        "signal": signal
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
