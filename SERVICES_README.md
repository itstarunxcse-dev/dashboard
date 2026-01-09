# 🚀 Services Architecture - Updated

## Overview
The project now uses a **microservices architecture** with three separate API services:

1. **ML Signal Service** (Port 8001) - Provides live and historical ML predictions
2. **Backtesting Service** (Port 8002) - VectorBT-powered backtesting engine
3. **Alerts Service** (Port 8003) - Email alerts with scheduled jobs

---

## 📊 1. ML Signal Service

**Location:** `signals/api.py`  
**Port:** 8001  
**Tech Stack:** FastAPI, yfinance, scikit-learn, XGBoost

### Endpoints:

#### POST `/api/v1/ml/signal/live`
**Purpose:** Get today's signal for dashboard
```json
Request:
{
  "ticker": "AAPL"
}

Response:
{
  "ticker": "AAPL",
  "signal": "BUY",
  "expected_return": 0.0234,
  "current_price": 175.43,
  "confidence": 85.5,
  "timestamp": "2026-01-09T10:30:00"
}
```

#### POST `/api/v1/ml/signal/historical`
**Purpose:** Get 5 years of OHLCV + signals for backtesting
```json
Request:
{
  "ticker": "AAPL"
}

Response:
{
  "ticker": "AAPL",
  "rows": [
    {
      "date": "2021-01-04",
      "open": 133.52,
      "high": 133.61,
      "low": 126.76,
      "close": 129.41,
      "volume": 143301900,
      "signal": 1  // 1 = BUY, -1 = SELL
    },
    ...
  ],
  "total_rows": 1260
}
```

### Start Service:
```bash
# Windows
start_ml_service.bat

# Manual
uvicorn signals.api:app --host 0.0.0.0 --port 8001 --reload
```

---

## 🧮 2. Backtesting Service (VectorBT)

**Location:** `api/backtesting_api.py`  
**Engine:** `backtesting/engine_vectorbt.py`  
**Port:** 8002  
**Tech Stack:** FastAPI, VectorBT, pandas

### Features:
- High-performance vectorized backtesting
- ML strategy vs Market (Buy & Hold) comparison
- Confidence scoring (0-100)
- Trade-by-trade analysis
- Equity curves and PnL visualization

### Endpoint:

#### POST `/api/v1/backtest/run`
```json
Request:
{
  "ticker": "AAPL"
}

Response:
{
  "confidence_score": 73.5,
  "ml_metrics": {
    "total_return_pct": 145.3,
    "cagr_pct": 18.2,
    "volatility_pct": 22.1,
    "sharpe_ratio": 1.45,
    "max_drawdown_pct": -15.3,
    "total_equity_value": 2453000,
    "total_trades": 47,
    "win_rate_pct": 61.7
  },
  "market_metrics": {
    "total_return_pct": 98.4,
    "cagr_pct": 14.7,
    "volatility_pct": 25.3,
    "sharpe_ratio": 0.89,
    "max_drawdown_pct": -23.1
  },
  "trading_metrics": {
    "winning_trades": 29,
    "losing_trades": 18,
    "profit_factor": 2.1,
    "avg_win_price": 12.45,
    "avg_loss_price": -8.32
  },
  "equity_curve": [...],
  "pnl_graph": [...],
  "trade_visualization": {...}
}
```

### Start Service:
```bash
# Windows
start_backtesting_service.bat

# Manual
uvicorn api.backtesting_api:app --host 0.0.0.0 --port 8002 --reload
```

---

## 🔔 3. Alerts Service

**Location:** `alerts/main.py`  
**Port:** 8003  
**Tech Stack:** FastAPI, APScheduler, SMTP (Gmail)

### Features:
- Scheduled email alerts (10:00 AM, 12:30 PM, 3:00 PM daily)
- Fetches signals from ML Service automatically
- Background job processing with APScheduler
- Gmail integration with App Password

### Configuration:
Edit `alerts/main.py`:
```python
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Generate from Google Account
```

### Endpoints:

#### POST `/create-alert`
```json
Request:
{
  "user_email": "user@example.com",
  "ticker_name": "AAPL"
}

Response:
{
  "status": "success",
  "message": "Alerts set for AAPL at 10:00, 12:30, 15:00",
  "user": "user@example.com"
}
```

