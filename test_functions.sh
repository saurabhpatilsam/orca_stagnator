#!/bin/bash
# Test Supabase Edge Functions

set -e

echo "🧪 Testing Supabase Edge Functions"
echo "=================================="

# Get project URL
if [ -f ".supabase/config.toml" ]; then
    PROJECT_REF=$(cat .supabase/config.toml | grep project_id | cut -d'"' -f2)
    SUPABASE_URL="https://${PROJECT_REF}.supabase.co"
else
    echo "❌ Not linked to Supabase project"
    exit 1
fi

echo "🌐 Project URL: $SUPABASE_URL"
echo ""

# Test scheduler function
echo "⏰ Testing scheduler function..."
echo "curl -X POST ${SUPABASE_URL}/functions/v1/scheduler"
echo ""

SCHEDULER_RESULT=$(supabase functions invoke scheduler --method POST --body '{}' 2>/dev/null || echo "Error calling scheduler")
echo "📊 Scheduler Result:"
echo "$SCHEDULER_RESULT" | jq . 2>/dev/null || echo "$SCHEDULER_RESULT"
echo ""

# Test fetch-historical-candles function
echo "📊 Testing fetch-historical-candles function..."
echo "curl -X POST ${SUPABASE_URL}/functions/v1/fetch-historical-candles -d '{\"timeframe\": 30, \"days_back\": 2}'"
echo ""

HISTORICAL_RESULT=$(supabase functions invoke fetch-historical-candles --method POST --body '{"timeframe": 30, "days_back": 2}' 2>/dev/null || echo "Error calling fetch-historical-candles")
echo "📊 Historical Result:"
echo "$HISTORICAL_RESULT" | jq . 2>/dev/null || echo "$HISTORICAL_RESULT"
echo ""

# Test fetch-candles function for each timeframe
for TIMEFRAME in 5 15 30 60; do
    echo "📈 Testing fetch-candles for ${TIMEFRAME}-minute timeframe..."
    echo "curl -X POST ${SUPABASE_URL}/functions/v1/fetch-candles -d '{\"timeframe\": ${TIMEFRAME}}'"
    echo ""
    
    FETCH_RESULT=$(supabase functions invoke fetch-candles --method POST --body "{\"timeframe\": ${TIMEFRAME}}" 2>/dev/null || echo "Error calling fetch-candles")
    echo "📊 Fetch Result (${TIMEFRAME}min):"
    echo "$FETCH_RESULT" | jq . 2>/dev/null || echo "$FETCH_RESULT"
    echo ""
done

# Check database for recent data
echo "🔍 Checking database for recent candle data..."
echo "SELECT 'fetch_log' as table_name, timeframe, last_fetch FROM public.candle_fetch_log ORDER BY timeframe;" | supabase db psql

echo ""
echo "SELECT '5min' as timeframe, COUNT(*) as count, MAX(candle_time) as latest FROM orca.nq_candles_5min 
UNION ALL SELECT '15min', COUNT(*), MAX(candle_time) FROM orca.nq_candles_15min
UNION ALL SELECT '30min', COUNT(*), MAX(candle_time) FROM orca.nq_candles_30min  
UNION ALL SELECT '1hour', COUNT(*), MAX(candle_time) FROM orca.nq_candles_1hour;" | supabase db psql

echo ""
echo "✅ Testing complete!"
echo ""
echo "💡 To monitor functions in real-time:"
echo "   supabase functions logs scheduler --follow"
echo "   supabase functions logs fetch-candles --follow"
echo "   supabase functions logs fetch-historical-candles --follow"
