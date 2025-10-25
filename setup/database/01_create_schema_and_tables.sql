-- ========================================
-- STEP 1: CREATE SCHEMA AND TABLES
-- ========================================
-- Run this in Supabase SQL Editor
-- Creates all tables for all instruments and timeframes

-- Create schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS orca;

-- Set search path
SET search_path TO orca, public;

-- Drop existing tables if needed (optional - uncomment if you want to reset)
-- DROP TABLE IF EXISTS orca.nq_candles_5min CASCADE;
-- DROP TABLE IF EXISTS orca.nq_candles_15min CASCADE;
-- DROP TABLE IF EXISTS orca.nq_candles_30min CASCADE;
-- DROP TABLE IF EXISTS orca.nq_candles_1hour CASCADE;
-- DROP TABLE IF EXISTS orca.mnq_candles_5min CASCADE;
-- DROP TABLE IF EXISTS orca.mnq_candles_15min CASCADE;
-- DROP TABLE IF EXISTS orca.mnq_candles_30min CASCADE;
-- DROP TABLE IF EXISTS orca.mnq_candles_1hour CASCADE;
-- DROP TABLE IF EXISTS orca.es_candles_5min CASCADE;
-- DROP TABLE IF EXISTS orca.es_candles_15min CASCADE;
-- DROP TABLE IF EXISTS orca.es_candles_30min CASCADE;
-- DROP TABLE IF EXISTS orca.es_candles_1hour CASCADE;
-- DROP TABLE IF EXISTS orca.mes_candles_5min CASCADE;
-- DROP TABLE IF EXISTS orca.mes_candles_15min CASCADE;
-- DROP TABLE IF EXISTS orca.mes_candles_30min CASCADE;
-- DROP TABLE IF EXISTS orca.mes_candles_1hour CASCADE;

-- ============================================
-- NQ (E-mini Nasdaq) Tables
-- ============================================

CREATE TABLE IF NOT EXISTS orca.nq_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.nq_candles_15min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.nq_candles_30min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.nq_candles_1hour (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

-- ============================================
-- MNQ (Micro E-mini Nasdaq) Tables
-- ============================================

CREATE TABLE IF NOT EXISTS orca.mnq_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mnq_candles_15min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mnq_candles_30min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mnq_candles_1hour (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

-- ============================================
-- ES (E-mini S&P 500) Tables
-- ============================================

CREATE TABLE IF NOT EXISTS orca.es_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.es_candles_15min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.es_candles_30min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.es_candles_1hour (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

-- ============================================
-- MES (Micro E-mini S&P 500) Tables
-- ============================================

CREATE TABLE IF NOT EXISTS orca.mes_candles_5min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mes_candles_15min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mes_candles_30min (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

CREATE TABLE IF NOT EXISTS orca.mes_candles_1hour (
    id BIGSERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    candle_time TIMESTAMPTZ NOT NULL,
    open DECIMAL(12, 4) NOT NULL,
    high DECIMAL(12, 4) NOT NULL,
    low DECIMAL(12, 4) NOT NULL,
    close DECIMAL(12, 4) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    up_volume BIGINT DEFAULT 0,
    down_volume BIGINT DEFAULT 0,
    up_ticks INTEGER DEFAULT 0,
    down_ticks INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, candle_time)
);

-- Create indexes for all tables
CREATE INDEX IF NOT EXISTS idx_nq_5min_time ON orca.nq_candles_5min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_15min_time ON orca.nq_candles_15min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_30min_time ON orca.nq_candles_30min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_1hour_time ON orca.nq_candles_1hour(candle_time DESC);

CREATE INDEX IF NOT EXISTS idx_mnq_5min_time ON orca.mnq_candles_5min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_15min_time ON orca.mnq_candles_15min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_30min_time ON orca.mnq_candles_30min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_1hour_time ON orca.mnq_candles_1hour(candle_time DESC);

CREATE INDEX IF NOT EXISTS idx_es_5min_time ON orca.es_candles_5min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_15min_time ON orca.es_candles_15min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_30min_time ON orca.es_candles_30min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_1hour_time ON orca.es_candles_1hour(candle_time DESC);

CREATE INDEX IF NOT EXISTS idx_mes_5min_time ON orca.mes_candles_5min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_15min_time ON orca.mes_candles_15min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_30min_time ON orca.mes_candles_30min(candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_1hour_time ON orca.mes_candles_1hour(candle_time DESC);

-- Grant permissions
GRANT ALL ON ALL TABLES IN SCHEMA orca TO postgres, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA orca TO postgres, authenticated, service_role;

-- Verify tables were created
SELECT 'Tables created: ' || COUNT(*)::text as status
FROM pg_tables 
WHERE schemaname = 'orca' AND tablename LIKE '%candles%';
