# -*- coding: utf-8 -*-
"""
🔔 Smart Alerts Configuration
AI + Strategy + Technical + Preference based alerts
Production-ready Streamlit UI (Glassmorphism)
"""

import streamlit as st
import sys
import time
from pathlib import Path
from typing import Dict, Any

# ======================================================
# PROJECT SETUP
# ======================================================
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Alerts & Preferences",
    page_icon="🔔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# DEFAULT CONFIGURATION
# ======================================================
ALERT_DEFAULTS: Dict[str, Any] = {
    "alerts_enabled": True,

    # AI Signals
    "alert_buy": True,
    "alert_sell": True,
    "alert_hold": False,
    "alert_conf_threshold": 75,

    # Strategy
    "alert_trend_reversal": True,
    "alert_support_resistance": False,

    # Technicals
    "alert_rsi_ob": True,
    "alert_rsi_os": True,
    "alert_macd": True,

    # Preferences
    "alert_sound": "Ping",
    "alert_position": "Top Right",
    "alert_duration": 5,
}

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

    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .info-box {
        background: rgba(99,102,241,.14);
        border-left: 3px solid #6366f1;
        border-radius: 12px;
        padding: 16px;
        font-size: .9rem;
        color: #e0e7ff;
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
# STATE MANAGEMENT
# ======================================================
def init_session_state():
    for key, value in ALERT_DEFAULTS.items():
        st.session_state.setdefault(key, value)

def reset_to_defaults():
    for key, value in ALERT_DEFAULTS.items():
        st.session_state[key] = value

def alerts_disabled() -> bool:
    return not st.session_state.alerts_enabled

# ======================================================
# BACKEND CONFIG EXPORT
# ======================================================
def collect_alert_config() -> Dict[str, Any]:
    """Final config passed to backend / ML engine"""
    return {
        "enabled": st.session_state.alerts_enabled,
        "ai": {
            "signals": {
                "buy": st.session_state.alert_buy,
                "sell": st.session_state.alert_sell,
                "hold": st.session_state.alert_hold,
            },
            "confidence_threshold": st.session_state.alert_conf_threshold
        },
        "strategy": {
            "trend_reversal": st.session_state.alert_trend_reversal,
            "support_resistance": st.session_state.alert_support_resistance
        },
        "technicals": {
            "rsi": {
                "overbought": st.session_state.alert_rsi_ob,
                "oversold": st.session_state.alert_rsi_os
            },
            "macd": st.session_state.alert_macd
        },
        "ui": {
            "sound": st.session_state.alert_sound,
            "position": st.session_state.alert_position,
            "duration_sec": st.session_state.alert_duration
        }
    }

# ======================================================
# MAIN UI
# ======================================================
def main():
    load_glass_styles()
    init_session_state()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------
    status_color = "#4ade80" if st.session_state.alerts_enabled else "#f87171"
    status_text = "ACTIVE" if st.session_state.alerts_enabled else "PAUSED"

    st.markdown(f"""
    <div class="glass-header">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="gradient-text" style="font-size:36px;">
                    🔔 Alerts & Preferences
                </div>
                <div style="opacity:.65;">
                    Configure AI-driven & market-based alerts
                </div>
            </div>
            <div style="background:rgba(255,255,255,.06);padding:12px 20px;border-radius:14px;">
                <small>Status</small><br>
                <b style="color:{status_color}">● {status_text}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    # MASTER SWITCH
    # --------------------------------------------------
    col1, col2 = st.columns([1, 2])

    with col1:
        glass_card("Master Control", "🔌")
        st.toggle("Enable Alerts", key="alerts_enabled")
        st.caption("Disable to instantly mute all alerts.")
        glass_card_end()

    with col2:
        st.markdown("""
        <div class="glass-card info-box">
            Alerts are generated by the ML engine and delivered as
            in-app notifications or external integrations.
        </div>
        """, unsafe_allow_html=True)

    if alerts_disabled():
        st.warning("Enable alerts to configure settings.")
        return

    # --------------------------------------------------
    # CONFIGURATION PANELS
    # --------------------------------------------------
    left, right = st.columns(2)

    with left:
        glass_card("AI Signals", "🤖")
        st.checkbox("BUY", key="alert_buy")
        st.checkbox("SELL", key="alert_sell")
        st.checkbox("HOLD", key="alert_hold")
        st.slider("Confidence Threshold (%)", 60, 99, key="alert_conf_threshold")
        glass_card_end()

        glass_card("Strategy Events", "🎯")
        st.checkbox("Trend Reversal", key="alert_trend_reversal")
        st.checkbox("Support / Resistance Break", key="alert_support_resistance")
        glass_card_end()

    with right:
        glass_card("Technical Indicators", "📊")
        st.checkbox("RSI Overbought", key="alert_rsi_ob")
        st.checkbox("RSI Oversold", key="alert_rsi_os")
        st.checkbox("MACD Crossover", key="alert_macd")
        glass_card_end()

        glass_card("Notification Preferences", "⚙️")
        st.selectbox("Sound", ["Ping", "Chime", "Silent"], key="alert_sound")
        st.selectbox("Position", ["Top Right", "Bottom Right"], key="alert_position")
        st.slider("Duration (seconds)", 3, 30, key="alert_duration")
        glass_card_end()

    # --------------------------------------------------
    # ACTIONS
    # --------------------------------------------------
    save, reset = st.columns([3, 1])

    with save:
        if st.button("💾 Save Configuration", type="primary", width='stretch'):
            with st.spinner("Saving alert configuration..."):
                time.sleep(0.6)
                st.session_state.saved_alert_config = collect_alert_config()
            st.success("Alert configuration saved successfully.")

            with st.expander("🔍 Preview JSON (Backend Payload)"):
                st.json(st.session_state.saved_alert_config)

    with reset:
        if st.button("↩ Reset", width='stretch'):
            reset_to_defaults()
            st.rerun()

# ======================================================
if __name__ == "__main__":
    main()
