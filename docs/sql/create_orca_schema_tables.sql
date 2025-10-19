-- ============================================================================
-- CREATE TICK DATA TABLES IN ORCA SCHEMA
-- ============================================================================
-- Run this in your Supabase SQL Editor
-- ============================================================================

-- 1. Create orca schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS orca;

-- 2. Create ticks_es table in orca schema
CREATE TABLE IF NOT EXISTS orca.ticks_es (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create ticks_nq table in orca schema
CREATE TABLE IF NOT EXISTS orca.ticks_nq (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Create indexes for fast queries on ticks_es
CREATE INDEX IF NOT EXISTS idx_orca_ticks_es_ts ON orca.ticks_es(ts DESC);
CREATE INDEX IF NOT EXISTS idx_orca_ticks_es_ts_asc ON orca.ticks_es(ts ASC);
CREATE INDEX IF NOT EXISTS idx_orca_ticks_es_created_at ON orca.ticks_es(created_at);

-- 5. Create indexes for fast queries on ticks_nq
CREATE INDEX IF NOT EXISTS idx_orca_ticks_nq_ts ON orca.ticks_nq(ts DESC);
CREATE INDEX IF NOT EXISTS idx_orca_ticks_nq_ts_asc ON orca.ticks_nq(ts ASC);
CREATE INDEX IF NOT EXISTS idx_orca_ticks_nq_created_at ON orca.ticks_nq(created_at);

-- 6. Disable Row Level Security (RLS) for service role access
ALTER TABLE orca.ticks_es DISABLE ROW LEVEL SECURITY;
ALTER TABLE orca.ticks_nq DISABLE ROW LEVEL SECURITY;

-- 7. Grant all privileges to service role
GRANT USAGE ON SCHEMA orca TO service_role;
GRANT USAGE ON SCHEMA orca TO authenticated;

GRANT ALL ON orca.ticks_es TO service_role;
GRANT ALL ON orca.ticks_nq TO service_role;

-- 8. Grant sequence usage
GRANT USAGE, SELECT ON SEQUENCE orca.ticks_es_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE orca.ticks_nq_id_seq TO service_role;

-- 9. Set search path to include orca schema (optional)
-- ALTER DATABASE postgres SET search_path TO orca, public;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify:

-- List tables in orca schema
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'orca';

-- Check table structures
\d orca.ticks_es
\d orca.ticks_nq

-- Verify row counts (should be 0)
SELECT COUNT(*) FROM orca.ticks_es;
SELECT COUNT(*) FROM orca.ticks_nq;
