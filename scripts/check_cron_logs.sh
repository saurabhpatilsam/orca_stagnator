#!/bin/bash
# Check Cron Job Execution Logs and Failures

set -euo pipefail

PROJECT_ID="dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

echo "=================================================="
echo "🔍 CHECKING CRON JOB LOGS"
echo "=================================================="
echo ""

# Check if we can access Supabase logs API
echo "📊 Attempting to fetch edge function logs..."
echo ""

# Test fetch-candles function directly to see if it's working
echo "🧪 Testing fetch-candles edge function..."
response=$(curl -s -X POST \
  "https://${PROJECT_ID}.supabase.co/functions/v1/fetch-candles" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5, "symbol": "NQZ5"}')

success=$(echo "$response" | jq -r '.success // false')
error=$(echo "$response" | jq -r '.error // ""')

if [ "$success" = "true" ]; then
  echo "✅ Edge function is working!"
  echo "$response" | jq '.'
else
  echo "❌ Edge function FAILED!"
  echo "Error: $error"
  echo "Full response:"
  echo "$response" | jq '.'
fi

echo ""
echo "=================================================="
echo "🔍 TESTING ALL INSTRUMENTS"
echo "=================================================="
echo ""

# Test each instrument to see which ones fail
instruments=(
  "5:NQZ5:NQ 5min"
  "15:NQZ5:NQ 15min"
  "5:MNQZ5:MNQ 5min"
  "15:MNQZ5:MNQ 15min"
  "5:ESZ5:ES 5min"
  "15:ESZ5:ES 15min"
  "5:MESZ5:MES 5min"
  "15:MESZ5:MES 15min"
)

success_count=0
fail_count=0

for inst in "${instruments[@]}"; do
  IFS=':' read -r timeframe symbol name <<< "$inst"
  
  echo -n "Testing $name... "
  
  response=$(curl -s -X POST \
    "https://${PROJECT_ID}.supabase.co/functions/v1/fetch-candles" \
    -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d "{\"timeframe\": ${timeframe}, \"symbol\": \"${symbol}\"}" \
    -w "\n%{http_code}")
  
  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | head -n-1)
  
  success=$(echo "$body" | jq -r '.success // false' 2>/dev/null || echo "false")
  error=$(echo "$body" | jq -r '.error // ""' 2>/dev/null || echo "")
  
  if [ "$success" = "true" ]; then
    echo "✅ OK"
    ((success_count++))
  else
    echo "❌ FAILED (HTTP $http_code)"
    ((fail_count++))
    if [ -n "$error" ]; then
      echo "   Error: $error"
    fi
    echo "   Response: $(echo "$body" | head -c 200)"
  fi
done

echo ""
echo "=================================================="
echo "📈 SUMMARY"
echo "=================================================="
echo "✅ Success: $success_count"
echo "❌ Failed: $fail_count"
echo ""

# Check token status in Redis
echo "🔑 Checking token status..."
echo ""

# Test token refresh
echo "Testing token refresh function..."
refresh_response=$(curl -s -X POST \
  "https://${PROJECT_ID}.supabase.co/functions/v1/refresh-tokens" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json")

refresh_success=$(echo "$refresh_response" | jq -r '.success // false')

if [ "$refresh_success" = "true" ]; then
  echo "✅ Token refresh working"
  echo "$refresh_response" | jq '.'
else
  echo "❌ Token refresh FAILED"
  echo "$refresh_response" | jq '.'
fi

echo ""
echo "=================================================="
echo "💡 RECOMMENDATIONS"
echo "=================================================="

if [ $fail_count -gt 0 ]; then
  echo "⚠️  FAILURES DETECTED!"
  echo ""
  echo "Possible causes:"
  echo "1. Expired tokens - Run: cd data-collection/token-management && python3 token_generator_and_redis_manager.py"
  echo "2. Redis connection issue - Check REDIS_HOST, REDIS_PORT, REDIS_PASSWORD in Supabase secrets"
  echo "3. Tradovate API issue - Check if demo.tradovateapi.com is accessible"
  echo "4. Symbol issue - Verify NQZ5, MNQZ5, ESZ5, MESZ5 are valid contracts"
  echo ""
  echo "Next steps:"
  echo "1. Refresh tokens manually"
  echo "2. Check Supabase Edge Function logs at: https://supabase.com/dashboard/project/${PROJECT_ID}/logs/edge-functions"
  echo "3. Check if Redis is accessible"
else
  echo "✅ All tests passed! Cron jobs should be working."
  echo ""
  echo "If you still see failures in Supabase dashboard:"
  echo "1. Check the exact time of failures"
  echo "2. Check if they occurred before the token refresh"
  echo "3. Old failures can be ignored if recent runs are successful"
fi

echo ""
echo "=================================================="
