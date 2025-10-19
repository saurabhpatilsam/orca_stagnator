#!/usr/bin/env python3
"""
Get the close price of the previous 30-minute candle for NQ
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_30min_candle_close():
    """
    Fetch the close price of the previous 30-minute candle
    """
    print("="*70)
    print("📊 Fetching Previous 30-Minute Candle Close for NQ")
    print("="*70)
    
    # Try Cloud Supabase first (uses public schema)
    cloud_url = os.getenv('CLOUD_SUPABASE_URL')
    cloud_key = os.getenv('CLOUD_SUPABASE_KEY')
    
    selfhosted_url = os.getenv('SELFHOSTED_SUPABASE_URL')
    selfhosted_key = os.getenv('SELFHOSTED_SUPABASE_KEY')
    
    # Try cloud first, then self-hosted
    configs = [
        ("Cloud", cloud_url, cloud_key, "public"),
        ("Self-Hosted", selfhosted_url, selfhosted_key, "public")
    ]
    
    for config_name, url, key, schema in configs:
        if not url or not key:
            continue
            
        print(f"\n🔍 Trying {config_name} Supabase...")
        print(f"   URL: {url}")
        
        result = fetch_candle_from_supabase(url, key, schema)
        if result:
            return result
    
    print("\n❌ Could not fetch data from any Supabase instance")
    print("\n💡 Alternative: Use mock data for testing")
    return create_mock_candle()

def fetch_candle_from_supabase(supabase_url, supabase_key, schema):
    """
    Fetch 30-minute candle data from Supabase
    """
    try:
        # Calculate the previous 30-minute candle time range
        now = datetime.now()
        
        # Round down to the previous 30-minute mark
        if now.minute < 30:
            candle_end = now.replace(minute=0, second=0, microsecond=0)
        else:
            candle_end = now.replace(minute=30, second=0, microsecond=0)
        
        candle_start = candle_end - timedelta(minutes=30)
        
        print(f"   Candle Period: {candle_start.strftime('%H:%M')} - {candle_end.strftime('%H:%M')}")
        
        # Construct API request
        table_name = "nq_tick_data"
        api_url = f"{supabase_url}/rest/v1/{table_name}"
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Get all ticks in the candle period
        params = {
            "select": "time,last,volume",
            "time": f"gte.{candle_start.isoformat()},lte.{candle_end.isoformat()}",
            "order": "time.asc",
            "limit": "10000"
        }
        
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                # Extract OHLC from ticks
                prices = [float(tick['last']) for tick in data]
                volumes = [int(tick['volume']) for tick in data]
                
                candle = {
                    'start_time': candle_start,
                    'end_time': candle_end,
                    'open': prices[0],
                    'high': max(prices),
                    'low': min(prices),
                    'close': prices[-1],  # Last tick is the close
                    'volume': sum(volumes),
                    'ticks': len(data)
                }
                
                print(f"   ✅ Found {len(data)} ticks")
                print_candle_data(candle)
                return candle
            else:
                print(f"   ⚠️  No data in this time range")
                
        else:
            print(f"   ❌ API Error: {response.status_code}")
            if response.status_code == 404:
                print(f"      Table not found in {schema} schema")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None

def create_mock_candle():
    """
    Create mock candle data for testing
    """
    now = datetime.now()
    
    # Previous 30-minute candle
    if now.minute < 30:
        candle_end = now.replace(minute=0, second=0, microsecond=0)
    else:
        candle_end = now.replace(minute=30, second=0, microsecond=0)
    
    candle_start = candle_end - timedelta(minutes=30)
    
    # Mock NQ prices (typical intraday movement)
    mock_candle = {
        'start_time': candle_start,
        'end_time': candle_end,
        'open': 24758.75,
        'high': 24802.50,
        'low': 24723.25,
        'close': 24789.00,
        'volume': 15234,
        'ticks': 0,
        'is_mock': True
    }
    
    print("\n⚠️  Using MOCK DATA (no database connection)")
    print_candle_data(mock_candle)
    return mock_candle

def print_candle_data(candle):
    """
    Print formatted candle data
    """
    change = candle['close'] - candle['open']
    change_pct = (change / candle['open'] * 100)
    
    print("\n" + "="*70)
    print("📊 Previous 30-Minute Candle for NQ (MNQZ5)")
    print("="*70)
    print(f"Period:      {candle['start_time'].strftime('%Y-%m-%d %H:%M')} - {candle['end_time'].strftime('%H:%M')}")
    print("-" * 70)
    print(f"Open:        ${candle['open']:,.2f}")
    print(f"High:        ${candle['high']:,.2f}")
    print(f"Low:         ${candle['low']:,.2f}")
    print(f"Close:       ${candle['close']:,.2f}  ⭐ CLOSE PRICE")
    print("-" * 70)
    print(f"Change:      ${change:+,.2f}  ({change_pct:+.2f}%)")
    print(f"Range:       ${candle['high'] - candle['low']:,.2f}")
    print(f"Volume:      {candle['volume']:,} contracts")
    
    if candle['ticks'] > 0:
        print(f"Ticks:       {candle['ticks']:,} data points")
    
    if candle.get('is_mock'):
        print("\n⚠️  NOTE: This is MOCK data - not real market data")
    
    print("="*70)
    
    # Show just the close price prominently
    print(f"\n🎯 ANSWER: Previous 30-min candle CLOSE = ${candle['close']:,.2f}")
    print()

if __name__ == "__main__":
    candle = get_30min_candle_close()
