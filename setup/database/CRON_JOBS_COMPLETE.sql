-- ========================================
-- AUTOMATED CRON JOB SETUP - ALL 16 STREAMS
-- ========================================
-- Copy this entire file and run in Supabase SQL Editor
-- https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

-- Enable pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Remove any existing cron jobs with these names
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

-- Create all 16 cron jobs

-- 1/16: fetch-nq-5min

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


-- 2/16: fetch-nq-15min

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


-- 3/16: fetch-nq-30min

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


-- 4/16: fetch-nq-60min

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


-- 5/16: fetch-mnq-5min

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


-- 6/16: fetch-mnq-15min

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


-- 7/16: fetch-mnq-30min

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


-- 8/16: fetch-mnq-60min

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


-- 9/16: fetch-es-5min

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


-- 10/16: fetch-es-15min

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


-- 11/16: fetch-es-30min

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


-- 12/16: fetch-es-60min

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


-- 13/16: fetch-mes-5min

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


-- 14/16: fetch-mes-15min

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


-- 15/16: fetch-mes-30min

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


-- 16/16: fetch-mes-60min

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


-- Verify cron jobs were created
SELECT 
    jobname, 
    schedule, 
    active,
    command
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- Show count
SELECT 
    'Total cron jobs created: ' || COUNT(*)::text as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%';
