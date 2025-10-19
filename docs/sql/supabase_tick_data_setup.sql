-- ============================================================================
-- SUPABASE TICK DATA TABLES SETUP
-- ============================================================================
-- This SQL script creates the necessary tables for storing historical tick data
-- and OHLC candle data for backtesting purposes.
-- ============================================================================

-- 1. Create tick_data table for storing tick-by-tick market data
CREATE TABLE IF NOT EXISTS tick_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    price DECIMAL(12, 2) NOT NULL,
    volume INTEGER DEFAULT 0,
    bid DECIMAL(12, 2),
    ask DECIMAL(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_tick_data_timestamp ON tick_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_tick_data_instrument ON tick_data(instrument);
CREATE INDEX IF NOT EXISTS idx_tick_data_instrument_timestamp ON tick_data(instrument, timestamp);
CREATE INDEX IF NOT EXISTS idx_tick_data_lookup ON tick_data(instrument, timestamp DESC);

-- Add comments
COMMENT ON TABLE tick_data IS 'Stores tick-by-tick market data for backtesting';
COMMENT ON COLUMN tick_data.timestamp IS 'Timestamp of the tick in ET timezone';
COMMENT ON COLUMN tick_data.instrument IS 'Trading instrument (e.g., ESZ5, NQZ5)';
COMMENT ON COLUMN tick_data.price IS 'Last traded price';
COMMENT ON COLUMN tick_data.volume IS 'Volume at this tick';
COMMENT ON COLUMN tick_data.bid IS 'Bid price';
COMMENT ON COLUMN tick_data.ask IS 'Ask price';

-- ============================================================================

-- 2. Create ohlc_data table for storing candle data
CREATE TABLE IF NOT EXISTS ohlc_data (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    timeframe VARCHAR(20) NOT NULL, -- '1h', '5m', '1d', etc.
    open_price DECIMAL(12, 2) NOT NULL,
    high_price DECIMAL(12, 2) NOT NULL,
    low_price DECIMAL(12, 2) NOT NULL,
    close_price DECIMAL(12, 2) NOT NULL,
    volume INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(instrument, timestamp, timeframe)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ohlc_timestamp ON ohlc_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_ohlc_instrument ON ohlc_data(instrument);
CREATE INDEX IF NOT EXISTS idx_ohlc_timeframe ON ohlc_data(timeframe);
CREATE INDEX IF NOT EXISTS idx_ohlc_lookup ON ohlc_data(instrument, timeframe, timestamp DESC);

-- Add comments
COMMENT ON TABLE ohlc_data IS 'Stores OHLC candle data for various timeframes';
COMMENT ON COLUMN ohlc_data.timestamp IS 'Candle start time in ET timezone';
COMMENT ON COLUMN ohlc_data.instrument IS 'Trading instrument (e.g., ESZ5, NQZ5)';
COMMENT ON COLUMN ohlc_data.timeframe IS 'Candle timeframe (1m, 5m, 15m, 1h, 1d, etc.)';
COMMENT ON COLUMN ohlc_data.open_price IS 'Opening price of the candle';
COMMENT ON COLUMN ohlc_data.high_price IS 'Highest price in the candle';
COMMENT ON COLUMN ohlc_data.low_price IS 'Lowest price in the candle';
COMMENT ON COLUMN ohlc_data.close_price IS 'Closing price of the candle';

-- ============================================================================

-- 3. Create backtest_results table for storing backtest performance
CREATE TABLE IF NOT EXISTS backtest_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_date DATE NOT NULL,
    instrument VARCHAR(50) NOT NULL,
    strategy_name VARCHAR(100) NOT NULL,
    first_hour_high DECIMAL(12, 2) NOT NULL,
    first_hour_low DECIMAL(12, 2) NOT NULL,
    total_orders INTEGER NOT NULL,
    filled_orders INTEGER NOT NULL,
    winning_trades INTEGER NOT NULL,
    losing_trades INTEGER NOT NULL,
    total_pnl DECIMAL(12, 2) NOT NULL,
    win_rate DECIMAL(5, 2) NOT NULL,
    average_win DECIMAL(12, 2),
    average_loss DECIMAL(12, 2),
    largest_win DECIMAL(12, 2),
    largest_loss DECIMAL(12, 2),
    total_ticks_processed INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_backtest_results_date ON backtest_results(test_date DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_results_instrument ON backtest_results(instrument);
CREATE INDEX IF NOT EXISTS idx_backtest_results_strategy ON backtest_results(strategy_name);

-- Add comments
COMMENT ON TABLE backtest_results IS 'Stores backtest performance results';
COMMENT ON COLUMN backtest_results.test_date IS 'Date of the backtest';
COMMENT ON COLUMN backtest_results.total_pnl IS 'Total profit/loss for the day';
COMMENT ON COLUMN backtest_results.win_rate IS 'Percentage of winning trades';

-- ============================================================================

-- 4. Create backtest_trades table for storing individual trade details
CREATE TABLE IF NOT EXISTS backtest_trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backtest_id UUID REFERENCES backtest_results(id) ON DELETE CASCADE,
    order_id INTEGER NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('long', 'short')),
    entry_price DECIMAL(12, 2) NOT NULL,
    stop_loss DECIMAL(12, 2) NOT NULL,
    take_profit DECIMAL(12, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    fill_time TIMESTAMP WITH TIME ZONE,
    fill_price DECIMAL(12, 2),
    exit_time TIMESTAMP WITH TIME ZONE,
    exit_price DECIMAL(12, 2),
    exit_reason VARCHAR(50),
    pnl DECIMAL(12, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest_id ON backtest_trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_backtest_trades_status ON backtest_trades(status);

-- Add comments
COMMENT ON TABLE backtest_trades IS 'Stores individual trade details from backtests';
COMMENT ON COLUMN backtest_trades.backtest_id IS 'Reference to parent backtest result';
COMMENT ON COLUMN backtest_trades.pnl IS 'Profit/loss for this individual trade';

-- ============================================================================

-- 5. Create helper function to get tick data for a date range
CREATE OR REPLACE FUNCTION get_tick_data_for_date(
    p_instrument VARCHAR,
    p_date DATE,
    p_start_hour INTEGER DEFAULT 10,
    p_start_minute INTEGER DEFAULT 30,
    p_end_hour INTEGER DEFAULT 16,
    p_end_minute INTEGER DEFAULT 0
)
RETURNS TABLE (
    timestamp TIMESTAMP WITH TIME ZONE,
    price DECIMAL(12, 2),
    volume INTEGER,
    bid DECIMAL(12, 2),
    ask DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.timestamp,
        t.price,
        t.volume,
        t.bid,
        t.ask
    FROM tick_data t
    WHERE t.instrument = p_instrument
    AND t.timestamp::date = p_date
    AND EXTRACT(HOUR FROM t.timestamp) >= p_start_hour
    AND EXTRACT(HOUR FROM t.timestamp) < p_end_hour
    ORDER BY t.timestamp ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================

-- 6. Create helper function to get first hour candle
CREATE OR REPLACE FUNCTION get_first_hour_candle(
    p_instrument VARCHAR,
    p_date DATE
)
RETURNS TABLE (
    open_price DECIMAL(12, 2),
    high_price DECIMAL(12, 2),
    low_price DECIMAL(12, 2),
    close_price DECIMAL(12, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.open_price,
        o.high_price,
        o.low_price,
        o.close_price
    FROM ohlc_data o
    WHERE o.instrument = p_instrument
    AND o.timestamp::date = p_date
    AND o.timeframe = '1h'
    AND EXTRACT(HOUR FROM o.timestamp) = 9
    AND EXTRACT(MINUTE FROM o.timestamp) = 30
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================

-- 7. Enable Row Level Security (optional - adjust based on your needs)
-- ALTER TABLE tick_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ohlc_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE backtest_results ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE backtest_trades ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================
-- Next steps:
-- 1. Run this SQL in your Supabase SQL Editor
-- 2. Import historical tick data into tick_data table
-- 3. Import OHLC data into ohlc_data table (optional)
-- 4. Run backtests using backtest.py
-- ============================================================================

-- Example queries:

-- View tick data for a specific date:
-- SELECT * FROM tick_data 
-- WHERE instrument = 'ESZ5' 
-- AND timestamp::date = '2025-10-09'
-- ORDER BY timestamp
-- LIMIT 100;

-- View first hour candle:
-- SELECT * FROM get_first_hour_candle('ESZ5', '2025-10-09');

-- View tick data from first hour close onwards:
-- SELECT * FROM get_tick_data_for_date('ESZ5', '2025-10-09');

-- View backtest results:
-- SELECT * FROM backtest_results ORDER BY test_date DESC LIMIT 10;

-- View trades for a specific backtest:
-- SELECT * FROM backtest_trades WHERE backtest_id = 'your-backtest-uuid';
