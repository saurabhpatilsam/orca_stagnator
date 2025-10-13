-- ============================================================================
-- SUPABASE TRADING SIGNALS TABLE SETUP
-- ============================================================================
-- This SQL script creates the necessary tables and triggers for the 
-- trading signal system that integrates with Tradovate API
-- ============================================================================

-- 1. Create the trading_signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Signal metadata
    signal_id VARCHAR(100) UNIQUE NOT NULL,  -- Unique identifier from strategy
    strategy_name VARCHAR(100) NOT NULL,      -- Name of the strategy generating signal
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Order details
    instrument VARCHAR(50) NOT NULL,          -- Trading instrument (e.g., 'MNQZ5')
    side VARCHAR(10) NOT NULL CHECK (side IN ('buy', 'sell')),
    order_type VARCHAR(20) NOT NULL DEFAULT 'limit' CHECK (order_type IN ('market', 'limit', 'stop')),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(12, 2),                     -- Limit price (NULL for market orders)
    stop_loss DECIMAL(12, 2) DEFAULT 0.0,
    take_profit DECIMAL(12, 2) DEFAULT 0.0,
    
    -- Account information
    account_name VARCHAR(100) NOT NULL,       -- Tradovate account name
    account_id VARCHAR(50),                   -- Tradovate account ID (filled after lookup)
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'processing', 'placed', 'failed', 'cancelled')
    ),
    
    -- Order placement results
    tradovate_order_id VARCHAR(100),          -- Order ID from Tradovate
    error_message TEXT,                       -- Error message if placement failed
    placement_attempts INTEGER DEFAULT 0,     -- Number of placement attempts
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,       -- Additional strategy-specific data
    
    -- Indexes for performance
    CONSTRAINT unique_signal_id UNIQUE (signal_id)
);

-- 2. Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_trading_signals_status ON trading_signals(status);
CREATE INDEX IF NOT EXISTS idx_trading_signals_created_at ON trading_signals(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trading_signals_strategy ON trading_signals(strategy_name);
CREATE INDEX IF NOT EXISTS idx_trading_signals_account ON trading_signals(account_name);

-- 3. Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_trading_signals_updated_at ON trading_signals;
CREATE TRIGGER update_trading_signals_updated_at
    BEFORE UPDATE ON trading_signals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Create order_history table for tracking all order events
CREATE TABLE IF NOT EXISTS order_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_id UUID REFERENCES trading_signals(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,          -- 'created', 'placed', 'filled', 'cancelled', 'failed'
    event_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_order_history_signal_id ON order_history(signal_id);
CREATE INDEX IF NOT EXISTS idx_order_history_created_at ON order_history(created_at DESC);

-- 6. Enable Row Level Security (RLS) - IMPORTANT for production
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_history ENABLE ROW LEVEL SECURITY;

-- 7. Create policies for authenticated users (adjust based on your auth setup)
-- For now, allow all operations for authenticated users
CREATE POLICY "Allow all operations for authenticated users" ON trading_signals
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Allow all operations for authenticated users" ON order_history
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- 8. Create a view for active signals
CREATE OR REPLACE VIEW active_signals AS
SELECT 
    id,
    signal_id,
    strategy_name,
    instrument,
    side,
    order_type,
    quantity,
    price,
    status,
    created_at,
    account_name
FROM trading_signals
WHERE status IN ('pending', 'processing')
ORDER BY created_at DESC;

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================
-- Next steps:
-- 1. Run this SQL in your Supabase SQL Editor
-- 2. Update your Supabase connection details in .env file
-- 3. Use the Python scripts to send signals and listen for updates
-- ============================================================================

-- Example query to view all signals:
-- SELECT * FROM trading_signals ORDER BY created_at DESC LIMIT 10;

-- Example query to view pending signals:
-- SELECT * FROM active_signals;

-- Example query to view order history:
-- SELECT * FROM order_history WHERE signal_id = 'your-signal-uuid' ORDER BY created_at DESC;
