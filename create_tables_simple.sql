-- Simple table creation for self-hosted Supabase
-- Run this directly in PostgreSQL

CREATE TABLE IF NOT EXISTS public.ticks_es (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.ticks_nq (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2) NOT NULL,
    vol INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ticks_es_ts ON public.ticks_es(ts DESC);
CREATE INDEX IF NOT EXISTS idx_ticks_nq_ts ON public.ticks_nq(ts DESC);

ALTER TABLE public.ticks_es DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticks_nq DISABLE ROW LEVEL SECURITY;

GRANT ALL ON public.ticks_es TO service_role;
GRANT ALL ON public.ticks_nq TO service_role;
GRANT USAGE ON SEQUENCE public.ticks_es_id_seq TO service_role;
GRANT USAGE ON SEQUENCE public.ticks_nq_id_seq TO service_role;
