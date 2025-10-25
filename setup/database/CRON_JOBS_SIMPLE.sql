-- ========================================
-- SIMPLIFIED CRON JOB SETUP - ALL 16 STREAMS
-- ========================================
-- This version skips extension setup and goes straight to creating cron jobs
-- Run this in Supabase SQL Editor

-- Remove any existing cron jobs with these names (to avoid duplicates)
DO $$
DECLARE
    job_name TEXT;
BEGIN
    FOR job_name IN 
        SELECT jobname FROM cron.job WHERE jobname LIKE 'fetch-%'
    LOOP
        PERFORM cron.unschedule(job_name);
        RAISE NOTICE 'Unscheduled existing job: %', job_name;
    END LOOP;
END $$;

-- ========================================
-- NQ (E-mini Nasdaq) - 4 timeframes
-- ========================================

-- 1/16: NQ 5-minute
SELECT cron.schedule(
    'fetch-nq-5min',
    '*/5 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 5, "symbol": "NQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 2/16: NQ 15-minute
SELECT cron.schedule(
    'fetch-nq-15min',
    '*/15 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 15, "symbol": "NQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 3/16: NQ 30-minute
SELECT cron.schedule(
    'fetch-nq-30min',
    '*/30 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 30, "symbol": "NQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 4/16: NQ 60-minute
SELECT cron.schedule(
    'fetch-nq-60min',
    '0 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 60, "symbol": "NQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- ========================================
-- MNQ (Micro E-mini Nasdaq) - 4 timeframes
-- ========================================

-- 5/16: MNQ 5-minute
SELECT cron.schedule(
    'fetch-mnq-5min',
    '*/5 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 5, "symbol": "MNQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 6/16: MNQ 15-minute
SELECT cron.schedule(
    'fetch-mnq-15min',
    '*/15 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 15, "symbol": "MNQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 7/16: MNQ 30-minute
SELECT cron.schedule(
    'fetch-mnq-30min',
    '*/30 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 30, "symbol": "MNQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 8/16: MNQ 60-minute
SELECT cron.schedule(
    'fetch-mnq-60min',
    '0 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 60, "symbol": "MNQZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- ========================================
-- ES (E-mini S&P 500) - 4 timeframes
-- ========================================

-- 9/16: ES 5-minute
SELECT cron.schedule(
    'fetch-es-5min',
    '*/5 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 5, "symbol": "ESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 10/16: ES 15-minute
SELECT cron.schedule(
    'fetch-es-15min',
    '*/15 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 15, "symbol": "ESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 11/16: ES 30-minute
SELECT cron.schedule(
    'fetch-es-30min',
    '*/30 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 30, "symbol": "ESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 12/16: ES 60-minute
SELECT cron.schedule(
    'fetch-es-60min',
    '0 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 60, "symbol": "ESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- ========================================
-- MES (Micro E-mini S&P 500) - 4 timeframes
-- ========================================

-- 13/16: MES 5-minute
SELECT cron.schedule(
    'fetch-mes-5min',
    '*/5 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 5, "symbol": "MESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 14/16: MES 15-minute
SELECT cron.schedule(
    'fetch-mes-15min',
    '*/15 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 15, "symbol": "MESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 15/16: MES 30-minute
SELECT cron.schedule(
    'fetch-mes-30min',
    '*/30 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 30, "symbol": "MESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- 16/16: MES 60-minute
SELECT cron.schedule(
    'fetch-mes-60min',
    '0 * * * *',
    $$
    SELECT net.http_post(
        url:='https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        headers:='{"Content-Type": "application/json", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"}'::jsonb,
        body:='{"timeframe": 60, "symbol": "MESZ5"}'::jsonb
    ) AS request_id;
    $$
);

-- ========================================
-- VERIFICATION
-- ========================================

-- Show all created cron jobs
SELECT 
    jobname, 
    schedule, 
    active
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- Show count
SELECT 
    '✅ Total cron jobs created: ' || COUNT(*)::text as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%';
