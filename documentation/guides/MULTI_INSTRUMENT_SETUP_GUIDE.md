# Multi-Instrument Setup Guide

## 🎯 Overview

Complete setup for **4 instruments** with **4 timeframes** each = **16 total data streams**

### Instruments
1. **NQ** - E-mini Nasdaq (NQZ5)
2. **MNQ** - Micro E-mini Nasdaq (MNQZ5)  
3. **ES** - E-mini S&P 500 (ESZ5)
4. **MES** - Micro E-mini S&P 500 (MESZ5)

### Timeframes
- 5 minutes
- 15 minutes
- 30 minutes
- 1 hour

## 📋 Setup Steps

### Step 1: Create Database Tables

Go to Supabase SQL Editor: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

1. Copy contents of `scripts/create_all_instrument_tables.sql`
2. Paste and run
3. Verify: Should see 16 tables created (4 instruments × 4 timeframes)

Expected tables:
```
orca.nq_candles_5min, orca.nq_candles_15min, orca.nq_candles_30min, orca.nq_candles_1hour
orca.mnq_candles_5min, orca.mnq_candles_15min, orca.mnq_candles_30min, orca.mnq_candles_1hour
orca.es_candles_5min, orca.es_candles_15min, orca.es_candles_30min, orca.es_candles_1hour
orca.mes_candles_5min, orca.mes_candles_15min, orca.mes_candles_30min, orca.mes_candles_1hour
```

### Step 2: Create Insert Functions

Still in Supabase SQL Editor:

1. Copy contents of `scripts/create_all_insert_functions.sql`
2. Paste and run
3. Verify: Should see 16 RPC functions created

Expected functions:
```
insert_nq_candles_5min, insert_nq_candles_15min, insert_nq_candles_30min, insert_nq_candles_1hour
insert_mnq_candles_5min, insert_mnq_candles_15min, insert_mnq_candles_30min, insert_mnq_candles_1hour
insert_es_candles_5min, insert_es_candles_15min, insert_es_candles_30min, insert_es_candles_1hour
insert_mes_candles_5min, insert_mes_candles_15min, insert_mes_candles_30min, insert_mes_candles_1hour
```

### Step 3: Deploy Updated Edge Function

**Already completed!** ✅

The `fetch-candles` edge function has been updated to support multiple symbols via the `symbol` parameter.

### Step 4: Set Up Cron Jobs

Still in Supabase SQL Editor:

1. Copy contents of `scripts/setup_all_instruments_cron.sql`
2. Paste and run
3. Verify: Should see 16 cron jobs created

### Step 5: Initial Data Collection

Run this script to fetch initial data for all instruments:

```bash
bash scripts/init_all_instruments.sh
```

This will:
- Test all 16 combinations
- Fetch initial candles for each
- Report success/failure for each stream

## 🧪 Testing Individual Instruments

### Test NQ (E-mini Nasdaq)
```bash
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "NQZ5"}'
```

### Test MNQ (Micro E-mini Nasdaq)
```bash
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "MNQZ5"}'
```

### Test ES (E-mini S&P 500)
```bash
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "ESZ5"}'
```

### Test MES (Micro E-mini S&P 500)
```bash
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "MESZ5"}'
```

## 📊 Verify Data in Supabase

Run this query in Supabase SQL Editor:

```sql
-- Check all tables
SELECT 
    CASE 
        WHEN tablename LIKE 'nq_candles_%' THEN 'NQ'
        WHEN tablename LIKE 'mnq_candles_%' THEN 'MNQ'
        WHEN tablename LIKE 'es_candles_%' THEN 'ES'
        WHEN tablename LIKE 'mes_candles_%' THEN 'MES'
    END as instrument,
    CASE 
        WHEN tablename LIKE '%_5min' THEN '5min'
        WHEN tablename LIKE '%_15min' THEN '15min'
        WHEN tablename LIKE '%_30min' THEN '30min'
        WHEN tablename LIKE '%_1hour' THEN '1hour'
    END as timeframe,
    tablename,
    (SELECT COUNT(*) FROM orca.nq_candles_5min WHERE tablename = 'nq_candles_5min') as row_count
FROM pg_tables
WHERE schemaname = 'orca' 
  AND tablename LIKE '%_candles_%'
ORDER BY instrument, timeframe;

-- Check specific instrument
SELECT 
    symbol,
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.mnq_candles_5min
ORDER BY candle_time DESC
LIMIT 10;
```

