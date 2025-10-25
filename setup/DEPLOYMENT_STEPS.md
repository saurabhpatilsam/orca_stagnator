# 🚀 FIXED DEPLOYMENT STEPS

## Issue Found
The previous SQL file had a syntax error at line 713 because:
- It tried to create cron jobs without enabling required extensions first
- The `http` extension wasn't enabled

## ✅ Solution - Run These 2 Files in Order

### Step 1: Install RPC Functions (2 minutes)

**File**: `setup/database/RPC_FUNCTIONS_ONLY.sql`

1. Open Supabase SQL Editor:
   https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

2. Copy entire content of `setup/database/RPC_FUNCTIONS_ONLY.sql`

3. Paste and click **Run**

4. You should see: `RPC Functions created: 16`

---

### Step 2: Test Edge Functions (1 minute)

```bash
bash data-collection/verification/test_all_edge_functions.sh
```

**Expected Result**: `✅ Fetched: 10, Stored: 10` (not 0 anymore!)

If this works, your RPC functions are installed correctly! 🎉

---

### Step 3: Setup Automated Cron Jobs (Optional - 3 minutes)

For cron jobs, you have **3 options**:

#### Option A: Supabase Dashboard (Easiest)
1. Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/database/cron-jobs
2. Click "Create a new cron job"
3. For each instrument/timeframe combination, create a job:
   - **Name**: `fetch-nq-5min`
   - **Schedule**: `*/5 * * * *` (every 5 minutes)
   - **SQL Command**:
   ```sql
   SELECT
       status,
       content::json->>'success' as success
   FROM extensions.http((
       'POST',
       'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
       ARRAY[
           extensions.http_header('Content-Type', 'application/json'),
           extensions.http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')
       ],
       'application/json',
       '{"timeframe": 5, "symbol": "NQZ5"}'
   )::extensions.http_request);
   ```

#### Option B: Enable Extensions First, Then SQL
1. Run `setup/database/ENABLE_EXTENSIONS_AND_CRON.sql` in SQL Editor
2. Then run `setup/database/03_create_cron_jobs.sql`

#### Option C: External Cron (Local Machine)
Use cron on your local machine or a server to call edge functions every 5/15/30/60 minutes.

---

## Quick Verification

After Step 1 & 2, check if data is being stored:

```sql
-- Run in Supabase SQL Editor
SELECT 
    'NQ 5min' as stream, COUNT(*) as rows FROM orca.nq_candles_5min
UNION ALL
SELECT 'MNQ 5min', COUNT(*) FROM orca.mnq_candles_5min
UNION ALL  
SELECT 'ES 5min', COUNT(*) FROM orca.es_candles_5min
UNION ALL
SELECT 'MES 5min', COUNT(*) FROM orca.mes_candles_5min;
```

If you see rows > 0 after running edge functions, SUCCESS! ✅

---

## Summary

| Step | Action | Status |
|------|--------|--------|
| 1 | Run RPC_FUNCTIONS_ONLY.sql | ⏳ Required |
| 2 | Test edge functions | ⏳ Required |
| 3 | Setup cron jobs | ⏳ Optional (for automation) |

**Without cron jobs**: You can manually trigger edge functions anytime
**With cron jobs**: Fully automated 24/7 data collection

---

## Files Created

- ✅ `setup/database/RPC_FUNCTIONS_ONLY.sql` - Install functions (no errors)
- ✅ `setup/database/ENABLE_EXTENSIONS_AND_CRON.sql` - Enable extensions
- ✅ `setup/DEPLOYMENT_STEPS.md` - This guide
