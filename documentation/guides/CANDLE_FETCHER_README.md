# 📊 Automated Candle Data Fetcher

Automated system to fetch and store OHLC candle data from Tradovate into Supabase.

## 🎯 Features

✅ **Multiple Timeframes:**
- 5-minute candles
- 15-minute candles
- 30-minute candles
- 1-hour candles

✅ **Automated Fetching:**
- Runs continuously as a daemon
- Fetches data on schedule
- Auto-reconnects and refreshes tokens
- Stores in Supabase PostgreSQL

✅ **Data Storage:**
- Dedicated tables per timeframe
- Automatic duplicate handling (upsert)
- Indexed for fast queries
- Complete OHLC + volume data

---

## 🚀 Quick Start

### Step 1: Create Supabase Tables

```bash
# Copy SQL to Supabase SQL Editor and run it
cat supabase_candle_tables.sql
```

Or manually run in Supabase Dashboard:
1. Go to SQL Editor
2. Paste contents of `supabase_candle_tables.sql`
3. Click "Run"

### Step 2: Set Environment Variables

```bash
export SUPABASE_URL="your-supabase-url"
export SUPABASE_SERVICE_KEY="your-service-key"
```

Or create a `.env` file:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 3: Install Dependencies

```bash
pip install supabase schedule loguru websocket-client
```

### Step 4: Run the Fetcher

**Test Mode (run once):**
```bash
python3 automated_candle_fetcher.py --manual
```

**Daemon Mode (continuous):**
```bash
python3 automated_candle_fetcher.py --daemon
```

Or simply:
```bash
python3 automated_candle_fetcher.py
```

---

## 📋 How It Works

### Architecture

```
┌─────────────────┐
│   Tradovate     │
│   WebSocket     │
│   (Live Data)   │
└────────┬────────┘
         │
         │ Fetch OHLC
         │ Every N minutes
         ▼
┌─────────────────┐
│  Python Script  │
│   - 5min data   │
│   - 15min data  │
│   - 30min data  │
│   - 1hour data  │
└────────┬────────┘
         │
         │ Store
         ▼
┌─────────────────┐
│   Supabase DB   │
│  (PostgreSQL)   │
│   - Historical  │
│   - Queryable   │
└─────────────────┘
```

### Fetch Schedule

| Timeframe | Frequency | Records/Fetch |
|-----------|-----------|---------------|
| 5 min     | Every 5 min | 50 bars |
| 15 min    | Every 15 min | 50 bars |
| 30 min    | Every 30 min | 50 bars |
| 1 hour    | Every 1 hour | 50 bars |

### Data Flow

1. **Connect to Tradovate**
   - Get token from Redis
   - Renew to get MD token
   - Connect WebSocket
   - Authorize

2. **Fetch Candle Data**
   - Request historical bars
   - Parse OHLC data
   - Extract volume metrics

3. **Store in Supabase**
   - Insert into appropriate table
   - Handle duplicates (upsert)
   - Index for fast queries

4. **Repeat**
   - Schedule runs automatically
   - Reconnects if disconnected
   - Refreshes tokens every 4 hours

---

## 📊 Database Schema

### Tables Created

```sql
orca.nq_candles_5min
orca.nq_candles_15min
orca.nq_candles_30min
orca.nq_candles_1hour
```

### Table Structure

```sql
CREATE TABLE orca.nq_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);
```

---

## 🔍 Querying Data

### Get Latest 50 Candles

```sql
SELECT * FROM orca.get_latest_candles('5min', 'NQZ5', 50);
SELECT * FROM orca.get_latest_candles('30min', 'NQZ5', 50);
```

### Get Candles in Time Range

```sql
SELECT * FROM orca.get_candles_range(
    '30min',
    'NQZ5',
    '2025-10-15 14:00:00+00',
    '2025-10-15 18:00:00+00'
);
```

### Direct Query

```sql
-- Latest 10 5-minute candles
SELECT candle_time, open, high, low, close, volume
FROM orca.nq_candles_5min
WHERE symbol = 'NQZ5'
ORDER BY candle_time DESC
LIMIT 10;

-- Average close price for last hour
SELECT AVG(close) as avg_close
FROM orca.nq_candles_5min
WHERE symbol = 'NQZ5'
AND candle_time >= NOW() - INTERVAL '1 hour';
```

### Python Query

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get latest 30-min candles
result = supabase.schema("orca").table("nq_candles_30min").select(
    "candle_time, open, high, low, close, volume"
).eq("symbol", "NQZ5").order("candle_time", desc=True).limit(10).execute()

candles = result.data
for candle in candles:
    print(f"{candle['candle_time']}: Close ${candle['close']}")
