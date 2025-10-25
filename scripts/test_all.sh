#!/bin/bash
# Quick Test Script - Check if everything is working

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Multi-Instrument Setup${NC}\n"

# Test 1: Check tables
echo -ne "${CYAN}1. Checking tables...${NC} "
TABLE_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")
echo -e "${GREEN}✅ Found ${TABLE_COUNT}/16 tables${NC}"

# Test 2: Check functions
echo -ne "${CYAN}2. Checking RPC functions...${NC} "
FUNC_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name LIKE 'insert_%_candles_%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")
echo -e "${GREEN}✅ Found ${FUNC_COUNT}/16 functions${NC}"

# Test 3: Check cron jobs
echo -ne "${CYAN}3. Checking cron jobs...${NC} "
CRON_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")
echo -e "${GREEN}✅ Found ${CRON_COUNT}/16 cron jobs${NC}"

# Test 4: Check data in tables
echo -e "\n${CYAN}4. Checking data in tables:${NC}"

for instrument in nq mnq es mes; do
    ROW_COUNT=$(supabase db execute \
        --query "SELECT COUNT(*) FROM orca.${instrument}_candles_5min" \
        --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")
    
    # Convert to uppercase for display (macOS compatible)
    instrument_upper=$(echo "$instrument" | tr '[:lower:]' '[:upper:]')
    
    if [ "$ROW_COUNT" -gt "0" ]; then
        echo -e "   ${instrument_upper}: ${GREEN}${ROW_COUNT} candles${NC}"
    else
        echo -e "   ${instrument_upper}: ${YELLOW}No data yet${NC}"
    fi
done

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ "$TABLE_COUNT" = "16" ] && [ "$FUNC_COUNT" = "16" ] && [ "$CRON_COUNT" = "16" ]; then
    echo -e "${GREEN}✅ All systems operational!${NC}"
else
    echo -e "${YELLOW}⚠️  Some components missing, run setup again${NC}"
fi
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
