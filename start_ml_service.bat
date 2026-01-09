# Start ML Signal Service on port 8001
uvicorn signals.api:app --host 0.0.0.0 --port 8001 --reload
