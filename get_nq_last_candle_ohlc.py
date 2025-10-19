#!/usr/bin/env python3
"""
Get OHLC data for the last completed 30-minute candle for NQ
Uses Tradovate API with real authentication
"""
import os
import sys
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def calculate_last_candle_period():
    """
    Calculate the time range for the last completed 30-minute candle
    """
    now = datetime.now()
    
    # Round down to the nearest 30-minute mark
    if now.minute < 30:
        candle_end = now.replace(minute=0, second=0, microsecond=0)
        candle_start = (now.replace(minute=0, second=0, microsecond=0) - timedelta(minutes=30))
    else:
        candle_end = now.replace(minute=30, second=0, microsecond=0)
        candle_start = now.replace(minute=0, second=0, microsecond=0)
    
    return candle_start, candle_end

def get_accounts_with_tokens():
    """
    Get all accounts that have valid tokens in Redis
    """
    redis_client = get_redis_client()
    if not redis_client:
        return []
    
    accounts_to_try = [
        "PAAPEX2666680000001",
        "PAAPEX2666680000002",
        "PAAPEX2666680000003",
        "PAAPEX2666680000004",
        "PAAPEX2666680000005"
    ]
    
    valid_accounts = []
    for account in accounts_to_try:
        token = redis_client.get(f"token:{account}")
        if token:
            valid_accounts.append(account)
    
    return valid_accounts

def get_last_30min_candle_ohlc():
    """
    Get OHLC for the last completed 30-minute candle
    """
    print("="*70)
    print("📊 Last 30-Minute Candle OHLC for NQ")
    print("="*70)
    
    # Calculate candle period
    candle_start, candle_end = calculate_last_candle_period()
    print(f"\n📅 Last Completed 30-Min Candle:")
    print(f"   Start: {candle_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End:   {candle_end.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Connect to Redis
    print(f"\n1. Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Redis connection failed")
        return None
    print("✅ Redis connected")
    
    # Find account with token
    print(f"\n2. Finding valid Tradovate token...")
    accounts = get_accounts_with_tokens()
    if not accounts:
        print("❌ No valid tokens found")
        return None
    
    account_name = accounts[0]
    print(f"✅ Using account: {account_name}")
    
    # Initialize broker
    print(f"\n3. Initializing Tradovate broker...")
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
    
    # Get current quote (this gives us session data, not 30-min bars)
    print(f"\n4. Fetching real-time quote for MNQZ5...")
    instrument = "MNQZ5"
    
    try:
        quote_response = broker.get_price_quotes(symbol=instrument)
        
        if hasattr(quote_response, 's') and quote_response.s == 'ok':
            if hasattr(quote_response, 'd') and quote_response.d:
                quote_data = quote_response.d[0]['v']
                
                # Extract current data (this is session-level data)
                current_price = float(quote_data.get('lp', 0))
                open_price = float(quote_data.get('open_price', 0))
                high_price = float(quote_data.get('high_price', 0))
                low_price = float(quote_data.get('low_price', 0))
                volume = int(quote_data.get('volume', 0))
                
                print("✅ Quote received")
                
                # Note: Tradovate /quotes endpoint returns session data, not 30-min bars
                # For true 30-minute OHLC, we would need:
                # - Historical chart/bars endpoint
                # - Or tick data aggregation from Supabase
                
                print("\n" + "="*70)
                print("⚠️  NOTE: Tradovate /quotes endpoint limitation")
                print("="*70)
                print("The /quotes API returns SESSION-LEVEL data (entire trading day),")
                print("NOT 30-minute candle data.")
                print()
                print("To get true 30-minute OHLC candles, you need:")
                print("  1. Tradovate Chart/Bars API endpoint (may not be available)")
                print("  2. Tick data from Supabase aggregated into 30-min bars")
                print("  3. Third-party market data provider (TradingView, Polygon, etc.)")
                print("="*70)
                
                # Display session data as reference
                print("\n📊 Session Data (Today's Trading Session)")
                print("="*70)
                print(f"Symbol:          {instrument}")
                print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 70)
                print(f"Current Price:   ${current_price:,.2f}  ⭐")
                print(f"Session Open:    ${open_price:,.2f}")
                print(f"Session High:    ${high_price:,.2f}")
                print(f"Session Low:     ${low_price:,.2f}")
                print(f"Session Volume:  {volume:,} contracts")
                print("="*70)
                
                # Approximate last candle (using current price as close)
                print(f"\n📈 APPROXIMATED Last 30-Min Candle")
                print(f"   (Using current market data - NOT actual historical bars)")
                print("="*70)
                print(f"Period:      {candle_start.strftime('%H:%M')} - {candle_end.strftime('%H:%M')}")
                print("-" * 70)
                
                # Since we can't get true historical bars, we use current data
                # This is an approximation only
                candle = {
                    'start': candle_start,
                    'end': candle_end,
                    'open': open_price,  # Session open (not candle open)
                    'high': high_price,  # Session high (not candle high)
                    'low': low_price,    # Session low (not candle low)
                    'close': current_price,  # Current price (not candle close)
                    'volume': volume,
                    'is_approximate': True
                }
                
                print(f"Open:        ${candle['open']:,.2f}  (⚠️ session open)")
                print(f"High:        ${candle['high']:,.2f}  (⚠️ session high)")
                print(f"Low:         ${candle['low']:,.2f}  (⚠️ session low)")
                print(f"Close:       ${candle['close']:,.2f}  (⚠️ current price)")
                print(f"Volume:      {candle['volume']:,}  (⚠️ session volume)")
                print("="*70)
                
                print("\n⚠️  WARNING: This is NOT true 30-minute candle data!")
                print("   It's session-level data used as an approximation.")
                
                return candle
                
        else:
            print("❌ Failed to get quote")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def suggest_alternatives():
    """
    Suggest alternative methods to get true 30-minute OHLC data
    """
    print("\n" + "="*70)
    print("💡 Alternative Solutions for True 30-Min OHLC Data")
    print("="*70)
    
    print("\n1. Enable Supabase Tick Data Aggregation:")
    print("   - Query orca.nq_tick_data table")
    print("   - Aggregate ticks into 30-minute bars")
    print("   - Create SQL function for OHLC calculation")
    
    print("\n2. Use TradingView Charts API:")
    print("   - TradingView provides historical bars")
    print("   - Can specify timeframe (30 minutes)")
    print("   - May require separate authentication")
    
    print("\n3. Use Third-Party Data Provider:")
    print("   - Polygon.io (requires API key)")
    print("   - Alpha Vantage (free tier available)")
    print("   - IEX Cloud (real-time market data)")
    
    print("\n4. Store Historical Bars in Supabase:")
    print("   - Run periodic job to aggregate tick data")
    print("   - Store pre-calculated OHLC bars")
    print("   - Query for specific time periods")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    candle = get_last_30min_candle_ohlc()
    
    if candle:
        print(f"\n🎯 Last 30-Min Candle CLOSE (Approximate): ${candle['close']:,.2f}")
    
    suggest_alternatives()
