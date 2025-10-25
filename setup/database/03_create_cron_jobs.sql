-- ========================================
-- STEP 3: CREATE CRON JOBS
-- ========================================
-- Run this after creating tables and functions
-- Creates all cron jobs for automated data collection

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove any existing jobs to avoid duplicates
DO $$ 
DECLARE
    job_record RECORD;
BEGIN
    FOR job_record IN 
        SELECT jobid FROM cron.job 
        WHERE jobname LIKE 'fetch-%'
    LOOP
        PERFORM cron.unschedule(job_record.jobid);
    END LOOP;
END $$;

-- Service configuration
DO $$
DECLARE
    v_supabase_url TEXT := 'https://dcoukhtfcloqpfmijock.supabase.co';
    v_service_key TEXT := 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w';
BEGIN
    -- NQ Cron Jobs
    PERFORM cron.schedule(
        'fetch-nq-5min',
        '*/5 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 5, "symbol": "NQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-nq-15min',
        '*/15 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 15, "symbol": "NQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-nq-30min',
        '*/30 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 30, "symbol": "NQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-nq-60min',
        '0 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 60, "symbol": "NQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    -- MNQ Cron Jobs
    PERFORM cron.schedule(
        'fetch-mnq-5min',
        '*/5 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 5, "symbol": "MNQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mnq-15min',
        '*/15 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 15, "symbol": "MNQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mnq-30min',
        '*/30 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 30, "symbol": "MNQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mnq-60min',
        '0 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 60, "symbol": "MNQZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    -- ES Cron Jobs
    PERFORM cron.schedule(
        'fetch-es-5min',
        '*/5 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 5, "symbol": "ESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-es-15min',
        '*/15 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 15, "symbol": "ESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-es-30min',
        '*/30 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 30, "symbol": "ESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-es-60min',
        '0 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 60, "symbol": "ESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    -- MES Cron Jobs
    PERFORM cron.schedule(
        'fetch-mes-5min',
        '*/5 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 5, "symbol": "MESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mes-15min',
        '*/15 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 15, "symbol": "MESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mes-30min',
        '*/30 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 30, "symbol": "MESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );

    PERFORM cron.schedule(
        'fetch-mes-60min',
        '0 * * * *',
        format($$
        SELECT
            status,
            content::json->>'success' as success,
            content::json->>'candles_stored' as candles_stored
        FROM http((
            'POST',
            '%s/functions/v1/fetch-candles',
            ARRAY[http_header('Content-Type', 'application/json'),
                  http_header('Authorization', 'Bearer %s')],
            'application/json',
            '{"timeframe": 60, "symbol": "MESZ5"}'
        )::http_request)
        $$, v_supabase_url, v_service_key)
    );
END $$;

-- Verify cron jobs were created
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    created_at
FROM cron.job 
WHERE jobname LIKE 'fetch-%'
ORDER BY jobname;

-- Should show 16 rows (4 instruments × 4 timeframes)
SELECT 'Cron jobs created: ' || COUNT(*)::text as status
FROM cron.job 
WHERE jobname LIKE 'fetch-%';
