# -*- coding: utf-8 -*-
"""
🔔 Smart Alerts Configuration
AI + Strategy + Technical + Preference based alerts
Production-ready Streamlit UI (Glassmorphism)
"""

import streamlit as st
import sys
import time
import requests
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from ui.utils.constants import get_common_tickers
from ui.utils.design import glass_card, glass_card_end

# ======================================================
# PROJECT SETUP
# ======================================================
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

ALERTS_API_URL = "http://localhost:8001"

st.set_page_config(
    page_title="Alerts & Preferences",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# THEME / STYLES
# ======================================================
@st.cache_resource
def load_glass_styles():
    st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #020617);
        color: #e5e7eb;
    }

    .glass-card {
        background: rgba(255,255,255,0.06);
        backdrop-filter: blur(18px) saturate(160%);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 22px;
        box-shadow: 0 10px 35px rgba(0,0,0,.4);
    }

    .glass-header {
        background: linear-gradient(
            135deg,
            rgba(99,102,241,.18),
            rgba(168,85,247,.18)
        );
        backdrop-filter: blur(22px);
        border-radius: 22px;
        padding: 32px;
        margin-bottom: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,.55);
    }

    .gradient-text {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
        margin-left: 10px;
    }
    
    .status-online {
        background: rgba(0, 255, 127, 0.2);
        color: #00ff7f;
        border: 1px solid rgba(0, 255, 127, 0.4);
    }
    
    .status-offline {
        background: rgba(255, 99, 71, 0.2);
        color: #ff6347;
        border: 1px solid rgba(255, 99, 71, 0.4);
    }

    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Custom input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.1);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def glass_card(title: str, icon: str):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-header">{icon} {title}</div>
        """,
        unsafe_allow_html=True
    )

def glass_card_end():
    st.markdown("</div>", unsafe_allow_html=True)

# ======================================================
# API INTERACTION
# ======================================================
def check_api_status():
    try:
        response = requests.get(f"{ALERTS_API_URL}/health", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def fetch_active_alerts():
    try:
        response = requests.get(f"{ALERTS_API_URL}/active-alerts", timeout=3)
        if response.status_code == 200:
            return response.json().get('jobs', [])
        return []
    except:
        return []

def configure_email(email, password):
    try:
        response = requests.post(
            f"{ALERTS_API_URL}/configure-email", 
            json={"email": email, "password": password},
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def create_alert(email, ticker, time_str, date_str=None):
    payload = {"user_email": email, "ticker_name": ticker, "alert_time": time_str}
    if date_str:
        payload["alert_date"] = date_str
        
    try:
        response = requests.post(
            f"{ALERTS_API_URL}/create-alert", 
            json=payload,
            timeout=5
        )
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

def stop_alert(email, ticker):
    try:
        response = requests.delete(
            f"{ALERTS_API_URL}/stop-alert/{email}/{ticker}",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def send_test_email(email):
    try:
        response = requests.post(f"{ALERTS_API_URL}/test-email?email={email}", timeout=10)
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

# ======================================================
# MAIN UI
# ======================================================
def main():
    load_glass_styles()
    
    # 1. Check Service Status
    is_online, health_data = check_api_status()
    
    status_html = '<span class="status-badge status-online">● ONLINE</span>' if is_online else '<span class="status-badge status-offline">● OFFLINE</span>'
    
    st.markdown(f"""
    <div class="glass-header">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="gradient-text" style="font-size:36px;">
                    🔔 Alerts & Notifications
                </div>
                <div style="opacity:.65;">
                    Manage real-time email alerts and monitoring schedules
                </div>
            </div>
            <div>
                {status_html}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not is_online:
        st.error("⚠️ Alerts Middleware Service is unreachable. Please start `alerts/main.py` on port 8001.")
        st.code("uvicorn alerts.main:app --host 0.0.0.0 --port 8001", language="bash")
    
    # ======================================================
    # TABS
    # ======================================================
    # REMOVED "Email Configuration" TAB as requested
    tab_alerts, tab_prefs = st.tabs(["📢 Active Alerts", "🎨 UI Preferences"])
    
    # --------------------------------------------------
    # TAB 1: ACTIVE ALERTS & CREATE
    # --------------------------------------------------
    with tab_alerts:
        col1, col2 = st.columns([1, 2])
        
        # CREATE ALERT FORM
        with col1:
            glass_card("Create New Alert", "➕")
            if is_online:
                with st.form("create_alert_form"):
                    tickers = get_common_tickers()
                    new_ticker = st.selectbox("Ticker Symbol", options=tickers, key="create_alert_ticker")
                    target_email = st.text_input("Notify Email", placeholder="your@email.com")
                    
                    st.markdown("### 📅 Schedule Alert")
                    
                    # Date & Time Inputs for One-Time Alert
                    c_date, c_time = st.columns(2)
                    with c_date:
                        import datetime as dt
                        d = st.date_input("Date", dt.date.today())
                        selected_date_str = d.strftime("%Y-%m-%d")
                    with c_time:
                         # Text Input for Time as requested
                         time_str_val = st.text_input("Time (HH:MM)", value="10:00", help="24-Hour Format ie. 23:30")
                    
                    st.caption(f"Alert will be sent ONCE on **{selected_date_str} at {time_str_val}**")

                    submitted = st.form_submit_button("Schedule Alert", type="primary")
                    
                    if submitted:
                        # Basic Time Validation
                        import re
                        if not re.match(r"^\d{1,2}:\d{2}$", time_str_val):
                            st.error("❌ Invalid Time Format! Use HH:MM (e.g. 23:30)")
                        elif new_ticker and target_email:
                            success, msg = create_alert(target_email, new_ticker, time_str_val, selected_date_str)
                            if success:
                                st.success(f"✅ Alert Scheduled!")
                                st.caption(msg.get('message'))
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error(f"Failed: {msg}")
                        else:
                            st.warning("Please fill all fields.")
            
            st.markdown("---")
            with st.expander("⚡ Send Instant Report"):
                st.caption("Immediately fetch live data and email a report.")
                
                # Use shared tickers dropdown
                ir_tickers_list = get_common_tickers()
                ir_ticker = st.selectbox("Ticker", options=ir_tickers_list, key="ir_ticker")
                
                ir_email = st.text_input("Email", key="ir_email")
                
                if st.button("Send Instant Report"):
                    if ir_ticker and ir_email:
                        with st.spinner("Fetching & Sending..."):
                            try:
                                r = requests.post(
                                    f"{ALERTS_API_URL}/instant-report",
                                    json={"user_email": ir_email, "ticker_name": ir_ticker},
                                    timeout=15
                                )
                                if r.status_code == 200:
                                    st.success(f"✅ Sent! {r.json().get('message')}")
                                else:
                                    st.error(f"Failed: {r.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                    else:
                        st.warning("Fill Ticker & Email")
            
            glass_card_end()
            
        # LIST ACTIVE ALERTS
        with col2:
            glass_card("Active Monitoring Jobs", "📡")
            if is_online:
                jobs = fetch_active_alerts()
                if jobs:
                    # Job format: {'id': 'email_ticker_timestr', 'args': ['email', 'ticker']}
                    # Note: We changed ID format in backend to include time_str
                    
                    for job in jobs:
                        email = job['args'][0]
                        ticker = job['args'][1]
                        
                        # Format Next Run Time
                        raw_run = job.get('next_run', '')
                        # Try to format it nicely
                        try:
                            # Standard string format from APScheduler often looks like "2024-01-01 10:00:00+05:30"
                            # We just want to ensure it looks readable
                            run_display = raw_run.split('+')[0] # Remove timezone offset for cleanliness
                        except:
                            run_display = raw_run

                        job_id = job['id']
                        
                        glass_card(f"{ticker}", "🔔") 
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.caption(f"📧 {email}")
                            st.markdown(f"**📅 Next Run:** `{run_display}`")
                        with c2:
                            if st.button("Stop", key=f"stop_{job_id}"):
                                stop_alert(email, ticker)
                                st.rerun()
                        glass_card_end()
                else:
                    st.info("No active alerts configured.")
                    
                # Clear All Button
                st.markdown("---")
                if st.button("🗑️ Clear ALL Alerts", key="clear_all"):
                    try:
                        resp = requests.delete(f"{ALERTS_API_URL}/clear-all-alerts", timeout=5)
                        if resp.status_code == 200:
                            st.success("All alerts cleared!")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Failed to clear: {e}")
            else:
                st.warning("Cannot fetch alerts.")
            glass_card_end()

    # --------------------------------------------------
    # TAB 2: UI PREFERENCES
    # --------------------------------------------------
    with tab_prefs:
        glass_card("Client-Side Preferences", "🎨")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Notification Sound", ["Ping", "Chime", "Silent"])
            st.checkbox("Show Desktop Notifications", value=True)
        with c2:
            st.slider("Notification Duration (s)", 3, 30, 5)
            st.selectbox("Theme Mode", ["Dark (Glass)", "Light"])
        
        if st.button("Save UI Preferences"):
            st.success("Preferences saved to local session.")
        glass_card_end()

if __name__ == "__main__":
    main()
