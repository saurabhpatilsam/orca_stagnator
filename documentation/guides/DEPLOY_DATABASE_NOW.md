# 🚀 DEPLOY DATABASE - COMPLETE SETUP GUIDE

## Current Status

✅ **Edge Functions**: 100% working (all 16 combinations tested)
✅ **Token Refresh**: Automated and working
❌ **Database Tables**: Not created yet
❌ **RPC Functions**: Not created yet
❌ **Cron Jobs**: Not verified

## Issue Found

Edge functions are fetching candles successfully but **0 candles stored** because:
- Database tables don't exist in `orca` schema
- RPC insert functions don't exist
- Cron jobs might not be set up

## 📋 Step-by-Step Deployment

### Step 1: Create All Database Tables (REQUIRED)

**File**: `scripts/create_all_instrument_tables.sql`

**Open in Supabase**:
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

**Copy and run the entire file** - This creates:
- 16 tables in `orca` schema (4 instruments × 4 timeframes)
- All necessary indexes
- Tables: nq_candles_5min, nq_candles_15min, etc.

### Step 2: Create All RPC Insert Functions (REQUIRED)

**File**: `scripts/create_all_insert_functions.sql`

**Copy and run the entire file** - This creates:
- 16 RPC functions: `insert_nq_candles_5min()`, `insert_mnq_candles_5min()`, etc.
- Functions handle upserts (insert or update on conflict)

### Step 3: Set Up Cron Jobs (REQUIRED)

**File**: `scripts/cron_jobs_final.sql`

**Copy and run the entire file** - This creates:
- 16 cron jobs (one per instrument/timeframe combination)
- Schedules: */5, */15, */30, 0 (every 5/15/30/60 minutes)

### Step 4: Verify Everything Works

Run this SQL to check:

```sql
-- Check tables exist
SELECT schemaname, tablename 
FROM pg_tables 
WHERE tablename LIKE '%candles%'
ORDER BY schemaname, tablename;

-- Check RPC functions exist
SELECT proname 
FROM pg_proc 
WHERE proname LIKE 'insert_%candles%'
ORDER BY proname;

-- Check cron jobs
SELECT jobname, schedule, active 
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;
```

Expected results:
- 16 tables in `orca` schema
- 16 RPC functions
- 16 active cron jobs

### Step 5: Test Data Collection

Run the verification script:

```bash
python3 scripts/verify_all_instruments.py
```

This should now show:
- ✅ All edge functions working
- ✅ Candles being stored (not 0)
- ✅ Database rows > 0 for all tables

## 🔍 Quick Verification After Setup

```sql
-- Check if data is being collected
SELECT 
    'nq_5min' as table_name, COUNT(*) as rows FROM orca.nq_candles_5min
UNION ALL
SELECT 'mnq_5min', COUNT(*) FROM orca.mnq_candles_5min
UNION ALL
SELECT 'es_5min', COUNT(*) FROM orca.es_candles_5min
UNION ALL
SELECT 'mes_5min', COUNT(*) FROM orca.mes_candles_5min;
```

If you see rows > 0, it's working!

## 📊 Expected Final State

After running all 3 SQL files:

```
✅ 16 Tables created in orca schema
✅ 16 RPC functions created
✅ 16 Cron jobs active
✅ Data flowing every 5/15/30/60 minutes
✅ Token refresh automated (already done)
```

## ⚡ Files to Run (In Order)

1. `scripts/create_all_instrument_tables.sql` - Tables
2. `scripts/create_all_insert_functions.sql` - RPC Functions
3. `scripts/cron_jobs_final.sql` - Cron Jobs

**Each file should be run in Supabase SQL Editor:**
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

## 🎯 After Setup

Your system will automatically:
- Fetch candlestick data for NQ, MNQ, ES, MES
- Store data for 5min, 15min, 30min, 1hour timeframes
- Refresh tokens every time edge functions run
- Run 24/7 without manual intervention

Total: **16 automated data streams** collecting continuously!
