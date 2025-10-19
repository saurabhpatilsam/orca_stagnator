#!/usr/bin/env python3
"""
Automated Candle Data Fetcher
Fetches OHLC candle data from Tradovate and stores in Supabase
Timeframes: 5min, 15min, 30min, 1hour
"""
import sys
import os
import json
import time
import ssl
import websocket
import threading
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from app.services.orca_redis.client import get_redis_client
from supabase import create_client, Client

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("python-dotenv not installed, using system environment variables only")

# =====================================================
# Configuration
# =====================================================
TRADOVATE_USERNAMES = ["APEX_266668", "APEX_265995", "APEX_272045", "APEX_136189"]
REST_BASE_URL = "https://demo.tradovateapi.com/v1"
WS_URL = "wss://md-demo.tradovateapi.com/v1/websocket"

# Supabase Configuration (from environment)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

# Timeframes to fetch
TIMEFRAMES = {
    "5min": {"minutes": 5, "table": "nq_candles_5min", "bars_count": 5},
    "15min": {"minutes": 15, "table": "nq_candles_15min", "bars_count": 5},
    "30min": {"minutes": 30, "table": "nq_candles_30min", "bars_count": 5},
    "1hour": {"minutes": 60, "table": "nq_candles_1hour", "bars_count": 5}
}

# =====================================================
# Simplified WebSocket Client
# =====================================================
class TradovateWebSocketClient:
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
        logger.info("Connecting to Tradovate WebSocket...")
        
        def on_open(ws):
            logger.info("WebSocket opened")
            auth_msg = f"authorize\n{self.request_id}\n\n{self.md_token}"
            ws.send(auth_msg)
            self.request_id += 1
            
        def on_message(ws, message):
            if message == "h":
                ws.send("[]")
                return
            elif message == "o":
                return
            elif message.startswith("a["):
                data = json.loads(message[2:-1])
                
                if data.get("s") == 200 and not self.authorized:
                    self.authorized = True
                    logger.info("WebSocket authorized")
                
                elif data.get("e") == "chart":
                    self._process_chart_data(data.get("d", {}))
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.debug("WebSocket closed")
        
        self.ws = websocket.WebSocketApp(
            WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
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
    
    def request_chart_data(self, symbol, bar_size_minutes, num_bars):
        """Request historical chart data"""
        if not self.authorized:
            logger.error("Not authorized")
            return None
        
        starting_time = datetime.now()
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
        
        message = f"md/getChart\n{req_id}\n\n{json.dumps(request_body)}"
        self.ws.send(message)
        self.request_id += 1
        
        logger.debug(f"Requested {bar_size_minutes}min chart data (request #{req_id})")
        
        if self.chart_events[req_id].wait(timeout=30):
            return self.chart_data[req_id]["bars"]
        else:
            logger.warning("Timeout waiting for chart data")
            return None
    
    def _process_chart_data(self, data):
        """Process incoming chart data"""
        for chart in data.get("charts", []):
            if chart.get("eoh", False):
                for req_id, chart_data in self.chart_data.items():
                    if not chart_data["complete"]:
                        chart_data["complete"] = True
                        self.chart_events[req_id].set()
                        break
                continue
            
            bars = chart.get("bars", [])
            if bars:
                for req_id, chart_data in self.chart_data.items():
                    if not chart_data["complete"]:
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
                                "down_ticks": bar.get("downTicks", 0)
                            }
                            chart_data["bars"].append(processed_bar)
                        break
    
    def close(self):
        if self.ws:
            self.ws.close()

# =====================================================
# Tradovate Token Management
# =====================================================
def get_tradovate_tokens(account_name):
    """Get tokens from Redis and renew them"""
    logger.info(f"Getting tokens for {account_name}...")
    
    redis_client = get_redis_client()
    if not redis_client:
        logger.error("Redis connection failed")
        return None, None
    
    tv_token = redis_client.get(f"token:{account_name}")
    if not tv_token:
        logger.warning(f"No token found for {account_name}")
        return None, None
    
    logger.debug("TV token retrieved from Redis")
    
    # Renew tokens
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
        
        logger.debug("MD access token obtained")
        return access_token, md_token
    
    except Exception as e:
        logger.error(f"Token renewal failed: {e}")
        return None, None

def discover_contract(access_token, symbol_prefix):
    """Discover current front-month contract"""
    logger.info(f"Discovering current {symbol_prefix} contract...")
    
    import requests
    url = f"{REST_BASE_URL}/contract/suggest?t={symbol_prefix}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        contracts = response.json()
        
        if contracts:
            contract_name = contracts[0].get("name")
            logger.info(f"Using contract: {contract_name}")
            return contract_name
        else:
            logger.error("No contracts found")
            return None
    
    except Exception as e:
        logger.error(f"Contract discovery failed: {e}")
        return None

