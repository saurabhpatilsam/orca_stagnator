#!/bin/bash
# Health Check Script for Edge Functions
# Tests all edge functions and reports their status

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/health_check_$(date +%Y%m%d).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

test_edge_function() {
    local timeframe=$1
    local response=$(curl -s -X POST \
        "${SUPABASE_URL}/functions/v1/fetch-candles" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"timeframe\": ${timeframe}}")
    
    if echo "$response" | grep -q '"success":true'; then
        echo -e "${GREEN}✅ ${timeframe}min candles: WORKING${NC}"
        log "✅ ${timeframe}min candles: WORKING"
        return 0
    else
        echo -e "${RED}❌ ${timeframe}min candles: FAILED${NC}"
        log "❌ ${timeframe}min candles: FAILED - Response: $response"
        return 1
    fi
}

test_scheduler() {
    local response=$(curl -s -X POST \
        "${SUPABASE_URL}/functions/v1/scheduler" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -d '{}')
    
    if echo "$response" | grep -q '"total_schedules"'; then
        echo -e "${GREEN}✅ Scheduler: WORKING${NC}"
        log "✅ Scheduler: WORKING"
        return 0
    else
        echo -e "${RED}❌ Scheduler: FAILED${NC}"
        log "❌ Scheduler: FAILED - Response: $response"
        return 1
    fi
}

echo "=========================================="
echo "🏥 Edge Functions Health Check"
echo "=========================================="
log "=========================================="
log "🏥 Starting health check"
log "=========================================="

FAILED=0
PASSED=0

# Test each timeframe
for tf in 5 15 30 60; do
    if test_edge_function $tf; then
        ((PASSED++))
    else
        ((FAILED++))
    fi
    sleep 1
done

# Test scheduler
echo ""
if test_scheduler; then
    ((PASSED++))
else
    ((FAILED++))
fi

echo ""
echo "=========================================="
echo "📊 Health Check Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"

log "=========================================="
log "📊 Health Check Summary: Passed: ${PASSED}, Failed: ${FAILED}"
log "=========================================="

if [ $FAILED -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some functions failed. Consider running:${NC}"
    echo "   python3 token_generator_and_redis_manager.py"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All edge functions are healthy!${NC}"
exit 0
