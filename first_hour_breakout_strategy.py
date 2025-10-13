"""
First Hour Breakout Trading Strategy
=====================================
This strategy implements a first-hour breakout system for ES/NQ futures.

Strategy Rules:
1. Wait for first 1-hour candle after US market open (9:30 AM ET)
2. Mark the high and low of the first hour candle
3. Place SHORT orders every 9 points above the high (max 5 orders)
4. Place LONG orders every 9 points below the low (max 5 orders)
5. Each order has 5 points stop loss and 5 points take profit
6. Quantity: 1 contract per order

Author: Automated Trading System
Date: 2025-10-11
"""

import os
import sys
import time
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from send_trading_signal import TradingSignalSender

# Load environment variables
load_dotenv()

# ============================================================================
# STRATEGY CONFIGURATION
# ============================================================================

class StrategyConfig:
    """Configuration for the first hour breakout strategy"""
    
    # Instrument settings
    INSTRUMENT = os.getenv("STRATEGY_INSTRUMENT", "ESZ5")  # ES December 2025
    ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "PAAPEX1361890000010")
    
    # Market timing (US Eastern Time)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    FIRST_HOUR_DURATION_MINUTES = 60
    
    # Entry settings
    POINTS_SPACING = 9  # Points between each order
    MAX_ORDERS_PER_SIDE = 5  # Maximum orders on each side
    
    # Risk management
    STOP_LOSS_POINTS = 5
    TAKE_PROFIT_POINTS = 5
    QUANTITY_PER_ORDER = 1
    
    # Order type
    ORDER_TYPE = "limit"
    
    # Strategy name
    STRATEGY_NAME = "first_hour_breakout"


# ============================================================================
# FIRST HOUR CANDLE DATA
# ============================================================================

class FirstHourCandle:
    """Stores the first hour candle data"""
    
    def __init__(self, open_price: float, high: float, low: float, close: float, timestamp: datetime):
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"FirstHourCandle(O:{self.open}, H:{self.high}, L:{self.low}, C:{self.close})"


# ============================================================================
# STRATEGY IMPLEMENTATION
# ============================================================================

