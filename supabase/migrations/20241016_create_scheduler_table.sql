-- Create table to track candle fetch schedules
CREATE TABLE IF NOT EXISTS public.candle_fetch_log (
    id BIGSERIAL PRIMARY KEY,
    timeframe INTEGER NOT NULL UNIQUE,
    last_fetch TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_candle_fetch_log_timeframe ON public.candle_fetch_log(timeframe);

-- Insert initial records for each timeframe
INSERT INTO public.candle_fetch_log (timeframe, last_fetch) VALUES
    (5, NOW() - INTERVAL '10 minutes'),
    (15, NOW() - INTERVAL '20 minutes'),
    (30, NOW() - INTERVAL '35 minutes'),
    (60, NOW() - INTERVAL '65 minutes')
ON CONFLICT (timeframe) DO NOTHING;

-- Grant permissions
GRANT ALL ON public.candle_fetch_log TO authenticated, anon, service_role;
GRANT ALL ON SEQUENCE candle_fetch_log_id_seq TO authenticated, anon, service_role;

-- Create function to setup cron job (pg_cron extension)
CREATE OR REPLACE FUNCTION setup_candle_scheduler()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Schedule the scheduler function to run every minute
    -- This requires pg_cron extension to be enabled
    PERFORM cron.schedule(
        'candle-scheduler',
        '* * * * *', -- Every minute
        $$
        SELECT net.http_post(
            url := current_setting('app.supabase_url') || '/functions/v1/scheduler',
            headers := jsonb_build_object(
                'Authorization', 'Bearer ' || current_setting('app.service_role_key'),
                'Content-Type', 'application/json'
            ),
            body := '{}'::jsonb
        );
        $$
    );
    
    RAISE NOTICE 'Candle scheduler cron job created successfully';
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION setup_candle_scheduler() TO service_role;

COMMENT ON TABLE public.candle_fetch_log IS 'Tracks the last fetch time for each candle timeframe to manage scheduling';
COMMENT ON FUNCTION setup_candle_scheduler() IS 'Sets up a cron job to call the scheduler edge function every minute';
