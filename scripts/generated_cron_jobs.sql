
-- ============================================
-- Automated Cron Job Setup for All Instruments
-- Total: 16 cron jobs (4 instruments × 4 timeframes)
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove existing jobs to avoid duplicates
DO $$ 
DECLARE
    job_record RECORD;
BEGIN
    FOR job_record IN 
        SELECT jobid FROM cron.job 
        WHERE jobname LIKE 'fetch-nq-%'
           OR jobname LIKE 'fetch-mnq-%'
           OR jobname LIKE 'fetch-es-%'
           OR jobname LIKE 'fetch-mes-%'
    LOOP
        PERFORM cron.unschedule(job_record.jobid);
    END LOOP;
END $$;



-- ============================================
-- NQ (NQZ5)
-- ============================================


-- NQ 5-minute candles
SELECT cron.schedule(
    'fetch-nq-5min',
    '*/5 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 5, "symbol": "NQZ5"}'
    )::http_request);
    $$
);


-- NQ 15-minute candles
SELECT cron.schedule(
    'fetch-nq-15min',
    '*/15 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 15, "symbol": "NQZ5"}'
    )::http_request);
    $$
);


-- NQ 30-minute candles
SELECT cron.schedule(
    'fetch-nq-30min',
    '*/30 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 30, "symbol": "NQZ5"}'
    )::http_request);
    $$
);


-- NQ 60-minute candles
SELECT cron.schedule(
    'fetch-nq-60min',
    '0 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 60, "symbol": "NQZ5"}'
    )::http_request);
    $$
);


-- ============================================
-- MNQ (MNQZ5)
-- ============================================


-- MNQ 5-minute candles
SELECT cron.schedule(
    'fetch-mnq-5min',
    '*/5 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 5, "symbol": "MNQZ5"}'
    )::http_request);
    $$
);


-- MNQ 15-minute candles
SELECT cron.schedule(
    'fetch-mnq-15min',
    '*/15 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 15, "symbol": "MNQZ5"}'
    )::http_request);
    $$
);


-- MNQ 30-minute candles
SELECT cron.schedule(
    'fetch-mnq-30min',
    '*/30 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 30, "symbol": "MNQZ5"}'
    )::http_request);
    $$
);


-- MNQ 60-minute candles
SELECT cron.schedule(
    'fetch-mnq-60min',
    '0 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 60, "symbol": "MNQZ5"}'
    )::http_request);
    $$
);


-- ============================================
-- ES (ESZ5)
-- ============================================


-- ES 5-minute candles
SELECT cron.schedule(
    'fetch-es-5min',
    '*/5 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 5, "symbol": "ESZ5"}'
    )::http_request);
    $$
);


-- ES 15-minute candles
SELECT cron.schedule(
    'fetch-es-15min',
    '*/15 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 15, "symbol": "ESZ5"}'
    )::http_request);
    $$
);


-- ES 30-minute candles
SELECT cron.schedule(
    'fetch-es-30min',
    '*/30 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 30, "symbol": "ESZ5"}'
    )::http_request);
    $$
);


-- ES 60-minute candles
SELECT cron.schedule(
    'fetch-es-60min',
    '0 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 60, "symbol": "ESZ5"}'
    )::http_request);
    $$
);


-- ============================================
-- MES (MESZ5)
-- ============================================


-- MES 5-minute candles
SELECT cron.schedule(
    'fetch-mes-5min',
    '*/5 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 5, "symbol": "MESZ5"}'
    )::http_request);
    $$
);


-- MES 15-minute candles
SELECT cron.schedule(
    'fetch-mes-15min',
    '*/15 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 15, "symbol": "MESZ5"}'
    )::http_request);
    $$
);


-- MES 30-minute candles
SELECT cron.schedule(
    'fetch-mes-30min',
    '*/30 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 30, "symbol": "MESZ5"}'
    )::http_request);
    $$
);


-- MES 60-minute candles
SELECT cron.schedule(
    'fetch-mes-60min',
    '0 * * * *',
    $$
    SELECT status, content::json->>'success' as success
    FROM http((
        'POST',
        'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
        ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
        'application/json',
        '{"timeframe": 60, "symbol": "MESZ5"}'
    )::http_request);
    $$
);


-- ============================================
-- Verification - List All Cron Jobs
-- ============================================
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    CASE 
        WHEN schedule = '*/5 * * * *' THEN 'Every 5 minutes'
        WHEN schedule = '*/15 * * * *' THEN 'Every 15 minutes'
        WHEN schedule = '*/30 * * * *' THEN 'Every 30 minutes'
        WHEN schedule = '0 * * * *' THEN 'Every hour'
    END as frequency
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 1
        WHEN jobname LIKE 'fetch-mnq-%' THEN 2
        WHEN jobname LIKE 'fetch-es-%' THEN 3
        WHEN jobname LIKE 'fetch-mes-%' THEN 4
    END,
    jobname;

-- Summary by instrument
SELECT 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 'NQ (E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-mnq-%' THEN 'MNQ (Micro E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-es-%' THEN 'ES (E-mini S&P 500)'
        WHEN jobname LIKE 'fetch-mes-%' THEN 'MES (Micro E-mini S&P 500)'
    END as instrument,
    COUNT(*) as cron_jobs_count
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
GROUP BY 
    CASE 
        WHEN jobname LIKE 'fetch-nq-%' THEN 'NQ (E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-mnq-%' THEN 'MNQ (Micro E-mini Nasdaq)'
        WHEN jobname LIKE 'fetch-es-%' THEN 'ES (E-mini S&P 500)'
        WHEN jobname LIKE 'fetch-mes-%' THEN 'MES (Micro E-mini S&P 500)'
    END
ORDER BY instrument;
