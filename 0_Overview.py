import streamlit as st
import time

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Overview - AI Stock Trading",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. DATA MODELS (Easy to Edit) ---
# Centralize data here so you don't hunt through HTML code later
FEATURES = [
    {
        "icon": "📊",
        "title": "Trading Dashboard",
        "desc": "Real-time stock price visualization with interactive candlestick charts and volume analysis.",
        "color": "var(--primary-color)",
        "link": "pages/1_📊_AI_Signals.py",
        "btn_txt": "Open Dashboard"
    },
    {
        "icon": "📈",
        "title": "Technical Analysis",
        "desc": "Advanced indicators (RSI, MACD) combined with AI-driven prediction models.",
        "color": "var(--secondary-color)",
        "link": "pages/2_📈_Strategy_Analysis.py",
        "btn_txt": "View Analysis"
    },
    {
        "icon": "⚙️",
        "title": "Settings & AI Config",
        "desc": "Customize your trading preferences, risk tolerance, and AI model parameters.",
        "color": "var(--accent-color)",
        "link": "pages/3_⚙️_Alerts_&_Preferences.py",
        "btn_txt": "Configure"
    }
]

STATS = [
    {"value": "50+", "label": "Indicators", "color": "#6496ff"},
    {"value": "Real-Time", "label": "Data Feed", "color": "#00ff7f"},
    {"value": "94%", "label": "Uptime", "color": "#ffd700"},
    {"value": "Free", "label": "Open Source", "color": "#ff6347"},
]

# --- 3. STYLING ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* CSS Variables for easy theming */
        :root {
            --primary-color: #667eea;
            --secondary-color: #00ff7f;
            --accent-color: #ffd700;
            --bg-card: rgba(255, 255, 255, 0.05);
            --border-card: rgba(255, 255, 255, 0.1);
        }

        /* Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 40px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }

        .hero-container {
            text-align: center;
            padding: 60px 20px 40px;
            animation: fadeInUp 0.8s ease-out;
        }

        .hero-title {
            font-size: clamp(40px, 5vw, 72px); /* Responsive font size */
            font-weight: 900;
            background: linear-gradient(135deg, var(--primary-color) 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .hero-subtitle {
            font-size: clamp(16px, 2vw, 24px);
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 30px;
            font-weight: 300;
        }

        /* Cards */
        .feature-card {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            height: 100%; /* Fill column height */
            min-height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            backdrop-filter: blur(10px);
        }

        .feature-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.3);
            border-color: rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.08);
        }

        .card-icon { font-size: 40px; margin-bottom: 15px; }
        .card-title { font-size: 20px; font-weight: 700; color: white; margin-bottom: 10px; }
        .card-desc { font-size: 14px; color: rgba(255, 255, 255, 0.6); line-height: 1.6; flex-grow: 1;}

        /* Stats */
        .stat-box {
            background: rgba(18, 18, 18, 0.6);
            border-left: 4px solid;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .footer {
            margin-top: 80px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            font-size: 12px;
            color: rgba(255,255,255,0.4);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 4. COMPONENT FUNCTIONS ---

def render_hero():
    st.markdown("""
        <div class="hero-container">
            <div style="font-size: 60px; margin-bottom: 0px;">🤖</div>
            <div class="hero-title">AI Stock Signal Dashboard</div>
            <div class="hero-subtitle">
                Institutional-grade analysis powered by <span style="color: #f093fb;">Generative AI</span> & <span style="color: #667eea;">Machine Learning</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # IMPROVEMENT: Add a Quick Action search bar directly on Home
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            query = st.text_input("", placeholder="🔍 Enter Ticker (e.g., AAPL) to analyze immediately...", label_visibility="collapsed")
            if query:
                st.session_state['ticker'] = query.upper()
                st.toast(f"Redirecting to analysis for {query.upper()}...", icon="🚀")
                time.sleep(0.5)
                # Use st.switch_page if dashboard exists, otherwise handle gracefully
                try:
                    st.switch_page("pages/1_📊_AI_Signals.py")
                except:
                    st.error("Dashboard page not found. Please ensure 'pages/1_📊_AI_Signals.py' exists.")

def render_features():
    st.markdown("### ⚡ Core Capabilities")
    cols = st.columns(len(FEATURES))
    
    for i, col in enumerate(cols):
        feature = FEATURES[i]
        with col:
            # Render the Visual Card using HTML
            st.markdown(f"""
                <div class="feature-card" style="border-top: 3px solid {feature['color']};">
                    <div class="card-icon">{feature['icon']}</div>
                    <div class="card-title">{feature['title']}</div>
                    <div class="card-desc">{feature['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Render the Navigation Button (Native Streamlit)
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            try:
                st.page_link(
                    feature['link'], 
                    label=feature['btn_txt'], 
                    icon="👉", 
                    use_container_width=True
                )
            except Exception:
                # Fallback if page doesn't exist yet
                st.button(feature['btn_txt'], key=f"btn_{i}", disabled=True, help="Page under construction")

def render_stats():
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    cols = st.columns(len(STATS))
    
    for i, col in enumerate(cols):
        stat = STATS[i]
        with col:
            st.markdown(f"""
                <div class="stat-box" style="border-color: {stat['color']};">
                    <div style="font-size: 24px; font-weight: 800; color: {stat['color']};">{stat['value']}</div>
                    <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7;">{stat['label']}</div>
                </div>
            """, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
        <div class="footer">
            ⚠️ <strong>Disclaimer:</strong> This application is for educational purposes only. Not financial advice.<br>
            Always consult with a qualified financial advisor before making investment decisions.
        </div>
    """, unsafe_allow_html=True)

# --- 5. MAIN EXECUTION ---
def main():
    inject_custom_css()
    
    render_hero()
    st.markdown("---") 
    render_features()
    render_stats()
    render_footer()

if __name__ == "__main__":
    main()