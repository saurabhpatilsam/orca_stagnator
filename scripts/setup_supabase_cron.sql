-- Setup Supabase Cron Jobs for Automatic Candle Fetching
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new

-- IMPORTANT: Make sure these extensions are enabled first
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove any existing jobs to avoid duplicates
DO $$ 
DECLARE
    job_record RECORD;
BEGIN
    FOR job_record IN 
        SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-candles-%'
    LOOP
        PERFORM cron.unschedule(job_record.jobid);
    END LOOP;
END $$;

-- Schedule 5-minute candles (every 5 minutes)
SELECT cron.schedule(
  'fetch-candles-5min',
  '*/5 * * * *',
  $$
  SELECT 
    status,
    content::json->>'success' as success,
    content::json->>'candles_stored' as candles_stored
  FROM http((
    'POST',
    'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    ARRAY[http_header('Content-Type', 'application/json'), 
          http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
    'application/json',
    '{"timeframe": 5}'
  )::http_request);
  $$
);

-- Schedule 15-minute candles (every 15 minutes)
SELECT cron.schedule(
  'fetch-candles-15min',
  '*/15 * * * *',
  $$
  SELECT 
    status,
    content::json->>'success' as success,
    content::json->>'candles_stored' as candles_stored
  FROM http((
    'POST',
    'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    ARRAY[http_header('Content-Type', 'application/json'), 
          http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
    'application/json',
    '{"timeframe": 15}'
  )::http_request);
  $$
);

-- Schedule 30-minute candles (every 30 minutes)
SELECT cron.schedule(
  'fetch-candles-30min',
  '*/30 * * * *',
  $$
  SELECT 
    status,
    content::json->>'success' as success,
    content::json->>'candles_stored' as candles_stored
  FROM http((
    'POST',
    'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    ARRAY[http_header('Content-Type', 'application/json'), 
          http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
    'application/json',
    '{"timeframe": 30}'
  )::http_request);
  $$
);

-- Schedule 1-hour candles (every hour at minute 0)
SELECT cron.schedule(
  'fetch-candles-1hour',
  '0 * * * *',
  $$
  SELECT 
    status,
    content::json->>'success' as success,
    content::json->>'candles_stored' as candles_stored
  FROM http((
    'POST',
    'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
    ARRAY[http_header('Content-Type', 'application/json'), 
          http_header('Authorization', 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
    'application/json',
    '{"timeframe": 60}'
  )::http_request);
  $$
);

-- Verify jobs were created
SELECT 
    jobid,
    jobname,
    schedule,
    active,
    created_at
FROM cron.job 
WHERE jobname LIKE 'fetch-candles-%'
ORDER BY jobname;

-- Show next scheduled run times
SELECT 
    jobname,
    schedule,
    active,
    CASE 
        WHEN schedule = '*/5 * * * *' THEN 'Every 5 minutes'
        WHEN schedule = '*/15 * * * *' THEN 'Every 15 minutes'
        WHEN schedule = '*/30 * * * *' THEN 'Every 30 minutes'
        WHEN schedule = '0 * * * *' THEN 'Every hour'
    END as frequency
FROM cron.job 
WHERE jobname LIKE 'fetch-candles-%'
ORDER BY jobname;
