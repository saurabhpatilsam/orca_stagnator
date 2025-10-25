-- Create RPC Insert Functions for All Instruments
-- Run this AFTER creating tables
-- Total: 16 functions (4 instruments × 4 timeframes)

-- ============================================
-- NQ (E-mini Nasdaq) Insert Functions
-- ============================================

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

-- ============================================
-- MNQ (Micro E-mini Nasdaq) Insert Functions
-- ============================================

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

-- ============================================
-- ES (E-mini S&P 500) Insert Functions
-- ============================================

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

-- ============================================
-- MES (Micro E-mini S&P 500) Insert Functions
-- ============================================

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

-- ============================================
-- Grant Execute Permissions
-- ============================================

GRANT EXECUTE ON FUNCTION public.insert_nq_candles_5min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_15min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_30min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_1hour TO authenticated, anon, service_role;

GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_5min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_15min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_30min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_1hour TO authenticated, anon, service_role;

GRANT EXECUTE ON FUNCTION public.insert_es_candles_5min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_15min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_30min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_1hour TO authenticated, anon, service_role;

GRANT EXECUTE ON FUNCTION public.insert_mes_candles_5min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_15min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_30min TO authenticated, anon, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_1hour TO authenticated, anon, service_role;

-- ============================================
-- Verification
-- ============================================

SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE 'insert_%_candles_%'
ORDER BY routine_name;
