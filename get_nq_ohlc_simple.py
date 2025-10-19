#!/usr/bin/env python3
"""
Fetch last 30 minutes of OHLC data for NQ from Supabase tick data
Simple version using direct SQL query
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def get_nq_ohlc_30min():
    """
    Fetch last 30 minutes of OHLC data for NQ from Supabase
    """
    print("="*70)
    print("📊 Fetching 30-Minute OHLC Data for NQ")
    print("="*70)
    
    # Configuration
    supabase_url = os.getenv('SELFHOSTED_SUPABASE_URL')
    supabase_key = os.getenv('SELFHOSTED_SUPABASE_KEY')
    schema = os.getenv('SELFHOSTED_SCHEMA', 'orca')
    
    if not supabase_url or not supabase_key:
        print("\n❌ Supabase credentials not found in .env")
        print("   Required: SELFHOSTED_SUPABASE_URL, SELFHOSTED_SUPABASE_KEY")
        return None
    
    print(f"\n1. Connecting to Supabase...")
    print(f"   URL: {supabase_url}")
    print(f"   Schema: {schema}")
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None
    
    # Calculate time range (last 30 minutes)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    print(f"\n2. Fetching tick data...")
    print(f"   Time Range: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
    print(f"   Date: {start_time.strftime('%Y-%m-%d')}")
    
    try:
        # Query tick data from last 30 minutes
        table_name = f"{schema}.nq_tick_data" if schema else "nq_tick_data"
        
        response = supabase.table(table_name)\
            .select('time, last, volume')\
            .gte('time', start_time.isoformat())\
            .lte('time', end_time.isoformat())\
            .order('time')\
            .execute()
        
        if not response.data or len(response.data) == 0:
            print(f"\n⚠️  No tick data found in last 30 minutes")
            print(f"   Trying to get today's data...")
            
            # Try getting any data from today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            response = supabase.table(table_name)\
                .select('time, last, volume')\
                .gte('time', today_start.isoformat())\
                .order('time', desc=True)\
                .limit(1000)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                print(f"❌ No data available for today")
                return None
            
            print(f"✅ Found {len(response.data)} ticks from today")
        else:
            print(f"✅ Found {len(response.data)} ticks in last 30 minutes")
        
        # Convert to DataFrame
        df = pd.DataFrame(response.data)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Calculate OHLC
        ohlc = {
            'symbol': 'MNQZ5',
            'start_time': df['time'].iloc[0],
            'end_time': df['time'].iloc[-1],
            'open': float(df['last'].iloc[0]),
            'high': float(df['last'].max()),
            'low': float(df['last'].min()),
            'close': float(df['last'].iloc[-1]),
            'volume': int(df['volume'].sum()),
            'ticks': len(df)
        }
        
        # Print results
        print(f"\n📊 OHLC Data for NQ (Last 30 Minutes)")
        print("="*70)
        print(f"Symbol:      {ohlc['symbol']}")
        print(f"Period:      {ohlc['start_time'].strftime('%Y-%m-%d %H:%M:%S')} to")
        print(f"             {ohlc['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"-" * 70)
        print(f"Open:        ${ohlc['open']:,.2f}")
        print(f"High:        ${ohlc['high']:,.2f}")
        print(f"Low:         ${ohlc['low']:,.2f}")
        print(f"Close:       ${ohlc['close']:,.2f}")
        print(f"-" * 70)
        print(f"Change:      ${ohlc['close'] - ohlc['open']:+,.2f}  ({((ohlc['close'] - ohlc['open']) / ohlc['open'] * 100):+.2f}%)")
        print(f"Range:       ${ohlc['high'] - ohlc['low']:,.2f}  ({ohlc['low']:,.2f} - {ohlc['high']:,.2f})")
        print(f"-" * 70)
        print(f"Volume:      {ohlc['volume']:,} contracts")
        print(f"Ticks:       {ohlc['ticks']:,} data points")
        print("="*70)
        
        return ohlc
        
    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    ohlc_data = get_nq_ohlc_30min()
    
    if ohlc_data:
        print("\n✅ Successfully fetched OHLC data!")
    else:
        print("\n❌ Failed to fetch OHLC data")
        print("\n💡 Troubleshooting:")
        print("   1. Check .env file has SELFHOSTED_SUPABASE_URL and SELFHOSTED_SUPABASE_KEY")
        print("   2. Verify tick data exists in Supabase")
        print("   3. Check if data was uploaded for today")
