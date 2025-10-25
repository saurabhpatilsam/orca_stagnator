-- Create Candlestick Tables for All Instruments
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new
-- 
-- Instruments: NQ (E-mini Nasdaq), MNQ (Micro E-mini Nasdaq), ES (E-mini S&P 500), MES (Micro E-mini S&P 500)
-- Timeframes: 5min, 15min, 30min, 1hour
-- Total: 16 tables (4 instruments × 4 timeframes)

-- Ensure schema exists
CREATE SCHEMA IF NOT EXISTS orca;

-- ============================================
-- NQ (E-mini Nasdaq) Tables
-- ============================================

-- NQ 5-minute candles
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

CREATE INDEX IF NOT EXISTS idx_nq_5min_symbol_time ON orca.nq_candles_5min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_5min_time ON orca.nq_candles_5min(candle_time DESC);

-- NQ 15-minute candles
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

CREATE INDEX IF NOT EXISTS idx_nq_15min_symbol_time ON orca.nq_candles_15min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_15min_time ON orca.nq_candles_15min(candle_time DESC);

-- NQ 30-minute candles
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

CREATE INDEX IF NOT EXISTS idx_nq_30min_symbol_time ON orca.nq_candles_30min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_30min_time ON orca.nq_candles_30min(candle_time DESC);

-- NQ 1-hour candles
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

CREATE INDEX IF NOT EXISTS idx_nq_1hour_symbol_time ON orca.nq_candles_1hour(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_nq_1hour_time ON orca.nq_candles_1hour(candle_time DESC);

-- ============================================
-- MNQ (Micro E-mini Nasdaq) Tables
-- ============================================

-- MNQ 5-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mnq_5min_symbol_time ON orca.mnq_candles_5min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_5min_time ON orca.mnq_candles_5min(candle_time DESC);

-- MNQ 15-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mnq_15min_symbol_time ON orca.mnq_candles_15min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_15min_time ON orca.mnq_candles_15min(candle_time DESC);

-- MNQ 30-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mnq_30min_symbol_time ON orca.mnq_candles_30min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_30min_time ON orca.mnq_candles_30min(candle_time DESC);

-- MNQ 1-hour candles
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

CREATE INDEX IF NOT EXISTS idx_mnq_1hour_symbol_time ON orca.mnq_candles_1hour(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mnq_1hour_time ON orca.mnq_candles_1hour(candle_time DESC);

-- ============================================
-- ES (E-mini S&P 500) Tables
-- ============================================

-- ES 5-minute candles
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

CREATE INDEX IF NOT EXISTS idx_es_5min_symbol_time ON orca.es_candles_5min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_5min_time ON orca.es_candles_5min(candle_time DESC);

-- ES 15-minute candles
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

CREATE INDEX IF NOT EXISTS idx_es_15min_symbol_time ON orca.es_candles_15min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_15min_time ON orca.es_candles_15min(candle_time DESC);

-- ES 30-minute candles
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

CREATE INDEX IF NOT EXISTS idx_es_30min_symbol_time ON orca.es_candles_30min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_30min_time ON orca.es_candles_30min(candle_time DESC);

-- ES 1-hour candles
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

CREATE INDEX IF NOT EXISTS idx_es_1hour_symbol_time ON orca.es_candles_1hour(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_es_1hour_time ON orca.es_candles_1hour(candle_time DESC);

-- ============================================
-- MES (Micro E-mini S&P 500) Tables
-- ============================================

-- MES 5-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mes_5min_symbol_time ON orca.mes_candles_5min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_5min_time ON orca.mes_candles_5min(candle_time DESC);

-- MES 15-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mes_15min_symbol_time ON orca.mes_candles_15min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_15min_time ON orca.mes_candles_15min(candle_time DESC);

-- MES 30-minute candles
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

CREATE INDEX IF NOT EXISTS idx_mes_30min_symbol_time ON orca.mes_candles_30min(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_30min_time ON orca.mes_candles_30min(candle_time DESC);

-- MES 1-hour candles
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

CREATE INDEX IF NOT EXISTS idx_mes_1hour_symbol_time ON orca.mes_candles_1hour(symbol, candle_time DESC);
CREATE INDEX IF NOT EXISTS idx_mes_1hour_time ON orca.mes_candles_1hour(candle_time DESC);

-- ============================================
-- Verification Query
-- ============================================

SELECT 
    schemaname, 
    tablename,
    CASE 
        WHEN tablename LIKE '%_5min' THEN '5 minutes'
        WHEN tablename LIKE '%_15min' THEN '15 minutes'
        WHEN tablename LIKE '%_30min' THEN '30 minutes'
        WHEN tablename LIKE '%_1hour' THEN '1 hour'
    END as timeframe
FROM pg_tables
WHERE schemaname = 'orca' 
  AND tablename LIKE '%_candles_%'
ORDER BY tablename;
