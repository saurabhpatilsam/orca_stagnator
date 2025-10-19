#!/usr/bin/env python3
"""
Get 30-minute OHLC candle data from Tradovate using WebSocket
Standalone implementation based on tradovate_data/api.py and tradovatesocket.py
"""
import sys
import os
import json
import time
import random
import websocket
import threading
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client

# Configuration
TRADOVATE_USERNAMES = ["APEX_266668", "APEX_265995", "APEX_272045", "APEX_136189"]
REST_BASE_URL = "https://demo.tradovateapi.com/v1"
WS_URL = "wss://md-demo.tradovateapi.com/v1/websocket"

class SimpleTradovateWebSocket:
    """Simplified WebSocket client for Tradovate chart data"""
    
    def __init__(self, md_token):
        self.md_token = md_token
        self.ws = None
        self.authorized = False
        self.request_id = 1
        self.chart_data = {}
        self.chart_events = {}
        
    def connect(self):
        """Connect and authorize WebSocket"""
        print("   Connecting to WebSocket...")
        
        def on_open(ws):
            print("   ✅ WebSocket opened")
            # Authorize
            auth_msg = f"authorize\n{self.request_id}\n\n{self.md_token}"
            ws.send(auth_msg)
            self.request_id += 1
            
        def on_message(ws, message):
            if message == "h":
                ws.send("[]")  # Heartbeat response
                return
            elif message == "o":
                return
            elif message.startswith("a["):
                data = json.loads(message[2:-1])
                
                # Check authorization
                if data.get("s") == 200 and not self.authorized:
                    self.authorized = True
                    print("   ✅ WebSocket authorized")
                
                # Check for chart data
                elif data.get("e") == "chart":
                    self._process_chart_data(data.get("d", {}))
        
        def on_error(ws, error):
            print(f"   ❌ WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print(f"   WebSocket closed")
        
        self.ws = websocket.WebSocketApp(
            WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in thread with SSL verification disabled
        import ssl
        ws_thread = threading.Thread(
            target=lambda: self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}),
            daemon=True
        )
        ws_thread.start()
        
        # Wait for authorization
        timeout = 10
        start = time.time()
        while not self.authorized and (time.time() - start) < timeout:
            time.sleep(0.1)
        
        return self.authorized
    
    def request_chart_data(self, symbol, bar_size_minutes, starting_time, num_bars):
        """Request historical chart data"""
        if not self.authorized:
            print("   ❌ Not authorized")
            return None
        
        # Prepare request
        closest_time = (starting_time + timedelta(minutes=bar_size_minutes)).isoformat()
        if not closest_time.endswith("Z"):
            closest_time += "Z"
        
        request_body = {
            "symbol": symbol,
            "chartDescription": {
                "underlyingType": "MinuteBar",
                "elementSize": bar_size_minutes,
                "elementSizeUnit": "UnderlyingUnits"
            },
            "timeRange": {
                "closestTimestamp": closest_time,
                "asMuchAsElements": num_bars + 1
            }
        }
        
        req_id = self.request_id
        self.chart_data[req_id] = {"bars": [], "complete": False}
        self.chart_events[req_id] = threading.Event()
        
        # Send request
        message = f"md/getChart\n{req_id}\n\n{json.dumps(request_body)}"
        self.ws.send(message)
        self.request_id += 1
        
        print(f"   📊 Requested chart data (request #{req_id})")
        
        # Wait for data
        if self.chart_events[req_id].wait(timeout=30):
            return self.chart_data[req_id]["bars"]
        else:
            print("   ⚠️  Timeout waiting for chart data")
            return None
    
    def _process_chart_data(self, data):
        """Process incoming chart data"""
        for chart in data.get("charts", []):
            # Check for end of data
            if chart.get("eoh", False):
                for req_id, chart_data in self.chart_data.items():
                    if not chart_data["complete"]:
                        chart_data["complete"] = True
                        self.chart_events[req_id].set()
                        break
                continue
            
            # Process bars
            bars = chart.get("bars", [])
            if bars:
                for req_id, chart_data in self.chart_data.items():
                    if not chart_data["complete"]:
                        for bar in bars[:-1]:  # Exclude last incomplete bar
                            processed_bar = {
                                "timestamp": bar["timestamp"],
                                "datetime": datetime.fromisoformat(bar["timestamp"].replace("Z", "+00:00")),
                                "open": bar["open"],
                                "high": bar["high"],
                                "low": bar["low"],
                                "close": bar["close"],
                                "volume": bar.get("upVolume", 0) + bar.get("downVolume", 0)
                            }
                            chart_data["bars"].append(processed_bar)
                        break
    
    def close(self):
        """Close WebSocket"""
        if self.ws:
            self.ws.close()

