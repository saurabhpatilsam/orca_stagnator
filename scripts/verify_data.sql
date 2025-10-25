-- Verify Fresh Data Collection
-- Run this in Supabase SQL Editor to check your data

-- 1. Check row counts for each timeframe
SELECT 
    'nq_candles_5min' as table_name, 
    COUNT(*) as total_candles,
    MIN(candle_time) as oldest_candle,
    MAX(candle_time) as newest_candle
FROM orca.nq_candles_5min
UNION ALL
SELECT 
    'nq_candles_15min', 
    COUNT(*), 
    MIN(candle_time), 
    MAX(candle_time) 
FROM orca.nq_candles_15min
UNION ALL
SELECT 
    'nq_candles_30min', 
    COUNT(*), 
    MIN(candle_time), 
    MAX(candle_time) 
FROM orca.nq_candles_30min
UNION ALL
SELECT 
    'nq_candles_1hour', 
    COUNT(*), 
    MIN(candle_time), 
    MAX(candle_time) 
FROM orca.nq_candles_1hour
ORDER BY table_name;

-- 2. View latest 5 candles from 5-minute table
SELECT 
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.nq_candles_5min
ORDER BY candle_time DESC
LIMIT 5;

-- 3. View latest 5 candles from 15-minute table
SELECT 
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.nq_candles_15min
ORDER BY candle_time DESC
LIMIT 5;

-- 4. View latest 5 candles from 30-minute table
SELECT 
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.nq_candles_30min
ORDER BY candle_time DESC
LIMIT 5;

-- 5. View latest 5 candles from 1-hour table
SELECT 
    candle_time,
    open,
    high,
    low,
    close,
    volume
FROM orca.nq_candles_1hour
ORDER BY candle_time DESC
LIMIT 5;

-- 6. Check for any gaps in data (5-minute example)
SELECT 
    candle_time,
    LEAD(candle_time) OVER (ORDER BY candle_time) as next_candle_time,
    EXTRACT(EPOCH FROM (LEAD(candle_time) OVER (ORDER BY candle_time) - candle_time))/60 as gap_minutes
FROM orca.nq_candles_5min
ORDER BY candle_time DESC
LIMIT 20;
