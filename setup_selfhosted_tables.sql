-- ============================================================================
-- CREATE TICK DATA TABLES FOR SELF-HOSTED SUPABASE
-- ============================================================================
-- Run this SQL in your self-hosted Supabase PostgreSQL database
-- ============================================================================

-- 1. Create ticks_es table for ES (E-mini S&P 500)
CREATE TABLE IF NOT EXISTS public.ticks_es (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create ticks_nq table for NQ (E-mini NASDAQ-100)
CREATE TABLE IF NOT EXISTS public.ticks_nq (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Create indexes for fast queries on ticks_es
CREATE INDEX IF NOT EXISTS idx_ticks_es_ts ON public.ticks_es(ts DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_es_ts_asc ON public.ticks_es(ts ASC);
CREATE INDEX IF NOT EXISTS idx_ticks_es_created_at ON public.ticks_es(created_at);

-- 4. Create indexes for fast queries on ticks_nq
CREATE INDEX IF NOT EXISTS idx_ticks_nq_ts ON public.ticks_nq(ts DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_nq_ts_asc ON public.ticks_nq(ts ASC);
CREATE INDEX IF NOT EXISTS idx_ticks_nq_created_at ON public.ticks_nq(created_at);

-- 5. Disable Row Level Security (RLS) for service role access
ALTER TABLE public.ticks_es DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticks_nq DISABLE ROW LEVEL SECURITY;

-- 6. Grant all privileges to authenticated and service roles
GRANT ALL ON public.ticks_es TO authenticated;
GRANT ALL ON public.ticks_es TO service_role;
GRANT ALL ON public.ticks_nq TO authenticated;
GRANT ALL ON public.ticks_nq TO service_role;

-- 7. Grant sequence usage
GRANT USAGE, SELECT ON SEQUENCE public.ticks_es_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.ticks_es_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.ticks_nq_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.ticks_nq_id_seq TO service_role;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these to verify tables were created successfully:

-- Check ticks_es table structure
\d public.ticks_es

-- Check ticks_nq table structure
\d public.ticks_nq

-- Verify row counts (should be 0)
SELECT COUNT(*) FROM public.ticks_es;
SELECT COUNT(*) FROM public.ticks_nq;

-- ============================================================================
-- DONE!
-- ============================================================================
