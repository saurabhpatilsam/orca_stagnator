# Supabase Trading Signal Integration - Setup Guide

## Overview

This integration allows you to:
1. **Send trading signals** from your Python strategies (running anywhere, including Docker containers)
2. **Automatically place orders** on Tradovate when signals are received
3. **Track order status** and history in Supabase

## Architecture

```
┌─────────────────────┐
│  Trading Strategy   │
│  (Python/Docker)    │
└──────────┬──────────┘
           │ sends signal
           ▼
┌─────────────────────┐
│     Supabase        │
│  trading_signals    │
│      table          │
└──────────┬──────────┘
           │ real-time polling
           ▼
┌─────────────────────┐
│  Order Listener     │
│    Service          │
└──────────┬──────────┘
           │ places order
           ▼
┌─────────────────────┐
│  Tradovate API      │
│   (via Redis)       │
└─────────────────────┘
```

## Setup Instructions

### Step 1: Set Up Supabase Database

1. **Go to your Supabase project** at https://supabase.com
2. **Navigate to SQL Editor**
3. **Copy and paste** the contents of `supabase_setup.sql`
4. **Run the SQL script** to create tables and triggers

This will create:
- `trading_signals` table - stores all trading signals
- `order_history` table - tracks order events
- Indexes for performance
- Triggers for auto-updating timestamps

### Step 2: Get Supabase Credentials

1. Go to **Project Settings** → **API**
2. Copy the following:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

### Step 3: Configure Environment Variables

Create or update your `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here

# Tradovate API Configuration
TRADING_API_BASE=https://tv-demo.tradovateapi.com
POLL_INTERVAL=2  # How often to check for new signals (seconds)

# Redis Configuration (already configured)
REDIS_HOST=redismanager.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=your_redis_password
```

### Step 4: Install Python Dependencies

```bash
pip install supabase python-dotenv loguru
```

### Step 5: Test the Setup

#### Test 1: Send a Test Signal

```bash
python3 send_trading_signal.py
```

This will send a test signal to Supabase. Check your Supabase dashboard to verify it appears in the `trading_signals` table.

#### Test 2: Start the Order Listener

```bash
python3 supabase_order_listener.py
```

This will start the service that monitors Supabase and places orders. Keep it running in a terminal.

#### Test 3: Send a Signal and Watch It Execute

In another terminal:
```bash
python3 send_trading_signal.py
```

You should see the listener pick up the signal and attempt to place the order!

## Usage Examples

### Example 1: Send Signal from Your Strategy

```python
from send_trading_signal import TradingSignalSender

# Initialize sender
sender = TradingSignalSender()

# Send a buy signal
result = sender.send_signal(
    instrument="MNQZ5",
    side="buy",
    quantity=1,
    strategy_name="my_strategy",
    order_type="limit",
    price=21000.0,
    stop_loss=20900.0,
    take_profit=21100.0,
    metadata={
        "indicator": "RSI",
        "value": 35
    }
)

if result["success"]:
    print(f"Signal sent: {result['signal_id']}")
```

### Example 2: Use in Docker Container

```python
# In your Docker container strategy
import os
from send_trading_signal import TradingSignalSender

# Make sure SUPABASE_URL and SUPABASE_KEY are set in Docker environment
sender = TradingSignalSender()

# When your strategy detects a signal
if trading_condition_met:
    sender.send_signal(
        instrument="MNQZ5",
        side="buy",
        quantity=1,
        strategy_name="docker_strategy",
        order_type="market"
    )
```

### Example 3: Check Signal Status

```python
from send_trading_signal import TradingSignalSender

sender = TradingSignalSender()

# Check status of a signal
status = sender.get_signal_status("your_signal_id")
print(f"Status: {status['status']}")
print(f"Tradovate Order ID: {status.get('tradovate_order_id')}")
```

## Running as a Service

### Option 1: Run in Terminal (Development)

```bash
python3 supabase_order_listener.py
```

### Option 2: Run with nohup (Background)

