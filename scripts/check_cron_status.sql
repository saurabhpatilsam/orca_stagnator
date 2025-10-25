-- ========================================
-- CRON JOB STATUS CHECKER
-- Run this in Supabase SQL Editor to diagnose issues
-- ========================================

-- 1. Check all active cron jobs
SELECT 
    '=== ACTIVE CRON JOBS ===' as section,
    NULL::text as jobname, 
    NULL::text as schedule, 
    NULL::boolean as active
UNION ALL
SELECT 
    NULL,
    jobname, 
    schedule, 
    active 
FROM cron.job 
WHERE jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%'
ORDER BY section DESC, jobname;

-- 2. Check recent job executions (last 20)
SELECT 
    '=== RECENT EXECUTIONS (Last 20) ===' as info,
    NULL::text as jobname,
    NULL::text as status,
    NULL::text as error,
    NULL::timestamp as time
UNION ALL
SELECT 
    NULL,
    jobname,
    status,
    CASE 
        WHEN status = 'failed' THEN LEFT(return_message, 100)
        ELSE 'OK'
    END as error,
    start_time
FROM cron.job_run_details 
WHERE jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%'
ORDER BY info DESC, time DESC NULLS LAST
LIMIT 21;

-- 3. Count successes vs failures in last hour
SELECT 
    '=== SUCCESS/FAILURE COUNT (Last Hour) ===' as metric,
    NULL::text as status,
    NULL::bigint as count
UNION ALL
SELECT 
    NULL,
    status,
    COUNT(*) 
