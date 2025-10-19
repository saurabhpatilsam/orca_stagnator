#!/usr/bin/env python3
"""
Get real-time NQ price data from Tradovate API
Uses existing broker implementation with Redis token authentication
"""
import os
import sys
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def check_redis_token():
    """
    Check if valid token exists in Redis
    """
    print("="*70)
    print("🔐 Checking Tradovate Authentication")
    print("="*70)
    
    # Try multiple accounts that may have tokens
    accounts_to_try = [
        "PAAPEX2666680000001",
        "PAAPEX2666680000002",
        "PAAPEX2666680000003",
        "PAAPEX1361890000010"
    ]
    
    print(f"\n1. Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Redis connection failed")
        return None, None
    print("✅ Redis connected")
    
    print(f"\n2. Checking for Tradovate tokens...")
    
    # Try each account
    for account_name in accounts_to_try:
        try:
            token = redis_client.get(f"token:{account_name}")
            if token:
                print(f"✅ Token found for account: {account_name}")
                print(f"   Token length: {len(token)} characters")
                return redis_client, account_name
            else:
                print(f"   ⚠️  No token for {account_name}")
        except Exception as e:
            print(f"   ❌ Error checking {account_name}: {e}")
    
    print(f"\n❌ No valid tokens found in Redis")
    print(f"\n💡 To authenticate with Tradovate:")
    print(f"   1. Run: python3 scripts/get_trading_token.py")
    print(f"   2. Or: python3 scripts/get_trading_token_final.py")
    return None, None

def get_nq_realtime_price(redis_client, account_name):
    """
    Fetch real-time NQ price from Tradovate API
    """
    print("\n" + "="*70)
    print("📊 Fetching Real-Time NQ Price from Tradovate")
    print("="*70)
    
    instrument = "MNQZ5"  # Micro E-mini Nasdaq-100 December 2025
    
    print(f"\n3. Initializing Tradovate broker...")
    print(f"   Environment: Demo")
    print(f"   Base URL: https://tv-demo.tradovateapi.com")
    
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        print("✅ Broker initialized")
        
        print(f"\n4. Fetching real-time quote for {instrument}...")
        print(f"   Endpoint: GET /quotes?locale=en&symbols={instrument}")
        
        # Use the broker's get_price_quotes method
        quote_response = broker.get_price_quotes(symbol=instrument)
        
        if hasattr(quote_response, 's') and quote_response.s == 'ok':
            if hasattr(quote_response, 'd') and quote_response.d:
                quote_data = quote_response.d[0]['v']
                
                # Extract price data
                last_price = float(quote_data.get('lp', 0))
                bid = float(quote_data.get('bid', 0))
                ask = float(quote_data.get('ask', 0))
                high = float(quote_data.get('high_price', 0))
                low = float(quote_data.get('low_price', 0))
                open_price = float(quote_data.get('open_price', 0))
                volume = int(quote_data.get('volume', 0))
                
                # Calculate metrics
                change = last_price - open_price
                change_pct = (change / open_price * 100) if open_price > 0 else 0
                spread = ask - bid
                range_size = high - low
                
                # Print results
                print("\n✅ Quote received successfully!")
                print("\n" + "="*70)
                print(f"📈 REAL-TIME NQ PRICE DATA (Tradovate Live)")
                print("="*70)
                print(f"Symbol:          {instrument}")
                print(f"Timestamp:       {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Source:          Tradovate Demo API")
                print("-" * 70)
                print(f"Last Price:      ${last_price:,.2f}  ⭐")
                print(f"Bid:             ${bid:,.2f}")
                print(f"Ask:             ${ask:,.2f}")
                print(f"Spread:          ${spread:.2f}")
                print("-" * 70)
                print(f"Open:            ${open_price:,.2f}")
                print(f"High:            ${high:,.2f}")
                print(f"Low:             ${low:,.2f}")
                print("-" * 70)
                print(f"Change:          ${change:+,.2f}  ({change_pct:+.2f}%)")
                print(f"Day Range:       ${range_size:,.2f}  ({low:,.2f} - {high:,.2f})")
                print(f"Volume:          {volume:,} contracts")
                print("="*70)
                
                print(f"\n🎯 ANSWER: Current NQ Price = ${last_price:,.2f}")
                
                return {
                    'symbol': instrument,
                    'timestamp': datetime.now(),
                    'last_price': last_price,
                    'bid': bid,
                    'ask': ask,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'volume': volume,
                    'change': change,
                    'change_pct': change_pct,
                    'source': 'Tradovate Demo API'
                }
            else:
                print("❌ No quote data in response")
                return None
        else:
            error_msg = quote_response.errmsg if hasattr(quote_response, 'errmsg') else 'Unknown error'
            print(f"❌ API returned error: {error_msg}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error fetching price: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Main execution flow
    """
    # Step 1: Check authentication
    redis_client, account_name = check_redis_token()
    
    if not redis_client or not account_name:
        print("\n" + "="*70)
        print("❌ Cannot proceed without valid authentication")
        print("="*70)
        print("\n📝 Steps to authenticate:")
        print("   1. Go to scripts/ folder")
        print("   2. Run: python3 get_trading_token.py")
        print("   3. Follow the authentication flow")
        print("   4. Token will be stored in Redis")
        print("   5. Run this script again")
        return None
    
    # Step 2: Fetch real-time price
    price_data = get_nq_realtime_price(redis_client, account_name)
    
    if price_data:
        print("\n✅ Successfully fetched real-time NQ price data!")
    else:
        print("\n❌ Failed to fetch price data")
        print("\n💡 Troubleshooting:")
        print("   1. Token may have expired - refresh it")
        print("   2. Tradovate API may be down")
        print("   3. Check internet connection")
    
    return price_data

if __name__ == "__main__":
    main()
