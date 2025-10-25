-- 16 Cron Jobs for All Instruments
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS http;

-- Remove old jobs
DO $$ DECLARE r RECORD; BEGIN
  FOR r IN SELECT jobid FROM cron.job WHERE jobname LIKE 'fetch-%' LOOP
    PERFORM cron.unschedule(r.jobid);
  END LOOP;
END $$;


-- NQ (NQZ5)
SELECT cron.schedule('fetch-nq-5min', '*/5 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":5,"symbol":"NQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-nq-15min', '*/15 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":15,"symbol":"NQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-nq-30min', '*/30 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":30,"symbol":"NQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-nq-60min', '0 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":60,"symbol":"NQZ5"}')::http_request);
$$);

-- MNQ (MNQZ5)
SELECT cron.schedule('fetch-mnq-5min', '*/5 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":5,"symbol":"MNQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mnq-15min', '*/15 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":15,"symbol":"MNQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mnq-30min', '*/30 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":30,"symbol":"MNQZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mnq-60min', '0 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":60,"symbol":"MNQZ5"}')::http_request);
$$);

-- ES (ESZ5)
SELECT cron.schedule('fetch-es-5min', '*/5 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":5,"symbol":"ESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-es-15min', '*/15 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":15,"symbol":"ESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-es-30min', '*/30 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":30,"symbol":"ESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-es-60min', '0 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":60,"symbol":"ESZ5"}')::http_request);
$$);

-- MES (MESZ5)
SELECT cron.schedule('fetch-mes-5min', '*/5 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":5,"symbol":"MESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mes-15min', '*/15 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":15,"symbol":"MESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mes-30min', '*/30 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":30,"symbol":"MESZ5"}')::http_request);
$$);
SELECT cron.schedule('fetch-mes-60min', '0 * * * *', $$
SELECT status FROM http(('POST', 'https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles',
ARRAY[http_header('Content-Type','application/json'), http_header('Authorization','Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w')],
'application/json', '{"timeframe":60,"symbol":"MESZ5"}')::http_request);
$$);