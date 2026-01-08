import streamlit as st
from typing import Tuple, List

# Define constants for easy maintenance
PERIOD_OPTIONS = ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"]
INTERVAL_OPTIONS = ["1d", "1wk", "1mo"]

def get_available_tickers() -> List[str]:
    """Get available tickers from pipeline or use defaults"""
    try:
        from data.pipeline_adapter import get_available_tickers, is_pipeline_available
        if is_pipeline_available():
            tickers = get_available_tickers()
            return tickers if tickers else get_default_tickers()
    except Exception:
        pass
    return get_default_tickers()

def get_default_tickers() -> List[str]:
    """Default ticker list if pipeline is not available"""
    return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]

@st.cache_data(ttl=600)
def get_ticker_options() -> List[str]:
    """Cache ticker options for 10 minutes"""
    return get_available_tickers()

def render_controls() -> Tuple[str, str, str]:
    """
    Renders minimalistic trading controls with pipeline integration.
    
    Returns:
        Tuple[str, str, str]: (symbol, period, interval)
    """
    # Get available tickers
    all_tickers = get_ticker_options()
    
    # 1. Search Input
    symbol = st.text_input(
        "🔍 Market Search",
        value="AAPL",
        placeholder="e.g. AAPL, MSFT, GOOGL",
        help=f"{len(all_tickers)} tickers available from pipeline"
    )

    # 2. Advanced Settings
    with st.expander("⚙️ Advanced Settings"):
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox("History", PERIOD_OPTIONS, index=3)
        with col2:
            interval = st.selectbox("Interval", INTERVAL_OPTIONS, index=0)

    # 3. Quick Select - Use all pipeline tickers
    quick_tickers = ["Custom Search"] + sorted(all_tickers)  # All available tickers, sorted
    quick_select = st.selectbox(
        "Quick Select",
        quick_tickers,
        index=0,
        help=f"Select from {len(all_tickers)} available tickers"
    )

    # Logic: Use Quick Select if active, otherwise use Search Input
    final_symbol = quick_select if quick_select != "Custom Search" else symbol
    
    return final_symbol.strip().upper(), period, interval