# Tick-by-Tick Backtesting System - Complete Guide

## Overview

This backtesting system simulates your first-hour breakout strategy using **real tick-by-tick market data** from Supabase. Unlike candle-based backtesting, this provides **accurate fill simulation** by testing every single price tick.

## Features

✅ **Tick-by-Tick Precision** - Tests every price movement, not just candles  
✅ **Accurate Fill Simulation** - Realistic order fills based on actual price action  
✅ **Stop Loss & Take Profit Tracking** - Monitors SL/TP on every tick  
✅ **Detailed Performance Metrics** - Win rate, P&L, average win/loss  
✅ **Trade-by-Trade Analysis** - See exactly when and why each trade closed  
✅ **Historical Data from Supabase** - Uses your real market data  

## How It Works

### Step-by-Step Process

```
1. Load First Hour Candle (OHLC)
        ↓
2. Calculate Order Levels
   - 5 SHORT orders (every 9 points above high)
   - 5 LONG orders (every 9 points below low)
        ↓
3. Load Tick Data from Supabase
   - Starting from first hour close (10:30 AM)
   - Until market close (4:00 PM)
        ↓
4. Process Each Tick
   - Check if any orders should fill
   - Monitor filled orders for SL/TP
   - Update order status
        ↓
5. Calculate Performance Metrics
   - Win rate, P&L, average win/loss
   - Trade-by-trade details
```

### Order Fill Logic

**LONG Orders:**
- **Fill**: When price drops to or below entry price
- **Stop Loss**: When price drops to or below SL level
- **Take Profit**: When price rises to or above TP level

**SHORT Orders:**
- **Fill**: When price rises to or above entry price
- **Stop Loss**: When price rises to or above SL level
- **Take Profit**: When price drops to or below TP level

## Supabase Table Setup

### 1. Create Tick Data Table

Run this SQL in your Supabase SQL Editor:

```sql
-- Create tick_data table for storing historical tick data
CREATE TABLE IF NOT EXISTS tick_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    volume INTEGER DEFAULT 0,
    bid DECIMAL(12, 2),
    ask DECIMAL(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_tick_data_timestamp ON tick_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_tick_data_instrument ON tick_data(instrument);
CREATE INDEX IF NOT EXISTS idx_tick_data_instrument_timestamp ON tick_data(instrument, timestamp);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_tick_data_lookup ON tick_data(instrument, timestamp DESC);
```

### 2. Create OHLC/Candle Data Table (Optional)

```sql
-- Create ohlc_data table for storing candle data
CREATE TABLE IF NOT EXISTS ohlc_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    timeframe VARCHAR(20) NOT NULL, -- '1h', '5m', '1d', etc.
    open_price DECIMAL(12, 2) NOT NULL,
    high_price DECIMAL(12, 2) NOT NULL,
    low_price DECIMAL(12, 2) NOT NULL,
    close_price DECIMAL(12, 2) NOT NULL,
    volume INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(instrument, timestamp, timeframe)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp ON ohlc_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_ohlc_instrument ON ohlc_data(instrument);
CREATE INDEX IF NOT EXISTS idx_ohlc_lookup ON ohlc_data(instrument, timeframe, timestamp DESC);
```

## Usage

### Basic Usage

```bash
# Run the backtester
python3 backtest.py

# Enter test date when prompted
Enter test date (YYYY-MM-DD) [default: 2025-10-09]: 2025-10-09

# Enter instrument when prompted
Enter instrument [default: ESZ5]: ESZ5

# View results and save to file
```

### Programmatic Usage

```python
from backtest import BacktestEngine, ResultsReporter

# Initialize engine
engine = BacktestEngine()

# Run backtest for a specific date
result = engine.run_backtest(date="2025-10-09", instrument="ESZ5")

# Print results
ResultsReporter.print_summary(result)
ResultsReporter.print_trade_details(result)

# Save to file
ResultsReporter.save_to_file(result)
```

### Batch Testing Multiple Dates

```python
from backtest import BacktestEngine, ResultsReporter
from datetime import datetime, timedelta

engine = BacktestEngine()

# Test multiple dates
start_date = datetime(2025, 10, 1)
end_date = datetime(2025, 10, 31)

results = []
current_date = start_date

while current_date <= end_date:
    # Skip weekends
    if current_date.weekday() < 5:
        date_str = current_date.strftime('%Y-%m-%d')
        result = engine.run_backtest(date=date_str)
        if result:
            results.append(result)
    
    current_date += timedelta(days=1)

# Calculate aggregate statistics
total_pnl = sum(r.total_pnl for r in results)
avg_win_rate = sum(r.win_rate for r in results) / len(results)

print(f"Total P&L for October: ${total_pnl:.2f}")
print(f"Average Win Rate: {avg_win_rate:.2f}%")
```

## Integrating Real Tick Data

### Option 1: Import from CSV

```python
import pandas as pd
from supabase import create_client

# Load CSV with tick data
df = pd.read_csv('tick_data_2025-10-09.csv')

# Connect to Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Insert tick data
for _, row in df.iterrows():
    supabase.table('tick_data').insert({
        'timestamp': row['timestamp'],
        'instrument': row['instrument'],
        'price': row['price'],
        'volume': row['volume'],
        'bid': row['bid'],
        'ask': row['ask']
    }).execute()
```

### Option 2: Stream from Tradovate API

```python
# Real-time tick data collection (run during market hours)
from app.services.tradingview.broker import TradingViewTradovateBroker
import time

broker = TradingViewTradovateBroker(...)

while market_is_open():
    # Get current quote
    quote = broker.get_price_quotes("ESZ5")
    
    # Save to Supabase
    supabase.table('tick_data').insert({
        'timestamp': datetime.now(),
        'instrument': 'ESZ5',
        'price': quote['price'],
        'volume': quote.get('volume', 0),
        'bid': quote.get('bid'),
        'ask': quote.get('ask')
    }).execute()
    
    time.sleep(1)  # Collect tick every second
```

