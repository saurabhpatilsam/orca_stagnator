# First Hour Breakout Strategy - Complete Guide

## Strategy Overview

This automated trading strategy implements a first-hour breakout system for ES (E-mini S&P 500) and NQ (E-mini Nasdaq) futures contracts.

### Strategy Logic

1. **Wait for Market Open**: US market opens at 9:30 AM ET
2. **Mark First Hour Candle**: Record the high and low of the first 60-minute candle (9:30 AM - 10:30 AM ET)
3. **Place Orders**:
   - **SHORT Orders**: Every 9 points ABOVE the first hour high (max 5 orders)
   - **LONG Orders**: Every 9 points BELOW the first hour low (max 5 orders)
4. **Risk Management**: Each order has 5 points stop loss and 5 points take profit
5. **Quantity**: 1 contract per order

### Example

If the first hour candle has:
- **High**: 5920.00
- **Low**: 5880.00

**SHORT Orders** (above high):
1. Entry: 5929.00, SL: 5934.00, TP: 5924.00
2. Entry: 5938.00, SL: 5943.00, TP: 5933.00
3. Entry: 5947.00, SL: 5952.00, TP: 5942.00
4. Entry: 5956.00, SL: 5961.00, TP: 5951.00
5. Entry: 5965.00, SL: 5970.00, TP: 5960.00

**LONG Orders** (below low):
1. Entry: 5871.00, SL: 5866.00, TP: 5876.00
2. Entry: 5862.00, SL: 5857.00, TP: 5867.00
3. Entry: 5853.00, SL: 5848.00, TP: 5858.00
4. Entry: 5844.00, SL: 5839.00, TP: 5849.00
5. Entry: 5835.00, SL: 5830.00, TP: 5840.00

## Files

- `first_hour_breakout_strategy.py` - Main strategy implementation
- `strategy_config.py` - Configuration settings
- `send_trading_signal.py` - Sends signals to Supabase
- `supabase_order_listener.py` - Monitors Supabase and places orders

## Setup

### 1. Install Dependencies

```bash
pip install pytz loguru python-dotenv supabase
```

### 2. Configure Settings

Edit your `.env` file or `strategy_config.py`:

```bash
# Instrument
STRATEGY_INSTRUMENT=ESZ5  # ES December 2025

# Account
ACCOUNT_NAME=PAAPEX1361890000010

# Strategy Parameters
POINTS_SPACING=9
MAX_ORDERS_PER_SIDE=5
STOP_LOSS_POINTS=5
TAKE_PROFIT_POINTS=5
QUANTITY_PER_ORDER=1

# Mode
TEST_MODE=true  # Set to false for live trading
```

### 3. Ensure Order Listener is Running

The order listener must be running to automatically place orders:

```bash
python3 supabase_order_listener.py
```

## Usage

### Test Mode (Immediate Execution with Sample Data)

```bash
python3 first_hour_breakout_strategy.py
```

This will:
1. Use sample first-hour candle data
2. Calculate order levels
3. Send signals to Supabase
4. Order listener will attempt to place orders

### Production Mode (Wait for Market Open)

Edit `first_hour_breakout_strategy.py` and uncomment the production code in `main()`:

```python
def main():
    strategy = FirstHourBreakoutStrategy()
    
    # Comment out test mode:
    # strategy.run_once()
    
    # Uncomment production mode:
    logger.info("Waiting for first hour to close...")
    strategy.wait_for_first_hour_close()
    strategy.run_once()
```

Then run:
```bash
python3 first_hour_breakout_strategy.py
```

The strategy will:
1. Wait until 10:30 AM ET (first hour close)
2. Fetch the first hour candle data
3. Calculate and place all orders automatically

### Schedule for Daily Execution

#### Option 1: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line to run at 9:00 AM ET daily (before market open)
0 9 * * 1-5 cd /path/to/orca-ven-backend-main && /usr/bin/python3 first_hour_breakout_strategy.py >> strategy.log 2>&1
```

#### Option 2: systemd Timer (Linux)

Create `/etc/systemd/system/trading-strategy.service`:

```ini
[Unit]
Description=First Hour Breakout Trading Strategy
After=network.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/orca-ven-backend-main
ExecStart=/usr/bin/python3 first_hour_breakout_strategy.py
```

Create `/etc/systemd/system/trading-strategy.timer`:

```ini
[Unit]
Description=Run Trading Strategy Daily

[Timer]
OnCalendar=Mon-Fri 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable trading-strategy.timer
sudo systemctl start trading-strategy.timer
```

#### Option 3: Docker Container

Create `Dockerfile.strategy`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "first_hour_breakout_strategy.py"]
```

