#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to fetch AMZN details using the data fetcher API
Returns comprehensive stock data as JSON
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from data.fetcher import DataEngine
from ml.predictor import MLEngine
from contracts.schema import StockData

def fetch_amzn_details():
    """
    Fetch Amazon (AMZN) stock details with MAXIMUM data and ML predictions
    Returns comprehensive analysis as JSON
    """
    print("=" * 70)
    print(" " * 15 + "FETCHING MAXIMUM AMZN STOCK DETAILS")
    print("=" * 70)
    print()
    
    # Initialize engines
    data_engine = DataEngine()
    ml_engine = MLEngine()
    
    # Fetch AMZN data with MAXIMUM history
    print("📊 Fetching Amazon (AMZN) stock data with maximum history...")
    print()
    
    try:
        # Fetch with MAXIMUM available data
        stock_data = data_engine.fetch_data(
            symbol="AMZN",
            period="max",  # Maximum available history
            interval="1d"
        )
        
        if stock_data is None:
            print("❌ Failed to fetch AMZN data")
            return None
        
        print("✅ Successfully fetched AMZN data")
        print()
        
        # Generate ML prediction
        print("🤖 Generating ML prediction...")
        ml_signal = ml_engine.predict(stock_data)
        print("✅ ML prediction generated")
        print()
        
        # Convert to dictionaries
        stock_dict = stock_data.model_dump()
        ml_dict = ml_signal.model_dump()
        
        # Combine all data
        comprehensive_data = {
            "stock_data": stock_dict,
            "ml_prediction": ml_dict,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Pretty print comprehensive summary
        print("=" * 70)
        print("COMPREHENSIVE AMZN ANALYSIS")
        print("=" * 70)
        print()
        print("📊 STOCK DATA SUMMARY")
        print("-" * 70)
        print(f"Symbol: {stock_dict['symbol']}")
        print(f"Current Price: ${stock_dict['current_price']:.2f}")
        print(f"Price Change: ${stock_dict['price_change']:.2f} ({stock_dict['price_change_pct']:.2f}%)")
        print(f"Market Status: {stock_dict['market_status']}")
        print(f"Last Updated: {stock_dict['last_updated']}")
        print()
        print(f"📈 Historical Data Points: {len(stock_dict['dates'])} days")
        print(f"📅 Date Range: {stock_dict['dates'][0]} to {stock_dict['dates'][-1]}")
        print(f"💰 Price Range: ${min(stock_dict['lows']):.2f} - ${max(stock_dict['highs']):.2f}")
        print(f"📊 Avg Volume: {sum(stock_dict['volumes']) / len(stock_dict['volumes']):,.0f}")
        print()
        
        # Technical indicators summary
        print("📈 TECHNICAL INDICATORS (Latest Values)")
        print("-" * 70)
        if stock_dict['rsi'] and len(stock_dict['rsi']) > 0:
            rsi = stock_dict['rsi'][-1]
            rsi_signal = "🔴 Overbought" if rsi > 70 else "🟢 Oversold" if rsi < 30 else "🟡 Neutral"
            print(f"RSI (14): {rsi:.2f} {rsi_signal}")
        if stock_dict['sma_20'] and len(stock_dict['sma_20']) > 0:
            sma20 = stock_dict['sma_20'][-1]
            price = stock_dict['current_price']
            trend = "🟢 Above" if price > sma20 else "🔴 Below"
            print(f"SMA (20): ${sma20:.2f} - Price {trend}")
        if stock_dict['sma_50'] and len(stock_dict['sma_50']) > 0:
            sma50 = stock_dict['sma_50'][-1]
            trend = "🟢 Above" if price > sma50 else "🔴 Below"
            print(f"SMA (50): ${sma50:.2f} - Price {trend}")
        if stock_dict['ema_12'] and len(stock_dict['ema_12']) > 0:
            print(f"EMA (12): ${stock_dict['ema_12'][-1]:.2f}")
        if stock_dict['ema_26'] and len(stock_dict['ema_26']) > 0:
            print(f"EMA (26): ${stock_dict['ema_26'][-1]:.2f}")
        if stock_dict['macd'] and len(stock_dict['macd']) > 0:
            macd = stock_dict['macd'][-1]
            macd_signal = stock_dict['macd_signal'][-1]
            macd_trend = "🟢 Bullish" if macd > macd_signal else "🔴 Bearish"
            print(f"MACD: {macd:.2f} {macd_trend}")
        if stock_dict['macd_signal'] and len(stock_dict['macd_signal']) > 0:
            print(f"MACD Signal: {stock_dict['macd_signal'][-1]:.2f}")
        if stock_dict['macd_hist'] and len(stock_dict['macd_hist']) > 0:
            print(f"MACD Histogram: {stock_dict['macd_hist'][-1]:.2f}")
        print()
        
        # ML Prediction Summary
        print("🤖 ML PREDICTION ANALYSIS")
        print("-" * 70)
        action_emoji = "🚀" if ml_dict['action'] == "BUY" else "💥" if ml_dict['action'] == "SELL" else "⏸️"
        print(f"Signal: {action_emoji} {ml_dict['action']}")
        print(f"Signal Value: {ml_dict['signal_value']} (1=BUY, 0=HOLD, -1=SELL)")
        print(f"Confidence: {ml_dict['confidence']:.1f}% ({ml_dict['confidence_level']})")
        print(f"Model: {ml_dict['model_type']} {ml_dict['model_version']}")
        print(f"Last Trained: {ml_dict['last_trained']}")
        print(f"Prediction Frequency: {ml_dict['prediction_frequency']}")
        print()
        print("Key Factors:")
        for i, factor in enumerate(ml_dict['key_factors'][:5], 1):
            print(f"  {i}. {factor}")
        print()
        print("Feature Importance (Top 5):")
        sorted_features = sorted(ml_dict['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:5]
        for feature, importance in sorted_features:
            bar = "█" * int(importance / 5)
            print(f"  {feature:.<30} {importance:>5.1f}% {bar}")
        print()
        
        print("💡 AI Reasoning:")
        print("-" * 70)
        reasoning_lines = ml_dict['reasoning'].split('\n')[:10]
        for line in reasoning_lines:
            print(f"  {line}")
        if len(ml_dict['reasoning'].split('\n')) > 10:
            print("  ... (see JSON file for full reasoning)")
        print()
        
        # Save comprehensive data to JSON file
        output_file = PROJECT_ROOT / "amzn_comprehensive_analysis.json"
        
        # Convert datetime objects to strings for JSON serialization
        stock_dict['last_updated'] = stock_dict['last_updated'].isoformat()
        ml_dict['timestamp'] = ml_dict['timestamp'].isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
        
        print("=" * 70)
        print(f"✅ Comprehensive JSON data saved to: {output_file}")
        print(f"   File size: {output_file.stat().st_size / 1024:.1f} KB")
        print("=" * 70)
        print()
        
        # Print JSON structure summary
        print("📄 JSON FILE STRUCTURE:")
        print("-" * 70)
        print(f"✓ stock_data:")
        print(f"  - Basic info: symbol, price, change, status")
        print(f"  - Historical data: {len(stock_dict['dates'])} days of OHLCV data")
        print(f"  - Technical indicators: RSI, SMA, EMA, MACD (all arrays)")
        print(f"✓ ml_prediction:")
        print(f"  - Signal: {ml_dict['action']} with {ml_dict['confidence']:.1f}% confidence")
        print(f"  - Key factors: {len(ml_dict['key_factors'])} factors")
        print(f"  - Feature importance: {len(ml_dict['feature_importance'])} features")
        print(f"  - Full AI reasoning included")
        print(f"✓ analysis_timestamp: {comprehensive_data['analysis_timestamp']}")
        print()
        
        return comprehensive_data
        
    except Exception as e:
        print(f"❌ Error fetching AMZN data: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = fetch_amzn_details()
    
    if result:
        stock = result['stock_data']
        ml = result['ml_prediction']
        
        print("=" * 70)
        print("✅ COMPREHENSIVE TEST COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print(f"📊 Stock Data: {len(stock['dates'])} days of history")
        print(f"💰 Price: ${stock['current_price']:.2f} ({stock['price_change_pct']:.2f}%)")
        print(f"🤖 ML Signal: {ml['action']} at {ml['confidence']:.1f}% confidence")
        print("📁 JSON file: amzn_comprehensive_analysis.json")
        print("=" * 70)
    else:
        print("=" * 70)
        print("❌ Test failed!")
        print("=" * 70)
        sys.exit(1)
