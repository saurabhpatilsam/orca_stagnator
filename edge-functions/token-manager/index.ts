import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import { Redis } from "https://deno.land/x/redis@v0.29.0/mod.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface TokenData {
  account_name: string;
  main_account: string;
  access_token: string;
  token_length: number;
  expires_at: string;
  metadata?: any;
}

interface RedisConfig {
  hostname: string;
  port: number;
  password: string;
  tls: boolean;
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    )

    // Redis configuration
    const redisConfig: RedisConfig = {
      hostname: "redismanager.redis.cache.windows.net",
      port: 6380,
      password: Deno.env.get('REDIS_PASSWORD') || '',
      tls: true
    };

    const { method, url } = req;
    const urlObj = new URL(url);
    const action = urlObj.searchParams.get('action') || 'sync';

    console.log(`🔐 Token Manager - Action: ${action}, Method: ${method}`);

    switch (action) {
      case 'sync':
        return await syncTokensFromRedis(supabaseClient, redisConfig);
      
      case 'get':
        const account = urlObj.searchParams.get('account');
        return await getTokenFromSupabase(supabaseClient, account);
      
      case 'store':
        if (method === 'POST') {
          const body = await req.json();
          return await storeTokensInSupabase(supabaseClient, body.tokens);
        }
        break;
      
      case 'cleanup':
        return await cleanupExpiredTokens(supabaseClient);
      
      case 'status':
        return await getTokenStatus(supabaseClient, redisConfig);
      
      default:
        return new Response(
          JSON.stringify({ error: 'Invalid action. Use: sync, get, store, cleanup, status' }),
          { 
            status: 400, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        );
    }

  } catch (error) {
    console.error('❌ Token Manager Error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Internal server error', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
})

