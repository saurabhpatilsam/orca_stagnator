-- Complete setup: Tables + RPC Functions + Schema Reload
-- Run this entire script in Supabase SQL Editor

-- =====================================================
-- 1. Create orca schema
-- =====================================================
CREATE SCHEMA IF NOT EXISTS orca;

-- =====================================================
-- 2. Create candle tables (if not exist)
-- =====================================================
CREATE TABLE IF NOT EXISTS orca.nq_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE INDEX IF NOT EXISTS idx_nq_5min_symbol_time ON orca.nq_candles_5min(symbol, candle_time DESC);

CREATE TABLE IF NOT EXISTS orca.nq_candles_15min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE INDEX IF NOT EXISTS idx_nq_15min_symbol_time ON orca.nq_candles_15min(symbol, candle_time DESC);

CREATE TABLE IF NOT EXISTS orca.nq_candles_30min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE INDEX IF NOT EXISTS idx_nq_30min_symbol_time ON orca.nq_candles_30min(symbol, candle_time DESC);

CREATE TABLE IF NOT EXISTS orca.nq_candles_1hour (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE INDEX IF NOT EXISTS idx_nq_1hour_symbol_time ON orca.nq_candles_1hour(symbol, candle_time DESC);

-- =====================================================
-- 3. Create RPC Functions
-- =====================================================

-- Function to insert 5-minute candles
CREATE OR REPLACE FUNCTION public.insert_nq_candles_5min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMP WITH TIME ZONE,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
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
    
    RETURN json_build_object('success', true, 'message', 'Candle inserted/updated');
END;
$$;

-- Function to insert 15-minute candles
CREATE OR REPLACE FUNCTION public.insert_nq_candles_15min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMP WITH TIME ZONE,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
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
    
    RETURN json_build_object('success', true, 'message', 'Candle inserted/updated');
END;
$$;

-- Function to insert 30-minute candles
CREATE OR REPLACE FUNCTION public.insert_nq_candles_30min(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMP WITH TIME ZONE,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
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
    
    RETURN json_build_object('success', true, 'message', 'Candle inserted/updated');
END;
$$;

-- Function to insert 1-hour candles
CREATE OR REPLACE FUNCTION public.insert_nq_candles_1hour(
    p_symbol VARCHAR,
    p_candle_time TIMESTAMP WITH TIME ZONE,
    p_open DECIMAL,
    p_high DECIMAL,
    p_low DECIMAL,
    p_close DECIMAL,
    p_volume BIGINT,
    p_up_volume BIGINT DEFAULT 0,
    p_down_volume BIGINT DEFAULT 0,
    p_up_ticks INTEGER DEFAULT 0,
    p_down_ticks INTEGER DEFAULT 0
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
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
    
    RETURN json_build_object('success', true, 'message', 'Candle inserted/updated');
END;
$$;

-- Function to query candles
CREATE OR REPLACE FUNCTION public.get_nq_candles(
    p_timeframe TEXT,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    candle_time TIMESTAMP WITH TIME ZONE,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT candle_time, open, high, low, close, volume 
         FROM orca.nq_candles_%s 
         ORDER BY candle_time DESC 
         LIMIT $1',
        p_timeframe
    ) USING p_limit;
END;
$$;

-- =====================================================
-- 4. Grant permissions
-- =====================================================
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_5min TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_15min TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_30min TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_1hour TO authenticated, anon;
GRANT EXECUTE ON FUNCTION public.get_nq_candles TO authenticated, anon;

-- =====================================================
-- 5. Reload PostgREST schema
-- =====================================================
NOTIFY pgrst, 'reload schema';

-- Done! Setup complete.
SELECT 'Setup complete! Tables created, RPC functions added, and schema reloaded.' as status;
