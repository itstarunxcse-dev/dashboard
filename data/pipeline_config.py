# -*- coding: utf-8 -*-
"""
Pipeline Data Configuration
Centralized configuration for the Al-Powered-Stock-ETF-Signal-Generation-Platform-pipeline
"""

import os
from pathlib import Path

# Pipeline paths
PROJECT_ROOT = Path(__file__).parent.parent
PIPELINE_PATH = PROJECT_ROOT / "Al-Powered-Stock-ETF-Signal-Generation-Platform-pipeline"
PIPELINE_DATA_PATH = PIPELINE_PATH / "data"

# Data files
CLEAN_DATA_FILE = PIPELINE_DATA_PATH / "clean_market.parquet"
FEATURED_DATA_FILE = PIPELINE_DATA_PATH / "featured_market.parquet"
RAW_DATA_FILE = PIPELINE_DATA_PATH / "raw_market.parquet"
TICKER_ENCODER_FILE = PIPELINE_DATA_PATH / "ticker_encoder.parquet"
TICKER_FILE = PIPELINE_DATA_PATH / "ticker.txt"

# Data source configuration
DATA_SOURCE = 'pipeline'  # Options: 'pipeline', 'csv', 'yfinance'

# Column mappings - Pipeline to Standard format
PIPELINE_TO_STANDARD_COLUMNS = {
    'date': 'Date',
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume',
    'ticker': 'Ticker',
    'daily_return': 'Return',
    'ma20': 'SMA_20',
    'ma50': 'SMA_50',
    'rsi': 'RSI_14',
    'macd': 'MACD',
    'volatility': 'Volatility',
    'ema12': 'EMA_12',
    'ema26': 'EMA_26',
    'macd_signal': 'MACD_Signal',
    'volume_change': 'Volume_Change',
    'close_ma20_ratio': 'Close_MA20_Ratio'
}

# Standard columns expected by ML and backtesting modules
STANDARD_COLUMNS = [
    'Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume',
    'Return', 'SMA_20', 'SMA_50', 'RSI_14', 'MACD', 'Volatility'
]

# Backtesting configuration
INITIAL_CAPITAL = 1000000.0
COMMISSION = 0.002  # 0.2%

# API endpoints (if using pipeline APIs)
PIPELINE_API_URL = "http://localhost:8000"
LIVE_INDICATOR_API_URL = "http://localhost:8001"
