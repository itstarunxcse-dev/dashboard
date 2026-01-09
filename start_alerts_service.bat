# Start Alerts Service on port 8003
uvicorn alerts.main:app --host 0.0.0.0 --port 8003 --reload
