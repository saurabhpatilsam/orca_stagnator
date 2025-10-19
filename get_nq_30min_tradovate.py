#!/usr/bin/env python3
"""
Get 30-minute OHLC candle data from Tradovate Chart/Bars API
Uses the official Tradovate /chart/bars endpoint
"""
import os
import sys
import json
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def get_30min_candles_tradovate(instrument="MNQZ5", num_bars=10):
    """
    Fetch 30-minute candle data from Tradovate Chart/Bars API
    
    Args:
        instrument: Trading instrument (e.g., MNQZ5, ESZ5)
        num_bars: Number of bars to fetch
    
    Returns:
        List of OHLC candles
    """
    print("="*70)
    print("📊 Fetching 30-Min Candles from Tradovate Chart/Bars API")
    print("="*70)
    
    # Get Redis and token
    print("\n1. Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Redis connection failed")
        return None
    print("✅ Redis connected")
    
    # Find valid account
    print("\n2. Finding valid Tradovate account...")
    accounts = [
        "PAAPEX2666680000001",
        "PAAPEX2666680000002",
        "PAAPEX2666680000003"
    ]
    
    account_name = None
    for acc in accounts:
        token = redis_client.get(f"token:{acc}")
        if token:
            account_name = acc
            break
    
    if not account_name:
        print("❌ No valid token found")
        return None
    
    print(f"✅ Using account: {account_name}")
    
    # Initialize broker
    print("\n3. Initializing Tradovate broker...")
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        print("✅ Broker initialized")
    except Exception as e:
        print(f"❌ Failed to initialize broker: {e}")
        return None
    
    # Fetch chart data
    print(f"\n4. Fetching 30-minute bars for {instrument}...")
    print(f"   Endpoint: /chart/bars")
    
    try:
        # Chart description for 30-minute bars
        chart_description = {
            "underlyingType": "MinuteBar",
            "elementSize": 30,  # 30-minute bars
            "withHistogram": True
        }
        
        # Construct endpoint
        chart_desc_json = json.dumps(chart_description)
        endpoint = f"/chart/bars?symbol={instrument}&chartDescription={chart_desc_json}&locale=en"
        
        print(f"   Chart Description: {chart_description}")
        print(f"   Requesting last {num_bars} bars...")
        
        # Make request
        response = broker._make_request("GET", endpoint)
        
        if hasattr(response, 's') and response.s == 'ok':
            if hasattr(response, 'd') and response.d:
                bars = response.d
                
                print(f"\n✅ Received {len(bars)} bars from Tradovate!")
                
                # Parse bars
                candles = []
                for bar in bars[-num_bars:]:  # Get last N bars
                    candle = {
                        'timestamp': bar.get('t'),
                        'open': float(bar.get('o', 0)),
                        'high': float(bar.get('h', 0)),
                        'low': float(bar.get('l', 0)),
                        'close': float(bar.get('c', 0)),
                        'volume': int(bar.get('v', 0))
                    }
                    candles.append(candle)
                
                # Display results
                print("\n" + "="*70)
                print(f"📈 30-Minute Candles for {instrument}")
                print("="*70)
                
                for i, candle in enumerate(candles, 1):
                    time = datetime.fromisoformat(candle['timestamp'].replace('Z', '+00:00'))
                    change = candle['close'] - candle['open']
                    change_pct = (change / candle['open'] * 100) if candle['open'] > 0 else 0
                    
                    print(f"\n📊 Candle #{i}")
                    print(f"Time:    {time.strftime('%Y-%m-%d %H:%M')}")
                    print(f"Open:    ${candle['open']:,.2f}")
                    print(f"High:    ${candle['high']:,.2f}")
                    print(f"Low:     ${candle['low']:,.2f}")
                    print(f"Close:   ${candle['close']:,.2f}  ({change:+.2f}, {change_pct:+.2f}%)")
                    print(f"Volume:  {candle['volume']:,}")
                
                # Highlight last candle
                if candles:
                    last = candles[-1]
                    print("\n" + "="*70)
                    print("🎯 LAST 30-MIN CANDLE CLOSE")
                    print("="*70)
                    print(f"Time:    {datetime.fromisoformat(last['timestamp'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
                    print(f"Open:    ${last['open']:,.2f}")
                    print(f"High:    ${last['high']:,.2f}")
                    print(f"Low:     ${last['low']:,.2f}")
                    print(f"Close:   ${last['close']:,.2f}  ⭐")
                    print(f"Volume:  {last['volume']:,}")
                    print("="*70)
                
                return candles
            else:
                print("❌ No bar data in response")
                return None
        else:
            error_msg = response.errmsg if hasattr(response, 'errmsg') else 'Unknown error'
            print(f"❌ API error: {error_msg}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error fetching chart data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n🚀 Starting Tradovate Chart/Bars API Test\n")
    
    # Fetch 30-minute candles
    candles = get_30min_candles_tradovate(instrument="MNQZ5", num_bars=5)
    
    if candles:
        print("\n✅ Successfully fetched 30-minute OHLC data from Tradovate!")
        print(f"   Total candles received: {len(candles)}")
        
        if candles:
            last_close = candles[-1]['close']
            print(f"\n🎯 Answer: Last 30-min candle CLOSE = ${last_close:,.2f}")
    else:
        print("\n❌ Failed to fetch candle data")
        print("\n💡 Possible reasons:")
        print("   1. Market is closed (no recent bars)")
        print("   2. Instrument symbol incorrect")
        print("   3. Token expired")
        print("   4. Chart/bars endpoint not available in demo")
