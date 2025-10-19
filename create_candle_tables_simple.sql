-- Copy and paste this ENTIRE script into Supabase SQL Editor and click RUN

-- 0. Create orca schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS orca;

-- 1. Create 5-minute candles table
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
CREATE INDEX IF NOT EXISTS idx_nq_5min_time ON orca.nq_candles_5min(candle_time DESC);

-- 2. Create 15-minute candles table
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

-- 3. Create 30-minute candles table
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

-- 4. Create 1-hour candles table
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

-- 5. Grant permissions
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_5min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_15min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_30min TO authenticated;
GRANT SELECT, INSERT, UPDATE ON orca.nq_candles_1hour TO authenticated;

GRANT USAGE ON SEQUENCE orca.nq_candles_5min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_15min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_30min_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE orca.nq_candles_1hour_id_seq TO authenticated;

-- Done! Tables created successfully.
