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

// Tradovate API functions
async function getTradovateTokens(): Promise<TradovateTokens | null> {
  try {
    // Get stored tokens from Redis/Supabase
    const response = await fetch(`${Deno.env.get('REDIS_API_URL')}/get-tokens`, {
      headers: {
        'Authorization': `Bearer ${Deno.env.get('REDIS_API_KEY')}`
      }
    });
    
    if (!response.ok) {
      console.error('Failed to get tokens from Redis');
      return null;
    }
    
    const tokens = await response.json();
    return tokens;
  } catch (error) {
    console.error('Error getting tokens:', error);
    return null;
  }
}

async function discoverContract(accessToken: string, symbol: string): Promise<string | null> {
  try {
    const response = await fetch('https://md.tradovateapi.com/v1/contractMaturity/find', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: symbol })
    });
    
    if (!response.ok) {
      console.error('Failed to discover contract');
      return null;
    }
    
    const data = await response.json();
    return data.name || null;
  } catch (error) {
    console.error('Error discovering contract:', error);
    return null;
  }
}

async function fetchCandleData(
  mdToken: string, 
  symbol: string, 
  timeframe: number, 
  bars: number = 5
): Promise<CandleData[]> {
  try {
    // This is a simplified version - you'd need to implement WebSocket connection
    // For now, we'll use a REST API approach or mock data
    
    // Mock data for demonstration - replace with actual Tradovate WebSocket logic
    const mockCandles: CandleData[] = [];
    const now = new Date();
    
    for (let i = bars - 1; i >= 0; i--) {
      const candleTime = new Date(now.getTime() - (i * timeframe * 60 * 1000));
      const basePrice = 24950 + Math.random() * 100;
      
      mockCandles.push({
        datetime: candleTime.toISOString(),
        open: basePrice,
        high: basePrice + Math.random() * 20,
        low: basePrice - Math.random() * 20,
        close: basePrice + (Math.random() - 0.5) * 10,
        volume: Math.floor(Math.random() * 1000) + 100,
        up_volume: Math.floor(Math.random() * 500),
        down_volume: Math.floor(Math.random() * 500),
        up_ticks: Math.floor(Math.random() * 100),
        down_ticks: Math.floor(Math.random() * 100)
      });
    }
    
    return mockCandles;
  } catch (error) {
    console.error('Error fetching candle data:', error);
    return [];
  }
}

async function storeCandlesInSupabase(
  supabase: any,
  timeframe: number,
  candles: CandleData[],
  symbol: string
): Promise<{ success: number; errors: number }> {
  const functionMap: { [key: number]: string } = {
    1: 'insert_nq_candles_1min',
    5: 'insert_nq_candles_5min',
    10: 'insert_nq_candles_10min',
    15: 'insert_nq_candles_15min',
    30: 'insert_nq_candles_30min',
    60: 'insert_nq_candles_1hour'
  };
  
  const functionName = functionMap[timeframe];
  if (!functionName) {
    throw new Error(`Invalid timeframe: ${timeframe}`);
  }
  
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
    const { timeframe } = await req.json();
    
    if (!timeframe || ![1, 5, 10, 15, 30, 60].includes(timeframe)) {
      return new Response(
        JSON.stringify({ error: 'Invalid timeframe. Must be 1, 5, 10, 15, 30, or 60' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    console.log(`🚀 Fetching ${timeframe}-minute candles...`);

    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('supabase_service_key_orca') ?? ''
    );

    // Get Tradovate tokens
    const tokens = await getTradovateTokens();
    if (!tokens) {
      throw new Error('Failed to get Tradovate tokens');
    }

    // Discover current NQ contract
    const contractSymbol = await discoverContract(tokens.access_token, 'NQ');
    if (!contractSymbol) {
      throw new Error('Failed to discover NQ contract');
    }

    console.log(`📊 Using contract: ${contractSymbol}`);

    // Fetch candle data
    const candles = await fetchCandleData(
      tokens.md_access_token,
      contractSymbol,
      timeframe,
      5
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
      contractSymbol
    );

    console.log(`✅ Stored ${result.success}/${candles.length} candles`);

    return new Response(
      JSON.stringify({
        success: true,
        timeframe,
        symbol: contractSymbol,
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
