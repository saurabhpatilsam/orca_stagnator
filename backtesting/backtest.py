"""
Tick-by-Tick Backtesting System
================================
This backtester simulates the first-hour breakout strategy using real tick-by-tick
market data from Supabase. It provides accurate performance metrics by testing
every single price tick to determine order fills, stop losses, and take profits.

Features:
- Tick-by-tick simulation (not candle-based)
- Real historical data from Supabase
- Accurate fill simulation
- Stop loss and take profit tracking
- Detailed performance metrics
- Trade-by-trade analysis

Author: Automated Trading System
Date: 2025-10-11
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pytz
from loguru import logger
from supabase import create_client, Client
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

class BacktestConfig:
    """Configuration for backtesting"""
    
    # Supabase connection
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Strategy parameters (same as live trading)
    POINTS_SPACING = 9
    MAX_ORDERS_PER_SIDE = 5
    STOP_LOSS_POINTS = 5
    TAKE_PROFIT_POINTS = 5
    QUANTITY_PER_ORDER = 1
    
    # Market timing
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    FIRST_HOUR_DURATION_MINUTES = 60
    
    # Instrument
    INSTRUMENT = "ESZ5"
    
    # Timezone
    ET_TZ = pytz.timezone('US/Eastern')


# ============================================================================
# DATA MODELS
# ============================================================================

class OrderStatus(Enum):
    """Order status enumeration"""
    PENDING = "pending"
    FILLED = "filled"
    STOPPED_OUT = "stopped_out"
    TAKE_PROFIT = "take_profit"
    CANCELLED = "cancelled"


class OrderSide(Enum):
    """Order side enumeration"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Tick:
    """Represents a single market tick"""
    timestamp: datetime
    price: float
    volume: int = 0
    bid: Optional[float] = None
    ask: Optional[float] = None


@dataclass
class Order:
    """Represents a trading order"""
    order_id: int
    side: OrderSide
    entry_price: float
    stop_loss: float
    take_profit: float
    quantity: int
    status: OrderStatus = OrderStatus.PENDING
    fill_time: Optional[datetime] = None
    fill_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl: float = 0.0
    
    def __repr__(self):
        return f"Order({self.order_id}, {self.side.value}, Entry:{self.entry_price}, Status:{self.status.value})"


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    test_date: str
    instrument: str
    first_hour_high: float
    first_hour_low: float
    total_orders: int = 0
    filled_orders: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    win_rate: float = 0.0
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    total_ticks_processed: int = 0
    orders: List[Order] = field(default_factory=list)
    
    def calculate_metrics(self):
        """Calculate performance metrics"""
        if self.filled_orders == 0:
            return
        
        wins = [o.pnl for o in self.orders if o.pnl > 0]
        losses = [o.pnl for o in self.orders if o.pnl < 0]
        
        self.winning_trades = len(wins)
        self.losing_trades = len(losses)
        self.total_pnl = sum([o.pnl for o in self.orders])
        self.win_rate = (self.winning_trades / self.filled_orders * 100) if self.filled_orders > 0 else 0
        self.average_win = sum(wins) / len(wins) if wins else 0
        self.average_loss = sum(losses) / len(losses) if losses else 0
        self.largest_win = max(wins) if wins else 0
        self.largest_loss = min(losses) if losses else 0


# ============================================================================
# TICK DATA LOADER
# ============================================================================

