# 🚀 Quick Setup Guide - Candle Data Fetcher

## ✅ **Step 1: Create Tables in Supabase** (2 minutes)

### Go to Supabase Dashboard:
1. Open [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Select your project
3. Click **SQL Editor** in the left sidebar
4. Click **New Query**

### Copy and Run SQL:
```bash
# Open the SQL file in your terminal
cat create_candle_tables_simple.sql
```

Or manually copy the contents of **`create_candle_tables_simple.sql`** and paste into Supabase SQL Editor, then click **RUN**.

### Expected Result:
You should see:
```
Success. No rows returned
```

This creates 4 tables:
- ✅ `orca.nq_candles_5min`
- ✅ `orca.nq_candles_15min`
- ✅ `orca.nq_candles_30min`
- ✅ `orca.nq_candles_1hour`

---

## ✅ **Step 2: Verify Your .env File** (1 minute)

Make sure your `.env` file has these variables:

```bash
# Check if they exist
cat .env | grep SUPABASE
```

Should show:
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

If missing, add them to your `.env` file:
1. Get SUPABASE_URL from: Supabase Dashboard → Settings → API → Project URL
2. Get SUPABASE_ANON_KEY from: Supabase Dashboard → Settings → API → Project API keys → anon/public

---

## ✅ **Step 3: Test the Fetcher** (30 seconds)

Run a manual test:

```bash
python3 automated_candle_fetcher.py --manual
```

### Expected Output:
```
2025-10-15 19:13:11 | INFO | Loaded environment variables from .env file
======================================================================
Initializing Tradovate connection...
======================================================================
Trying account: APEX_266668
Getting tokens for APEX_266668...
MD access token obtained
Discovering current NQ contract...
Using contract: NQZ5
Connecting to Tradovate WebSocket...
WebSocket opened
WebSocket authorized
✅ Connected to Tradovate using APEX_266668
======================================================================
🔄 Fetching all timeframes - 2025-10-15 19:13:15
======================================================================
📊 Fetching 5min candles...
Received 50 5min bars
✅ Stored 50 candles in nq_candles_5min
Last 5min candle: 2025-10-15 16:00:00 - Close: $24,959.50
📊 Fetching 15min candles...
Received 50 15min bars
✅ Stored 50 candles in nq_candles_15min
📊 Fetching 30min candles...
Received 50 30min bars
✅ Stored 50 candles in nq_candles_30min
📊 Fetching 1hour candles...
Received 50 1hour bars
✅ Stored 50 candles in nq_candles_1hour
======================================================================
✅ Completed fetching all timeframes
======================================================================
```

---

## ✅ **Step 4: Verify Data in Supabase** (30 seconds)

Go to Supabase → Table Editor → Schema: orca

You should see 4 new tables with data:
- `nq_candles_5min` → 50 rows
- `nq_candles_15min` → 50 rows
- `nq_candles_30min` → 50 rows
- `nq_candles_1hour` → 50 rows

Or run this SQL query:
```sql
SELECT 
    'nq_candles_5min' as table_name, 
    COUNT(*) as total_records
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
```

---

## ✅ **Step 5: Run as Daemon** (Continuous)

Once the test works, run it continuously:

```bash
python3 automated_candle_fetcher.py --daemon
```

Or simply:
```bash
python3 automated_candle_fetcher.py
```

### What Happens:
- Fetches 5-minute candles every 5 minutes
- Fetches 15-minute candles every 15 minutes
- Fetches 30-minute candles every 30 minutes
- Fetches 1-hour candles every 1 hour
- Auto-reconnects if connection drops
- Refreshes tokens every 4 hours

### To Run in Background:
```bash
# Option 1: Using screen
screen -S candle-fetcher
python3 automated_candle_fetcher.py
# Press Ctrl+A then D to detach

# Option 2: Using nohup
nohup python3 automated_candle_fetcher.py > candle_fetcher.log 2>&1 &

# Check logs
tail -f candle_fetcher.log
```

---

## 📊 **Quick Data Queries**

### Get Latest 10 Candles (30-min):
```sql
SELECT candle_time, open, high, low, close, volume
FROM orca.nq_candles_30min
WHERE symbol = 'NQZ5'
ORDER BY candle_time DESC
LIMIT 10;
```

### Get Last Hour of 5-min Candles:
```sql
SELECT candle_time, open, high, low, close
FROM orca.nq_candles_5min
WHERE symbol = 'NQZ5'
AND candle_time >= NOW() - INTERVAL '1 hour'
ORDER BY candle_time ASC;
```

### Python Query:
```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Get latest 30-min candles
result = supabase.schema("orca").table("nq_candles_30min").select(
    "candle_time, open, high, low, close, volume"
).eq("symbol", "NQZ5").order("candle_time", desc=True).limit(10).execute()

for candle in result.data:
    print(f"{candle['candle_time']}: ${candle['close']}")
```

---

## ⚠️ **Troubleshooting**

### "Supabase credentials not found"
- Check `.env` file has `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Make sure there are no spaces around the `=` sign
- Ensure keys are not quoted (unless they contain spaces)

### "No token found in Redis"
```bash
python3 scripts/get_trading_token.py
```

### "Table does not exist"
- Run `create_candle_tables_simple.sql` in Supabase SQL Editor
- Make sure you're in the correct schema (`orca`)

### Check if tables exist:
```sql
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'orca' 
AND table_name LIKE 'nq_candles%';
```

---

## 🎯 **Summary**

**What You Created:**
1. ✅ 4 Supabase tables for candle storage
2. ✅ Automated fetcher that runs on schedule
3. ✅ Complete OHLC data with volume metrics

**What Happens Automatically:**
- Every 5 min: Fetches and stores 50 x 5-min candles
- Every 15 min: Fetches and stores 50 x 15-min candles
- Every 30 min: Fetches and stores 50 x 30-min candles
- Every 1 hour: Fetches and stores 50 x 1-hour candles

**Ready to Use For:**
- ✅ Backtesting strategies
- ✅ Real-time analysis
- ✅ Technical indicators
- ✅ Pattern recognition
- ✅ Data export

---

🚀 **You're all set! Start with Step 1 above.**