## 🔄 Automated Updates

Once cron jobs are set up, data will automatically update:

### NQ, MNQ, ES, MES
- **5-minute candles**: Every 5 minutes
- **15-minute candles**: Every 15 minutes
- **30-minute candles**: Every 30 minutes
- **1-hour candles**: Every hour

## 📋 Cron Job Status

Check cron jobs in Supabase SQL Editor:

```sql
SELECT 
    jobname,
    schedule,
    active,
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 'NQ'
        WHEN jobname LIKE 'fetch-mnq-%' THEN 'MNQ'
        WHEN jobname LIKE 'fetch-es-%' THEN 'ES'
        WHEN jobname LIKE 'fetch-mes-%' THEN 'MES'
    END as instrument,
    CASE 
        WHEN schedule = '*/5 * * * *' THEN 'Every 5 minutes'
        WHEN schedule = '*/15 * * * *' THEN 'Every 15 minutes'
        WHEN schedule = '*/30 * * * *' THEN 'Every 30 minutes'
        WHEN schedule = '0 * * * *' THEN 'Every hour'
    END as frequency
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY instrument, frequency;

-- Check recent cron runs
SELECT 
    j.jobname,
    jrd.status,
    jrd.start_time,
    jrd.end_time
FROM cron.job_run_details jrd
JOIN cron.job j ON jrd.jobid = j.jobid
WHERE j.jobname LIKE 'fetch-%'
ORDER BY jrd.start_time DESC
LIMIT 20;
```

## 🎯 Architecture

### Symbol Mapping
The edge function automatically maps symbols to the correct table:

```typescript
Symbol → Table Prefix
------------------------
NQZ5   → nq
MNQZ5  → mnq
ESZ5   → es
MESZ5  → mes
```

### Data Flow
```
Tradovate API (WebSocket)
    ↓
Edge Function (fetch-candles)
    ↓
Symbol Detection
    ↓
RPC Function (insert_[instrument]_candles_[timeframe])
    ↓
Database Table (orca.[instrument]_candles_[timeframe])
```

## 📁 Files Created

1. **`scripts/create_all_instrument_tables.sql`** - Creates 16 database tables
2. **`scripts/create_all_insert_functions.sql`** - Creates 16 RPC functions
3. **`scripts/setup_all_instruments_cron.sql`** - Sets up 16 cron jobs
4. **`scripts/init_all_instruments.sh`** - Initializes data for all instruments
5. **`MULTI_INSTRUMENT_SETUP_GUIDE.md`** - This guide

## ✅ Checklist

- [ ] Step 1: Created database tables (16 tables)
- [ ] Step 2: Created insert functions (16 functions)
- [ ] Step 3: Edge function deployed (already done ✅)
- [ ] Step 4: Set up cron jobs (16 cron jobs)
- [ ] Step 5: Run initial data collection
- [ ] Step 6: Verify data is updating

## 🚨 Important Notes

1. **Symbols are December 2025 contracts**: NQZ5, MNQZ5, ESZ5, MESZ5 (Z = December)
2. **Market Hours**: Futures trade Sunday 6PM ET to Friday 5PM ET
3. **Tokens**: Auto-refresh every 50 minutes via local cron
4. **Storage**: Each candle takes ~200 bytes, ~300 candles/day per timeframe
5. **Backward Compatibility**: Omitting `symbol` parameter defaults to MNQZ5

## 📞 Quick Commands

```bash
# Test all instruments manually
bash scripts/init_all_instruments.sh

# Check cron status
supabase sql --project-ref dcoukhtfcloqpfmijock \
  --query "SELECT jobname, active FROM cron.job WHERE jobname LIKE 'fetch-%'"

# View table row counts
supabase sql --project-ref dcoukhtfcloqpfmijock \
  --query "SELECT tablename, (SELECT COUNT(*) FROM orca.nq_candles_5min) FROM pg_tables WHERE schemaname='orca' LIMIT 1"
```

## 🎉 Expected Results

After complete setup:

- ✅ 16 tables created
- ✅ 16 insert functions created  
- ✅ 16 cron jobs active
- ✅ Data updating automatically
- ✅ All 4 instruments streaming live data

---

**Status**: Ready for production use
**Last Updated**: October 22, 2025
