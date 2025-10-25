-- ========================================
-- VERIFICATION SCRIPT
-- ========================================
-- Run this after completing all setup steps
-- Verifies everything is properly configured

-- 1. Check schemas
SELECT 
    '✅ Schema exists' as status
FROM information_schema.schemata 
WHERE schema_name = 'orca';

-- 2. Check tables created
SELECT 
    COUNT(*) as table_count,
    CASE 
        WHEN COUNT(*) = 16 THEN '✅ All 16 tables created'
        ELSE '❌ Only ' || COUNT(*) || ' tables found (expected 16)'
    END as status
FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%candles%';

-- List all tables
SELECT 
    schemaname || '.' || tablename as table_name,
    '✅' as status
FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%candles%'
ORDER BY tablename;

-- 3. Check RPC functions
SELECT 
    COUNT(*) as function_count,
    CASE 
        WHEN COUNT(*) = 16 THEN '✅ All 16 RPC functions created'
        ELSE '❌ Only ' || COUNT(*) || ' functions found (expected 16)'
    END as status
FROM pg_proc 
WHERE proname LIKE 'insert_%_candles_%';

-- List all functions
SELECT 
    proname as function_name,
    '✅' as status
FROM pg_proc 
WHERE proname LIKE 'insert_%_candles_%'
ORDER BY proname;

-- 4. Check cron jobs
SELECT 
    COUNT(*) as cron_job_count,
    CASE 
        WHEN COUNT(*) = 16 THEN '✅ All 16 cron jobs created'
        ELSE '❌ Only ' || COUNT(*) || ' cron jobs found (expected 16)'
    END as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%';

-- List all cron jobs with schedules
SELECT 
    jobname,
    schedule,
    CASE active 
        WHEN true THEN '✅ Active'
        ELSE '❌ Inactive'
    END as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- 5. Check if data is being collected (check row counts)
SELECT 'Data Collection Status:' as section;

-- Check each table for data
DO $$
DECLARE
    r RECORD;
    row_count INTEGER;
BEGIN
    RAISE NOTICE '===== Data Collection Status =====';
    FOR r IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'orca' AND tablename LIKE '%candles%'
        ORDER BY tablename
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM orca.%I', r.tablename) INTO row_count;
        IF row_count > 0 THEN
            RAISE NOTICE '✅ %.%: % rows', 'orca', r.tablename, row_count;
        ELSE
            RAISE NOTICE '⚠️  %.%: 0 rows (no data yet)', 'orca', r.tablename;
        END IF;
    END LOOP;
END $$;

-- 6. Check recent cron job runs (if available)
SELECT 'Recent Cron Job Executions:' as section;

-- Check if job_run_details table exists and has data
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'cron' AND table_name = 'job_run_details') THEN
        RAISE NOTICE 'Recent job runs:';
        -- Show last 5 runs
        PERFORM jobname, status, return_message, start_time
        FROM cron.job_run_details
        WHERE jobname LIKE 'fetch-%'
        ORDER BY start_time DESC
        LIMIT 5;
    ELSE
        RAISE NOTICE 'Job run details not available';
    END IF;
END $$;

-- Final summary
SELECT '===== SETUP VERIFICATION COMPLETE =====' as summary;

SELECT 
    'Tables: ' || (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%candles%')::text || '/16' as tables,
    'Functions: ' || (SELECT COUNT(*) FROM pg_proc WHERE proname LIKE 'insert_%_candles_%')::text || '/16' as functions,
    'Cron Jobs: ' || (SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%')::text || '/16' as cron_jobs,
    CASE 
        WHEN (SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%candles%') = 16
         AND (SELECT COUNT(*) FROM pg_proc WHERE proname LIKE 'insert_%_candles_%') = 16
         AND (SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%') = 16
        THEN '✅ ALL SYSTEMS READY'
        ELSE '❌ SETUP INCOMPLETE'
    END as overall_status;
