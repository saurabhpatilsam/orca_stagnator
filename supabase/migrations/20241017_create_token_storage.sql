-- Create token storage table for Tradovate tokens
CREATE TABLE IF NOT EXISTS public.tradovate_tokens (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    account_name TEXT NOT NULL UNIQUE,
    main_account TEXT NOT NULL, -- APEX_272045, etc.
    token_type TEXT NOT NULL DEFAULT 'bearer', -- bearer, auth, etc.
    access_token TEXT NOT NULL,
    token_length INTEGER,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_tradovate_tokens_account_name ON public.tradovate_tokens(account_name);
CREATE INDEX IF NOT EXISTS idx_tradovate_tokens_main_account ON public.tradovate_tokens(main_account);
CREATE INDEX IF NOT EXISTS idx_tradovate_tokens_active ON public.tradovate_tokens(is_active);
CREATE INDEX IF NOT EXISTS idx_tradovate_tokens_expires_at ON public.tradovate_tokens(expires_at);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tradovate_tokens_updated_at 
    BEFORE UPDATE ON public.tradovate_tokens 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create token key mapping table for Redis key structure
CREATE TABLE IF NOT EXISTS public.token_key_mappings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    main_account TEXT NOT NULL, -- APEX_272045
    redis_key TEXT NOT NULL, -- token:APEX_272045, token:PAAPEX2720450000001, etc.
    key_type TEXT NOT NULL, -- main, sub_account, auth
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for key mappings
CREATE INDEX IF NOT EXISTS idx_token_key_mappings_main_account ON public.token_key_mappings(main_account);
CREATE INDEX IF NOT EXISTS idx_token_key_mappings_redis_key ON public.token_key_mappings(redis_key);

-- Insert sample data structure (this will be populated by the Edge Function)
COMMENT ON TABLE public.tradovate_tokens IS 'Stores Tradovate API tokens with metadata and expiration tracking';
COMMENT ON TABLE public.token_key_mappings IS 'Maps Redis key structure to main accounts for token management';

-- Enable RLS (Row Level Security) if needed
-- ALTER TABLE public.tradovate_tokens ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.token_key_mappings ENABLE ROW LEVEL SECURITY;