### Option 3: Import Historical Data

```python
# Download historical tick data from your broker
# Then bulk insert into Supabase

import json

# Load historical data
with open('historical_ticks.json', 'r') as f:
    ticks = json.load(f)

# Batch insert (more efficient)
batch_size = 1000
for i in range(0, len(ticks), batch_size):
    batch = ticks[i:i+batch_size]
    supabase.table('tick_data').insert(batch).execute()
```

## Example Output

### Summary Report

```
======================================================================
BACKTEST RESULTS SUMMARY
======================================================================
Date:                2025-10-09
Instrument:          ESZ5
First Hour High:     5920.00
First Hour Low:      5880.00
Ticks Processed:     19,800
----------------------------------------------------------------------
Total Orders:        10
Filled Orders:       7
Winning Trades:      4
Losing Trades:       3
Win Rate:            57.14%
----------------------------------------------------------------------
Total P&L:           $15.00
Average Win:         $5.00
Average Loss:        -$5.00
Largest Win:         $5.00
Largest Loss:        -$5.00
======================================================================
```

### Trade-by-Trade Details

```
======================================================================
TRADE-BY-TRADE DETAILS
======================================================================

Order #1 (SHORT)
  Entry: 5929.00 at 10:45:23
  Exit:  5924.00 at 10:52:15
  Reason: Take Profit
  P&L: $5.00
  Duration: 412 seconds

Order #2 (SHORT)
  Entry: 5938.00 at 11:15:45
  Exit:  5943.00 at 11:18:30
  Reason: Stop Loss
  P&L: -$5.00
  Duration: 165 seconds

Order #3 (LONG)
  Entry: 5871.00 at 13:22:10
  Exit:  5876.00 at 13:35:42
  Reason: Take Profit
  P&L: $5.00
  Duration: 812 seconds
```

## Performance Metrics Explained

| Metric | Description |
|--------|-------------|
| **Total Orders** | Number of orders placed (5 SHORT + 5 LONG) |
| **Filled Orders** | Orders that were executed |
| **Winning Trades** | Trades that hit take profit |
| **Losing Trades** | Trades that hit stop loss |
| **Win Rate** | Percentage of winning trades |
| **Total P&L** | Sum of all profits and losses |
| **Average Win** | Average profit per winning trade |
| **Average Loss** | Average loss per losing trade |
| **Largest Win** | Biggest single winning trade |
| **Largest Loss** | Biggest single losing trade |

## Customization

### Modify Strategy Parameters

Edit `backtest.py`:

```python
class BacktestConfig:
    POINTS_SPACING = 12  # Change to 12 points instead of 9
    MAX_ORDERS_PER_SIDE = 3  # Only 3 orders per side
    STOP_LOSS_POINTS = 10  # Wider stop loss
    TAKE_PROFIT_POINTS = 15  # Larger profit target
```

### Test Different Instruments

```python
# Test NQ instead of ES
result = engine.run_backtest(date="2025-10-09", instrument="NQZ5")
```

### Custom Time Range

Modify the `load_tick_data` method to load data for specific hours:

```python
# Only test afternoon session (12:00 PM - 4:00 PM)
start_time = test_date.replace(hour=12, minute=0)
end_time = test_date.replace(hour=16, minute=0)
```

## Troubleshooting

### Issue: "No tick data found"

**Solution**: Make sure you have tick data in Supabase for the test date.

```sql
-- Check if data exists
SELECT COUNT(*) FROM tick_data 
WHERE instrument = 'ESZ5' 
AND timestamp::date = '2025-10-09';
```

### Issue: "All orders remain unfilled"

**Possible Causes**:
1. Price never reached order levels
2. Tick data doesn't cover the full trading day
3. Order levels are too far from market

**Solution**: Check the first hour high/low and verify tick data range.

### Issue: "Backtest runs slowly"

**Solution**: 
1. Add database indexes (see SQL above)
2. Reduce tick frequency (use 1-second or 5-second ticks instead of every tick)
3. Limit time range

## Best Practices

1. **Use Real Data**: Always backtest with actual historical tick data
2. **Test Multiple Days**: Don't rely on a single day's results
3. **Account for Slippage**: Real fills may differ from backtest
4. **Consider Commissions**: Add trading costs to P&L calculations
5. **Validate Results**: Compare backtest results with live trading
6. **Keep Data Updated**: Regularly import new tick data

## Advanced Features

### Walk-Forward Analysis

Test strategy on rolling windows:

```python
# Train on 20 days, test on next 5 days
train_period = 20
test_period = 5

# Implement walk-forward optimization
# (optimize parameters on train period, test on test period)
```

### Monte Carlo Simulation

Randomize trade order to test robustness:

```python
import random

# Shuffle trade sequence
random.shuffle(orders)

# Run multiple simulations
for i in range(1000):
    # Randomize and test
    pass
```

### Optimization

Find best parameters:

```python
# Test different point spacings
for spacing in range(5, 15):
    BacktestConfig.POINTS_SPACING = spacing
    result = engine.run_backtest(date="2025-10-09")
    print(f"Spacing: {spacing}, P&L: {result.total_pnl}")
```

## Next Steps

1. ✅ Set up Supabase tick data table
2. ✅ Import historical tick data
3. ✅ Run backtest for a single day
4. ✅ Analyze results
5. ✅ Test multiple days
6. ✅ Optimize parameters
7. ✅ Compare with live trading results

---

**Ready to backtest your strategy with tick-by-tick precision!** 🚀