```bash
nohup python3 supabase_order_listener.py > order_listener.log 2>&1 &
```

### Option 3: Run as systemd Service (Production Linux)

Create `/etc/systemd/system/supabase-order-listener.service`:

```ini
[Unit]
Description=Supabase Order Listener Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/orca-ven-backend-main
ExecStart=/usr/bin/python3 supabase_order_listener.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable supabase-order-listener
sudo systemctl start supabase-order-listener
sudo systemctl status supabase-order-listener
```

### Option 4: Run in Docker

Create `Dockerfile.listener`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "supabase_order_listener.py"]
```

Build and run:
```bash
docker build -f Dockerfile.listener -t order-listener .
docker run -d --name order-listener --env-file .env order-listener
```

## Monitoring and Debugging

### View Logs

```bash
# If running in terminal, logs appear in console

# If running with nohup
tail -f order_listener.log

# If running as systemd service
sudo journalctl -u supabase-order-listener -f
```

### Check Supabase Tables

```sql
-- View all signals
SELECT * FROM trading_signals ORDER BY created_at DESC LIMIT 10;

-- View pending signals
SELECT * FROM active_signals;

-- View order history for a signal
SELECT * FROM order_history 
WHERE signal_id = 'your-signal-uuid' 
ORDER BY created_at DESC;

-- View failed orders
SELECT * FROM trading_signals 
WHERE status = 'failed' 
ORDER BY created_at DESC;
```

### Common Issues and Solutions

#### Issue: "Missing Supabase credentials"
**Solution**: Make sure `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`

#### Issue: "Failed to connect to Redis"
**Solution**: Check Redis credentials in `.env` and ensure Redis is accessible

#### Issue: "Order modification rejected"
**Solution**: 
- Check if market is open
- Verify price is close to current market price
- Ensure instrument symbol is correct (e.g., MNQZ5 for current quarter)

#### Issue: Signals not being processed
**Solution**:
- Check if `supabase_order_listener.py` is running
- Verify signal status is 'pending' in Supabase
- Check listener logs for errors

## Database Schema

### trading_signals Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| signal_id | VARCHAR | Unique signal identifier |
| strategy_name | VARCHAR | Name of strategy |
| instrument | VARCHAR | Trading instrument |
| side | VARCHAR | 'buy' or 'sell' |
| order_type | VARCHAR | 'market', 'limit', or 'stop' |
| quantity | INTEGER | Order quantity |
| price | DECIMAL | Limit price |
| stop_loss | DECIMAL | Stop loss price |
| take_profit | DECIMAL | Take profit price |
| account_name | VARCHAR | Tradovate account name |
| account_id | VARCHAR | Tradovate account ID |
| status | VARCHAR | 'pending', 'processing', 'placed', 'failed', 'cancelled' |
| tradovate_order_id | VARCHAR | Order ID from Tradovate |
| error_message | TEXT | Error if placement failed |
| metadata | JSONB | Additional strategy data |
| created_at | TIMESTAMP | When signal was created |
| updated_at | TIMESTAMP | Last update time |

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use Row Level Security (RLS)** in Supabase for production
3. **Rotate API keys** regularly
4. **Monitor failed orders** for suspicious activity
5. **Set up alerts** for unusual trading patterns

## Next Steps

1. ✅ Complete setup steps above
2. ✅ Test with demo account
3. ✅ Monitor for a few days
4. ✅ Switch to live account when confident
5. ✅ Set up monitoring and alerts
6. ✅ Implement additional risk management

## Support

For issues or questions:
- Check logs first
- Review Supabase dashboard
- Verify Tradovate API status
- Check Redis connection

## Files Reference

- `supabase_setup.sql` - Database schema and setup
- `send_trading_signal.py` - Send signals from strategies
- `supabase_order_listener.py` - Background service for order placement
- `place_order_production.py` - Direct order placement (for testing)
- `SUPABASE_SETUP_GUIDE.md` - This file

---

**Ready to start automated trading!** 🚀
