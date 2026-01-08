import pandas as pd
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline adapter
try:
    from data.pipeline_adapter import get_pipeline_data, is_pipeline_available
    from data.pipeline_config import DATA_SOURCE
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    DATA_SOURCE = 'csv'

def load_historical_data(csv_path: str = "ml_trading_signals.csv",
                        ticker: str = None,
                        use_pipeline: bool = None) -> pd.DataFrame:
    """
    Load historical trading data from multiple sources.
    
    Data Sources (priority order):
    1. Pipeline data (if available and configured)
    2. CSV file (fallback)
    
    Args:
        csv_path: Path to the CSV file (default: "ml_trading_signals.csv")
        ticker: Optional ticker symbol to load (e.g., 'AAPL')
        use_pipeline: Force use of pipeline. If None, uses DATA_SOURCE config
    
    Returns:
        pd.DataFrame with Date index and columns: Open, High, Low, Close, Volume, Signal
        Signal: 1 = buy, -1 = sell, 0 = hold
    """
    # Determine data source
    should_use_pipeline = use_pipeline if use_pipeline is not None else (DATA_SOURCE == 'pipeline')
    
    # Try pipeline first if configured
    if should_use_pipeline and PIPELINE_AVAILABLE and is_pipeline_available():
        try:
            print(f"📊 Loading data from pipeline...")
            df = load_from_pipeline(ticker)
            
            if not df.empty:
                print(f"✅ Successfully loaded from pipeline. Shape: {df.shape}")
                return df
        except Exception as e:
            print(f"⚠️ Error loading from pipeline: {e}")
            print(f"Falling back to CSV file: {csv_path}")
    
    # Fallback to CSV
    return load_from_csv(csv_path, ticker)


def load_from_pipeline(ticker: str = None) -> pd.DataFrame:
    """
    Load data from pipeline.
    
    Args:
        ticker: Optional ticker symbol. If None, loads first available ticker.
    
    Returns:
        DataFrame with processed data including technical indicators
    """
    if not PIPELINE_AVAILABLE:
        raise ImportError("Pipeline module not available")
    
    try:
        # Get data from pipeline
        if ticker:
            df = get_pipeline_data(ticker=ticker)
        else:
            # Load first available ticker
            from data.pipeline_adapter import get_available_tickers
            tickers = get_available_tickers()
            if not tickers:
                raise ValueError("No tickers available in pipeline")
            
            # Prefer AAPL if available
            selected_ticker = 'AAPL' if 'AAPL' in tickers else tickers[0]
            df = get_pipeline_data(ticker=selected_ticker)
            print(f"📊 Loaded data for ticker: {selected_ticker}")
        
        # Generate Signal column if not present
        if 'Signal' not in df.columns:
            df['Signal'] = generate_signals_from_indicators(df)
        
        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    except Exception as e:
        raise ValueError(f"Failed to load data from pipeline: {e}")


def load_from_csv(csv_path: str, ticker: str = None) -> pd.DataFrame:
    """
    Load data from CSV file (original implementation).
    
    Args:
        csv_path: Path to CSV file
        ticker: Optional ticker to filter
    
    Returns:
        DataFrame with Date index
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    df.set_index("Date", inplace=True)
    
    df = df.sort_index().dropna()
    
    # If Ticker column exists, filter for specified ticker or default
    if 'Ticker' in df.columns:
        tickers = df['Ticker'].unique()
        if ticker and ticker in tickers:
            selected_ticker = ticker
        else:
            selected_ticker = 'AAPL' if 'AAPL' in tickers else tickers[0]
        df = df[df['Ticker'] == selected_ticker].copy()
        print(f"📊 Loaded data for ticker: {selected_ticker}")
    
    return df


def generate_signals_from_indicators(df: pd.DataFrame) -> pd.Series:
    """
    Generate trading signals from technical indicators.
    
    Strategy:
    - Buy (1): RSI < 30 (oversold) OR (MACD > 0 and Close > SMA_50)
    - Sell (-1): RSI > 70 (overbought) OR (MACD < 0 and Close < SMA_50)
    - Hold (0): Otherwise
    """
    signals = pd.Series(0, index=df.index)
    
    rsi = df.get('RSI_14', df.get('rsi', None))
    macd = df.get('MACD', df.get('macd', None))
    close = df.get('Close', df.get('close', None))
    sma_50 = df.get('SMA_50', df.get('ma50', None))
    
    if rsi is not None and macd is not None and close is not None and sma_50 is not None:
        # Buy signals
        buy_condition = (rsi < 30) | ((macd > 0) & (close > sma_50))
        signals[buy_condition] = 1
        
        # Sell signals
        sell_condition = (rsi > 70) | ((macd < 0) & (close < sma_50))
        signals[sell_condition] = -1
    
    return signals
