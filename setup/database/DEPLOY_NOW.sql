-- ========================================
-- QUICK DEPLOY - RPC FUNCTIONS & CRON JOBS
-- ========================================
-- Tables already exist, this adds functions and automation
-- Run this in Supabase SQL Editor

-- ========================================
-- STEP 2: CREATE RPC FUNCTIONS
-- ========================================
-- Run this after creating tables
-- Creates all insert functions for all instruments

-- NQ Functions
CREATE OR REPLACE FUNCTION public.insert_nq_candles_5min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.nq_candles_5min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '5min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_nq_candles_15min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.nq_candles_15min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '15min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_nq_candles_30min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.nq_candles_30min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '30min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_nq_candles_1hour(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.nq_candles_1hour (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '1hour');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- MNQ Functions
CREATE OR REPLACE FUNCTION public.insert_mnq_candles_5min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mnq_candles_5min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '5min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mnq_candles_15min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mnq_candles_15min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '15min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mnq_candles_30min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mnq_candles_30min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '30min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mnq_candles_1hour(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mnq_candles_1hour (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '1hour');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- ES Functions
CREATE OR REPLACE FUNCTION public.insert_es_candles_5min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.es_candles_5min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '5min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_es_candles_15min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.es_candles_15min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '15min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_es_candles_30min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.es_candles_30min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '30min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_es_candles_1hour(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.es_candles_1hour (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '1hour');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- MES Functions
CREATE OR REPLACE FUNCTION public.insert_mes_candles_5min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mes_candles_5min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '5min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mes_candles_15min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mes_candles_15min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '15min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mes_candles_30min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mes_candles_30min (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '30min');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.insert_mes_candles_1hour(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMPTZ,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
) RETURNS JSON AS $$
DECLARE
    v_result JSON;
BEGIN
    INSERT INTO orca.mes_candles_1hour (
        symbol, candle_time, open, high, low, close, volume,
        up_volume, down_volume, up_ticks, down_ticks
    ) VALUES (
        p_symbol, p_candle_time, p_open, p_high, p_low, p_close, p_volume,
        p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
    )
    ON CONFLICT (symbol, candle_time) 
    DO UPDATE SET
        open = EXCLUDED.open,
        high = EXCLUDED.high,
        low = EXCLUDED.low,
        close = EXCLUDED.close,
        volume = EXCLUDED.volume,
        up_volume = EXCLUDED.up_volume,
        down_volume = EXCLUDED.down_volume,
        up_ticks = EXCLUDED.up_ticks,
        down_ticks = EXCLUDED.down_ticks,
        updated_at = NOW();
    
    v_result := json_build_object('success', true, 'symbol', p_symbol, 'timeframe', '1hour');
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- Verify functions were created
SELECT 'Functions created: ' || COUNT(*)::text as status
FROM pg_proc 
WHERE proname LIKE 'insert_%_candles_%';


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


-- ========================================
-- DONE! Test with:
-- bash data-collection/verification/test_all_edge_functions.sh
-- ========================================
