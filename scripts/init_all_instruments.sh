#!/bin/bash
# Initialize All Instruments
# Fetches initial data for all 4 instruments × 4 timeframes = 16 combinations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Instruments and symbols (Bash 3.2 compatible)
INSTRUMENTS_NAMES=("NQ" "MNQ" "ES" "MES")
INSTRUMENTS_SYMBOLS=("NQZ5" "MNQZ5" "ESZ5" "MESZ5")

# Timeframes
TIMEFRAMES=(5 15 30 60)

echo -e "${BLUE}=========================================="
echo "🚀 Initializing All Instruments"
echo -e "==========================================${NC}\n"

echo -e "${CYAN}Instruments:${NC}"
for i in "${!INSTRUMENTS_NAMES[@]}"; do
    echo "  • ${INSTRUMENTS_NAMES[$i]} (${INSTRUMENTS_SYMBOLS[$i]})"
done

echo -e "\n${CYAN}Timeframes:${NC} 5min, 15min, 30min, 1hour"
echo -e "\n${CYAN}Total combinations:${NC} 16\n"

# Step 1: Refresh tokens
echo -e "${YELLOW}Step 1: Refreshing Tradovate tokens...${NC}"
cd "$PROJECT_DIR"
if python3 token_generator_and_redis_manager.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Tokens refreshed successfully${NC}\n"
else
    echo -e "${RED}❌ Token refresh failed${NC}"
    exit 1
fi

# Step 2: Fetch data for all combinations
echo -e "${YELLOW}Step 2: Fetching data for all instruments and timeframes...${NC}\n"

SUCCESS_COUNT=0
FAILED_COUNT=0
TOTAL_COUNT=0

for i in "${!INSTRUMENTS_NAMES[@]}"; do
    instrument="${INSTRUMENTS_NAMES[$i]}"
    symbol="${INSTRUMENTS_SYMBOLS[$i]}"
    
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 ${instrument} (${symbol})${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    for timeframe in "${TIMEFRAMES[@]}"; do
        ((TOTAL_COUNT++))
        
        tf_label=$([ "$timeframe" = "60" ] && echo "1hour" || echo "${timeframe}min")
        echo -ne "${BLUE}  Testing ${tf_label}...${NC} "
        
        RESPONSE=$(curl -s -X POST \
            "${SUPABASE_URL}/functions/v1/fetch-candles" \
            -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
            -H "Content-Type: application/json" \
            -d "{\"timeframe\": ${timeframe}, \"symbol\": \"${symbol}\"}")
        
        if echo "$RESPONSE" | grep -q '"success":true'; then
            STORED=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('candles_stored', 0))" 2>/dev/null || echo "0")
            echo -e "${GREEN}✅ Stored ${STORED} candles${NC}"
            ((SUCCESS_COUNT++))
        else
            ERROR=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('error', 'Unknown error'))" 2>/dev/null || echo "Connection error")
            echo -e "${RED}❌ Failed: ${ERROR}${NC}"
            ((FAILED_COUNT++))
        fi
        
        sleep 1
    done
    
    echo ""
done

# Summary
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Initialization Summary${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${CYAN}Total combinations tested:${NC} ${TOTAL_COUNT}"
echo -e "${GREEN}✅ Successful:${NC} ${SUCCESS_COUNT}"
echo -e "${RED}❌ Failed:${NC} ${FAILED_COUNT}"

SUCCESS_RATE=$((SUCCESS_COUNT * 100 / TOTAL_COUNT))
echo -e "${CYAN}Success rate:${NC} ${SUCCESS_RATE}%\n"

if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Some operations failed. Check:${NC}"
    echo "  1. Tokens are valid (run: python3 token_generator_and_redis_manager.py)"
    echo "  2. Supabase tables exist (run: scripts/create_all_instrument_tables.sql)"
    echo "  3. RPC functions exist (run: scripts/create_all_insert_functions.sql)"
    echo "  4. Market is open (Futures: Sun 6PM - Fri 5PM ET)"
    echo ""
fi

echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📝 Next Steps:${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo "1. Set up cron jobs in Supabase SQL Editor:"
echo "   Run: scripts/setup_all_instruments_cron.sql"
echo ""
echo "2. Verify data in Supabase:"
echo "   SELECT * FROM orca.mnq_candles_5min ORDER BY candle_time DESC LIMIT 5;"
echo ""
echo "3. Check cron job status:"
echo "   SELECT jobname, active FROM cron.job WHERE jobname LIKE 'fetch-%';"
echo ""

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}🎉 All instruments initialized successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Initialization completed with ${FAILED_COUNT} error(s)${NC}"
    exit 1
fi
