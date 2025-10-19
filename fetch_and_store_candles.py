#!/usr/bin/env python3
"""
Fetch 5 candles for each timeframe and store in Supabase
Then verify the data was stored correctly
"""
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_supabase.orca_supabase import SUPABASE
from get_nq_30min_working import get_30min_candles

def get_candles_from_tradovate(timeframe_minutes, num_bars=5):
    """
    Fetch candles from Tradovate using the working WebSocket implementation
    """
    print(f"\n📊 Fetching {timeframe_minutes}-minute candles...")
    
    # Import the necessary modules
    from app.services.orca_redis.client import get_redis_client
    import requests
    import websocket
    import threading
    import json
    import time
    import ssl
    
    TRADOVATE_USERNAMES = ["APEX_266668", "APEX_265995", "APEX_272045", "APEX_136189"]
    REST_BASE_URL = "https://demo.tradovateapi.com/v1"
    WS_URL = "wss://md-demo.tradovateapi.com/v1/websocket"
    
    # Try each account
    for account_name in TRADOVATE_USERNAMES:
        try:
            print(f"  Trying account: {account_name}")
            
            # Get tokens
            redis_client = get_redis_client()
            tv_token = redis_client.get(f"token:{account_name}")
            
            if not tv_token:
                continue
            
            # Renew tokens
            headers = {"Accept": "application/json", "Authorization": f"Bearer {tv_token}"}
            response = requests.get(f"{REST_BASE_URL}/auth/renewaccesstoken", headers=headers)
            data = response.json()
            md_token = data.get("mdAccessToken")
            access_token = data.get("accessToken")
            
            if not md_token or not access_token:
                continue
            
            # Discover contract
            url = f"{REST_BASE_URL}/contract/suggest?t=NQ"
            headers = {"Authorization": f"Bearer {access_token}"}
            response = requests.get(url, headers=headers)
            contracts = response.json()
            contract_symbol = contracts[0].get("name")
            
            print(f"  Using contract: {contract_symbol}")
            
            # Connect WebSocket
            ws_data = {"authorized": False, "bars": [], "complete": False}
            
            def on_open(ws):
                auth_msg = f"authorize\n1\n\n{md_token}"
                ws.send(auth_msg)
            
            def on_message(ws, message):
                if message == "o":
                    return
                elif message.startswith("a["):
                    data = json.loads(message[2:-1])
                    
                    if data.get("s") == 200 and not ws_data["authorized"]:
                        ws_data["authorized"] = True
                        
                        # Request chart data
                        closest_time = datetime.now().isoformat() + "Z"
                        request_body = {
                            "symbol": contract_symbol,
                            "chartDescription": {
                                "underlyingType": "MinuteBar",
                                "elementSize": timeframe_minutes
                            },
                            "timeRange": {
                                "closestTimestamp": closest_time,
                                "asMuchAsElements": num_bars + 1
                            }
                        }
                        message = f"md/getChart\n2\n\n{json.dumps(request_body)}"
                        ws.send(message)
                    
                    elif data.get("e") == "chart":
                        for chart in data.get("d", {}).get("charts", []):
                            if chart.get("eoh", False):
                                ws_data["complete"] = True
                                ws.close()
                                continue
                            
                            bars = chart.get("bars", [])
                            if bars:
                                for bar in bars[:-1]:
                                    processed_bar = {
                                        "timestamp": bar["timestamp"],
                                        "datetime": datetime.fromisoformat(bar["timestamp"].replace("Z", "+00:00")),
                                        "open": bar["open"],
                                        "high": bar["high"],
                                        "low": bar["low"],
                                        "close": bar["close"],
                                        "volume": bar.get("upVolume", 0) + bar.get("downVolume", 0),
                                        "up_volume": bar.get("upVolume", 0),
                                        "down_volume": bar.get("downVolume", 0),
                                        "up_ticks": bar.get("upTicks", 0),
                                        "down_ticks": bar.get("downTicks", 0),
                                        "symbol": contract_symbol
                                    }
                                    ws_data["bars"].append(processed_bar)
            
            ws = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message)
            ws_thread = threading.Thread(
                target=lambda: ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}),
                daemon=True
            )
            ws_thread.start()
            
            # Wait for data
            timeout = 15
            start = time.time()
            while not ws_data["complete"] and (time.time() - start) < timeout:
                time.sleep(0.5)
            
            if ws_data["bars"]:
                print(f"  ✅ Fetched {len(ws_data['bars'])} bars")
                return ws_data["bars"], contract_symbol
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue
    
    return None, None

