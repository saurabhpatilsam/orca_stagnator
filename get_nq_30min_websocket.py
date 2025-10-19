#!/usr/bin/env python3
"""
Get 30-minute OHLC candle data from Tradovate using WebSocket
Based on working implementation in tradovate_data/api.py
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from datetime import datetime, timedelta
from tradovate_data.api import TradovateAuth

def get_30min_candles_websocket(symbol="NQ", num_bars=5):
    """
    Get 30-minute OHLC candles using Tradovate WebSocket API
    
    Args:
        symbol: Instrument symbol prefix (NQ, ES)
        num_bars: Number of 30-minute bars to fetch
    
    Returns:
        List of OHLC candles
    """
    print("="*70)
    print("📊 Fetching 30-Min Candles via Tradovate WebSocket")
    print("="*70)
    
    try:
        # Initialize Tradovate Auth (connects WebSocket automatically)
        print("\n1. Initializing Tradovate WebSocket connection...")
        print("   This will:")
        print("   - Get token from Redis")
        print("   - Connect to WebSocket")
        print("   - Authorize")
        print("   - Discover current contract")
        
        auth_client = TradovateAuth(instruments=[symbol])
        
        # Wait for socket to be ready
        print("\n2. Waiting for WebSocket authorization...")
        timeout = 15
        start_time = time.time()
        while not auth_client.socket_connect and (time.time() - start_time) < timeout:
            time.sleep(0.5)
        
        if not auth_client.socket_connect:
            print("❌ WebSocket not authorized within timeout")
            return None
        
        print("✅ WebSocket connected and authorized!")
        
        # Get discovered contract
        if not auth_client.contracts:
            print("❌ No contracts discovered")
            return None
        
        contract = auth_client.contracts[0]
        contract_symbol = contract["name"]
        print(f"\n3. Using contract: {contract_symbol}")
        
        # Calculate starting time for bars
        # Get data starting from a few hours ago
        starting_time = datetime.now() - timedelta(hours=3)
        
        print(f"\n4. Requesting {num_bars} x 30-minute bars...")
        print(f"   Symbol: {contract_symbol}")
        print(f"   Bar Size: 30 minutes")
        print(f"   Starting: {starting_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Number of bars: {num_bars}")
        
        # Get bars using WebSocket
        bars = auth_client.get_bars(
            symbol=contract_symbol,
            bar_size_minutes=30,
            starting_time=starting_time,
            number_of_bars=num_bars,
            timeout=30
        )
        
        if not bars:
            print("\n❌ No bars received")
            print("\n💡 Possible reasons:")
            print("   1. Market is closed")
            print("   2. No data for requested time period")
            print("   3. Starting time too far in past")
            return None
        
        # Display results
        print(f"\n✅ Received {len(bars)} bars!")
        print("\n" + "="*70)
        print(f"📈 30-Minute OHLC Candles for {symbol} ({contract_symbol})")
        print("="*70)
        
        for i, bar in enumerate(bars, 1):
            dt = bar['datetime']
            open_price = bar['open']
            high_price = bar['high']
            low_price = bar['low']
            close_price = bar['close']
            
            change = close_price - open_price
            change_pct = (change / open_price * 100) if open_price > 0 else 0
            
            print(f"\n📊 Candle #{i}")
            print(f"Time:    {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Open:    ${open_price:,.2f}")
            print(f"High:    ${high_price:,.2f}")
            print(f"Low:     ${low_price:,.2f}")
            print(f"Close:   ${close_price:,.2f}  ({change:+.2f}, {change_pct:+.2f}%)")
            print(f"Up Vol:  {bar['volume']['up']:,}")
            print(f"Dn Vol:  {bar['volume']['down']:,}")
        
        # Highlight last candle
        if bars:
            last = bars[-1]
            print("\n" + "="*70)
            print("🎯 LAST 30-MIN CANDLE")
            print("="*70)
            print(f"Time:    {last['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Open:    ${last['open']:,.2f}")
            print(f"High:    ${last['high']:,.2f}")
            print(f"Low:     ${last['low']:,.2f}")
            print(f"Close:   ${last['close']:,.2f}  ⭐")
            print("="*70)
        
        # Cleanup
        print("\n5. Cleaning up...")
        auth_client.stop_token_renewal_scheduler()
        if auth_client.socket:
            auth_client.socket.stop()
        
        return bars
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("\n🚀 Starting Tradovate WebSocket Chart Data Test\n")
    
    # Fetch NQ 30-minute candles
    bars = get_30min_candles_websocket(symbol="NQ", num_bars=5)
    
    if bars:
        print(f"\n✅ Successfully fetched {len(bars)} bars!")
        last_close = bars[-1]['close']
        print(f"\n🎯 Answer: Last 30-min candle CLOSE = ${last_close:,.2f}")
    else:
        print("\n❌ Failed to fetch candle data")
    
    print("\n" + "="*70)
    print("✅ Test Complete")
    print("="*70)
