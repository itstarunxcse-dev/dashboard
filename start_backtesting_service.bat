# Start Backtesting API Service on port 8002
uvicorn api.backtesting_api:app --host 0.0.0.0 --port 8002 --reload
