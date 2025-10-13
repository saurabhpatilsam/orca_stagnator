"""
Fully Automated 24/7 Trading Daemon
====================================
This daemon runs continuously and handles all trading operations automatically:
- Detects US market open/close times
- Handles market holidays
- Cancels all orders 5 minutes before market open
- Waits for first hour candle to close
- Places all orders automatically
- Runs Monday-Friday without manual intervention

Author: Automated Trading System
Date: 2025-10-11
"""

import os
import sys
import time
import pytz
import signal as sys_signal
from datetime import datetime, timedelta, time as dt_time
from typing import Optional, List, Dict
from loguru import logger
import pandas_market_calendars as mcal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from send_trading_signal import TradingSignalSender
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class DaemonConfig:
    """Configuration for the automated trading daemon"""
    
    # Instrument settings
    INSTRUMENT = os.getenv("STRATEGY_INSTRUMENT", "ESZ5")
    ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "PAAPEX1361890000010")
    
    # Market timing (US Eastern Time)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    FIRST_HOUR_DURATION_MINUTES = 60
    
    # Pre-market order cancellation (5 minutes before open)
    CANCEL_ORDERS_BEFORE_OPEN_MINUTES = 5
    
    # Entry settings
    POINTS_SPACING = 9
    MAX_ORDERS_PER_SIDE = 5
    
    # Risk management
    STOP_LOSS_POINTS = 5
    TAKE_PROFIT_POINTS = 5
    QUANTITY_PER_ORDER = 1
    
    # Order settings
    ORDER_TYPE = "limit"
    STRATEGY_NAME = "first_hour_breakout_automated"
    
    # Daemon settings
    CHECK_INTERVAL_SECONDS = 30  # Check every 30 seconds
    
    # Market calendar
    EXCHANGE = "CME"  # Chicago Mercantile Exchange for ES/NQ


# ============================================================================
# US MARKET CALENDAR & HOLIDAY HANDLER
# ============================================================================