# =====================================================
# Supabase Storage
# =====================================================
class SupabaseStorage:
    """Handle Supabase storage operations"""
    
    def __init__(self):
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Supabase credentials not found in environment")
        
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    
    def store_candles(self, timeframe: str, symbol: str, candles: List[Dict]):
        """Store candles in Supabase"""
        table_name = TIMEFRAMES[timeframe]["table"]
        
        logger.info(f"Storing {len(candles)} {timeframe} candles for {symbol}...")
        
        # Prepare data for insertion
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
            # Use upsert to handle duplicates
            result = self.client.schema("orca").table(table_name).upsert(
                records,
                on_conflict="symbol,candle_time"
            ).execute()
            
            logger.success(f"✅ Stored {len(records)} candles in {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store candles: {e}")
            return False
    
    def get_latest_candle_time(self, timeframe: str, symbol: str) -> Optional[datetime]:
        """Get the timestamp of the latest stored candle"""
        table_name = TIMEFRAMES[timeframe]["table"]
        
        try:
            result = self.client.schema("orca").table(table_name).select("candle_time").eq(
                "symbol", symbol
            ).order("candle_time", desc=True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return datetime.fromisoformat(result.data[0]["candle_time"])
            return None
            
        except Exception as e:
            logger.error(f"Failed to get latest candle time: {e}")
            return None

# =====================================================
# Candle Data Fetcher
# =====================================================
class CandleFetcher:
    """Automated candle data fetcher"""
    
    def __init__(self):
        self.storage = SupabaseStorage()
        self.symbol = "NQ"
        self.contract_symbol = None
        self.ws_client = None
        
    def initialize_connection(self):
        """Initialize connection to Tradovate"""
        logger.info("="*70)
        logger.info("Initializing Tradovate connection...")
        logger.info("="*70)
        
        # Try different accounts
        for account_name in TRADOVATE_USERNAMES:
            logger.info(f"Trying account: {account_name}")
            
            access_token, md_token = get_tradovate_tokens(account_name)
            if not access_token or not md_token:
                continue
            
            self.contract_symbol = discover_contract(access_token, self.symbol)
            if not self.contract_symbol:
                continue
            
            # Connect WebSocket
            self.ws_client = TradovateWebSocketClient(md_token)
            if self.ws_client.connect():
                logger.success(f"✅ Connected to Tradovate using {account_name}")
                return True
            
        logger.error("❌ Failed to connect to Tradovate")
        return False
    
    def fetch_and_store_timeframe(self, timeframe: str):
        """Fetch and store candles for a specific timeframe"""
        if not self.ws_client or not self.contract_symbol:
            logger.error(f"Not connected to Tradovate")
            return False
        
        config = TIMEFRAMES[timeframe]
        bar_size = config["minutes"]
        bars_count = config["bars_count"]
        
        logger.info(f"📊 Fetching {timeframe} candles...")
        
        try:
            bars = self.ws_client.request_chart_data(
                symbol=self.contract_symbol,
                bar_size_minutes=bar_size,
                num_bars=bars_count
            )
            
            if bars and len(bars) > 0:
                logger.info(f"Received {len(bars)} {timeframe} bars")
                
                # Store in Supabase
                success = self.storage.store_candles(timeframe, self.contract_symbol, bars)
                
                if success:
                    last_candle = bars[-1]
                    logger.info(f"Last {timeframe} candle: {last_candle['datetime']} - Close: ${last_candle['close']:,.2f}")
                
                return success
            else:
                logger.warning(f"No bars received for {timeframe}")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching {timeframe} candles: {e}")
            return False
    
    def fetch_all_timeframes(self):
        """Fetch and store all timeframes"""
        logger.info("="*70)
        logger.info(f"🔄 Fetching all timeframes - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Reconnect if needed
        if not self.ws_client or not self.contract_symbol:
            if not self.initialize_connection():
                logger.error("Failed to initialize connection")
                return
        
        # Fetch each timeframe
        for timeframe in TIMEFRAMES.keys():
            try:
                self.fetch_and_store_timeframe(timeframe)
                time.sleep(2)  # Small delay between requests
            except Exception as e:
                logger.error(f"Error processing {timeframe}: {e}")
        
        logger.info("="*70)
        logger.success(f"✅ Completed fetching all timeframes")
        logger.info("="*70)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.ws_client:
            self.ws_client.close()

# =====================================================
# Scheduler
# =====================================================
def run_scheduler():
    """Run scheduled candle fetching"""
    logger.info("🚀 Starting Automated Candle Fetcher")
    logger.info("="*70)
    logger.info("Schedule:")
    logger.info("  - 5min candles:  Every 5 minutes")
    logger.info("  - 15min candles: Every 15 minutes")
    logger.info("  - 30min candles: Every 30 minutes")
    logger.info("  - 1hour candles: Every hour")
    logger.info("="*70)
    
    fetcher = CandleFetcher()
    
    # Initial fetch
    logger.info("\n📊 Running initial fetch...")
    fetcher.fetch_all_timeframes()
    
    # Schedule periodic fetching
    schedule.every(5).minutes.do(lambda: fetcher.fetch_and_store_timeframe("5min"))
    schedule.every(15).minutes.do(lambda: fetcher.fetch_and_store_timeframe("15min"))
    schedule.every(30).minutes.do(lambda: fetcher.fetch_and_store_timeframe("30min"))
    schedule.every(1).hours.do(lambda: fetcher.fetch_and_store_timeframe("1hour"))
    
    # Re-initialize connection every 4 hours (refresh tokens)
    schedule.every(4).hours.do(fetcher.initialize_connection)
    
    logger.info("\n✅ Scheduler started. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down...")
        fetcher.cleanup()
        logger.info("👋 Goodbye!")

# =====================================================
# Manual Fetch (for testing)
# =====================================================
def manual_fetch():
    """Manually fetch and store candles once"""
    logger.info("📊 Manual fetch mode")
    
    fetcher = CandleFetcher()
    fetcher.fetch_all_timeframes()
    fetcher.cleanup()

# =====================================================
# Main
# =====================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Automated Candle Data Fetcher")
    parser.add_argument("--manual", action="store_true", help="Run once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run as continuous daemon")
    
    args = parser.parse_args()
    
    if args.manual:
        manual_fetch()
    else:
        # Default: run as scheduled daemon
        run_scheduler()