```

---

## 🛠️ Running as System Service

### Create Systemd Service (Linux)

```bash
sudo nano /etc/systemd/system/candle-fetcher.service
```

```ini
[Unit]
Description=NQ Candle Data Fetcher
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/orca-ven-backend-main
Environment="SUPABASE_URL=your-url"
Environment="SUPABASE_SERVICE_KEY=your-key"
ExecStart=/usr/bin/python3 /path/to/automated_candle_fetcher.py --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable candle-fetcher
sudo systemctl start candle-fetcher

# Check status
sudo systemctl status candle-fetcher

# View logs
sudo journalctl -u candle-fetcher -f
```

### Using Screen (Alternative)

```bash
# Start in screen
screen -S candle-fetcher
python3 automated_candle_fetcher.py --daemon

# Detach: Ctrl+A then D

# Reattach
screen -r candle-fetcher
```

### Using nohup (Alternative)

```bash
nohup python3 automated_candle_fetcher.py --daemon > candle_fetcher.log 2>&1 &

# Check logs
tail -f candle_fetcher.log
```

---

## 📈 Monitoring

### Check Logs

```python
# Script outputs logs with loguru
# Shows:
# - Connection status
# - Fetch operations
# - Storage results
# - Errors

# Example output:
# 2025-10-15 18:00:00 | INFO | Fetching 5min candles...
# 2025-10-15 18:00:05 | SUCCESS | ✅ Stored 50 candles in nq_candles_5min
# 2025-10-15 18:00:05 | INFO | Last 5min candle: 2025-10-15 16:00:00 - Close: $24,959.50
```

### Check Data in Supabase

```sql
-- Count records per timeframe
SELECT 'nq_candles_5min' as table_name, COUNT(*) as total_records
FROM orca.nq_candles_5min
UNION ALL
SELECT 'nq_candles_15min', COUNT(*)
FROM orca.nq_candles_15min
UNION ALL
SELECT 'nq_candles_30min', COUNT(*)
FROM orca.nq_candles_30min
UNION ALL
SELECT 'nq_candles_1hour', COUNT(*)
FROM orca.nq_candles_1hour;

-- Latest candle per timeframe
SELECT '5min' as timeframe, MAX(candle_time) as latest_candle
FROM orca.nq_candles_5min
UNION ALL
SELECT '15min', MAX(candle_time)
FROM orca.nq_candles_15min
UNION ALL
SELECT '30min', MAX(candle_time)
FROM orca.nq_candles_30min
UNION ALL
SELECT '1hour', MAX(candle_time)
FROM orca.nq_candles_1hour;
```

---

## ⚠️ Troubleshooting

### Issue: "No token found"

**Solution:** Ensure Redis has valid Tradovate tokens
```bash
python3 scripts/get_trading_token.py
```

### Issue: "Supabase credentials not found"

**Solution:** Set environment variables
```bash
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"
```

### Issue: "Table does not exist"

**Solution:** Run the SQL schema creation
```bash
# Copy and run supabase_candle_tables.sql in Supabase SQL Editor
```

### Issue: "WebSocket connection failed"

**Possible causes:**
- Network issues
- Token expired
- Demo environment down

**Solution:** Check logs and retry

### Issue: "Duplicate key error"

**Solution:** The script uses upsert, but if you see this:
```sql
-- Delete duplicates manually
DELETE FROM orca.nq_candles_5min a
USING orca.nq_candles_5min b
WHERE a.id > b.id
AND a.symbol = b.symbol
AND a.candle_time = b.candle_time;
```

---

## 🎯 Use Cases

### 1. Historical Analysis

```python
# Get last 100 30-minute candles for backtesting
result = supabase.schema("orca").table("nq_candles_30min").select("*").eq(
    "symbol", "NQZ5"
).order("candle_time", desc=True).limit(100).execute()

candles = result.data
# Analyze patterns, calculate indicators, etc.
```

### 2. Real-time Trading Signals

```python
# Get latest 5-minute candle
result = supabase.schema("orca").table("nq_candles_5min").select("*").eq(
    "symbol", "NQZ5"
).order("candle_time", desc=True).limit(1).execute()

latest_candle = result.data[0]
if latest_candle['close'] > latest_candle['open']:
    print("Bullish candle - Consider long")
```

### 3. Data Export

```python
import pandas as pd

# Export to CSV for analysis
result = supabase.schema("orca").table("nq_candles_30min").select("*").eq(
    "symbol", "NQZ5"
).execute()

df = pd.DataFrame(result.data)
df.to_csv('nq_30min_candles.csv', index=False)
```

---

## 📝 Summary

✅ **Created:**
- `supabase_candle_tables.sql` - Database schema
- `automated_candle_fetcher.py` - Fetcher script
- `CANDLE_FETCHER_README.md` - This guide

✅ **Features:**
- Automated fetching every 5/15/30/60 minutes
- Stores in Supabase PostgreSQL
- Handles reconnection & token refresh
- Ready for production use

✅ **Next Steps:**
1. Run SQL schema in Supabase
2. Set environment variables
3. Start the fetcher
4. Query your data!

🚀 **Happy Trading!**
