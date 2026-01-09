# -*- coding: utf-8 -*-
"""
API Testing Script
Test all new endpoints from DE team
"""

from data.api_client import DashboardAPIClient
import sys

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /health")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.check_health()
        print("✅ SUCCESS")
        print(f"Status: {result.get('status')}")
        print(f"Version: {result.get('version')}")
        print(f"Models Loaded: {result.get('models_loaded')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_pipeline():
    """Test pipeline endpoint"""
    print("\n" + "="*60)
    print("Testing: POST /run-pipeline")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.run_pipeline()
        print("✅ SUCCESS")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_recent_data():
    """Test recent data endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/recent/AAPL?days=30")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.get_recent_data("AAPL", days=30)
        print("✅ SUCCESS")
        print(f"Ticker: {result.get('ticker')}")
        print(f"Days: {result.get('days')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_ticker_data():
    """Test ticker data endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/ticker/MSFT")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.get_ticker_data("MSFT", start_date="2024-01-01", limit=10)
        print("✅ SUCCESS")
        print(f"Ticker: {result.get('ticker')}")
        print(f"Start Date: {result.get('start_date')}")
        print(f"Limit: {result.get('limit')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_latest_market():
    """Test latest market endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/latest?limit=10")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.get_latest_market(limit=10)
        print("✅ SUCCESS")
        print(f"Limit: {result.get('limit')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_top_performers():
    """Test top performers endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/top-performers?top_n=10")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.get_top_performers(top_n=10)
        print("✅ SUCCESS")
        print(f"Top N: {result.get('top_n')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_ticker_stats():
    """Test ticker stats endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/stats/GOOGL")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.get_ticker_stats("GOOGL", start_date="2024-01-01")
        print("✅ SUCCESS")
        print(f"Ticker: {result.get('ticker')}")
        print(f"Start Date: {result.get('start_date')}")
        print(f"End Date: {result.get('end_date')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_rsi_search():
    """Test RSI search endpoint"""
    print("\n" + "="*60)
    print("Testing: GET /supabase/rsi-search (Oversold stocks)")
    print("="*60)
    try:
        client = DashboardAPIClient()
        result = client.search_by_rsi(min_rsi=0, max_rsi=30)
        print("✅ SUCCESS")
        print(f"Min RSI: {result.get('min_rsi')}")
        print(f"Max RSI: {result.get('max_rsi')}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "🚀 "*30)
    print("API ENDPOINT TESTING SUITE")
    print("Base URL: http://127.0.0.1:8000")
    print("🚀 "*30)
    
    tests = [
        ("Health Check", test_health),
        ("Pipeline Control", test_pipeline),
        ("Recent Data", test_recent_data),
        ("Ticker Data", test_ticker_data),
        ("Latest Market", test_latest_market),
        ("Top Performers", test_top_performers),
        ("Ticker Stats", test_ticker_stats),
        ("RSI Search", test_rsi_search)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n💡 Note: Endpoints return placeholder data until Supabase is connected")
    
    return passed == total

if __name__ == "__main__":
    print("\n⚠️  Make sure the API server is running:")
    print("   cd signals")
    print("   python api.py")
    print("\nPress Enter to continue...")
    input()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