def get_tradovate_tokens(account_name):
    """Get tokens from Redis and renew them"""
    print(f"\n1. Getting tokens for {account_name}...")
    
    # Get TV token from Redis
    redis_client = get_redis_client()
    if not redis_client:
        print("   ❌ Redis connection failed")
        return None, None
    
    tv_token = redis_client.get(f"token:{account_name}")
    if not tv_token:
        print(f"   ❌ No token found for {account_name}")
        return None, None
    
    print("   ✅ TV token retrieved from Redis")
    
    # Renew tokens to get MD token
    print("\n2. Renewing tokens to get MD access token...")
    import requests
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {tv_token}"
    }
    
    try:
        response = requests.get(f"{REST_BASE_URL}/auth/renewaccesstoken", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        md_token = data.get("mdAccessToken")
        access_token = data.get("accessToken")
        
        print("   ✅ MD access token obtained")
        return access_token, md_token
    
    except Exception as e:
        print(f"   ❌ Token renewal failed: {e}")
        return None, None

def discover_contract(access_token, symbol_prefix):
    """Discover current front-month contract"""
    print(f"\n3. Discovering current {symbol_prefix} contract...")
    
    import requests
    
    url = f"{REST_BASE_URL}/contract/suggest?t={symbol_prefix}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        contracts = response.json()
        
        if contracts:
            contract = contracts[0]
            contract_name = contract.get("name")
            print(f"   ✅ Using contract: {contract_name}")
            return contract_name
        else:
            print("   ❌ No contracts found")
            return None
    
    except Exception as e:
        print(f"   ❌ Contract discovery failed: {e}")
        return None

def get_30min_candles(symbol="NQ", num_bars=5):
    """Main function to get 30-minute candles"""
    print("="*70)
    print("📊 Fetching 30-Min Candles from Tradovate WebSocket")
    print("="*70)
    
    # Try different accounts
    for account_name in TRADOVATE_USERNAMES:
        print(f"\n🔍 Trying account: {account_name}")
        
        # Get tokens
        access_token, md_token = get_tradovate_tokens(account_name)
        if not access_token or not md_token:
            continue
        
        # Discover contract
        contract_symbol = discover_contract(access_token, symbol)
        if not contract_symbol:
            continue
        
        # Connect WebSocket
        print(f"\n4. Connecting to WebSocket...")
        ws_client = SimpleTradovateWebSocket(md_token)
        
        if not ws_client.connect():
            print("   ❌ WebSocket connection failed")
            continue
        
        # Request chart data
        print(f"\n5. Requesting {num_bars} x 30-minute bars...")
        # Get most recent data - use current time to get latest bars
        # The API returns bars BEFORE the specified timestamp
        starting_time = datetime.now()
        
        bars = ws_client.request_chart_data(
            symbol=contract_symbol,
            bar_size_minutes=30,
            starting_time=starting_time,
            num_bars=num_bars
        )
        
        ws_client.close()
        
        if bars:
            # Display results
            print(f"\n✅ Received {len(bars)} bars!")
            print("\n" + "="*70)
            print(f"📈 30-Minute OHLC Candles for {symbol} ({contract_symbol})")
            print("="*70)
            
            for i, bar in enumerate(bars, 1):
                dt = bar['datetime']
                change = bar['close'] - bar['open']
                change_pct = (change / bar['open'] * 100) if bar['open'] > 0 else 0
                
                print(f"\n📊 Candle #{i}")
                print(f"Time:    {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Open:    ${bar['open']:,.2f}")
                print(f"High:    ${bar['high']:,.2f}")
                print(f"Low:     ${bar['low']:,.2f}")
                print(f"Close:   ${bar['close']:,.2f}  ({change:+.2f}, {change_pct:+.2f}%)")
                print(f"Volume:  {bar['volume']:,}")
            
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
                print(f"Volume:  {last['volume']:,}")
                print("="*70)
            
            return bars
        else:
            print("   ⚠️  No bars received, trying next account...")
    
    print("\n❌ Failed to get data from any account")
    return None

if __name__ == "__main__":
    print("\n🚀 Starting Tradovate WebSocket Chart Data Test\n")
    print(f"Current time: 17:58 (Last completed candle should be 17:30)\n")
    
    # Request enough bars to get the most recent completed candle
    bars = get_30min_candles(symbol="NQ", num_bars=25)
    
    if bars:
        print(f"\n✅ Success! Fetched {len(bars)} bars")
        last_close = bars[-1]['close']
        print(f"\n🎯 ANSWER: Last 30-min candle CLOSE = ${last_close:,.2f}")
    else:
        print("\n❌ Failed to fetch candle data")
    
    print("\n" + "="*70)
    print("✅ Test Complete")
    print("="*70)