async function syncTokensFromRedis(supabaseClient: any, redisConfig: RedisConfig) {
  console.log('🔄 Starting Redis to Supabase sync...');
  
  try {
    // Connect to Redis
    const redis = new Redis(redisConfig);
    
    // Get all token keys from Redis
    const tokenKeys = await redis.keys("token:*");
    console.log(`📊 Found ${tokenKeys.length} token keys in Redis`);
    
    const tokens: TokenData[] = [];
    const keyMappings: any[] = [];
    
    for (const key of tokenKeys) {
      const token = await redis.get(key);
      const ttl = await redis.ttl(key);
      
      if (token) {
        const accountName = key.replace('token:', '');
        const mainAccount = getMainAccount(accountName);
        
        const tokenData: TokenData = {
          account_name: accountName,
          main_account: mainAccount,
          access_token: token,
          token_length: token.length,
          expires_at: new Date(Date.now() + (ttl * 1000)).toISOString(),
          metadata: {
            redis_key: key,
            ttl_seconds: ttl,
            synced_at: new Date().toISOString(),
            token_preview: token.substring(0, 50) + '...'
          }
        };
        
        tokens.push(tokenData);
        
        // Create key mapping
        keyMappings.push({
          main_account: mainAccount,
          redis_key: key,
          key_type: accountName.startsWith('APEX_') ? 'main' : 'sub_account'
        });
      }
    }
    
    await redis.quit();
    
    // Store tokens in Supabase
    const { data: tokenResult, error: tokenError } = await supabaseClient
      .from('tradovate_tokens')
      .upsert(tokens, { 
        onConflict: 'account_name',
        ignoreDuplicates: false 
      });
    
    if (tokenError) {
      console.error('❌ Error storing tokens:', tokenError);
      throw tokenError;
    }
    
    // Store key mappings
    const { data: mappingResult, error: mappingError } = await supabaseClient
      .from('token_key_mappings')
      .upsert(keyMappings, { 
        onConflict: 'redis_key',
        ignoreDuplicates: false 
      });
    
    if (mappingError) {
      console.error('❌ Error storing key mappings:', mappingError);
      throw mappingError;
    }
    
    console.log(`✅ Successfully synced ${tokens.length} tokens to Supabase`);
    
    return new Response(
      JSON.stringify({
        success: true,
        message: `Synced ${tokens.length} tokens from Redis to Supabase`,
        tokens_synced: tokens.length,
        key_mappings_created: keyMappings.length,
        accounts: tokens.map(t => t.account_name)
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
    
  } catch (error) {
    console.error('❌ Sync error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to sync tokens from Redis', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
}

async function getTokenFromSupabase(supabaseClient: any, account: string | null) {
  if (!account) {
    return new Response(
      JSON.stringify({ error: 'Account parameter is required' }),
      { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
  
  try {
    const { data, error } = await supabaseClient
      .from('tradovate_tokens')
      .select('*')
      .eq('account_name', account)
      .eq('is_active', true)
      .single();
    
    if (error) {
      console.error('❌ Error fetching token:', error);
      return new Response(
        JSON.stringify({ error: 'Token not found', details: error.message }),
        { 
          status: 404, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }
    
    // Check if token is expired
    const now = new Date();
    const expiresAt = new Date(data.expires_at);
    
    if (expiresAt <= now) {
      return new Response(
        JSON.stringify({ 
          error: 'Token expired', 
          expires_at: data.expires_at,
          account_name: data.account_name 
        }),
        { 
          status: 410, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        token: data.access_token,
        account_name: data.account_name,
        expires_at: data.expires_at,
        token_length: data.token_length,
        metadata: data.metadata
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
    
  } catch (error) {
    console.error('❌ Get token error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to retrieve token', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
}

async function storeTokensInSupabase(supabaseClient: any, tokens: TokenData[]) {
  try {
    const { data, error } = await supabaseClient
      .from('tradovate_tokens')
      .upsert(tokens, { 
        onConflict: 'account_name',
        ignoreDuplicates: false 
      });
    
    if (error) {
      console.error('❌ Error storing tokens:', error);
      throw error;
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        message: `Stored ${tokens.length} tokens in Supabase`,
        tokens_stored: tokens.length
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
    
  } catch (error) {
    console.error('❌ Store tokens error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to store tokens', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
}

async function cleanupExpiredTokens(supabaseClient: any) {
  try {
    const { data, error } = await supabaseClient
      .from('tradovate_tokens')
      .update({ is_active: false })
      .lt('expires_at', new Date().toISOString())
      .eq('is_active', true);
    
    if (error) {
      console.error('❌ Error cleaning up tokens:', error);
      throw error;
    }
    
    return new Response(
      JSON.stringify({
        success: true,
        message: 'Expired tokens marked as inactive',
        cleaned_up: data?.length || 0
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
    
  } catch (error) {
    console.error('❌ Cleanup error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to cleanup expired tokens', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
}

async function getTokenStatus(supabaseClient: any, redisConfig: RedisConfig) {
  try {
    // Get Supabase token count
    const { count: supabaseCount, error: supabaseError } = await supabaseClient
      .from('tradovate_tokens')
      .select('*', { count: 'exact', head: true })
      .eq('is_active', true);
    
    if (supabaseError) {
      console.error('❌ Error getting Supabase count:', supabaseError);
    }
    
    // Get Redis token count
    let redisCount = 0;
    try {
      const redis = new Redis(redisConfig);
      const tokenKeys = await redis.keys("token:*");
      redisCount = tokenKeys.length;
      await redis.quit();
    } catch (redisError) {
      console.error('❌ Error getting Redis count:', redisError);
    }
    
    // Get recent tokens
    const { data: recentTokens, error: recentError } = await supabaseClient
      .from('tradovate_tokens')
      .select('account_name, main_account, expires_at, created_at, updated_at')
      .eq('is_active', true)
      .order('updated_at', { ascending: false })
      .limit(10);
    
    return new Response(
      JSON.stringify({
        success: true,
        status: {
          supabase_tokens: supabaseCount || 0,
          redis_tokens: redisCount,
          sync_needed: (supabaseCount || 0) !== redisCount,
          last_updated: new Date().toISOString()
        },
        recent_tokens: recentTokens || []
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
    
  } catch (error) {
    console.error('❌ Status error:', error);
    return new Response(
      JSON.stringify({ 
        error: 'Failed to get token status', 
        details: error.message 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
}

function getMainAccount(accountName: string): string {
  // Extract main account from sub-account names
  // PAAPEX2720450000001 -> APEX_272045
  if (accountName.startsWith('PAAPEX')) {
    const numberPart = accountName.substring(6, 12); // Extract 272045 from PAAPEX272045...
    return `APEX_${numberPart}`;
  }
  
  // Already a main account
  if (accountName.startsWith('APEX_')) {
    return accountName;
  }
  
  // Fallback
  return accountName;
}

/* Deno.serve(serve) */