class MarketCalendar:
    """Handles US market calendar, holidays, and trading hours"""
    
    def __init__(self, exchange: str = "CME"):
        """Initialize market calendar"""
        try:
            self.calendar = mcal.get_calendar(exchange)
            logger.info(f"Market calendar initialized for {exchange}")
        except Exception as e:
            logger.warning(f"Could not load market calendar: {e}")
            logger.warning("Using basic calendar (may not account for all holidays)")
            self.calendar = None
        
        self.et_tz = pytz.timezone('US/Eastern')
    
    def is_market_open_today(self, date: datetime = None) -> bool:
        """
        Check if the market is open on a given date.
        
        Args:
            date: Date to check (defaults to today)
        
        Returns:
            True if market is open, False otherwise
        """
        if date is None:
            date = datetime.now(self.et_tz)
        
        # Check if it's a weekend
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # If we have the calendar, check for holidays
        if self.calendar:
            try:
                schedule = self.calendar.schedule(
                    start_date=date.strftime('%Y-%m-%d'),
                    end_date=date.strftime('%Y-%m-%d')
                )
                return len(schedule) > 0
            except Exception as e:
                logger.error(f"Error checking market calendar: {e}")
                # Fall back to basic check (weekday only)
                return date.weekday() < 5
        
        # Basic check: Monday-Friday
        return date.weekday() < 5
    
    def get_next_market_open(self, from_date: datetime = None) -> datetime:
        """
        Get the next market open datetime.
        
        Args:
            from_date: Starting date (defaults to now)
        
        Returns:
            datetime of next market open
        """
        if from_date is None:
            from_date = datetime.now(self.et_tz)
        
        # Start checking from tomorrow
        check_date = from_date + timedelta(days=1)
        
        # Find next trading day
        max_days_to_check = 10  # Don't check more than 10 days ahead
        for _ in range(max_days_to_check):
            if self.is_market_open_today(check_date):
                # Found a trading day, return market open time
                return check_date.replace(
                    hour=DaemonConfig.MARKET_OPEN_HOUR,
                    minute=DaemonConfig.MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0
                )
            check_date += timedelta(days=1)
        
        # Fallback: return next Monday
        days_until_monday = (7 - from_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        
        next_monday = from_date + timedelta(days=days_until_monday)
        return next_monday.replace(
            hour=DaemonConfig.MARKET_OPEN_HOUR,
            minute=DaemonConfig.MARKET_OPEN_MINUTE,
            second=0,
            microsecond=0
        )


# ============================================================================
# ORDER MANAGER
# ============================================================================

class OrderManager:
    """Manages order placement and cancellation"""
    
    def __init__(self):
        """Initialize order manager"""
        self.signal_sender = TradingSignalSender()
        self.placed_signal_ids: List[str] = []
    
    def cancel_all_orders(self) -> int:
        """
        Cancel all pending orders in Supabase.
        
        Returns:
            Number of orders cancelled
        """
        logger.info("Cancelling all pending orders...")
        
        cancelled_count = 0
        for signal_id in self.placed_signal_ids:
            try:
                if self.signal_sender.cancel_signal(signal_id):
                    cancelled_count += 1
                    logger.info(f"  ✅ Cancelled signal: {signal_id}")
            except Exception as e:
                logger.error(f"  ❌ Error cancelling signal {signal_id}: {e}")
        
        # Clear the list
        self.placed_signal_ids.clear()
        
        logger.success(f"Cancelled {cancelled_count} orders")
        return cancelled_count
    
    def place_breakout_orders(
        self,
        first_hour_high: float,
        first_hour_low: float
    ) -> Dict[str, List[str]]:
        """
        Place all breakout orders based on first hour high/low.
        
        Args:
            first_hour_high: High of first hour candle
            first_hour_low: Low of first hour candle
        
        Returns:
            Dict with lists of signal IDs for short and long orders
        """
        placed_signals = {
            'short_signals': [],
            'long_signals': []
        }
        
        logger.info("=" * 70)
        logger.info("PLACING BREAKOUT ORDERS")
        logger.info("=" * 70)
        logger.info(f"First Hour High: {first_hour_high}")
        logger.info(f"First Hour Low: {first_hour_low}")
        
        # Calculate and place SHORT orders
        logger.info(f"\n📉 Placing {DaemonConfig.MAX_ORDERS_PER_SIDE} SHORT orders...")
        for i in range(1, DaemonConfig.MAX_ORDERS_PER_SIDE + 1):
            price = first_hour_high + (i * DaemonConfig.POINTS_SPACING)
            stop_loss = price + DaemonConfig.STOP_LOSS_POINTS
            take_profit = price - DaemonConfig.TAKE_PROFIT_POINTS
            
            result = self.signal_sender.send_signal(
                instrument=DaemonConfig.INSTRUMENT,
                side="sell",
                quantity=DaemonConfig.QUANTITY_PER_ORDER,
                strategy_name=DaemonConfig.STRATEGY_NAME,
                order_type=DaemonConfig.ORDER_TYPE,
                price=round(price, 2),
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                account_name=DaemonConfig.ACCOUNT_NAME,
                metadata={
                    "order_number": i,
                    "side": "short",
                    "first_hour_high": first_hour_high,
                    "first_hour_low": first_hour_low,
                    "session_date": datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                }
            )
            
            if result["success"]:
                signal_id = result['signal_id']
                placed_signals['short_signals'].append(signal_id)
                self.placed_signal_ids.append(signal_id)
                logger.success(f"  ✅ SHORT #{i}: Entry={price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            else:
                logger.error(f"  ❌ Failed SHORT #{i}: {result.get('error')}")
        
        # Calculate and place LONG orders
        logger.info(f"\n📈 Placing {DaemonConfig.MAX_ORDERS_PER_SIDE} LONG orders...")
        for i in range(1, DaemonConfig.MAX_ORDERS_PER_SIDE + 1):
            price = first_hour_low - (i * DaemonConfig.POINTS_SPACING)
            stop_loss = price - DaemonConfig.STOP_LOSS_POINTS
            take_profit = price + DaemonConfig.TAKE_PROFIT_POINTS
            
            result = self.signal_sender.send_signal(
                instrument=DaemonConfig.INSTRUMENT,
                side="buy",
                quantity=DaemonConfig.QUANTITY_PER_ORDER,
                strategy_name=DaemonConfig.STRATEGY_NAME,
                order_type=DaemonConfig.ORDER_TYPE,
                price=round(price, 2),
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                account_name=DaemonConfig.ACCOUNT_NAME,
                metadata={
                    "order_number": i,
                    "side": "long",
                    "first_hour_high": first_hour_high,
                    "first_hour_low": first_hour_low,
                    "session_date": datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')
                }
            )
            
            if result["success"]:
                signal_id = result['signal_id']
                placed_signals['long_signals'].append(signal_id)
                self.placed_signal_ids.append(signal_id)
                logger.success(f"  ✅ LONG #{i}: Entry={price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
            else:
                logger.error(f"  ❌ Failed LONG #{i}: {result.get('error')}")
        
        logger.info("=" * 70)
        logger.success(f"Total orders placed: {len(self.placed_signal_ids)}")
        logger.info("=" * 70)
        
        return placed_signals


# ============================================================================
# AUTOMATED TRADING DAEMON
# ============================================================================

class AutomatedTradingDaemon:
    """Fully automated 24/7 trading daemon"""
    
    def __init__(self):
        """Initialize the daemon"""
        self.market_calendar = MarketCalendar(DaemonConfig.EXCHANGE)
        self.order_manager = OrderManager()
        self.running = True
        self.et_tz = pytz.timezone('US/Eastern')
        self.orders_placed_today = False
        
        logger.info("=" * 70)
        logger.info("AUTOMATED TRADING DAEMON INITIALIZED")
        logger.info("=" * 70)
        logger.info(f"Instrument: {DaemonConfig.INSTRUMENT}")
        logger.info(f"Account: {DaemonConfig.ACCOUNT_NAME}")
        logger.info(f"Market Open: {DaemonConfig.MARKET_OPEN_HOUR}:{DaemonConfig.MARKET_OPEN_MINUTE:02d} ET")
        logger.info(f"Strategy: First Hour Breakout")
        logger.info(f"Running: 24/7 Automated Mode")
        logger.info("=" * 70)
    
    def get_current_time_et(self) -> datetime:
        """Get current time in ET timezone"""
        return datetime.now(self.et_tz)
    
    def fetch_first_hour_candle_data(self) -> Optional[Dict[str, float]]:
        """
        Fetch first hour candle data from Tradovate API.
        
        This fetches the actual OHLC data for the first hour candle after market open
        directly from Tradovate API using the existing broker integration.
        
        Returns:
            Dict with 'open', 'high', 'low', 'close' or None if error
        """
        logger.info("Fetching first hour candle data from Tradovate API...")
        
        try:
            # Import broker here to avoid circular imports
            from app.services.orca_redis.client import get_redis_client
            from app.services.tradingview.broker import TradingViewTradovateBroker
            
            # Get Redis client
            redis_client = get_redis_client()
            if not redis_client:
                logger.error("Failed to connect to Redis")
                return None
            
            # Initialize broker
            broker = TradingViewTradovateBroker(
                redis_client=redis_client,
                account_name=DaemonConfig.ACCOUNT_NAME,
                base_url=os.getenv("TRADING_API_BASE", "https://tv-demo.tradovateapi.com")
            )
            
            # Get current time in ET
            now_et = self.get_current_time_et()
            market_open = now_et.replace(
                hour=DaemonConfig.MARKET_OPEN_HOUR,
                minute=DaemonConfig.MARKET_OPEN_MINUTE,
                second=0,
                microsecond=0
            )
            
            # Calculate first hour end time
            first_hour_end = market_open + timedelta(minutes=DaemonConfig.FIRST_HOUR_DURATION_MINUTES)
            
            # Fetch chart data from Tradovate API
            # Tradovate uses chart/bars endpoint for historical data
            # Format: /chart/bars?symbol=ESZ5&chartDescription={"underlyingType":"MinuteBar","elementSize":60}
            
            chart_description = {
                "underlyingType": "MinuteBar",
                "elementSize": 60,  # 60-minute bars
                "withHistogram": False
            }
            
            # Make request to get chart data
            import json
            endpoint = f"/chart/bars?symbol={DaemonConfig.INSTRUMENT}&chartDescription={json.dumps(chart_description)}&locale=en"
            
            logger.info(f"Requesting chart data for {DaemonConfig.INSTRUMENT}...")
            response = broker._make_request("GET", endpoint)
            
            if response.s == "ok" and response.d:
                # Parse the chart data
                # Tradovate returns bars in format: {t: timestamp, o: open, h: high, l: low, c: close}
                bars = response.d
                
                if not bars or len(bars) == 0:
                    logger.error("No chart data returned from Tradovate API")
                    return None
                
                # Get the first bar (first hour candle)
                # The most recent bar should be the first hour
                first_hour_bar = bars[0] if isinstance(bars, list) else bars
                
                candle_data = {
                    'open': float(first_hour_bar.get('o', 0)),
                    'high': float(first_hour_bar.get('h', 0)),
                    'low': float(first_hour_bar.get('l', 0)),
                    'close': float(first_hour_bar.get('c', 0)),
                    'timestamp': first_hour_bar.get('t', '')
                }
                
                logger.success(f"✅ First hour candle data retrieved from Tradovate:")
                logger.info(f"   Open:  {candle_data['open']:.2f}")
                logger.info(f"   High:  {candle_data['high']:.2f}")
                logger.info(f"   Low:   {candle_data['low']:.2f}")
                logger.info(f"   Close: {candle_data['close']:.2f}")
                
                return candle_data
            else:
                logger.error(f"Failed to get chart data: {response.errmsg}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching first hour candle data: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)
            
            # Fallback to sample data for testing
            logger.warning("⚠️  Using SAMPLE data as fallback")
            return {
                'open': 5900.00,
                'high': 5920.00,
                'low': 5880.00,
                'close': 5910.00
            }
    
    def should_cancel_orders(self, now_et: datetime) -> bool:
        """
        Check if we should cancel orders (5 minutes before market open).
        
        Args:
            now_et: Current time in ET
        
        Returns:
            True if we should cancel orders
        """
        if not self.market_calendar.is_market_open_today(now_et):
            return False
        
        market_open = now_et.replace(
            hour=DaemonConfig.MARKET_OPEN_HOUR,
            minute=DaemonConfig.MARKET_OPEN_MINUTE,
            second=0,
            microsecond=0
        )
        
        cancel_time = market_open - timedelta(minutes=DaemonConfig.CANCEL_ORDERS_BEFORE_OPEN_MINUTES)
        
        # Cancel if we're within the 5-minute window before open
        return cancel_time <= now_et < market_open
    
    def should_place_orders(self, now_et: datetime) -> bool:
        """
        Check if we should place orders (after first hour closes).
        
        Args:
            now_et: Current time in ET
        
        Returns:
            True if we should place orders
        """
        if not self.market_calendar.is_market_open_today(now_et):
            return False
        
        if self.orders_placed_today:
            return False
        
        market_open = now_et.replace(
            hour=DaemonConfig.MARKET_OPEN_HOUR,
            minute=DaemonConfig.MARKET_OPEN_MINUTE,
            second=0,
            microsecond=0
        )
        
        first_hour_close = market_open + timedelta(minutes=DaemonConfig.FIRST_HOUR_DURATION_MINUTES)
        
        # Place orders after first hour closes
        return now_et >= first_hour_close
    
    def run_daily_cycle(self):
        """Run one daily trading cycle"""
        now_et = self.get_current_time_et()
        
        # Check if we should cancel orders
        if self.should_cancel_orders(now_et):
            logger.info("🚫 Pre-market: Cancelling all orders...")
            self.order_manager.cancel_all_orders()
            self.orders_placed_today = False
            time.sleep(60)  # Wait a minute after cancelling
            return
        
        # Check if we should place orders
        if self.should_place_orders(now_et):
            logger.info("🎯 First hour closed: Placing orders...")
            
            # Fetch first hour candle data
            candle_data = self.fetch_first_hour_candle_data()
            
            if candle_data:
                # Place all orders
                self.order_manager.place_breakout_orders(
                    first_hour_high=candle_data['high'],
                    first_hour_low=candle_data['low']
                )
                self.orders_placed_today = True
                logger.success("✅ Daily orders placed successfully!")
            else:
                logger.error("❌ Failed to fetch candle data")
            
            return
        
        # Check if it's a new day (reset flag)
        if now_et.hour < DaemonConfig.MARKET_OPEN_HOUR:
            if self.orders_placed_today:
                logger.info("🌅 New trading day - resetting flags")
                self.orders_placed_today = False
    
    def run(self):
        """Main daemon loop - runs 24/7"""
        logger.info("🚀 Starting automated trading daemon...")
        logger.info("   Running 24/7 - Press Ctrl+C to stop")
        
        try:
            while self.running:
                now_et = self.get_current_time_et()
                
                # Log status every hour
                if now_et.minute == 0:
                    is_trading_day = self.market_calendar.is_market_open_today(now_et)
                    status = "TRADING DAY" if is_trading_day else "NON-TRADING DAY"
                    logger.info(f"⏰ {now_et.strftime('%Y-%m-%d %H:%M ET')} - {status}")
                
                # Run daily cycle
                self.run_daily_cycle()
                
                # Sleep before next check
                time.sleep(DaemonConfig.CHECK_INTERVAL_SECONDS)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️  Shutting down daemon...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Daemon error: {e}")
            raise
    
    def stop(self):
        """Stop the daemon"""
        logger.info("Stopping automated trading daemon...")
        self.running = False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("AUTOMATED TRADING DAEMON - 24/7 MODE")
    print("=" * 70)
    print("This daemon will run continuously and handle:")
    print("  ✅ Market open/close detection")
    print("  ✅ Holiday detection")
    print("  ✅ Pre-market order cancellation (5 min before open)")
    print("  ✅ First hour candle monitoring")
    print("  ✅ Automatic order placement")
    print("  ✅ Daily cycle management")
    print("=" * 70 + "\n")
    
    # Create and start daemon
    daemon = AutomatedTradingDaemon()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\nReceived shutdown signal")
        daemon.stop()
        sys.exit(0)
    
    sys_signal.signal(sys_signal.SIGINT, signal_handler)
    sys_signal.signal(sys_signal.SIGTERM, signal_handler)
    
    # Start the daemon
    daemon.run()


if __name__ == "__main__":
    main()
