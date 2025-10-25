-- Setup Cron Jobs for All Instruments and Timeframes
-- Run this in Supabase SQL Editor after creating tables and functions
-- Total: 16 cron jobs (4 instruments × 4 timeframes)

-- IMPORTANT: Make sure these extensions are enabled first
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove any existing jobs to avoid duplicates
DO $$ 
DECLARE
    job_record RECORD;
BEGIN
    FOR job_record IN 
        SELECT jobid FROM cron.job 
        WHERE jobname LIKE 'fetch-candles-%' 
           OR jobname LIKE 'fetch-mnq-%'
           OR jobname LIKE 'fetch-es-%'
           OR jobname LIKE 'fetch-mes-%'
    LOOP
        PERFORM cron.unschedule(job_record.jobid);
    END LOOP;
END $$;

-- Service role key for authentication
-- Replace with your actual key if different
DO $$
DECLARE
    service_key TEXT := 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w';
    base_url TEXT := 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles';
BEGIN
    -- ============================================
    -- NQ (E-mini Nasdaq) - Symbol: NQZ5
    -- ============================================
    
    -- NQ 5-minute (every 5 minutes)
    PERFORM cron.schedule(
        'fetch-nq-5min',
        '*/5 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 5, "symbol": "NQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- NQ 15-minute (every 15 minutes)
    PERFORM cron.schedule(
        'fetch-nq-15min',
        '*/15 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 15, "symbol": "NQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- NQ 30-minute (every 30 minutes)
    PERFORM cron.schedule(
        'fetch-nq-30min',
        '*/30 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 30, "symbol": "NQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- NQ 1-hour (every hour)
    PERFORM cron.schedule(
        'fetch-nq-1hour',
        '0 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 60, "symbol": "NQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ============================================
    -- MNQ (Micro E-mini Nasdaq) - Symbol: MNQZ5
    -- ============================================
    
    -- MNQ 5-minute (every 5 minutes)
    PERFORM cron.schedule(
        'fetch-mnq-5min',
        '*/5 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 5, "symbol": "MNQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MNQ 15-minute (every 15 minutes)
    PERFORM cron.schedule(
        'fetch-mnq-15min',
        '*/15 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 15, "symbol": "MNQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MNQ 30-minute (every 30 minutes)
    PERFORM cron.schedule(
        'fetch-mnq-30min',
        '*/30 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 30, "symbol": "MNQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MNQ 1-hour (every hour)
    PERFORM cron.schedule(
        'fetch-mnq-1hour',
        '0 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 60, "symbol": "MNQZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ============================================
    -- ES (E-mini S&P 500) - Symbol: ESZ5
    -- ============================================
    
    -- ES 5-minute (every 5 minutes)
    PERFORM cron.schedule(
        'fetch-es-5min',
        '*/5 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 5, "symbol": "ESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ES 15-minute (every 15 minutes)
    PERFORM cron.schedule(
        'fetch-es-15min',
        '*/15 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 15, "symbol": "ESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ES 30-minute (every 30 minutes)
    PERFORM cron.schedule(
        'fetch-es-30min',
        '*/30 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 30, "symbol": "ESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ES 1-hour (every hour)
    PERFORM cron.schedule(
        'fetch-es-1hour',
        '0 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 60, "symbol": "ESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- ============================================
    -- MES (Micro E-mini S&P 500) - Symbol: MESZ5
    -- ============================================
    
    -- MES 5-minute (every 5 minutes)
    PERFORM cron.schedule(
        'fetch-mes-5min',
        '*/5 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 5, "symbol": "MESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MES 15-minute (every 15 minutes)
    PERFORM cron.schedule(
        'fetch-mes-15min',
        '*/15 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 15, "symbol": "MESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MES 30-minute (every 30 minutes)
    PERFORM cron.schedule(
        'fetch-mes-30min',
        '*/30 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 30, "symbol": "MESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );

    -- MES 1-hour (every hour)
    PERFORM cron.schedule(
        'fetch-mes-1hour',
        '0 * * * *',
        format($cmd$
        SELECT status, content::json->>'success' as success
        FROM http((
            'POST',
            '%s',
            ARRAY[http_header('Content-Type', 'application/json'), http_header('Authorization', '%s')],
            'application/json',
            '{"timeframe": 60, "symbol": "MESZ5"}'
        )::http_request);
        $cmd$, base_url, service_key)
    );
END $$;

-- ============================================
-- Verification Query
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

-- Show summary
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
