import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface CandleData {
  datetime: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  up_volume?: number;
  down_volume?: number;
  up_ticks?: number;
  down_ticks?: number;
}

interface TradovateTokens {
  access_token: string;
  md_access_token: string;
}

// Import Redis connection
import { connect } from 'https://deno.land/x/redis@v0.31.0/mod.ts';

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

    const ttl = 3600; // 1 hour TTL to match token_generator_and_redis_manager.py
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
    // Don't throw - token renewal succeeded, Redis update is supplementary
  }
}

async function discoverContract(accessToken: string, symbolPrefix: string): Promise<string | null> {
  try {
    const url = `https://demo.tradovateapi.com/v1/contract/suggest?t=${symbolPrefix}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.error('Failed to discover contract');
      return null;
    }
    
    const contracts = await response.json();
    if (contracts && contracts.length > 0) {
      const contract = contracts[0];
      console.log(`✅ Using contract: ${contract.name}`);
      return contract.name;
    }
    return null;
  } catch (error) {
    console.error('Error discovering contract:', error);
    return null;
  }
}

function wsMsg(op: string, id: number, body: string, query = ''): string {
  return `${op}\n${id}\n${query}\n${body}`;
}

function parseSockJs(message: string): any | null {
  try {
    if (message === 'h') {
      return { type: 'heartbeat' };
    } else if (message === 'o') {
      return { type: 'open' };
    } else if (message === 'c') {
      return { type: 'close' };
    } else if (message.startsWith('a[')) {
      const jsonStr = message.slice(2, -1);
      return JSON.parse(jsonStr);
    }
    return null;
  } catch (e) {
    console.error('❌ SockJs parse error:', e);
    return null;
  }
}

function getLatestClosedCandleTime(timeframeMinutes: number): Date {
  const now = new Date();
  const currentMinutes = now.getUTCMinutes();
  const currentHours = now.getUTCHours();

  const totalMinutesFromMidnight = (currentHours * 60) + currentMinutes;
  const candlesSinceMidnight = Math.floor(totalMinutesFromMidnight / timeframeMinutes);
  const latestClosedCandleMinutes = candlesSinceMidnight * timeframeMinutes;

  const latestClosedCandle = new Date(now);
  latestClosedCandle.setUTCHours(Math.floor(latestClosedCandleMinutes / 60));
  latestClosedCandle.setUTCMinutes(latestClosedCandleMinutes % 60);
  latestClosedCandle.setUTCSeconds(0);
  latestClosedCandle.setUTCMilliseconds(0);

  return latestClosedCandle;
}

async function fetchRealtimeCandles(
  mdAccessToken: string,
  symbol: string,
  timeframe: number,
  numberOfBars: number = 10
): Promise<CandleData[]> {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket('wss://md-demo.tradovateapi.com/v1/websocket');
    const candles: CandleData[] = [];
    let authorized = false;
    let requestId = 1;
    let dataReceived = false;
    let heartbeatInterval: any;

    const latestClosedCandle = getLatestClosedCandleTime(timeframe);
    console.log(`📅 Current time: ${new Date().toISOString()}`);
    console.log(`📋 Latest closed ${timeframe}min candle: ${latestClosedCandle.toISOString()}`);
    console.log(`📊 Will request ${numberOfBars} candles`);

    const timer = setTimeout(() => {
      console.log('⏰ WebSocket timeout');
      try { ws.close(); } catch {}
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      reject(new Error('WebSocket timeout'));
    }, 30000);

    ws.onopen = () => {
      console.log('🔌 WebSocket connected');

      heartbeatInterval = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          try {
            ws.send('[]');
          } catch (e) {
            console.error('❌ Heartbeat failed:', e);
          }
        }
      }, 2400);

      const authMsg = wsMsg('authorize', requestId, mdAccessToken);
      console.log('🔐 Sending authorization...');
      ws.send(authMsg);
      requestId += 1;
    };

    ws.onmessage = (ev) => {
      const message = String(ev.data);
      const parsed = parseSockJs(message);

      if (!parsed) return;

      if (parsed.type === 'heartbeat') {
        try {
          ws.send('[]');
        } catch (e) {
          console.error('❌ Failed to respond to heartbeat:', e);
        }
        return;
      }

      if (parsed.type === 'open' || parsed.type === 'close') {
        return;
      }

      if (parsed.s === 200 && !authorized) {
        authorized = true;
        console.log('✅ WebSocket AUTHORIZED');

        const chartRequest = {
          symbol,
          chartDescription: {
            underlyingType: 'MinuteBar',
            elementSize: timeframe,
            elementSizeUnit: 'UnderlyingUnits',
            withHistogram: false,
          },
          timeRange: {
            closestTimestamp: latestClosedCandle.toISOString().replace('.000Z', 'Z'),
            asMuchAsElements: numberOfBars + 1,
          },
        };

        const chartMsg = wsMsg('md/getChart', requestId, JSON.stringify(chartRequest));
        console.log(`📊 Requesting ${numberOfBars} candles of ${timeframe}min data...`);
        ws.send(chartMsg);
        return;
      }

      if (parsed.e === 'chart') {
        console.log('📈 Chart event received');
        dataReceived = true;

        const chartData = parsed.d || {};
        for (const chart of (chartData.charts || [])) {
          if (chart.eoh) {
            console.log('🏁 End of historical data');
            candles.sort((a, b) => new Date(a.datetime).getTime() - new Date(b.datetime).getTime());
            console.log(`✅ Final result: ${candles.length} candles`);
            clearTimeout(timer);
            if (heartbeatInterval) clearInterval(heartbeatInterval);
            try { ws.close(); } catch {}
            resolve(candles);
            return;
          }

          const bars = chart.bars || [];
          if (bars.length > 0) {
            console.log(`📊 Received ${bars.length} candle bars`);

            for (let i = 0; i < bars.length - 1; i++) {
              const bar = bars[i];
              if (bar.timestamp) {
                candles.push({
                  datetime: new Date(bar.timestamp).toISOString(),
                  open: Number(bar.open || 0),
                  high: Number(bar.high || 0),
                  low: Number(bar.low || 0),
                  close: Number(bar.close || 0),
                  volume: Number(bar.upVolume || 0) + Number(bar.downVolume || 0),
                  up_volume: Number(bar.upVolume || 0),
                  down_volume: Number(bar.downVolume || 0),
                  up_ticks: Number(bar.upTicks || 0),
                  down_ticks: Number(bar.downTicks || 0),
                });
              }
            }
            console.log(`✅ Processed ${candles.length} candles so far`);
          }
        }
      }

      if (parsed.e === 'shutdown') {
        const reasonCode = parsed.d?.reasonCode || 'Unknown';
        console.log(`🛑 Server shutdown: ${reasonCode}`);
        clearTimeout(timer);
        if (heartbeatInterval) clearInterval(heartbeatInterval);
        reject(new Error(`Server shutdown: ${reasonCode}`));
      }
    };

    ws.onerror = (e) => {
      console.log('❌ WebSocket error:', e);
      clearTimeout(timer);
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      reject(new Error('WebSocket connection error'));
    };

    ws.onclose = (event) => {
      console.log(`🔌 WebSocket closed: ${event.code}`);
      clearTimeout(timer);
      if (heartbeatInterval) clearInterval(heartbeatInterval);
      if (!dataReceived) {
        reject(new Error('WebSocket closed without data'));
      }
    };
  });
}

async function storeCandlesInSupabase(
  supabase: any,
  timeframe: number,
  candles: CandleData[],
  symbol: string
): Promise<{ success: number; errors: number }> {
  // Map symbol to table prefix
  const getTablePrefix = (sym: string): string => {
    const upper = sym.toUpperCase();
    if (upper.includes('MNQ')) return 'mnq';
    if (upper.includes('NQ')) return 'nq';
    if (upper.includes('MES')) return 'mes';
    if (upper.includes('ES')) return 'es';
    // Default to nq for backward compatibility
    return 'nq';
  };
  
  const tablePrefix = getTablePrefix(symbol);
  
  const functionMap: { [key: string]: string } = {
    '1': `insert_${tablePrefix}_candles_1min`,
    '5': `insert_${tablePrefix}_candles_5min`,
    '10': `insert_${tablePrefix}_candles_10min`,
    '15': `insert_${tablePrefix}_candles_15min`,
    '30': `insert_${tablePrefix}_candles_30min`,
    '60': `insert_${tablePrefix}_candles_1hour`
  };
  
  const functionName = functionMap[timeframe.toString()];
  if (!functionName) {
    throw new Error(`Invalid timeframe: ${timeframe}`);
  }
  
  console.log(`📊 Using insert function: ${functionName} for symbol: ${symbol}`);

  
  let success = 0;
  let errors = 0;
  
  for (const candle of candles) {
    try {
      const { error } = await supabase.rpc(functionName, {
        p_symbol: symbol,
        p_candle_time: candle.datetime,
        p_open: candle.open,
        p_high: candle.high,
        p_low: candle.low,
        p_close: candle.close,
        p_volume: candle.volume,
        p_up_volume: candle.up_volume || 0,
        p_down_volume: candle.down_volume || 0,
        p_up_ticks: candle.up_ticks || 0,
        p_down_ticks: candle.down_ticks || 0
      });
      
      if (error) {
        console.error('Error storing candle:', error);
        errors++;
      } else {
        success++;
      }
    } catch (err) {
      console.error('Exception storing candle:', err);
      errors++;
    }
  }
  
  return { success, errors };
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { timeframe, symbol } = await req.json();
    
    if (!timeframe || ![1, 5, 10, 15, 30, 60].includes(timeframe)) {
      return new Response(
        JSON.stringify({ error: 'Invalid timeframe. Must be 1, 5, 10, 15, 30, or 60' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }
    
    // Default to MNQZ5 if no symbol provided (backward compatibility)
    const targetSymbol = symbol || 'MNQZ5';

    console.log(`🚀 Fetching ${timeframe}-minute candles using WebSocket...`);

    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    // Get Tradovate token from Redis
    const tvToken = await getTradovateTokenFromRedis();
    if (!tvToken) {
      throw new Error('No Tradovate TV token found in Redis');
    }

    // Renew tokens to get MD token
    const tokens = await renewTradovateTokens(tvToken);
    if (!tokens) {
      throw new Error('Failed to renew Tradovate tokens');
    }

    // Store renewed token back to Redis to prevent expiration
    await storeRenewedTokenInRedis(tokens.access_token);

    console.log(`📋 Using symbol: ${targetSymbol}`);

    // Fetch candle data using WebSocket
    const candles = await fetchRealtimeCandles(
      tokens.md_access_token,
      targetSymbol,
      timeframe,
      10  // Get last 10 candles
    );

    if (candles.length === 0) {
      throw new Error('No candle data received');
    }

    console.log(`📥 Fetched ${candles.length} candles`);

    // Store in Supabase
    const result = await storeCandlesInSupabase(
      supabase,
      timeframe,
      candles,
      targetSymbol
    );

    console.log(`💾 Stored ${result.success} candles successfully`);

    return new Response(
      JSON.stringify({
        success: true,
        timeframe,
        symbol: targetSymbol,
        candles_fetched: candles.length,
        candles_stored: result.success,
        errors: result.errors,
        timestamp: new Date().toISOString()
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );

  } catch (error) {
    console.error('Error in fetch-candles function:', error);
    
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
