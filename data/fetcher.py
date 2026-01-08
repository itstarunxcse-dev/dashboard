# -*- coding: utf-8 -*-
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from contracts.schema import StockData
from typing import Optional
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline integration
try:
    from data.pipeline_adapter import get_pipeline_data, is_pipeline_available
    from data.pipeline_config import DATA_SOURCE
    PIPELINE_AVAILABLE = True
except ImportError:
    PIPELINE_AVAILABLE = False
    DATA_SOURCE = 'yfinance'

class DataEngine:
    @staticmethod
    def fetch_data(symbol: str, period: str = "1y", interval: str = "1d", 
                   use_pipeline: bool = None) -> StockData:
        """
        Fetches market data and calculates technical indicators.
        
        Data sources (priority order):
        1. Pipeline data (if configured and available)
        2. Yahoo Finance (yfinance) - fallback
        
        Cached for 5 minutes to improve performance.
        """
        import streamlit as st
        
        @st.cache_data(ttl=300, show_spinner=False)
        def _fetch_cached(symbol: str, period: str, interval: str, use_pipeline_flag: bool) -> dict:
            data = DataEngine._fetch_uncached(symbol, period, interval, use_pipeline_flag)
            return data.dict()
        
        should_use_pipeline = use_pipeline if use_pipeline is not None else (DATA_SOURCE == 'pipeline')
        data_dict = _fetch_cached(symbol, period, interval, should_use_pipeline)
        return StockData(**data_dict)
    
    @staticmethod
    def _fetch_uncached(symbol: str, period: str, interval: str, use_pipeline: bool = False) -> StockData:
        """Internal method to fetch data without caching"""
        
        # Try pipeline first if configured
        if use_pipeline and PIPELINE_AVAILABLE and is_pipeline_available():
            try:
                return DataEngine._fetch_from_pipeline(symbol, period)
            except Exception as e:
                print(f"⚠️ Error fetching from pipeline: {e}. Falling back to yfinance...")
        
        # Fallback to yfinance
        return DataEngine._fetch_from_yfinance(symbol, period, interval)
    
    @staticmethod
    def _fetch_from_pipeline(symbol: str, period: str) -> StockData:
        """
        Fetch data from pipeline.
        
        Args:
            symbol: Stock ticker symbol
            period: Time period (converted to days)
        
        Returns:
            StockData object
        """
        # Convert period to date range
        end_date = datetime.now()
        period_days = {
            '1d': 1, '5d': 5, '1mo': 30, '3mo': 90,
            '6mo': 180, '1y': 365, '2y': 730, '5y': 1825, 'ytd': 365, 'max': 3650
        }
        days = period_days.get(period, 365)
        start_date = end_date - timedelta(days=days)
        
        # Get data from pipeline
        df = get_pipeline_data(
            ticker=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )
        
        if df.empty:
            raise ValueError(f"No data in pipeline for {symbol}")
        
        # Extract latest values
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
        
        price_change = current_price - prev_close
        price_change_pct = (price_change / prev_close) * 100 if prev_close else 0
        
        # Market status
        market_status = "Open" if datetime.now().weekday() < 5 else "Closed"
        
        return StockData(
            symbol=symbol.upper(),
            current_price=float(current_price),
            price_change=float(price_change),
            price_change_pct=float(price_change_pct),
            last_updated=datetime.now(),
            market_status=market_status,
            dates=df.index.strftime('%Y-%m-%d').tolist(),
            opens=df['Open'].tolist(),
            highs=df['High'].tolist(),
            lows=df['Low'].tolist(),
            closes=df['Close'].tolist(),
            volumes=df['Volume'].astype(int).tolist(),
            rsi=df['RSI_14'].tolist() if 'RSI_14' in df.columns else [50] * len(df),
            sma_20=df['SMA_20'].tolist() if 'SMA_20' in df.columns else df['Close'].tolist(),
            sma_50=df['SMA_50'].tolist() if 'SMA_50' in df.columns else df['Close'].tolist(),
            ema_12=df['EMA_12'].tolist() if 'EMA_12' in df.columns else df['Close'].tolist(),
            ema_26=df['EMA_26'].tolist() if 'EMA_26' in df.columns else df['Close'].tolist(),
            macd=df['MACD'].tolist() if 'MACD' in df.columns else [0] * len(df),
            macd_signal=df['MACD_Signal'].tolist() if 'MACD_Signal' in df.columns else [0] * len(df),
            macd_hist=(df['MACD'] - df['MACD_Signal']).tolist() if 'MACD' in df.columns and 'MACD_Signal' in df.columns else [0] * len(df)
        )
    
    @staticmethod
    def _fetch_from_yfinance(symbol: str, period: str, interval: str) -> StockData:
        """Original yfinance implementation"""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            # Calculate Indicators
            df['RSI'] = DataEngine._calculate_rsi(df['Close'])
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
            
            # MACD
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
            
            # Fill NaNs for JSON serialization
            df = df.fillna(0)
            
            # Get latest info
            try:
                info = ticker.info
                current_price = info.get('currentPrice', df['Close'].iloc[-1])
                prev_close = info.get('previousClose', df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1])
            except Exception:
                # Fallback if info fetch fails
                current_price = df['Close'].iloc[-1]
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1]

            price_change = current_price - prev_close
            price_change_pct = (price_change / prev_close) * 100 if prev_close else 0
            
            # Determine market status (simple heuristic)
            # In a real app, we'd check exchange hours
            market_status = "Open" if datetime.now().weekday() < 5 else "Closed"

            return StockData(
                symbol=symbol.upper(),
                current_price=float(current_price),
                price_change=float(price_change),
                price_change_pct=float(price_change_pct),
                last_updated=datetime.now(),
                market_status=market_status,
                dates=df.index.strftime('%Y-%m-%d').tolist(),
                opens=df['Open'].tolist(),
                highs=df['High'].tolist(),
                lows=df['Low'].tolist(),
                closes=df['Close'].tolist(),
                volumes=df['Volume'].astype(int).tolist(),
                rsi=df['RSI'].tolist(),
                sma_20=df['SMA_20'].tolist(),
                sma_50=df['SMA_50'].tolist(),
                ema_12=df['EMA_12'].tolist(),
                ema_26=df['EMA_26'].tolist(),
                macd=df['MACD'].tolist(),
                macd_signal=df['MACD_Signal'].tolist(),
                macd_hist=df['MACD_Hist'].tolist()
            )
            
        except Exception as e:
            raise RuntimeError(f"Data Engineering Error: {str(e)}")

    @staticmethod
    def _calculate_rsi(series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def load_historical_data(csv_path: str = "ml_trading_signals.csv") -> pd.DataFrame:
        """
        Load historical trading data from CSV file.
        
        Args:
            csv_path: Path to the CSV file (default: "ml_trading_signals.csv")
        
        Returns:
            pd.DataFrame with Date index and columns: Open, High, Low, Close, Volume, Signal
            Signal: 1 = buy, -1 = sell, 0 = hold
        """
        df = pd.read_csv(csv_path)
        
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        df.set_index("Date", inplace=True)
        
        df = df.sort_index().dropna()
        
        # Expected columns:
        # Open, High, Low, Close, Volume, Signal (1 buy, -1 sell, 0 hold)
        
        return df
    
    @staticmethod
    def load_ml_signals_data(csv_path: str = "ml_trading_signals.csv", 
                             ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Load ML trading signals dataset with comprehensive technical indicators.
        
        Args:
            csv_path: Path to the CSV file
            ticker: Optional ticker symbol to filter (e.g., 'AAPL')
        
        Returns:
            pd.DataFrame with Date index and all trading data including ML predictions
        """
        df = pd.read_csv(csv_path)
        
        # Parse date with day-first format
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
        df.set_index("Date", inplace=True)
        
        # Sort and clean
        df = df.sort_index().dropna()
        
        # Filter by ticker if specified
        if ticker and 'Ticker' in df.columns:
            df = df[df['Ticker'] == ticker].copy()
        
        return df
    
    @staticmethod
    def prepare_ml_data_for_backtest(csv_path: str = "ml_trading_signals.csv",
                                     ticker: str = "AAPL") -> pd.DataFrame:
        """
        Prepare ML signals data for backtesting engine.
        
        Args:
            csv_path: Path to the CSV file
            ticker: Ticker symbol to filter (default: 'AAPL')
        
        Returns:
            pd.DataFrame formatted for BacktestEngine with required columns
        """
        df = DataEngine.load_ml_signals_data(csv_path, ticker)
        
        # Create a clean dataframe with only needed columns for backtesting
        backtest_df = pd.DataFrame({
            'Open': df['Open'],
            'High': df['High'],
            'Low': df['Low'],
            'Close': df['Close'],
            'Volume': df['Volume'].astype(int),
            'Signal': df['Signal'].astype(int)
        })
        
        return backtest_df

