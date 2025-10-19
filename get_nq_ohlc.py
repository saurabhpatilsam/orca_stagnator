#!/usr/bin/env python3
"""
Fetch last 30 minutes of OHLC data for NQ from Tradovate API
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def get_nq_ohlc_30min():
    """
    Fetch last 30 minutes of OHLC data for NQ (MNQZ5)
    """
    print("="*70)
    print("Fetching 30-Minute OHLC Data for NQ")
    print("="*70)
    
    account_name = "PAAPEX1361890000010"
    instrument = "MNQZ5"
    
    print(f"\n1. Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Redis connection failed")
        return None
    print("✅ Redis connected")
    
    print(f"\n2. Initializing Tradovate broker...")
    broker = TradingViewTradovateBroker(
        redis_client=redis_client,
        account_name=account_name,
        base_url="https://tv-demo.tradovateapi.com"
    )
    print("✅ Broker initialized")
    
    print(f"\n3. Fetching current quote for {instrument}...")
    try:
        # Get current quote
        quote_response = broker.get_price_quotes(symbol=instrument)
        
        if hasattr(quote_response, 'd') and quote_response.d:
            quote_data = quote_response.d[0]['v']
            
            print(f"\n📊 Current Market Data for {instrument}:")
            print(f"   Last Price: ${quote_data.get('lp', 0):.2f}")
            print(f"   Bid: ${quote_data.get('bid', 0):.2f}")
            print(f"   Ask: ${quote_data.get('ask', 0):.2f}")
            print(f"   High: ${quote_data.get('high_price', 0):.2f}")
            print(f"   Low: ${quote_data.get('low_price', 0):.2f}")
            print(f"   Open: ${quote_data.get('open_price', 0):.2f}")
            print(f"   Volume: {quote_data.get('volume', 0):,}")
            
            # Calculate approximate OHLC for last 30 minutes
            # Note: Tradovate API quote endpoint gives session data, not 30-min bars
            print(f"\n⚠️  Note: Tradovate quote API returns session-level data")
            print(f"   For true 30-minute OHLC bars, you need:")
            print(f"   1. Historical bar API endpoint (if available)")
            print(f"   2. Or tick data from Supabase aggregated into bars")
            
            # Create a simple OHLC structure from current data
            current_time = datetime.now()
            ohlc_data = {
                'timestamp': current_time,
                'symbol': instrument,
                'open': quote_data.get('open_price', 0),
                'high': quote_data.get('high_price', 0),
                'low': quote_data.get('low_price', 0),
                'close': quote_data.get('lp', 0),
                'volume': quote_data.get('volume', 0)
            }
            
            return ohlc_data
        else:
            print("❌ No quote data available")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching quote: {e}")
        return None

def get_ohlc_from_supabase():
    """
    Alternative: Get OHLC data from Supabase tick data
    This aggregates tick data into 30-minute bars
    """
    print(f"\n4. Fetching OHLC from Supabase tick data...")
    print("   (Alternative method using stored tick data)")
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SELFHOSTED_SUPABASE_URL') or os.getenv('CLOUD_SUPABASE_URL')
        supabase_key = os.getenv('SELFHOSTED_SUPABASE_KEY') or os.getenv('CLOUD_SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("   ⚠️  Supabase credentials not found")
            return None
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Get tick data from last 30 minutes
        time_30min_ago = (datetime.now() - timedelta(minutes=30)).isoformat()
        
        schema = 'orca' if 'magicpitch' in supabase_url else 'public'
        table_name = f'{schema}.nq_tick_data' if schema == 'orca' else 'nq_tick_data'
        
        # Query tick data
        response = supabase.table(table_name).select('*').gte('time', time_30min_ago).order('time').execute()
        
        if response.data and len(response.data) > 0:
            df = pd.DataFrame(response.data)
            
            # Calculate OHLC
            ohlc = {
                'timestamp': datetime.now(),
                'symbol': 'MNQZ5',
                'open': df['last'].iloc[0],
                'high': df['last'].max(),
                'low': df['last'].min(),
                'close': df['last'].iloc[-1],
                'volume': df['volume'].sum(),
                'ticks': len(df)
            }
            
            print(f"\n📊 30-Minute OHLC from Supabase:")
            print(f"   Open: ${ohlc['open']:.2f}")
            print(f"   High: ${ohlc['high']:.2f}")
            print(f"   Low: ${ohlc['low']:.2f}")
            print(f"   Close: ${ohlc['close']:.2f}")
            print(f"   Volume: {ohlc['volume']:,}")
            print(f"   Ticks: {ohlc['ticks']:,}")
            
            return ohlc
        else:
            print("   ⚠️  No tick data found in last 30 minutes")
            return None
            
    except Exception as e:
        print(f"   ⚠️  Error accessing Supabase: {e}")
        return None

if __name__ == "__main__":
    # Try Method 2 first: Get OHLC from Supabase tick data (more reliable)
    print("\nAttempting to fetch OHLC from Supabase...")
    ohlc_data = get_ohlc_from_supabase()
    
    # Method 1: Get current quote (session data) - only if Supabase fails
    if not ohlc_data:
        print("\nFalling back to Tradovate API...")
        try:
            quote_data = get_nq_ohlc_30min()
        except Exception as e:
            print(f"❌ Tradovate API failed: {e}")
            print("\n💡 To use Tradovate API, refresh the token in Redis")
            print("   Run: python3 scripts/get_trading_token.py")
    
    print("\n" + "="*70)
    print("✅ Data fetch complete")
    print("="*70)
