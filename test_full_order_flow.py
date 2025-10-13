"""
End-to-End Order Placement Test
================================
This script tests the complete order flow:
1. Fetch October 9th ES data from Supabase
2. Calculate first hour HIGH/LOW
3. Generate orders based on strategy
4. Insert orders into Supabase trading_signals table
5. Order listener will automatically try to place them

Author: Automated Trading System
Date: 2025-10-12
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import uuid
from loguru import logger
from supabase import create_client, Client
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Strategy parameters
POINTS_SPACING = 9
MAX_ORDERS_PER_SIDE = 5
STOP_LOSS_POINTS = 5
TAKE_PROFIT_POINTS = 5
QUANTITY_PER_ORDER = 1

# Timezone
ET_TZ = pytz.timezone('US/Eastern')


def get_first_hour_candle(supabase: Client, date: str) -> Dict:
    """
    Get first hour candle for October 9, 2025.
    
    Args:
        supabase: Supabase client
        date: Date string (YYYY-MM-DD)
    
    Returns:
        Dict with open, high, low, close
    """
    logger.info(f"Fetching first hour candle for {date}...")
    
    # Parse date
    test_date = datetime.strptime(date, '%Y-%m-%d')
    test_date = ET_TZ.localize(test_date)
    
    # First hour: 9:30 AM - 10:30 AM ET
    market_open = test_date.replace(hour=9, minute=30, second=0, microsecond=0)
    first_hour_end = market_open + timedelta(hours=1)
    
    logger.info(f"Time range: {market_open} to {first_hour_end}")
    
    # Query Supabase for first hour ticks
    response = supabase.table('ticks_es')\
        .select('ts, last')\
        .gte('ts', market_open.isoformat())\
        .lt('ts', first_hour_end.isoformat())\
        .order('ts', desc=False)\
        .limit(10000)\
        .execute()
    
    if not response.data or len(response.data) == 0:
        logger.error("No data found for first hour")
        return None
    
    # Calculate OHLC
    prices = [float(row['last']) for row in response.data if row['last']]
    
    candle = {
        'open': prices[0],
        'high': max(prices),
        'low': min(prices),
        'close': prices[-1]
    }
    
    logger.success(f"✅ First hour candle calculated from {len(prices)} ticks:")
    logger.info(f"   Open:  {candle['open']:.2f}")
    logger.info(f"   High:  {candle['high']:.2f}")
    logger.info(f"   Low:   {candle['low']:.2f}")
    logger.info(f"   Close: {candle['close']:.2f}")
    
    return candle


def generate_orders(first_hour_high: float, first_hour_low: float) -> List[Dict]:
    """
    Generate orders based on first-hour breakout strategy.
    
    Args:
        first_hour_high: High of first hour
        first_hour_low: Low of first hour
    
    Returns:
        List of order dictionaries
    """
    logger.info("Generating orders based on strategy...")
    
    orders = []
    
    # Generate SHORT orders (above the high)
    for i in range(1, MAX_ORDERS_PER_SIDE + 1):
        entry_price = first_hour_high + (i * POINTS_SPACING)
        stop_loss = entry_price + STOP_LOSS_POINTS
        take_profit = entry_price - TAKE_PROFIT_POINTS
        
        order = {
            'signal_id': f'test_short_{i}_{uuid.uuid4().hex[:8]}',
            'strategy_name': 'first_hour_breakout',
            'instrument': 'ESZ5',
            'side': 'sell',
            'quantity': QUANTITY_PER_ORDER,
            'price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'order_type': 'limit',
            'account_name': 'demo_account',
            'status': 'pending'
        }
        orders.append(order)
        logger.info(f"  SHORT Order {i}: Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
    
    # Generate LONG orders (below the low)
    for i in range(1, MAX_ORDERS_PER_SIDE + 1):
        entry_price = first_hour_low - (i * POINTS_SPACING)
        stop_loss = entry_price - STOP_LOSS_POINTS
        take_profit = entry_price + TAKE_PROFIT_POINTS
        
        order = {
            'signal_id': f'test_long_{i}_{uuid.uuid4().hex[:8]}',
            'strategy_name': 'first_hour_breakout',
            'instrument': 'ESZ5',
            'side': 'buy',
            'quantity': QUANTITY_PER_ORDER,
            'price': round(entry_price, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': round(take_profit, 2),
            'order_type': 'limit',
            'account_name': 'demo_account',
            'status': 'pending'
        }
        orders.append(order)
        logger.info(f"  LONG Order {i}: Entry={entry_price:.2f}, SL={stop_loss:.2f}, TP={take_profit:.2f}")
    
    logger.success(f"✅ Generated {len(orders)} orders ({MAX_ORDERS_PER_SIDE} SHORT + {MAX_ORDERS_PER_SIDE} LONG)")
    
    return orders


def insert_orders_to_supabase(supabase: Client, orders: List[Dict]) -> bool:
    """
    Insert orders into Supabase trading_signals table.
    
    Args:
        supabase: Supabase client
        orders: List of order dictionaries
    
    Returns:
        True if successful
    """
    logger.info(f"Inserting {len(orders)} orders into Supabase...")
    
    try:
        response = supabase.table('trading_signals').insert(orders).execute()
        
        logger.success(f"✅ Successfully inserted {len(orders)} orders into trading_signals table")
        logger.info("Orders are now in Supabase and will be picked up by the order listener")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inserting orders: {e}")
        return False


def main():
    """Main execution"""
    
    print("\n" + "=" * 70)
    print("END-TO-END ORDER PLACEMENT TEST")
    print("=" * 70)
    print("Testing complete flow: Data → Strategy → Supabase → Tradovate API")
    print("=" * 70 + "\n")
    
    # Initialize Supabase
    logger.info("Initializing Supabase client...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.success("✅ Supabase client initialized")
    
    # Step 1: Get first hour candle for October 9, 2025
    logger.info("\n" + "=" * 70)
    logger.info("STEP 1: Fetch October 9th ES Data")
    logger.info("=" * 70)
    
    candle = get_first_hour_candle(supabase, '2025-10-09')
    
    if not candle:
        logger.error("Failed to get first hour candle")
        return
    
    # Step 2: Generate orders based on strategy
    logger.info("\n" + "=" * 70)
    logger.info("STEP 2: Generate Orders Based on Strategy")
    logger.info("=" * 70)
    
    orders = generate_orders(candle['high'], candle['low'])
    
    # Step 3: Insert orders into Supabase
    logger.info("\n" + "=" * 70)
    logger.info("STEP 3: Insert Orders into Supabase")
    logger.info("=" * 70)
    
    success = insert_orders_to_supabase(supabase, orders)
    
    if success:
        logger.info("\n" + "=" * 70)
        logger.success("TEST COMPLETE!")
        logger.info("=" * 70)
        logger.info("Next steps:")
        logger.info("1. ✅ Orders are now in Supabase trading_signals table")
        logger.info("2. 🔄 Order listener will automatically pick them up")
        logger.info("3. 📡 Listener will try to place orders via Tradovate API")
        logger.info("4. ⚠️  Orders will fail (market closed) but we'll see the error")
        logger.info("5. 📝 Check order_history table for placement attempts")
        logger.info("\nTo monitor:")
        logger.info("  - Check Supabase trading_signals table")
        logger.info("  - Check Supabase order_history table")
        logger.info("  - Run order listener: python3 supabase_order_listener.py")
        logger.info("=" * 70)
    else:
        logger.error("Failed to insert orders")


if __name__ == "__main__":
    main()