#### DELETE `/stop-alert/{user_email}/{ticker_name}`
Stops all scheduled alerts for a user/ticker combination.

### Start Service:
```bash
# Windows
start_alerts_service.bat

# Manual
uvicorn alerts.main:app --host 0.0.0.0 --port 8003 --reload
```

---

## 🔗 Service Communication Flow

```
┌──────────────┐
│  Streamlit   │
│  Dashboard   │
└──────┬───────┘
       │
       ├─────────────► ML Service (8001) ─────► Live Predictions
       │
       ├─────────────► Backtesting (8002) ────► Performance Analysis
       │                     │
       │                     └────────────────► ML Service (8001) [Historical Data]
       │
       └─────────────► Alerts Service (8003) ─► Scheduled Emails
                              │
                              └────────────────► ML Service (8001) [Signal Check]
```

---

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install VectorBT (for backtesting)
```bash
pip install -r backtesting/requirements_vectorbt.txt
```

### 3. Install APScheduler (for alerts)
```bash
pip install -r alerts/requirements.txt
```

---

## 🎯 Quick Start

### Start All Services (3 Terminals):
```bash
# Terminal 1: ML Service
start_ml_service.bat

# Terminal 2: Backtesting Service  
start_backtesting_service.bat

# Terminal 3: Alerts Service
start_alerts_service.bat
```

### Start Streamlit Dashboard:
```bash
streamlit run 0_Overview.py
```

---

## 🧪 Testing

### Test ML Service:
```bash
curl -X POST http://localhost:8001/api/v1/ml/signal/live \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### Test Backtesting Service:
```bash
curl -X POST http://localhost:8002/api/v1/backtest/run \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

### Test Alerts Service:
```bash
curl -X POST http://localhost:8003/create-alert \
  -H "Content-Type: application/json" \
  -d '{"user_email": "test@example.com", "ticker_name": "AAPL"}'
```

---

## 🗂️ File Structure

```
ProjD-main/
│
├── signals/
│   ├── api.py                    # ML Signal Service ⭐ UPDATED
│   ├── rf_model.pkl
│   └── xgb_model.pkl
│
├── backtesting/
│   ├── engine.py                 # Original engine (MACD-based)
│   ├── engine_vectorbt.py        # New VectorBT engine ⭐ NEW
│   └── requirements_vectorbt.txt
│
├── api/
│   ├── main.py
│   └── backtesting_api.py        # Backtesting API Service ⭐ NEW
│
├── alerts/
│   ├── main.py                   # Alerts Service ⭐ NEW
│   └── requirements.txt
│
├── app/
│   ├── data_loader.py            # Original data loader
│   ├── data_loader_vbt.py        # VectorBT data loader ⭐ NEW
│   ├── engine.py                 # Re-exports
│   └── schemas.py
│
├── start_ml_service.bat          ⭐ NEW
├── start_backtesting_service.bat ⭐ NEW
├── start_alerts_service.bat      ⭐ NEW
└── requirements.txt              # Updated with new dependencies
```

---

## 🔧 Key Changes from backtesting-and-alerts-main

### ✅ Implemented:
1. **VectorBT Engine** - High-performance backtesting
2. **Dual ML API** - Live + Historical endpoints
3. **Email Alerts** - APScheduler + Gmail SMTP
4. **Confidence Scoring** - ML vs Market performance
5. **Microservices Architecture** - 3 independent services

### 🔄 Integration Points:
- ML Service provides signals to both Dashboard and Backtesting
- Backtesting Service calls ML Service for historical data
- Alerts Service calls ML Service for real-time signal checks
- All services maintain backward compatibility with existing code

---

## 📝 Notes

- **Port 8001:** ML Signal Service (replaces old 8000)
- **Port 8002:** Backtesting Service
- **Port 8003:** Alerts Service
- Original `backtesting/engine.py` kept for compatibility
- Legacy endpoints in `signals/api.py` maintained

---

## 🚀 Next Steps

1. Update Gmail credentials in `alerts/main.py`
2. Test all three services independently
3. Integrate backtesting API calls in Strategy Analysis page
4. Add alert configuration UI in Alerts & Preferences page
5. Deploy services to cloud (AWS/Azure/GCP)

---

**Updated:** January 9, 2026  
**Architecture:** Microservices  
**Status:** ✅ Ready for Testing
