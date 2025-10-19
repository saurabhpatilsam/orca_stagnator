-- ============================================================================
-- CREATE TICK DATA TABLES FOR ES AND NQ
-- ============================================================================
-- Run this SQL in your Supabase SQL Editor to create the required tables
-- ============================================================================

-- 1. Create ticks_es table for ES (E-mini S&P 500) tick data
CREATE TABLE IF NOT EXISTS ticks_es (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for fast queries on ticks_es
CREATE INDEX IF NOT EXISTS idx_ticks_es_ts ON ticks_es(ts DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_es_ts_asc ON ticks_es(ts ASC);
CREATE INDEX IF NOT EXISTS idx_ticks_es_created_at ON ticks_es(created_at);

-- Add comments for ticks_es
COMMENT ON TABLE ticks_es IS 'Stores tick-by-tick data for ES (E-mini S&P 500)';
COMMENT ON COLUMN ticks_es.ts IS 'Timestamp of the tick (YYYYMMDD HHMMSS format)';
COMMENT ON COLUMN ticks_es.bid IS 'Bid price';
COMMENT ON COLUMN ticks_es.ask IS 'Ask price';
COMMENT ON COLUMN ticks_es.last IS 'Last traded price';
COMMENT ON COLUMN ticks_es.vol IS 'Volume at this tick';

-- ============================================================================

-- 2. Create ticks_nq table for NQ (E-mini NASDAQ-100) tick data
CREATE TABLE IF NOT EXISTS ticks_nq (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for fast queries on ticks_nq
CREATE INDEX IF NOT EXISTS idx_ticks_nq_ts ON ticks_nq(ts DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_nq_ts_asc ON ticks_nq(ts ASC);
CREATE INDEX IF NOT EXISTS idx_ticks_nq_created_at ON ticks_nq(created_at);

-- Add comments for ticks_nq
COMMENT ON TABLE ticks_nq IS 'Stores tick-by-tick data for NQ (E-mini NASDAQ-100)';
COMMENT ON COLUMN ticks_nq.ts IS 'Timestamp of the tick (YYYYMMDD HHMMSS format)';
COMMENT ON COLUMN ticks_nq.bid IS 'Bid price';
COMMENT ON COLUMN ticks_nq.ask IS 'Ask price';
COMMENT ON COLUMN ticks_nq.last IS 'Last traded price';
COMMENT ON COLUMN ticks_nq.vol IS 'Volume at this tick';

-- ============================================================================
-- DISABLE ROW LEVEL SECURITY (RLS) FOR BACKEND ACCESS
-- ============================================================================
-- This allows the service_role key to insert data without RLS restrictions

ALTER TABLE ticks_es DISABLE ROW LEVEL SECURITY;
ALTER TABLE ticks_nq DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================
-- Tables created:
--   ✅ ticks_es  - For ES (E-mini S&P 500) tick data
--   ✅ ticks_nq  - For NQ (E-mini NASDAQ-100) tick data
--
-- Next steps:
--   1. Go to Supabase Dashboard → SQL Editor
--   2. Paste and run this entire SQL script
--   3. Upload your TXT files through the web interface
-- ============================================================================

-- Example query to view data:
-- SELECT * FROM ticks_nq ORDER BY ts DESC LIMIT 100;
-- SELECT COUNT(*) FROM ticks_nq;
