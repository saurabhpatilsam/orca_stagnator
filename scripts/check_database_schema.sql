-- Check Database Schema and Tables
-- Run this in Supabase SQL Editor

-- 1. Check which schemas exist
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name IN ('public', 'orca')
ORDER BY schema_name;

-- 2. Check if candle tables exist and in which schema
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE tablename LIKE '%candles%'
ORDER BY schemaname, tablename;

-- 3. Check if RPC functions exist
SELECT 
    n.nspname as schema_name,
    p.proname as function_name,
    pg_get_function_arguments(p.oid) as arguments
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE p.proname LIKE 'insert_%candles%'
ORDER BY schema_name, function_name;

-- 4. Check cron jobs
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    created_at,
    updated_at
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- 5. Count rows in existing candle tables (if any)
DO $$
DECLARE
    r RECORD;
    row_count INTEGER;
BEGIN
    FOR r IN 
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE tablename LIKE '%candles%'
    LOOP
        EXECUTE format('SELECT COUNT(*) FROM %I.%I', r.schemaname, r.tablename) INTO row_count;
        RAISE NOTICE '% rows in %.%', row_count, r.schemaname, r.tablename;
    END LOOP;
END $$;