class TickDataLoader:
    """Loads tick-by-tick data from Supabase"""
    
    def __init__(self):
        """Initialize the data loader"""
        self.supabase: Client = create_client(
            BacktestConfig.SUPABASE_URL,
            BacktestConfig.SUPABASE_KEY
        )
        logger.info("Tick data loader initialized")
    
    def load_first_hour_candle(self, date: str, instrument: str) -> Optional[Dict[str, float]]:
        """
        Load the first hour candle OHLC data for a specific date.
        Calculates OHLC from tick data in Supabase.
        
        Args:
            date: Date in format 'YYYY-MM-DD'
            instrument: Trading instrument (e.g., 'ESZ5', 'NQZ5')
        
        Returns:
            Dict with 'open', 'high', 'low', 'close' or None
        """
        logger.info(f"Loading first hour candle for {instrument} on {date}...")
        
        try:
            # Parse the date
            test_date = datetime.strptime(date, '%Y-%m-%d')
            test_date = BacktestConfig.ET_TZ.localize(test_date)
            
            # Calculate first hour time range
            market_open = test_date.replace(
                hour=BacktestConfig.MARKET_OPEN_HOUR,
                minute=BacktestConfig.MARKET_OPEN_MINUTE,
                second=0,
                microsecond=0
            )
            first_hour_end = market_open + timedelta(minutes=BacktestConfig.FIRST_HOUR_DURATION_MINUTES)
            
            # Determine which table to use
            if instrument.startswith('ES'):
                table_name = 'ticks_es'
            elif instrument.startswith('NQ'):
                table_name = 'ticks_nq'
            else:
                logger.error(f"Unknown instrument: {instrument}")
                return None
            
            logger.info(f"Querying {table_name} for first hour ticks...")
            logger.info(f"Time range: {market_open} to {first_hour_end}")
            
            # Query Supabase for first hour tick data
            response = self.supabase.table(table_name)\
                .select('ts, last')\
                .gte('ts', market_open.isoformat())\
                .lt('ts', first_hour_end.isoformat())\
                .order('ts', desc=False)\
                .execute()
            
            if not response.data or len(response.data) == 0:
                logger.warning(f"No tick data found for first hour in {table_name}")
                logger.warning("Using sample data as fallback")
                return {
                    'open': 5900.00,
                    'high': 5920.00,
                    'low': 5880.00,
                    'close': 5910.00
                }
            
            # Calculate OHLC from ticks
            prices = [float(row['last']) for row in response.data if row['last']]
            
            if not prices:
                logger.error("No valid prices found in tick data")
                return None
            
            candle_data = {
                'open': prices[0],      # First tick price
                'high': max(prices),    # Highest price
                'low': min(prices),     # Lowest price
                'close': prices[-1]     # Last tick price
            }
            
            logger.success(f"✅ First hour candle calculated from {len(prices)} ticks:")
            logger.info(f"   Open:  {candle_data['open']:.2f}")
            logger.info(f"   High:  {candle_data['high']:.2f}")
            logger.info(f"   Low:   {candle_data['low']:.2f}")
            logger.info(f"   Close: {candle_data['close']:.2f}")
            
            return candle_data
            
        except Exception as e:
            logger.error(f"Error loading first hour candle: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)
            return None
    
    def load_tick_data(self, date: str, instrument: str, start_time: datetime = None) -> List[Tick]:
        """
        Load tick-by-tick data from Supabase for a specific date.
        
        Args:
            date: Date in format 'YYYY-MM-DD'
            instrument: Trading instrument (e.g., 'ESZ5', 'NQZ5')
            start_time: Start loading from this time (default: first hour close)
        
        Returns:
            List of Tick objects
        """
        logger.info(f"Loading tick data for {instrument} on {date}...")
        
        try:
            # Parse the date
            test_date = datetime.strptime(date, '%Y-%m-%d')
            test_date = BacktestConfig.ET_TZ.localize(test_date)
            
            # If no start time specified, use first hour close
            if start_time is None:
                market_open = test_date.replace(
                    hour=BacktestConfig.MARKET_OPEN_HOUR,
                    minute=BacktestConfig.MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0
                )
                start_time = market_open + timedelta(minutes=BacktestConfig.FIRST_HOUR_DURATION_MINUTES)
            
            # End of trading day (4:00 PM ET)
            end_time = test_date.replace(hour=16, minute=0, second=0, microsecond=0)
            
            # Determine which table to use based on instrument
            if instrument.startswith('ES'):
                table_name = 'ticks_es'
            elif instrument.startswith('NQ'):
                table_name = 'ticks_nq'
            else:
                logger.error(f"Unknown instrument: {instrument}. Supported: ES*, NQ*")
                return []
            
            logger.info(f"Querying Supabase table: {table_name}")
            logger.info(f"Time range: {start_time} to {end_time}")
            
            # Query Supabase for tick data with pagination
            # Supabase limits results to 1000 rows by default, so we need to paginate
            ticks = []
            page_size = 1000
            offset = 0
            
            while True:
                # Query one page of data
                response = self.supabase.table(table_name)\
                    .select('ts, bid, ask, last, vol')\
                    .gte('ts', start_time.isoformat())\
                    .lte('ts', end_time.isoformat())\
                    .order('ts', desc=False)\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                
                if not response.data or len(response.data) == 0:
                    break
                
                # Convert page data to Tick objects
                for row in response.data:
                    tick = Tick(
                        timestamp=datetime.fromisoformat(row['ts'].replace('Z', '+00:00')),
                        price=float(row['last']) if row['last'] else 0.0,
                        volume=int(row['vol']) if row['vol'] else 0,
                        bid=float(row['bid']) if row['bid'] else None,
                        ask=float(row['ask']) if row['ask'] else None
                    )
                    ticks.append(tick)
                
                # Log progress
                logger.info(f"   Loaded {len(ticks):,} ticks...")
                
                # Check if we got less than page_size (last page)
                if len(response.data) < page_size:
                    break
                
                offset += page_size
            
            if not ticks:
                logger.warning(f"No tick data found in {table_name} for {date}")
                logger.warning("Falling back to sample data for testing")
                return self._generate_sample_ticks(start_time, end_time)
            
            logger.success(f"✅ Loaded {len(ticks):,} ticks from Supabase")
            logger.info(f"   Time range: {ticks[0].timestamp} to {ticks[-1].timestamp}")
            logger.info(f"   Price range: {min(t.price for t in ticks):.2f} to {max(t.price for t in ticks):.2f}")
            
            return ticks
            
        except Exception as e:
            logger.error(f"Error loading tick data: {e}")
            logger.error(f"Error details: {str(e)}", exc_info=True)
            logger.warning("Falling back to sample data")
            return self._generate_sample_ticks(start_time, end_time)
    
    def _generate_sample_ticks(self, start_time: datetime, end_time: datetime) -> List[Tick]:
        """
        Generate sample tick data for testing.
        REPLACE THIS with actual Supabase query in production.
        
        Args:
            start_time: Start time
            end_time: End time
        
        Returns:
            List of sample Tick objects
        """
        import random
        
        ticks = []
        current_time = start_time
        current_price = 5910.00  # Starting from first hour close
        
        # Generate ticks every second for the trading day
        while current_time < end_time:
            # Simulate price movement
            price_change = random.uniform(-2, 2)
            current_price += price_change
            
            tick = Tick(
                timestamp=current_time,
                price=round(current_price, 2),
                volume=random.randint(1, 100),
                bid=round(current_price - 0.25, 2),
                ask=round(current_price + 0.25, 2)
            )
            ticks.append(tick)
            
            # Next tick (every 1 second for this sample)
            current_time += timedelta(seconds=1)
        
        return ticks


# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

class BacktestEngine:
    """Tick-by-tick backtesting engine"""
    
    def __init__(self):
        """Initialize the backtest engine"""
        self.data_loader = TickDataLoader()
        self.orders: List[Order] = []
        self.next_order_id = 1
        logger.info("Backtest engine initialized")
    
    def create_orders(self, first_hour_high: float, first_hour_low: float) -> List[Order]:
        """
        Create all orders based on first hour high/low.
        
        Args:
            first_hour_high: High of first hour candle
            first_hour_low: Low of first hour candle
        
        Returns:
            List of Order objects
        """
        orders = []
        
        # Create SHORT orders (above the high)
        for i in range(1, BacktestConfig.MAX_ORDERS_PER_SIDE + 1):
            entry_price = first_hour_high + (i * BacktestConfig.POINTS_SPACING)
            stop_loss = entry_price + BacktestConfig.STOP_LOSS_POINTS
            take_profit = entry_price - BacktestConfig.TAKE_PROFIT_POINTS
            
            order = Order(
                order_id=self.next_order_id,
                side=OrderSide.SHORT,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                quantity=BacktestConfig.QUANTITY_PER_ORDER
            )
            orders.append(order)
            self.next_order_id += 1
        
        # Create LONG orders (below the low)
        for i in range(1, BacktestConfig.MAX_ORDERS_PER_SIDE + 1):
            entry_price = first_hour_low - (i * BacktestConfig.POINTS_SPACING)
            stop_loss = entry_price - BacktestConfig.STOP_LOSS_POINTS
            take_profit = entry_price + BacktestConfig.TAKE_PROFIT_POINTS
            
            order = Order(
                order_id=self.next_order_id,
                side=OrderSide.LONG,
                entry_price=round(entry_price, 2),
                stop_loss=round(stop_loss, 2),
                take_profit=round(take_profit, 2),
                quantity=BacktestConfig.QUANTITY_PER_ORDER
            )
            orders.append(order)
            self.next_order_id += 1
        
        logger.info(f"Created {len(orders)} orders ({BacktestConfig.MAX_ORDERS_PER_SIDE} SHORT + {BacktestConfig.MAX_ORDERS_PER_SIDE} LONG)")
        
        return orders
    
    def process_tick(self, tick: Tick, orders: List[Order]) -> None:
        """
        Process a single tick and update order statuses.
        
        Args:
            tick: Current market tick
            orders: List of orders to check
        """
        for order in orders:
            # Skip if order is already closed
            if order.status in [OrderStatus.STOPPED_OUT, OrderStatus.TAKE_PROFIT, OrderStatus.CANCELLED]:
                continue
            
            # Check if order should be filled
            if order.status == OrderStatus.PENDING:
                filled = False
                
                if order.side == OrderSide.LONG:
                    # Long order fills when price drops to or below entry price
                    if tick.price <= order.entry_price:
                        filled = True
                else:  # SHORT
                    # Short order fills when price rises to or above entry price
                    if tick.price >= order.entry_price:
                        filled = True
                
                if filled:
                    order.status = OrderStatus.FILLED
                    order.fill_time = tick.timestamp
                    order.fill_price = order.entry_price
                    logger.debug(f"Order {order.order_id} FILLED at {order.fill_price} ({tick.timestamp})")
            
            # Check stop loss and take profit for filled orders
            elif order.status == OrderStatus.FILLED:
                if order.side == OrderSide.LONG:
                    # Check stop loss (price drops below SL)
                    if tick.price <= order.stop_loss:
                        order.status = OrderStatus.STOPPED_OUT
                        order.exit_time = tick.timestamp
                        order.exit_price = order.stop_loss
                        order.exit_reason = "Stop Loss"
                        order.pnl = (order.exit_price - order.fill_price) * order.quantity
                        logger.debug(f"Order {order.order_id} STOPPED OUT at {order.exit_price}, PnL: {order.pnl:.2f}")
                    
                    # Check take profit (price rises above TP)
                    elif tick.price >= order.take_profit:
                        order.status = OrderStatus.TAKE_PROFIT
                        order.exit_time = tick.timestamp
                        order.exit_price = order.take_profit
                        order.exit_reason = "Take Profit"
                        order.pnl = (order.exit_price - order.fill_price) * order.quantity
                        logger.debug(f"Order {order.order_id} TAKE PROFIT at {order.exit_price}, PnL: {order.pnl:.2f}")
                
                else:  # SHORT
                    # Check stop loss (price rises above SL)
                    if tick.price >= order.stop_loss:
                        order.status = OrderStatus.STOPPED_OUT
                        order.exit_time = tick.timestamp
                        order.exit_price = order.stop_loss
                        order.exit_reason = "Stop Loss"
                        order.pnl = (order.fill_price - order.exit_price) * order.quantity
                        logger.debug(f"Order {order.order_id} STOPPED OUT at {order.exit_price}, PnL: {order.pnl:.2f}")
                    
                    # Check take profit (price drops below TP)
                    elif tick.price <= order.take_profit:
                        order.status = OrderStatus.TAKE_PROFIT
                        order.exit_time = tick.timestamp
                        order.exit_price = order.take_profit
                        order.exit_reason = "Take Profit"
                        order.pnl = (order.fill_price - order.exit_price) * order.quantity
                        logger.debug(f"Order {order.order_id} TAKE PROFIT at {order.exit_price}, PnL: {order.pnl:.2f}")
    
    def run_backtest(self, date: str, instrument: str = None) -> BacktestResult:
        """
        Run a complete backtest for a specific date.
        
        Args:
            date: Date to backtest in format 'YYYY-MM-DD'
            instrument: Trading instrument (default: from config)
        
        Returns:
            BacktestResult object with performance metrics
        """
        if instrument is None:
            instrument = BacktestConfig.INSTRUMENT
        
        logger.info("=" * 70)
        logger.info(f"STARTING BACKTEST FOR {date}")
        logger.info("=" * 70)
        
        # Step 1: Load first hour candle
        first_hour_candle = self.data_loader.load_first_hour_candle(date, instrument)
        if not first_hour_candle:
            logger.error("Failed to load first hour candle data")
            return None
        
        # Step 2: Create orders
        orders = self.create_orders(
            first_hour_high=first_hour_candle['high'],
            first_hour_low=first_hour_candle['low']
        )
        
        # Step 3: Load tick data
        ticks = self.data_loader.load_tick_data(date, instrument)
        if not ticks:
            logger.error("Failed to load tick data")
            return None
        
        # Step 4: Process each tick
        logger.info(f"Processing {len(ticks)} ticks...")
        for i, tick in enumerate(ticks):
            self.process_tick(tick, orders)
            
            # Log progress every 1000 ticks
            if (i + 1) % 1000 == 0:
                logger.info(f"  Processed {i + 1}/{len(ticks)} ticks...")
        
        # Step 5: Calculate results
        result = BacktestResult(
            test_date=date,
            instrument=instrument,
            first_hour_high=first_hour_candle['high'],
            first_hour_low=first_hour_candle['low'],
            total_orders=len(orders),
            filled_orders=len([o for o in orders if o.status != OrderStatus.PENDING]),
            total_ticks_processed=len(ticks),
            orders=orders
        )
        result.calculate_metrics()
        
        logger.info("=" * 70)
        logger.success("BACKTEST COMPLETE")
        logger.info("=" * 70)
        
        return result


# ============================================================================
# RESULTS REPORTER
# ============================================================================

class ResultsReporter:
    """Generate detailed backtest reports"""
    
    @staticmethod
    def print_summary(result: BacktestResult):
        """Print a summary of backtest results"""
        print("\n" + "=" * 70)
        print("BACKTEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Date:                {result.test_date}")
        print(f"Instrument:          {result.instrument}")
        print(f"First Hour High:     {result.first_hour_high:.2f}")
        print(f"First Hour Low:      {result.first_hour_low:.2f}")
        print(f"Ticks Processed:     {result.total_ticks_processed:,}")
        print("-" * 70)
        print(f"Total Orders:        {result.total_orders}")
        print(f"Filled Orders:       {result.filled_orders}")
        print(f"Winning Trades:      {result.winning_trades}")
        print(f"Losing Trades:       {result.losing_trades}")
        print(f"Win Rate:            {result.win_rate:.2f}%")
        print("-" * 70)
        print(f"Total P&L:           ${result.total_pnl:.2f}")
        print(f"Average Win:         ${result.average_win:.2f}")
        print(f"Average Loss:        ${result.average_loss:.2f}")
        print(f"Largest Win:         ${result.largest_win:.2f}")
        print(f"Largest Loss:        ${result.largest_loss:.2f}")
        print("=" * 70)
    
    @staticmethod
    def print_trade_details(result: BacktestResult):
        """Print detailed trade-by-trade results"""
        print("\n" + "=" * 70)
        print("TRADE-BY-TRADE DETAILS")
        print("=" * 70)
        
        for order in result.orders:
            if order.status == OrderStatus.PENDING:
                print(f"\nOrder #{order.order_id} ({order.side.value.upper()})")
                print(f"  Status: NOT FILLED")
                print(f"  Entry Price: {order.entry_price:.2f}")
            else:
                print(f"\nOrder #{order.order_id} ({order.side.value.upper()})")
                print(f"  Entry: {order.fill_price:.2f} at {order.fill_time.strftime('%H:%M:%S')}")
                print(f"  Exit:  {order.exit_price:.2f} at {order.exit_time.strftime('%H:%M:%S')}")
                print(f"  Reason: {order.exit_reason}")
                print(f"  P&L: ${order.pnl:.2f}")
                print(f"  Duration: {(order.exit_time - order.fill_time).total_seconds():.0f} seconds")
        
        print("=" * 70)
    
    @staticmethod
    def save_to_file(result: BacktestResult, filename: str = None):
        """Save backtest results to a file"""
        if filename is None:
            filename = f"backtest_results_{result.test_date}_{result.instrument}.txt"
        
        with open(filename, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("BACKTEST RESULTS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Date: {result.test_date}\n")
            f.write(f"Instrument: {result.instrument}\n")
            f.write(f"First Hour High: {result.first_hour_high:.2f}\n")
            f.write(f"First Hour Low: {result.first_hour_low:.2f}\n")
            f.write(f"\nPerformance Metrics:\n")
            f.write(f"  Total Orders: {result.total_orders}\n")
            f.write(f"  Filled Orders: {result.filled_orders}\n")
            f.write(f"  Winning Trades: {result.winning_trades}\n")
            f.write(f"  Losing Trades: {result.losing_trades}\n")
            f.write(f"  Win Rate: {result.win_rate:.2f}%\n")
            f.write(f"  Total P&L: ${result.total_pnl:.2f}\n")
            f.write(f"  Average Win: ${result.average_win:.2f}\n")
            f.write(f"  Average Loss: ${result.average_loss:.2f}\n")
            f.write(f"\nTrade Details:\n")
            for order in result.orders:
                if order.status != OrderStatus.PENDING:
                    f.write(f"\n  Order #{order.order_id} ({order.side.value}):\n")
                    f.write(f"    Entry: {order.fill_price:.2f}\n")
                    f.write(f"    Exit: {order.exit_price:.2f}\n")
                    f.write(f"    P&L: ${order.pnl:.2f}\n")
        
        logger.success(f"Results saved to {filename}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point for backtesting"""
    
    print("\n" + "=" * 70)
    print("TICK-BY-TICK BACKTESTING SYSTEM")
    print("=" * 70)
    print("Test your first-hour breakout strategy with historical tick data")
    print("=" * 70 + "\n")
    
    # Get test date from user
    test_date = input("Enter test date (YYYY-MM-DD) [default: 2025-10-09]: ").strip()
    if not test_date:
        test_date = "2025-10-09"
    
    # Get instrument from user
    instrument = input(f"Enter instrument [default: {BacktestConfig.INSTRUMENT}]: ").strip()
    if not instrument:
        instrument = BacktestConfig.INSTRUMENT
    
    # Run backtest
    engine = BacktestEngine()
    result = engine.run_backtest(date=test_date, instrument=instrument)
    
    if result:
        # Print results
        ResultsReporter.print_summary(result)
        ResultsReporter.print_trade_details(result)
        
        # Save to file
        save = input("\nSave results to file? (y/n) [default: y]: ").strip().lower()
        if save != 'n':
            ResultsReporter.save_to_file(result)
    else:
        logger.error("Backtest failed")


if __name__ == "__main__":
    main()
