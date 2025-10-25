-- Direct test of RPC function
-- This will tell us if the function works at all

-- Test calling the function directly
SELECT public.insert_nq_candles_5min(
    'NQZ5'::VARCHAR,
    '2025-10-23 12:00:00+00'::TIMESTAMPTZ,
    21000.00::DECIMAL,
    21010.00::DECIMAL,
    20990.00::DECIMAL,
    21005.00::DECIMAL,
    1000::BIGINT,
    600::BIGINT,
    400::BIGINT,
    10::INTEGER,
    8::INTEGER
) as result;

-- Check if it was inserted
SELECT COUNT(*) as test_rows FROM orca.nq_candles_5min WHERE symbol = 'NQZ5';

-- Show the data
SELECT * FROM orca.nq_candles_5min WHERE symbol = 'NQZ5' ORDER BY candle_time DESC LIMIT 3;
