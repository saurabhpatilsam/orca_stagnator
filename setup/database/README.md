# 🚀 DATABASE SETUP INSTRUCTIONS

## Current Status
✅ **Edge Functions**: All working and fetching data
❌ **Database**: Tables and functions missing - causing 0 candles to be stored
⚠️ **Cron Jobs**: Need to verify/create

## Quick Setup (5 Minutes)

### 📍 Open Supabase SQL Editor
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

### 🔧 Run These SQL Files in Order:

1. **`01_create_schema_and_tables.sql`**
   - Creates `orca` schema
   - Creates 16 tables (4 instruments × 4 timeframes)
   - Creates all indexes
   - Sets permissions

2. **`02_create_rpc_functions.sql`**
   - Creates 16 RPC insert functions
   - Handles upserts (insert or update on conflict)

3. **`03_create_cron_jobs.sql`**
   - Enables pg_cron and http extensions
   - Creates 16 cron jobs
   - Schedules: */5, */15, */30, and hourly

4. **`04_verify_setup.sql`**
   - Verifies all components are created
   - Shows current status
   - Checks for data collection

## Instruments & Timeframes

### Instruments:
- **NQ**: E-mini Nasdaq (NQZ5)
- **MNQ**: Micro E-mini Nasdaq (MNQZ5)
- **ES**: E-mini S&P 500 (ESZ5)
- **MES**: Micro E-mini S&P 500 (MESZ5)

### Timeframes:
- 5 minutes
- 15 minutes
- 30 minutes
- 60 minutes (1 hour)

## Expected Results After Setup

```
✅ 16 Tables created in orca schema
✅ 16 RPC functions created
✅ 16 Cron jobs active
✅ Data collection starting automatically
```

## Verification Commands

After running all SQL files, test the system:

```bash
# Test edge functions
bash scripts/test_all_edge_functions.sh

# Should show:
# ✅ Fetched: 10+, Stored: 10+ (not 0)
```

## Troubleshooting

### If data is not being stored:
1. Check if tables exist: Run section 2 of `04_verify_setup.sql`
2. Check if functions exist: Run section 3 of `04_verify_setup.sql`
3. Check if cron jobs are active: Run section 4 of `04_verify_setup.sql`

### If cron jobs are not running:
1. Ensure pg_cron extension is enabled
2. Check that http extension is enabled
3. Verify service role key is correct in cron jobs

## Data Flow

```
Cron Job (every 5/15/30/60 min)
    ↓
Edge Function (fetch-candles)
    ↓
Fetches from Tradovate WebSocket
    ↓
Calls RPC Function (insert_xxx_candles_xxx)
    ↓
Stores in Database Table (orca.xxx_candles_xxx)
```

## Notes

- Token refresh is automated in edge functions
- Each edge function call renews tokens and updates Redis
- Data is upserted (updates if exists, inserts if new)
- All times are in UTC

## Support

If you encounter issues:
1. Check the verification script output
2. Review edge function logs in Supabase dashboard
3. Ensure Redis has valid tokens (run `python3 token_generator_and_redis_manager.py`)
