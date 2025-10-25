#!/bin/bash
# Auto Token Refresh Script
# Runs every 50 minutes to refresh Tradovate tokens before they expire (1 hour TTL)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/token_refresh_$(date +%Y%m%d).log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=========================================="
log "🔄 Starting automatic token refresh"
log "=========================================="

# Change to project directory
cd "$PROJECT_DIR"

# Run the token generator
if python3 token_generator_and_redis_manager.py >> "$LOG_FILE" 2>&1; then
    log "✅ Token refresh completed successfully"
    
    # Test one edge function to verify tokens work
    TEST_RESPONSE=$(curl -s -X POST \
        "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles" \
        -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w" \
        -H "Content-Type: application/json" \
        -d '{"timeframe": 5}')
    
    if echo "$TEST_RESPONSE" | grep -q '"success":true'; then
        log "✅ Edge function test passed - tokens are working"
    else
        log "⚠️  Edge function test failed - tokens may not be working properly"
        log "Response: $TEST_RESPONSE"
    fi
else
    log "❌ Token refresh failed"
    exit 1
fi

# Clean up old log files (keep last 7 days)
find "$LOG_DIR" -name "token_refresh_*.log" -mtime +7 -delete 2>/dev/null || true

log "=========================================="
log "🏁 Token refresh cycle complete"
log "=========================================="
