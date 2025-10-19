-- =====================================================
-- Supabase Tables for OHLC Candle Data Storage
-- =====================================================
-- Created: 2025-10-15
-- Purpose: Store historical candle data for NQ futures
-- Timeframes: 5min, 15min, 30min, 1hour
-- =====================================================

-- Drop existing tables if they exist (careful in production!)
-- DROP TABLE IF EXISTS orca.nq_candles_5min;
-- DROP TABLE IF EXISTS orca.nq_candles_15min;
-- DROP TABLE IF EXISTS orca.nq_candles_30min;
-- DROP TABLE IF EXISTS orca.nq_candles_1hour;

-- =====================================================
-- 0. Create Schema
-- =====================================================
CREATE SCHEMA IF NOT EXISTS orca;

-- =====================================================
-- 1. NQ 5-Minute Candles Table
-- =====================================================
CREATE TABLE IF NOT EXISTS orca.nq_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,                    -- e.g., 'NQZ5', 'NQH6'
    candle_time TIMESTAMP WITH TIME ZONE NOT NULL,  -- Candle start time
    open DECIMAL(10, 2) NOT NULL,                   -- Opening price
    high DECIMAL(10, 2) NOT NULL,                   -- Highest price
    low DECIMAL(10, 2) NOT NULL,                    -- Lowest price
    close DECIMAL(10, 2) NOT NULL,                  -- Closing price
    volume BIGINT NOT NULL DEFAULT 0,               -- Total volume
    up_volume BIGINT DEFAULT 0,                     -- Buy volume
    down_volume BIGINT DEFAULT 0,                   -- Sell volume
    up_ticks INTEGER DEFAULT 0,                     -- Number of upticks
    down_ticks INTEGER DEFAULT 0,                   -- Number of downticks
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique candles per symbol per time
    UNIQUE(symbol, candle_time)
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_nq_5min_symbol_time ON orca.nq_candles_5min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_5min_time ON orca.nq_candles_5min(candle_time DESC);

-- =====================================================
-- 2. NQ 15-Minute Candles Table
-- =====================================================
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
CREATE INDEX IF NOT EXISTS idx_nq_15min_time ON orca.nq_candles_15min(candle_time DESC);

-- =====================================================
-- 3. NQ 30-Minute Candles Table
-- =====================================================
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
CREATE INDEX IF NOT EXISTS idx_nq_30min_time ON orca.nq_candles_30min(candle_time DESC);

-- =====================================================
-- 4. NQ 1-Hour Candles Table
-- =====================================================
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
CREATE INDEX IF NOT EXISTS idx_nq_1hour_time ON orca.nq_candles_1hour(candle_time DESC);

-- =====================================================
-- 5. Function to Update updated_at Timestamp
-- =====================================================
CREATE OR REPLACE FUNCTION orca.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 6. Triggers for Auto-Update Timestamp
-- =====================================================
DROP TRIGGER IF EXISTS update_nq_5min_updated_at ON orca.nq_candles_5min;
CREATE TRIGGER update_nq_5min_updated_at
    BEFORE UPDATE ON orca.nq_candles_5min
    FOR EACH ROW
    EXECUTE FUNCTION orca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_nq_15min_updated_at ON orca.nq_candles_15min;
CREATE TRIGGER update_nq_15min_updated_at
    BEFORE UPDATE ON orca.nq_candles_15min
    FOR EACH ROW
    EXECUTE FUNCTION orca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_nq_30min_updated_at ON orca.nq_candles_30min;
CREATE TRIGGER update_nq_30min_updated_at
    BEFORE UPDATE ON orca.nq_candles_30min
    FOR EACH ROW
    EXECUTE FUNCTION orca.update_updated_at_column();

DROP TRIGGER IF EXISTS update_nq_1hour_updated_at ON orca.nq_candles_1hour;
CREATE TRIGGER update_nq_1hour_updated_at
    BEFORE UPDATE ON orca.nq_candles_1hour
    FOR EACH ROW
    EXECUTE FUNCTION orca.update_updated_at_column();

-- =====================================================
-- 7. Helper Functions for Querying Candles
-- =====================================================

-- Get latest N candles for a specific timeframe
CREATE OR REPLACE FUNCTION orca.get_latest_candles(
    p_timeframe TEXT,
    p_symbol TEXT,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    candle_time TIMESTAMP WITH TIME ZONE,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT candle_time, open, high, low, close, volume 
         FROM orca.nq_candles_%s 
         WHERE symbol = $1 
         ORDER BY candle_time DESC 
         LIMIT $2',
        p_timeframe
    ) USING p_symbol, p_limit;
END;
$$ LANGUAGE plpgsql;

-- Get candles within a time range
CREATE OR REPLACE FUNCTION orca.get_candles_range(
    p_timeframe TEXT,
    p_symbol TEXT,
    p_start_time TIMESTAMP WITH TIME ZONE,
    p_end_time TIMESTAMP WITH TIME ZONE
)
RETURNS TABLE (
    candle_time TIMESTAMP WITH TIME ZONE,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT candle_time, open, high, low, close, volume 
         FROM orca.nq_candles_%s 
         WHERE symbol = $1 
         AND candle_time >= $2 
         AND candle_time <= $3 
         ORDER BY candle_time ASC',
        p_timeframe
    ) USING p_symbol, p_start_time, p_end_time;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. Grant Permissions (adjust as needed)
-- =====================================================
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_5min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_15min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_30min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_1hour TO authenticated;

GRANT USAGE ON SEQUENCE orca.nq_candles_5min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_15min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_30min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_1hour_id_seq TO authenticated;

-- =====================================================
-- 9. Comments for Documentation
-- =====================================================
COMMENT ON TABLE orca.nq_candles_5min IS 'NQ futures 5-minute OHLC candle data';
COMMENT ON TABLE orca.nq_candles_15min IS 'NQ futures 15-minute OHLC candle data';
COMMENT ON TABLE orca.nq_candles_30min IS 'NQ futures 30-minute OHLC candle data';
COMMENT ON TABLE orca.nq_candles_1hour IS 'NQ futures 1-hour OHLC candle data';

-- =====================================================
-- Done! Tables Created Successfully
-- =====================================================
-- To use:
-- 1. Run this SQL in Supabase SQL Editor
-- 2. Use the automated script to populate data
-- 3. Query with: SELECT * FROM orca.get_latest_candles('5min', 'NQZ5', 50);
-- =====================================================
