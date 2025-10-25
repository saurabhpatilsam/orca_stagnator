-- Test if RPC functions work directly
-- Run this in Supabase SQL Editor to verify functions work

-- Test NQ 5min function
SELECT public.insert_nq_candles_5min(
    'NQZ5',
    NOW(),
    21000.00,
    21010.00,
    20990.00,
    21005.00,
    1000,
    600,
    400,
    10,
    8
);

-- Check if data was inserted
SELECT COUNT(*) as rows_inserted FROM orca.nq_candles_5min WHERE symbol = 'NQZ5';

-- List the data
SELECT * FROM orca.nq_candles_5min WHERE symbol = 'NQZ5' ORDER BY candle_time DESC LIMIT 5;
