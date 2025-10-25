# Multi-Instrument Setup Summary

## ✅ What's Been Done

### 1. Database Infrastructure (16 Tables)
Created candlestick tables for all 4 instruments × 4 timeframes:

#### NQ (E-mini Nasdaq)
- `orca.nq_candles_5min`
- `orca.nq_candles_15min`
- `orca.nq_candles_30min`
- `orca.nq_candles_1hour`

#### MNQ (Micro E-mini Nasdaq)
- `orca.mnq_candles_5min`
- `orca.mnq_candles_15min`
- `orca.mnq_candles_30min`
- `orca.mnq_candles_1hour`

#### ES (E-mini S&P 500)
- `orca.es_candles_5min`
- `orca.es_candles_15min`
- `orca.es_candles_30min`
- `orca.es_candles_1hour`

#### MES (Micro E-mini S&P 500)
- `orca.mes_candles_5min`
- `orca.mes_candles_15min`
- `orca.mes_candles_30min`
- `orca.mes_candles_1hour`

### 2. RPC Functions (16 Functions)
Created insert functions for all combinations:
- `insert_nq_candles_*` (4 functions)
- `insert_mnq_candles_*` (4 functions)
- `insert_es_candles_*` (4 functions)
- `insert_mes_candles_*` (4 functions)

### 3. Edge Function Updated
Updated `fetch-candles` edge function to:
- Accept `symbol` parameter
- Auto-detect instrument from symbol (NQ, MNQ, ES, MES)
- Route to correct table based on symbol
- Backward compatible (defaults to MNQZ5 if no symbol provided)

**Deployed**: ✅ https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles

### 4. Automation Scripts
Created comprehensive automation:
- `scripts/create_all_instrument_tables.sql` - Creates all tables
- `scripts/create_all_insert_functions.sql` - Creates all RPC functions
- `scripts/setup_all_instruments_cron.sql` - Sets up 16 cron jobs
- `scripts/init_all_instruments.sh` - Initializes all instruments
- `MULTI_INSTRUMENT_SETUP_GUIDE.md` - Complete setup guide

### 5. Symbol Mapping
```
NQZ5   → nq_candles_*   (E-mini Nasdaq)
MNQZ5  → mnq_candles_*  (Micro E-mini Nasdaq)
ESZ5   → es_candles_*   (E-mini S&P 500)
MESZ5  → mes_candles_*  (Micro E-mini S&P 500)
```

## 📋 What You Need to Do

### Step 1: Run SQL Scripts in Supabase

Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

**1. Create Tables (First)**
```sql
-- Copy and paste contents of: scripts/create_all_instrument_tables.sql
-- This creates 16 tables
```

**2. Create Functions (Second)**
```sql
-- Copy and paste contents of: scripts/create_all_insert_functions.sql
-- This creates 16 RPC functions
```

**3. Set Up Cron Jobs (Third)**
```sql
-- Copy and paste contents of: scripts/setup_all_instruments_cron.sql
-- This creates 16 cron jobs
```

### Step 2: Test the Setup

Run the initialization script:
```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main
bash scripts/init_all_instruments.sh
```

This will:
- Refresh tokens
- Test all 16 combinations
- Report success/failure for each
- Show summary statistics

### Step 3: Verify in Supabase

Run this in Supabase SQL Editor to check data:

```sql
-- Check all tables
SELECT 
    tablename,
    (SELECT COUNT(*) FROM orca.nq_candles_5min WHERE tablename = 'nq_candles_5min') as row_count
FROM pg_tables
WHERE schemaname = 'orca' 
  AND tablename LIKE '%_candles_%'
ORDER BY tablename;

-- View sample data from MNQ
SELECT * FROM orca.mnq_candles_5min ORDER BY candle_time DESC LIMIT 5;

-- Check cron jobs
SELECT jobname, schedule, active FROM cron.job WHERE jobname LIKE 'fetch-%' ORDER BY jobname;
```

## 🎯 Expected Results

After complete setup:

### Database
- ✅ 16 tables created
- ✅ All tables empty initially
- ✅ Data starts populating after init script

### Functions
- ✅ 16 RPC functions available
- ✅ Each function routes to correct table
- ✅ Handles inserts/updates automatically

### Cron Jobs
- ✅ 16 cron jobs scheduled
- ✅ 5-min jobs run every 5 minutes
- ✅ 15-min jobs run every 15 minutes
- ✅ 30-min jobs run every 30 minutes
- ✅ 1-hour jobs run every hour

