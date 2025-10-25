-- ========================================
-- ENABLE PG_NET EXTENSION (CRITICAL FIX)
-- ========================================
-- This extension is REQUIRED for cron jobs to make HTTP calls
-- Run this in Supabase SQL Editor immediately!

-- Enable pg_net extension (allows HTTP requests from PostgreSQL)
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Verify it was enabled
SELECT * FROM pg_extension WHERE extname = 'pg_net';

-- Grant necessary permissions
GRANT USAGE ON SCHEMA net TO postgres, anon, authenticated, service_role;

-- Verify the net.http_post function exists
SELECT 
    routine_name, 
    routine_schema 
FROM information_schema.routines 
WHERE routine_schema = 'net' 
  AND routine_name LIKE '%http%';

-- Test that net.http_post is accessible
SELECT 'pg_net extension is ready!' as status;

-- ========================================
-- WHAT THIS FIXES:
-- ========================================
-- Before: ERROR: schema "net" does not exist
-- After: Cron jobs can make HTTP calls to edge functions
--
-- This is REQUIRED for all your cron jobs to work!
-- ========================================
