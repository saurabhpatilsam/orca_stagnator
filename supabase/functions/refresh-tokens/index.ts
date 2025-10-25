import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { connect } from 'https://deno.land/x/redis@v0.31.0/mod.ts';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface TradovateTokens {
  access_token: string;
  md_access_token: string;
}

async function getTradovateTokenFromRedis(): Promise<string | null> {
  try {
    const redis = await connect({
      hostname: Deno.env.get('REDIS_HOST') || 'redismanager.redis.cache.windows.net',
      port: parseInt(Deno.env.get('REDIS_PORT') || '6380'),
      password: Deno.env.get('REDIS_PASSWORD'),
      tls: true,
    });

    const accounts = [
      'PAAPEX2666680000001',
      'APEX_266668',
      'PAAPEX2666680000003',
      'PAAPEX2666680000002',
      'PAAPEX2666680000004',
      'PAAPEX2666680000005',
    ];

    for (const account of accounts) {
      const token = await redis.get(`token:${account}`);
      if (token) {
        console.log(`✅ Found token for ${account}`);
        await redis.quit();
        return token;
      }
    }
    await redis.quit();
    return null;
  } catch (e) {
    console.error('❌ Redis error:', e);
    return null;
  }
}

async function renewTradovateTokens(tvToken: string): Promise<TradovateTokens | null> {
  try {
    const renewUrl = 'https://demo.tradovateapi.com/v1/auth/renewaccesstoken';

    const response = await fetch(renewUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${tvToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(`Token renewal failed: ${response.status}`);
    }

    const data = await response.json();

    if (!data.accessToken || !data.mdAccessToken) {
      throw new Error('Missing tokens in renewal response');
    }

    console.log('✅ Successfully renewed Tradovate tokens');

    return {
      access_token: data.accessToken,
      md_access_token: data.mdAccessToken,
    };
  } catch (e) {
    console.error('❌ Token renewal failed:', e);
    return null;
  }
}

async function storeRenewedTokenInRedis(accessToken: string): Promise<void> {
  try {
    const redis = await connect({
      hostname: Deno.env.get('REDIS_HOST') || 'redismanager.redis.cache.windows.net',
      port: parseInt(Deno.env.get('REDIS_PORT') || '6380'),
      password: Deno.env.get('REDIS_PASSWORD'),
      tls: true,
    });

    const accounts = [
      'PAAPEX2666680000001',
      'APEX_266668',
      'PAAPEX2666680000003',
      'PAAPEX2666680000002',
      'PAAPEX2666680000004',
      'PAAPEX2666680000005',
    ];

    const ttl = 3600; // 1 hour TTL to match token expiry
    let updateCount = 0;

    for (const account of accounts) {
      const key = `token:${account}`;
      await redis.setex(key, ttl, accessToken);
      updateCount++;
    }

    await redis.quit();
    console.log(`✅ Updated ${updateCount} tokens in Redis with ${ttl}s TTL`);
  } catch (e) {
    console.error('❌ Failed to store renewed token in Redis:', e);
    throw e;
  }
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🔄 Starting token refresh...');

    // Get current token from Redis
    const tvToken = await getTradovateTokenFromRedis();
    if (!tvToken) {
      throw new Error('No Tradovate token found in Redis');
    }

    // Renew tokens
    const tokens = await renewTradovateTokens(tvToken);
    if (!tokens) {
      throw new Error('Failed to renew Tradovate tokens');
    }

    // Store renewed token back to Redis
    await storeRenewedTokenInRedis(tokens.access_token);

    console.log('✅ Token refresh completed successfully');

    return new Response(
      JSON.stringify({
        success: true,
        message: 'Tokens refreshed successfully',
        tokens_updated: 6,
        ttl: 3600,
        timestamp: new Date().toISOString()
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );

  } catch (error) {
    console.error('❌ Error in refresh-tokens function:', error);
    
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
})