### Data Collection
After initialization:
- **NQ**: ~10 candles per timeframe initially
- **MNQ**: ~10 candles per timeframe initially
- **ES**: ~10 candles per timeframe initially
- **MES**: ~10 candles per timeframe initially

After 1 hour of cron jobs:
- **5-min**: ~12 candles per instrument (60min ÷ 5min = 12 candles)
- **15-min**: ~4 candles per instrument
- **30-min**: ~2 candles per instrument
- **1-hour**: ~1 candle per instrument

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│ Tradovate API (WebSocket)                           │
│ Symbols: NQZ5, MNQZ5, ESZ5, MESZ5                  │
└─────────────────────┬───────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────┐
│ Edge Function: fetch-candles                        │
│ - Accepts: timeframe + symbol                       │
│ - Detects: instrument from symbol                   │
│ - Fetches: WebSocket data from Tradovate           │
└─────────────────────┬───────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────┐
│ RPC Functions (16 total)                            │
│ - insert_[instrument]_candles_[timeframe]           │
│ - Handles: upserts (insert or update)              │
└─────────────────────┬───────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────┐
│ Database Tables (16 total)                          │
│ - orca.[instrument]_candles_[timeframe]             │
│ - Stores: OHLCV + volume breakdown                 │
└─────────────────────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────┐
│ Automated Updates (pg_cron)                         │
│ - 16 cron jobs                                       │
│ - Runs: 5/15/30/60 minute intervals                │
└─────────────────────────────────────────────────────┘
```

## 🔄 Data Update Frequency

### Per Instrument
```
Timeframe | Frequency        | Candles/Day
----------------------------------------------
5 min     | Every 5 minutes  | ~288
15 min    | Every 15 minutes | ~96
30 min    | Every 30 minutes | ~48
1 hour    | Every hour       | ~24
----------------------------------------------
TOTAL per instrument per day: ~456 candles
```

### All Instruments Combined
```
Total candles per day: ~1,824 (456 × 4 instruments)
```

## 📁 File Reference

| File | Purpose | Run Where |
|------|---------|-----------|
| `scripts/create_all_instrument_tables.sql` | Create 16 tables | Supabase SQL Editor |
| `scripts/create_all_insert_functions.sql` | Create 16 RPC functions | Supabase SQL Editor |
| `scripts/setup_all_instruments_cron.sql` | Setup 16 cron jobs | Supabase SQL Editor |
| `scripts/init_all_instruments.sh` | Test all combinations | Local terminal |
| `MULTI_INSTRUMENT_SETUP_GUIDE.md` | Complete guide | Documentation |
| `SETUP_SUMMARY.md` | This file | Documentation |

## 🧪 Manual Testing Commands

### Test Individual Instruments
```bash
# NQ (E-mini Nasdaq)
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "NQZ5"}'

# MNQ (Micro E-mini Nasdaq)  
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "MNQZ5"}'

# ES (E-mini S&P 500)
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "ESZ5"}'

# MES (Micro E-mini S&P 500)
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "MESZ5"}'
```

## ⚠️ Important Notes

1. **Contract Expiration**: Current symbols are December 2025 (Z5)
   - Need to update to March 2026 (H6) before December expiration
   
2. **Market Hours**: Futures trade Sunday 6PM ET to Friday 5PM ET
   - No data collection when market is closed
   
3. **Token Management**: Tokens auto-refresh every 50 minutes
   - Local cron job handles this automatically
   
4. **Storage**: ~1,824 candles/day × 200 bytes ≈ 365 KB/day
   - Very manageable storage requirements

## 🚨 Troubleshooting

### Tables Not Creating
- Check schema exists: `CREATE SCHEMA IF NOT EXISTS orca;`
- Check permissions: User must have CREATE TABLE rights

### Functions Not Working
- Verify tables exist first
- Check function syntax in Supabase logs
- Ensure GRANT statements executed

### Cron Jobs Not Running
- Verify pg_cron extension enabled
- Check http extension enabled
- Verify service role key is correct
- Check cron.job_run_details for errors

### No Data Being Stored
- Verify tokens are valid
- Check market is open
- Test edge function manually first
- Check Supabase function logs

## 🎉 Success Criteria

✅ All 16 tables created
✅ All 16 RPC functions working
✅ Edge function deployed and tested
✅ All 16 cron jobs scheduled
✅ Data updating automatically
✅ Manual tests pass for all instruments

---

**Status**: Ready for deployment
**Created**: October 22, 2025
**Next Update**: When adding new instruments or timeframes
