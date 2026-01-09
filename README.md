# AI-Powered Stock & ETF Signal Generation Platform

> **Auto-Start Integration** - January 9, 2026

Comprehensive stock trading platform with AI predictions, real-time data, and Supabase integration.

---

## 🚀 Quick Start (One Command - Everything Auto-Starts!)

```bash
streamlit run 0_Overview.py
```

**That's it!** The dashboard automatically:
- ✅ Starts API server in background
- ✅ Checks and installs dependencies
- ✅ Trains ML models if missing
- ✅ Opens interactive dashboard
- ✅ No separate setup needed!

**Access Points:**
- 📊 Dashboard: http://localhost:8501
- 📡 API: http://127.0.0.1:8000
- 📚 API Docs: http://127.0.0.1:8000/docs

---

## 🎯 Features

- ✅ **One-Command Startup** - Everything auto-starts
- ✅ **Background API Server** - Starts automatically with dashboard
- ✅ **8 REST API Endpoints** - Supabase-ready
- ✅ **Auto-dependency Management** - No manual setup
- ✅ **ML Models** - Random Forest + XGBoost ensemble
- ✅ **Interactive Dashboard** - Real-time stock analysis
- ✅ **Smart Port Detection** - Auto-finds available ports

---

## 📡 API Endpoints

**Base URL:** `http://127.0.0.1:8000`

### System & Pipeline
- `GET /health` - Health check
- `POST /run-pipeline` - Trigger data pipeline

### Stock Data & Charts
- `GET /supabase/recent/{ticker}?days=30` - Recent data
- `GET /supabase/ticker/{ticker}?start_date=2024-01-01&limit=100` - Historical data

### Market Overview
- `GET /supabase/latest?limit=10` - Latest market data
- `GET /supabase/top-performers?top_n=10` - Top performers

### Analysis
- `GET /supabase/stats/{ticker}?start_date=2024-01-01` - Statistics
- `GET /supabase/rsi-search?min_rsi=0&max_rsi=30` - RSI-based search

---

## 🧪 Testing

```bash
# Test all API endpoints
python test_api_endpoints.py
```

---

## 📁 Project Structure

```
ProjD-main/
├── 0_Overview.py        # Main dashboard (AUTO-STARTS API!)
├── signals/             # API & ML Models
│   ├── start_api.py    # Manual API starter (if needed)
│   ├── api.py          # FastAPI server
│   ├── train_and_save.py # Model training
│   └── requirements.txt # Dependencies
├── utils/
│   └── api_starter.py  # Background API launcher
├── pages/              # Dashboard pages
├── data/               # Data fetchers & adapters
├── ml/                 # ML predictor
└── ui/                 # UI components
```

---

## 🔧 Manual Steps (Only If Needed)

### Run API Server Only
```bash
python signals/start_api.py
```

### Install Dependencies Only
```bash
pip install -r signals/requirements.txt
```

### Train Models Only
```bash
cd signals
python train_and_save.py
```

---

## 📚 Full Documentation

See [docs/README.md](docs/README.md) for complete documentation.

---

## ⚡ How It Works

1. **Run Dashboard:** `streamlit run 0_Overview.py`
2. **Auto-Detection:** Checks if API is running
3. **Auto-Start:** Launches API in background if needed
4. **Auto-Setup:** Installs dependencies & trains models
5. **Ready!** Everything works seamlessly

---

**Version:** 2.0.0 - Auto-Start Integration  
**Updated:** January 9, 2026  
**API by:** Aman (DE Team)
