#!/usr/bin/env python3
"""
Fetch last 30 minutes of OHLC data for NQ from Supabase
Uses direct HTTP requests to bypass library version issues
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_nq_ohlc_30min():
    """
    Fetch last 30 minutes of OHLC data for NQ using Supabase REST API
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
    
    # Calculate time range (last 30 minutes)
    end_time = datetime.now()
    start_time = end_time - timedelta(minutes=30)
    
    print(f"\n2. Fetching tick data...")
    print(f"   Time Range: {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
    print(f"   Date: {start_time.strftime('%Y-%m-%d')}")
    
    try:
        # Construct REST API URL - try public schema first
        table_name = "nq_tick_data"
        api_url = f"{supabase_url}/rest/v1/{table_name}"
        
        # Headers for Supabase REST API
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Query parameters
        params = {
            "select": "time,last,volume",
            "time": f"gte.{start_time.isoformat()}",
            "time": f"lte.{end_time.isoformat()}",
            "order": "time.asc"
        }
        
        # Make the request
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        data = response.json()
        
        if not data or len(data) == 0:
            print(f"\n⚠️  No tick data found in last 30 minutes")
            print(f"   Trying to get today's data...")
            
            # Try getting any data from today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            params = {
                "select": "time,last,volume",
                "time": f"gte.{today_start.isoformat()}",
                "order": "time.desc",
                "limit": "1000"
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            data = response.json()
            
            if not data or len(data) == 0:
                print(f"❌ No data available for today")
                return None
            
            print(f"✅ Found {len(data)} ticks from today (most recent)")
        else:
            print(f"✅ Found {len(data)} ticks in last 30 minutes")
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
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
        
        # Calculate metrics
        change = ohlc['close'] - ohlc['open']
        change_pct = (change / ohlc['open'] * 100)
        range_size = ohlc['high'] - ohlc['low']
        
        # Print results
        print(f"\n📊 OHLC Data for NQ")
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
        print(f"Change:      ${change:+,.2f}  ({change_pct:+.2f}%)")
        print(f"Range:       ${range_size:,.2f}  ({ohlc['low']:,.2f} - {ohlc['high']:,.2f})")
        print(f"-" * 70)
        print(f"Volume:      {ohlc['volume']:,} contracts")
        print(f"Ticks:       {ohlc['ticks']:,} data points")
        print("="*70)
        
        # Also create a simple OHLC bar visualization
        bar_width = 50
        price_range = ohlc['high'] - ohlc['low']
        if price_range > 0:
            open_pos = int((ohlc['open'] - ohlc['low']) / price_range * bar_width)
            close_pos = int((ohlc['close'] - ohlc['low']) / price_range * bar_width)
            
            print(f"\n📈 Price Bar:")
            bar = [' '] * (bar_width + 1)
            bar[0] = '├'
            bar[bar_width] = '┤'
            bar[open_pos] = 'O'
            bar[close_pos] = 'C'
            
            print(f"   Low ${ohlc['low']:,.2f}  {''.join(bar)}  High ${ohlc['high']:,.2f}")
            print(f"                   O=Open, C=Close")
        
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
