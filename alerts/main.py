import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Default values (can be updated via API)
EMAIL_SENDER = "tarunsivasai03@gmail.com"  
EMAIL_PASSWORD = "odsi iyiq ywar zvba"   

app = FastAPI(title="Alerts Middleware API", version="2.1")

from pytz import timezone

# Initialize Scheduler with User's Timezone
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.start()

@app.delete("/clear-all-alerts")
def clear_all_alerts():
    """Stop/Delete ALL scheduled alerts"""
    scheduler.remove_all_jobs()
    return {"status": "success", "message": "All active alerts have been cleared."}

# ==========================================
# 2. DATA MODELS
# ==========================================
class AlertRequest(BaseModel):
    user_email: str
    ticker_name: str
    alert_time: str = None # Format: "HH:MM" for specific time
    alert_date: str = None # Optional: "YYYY-MM-DD" for one-time alerts
    interval_minutes: int = None # Optional: For recurring interval alerts

# ==========================================
# 3. CORE FUNCTIONS
# ==========================================
def fetch_ml_signal(ticker: str):
    """
    Connects to the ML Team's API to get the latest signal.
    """
    try:
        url = "http://localhost:8000/api/v1/ml/signal/live"
        response = requests.post(url, json={"ticker": ticker}, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ [ML API Error] {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ [Connection Failed] Could not connect to ML API: {e}")
        return None

def send_email_alert(user_email: str, ticker: str, signal_data: dict):
    """
    Sends a real email to the user using Gmail SMTP.
    """
    global EMAIL_SENDER, EMAIL_PASSWORD
    
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("❌ [Email Error] Credentials not configured.")
        return

    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_type = signal_data.get('signal', 'UNKNOWN')
        price = signal_data.get('current_price', 'N/A')
        confidence = f"{signal_data.get('confidence', 0):.2f}%"

        # HTML styled email body
        subject = f"🚨 ALERT: {signal_type} {ticker}"
        body = f"""
        Subject: {subject}

        TRADING ALERT SYSTEM
        ---------------------------------
        Time:       {current_time}
        Ticker:     {ticker}
        Signal:     {signal_type}
        Price:      {price}
        Confidence: {confidence}
        ---------------------------------
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = user_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, user_email, msg.as_string())

        print(f"✅ [Success] Email sent to {user_email} for {ticker}")

    except Exception as e:
        print(f"❌ [Email Failed] Could not send email: {e}")

def check_and_alert_job(user_email: str, ticker: str):
    """
    Scheduled job to check signal and send alert.
    """
    print(f"\n⏰ [Scheduler] Running check for {ticker} (User: {user_email})")

    # 1. Get Data from Live API
    data = fetch_ml_signal(ticker)

    if not data:
        print("⚠️ No data received from ML API.")
        return

    # 2. Check Signal & Send Email
    signal = data.get('signal')
    if signal in ["BUY", "SELL"]:
        print(f"🚀 Signal Detected: {signal}. Sending Email...")
        send_email_alert(user_email, ticker, data)
    else:
        print(f"ℹ️ Signal is {signal}. No alert needed.")

class InstantReportRequest(BaseModel):
    user_email: str
    ticker_name: str

# ==========================================
# 4. API ENDPOINTS
# ==========================================

@app.post("/instant-report")
def instant_report(request: InstantReportRequest):
    """Send an immediate stock report"""
    email = request.user_email
    ticker = request.ticker_name
    
    print(f"⚡ [Instant Report] Request for {ticker} -> {email}")
    
    # 1. Fetch Data
    data = fetch_ml_signal(ticker)
    if not data:
         raise HTTPException(status_code=404, detail=f"Could not fetch data for {ticker}. Check symbol.")
    
    # 2. Send Email
    try:
        # Construct a custom body for instant report? 
        # reusing send_email_alert is fine, it formats nicely.
        send_email_alert(email, ticker, data)
        return {"status": "success", "message": f"Instant report sent for {ticker}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-alert")
def create_alert(request: AlertRequest):
    """Create a new scheduled alert (Daily, One-Time, or Interval)"""
    email = request.user_email
    ticker = request.ticker_name
    time_str = request.alert_time
    date_str = request.alert_date
    interval_mins = request.interval_minutes
    
    # Create unique ID base
    base_id = f"{email}_{ticker}"
    if interval_mins:
        base_id += f"_every_{interval_mins}m"
    elif time_str:
        base_id += f"_{time_str.replace(':','')}"
    
    if date_str:
        base_id += f"_{date_str}"

    try:
        # --- INTERVAL ALERT ---
        if interval_mins and interval_mins > 0:
            job = scheduler.add_job(
                check_and_alert_job, 
                'interval', 
                minutes=interval_mins,
                id=base_id, 
                args=[email, ticker], 
                replace_existing=True
            )
            msg = f"Alert scheduled for {ticker} every {interval_mins} minutes"

        # --- SPECIFIC TIME ALERT ---
        elif time_str:
            # Parse time
            try:
                hour, minute = map(int, time_str.split(':'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")

            if date_str:
                # --- ONE-TIME ALERT ---
                from datetime import datetime
                run_date_str = f"{date_str} {time_str}:00"
                try:
                    run_date = datetime.strptime(run_date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                     raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
                
                # Use 'date' trigger for one-time execution
                job = scheduler.add_job(
                    check_and_alert_job, 
                    'date', 
                    run_date=run_date,
                    id=base_id, 
                    args=[email, ticker], 
                    replace_existing=True
                )
                msg = f"One-time alert set for {ticker} on {run_date_str}"
                
            else:
                # --- RECURRING DAILY ALERT ---
                job = scheduler.add_job(
                    check_and_alert_job, 
                    'cron', 
                    hour=hour, 
                    minute=minute,
                    id=base_id, 
                    args=[email, ticker], 
                    replace_existing=True
                )
                msg = f"Daily alert set for {ticker} at {time_str}"
        
        else:
             raise HTTPException(status_code=400, detail="Must provide unique Alert Time or Interval Minutes.")

        next_run = job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "Finished"
        return {"status": "success", "message": f"{msg}. Next run: {next_run}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/stop-alert/{user_email}/{ticker_name}")
def stop_alert(user_email: str, ticker_name: str):
    """Stop all alerts for a ticker"""
    base_id = f"{user_email}_{ticker_name}"
    removed_count = 0
    
    # Iterate and remove matching jobs
    for job in scheduler.get_jobs():
        if job.id.startswith(base_id):
            scheduler.remove_job(job.id)
            removed_count += 1
            
    if removed_count > 0:
        return {"status": "success", "message": f"Stopped {removed_count} alerts for {ticker_name}"}
    return {"status": "warning", "message": "No active alerts found"}

@app.get("/active-alerts")
def get_active_alerts():
    """List all active scheduled jobs"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "next_run": str(job.next_run_time),
            "args": job.args
        })
    return {"count": len(jobs), "jobs": jobs}

@app.get("/health")
def health_check():
    return {
        "status": "active", 
        "system": "Alerts Middleware API",
        "email_configured": bool(EMAIL_SENDER and EMAIL_PASSWORD)
    }

@app.post("/test-email")
def test_email_endpoint(email: str):
    """Send a test email immediately"""
    try:
        dummy_data = {
            "signal": "TEST_SIGNAL",
            "current_price": 123.45,
            "confidence": 99.9
        }
        send_email_alert(email, "TEST-TICKER", dummy_data)
        return {"status": "success", "message": f"Test email sent to {email}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