FROM cron.job_run_details 
WHERE (jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%')
  AND start_time > NOW() - INTERVAL '1 hour'
GROUP BY status
ORDER BY metric DESC, count DESC NULLS LAST;

-- 4. Check for recent failures only
SELECT 
    '=== RECENT FAILURES ONLY (Last Hour) ===' as section,
    NULL::text as jobname,
    NULL::text as error,
    NULL::timestamp as time
UNION ALL
SELECT 
    NULL,
    jobname,
    LEFT(return_message, 150) as error,
    start_time
FROM cron.job_run_details 
WHERE (jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%')
  AND status = 'failed'
  AND start_time > NOW() - INTERVAL '1 hour'
ORDER BY section DESC, time DESC NULLS LAST
LIMIT 21;

-- 5. Check data freshness (how recent is our data?)
SELECT 
    '=== DATA FRESHNESS CHECK ===' as metric,
    NULL::text as table_name,
    NULL::bigint as row_count,
    NULL::timestamp as latest_candle,
    NULL::text as age
UNION ALL
SELECT 
    NULL,
    'nq_candles_5min' as table_name,
    COUNT(*) as row_count,
    MAX(candle_time) as latest_candle,
    CASE 
        WHEN MAX(candle_time) > NOW() - INTERVAL '10 minutes' THEN '✅ Fresh'
        WHEN MAX(candle_time) > NOW() - INTERVAL '30 minutes' THEN '⚠️ Stale'
        ELSE '❌ Very Old'
    END as age
FROM orca.nq_candles_5min
UNION ALL
SELECT 
    NULL,
    'mnq_candles_5min',
    COUNT(*),
    MAX(candle_time),
    CASE 
        WHEN MAX(candle_time) > NOW() - INTERVAL '10 minutes' THEN '✅ Fresh'
        WHEN MAX(candle_time) > NOW() - INTERVAL '30 minutes' THEN '⚠️ Stale'
        ELSE '❌ Very Old'
    END
FROM orca.mnq_candles_5min
UNION ALL
SELECT 
    NULL,
    'es_candles_5min',
    COUNT(*),
    MAX(candle_time),
    CASE 
        WHEN MAX(candle_time) > NOW() - INTERVAL '10 minutes' THEN '✅ Fresh'
        WHEN MAX(candle_time) > NOW() - INTERVAL '30 minutes' THEN '⚠️ Stale'
        ELSE '❌ Very Old'
    END
FROM orca.es_candles_5min
UNION ALL
SELECT 
    NULL,
    'mes_candles_5min',
    COUNT(*),
    MAX(candle_time),
    CASE 
        WHEN MAX(candle_time) > NOW() - INTERVAL '10 minutes' THEN '✅ Fresh'
        WHEN MAX(candle_time) > NOW() - INTERVAL '30 minutes' THEN '⚠️ Stale'
        ELSE '❌ Very Old'
    END
FROM orca.mes_candles_5min
ORDER BY metric DESC, table_name NULLS FIRST;

-- 6. Summary
SELECT 
    '=== SUMMARY ===' as info,
    NULL::text as metric,
    NULL::text as value
UNION ALL
SELECT 
    NULL,
    'Total Cron Jobs' as metric,
    COUNT(*)::text as value
FROM cron.job 
WHERE jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%'
UNION ALL
SELECT 
    NULL,
    'Active Jobs',
    COUNT(*)::text
FROM cron.job 
WHERE (jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%') AND active = true
UNION ALL
SELECT 
    NULL,
    'Failed Runs (Last Hour)',
    COUNT(*)::text
FROM cron.job_run_details 
WHERE (jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%')
  AND status = 'failed'
  AND start_time > NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 
    NULL,
    'Success Runs (Last Hour)',
    COUNT(*)::text
FROM cron.job_run_details 
WHERE (jobname LIKE 'fetch-%' OR jobname LIKE 'refresh-%')
  AND status = 'succeeded'
  AND start_time > NOW() - INTERVAL '1 hour'
ORDER BY info DESC, metric NULLS FIRST;

-- ========================================
-- INTERPRETATION GUIDE
-- ========================================
-- 
-- HEALTHY SYSTEM:
-- - All cron jobs active = true
-- - Recent failures = 0 or very low
-- - Data freshness = "Fresh" (< 10 minutes old)
-- - Success rate > 95%
--
-- NEEDS ATTENTION:
-- - Some recent failures (< 10%)
-- - Data slightly stale (10-30 min old)
-- - Check error messages
--
-- PROBLEM:
-- - Many recent failures (> 10%)
-- - Data very old (> 30 min)
-- - Consistent error pattern
-- - Action: Refresh tokens and check Redis
-- ========================================

-- 1. Check if pg_cron extension is enabled
SELECT * FROM pg_extension WHERE extname = 'pg_cron';

-- 2. List all cron jobs
SELECT 
    jobid,
    jobname,
    schedule,
    command,
    active,
    created_at
FROM cron.job 
WHERE jobname LIKE 'fetch-candles-%'
ORDER BY jobname;

-- 3. Check cron job run history (last 20 runs)
SELECT 
    runid,
    jobid,
    job_pid,
    database,
    username,
    command,
    status,
    return_message,
    start_time,
    end_time
FROM cron.job_run_details
WHERE jobid IN (SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-candles-%')
ORDER BY start_time DESC
LIMIT 20;

-- 4. Check for failed runs
SELECT 
    j.jobname,
    jrd.status,
    jrd.return_message,
    jrd.start_time,
    jrd.end_time
FROM cron.job_run_details jrd
JOIN cron.job j ON jrd.jobid = j.jobid
WHERE j.jobname LIKE 'fetch-candles-%'
  AND jrd.status = 'failed'
ORDER BY jrd.start_time DESC
LIMIT 10;

-- 5. Check latest candle times to see if data is updating
SELECT 
    'nq_candles_5min' as table_name,
    MAX(candle_time) as latest_candle,
    NOW() - MAX(candle_time) as time_since_last_update,
    COUNT(*) as total_candles
FROM orca.nq_candles_5min
UNION ALL
SELECT 
    'nq_candles_15min',
    MAX(candle_time),
    NOW() - MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_15min
UNION ALL
SELECT 
    'nq_candles_30min',
    MAX(candle_time),
    NOW() - MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_30min
UNION ALL
SELECT 
    'nq_candles_1hour',
    MAX(candle_time),
    NOW() - MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_1hour
ORDER BY table_name;

-- 6. Check if http extension is enabled (needed for cron jobs to call edge functions)
SELECT * FROM pg_extension WHERE extname = 'http';

-- 7. Test if we can make HTTP calls from database
-- (This should work if http extension is installed)
-- SELECT status, content::json 
-- FROM http_get('https://httpbin.org/get');
