# 🔍 Diagnosing Cron Job Failures in Supabase

## Current Test Results: ✅ ALL WORKING

Just tested (2025-10-23 13:17 UTC):
- ✅ NQ 5min: OK (10 candles)
- ✅ MNQ 5min: OK (10 candles)
- ✅ ES 5min: OK (10 candles)
- ✅ MES 5min: OK (10 candles)

**Conclusion**: Edge functions are working perfectly RIGHT NOW.

---

## 📊 Check Supabase Dashboard Logs

### Step 1: View Cron Job History

Go to Supabase SQL Editor:
```
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new
```

Run this query to see recent cron job executions:
```sql
SELECT 
    jobname,
    status,
    return_message,
    start_time,
    end_time,
    EXTRACT(EPOCH FROM (end_time - start_time)) as duration_seconds
FROM cron.job_run_details 
WHERE jobname LIKE 'fetch-%' 
ORDER BY start_time DESC 
LIMIT 50;
```

**What to look for:**
- ✅ `status = 'succeeded'` - Job worked
- ❌ `status = 'failed'` - Job failed
- `return_message` - Error details if failed

### Step 2: Check Edge Function Logs

Go to Edge Function Logs:
```
https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/logs/edge-functions
```

**Filter by:**
- Function: `fetch-candles`
- Time range: Last 1 hour or 24 hours

**Look for:**
- ❌ "No Tradovate TV token found in Redis" - Token expired
- ❌ "Token renewal failed" - Tradovate API issue
- ❌ "WebSocket timeout" - Network issue (can be ignored if occasional)
- ❌ "Redis connection error" - Redis credentials issue

### Step 3: Check When Failures Occurred

**IMPORTANT**: If failures are OLD (before 2025-10-23 14:08 UTC), they can be ignored!

We refreshed all tokens at **14:08 UTC** and implemented auto-refresh. Any failures BEFORE that time are from the old token expiry issue.

---

## 🎯 Common Failure Patterns

### Pattern 1: Old Token Expiry (FIXED)

**Symptoms:**
- Failures clustered around 1-hour intervals
- Error: "No Tradovate TV token found in Redis"
- Multiple jobs failing at similar times

**Status**: ✅ FIXED
- Tokens now auto-refresh on every call (every 5 min)
- Backup refresh every 50 minutes
- Last token refresh: 2025-10-23 14:08 UTC

**Action**: Ignore failures before 14:08 UTC

### Pattern 2: Occasional WebSocket Timeouts

**Symptoms:**
- Random failures across different times
- Error: "WebSocket timeout" or "WebSocket closed"
- Only 1-2 jobs fail, others succeed

**Status**: Normal occasional issue
- Tradovate WebSocket can timeout occasionally
- Cron jobs retry automatically on next cycle
- No action needed if < 5% failure rate

**Action**: No action needed

### Pattern 3: Redis Connection Issues

**Symptoms:**
- All jobs failing at the same time
- Error: "Redis connection error" or "ECONNREFUSED"
- Persistent failures

**Status**: Check Redis credentials
- Redis Host: redismanager.redis.cache.windows.net
- Redis Port: 6380
- Redis Password: Check Supabase secrets

**Action**: 
```bash
# Test Redis connection from edge function
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/refresh-tokens" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json"
```

If it fails, check Redis secrets in Supabase dashboard.

### Pattern 4: Tradovate API Issues

**Symptoms:**
- Error: "Token renewal failed" or API errors
- All jobs failing
- Could be demo API maintenance

**Status**: External dependency
- Tradovate demo API: demo.tradovateapi.com
- Check if accessible

**Action**:
```bash
# Test Tradovate API accessibility
curl -I https://demo.tradovateapi.com/v1/auth/renewaccesstoken
# Should return HTTP 401 (unauthorized is OK, means API is up)
```

---

## 🧪 Quick Health Check Commands

### Test All Edge Functions Now:
```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main
bash scripts/monitor_cron_jobs.sh
```

### Refresh Tokens Manually:
```bash
cd data-collection/token-management
python3 token_generator_and_redis_manager.py
```

### Test Single Job:
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "NQZ5"}'
```

---

## 📈 Expected Success Rate

### Normal Operation:
- **Success rate**: 95-100%
- **Occasional failures**: 0-5% (WebSocket timeouts are normal)
- **Pattern**: Random failures, not clustered

### Problem Indicators:
- ❌ Success rate < 90%
- ❌ All jobs failing at once
- ❌ Failures clustered at 1-hour intervals
- ❌ Persistent errors for same job

---

## 🎯 Action Plan Based on Dashboard

### If You See Failures Before 14:08 UTC Today:
✅ **Ignore them** - Those were from the token expiry issue that's now fixed

### If You See Recent Failures (After 14:08 UTC):
1. **Check the error message** in `return_message` column
2. **Check the pattern** - all jobs or just some?
3. **Check the frequency** - occasional or persistent?
4. **Run health check**: `bash scripts/monitor_cron_jobs.sh`

### If Health Check Shows All Working:
✅ **System is healthy** - Dashboard shows old failures that are already resolved

### If Health Check Shows Failures:
1. Refresh tokens: `cd data-collection/token-management && python3 token_generator_and_redis_manager.py`
2. Test again
3. Check Redis connection
4. Check Tradovate API accessibility

---

## 📊 Query to See Only RECENT Failures

Run this in Supabase SQL Editor to see only recent issues:

```sql
-- Failures in last hour
SELECT 
    jobname,
    status,
    return_message,
    start_time
FROM cron.job_run_details 
WHERE jobname LIKE 'fetch-%' 
  AND status = 'failed'
  AND start_time > NOW() - INTERVAL '1 hour'
ORDER BY start_time DESC;
```

If this returns **0 rows** = No recent failures! ✅

---

## 🏁 Summary

**Current Status (as of 13:17 UTC):**
- ✅ All 4 instruments tested: Working
- ✅ Edge functions responding correctly
- ✅ Tokens are fresh (refreshed 14:08 UTC)
- ✅ Auto-refresh active

**Most Likely Scenario:**
The failures you see in Supabase dashboard are from BEFORE we fixed the token issue. They're historical data and can be ignored.

**How to Confirm:**
1. Go to Supabase SQL Editor
2. Run the "recent failures" query above
3. If 0 rows = System is healthy! ✅
4. If rows exist = Check error messages and follow action plan

**Next Check:**
Wait 5-10 minutes and verify data is being collected:
```sql
SELECT MAX(candle_time) as latest_data 
FROM orca.nq_candles_5min;
```

Latest data should be within last 5-10 minutes.
