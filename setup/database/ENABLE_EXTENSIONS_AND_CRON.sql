-- ========================================
-- STEP 1: ENABLE REQUIRED EXTENSIONS
-- ========================================
-- Run this FIRST before creating cron jobs

CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http WITH SCHEMA extensions;

-- Grant permissions
GRANT USAGE ON SCHEMA cron TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cron TO postgres;

SELECT 'Extensions enabled successfully' as status;
