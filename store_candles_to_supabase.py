#!/usr/bin/env python3
"""
Fetch candles using the working script and store in Supabase
"""
import sys
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Create fresh Supabase client (with defaults from orca_supabase.py)
SUPABASE_URL = os.getenv("SUPABASE_URL", default='https://dcoukhtfcloqpfmijock.supabase.co')
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or 'sb_secret__t3NV0SUY8ywb2y_44jRDA_JOcR--G_'

print(f"Using Supabase URL: {SUPABASE_URL}")
SUPABASE: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure to use orca schema
SUPABASE.postgrest.schema("orca")

# Import the working candle fetcher components
from get_nq_30min_working import (
    get_tradovate_tokens,
    discover_contract,
    SimpleTradovateWebSocket,
    TRADOVATE_USERNAMES
)

def fetch_candles(timeframe_minutes, num_bars=5):
    """
    Fetch candles for a specific timeframe
    """
    print(f"\n📊 Fetching {timeframe_minutes}-minute candles...")
    
    for account_name in TRADOVATE_USERNAMES:
        print(f"  🔍 Trying account: {account_name}")
        
        # Get tokens
        access_token, md_token = get_tradovate_tokens(account_name)
        if not access_token or not md_token:
            continue
        
        # Discover contract
        contract_symbol = discover_contract(access_token, "NQ")
        if not contract_symbol:
            continue
        
        print(f"  ✅ Using contract: {contract_symbol}")
        
        # Connect WebSocket
        ws_client = SimpleTradovateWebSocket(md_token)
        
        if not ws_client.connect():
            print(f"  ❌ WebSocket connection failed")
            continue
        
        # Request chart data
        bars = ws_client.request_chart_data(
            symbol=contract_symbol,
            bar_size_minutes=timeframe_minutes,
            starting_time=datetime.now(),
            num_bars=num_bars
        )
        
        ws_client.close()
        
        if bars and len(bars) > 0:
            print(f"  ✅ Fetched {len(bars)} bars")
            return bars, contract_symbol
        else:
            print(f"  ⚠️  No bars received")
    
    return None, None

def store_candles(timeframe_minutes, candles, symbol):
    """
    Store candles in Supabase using RPC functions
    """
    function_map = {
        5: "insert_nq_candles_5min",
        15: "insert_nq_candles_15min",
        30: "insert_nq_candles_30min",
        60: "insert_nq_candles_1hour"
    }
    
    function_name = function_map.get(timeframe_minutes)
    if not function_name:
        print(f"  ❌ Invalid timeframe: {timeframe_minutes}")
        return False
    
    print(f"  📥 Storing {len(candles)} candles using {function_name}...")
    
    success_count = 0
    error_count = 0
    
    # Insert each candle using RPC function
    for candle in candles:
        try:
            result = SUPABASE.rpc(function_name, {
                "p_symbol": symbol,
                "p_candle_time": candle["datetime"].isoformat(),
                "p_open": float(candle["open"]),
                "p_high": float(candle["high"]),
                "p_low": float(candle["low"]),
                "p_close": float(candle["close"]),
                "p_volume": int(candle.get("volume", 0)),
                "p_up_volume": int(candle.get("up_volume", 0)),
                "p_down_volume": int(candle.get("down_volume", 0)),
                "p_up_ticks": int(candle.get("up_ticks", 0)),
                "p_down_ticks": int(candle.get("down_ticks", 0))
            }).execute()
            success_count += 1
        except Exception as e:
            # Check if it's just a JSON parsing error but data was stored
            error_str = str(e)
            if '"success" : true' in error_str or 'Candle inserted/updated' in error_str:
                success_count += 1  # Data was stored successfully
            else:
                error_count += 1
                print(f"  ⚠️  Error inserting candle at {candle['datetime']}: {e}")
    
    if success_count > 0:
        print(f"  ✅ Successfully stored {success_count} candles")
    if error_count > 0:
        print(f"  ⚠️  Failed to store {error_count} candles")
    
    return success_count > 0

def verify_data(timeframe_minutes):
    """
    Verify data was stored correctly using RPC function
    """
    timeframe_map = {
        5: "5min",
        15: "15min",
        30: "30min",
        60: "1hour"
    }
    
    timeframe = timeframe_map.get(timeframe_minutes)
    
    print(f"\n🔍 Verifying data for {timeframe} candles...")
    
    try:
        result = SUPABASE.rpc("get_nq_candles", {
            "p_timeframe": timeframe,
            "p_limit": 5
        }).execute()
        
        if result.data and len(result.data) > 0:
            print(f"  ✅ Found {len(result.data)} candles in database:")
            for candle in result.data:
                dt = candle['candle_time']
                print(f"     {dt}: Open=${candle['open']:,.2f}, High=${candle['high']:,.2f}, Low=${candle['low']:,.2f}, Close=${candle['close']:,.2f}, Vol={candle['volume']:,}")
            return True
        else:
            print(f"  ⚠️  No data found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error querying data: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*70)
    print("🚀 Fetch and Store NQ Candles to Supabase")
    print("="*70)
    
    timeframes = [5, 15, 30, 60]
    timeframe_names = {
        5: "5-minute",
        15: "15-minute",
        30: "30-minute",
        60: "1-hour"
    }
    
    results = {}
    
    for timeframe in timeframes:
        print(f"\n{'='*70}")
        print(f"📈 {timeframe_names[timeframe].upper()} CANDLES")
        print(f"{'='*70}")
        
        # Fetch candles from Tradovate
        candles, symbol = fetch_candles(timeframe, num_bars=5)
        
        if not candles:
            print(f"  ❌ Failed to fetch {timeframe_names[timeframe]} candles")
            results[timeframe] = False
            continue
        
        # Store in Supabase
        success = store_candles(timeframe, candles, symbol)
        results[timeframe] = success
        
        # Verify
        if success:
            verify_data(timeframe)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 SUMMARY")
    print(f"{'='*70}")
    
    for timeframe in timeframes:
        status = "✅ SUCCESS" if results.get(timeframe) else "❌ FAILED"
        print(f"  {timeframe_names[timeframe]:12} : {status}")
    
    all_success = all(results.values())
    if all_success:
        print(f"\n{'='*70}")
        print("🎉 ALL CANDLES FETCHED AND STORED SUCCESSFULLY!")
        print(f"{'='*70}")
        print("\n✅ You can now query your candles from Supabase:")
        print("   SELECT * FROM orca.nq_candles_5min ORDER BY candle_time DESC LIMIT 5;")
        print("   SELECT * FROM orca.nq_candles_15min ORDER BY candle_time DESC LIMIT 5;")
        print("   SELECT * FROM orca.nq_candles_30min ORDER BY candle_time DESC LIMIT 5;")
        print("   SELECT * FROM orca.nq_candles_1hour ORDER BY candle_time DESC LIMIT 5;")
    else:
        print(f"\n{'='*70}")
        print("⚠️  SOME OPERATIONS FAILED")
        print(f"{'='*70}")
    
    print()

if __name__ == "__main__":
    main()
