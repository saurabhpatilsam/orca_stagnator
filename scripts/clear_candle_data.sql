-- Clear All Candlestick Data
-- This will remove all existing candle data from all timeframe tables
-- Run this in Supabase SQL Editor

BEGIN;

-- Clear 5-minute candles
TRUNCATE TABLE orca.nq_candles_5min;

-- Clear 15-minute candles
TRUNCATE TABLE orca.nq_candles_15min;

-- Clear 30-minute candles
TRUNCATE TABLE orca.nq_candles_30min;

-- Clear 1-hour candles
TRUNCATE TABLE orca.nq_candles_1hour;

-- Clear fetch log (optional - tracks last fetch times)
-- TRUNCATE TABLE orca.candle_fetch_log;

COMMIT;

-- Verify tables are empty
SELECT 'nq_candles_5min' as table_name, COUNT(*) as row_count FROM orca.nq_candles_5min
UNION ALL
SELECT 'nq_candles_15min', COUNT(*) FROM orca.nq_candles_15min
UNION ALL
SELECT 'nq_candles_30min', COUNT(*) FROM orca.nq_candles_30min
UNION ALL
SELECT 'nq_candles_1hour', COUNT(*) FROM orca.nq_candles_1hour
ORDER BY table_name;
