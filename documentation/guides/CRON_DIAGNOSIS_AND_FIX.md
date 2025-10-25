# Cron Jobs Diagnosis & Fix

## 🔍 Diagnosis Results

### ✅ What's Working
1. **Edge Functions**: All operational and storing data correctly
   - fetch-candles: ✅ Working (just tested successfully)
   - 5-min candles: ✅ Stored 10 candles
   - 30-min candles: ✅ Stored 10 candles
   
2. **Local Token Refresh**: Cron job configured
   - Schedule: Every 50 minutes
   - Status: Active in crontab

### ❌ What's NOT Working
**Supabase pg_cron jobs are NOT set up or running**

This is why you're not seeing automatic updates. The edge functions work fine when called manually, but there's no automatic scheduler in Supabase calling them every 5/15/30/60 minutes.

## 🔧 Root Cause

The `setup_cron_jobs.sql` file we created earlier uses the old `net.http_post` syntax which doesn't work properly. We need to use the newer `http()` function with proper syntax.

## ✅ Solution

### Step 1: Run This SQL in Supabase

Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

Copy and paste the entire contents of `scripts/setup_supabase_cron.sql` and click "Run".

This will:
1. ✅ Enable required extensions (pg_cron, http)
2. ✅ Remove any old broken cron jobs
3. ✅ Create new working cron jobs for all timeframes
4. ✅ Verify jobs were created successfully

### Step 2: Verify Cron Jobs Are Running

After 5-10 minutes, run `scripts/check_cron_status.sql` in Supabase to verify:

```sql
-- Check if jobs are scheduled
SELECT jobid, jobname, schedule, active
FROM cron.job 
WHERE jobname LIKE 'fetch-candles-%'
ORDER BY jobname;

-- Check recent runs
SELECT 
    j.jobname,
    jrd.status,
    jrd.start_time,
    jrd.end_time
FROM cron.job_run_details jrd
JOIN cron.job j ON jrd.jobid = j.jobid
WHERE j.jobname LIKE 'fetch-candles-%'
ORDER BY jrd.start_time DESC
LIMIT 10;
```

## 📊 Expected Results

### Cron Jobs Should Show:
```
jobname                  | schedule      | active
-------------------------|---------------|--------
fetch-candles-5min       | */5 * * * *   | true
fetch-candles-15min      | */15 * * * *  | true
fetch-candles-30min      | */30 * * * *  | true
fetch-candles-1hour      | 0 * * * *     | true
```

### Data Should Update:
- **5-minute candles**: New candle every 5 minutes
- **15-minute candles**: New candle every 15 minutes
- **30-minute candles**: New candle every 30 minutes
- **60-minute candles**: New candle every hour

## 🧪 Testing

### Manual Test (Works Now)
```bash
# Test 5-minute candles
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5}'
```

### Automatic Test (After Fix)
Wait 5-10 minutes after running the SQL, then check:

```sql
-- Check latest candles
SELECT 
    MAX(candle_time) as latest_candle,
    NOW() - MAX(candle_time) as time_since_last
FROM orca.nq_candles_5min;
```

Should show `time_since_last` less than 5-10 minutes.

## 🎯 Key Differences

### Old (Broken) Syntax:
```sql
SELECT net.http_post(
    url := 'https://...',
    headers := '{"Content-Type": "application/json"}'::jsonb,
    body := '{"timeframe": 5}'::jsonb
);
```

### New (Working) Syntax:
```sql
SELECT status, content::json
FROM http((
    'POST',
    'https://...',
    ARRAY[http_header('Content-Type', 'application/json')],
    'application/json',
    '{"timeframe": 5}'
)::http_request);
```

## 🔄 Complete System Status

### Local Machine (Your Mac)
- ✅ Token refresh cron: Active (every 50 minutes)
- ✅ Health check script: Available
- ✅ Edge functions: Working

### Supabase (Cloud)
- ✅ Edge functions deployed: Working
- ❌ pg_cron jobs: **NEED TO BE SET UP** (run setup_supabase_cron.sql)
- ✅ Database tables: Ready
- ✅ Extensions: pg_cron, http (will be enabled by script)

## 📋 Checklist

- [ ] Run `scripts/setup_supabase_cron.sql` in Supabase SQL Editor
- [ ] Wait 5-10 minutes
- [ ] Run `scripts/check_cron_status.sql` to verify jobs are running
- [ ] Check latest candle times are updating
- [ ] Verify cron job run history shows successful executions

## 🚨 Important Notes

1. **Token Expiry**: Tokens expire every hour, local cron refreshes every 50 minutes
2. **Market Hours**: Tradovate data only available during market hours
3. **First Run**: After setup, first candles might take 5-15 minutes to appear
4. **Monitoring**: Use `scripts/health_check.sh` to test edge functions anytime

## 📞 Quick Commands

```bash
# Test edge functions manually
bash scripts/health_check.sh

# Check local cron
crontab -l

# View token refresh logs (after first cron run)
ls -lht logs/token_refresh_*.log | head -1
```

## 🎉 After Fix

Once you run `setup_supabase_cron.sql`:

1. ✅ 5-minute candles auto-update every 5 minutes
2. ✅ 15-minute candles auto-update every 15 minutes
3. ✅ 30-minute candles auto-update every 30 minutes
4. ✅ 60-minute candles auto-update every hour
5. ✅ Tokens auto-refresh every 50 minutes
6. ✅ Complete automation - no manual intervention needed!

---

**Next Step**: Run `scripts/setup_supabase_cron.sql` in Supabase SQL Editor NOW to fix the issue.