Run:
```bash
docker build -f Dockerfile.strategy -t trading-strategy .
docker run -d --name strategy --env-file .env trading-strategy
```

## Customization

### Change Instrument

```python
# In strategy_config.py or .env
STRATEGY_INSTRUMENT=NQZ5  # Switch to Nasdaq
```

### Adjust Points Spacing

```python
# In strategy_config.py
POINTS_SPACING = 12  # Change to 12 points instead of 9
```

### Modify Risk Management

```python
# In strategy_config.py
STOP_LOSS_POINTS = 10  # Wider stop loss
TAKE_PROFIT_POINTS = 15  # Larger profit target
```

### Change Number of Orders

```python
# In strategy_config.py
MAX_ORDERS_PER_SIDE = 3  # Only 3 orders per side instead of 5
```

## Integrating Real Market Data

Currently, the strategy uses sample data. To integrate real market data, you need to implement the `fetch_first_hour_candle()` method.

### Option 1: TradingView (Recommended)

```python
# Install tradingview-ta
pip install tradingview-ta

# In first_hour_breakout_strategy.py
from tradingview_ta import TA_Handler, Interval

def fetch_first_hour_candle(self) -> Optional[FirstHourCandle]:
    """Fetch first hour candle from TradingView"""
    try:
        handler = TA_Handler(
            symbol=self.config.INSTRUMENT,
            screener="america",
            exchange="CME",
            interval=Interval.INTERVAL_1_HOUR
        )
        
        analysis = handler.get_analysis()
        
        return FirstHourCandle(
            open_price=analysis.indicators['open'],
            high=analysis.indicators['high'],
            low=analysis.indicators['low'],
            close=analysis.indicators['close'],
            timestamp=datetime.now(pytz.timezone('US/Eastern'))
        )
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None
```

### Option 2: Interactive Brokers

```python
# Install ib_insync
pip install ib_insync

# In first_hour_breakout_strategy.py
from ib_insync import IB, Future

def fetch_first_hour_candle(self) -> Optional[FirstHourCandle]:
    """Fetch first hour candle from Interactive Brokers"""
    try:
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1)
        
        contract = Future(symbol='ES', lastTradeDateOrContractMonth='202512', exchange='CME')
        
        bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='1 D',
            barSizeSetting='1 hour',
            whatToShow='TRADES',
            useRTH=True
        )
        
        if bars:
            first_bar = bars[0]
            return FirstHourCandle(
                open_price=first_bar.open,
                high=first_bar.high,
                low=first_bar.low,
                close=first_bar.close,
                timestamp=first_bar.date
            )
        
        ib.disconnect()
        return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None
```

### Option 3: Manual Input

```python
def fetch_first_hour_candle(self) -> Optional[FirstHourCandle]:
    """Manual input of first hour candle"""
    print("\nEnter first hour candle data:")
    open_price = float(input("Open: "))
    high = float(input("High: "))
    low = float(input("Low: "))
    close = float(input("Close: "))
    
    return FirstHourCandle(
        open_price=open_price,
        high=high,
        low=low,
        close=close,
        timestamp=datetime.now(pytz.timezone('US/Eastern'))
    )
```

## Monitoring

### View Signals in Supabase

Go to your Supabase dashboard:
- https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock
- Click "Table Editor" → "trading_signals"

### Check Strategy Logs

```bash
tail -f strategy.log
```

### Monitor Order Placement

```bash
# Check order listener logs
tail -f order_listener.log

# Or if running in terminal
ps aux | grep supabase_order_listener
```

## Troubleshooting

### Orders Not Placing

1. **Check if order listener is running**:
   ```bash
   ps aux | grep supabase_order_listener
   ```

2. **Check Supabase for pending signals**:
   ```sql
   SELECT * FROM trading_signals WHERE status = 'pending';
   ```

3. **Check market hours**: Market must be open for orders to be accepted

### Data Fetching Issues

1. **Verify data provider connection**
2. **Check instrument symbol is correct** (ESZ5, NQZ5, etc.)
3. **Ensure market is open** when fetching data

### Configuration Errors

```bash
# Validate configuration
python3 strategy_config.py
```

## Risk Warning

⚠️ **IMPORTANT**: This is an automated trading system that places real orders. Always:

1. **Test thoroughly** in demo/paper trading first
2. **Start with small position sizes**
3. **Monitor the system** regularly
4. **Have a kill switch** to stop all orders
5. **Understand the risks** of automated trading

## Support

For issues or questions:
1. Check logs first
2. Review Supabase dashboard
3. Verify all services are running
4. Check market hours and conditions

---

**Ready to automate your trading!** 🚀
