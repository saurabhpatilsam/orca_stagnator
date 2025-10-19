#!/usr/bin/env python3
"""
Continuous Candle Data Daemon
Runs 24/7 fetching and storing NQ candle data at scheduled intervals
"""
import sys
import os
import time
import signal
from datetime import datetime, timedelta
from typing import Dict, Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment
load_dotenv()

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/candle_daemon_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="DEBUG"
)

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL", default='https://dcoukhtfcloqpfmijock.supabase.co')
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or 'sb_secret__t3NV0SUY8ywb2y_44jRDA_JOcR--G_'
SUPABASE: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import candle fetcher
from get_nq_30min_working import (
    get_tradovate_tokens,
    discover_contract,
    SimpleTradovateWebSocket,
    TRADOVATE_USERNAMES
)

# Timeframe configuration
TIMEFRAMES = {
    5: {"interval_minutes": 5, "function": "insert_nq_candles_5min", "name": "5min"},
    15: {"interval_minutes": 15, "function": "insert_nq_candles_15min", "name": "15min"},
    30: {"interval_minutes": 30, "function": "insert_nq_candles_30min", "name": "30min"},
    60: {"interval_minutes": 60, "function": "insert_nq_candles_1hour", "name": "1hour"}
}

# Global state
running = True
last_fetch_times: Dict[int, Optional[datetime]] = {5: None, 15: None, 30: None, 60: None}

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info("Shutdown signal received. Stopping daemon...")
    running = False

def fetch_and_store_candles(timeframe_minutes: int, num_bars: int = 5) -> bool:
    """Fetch candles and store in Supabase"""
    config = TIMEFRAMES[timeframe_minutes]
    function_name = config["function"]
    
    logger.info(f"📊 Fetching {config['name']} candles...")
    
    # Try each Tradovate account
    for account_name in TRADOVATE_USERNAMES:
        try:
            # Get tokens
            access_token, md_token = get_tradovate_tokens(account_name)
            if not access_token or not md_token:
                continue
            
            # Discover contract
            contract_symbol = discover_contract(access_token, "NQ")
            if not contract_symbol:
                continue
            
            # Connect WebSocket and fetch data
            ws_client = SimpleTradovateWebSocket(md_token)
            if not ws_client.connect():
                continue
            
            bars = ws_client.request_chart_data(
                symbol=contract_symbol,
                bar_size_minutes=timeframe_minutes,
                starting_time=datetime.now(),
                num_bars=num_bars
            )
            
            ws_client.close()
            
            if not bars or len(bars) == 0:
                continue
            
            # Store candles
            success_count = 0
            for candle in bars:
                try:
                    SUPABASE.rpc(function_name, {
                        "p_symbol": contract_symbol,
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
                    error_str = str(e)
                    if '"success" : true' in error_str or 'Candle inserted/updated' in error_str:
                        success_count += 1
            
            logger.success(f"✅ Stored {success_count}/{len(bars)} {config['name']} candles")
            return True
            
        except Exception as e:
            logger.error(f"Error fetching {config['name']} candles with {account_name}: {e}")
            continue
    
    logger.error(f"❌ Failed to fetch {config['name']} candles from all accounts")
    return False

def should_fetch(timeframe_minutes: int) -> bool:
    """Determine if we should fetch this timeframe now"""
    last_fetch = last_fetch_times[timeframe_minutes]
    interval = TIMEFRAMES[timeframe_minutes]["interval_minutes"]
    
    if last_fetch is None:
        return True
    
    time_since_last = datetime.now() - last_fetch
    return time_since_last >= timedelta(minutes=interval)

def run_daemon():
    """Main daemon loop"""
    global running
    
    logger.info("="*70)
    logger.info("🚀 NQ Candle Data Daemon Started")
    logger.info("="*70)
    logger.info(f"Monitoring timeframes: {', '.join([TIMEFRAMES[tf]['name'] for tf in TIMEFRAMES])}")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*70)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    cycle_count = 0
    
    while running:
        cycle_count += 1
        logger.info(f"\n🔄 Cycle #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check each timeframe
        for timeframe_minutes in sorted(TIMEFRAMES.keys()):
            if should_fetch(timeframe_minutes):
                config = TIMEFRAMES[timeframe_minutes]
                logger.info(f"⏰ Time to fetch {config['name']} candles")
                
                try:
                    success = fetch_and_store_candles(timeframe_minutes, num_bars=5)
                    if success:
                        last_fetch_times[timeframe_minutes] = datetime.now()
                except Exception as e:
                    logger.error(f"Unexpected error in {config['name']} fetch: {e}")
            else:
                config = TIMEFRAMES[timeframe_minutes]
                next_fetch = last_fetch_times[timeframe_minutes] + timedelta(minutes=config["interval_minutes"])
                wait_time = (next_fetch - datetime.now()).total_seconds() / 60
                logger.debug(f"⏳ {config['name']}: Next fetch in {wait_time:.1f} minutes")
        
        # Sleep for 1 minute before next check
        logger.debug("💤 Sleeping for 1 minute...")
        time.sleep(60)
    
    logger.info("="*70)
    logger.info("👋 Daemon stopped gracefully")
    logger.info("="*70)

def main():
    """Entry point"""
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    try:
        run_daemon()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()