def store_candles_in_supabase(timeframe, candles, symbol):
    """
    Store candles in Supabase table
    """
    table_map = {
        5: "nq_candles_5min",
        15: "nq_candles_15min",
        30: "nq_candles_30min",
        60: "nq_candles_1hour"
    }
    
    table_name = table_map.get(timeframe)
    if not table_name:
        print(f"  ❌ Invalid timeframe: {timeframe}")
        return False
    
    print(f"  📥 Storing {len(candles)} candles in {table_name}...")
    
    # Prepare records
    records = []
    for candle in candles:
        record = {
            "symbol": symbol,
            "candle_time": candle["datetime"].isoformat(),
            "open": float(candle["open"]),
            "high": float(candle["high"]),
            "low": float(candle["low"]),
            "close": float(candle["close"]),
            "volume": int(candle["volume"]),
            "up_volume": int(candle.get("up_volume", 0)),
            "down_volume": int(candle.get("down_volume", 0)),
            "up_ticks": int(candle.get("up_ticks", 0)),
            "down_ticks": int(candle.get("down_ticks", 0))
        }
        records.append(record)
    
    try:
        # Insert data (upsert to handle duplicates)
        result = SUPABASE.schema("orca").table(table_name).upsert(
            records,
            on_conflict="symbol,candle_time"
        ).execute()
        
        print(f"  ✅ Successfully stored {len(records)} candles")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed to store candles: {e}")
        return False

def verify_data_in_supabase(timeframe):
    """
    Verify that data was stored correctly
    """
    table_map = {
        5: "nq_candles_5min",
        15: "nq_candles_15min",
        30: "nq_candles_30min",
        60: "nq_candles_1hour"
    }
    
    table_name = table_map.get(timeframe)
    
    print(f"\n🔍 Verifying data in {table_name}...")
    
    try:
        result = SUPABASE.schema("orca").table(table_name).select(
            "candle_time, open, high, low, close, volume"
        ).order("candle_time", desc=True).limit(5).execute()
        
        if result.data and len(result.data) > 0:
            print(f"  ✅ Found {len(result.data)} candles:")
            for candle in result.data:
                print(f"     {candle['candle_time']}: O=${candle['open']}, H=${candle['high']}, L=${candle['low']}, C=${candle['close']}, V={candle['volume']}")
            return True
        else:
            print(f"  ⚠️  No data found")
            return False
            
    except Exception as e:
        print(f"  ❌ Error querying data: {e}")
        return False

def main():
    print("="*70)
    print("🚀 Fetch and Store Candles Test")
    print("="*70)
    
    timeframes = [5, 15, 30, 60]
    timeframe_names = {5: "5-minute", 15: "15-minute", 30: "30-minute", 60: "1-hour"}
    
    results = {}
    
    for timeframe in timeframes:
        print(f"\n{'='*70}")
        print(f"📊 Processing {timeframe_names[timeframe]} candles")
        print(f"{'='*70}")
        
        # Fetch candles
        candles, symbol = get_candles_from_tradovate(timeframe, num_bars=5)
        
        if not candles:
            print(f"  ❌ Failed to fetch {timeframe_names[timeframe]} candles")
            results[timeframe] = False
            continue
        
        # Store in Supabase
        success = store_candles_in_supabase(timeframe, candles, symbol)
        results[timeframe] = success
        
        # Verify
        if success:
            verify_data_in_supabase(timeframe)
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Summary")
    print(f"{'='*70}")
    for timeframe in timeframes:
        status = "✅ Success" if results.get(timeframe) else "❌ Failed"
        print(f"  {timeframe_names[timeframe]:12} : {status}")
    
    print(f"\n{'='*70}")
    
    all_success = all(results.values())
    if all_success:
        print("🎉 All candles fetched and stored successfully!")
    else:
        print("⚠️  Some candles failed to fetch or store")
    
    print(f"{'='*70}")

if __name__ == "__main__":
    main()
