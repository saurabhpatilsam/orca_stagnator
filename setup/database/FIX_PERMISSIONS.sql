-- ========================================
-- FIX RPC FUNCTION PERMISSIONS
-- ========================================
-- This grants the necessary permissions so edge functions can call the RPC functions

-- Grant execute permissions to all roles that might need them
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_5min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_15min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_30min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_nq_candles_1hour TO anon, authenticated, service_role;

GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_5min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_15min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_30min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mnq_candles_1hour TO anon, authenticated, service_role;

GRANT EXECUTE ON FUNCTION public.insert_es_candles_5min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_15min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_30min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_es_candles_1hour TO anon, authenticated, service_role;

GRANT EXECUTE ON FUNCTION public.insert_mes_candles_5min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_15min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_30min TO anon, authenticated, service_role;
GRANT EXECUTE ON FUNCTION public.insert_mes_candles_1hour TO anon, authenticated, service_role;

-- Also grant access to the orca schema tables
GRANT ALL ON ALL TABLES IN SCHEMA orca TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA orca TO anon, authenticated, service_role;

SELECT 'Permissions granted successfully!' as status;