class FirstHourBreakoutStrategy:
    """First hour breakout trading strategy"""
    
    def __init__(self, config: StrategyConfig = None):
        """Initialize the strategy"""
        self.config = config or StrategyConfig()
        self.signal_sender = TradingSignalSender()
        self.first_hour_candle: Optional[FirstHourCandle] = None
        self.orders_placed = False
        
        logger.info(f"First Hour Breakout Strategy initialized for {self.config.INSTRUMENT}")
        logger.info(f"Market open: {self.config.MARKET_OPEN_HOUR}:{self.config.MARKET_OPEN_MINUTE:02d} ET")
        logger.info(f"Points spacing: {self.config.POINTS_SPACING}")
        logger.info(f"Max orders per side: {self.config.MAX_ORDERS_PER_SIDE}")
    
    def get_market_open_time(self, date: datetime = None) -> datetime:
        """
        Get the market open time for a given date in ET timezone.
        
        Args:
            date: Date to get market open time for (defaults to today)
        
        Returns:
            datetime object representing market open time in ET
        """
        if date is None:
            date = datetime.now(pytz.timezone('US/Eastern'))
        
        # Create market open time (9:30 AM ET)
        market_open = date.replace(
            hour=self.config.MARKET_OPEN_HOUR,
            minute=self.config.MARKET_OPEN_MINUTE,
            second=0,
            microsecond=0
        )
        
        return market_open
    
    def get_first_hour_end_time(self, market_open: datetime) -> datetime:
        """
        Get the end time of the first hour candle.
        
        Args:
            market_open: Market open datetime
        
        Returns:
            datetime object representing first hour end time
        """
        return market_open + timedelta(minutes=self.config.FIRST_HOUR_DURATION_MINUTES)
    
    def fetch_first_hour_candle(self) -> Optional[FirstHourCandle]:
        """
        Fetch the first hour candle data.
        
        In production, this would connect to your data provider (TradingView, IB, etc.)
        For now, this is a placeholder that you'll need to implement with your data source.
        
        Returns:
            FirstHourCandle object or None if data not available
        """
        logger.info("Fetching first hour candle data...")
        
        # TODO: Implement actual data fetching from your data provider
        # This is a placeholder - you need to connect to your data source
        
        # Example implementation (replace with actual data fetch):
        # For testing purposes, using sample data
        
        logger.warning("Using SAMPLE data - replace with actual data provider!")
        
        # Sample data for testing (REPLACE THIS)
        sample_candle = FirstHourCandle(
            open_price=5900.00,
            high=5920.00,
            low=5880.00,
            close=5910.00,
            timestamp=datetime.now(pytz.timezone('US/Eastern'))
        )
        
        logger.info(f"First hour candle: {sample_candle}")
        return sample_candle
    
    def calculate_order_levels(self, first_hour_candle: FirstHourCandle) -> Dict[str, List[float]]:
        """
        Calculate order entry levels based on first hour high/low.
        
        Args:
            first_hour_candle: FirstHourCandle object
        
        Returns:
            Dict with 'short_levels' and 'long_levels' lists
        """
        short_levels = []
        long_levels = []
        
        # Calculate SHORT levels (above the high)
        for i in range(1, self.config.MAX_ORDERS_PER_SIDE + 1):
            level = first_hour_candle.high + (i * self.config.POINTS_SPACING)
            short_levels.append(round(level, 2))
        
        # Calculate LONG levels (below the low)
        for i in range(1, self.config.MAX_ORDERS_PER_SIDE + 1):
            level = first_hour_candle.low - (i * self.config.POINTS_SPACING)
            long_levels.append(round(level, 2))
        
        logger.info(f"SHORT levels: {short_levels}")
        logger.info(f"LONG levels: {long_levels}")
        
        return {
            'short_levels': short_levels,
            'long_levels': long_levels
        }
    
    def place_orders(self, order_levels: Dict[str, List[float]]) -> Dict[str, List[str]]:
        """
        Place all orders by sending signals to Supabase.
        
        Args:
            order_levels: Dict with short and long order levels
        
        Returns:
            Dict with lists of signal IDs for short and long orders
        """
        placed_signals = {
            'short_signals': [],
            'long_signals': []
        }
        
        logger.info("=" * 70)
        logger.info("PLACING ORDERS")
        logger.info("=" * 70)
        
        # Place SHORT orders
        logger.info(f"\n📉 Placing {len(order_levels['short_levels'])} SHORT orders...")
        for idx, price in enumerate(order_levels['short_levels'], 1):
            stop_loss = price + self.config.STOP_LOSS_POINTS
            take_profit = price - self.config.TAKE_PROFIT_POINTS
            
            result = self.signal_sender.send_signal(
                instrument=self.config.INSTRUMENT,
                side="sell",
                quantity=self.config.QUANTITY_PER_ORDER,
                strategy_name=self.config.STRATEGY_NAME,
                order_type=self.config.ORDER_TYPE,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                account_name=self.config.ACCOUNT_NAME,
                metadata={
                    "order_number": idx,
                    "side": "short",
                    "first_hour_high": self.first_hour_candle.high,
                    "first_hour_low": self.first_hour_candle.low,
                    "entry_price": price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit
                }
            )
            
            if result["success"]:
                placed_signals['short_signals'].append(result['signal_id'])
                logger.success(f"  ✅ SHORT #{idx}: Entry={price}, SL={stop_loss}, TP={take_profit}")
            else:
                logger.error(f"  ❌ Failed to place SHORT #{idx}: {result.get('error')}")
        
        # Place LONG orders
        logger.info(f"\n📈 Placing {len(order_levels['long_levels'])} LONG orders...")
        for idx, price in enumerate(order_levels['long_levels'], 1):
            stop_loss = price - self.config.STOP_LOSS_POINTS
            take_profit = price + self.config.TAKE_PROFIT_POINTS
            
            result = self.signal_sender.send_signal(
                instrument=self.config.INSTRUMENT,
                side="buy",
                quantity=self.config.QUANTITY_PER_ORDER,
                strategy_name=self.config.STRATEGY_NAME,
                order_type=self.config.ORDER_TYPE,
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                account_name=self.config.ACCOUNT_NAME,
                metadata={
                    "order_number": idx,
                    "side": "long",
                    "first_hour_high": self.first_hour_candle.high,
                    "first_hour_low": self.first_hour_candle.low,
                    "entry_price": price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit
                }
            )
            
            if result["success"]:
                placed_signals['long_signals'].append(result['signal_id'])
                logger.success(f"  ✅ LONG #{idx}: Entry={price}, SL={stop_loss}, TP={take_profit}")
            else:
                logger.error(f"  ❌ Failed to place LONG #{idx}: {result.get('error')}")
        
        logger.info("=" * 70)
        logger.info(f"Total signals sent: {len(placed_signals['short_signals']) + len(placed_signals['long_signals'])}")
        logger.info("=" * 70)
        
        return placed_signals
    
    def run_once(self) -> bool:
        """
        Run the strategy once (fetch first hour candle and place orders).
        
        Returns:
            True if orders were placed successfully, False otherwise
        """
        if self.orders_placed:
            logger.warning("Orders already placed for today. Skipping.")
            return False
        
        logger.info("\n" + "=" * 70)
        logger.info("FIRST HOUR BREAKOUT STRATEGY - EXECUTION")
        logger.info("=" * 70)
        
        # Step 1: Fetch first hour candle
        self.first_hour_candle = self.fetch_first_hour_candle()
        
        if not self.first_hour_candle:
            logger.error("Failed to fetch first hour candle data")
            return False
        
        # Step 2: Calculate order levels
        order_levels = self.calculate_order_levels(self.first_hour_candle)
        
        # Step 3: Place orders
        placed_signals = self.place_orders(order_levels)
        
        # Mark orders as placed
        self.orders_placed = True
        
        logger.success("\n✅ Strategy execution complete!")
        logger.info(f"   SHORT orders: {len(placed_signals['short_signals'])}")
        logger.info(f"   LONG orders: {len(placed_signals['long_signals'])}")
        
        return True
    
    def wait_for_first_hour_close(self):
        """
        Wait until the first hour candle closes before executing strategy.
        This is useful for running the strategy in a loop.
        """
        et_tz = pytz.timezone('US/Eastern')
        
        while True:
            now_et = datetime.now(et_tz)
            market_open = self.get_market_open_time(now_et)
            first_hour_end = self.get_first_hour_end_time(market_open)
            
            # Check if we're past the first hour close
            if now_et >= first_hour_end:
                logger.info(f"First hour closed at {first_hour_end.strftime('%H:%M:%S ET')}")
                break
            
            # Calculate time remaining
            time_remaining = (first_hour_end - now_et).total_seconds()
            
            if time_remaining > 0:
                logger.info(f"Waiting for first hour to close... {int(time_remaining/60)} minutes remaining")
                time.sleep(60)  # Check every minute
            else:
                break


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for the strategy"""
    
    print("\n" + "=" * 70)
    print("FIRST HOUR BREAKOUT STRATEGY")
    print("=" * 70)
    print(f"Instrument: {StrategyConfig.INSTRUMENT}")
    print(f"Market Open: {StrategyConfig.MARKET_OPEN_HOUR}:{StrategyConfig.MARKET_OPEN_MINUTE:02d} ET")
    print(f"Points Spacing: {StrategyConfig.POINTS_SPACING}")
    print(f"Max Orders/Side: {StrategyConfig.MAX_ORDERS_PER_SIDE}")
    print(f"Stop Loss: {StrategyConfig.STOP_LOSS_POINTS} points")
    print(f"Take Profit: {StrategyConfig.TAKE_PROFIT_POINTS} points")
    print("=" * 70 + "\n")
    
    # Initialize strategy
    strategy = FirstHourBreakoutStrategy()
    
    # Option 1: Run immediately (for testing)
    logger.info("Running strategy immediately (test mode)...")
    strategy.run_once()
    
    # Option 2: Wait for first hour close (uncomment for production)
    # logger.info("Waiting for first hour to close...")
    # strategy.wait_for_first_hour_close()
    # strategy.run_once()


if __name__ == "__main__":
    main()
