#!/bin/bash
# Start Fresh Data Collection
# This script fetches fresh candle data for all timeframes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/fresh_data_$(date +%Y%m%d_%H%M%S).log"

# Create logs directory
mkdir -p "$LOG_DIR"

SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo -e "${BLUE}=========================================="
echo "🚀 Starting Fresh Data Collection"
echo "==========================================${NC}"
log "=========================================="
log "🚀 Starting Fresh Data Collection"
log "=========================================="

# Step 1: Refresh tokens
echo -e "\n${YELLOW}Step 1: Refreshing Tradovate tokens...${NC}"
log "Step 1: Refreshing Tradovate tokens..."

cd "$PROJECT_DIR"
if python3 token_generator_and_redis_manager.py >> "$LOG_FILE" 2>&1; then
    echo -e "${GREEN}✅ Tokens refreshed successfully${NC}"
    log "✅ Tokens refreshed successfully"
else
    echo -e "${RED}❌ Token refresh failed${NC}"
    log "❌ Token refresh failed"
    exit 1
fi

# Step 2: Fetch real-time candles for all timeframes
echo -e "\n${YELLOW}Step 2: Fetching real-time candles...${NC}"
log "Step 2: Fetching real-time candles..."

TIMEFRAMES=(5 15 30 60)
SUCCESS=0
FAILED=0

for tf in "${TIMEFRAMES[@]}"; do
    echo -e "\n${BLUE}📊 Fetching ${tf}-minute candles...${NC}"
    log "📊 Fetching ${tf}-minute candles..."
    
    RESPONSE=$(curl -s -X POST \
        "${SUPABASE_URL}/functions/v1/fetch-candles" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"timeframe\": ${tf}}")
    
    if echo "$RESPONSE" | grep -q '"success":true'; then
        STORED=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('candles_stored', 0))" 2>/dev/null || echo "0")
        echo -e "${GREEN}✅ ${tf}min: Stored ${STORED} candles${NC}"
        log "✅ ${tf}min: Stored ${STORED} candles"
        ((SUCCESS++))
    else
        echo -e "${RED}❌ ${tf}min: Failed${NC}"
        log "❌ ${tf}min: Failed - Response: $RESPONSE"
        ((FAILED++))
    fi
    
    sleep 2
done

# Step 3: Backfill historical data
echo -e "\n${YELLOW}Step 3: Backfilling historical data...${NC}"
log "Step 3: Backfilling historical data..."

BACKFILL_CONFIG=(
    "5:1"    # 5min: 1 day back
    "15:2"   # 15min: 2 days back
    "30:3"   # 30min: 3 days back
    "60:7"   # 60min: 7 days back
)

for config in "${BACKFILL_CONFIG[@]}"; do
    IFS=':' read -r tf days <<< "$config"
    
    echo -e "\n${BLUE}📥 Backfilling ${tf}min (${days} days)...${NC}"
    log "📥 Backfilling ${tf}min (${days} days)..."
    
    RESPONSE=$(curl -s -X POST \
        "${SUPABASE_URL}/functions/v1/fetch-historical-candles" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"timeframe\": ${tf}, \"days_back\": ${days}}")
    
    if echo "$RESPONSE" | grep -q '"success":true'; then
        STORED=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('candles_stored', 0))" 2>/dev/null || echo "0")
        echo -e "${GREEN}✅ ${tf}min: Stored ${STORED} historical candles${NC}"
        log "✅ ${tf}min: Stored ${STORED} historical candles"
    else
        echo -e "${RED}❌ ${tf}min: Historical fetch failed${NC}"
        log "❌ ${tf}min: Historical fetch failed - Response: $RESPONSE"
    fi
    
    sleep 2
done

# Summary
echo -e "\n${BLUE}=========================================="
echo "📊 Data Collection Summary"
echo "==========================================${NC}"
log "=========================================="
log "📊 Data Collection Summary"
log "=========================================="

echo -e "Real-time fetches:"
echo -e "  Successful: ${GREEN}${SUCCESS}${NC}"
echo -e "  Failed: ${RED}${FAILED}${NC}"

log "Real-time fetches: Successful: ${SUCCESS}, Failed: ${FAILED}"

echo -e "\n${GREEN}✅ Fresh data collection complete!${NC}"
echo -e "${YELLOW}⚡ Automated cron jobs will continue updating every 5/15/30/60 minutes${NC}"

log "✅ Fresh data collection complete!"
log "Log file: $LOG_FILE"

echo -e "\n${BLUE}📝 Next steps:${NC}"
echo "1. Verify data: bash scripts/health_check.sh"
echo "2. Check logs: cat $LOG_FILE"
echo "3. View data in Supabase SQL Editor"
