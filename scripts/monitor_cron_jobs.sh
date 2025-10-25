#!/bin/bash
# Comprehensive Cron Job Health Monitor
# Checks if data is being collected successfully

set -euo pipefail

echo "=================================================="
echo "🔍 CRON JOB HEALTH CHECK"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID="dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Function to test edge function
test_edge_function() {
    local timeframe=$1
    local symbol=$2
    local name=$3
    
    echo -n "Testing $name ($timeframe min, $symbol)... "
    
    response=$(curl -s -X POST \
        "https://${PROJECT_ID}.supabase.co/functions/v1/fetch-candles" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"timeframe\": ${timeframe}, \"symbol\": \"${symbol}\"}")
    
    success=$(echo "$response" | jq -r '.success // false')
    candles=$(echo "$response" | jq -r '.candles_stored // 0')
    error=$(echo "$response" | jq -r '.error // ""')
    
    if [ "$success" = "true" ] && [ "$candles" -gt 0 ]; then
        echo -e "${GREEN}✅ OK${NC} ($candles candles)"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        if [ -n "$error" ]; then
            echo "   Error: $error"
        fi
        return 1
    fi
}

# Function to check data freshness
check_data_freshness() {
    local instrument=$1
    local timeframe=$2
    
    echo -n "Checking $instrument ${timeframe} data freshness... "
    
    # This would require a SQL query to check last insert time
    # For now, just indicate it needs manual verification
    echo -e "${YELLOW}⏳ Check manually${NC}"
}

echo "📊 Testing Edge Functions (16 streams)"
echo "=================================================="
echo ""

success_count=0
fail_count=0

# NQ tests
test_edge_function 5 "NQZ5" "NQ 5min" && ((success_count++)) || ((fail_count++))
test_edge_function 15 "NQZ5" "NQ 15min" && ((success_count++)) || ((fail_count++))
test_edge_function 30 "NQZ5" "NQ 30min" && ((success_count++)) || ((fail_count++))
test_edge_function 60 "NQZ5" "NQ 60min" && ((success_count++)) || ((fail_count++))

echo ""

# MNQ tests
test_edge_function 5 "MNQZ5" "MNQ 5min" && ((success_count++)) || ((fail_count++))
test_edge_function 15 "MNQZ5" "MNQ 15min" && ((success_count++)) || ((fail_count++))
test_edge_function 30 "MNQZ5" "MNQ 30min" && ((success_count++)) || ((fail_count++))
test_edge_function 60 "MNQZ5" "MNQ 60min" && ((success_count++)) || ((fail_count++))

echo ""

# ES tests
test_edge_function 5 "ESZ5" "ES 5min" && ((success_count++)) || ((fail_count++))
test_edge_function 15 "ESZ5" "ES 15min" && ((success_count++)) || ((fail_count++))
test_edge_function 30 "ESZ5" "ES 30min" && ((success_count++)) || ((fail_count++))
test_edge_function 60 "ESZ5" "ES 60min" && ((success_count++)) || ((fail_count++))

echo ""

# MES tests
test_edge_function 5 "MESZ5" "MES 5min" && ((success_count++)) || ((fail_count++))
test_edge_function 15 "MESZ5" "MES 15min" && ((success_count++)) || ((fail_count++))
test_edge_function 30 "MESZ5" "MES 30min" && ((success_count++)) || ((fail_count++))
test_edge_function 60 "MESZ5" "MES 60min" && ((success_count++)) || ((fail_count++))

echo ""
echo "=================================================="
echo "📈 RESULTS"
echo "=================================================="
echo -e "${GREEN}✅ Successful: $success_count/16${NC}"
echo -e "${RED}❌ Failed: $fail_count/16${NC}"
echo ""

# Test token refresh
echo "🔄 Testing Token Refresh Function..."
refresh_response=$(curl -s -X POST \
    "https://${PROJECT_ID}.supabase.co/functions/v1/refresh-tokens" \
    -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json")

refresh_success=$(echo "$refresh_response" | jq -r '.success // false')
tokens_updated=$(echo "$refresh_response" | jq -r '.tokens_updated // 0')

if [ "$refresh_success" = "true" ]; then
    echo -e "${GREEN}✅ Token refresh working${NC} ($tokens_updated tokens updated)"
else
    echo -e "${RED}❌ Token refresh failed${NC}"
    echo "$refresh_response" | jq '.'
fi

echo ""
echo "=================================================="
echo "💡 RECOMMENDATIONS"
echo "=================================================="

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}✅ All edge functions working perfectly!${NC}"
    echo ""
    echo "Your cron jobs should be collecting data successfully."
    echo "Data collection happens:"
    echo "  • Every 5 minutes for 5min timeframes"
    echo "  • Every 15 minutes for 15min timeframes"
    echo "  • Every 30 minutes for 30min timeframes"
    echo "  • Every 60 minutes for 60min timeframes"
    echo ""
    echo "Token refresh happens every 50 minutes automatically."
else
    echo -e "${RED}⚠️  Some functions are failing!${NC}"
    echo ""
    echo "Possible issues:"
    echo "  1. Tokens expired - Run: cd data-collection/token-management && python3 token_generator_and_redis_manager.py"
    echo "  2. Redis connection issues - Check REDIS_PASSWORD in Supabase secrets"
    echo "  3. Tradovate API issues - Check if demo API is accessible"
fi

echo ""
echo "=================================================="
echo "🏁 Health check complete!"
echo "=================================================="
