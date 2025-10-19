#!/usr/bin/env python3
"""
Get 30-minute OHLC candle data from TradingView
Uses TradingView's data APIs

Note: TradingView doesn't have a simple public REST API for historical data.
Options:
1. Use tradingview-ta library (technical analysis only, limited historical)
2. Use TradingView's chart embed/UDF API (requires parsing)
3. Use TradingView webhook for real-time signals
"""
import requests
import json
from datetime import datetime, timedelta

def get_tradingview_data_option1():
    """
    Option 1: Try to use TradingView's public chart data endpoint
    This is used by their website but not officially documented
    """
    print("="*70)
    print("📊 Fetching Data from TradingView (Method 1: Chart API)")
    print("="*70)
    
    symbol = "NQ1!"  # Nasdaq 100 continuous contract
    exchange = "CME"
    interval = "30"  # 30 minutes
    
    print(f"\nSymbol: {symbol}")
    print(f"Exchange: {exchange}")
    print(f"Interval: {interval} minutes")
    
    try:
        # TradingView's unofficial chart data endpoint
        url = "https://scanner.tradingview.com/futures/scan"
        
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "symbols": {
                "tickers": [f"{exchange}:{symbol}"],
                "query": {"types": []}
            },
            "columns": [
                "name", "close", "open", "high", "low", "volume",
                "change", "change_abs"
            ]
        }
        
        print(f"\n🔍 Making request to TradingView scanner...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                ticker_data = data['data'][0]['d']
                
                print("\n✅ Data received!")
                print("\n" + "="*70)
                print("📈 Current NQ Data from TradingView")
                print("="*70)
                print(f"Symbol:  {ticker_data[0]}")
                print(f"Close:   ${ticker_data[1]:,.2f}")
                print(f"Open:    ${ticker_data[2]:,.2f}")
                print(f"High:    ${ticker_data[3]:,.2f}")
                print(f"Low:     ${ticker_data[4]:,.2f}")
                print(f"Volume:  {ticker_data[5]:,.0f}")
                print(f"Change:  ${ticker_data[7]:+,.2f} ({ticker_data[6]:+.2f}%)")
                print("="*70)
                
                print("\n⚠️  Note: This is current session data, not 30-min bars")
                return ticker_data
            else:
                print("❌ No data in response")
                return None
        else:
            print(f"❌ Request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_tradingview_data_option2():
    """
    Option 2: Use tradingview-ta library
    This provides technical analysis but limited historical data
    """
    print("\n" + "="*70)
    print("📊 Fetching Data from TradingView (Method 2: TA Library)")
    print("="*70)
    
    try:
        from tradingview_ta import TA_Handler, Interval
        
        print("\n🔍 Using tradingview-ta library...")
        
        handler = TA_Handler(
            symbol="NQ1!",
            exchange="CME",
            screener="america",
            interval=Interval.INTERVAL_30_MINUTES,
            timeout=10
        )
        
        analysis = handler.get_analysis()
        
        print("\n✅ Analysis received!")
        print("\n" + "="*70)
        print("📈 NQ Technical Analysis from TradingView")
        print("="*70)
        
        # Get indicators
        indicators = analysis.indicators
        
        print(f"Close:       ${indicators['close']:,.2f}")
        print(f"Open:        ${indicators['open']:,.2f}")
        print(f"High:        ${indicators['high']:,.2f}")
        print(f"Low:         ${indicators['low']:,.2f}")
        print(f"Volume:      {indicators['volume']:,.0f}")
        print(f"Change:      {indicators['change']:+.2f}%")
        
        print("\n" + "-"*70)
        print("Technical Indicators:")
        print(f"RSI:         {indicators.get('RSI', 'N/A')}")
        print(f"MACD:        {indicators.get('MACD.macd', 'N/A')}")
        print(f"EMA20:       ${indicators.get('EMA20', 0):,.2f}")
        print(f"SMA50:       ${indicators.get('SMA50', 0):,.2f}")
        
        print("\n" + "-"*70)
        print(f"Summary:     {analysis.summary['RECOMMENDATION']}")
        print(f"BUY:         {analysis.summary['BUY']}")
        print(f"SELL:        {analysis.summary['SELL']}")
        print(f"NEUTRAL:     {analysis.summary['NEUTRAL']}")
        print("="*70)
        
        print("\n⚠️  Note: This shows current bar data, not historical 30-min candles")
        
        return indicators
        
    except ImportError:
        print("\n❌ tradingview-ta library not installed")
        print("   Install with: pip install tradingview-ta")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def explain_tradingview_limitations():
    """
    Explain TradingView API limitations and alternatives
    """
    print("\n" + "="*70)
    print("💡 TradingView API Limitations & Alternatives")
    print("="*70)
    
    print("""
TradingView doesn't provide a simple public REST API for historical data.

Available Options:

1. ✅ Scanner API (Method 1 above)
   - Pros: No authentication needed
   - Cons: Only current session data, not historical bars
   - Use case: Real-time price monitoring

2. ✅ tradingview-ta Library (Method 2 above)
   - Pros: Easy to use, includes technical indicators
   - Cons: Current bar only, not historical candles
   - Use case: Technical analysis, current market state

3. ⚠️  TradingView Webhooks
   - Pros: Real-time signals from TradingView alerts
   - Cons: Requires TradingView Premium, one-way communication
   - Use case: Trigger trades from TradingView strategies

4. ⚠️  TradingView Chart Library
   - Pros: Full charting capabilities
   - Cons: Requires datafeed implementation, complex
   - Use case: Embedding charts in web applications

5. ❌ Official Historical Data API
   - Status: NOT PUBLICLY AVAILABLE
   - TradingView doesn't offer a direct API for historical OHLC data

RECOMMENDED ALTERNATIVES:

✅ Use Tradovate Chart/Bars API (Best for your use case)
   - Direct access to historical OHLC data
   - Same authentication you already have
   - See: get_nq_30min_tradovate.py

✅ Use Polygon.io API
   - Free tier: 5 API calls/minute
   - Historical bars in any timeframe
   - Clean REST API
   - Signup: https://polygon.io/

✅ Use Alpha Vantage API
   - Free tier: 5 calls/minute, 500/day
   - Good for stocks, limited futures support
   - API key: https://www.alphavantage.co/

✅ Aggregate Supabase Tick Data
   - You already have tick data stored
   - Create SQL function to generate OHLC bars
   - Zero additional cost
""")
    print("="*70)

if __name__ == "__main__":
    print("\n🚀 Testing TradingView Data Access\n")
    
    # Try Method 1: Scanner API
    data1 = get_tradingview_data_option1()
    
    # Try Method 2: TA Library
    data2 = get_tradingview_data_option2()
    
    # Explain limitations
    explain_tradingview_limitations()
    
    print("\n" + "="*70)
    print("🎯 CONCLUSION")
    print("="*70)
    print("""
For 30-minute OHLC historical data, use:
1. Tradovate Chart/Bars API ✅ (RECOMMENDED)
2. Aggregate your Supabase tick data ✅
3. Third-party data provider (Polygon.io, etc.) ✅

TradingView is best used for:
- Real-time signals via webhooks
- Technical analysis indicators
- Chart visualization
- Strategy alerts

NOT suitable for:
- Historical OHLC bar data retrieval
- Programmatic data access
""")
    print("="*70)
