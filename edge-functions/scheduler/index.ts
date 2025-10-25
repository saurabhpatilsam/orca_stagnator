import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ScheduleConfig {
  timeframe: number;
  interval_minutes: number;
  name: string;
}

const SCHEDULES: ScheduleConfig[] = [
  { timeframe: 5, interval_minutes: 5, name: '5min' },
  { timeframe: 15, interval_minutes: 15, name: '15min' },
  { timeframe: 30, interval_minutes: 30, name: '30min' },
  { timeframe: 60, interval_minutes: 60, name: '1hour' }
];

async function getLastFetchTime(supabase: any, timeframe: number): Promise<Date | null> {
  try {
    const { data, error } = await supabase
      .from('candle_fetch_log')
      .select('last_fetch')
      .eq('timeframe', timeframe)
      .single();
    
    if (error || !data) {
      return null;
    }
    
    return new Date(data.last_fetch);
  } catch {
    return null;
  }
}

async function updateLastFetchTime(supabase: any, timeframe: number): Promise<void> {
  const now = new Date().toISOString();
  
  const { error } = await supabase
    .from('candle_fetch_log')
    .upsert({
      timeframe,
      last_fetch: now,
      updated_at: now
    }, {
      onConflict: 'timeframe'
    });
    
  if (error) {
    console.error('Error updating last fetch time:', error);
  }
}

async function callFetchCandlesFunction(timeframe: number): Promise<any> {
  try {
    const response = await fetch(`${Deno.env.get('SUPABASE_URL')}/functions/v1/fetch-candles`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('SUPABASE_ANON_KEY')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ timeframe })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error calling fetch-candles for ${timeframe}min:`, error);
    throw error;
  }
}

serve(async (req) => {
  // Handle CORS
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🔄 Scheduler running...');
    
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const results = [];
    const now = new Date();

    // Check each timeframe
    for (const schedule of SCHEDULES) {
      try {
        console.log(`⏰ Checking ${schedule.name} schedule...`);
        
        const lastFetch = await getLastFetchTime(supabase, schedule.timeframe);
        let shouldFetch = false;
        
        if (!lastFetch) {
          console.log(`📅 No previous fetch for ${schedule.name}, fetching now`);
          shouldFetch = true;
        } else {
          const timeSinceLastFetch = (now.getTime() - lastFetch.getTime()) / (1000 * 60); // minutes
          shouldFetch = timeSinceLastFetch >= schedule.interval_minutes;
          
          console.log(`📊 ${schedule.name}: ${timeSinceLastFetch.toFixed(1)} min since last fetch (need ${schedule.interval_minutes})`);
        }
        
        if (shouldFetch) {
          console.log(`🚀 Fetching ${schedule.name} candles...`);
          
          const fetchResult = await callFetchCandlesFunction(schedule.timeframe);
          await updateLastFetchTime(supabase, schedule.timeframe);
          
          results.push({
            timeframe: schedule.timeframe,
            name: schedule.name,
            status: 'success',
            result: fetchResult
          });
          
          console.log(`✅ ${schedule.name}: ${fetchResult.candles_stored} candles stored`);
        } else {
          const nextFetchIn = schedule.interval_minutes - ((now.getTime() - lastFetch!.getTime()) / (1000 * 60));
          
          results.push({
            timeframe: schedule.timeframe,
            name: schedule.name,
            status: 'skipped',
            next_fetch_in_minutes: Math.round(nextFetchIn)
          });
          
          console.log(`⏳ ${schedule.name}: Next fetch in ${nextFetchIn.toFixed(1)} minutes`);
        }
        
      } catch (error) {
        console.error(`❌ Error processing ${schedule.name}:`, error);
        
        results.push({
          timeframe: schedule.timeframe,
          name: schedule.name,
          status: 'error',
          error: error.message
        });
      }
    }

    const summary = {
      timestamp: now.toISOString(),
      total_schedules: SCHEDULES.length,
      fetched: results.filter(r => r.status === 'success').length,
      skipped: results.filter(r => r.status === 'skipped').length,
      errors: results.filter(r => r.status === 'error').length,
      results
    };

    console.log(`📊 Scheduler complete: ${summary.fetched} fetched, ${summary.skipped} skipped, ${summary.errors} errors`);

    return new Response(
      JSON.stringify(summary),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );

  } catch (error) {
    console.error('Error in scheduler function:', error);
    
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
