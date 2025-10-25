# Fresh Data Setup Guide

## 🎯 Purpose
Clear all existing candlestick data and start fresh data collection from now.

## ⚠️ Important
This will **permanently delete** all existing candle data. Make sure you have backups if needed.

## 📋 Steps to Follow

### Step 1: Clear Existing Data in Supabase

1. Go to Supabase SQL Editor: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

2. Copy and paste the contents of `scripts/clear_candle_data.sql`:

```sql
BEGIN;

-- Clear 5-minute candles
TRUNCATE TABLE orca.nq_candles_5min;

-- Clear 15-minute candles
TRUNCATE TABLE orca.nq_candles_15min;

-- Clear 30-minute candles
TRUNCATE TABLE orca.nq_candles_30min;

-- Clear 1-hour candles
TRUNCATE TABLE orca.nq_candles_1hour;

COMMIT;

-- Verify tables are empty
SELECT 'nq_candles_5min' as table_name, COUNT(*) as row_count FROM orca.nq_candles_5min
UNION ALL
SELECT 'nq_candles_15min', COUNT(*) FROM orca.nq_candles_15min
UNION ALL
SELECT 'nq_candles_30min', COUNT(*) FROM orca.nq_candles_30min
UNION ALL
SELECT 'nq_candles_1hour', COUNT(*) FROM orca.nq_candles_1hour
ORDER BY table_name;
```

3. Click "Run" and verify all tables show `row_count: 0`

### Step 2: Start Fresh Data Collection

Run this command in your terminal:

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main
bash scripts/start_fresh_data.sh
```

This script will:
1. ✅ Refresh Tradovate tokens
2. ✅ Fetch real-time candles for 5/15/30/60 minutes
3. ✅ Backfill historical data (1-7 days depending on timeframe)

## 📊 What Gets Collected

### Real-Time Data
- **5-minute candles**: Latest 10 candles (~50 minutes)
- **15-minute candles**: Latest 10 candles (~2.5 hours)
- **30-minute candles**: Latest 10 candles (~5 hours)
- **60-minute candles**: Latest 10 candles (~10 hours)

### Historical Backfill
- **5-minute**: Last 1 day (~288 candles)
- **15-minute**: Last 2 days (~192 candles)
- **30-minute**: Last 3 days (~144 candles)
- **60-minute**: Last 7 days (~168 candles)

## ✅ Verification

After running the script, verify the data:

### Option 1: Health Check
```bash
bash scripts/health_check.sh
```

### Option 2: SQL Query
In Supabase SQL Editor:

```sql
-- Check row counts
SELECT 
    'nq_candles_5min' as table_name, 
    COUNT(*) as total_candles,
    MIN(candle_time) as oldest_candle,
    MAX(candle_time) as newest_candle
FROM orca.nq_candles_5min
UNION ALL
SELECT 'nq_candles_15min', COUNT(*), MIN(candle_time), MAX(candle_time) FROM orca.nq_candles_15min
UNION ALL
SELECT 'nq_candles_30min', COUNT(*), MIN(candle_time), MAX(candle_time) FROM orca.nq_candles_30min
UNION ALL
SELECT 'nq_candles_1hour', COUNT(*), MIN(candle_time), MAX(candle_time) FROM orca.nq_candles_1hour
ORDER BY table_name;
```

### Option 3: Sample Data
```sql
-- View latest 5 candles from each table
SELECT 'nq_candles_5min' as timeframe, * FROM orca.nq_candles_5min ORDER BY candle_time DESC LIMIT 5;
```

## 🔄 Ongoing Data Collection

After setup, data will automatically update via:

1. **Cron Jobs (pg_cron)**: Scheduled fetches at proper intervals
2. **Token Refresh**: Automatic every 50 minutes
3. **Scheduler Function**: Coordinates all data fetches

### Check Cron Jobs
In Supabase SQL Editor:

```sql
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    command
FROM cron.job 
WHERE jobname LIKE 'fetch-candles-%'
ORDER BY jobname;
```

## 📝 Logs

All activity is logged:

```bash
# View latest log
ls -lht logs/fresh_data_*.log | head -1

# Read the log
cat logs/fresh_data_YYYYMMDD_HHMMSS.log

# Monitor in real-time
tail -f logs/fresh_data_$(date +%Y%m%d)*.log
```

## 🔧 Troubleshooting

### Tables Still Have Data
- Make sure you ran the SQL TRUNCATE commands in Supabase
- Verify with: `SELECT COUNT(*) FROM orca.nq_candles_5min;`

### Script Fails
1. Check tokens: `python3 token_generator_and_redis_manager.py`
2. Verify edge functions: `bash scripts/health_check.sh`
3. Check logs: `cat logs/fresh_data_*.log`

### No Historical Data
- Historical backfill only works for recent data
- Market must be open or recently closed
- Check Tradovate API limits

## ⚡ Quick Reset Command

To clear and restart everything in one go:

```bash
# 1. Clear data (run SQL in Supabase first)
# 2. Then run:
cd /Users/stagnator/Downloads/orca-ven-backend-main
bash scripts/start_fresh_data.sh
```

## 📞 Expected Results

After successful execution:

```
✅ Tokens refreshed successfully
✅ 5min: Stored 10 candles
✅ 15min: Stored 10 candles
✅ 30min: Stored 10 candles
✅ 60min: Stored 10 candles
✅ 5min: Stored ~288 historical candles
✅ 15min: Stored ~192 historical candles
✅ 30min: Stored ~144 historical candles
✅ 60min: Stored ~168 historical candles

📊 Data Collection Summary
Real-time fetches: Successful: 4, Failed: 0
✅ Fresh data collection complete!
⚡ Automated cron jobs will continue updating every 5/15/30/60 minutes
```

## 🎉 Success Indicators

1. All edge function calls return `"success": true`
2. Candles are being stored (`candles_stored > 0`)
3. Tables contain data with recent timestamps
4. Health check shows all functions working
5. Cron jobs are active and scheduled

---

**Last Updated**: October 22, 2025
**Status**: Ready to use
