#!/bin/bash
# Test Token Refresh Fix
# This script triggers the edge function and verifies tokens are refreshed in Redis

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/test_token_refresh_$(date +%Y%m%d_%H%M%S).log"

mkdir -p "$LOG_DIR"

echo "=========================================="
echo "🧪 Testing Token Refresh Fix"
echo "=========================================="

# Load environment
if [ -f "$PROJECT_DIR/.env.configured" ]; then
    source "$PROJECT_DIR/.env.configured"
else
    echo "❌ .env.configured not found"
    exit 1
fi

SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"
SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

echo "📊 Step 1: Checking current Redis token TTL..."
echo ""

# Check Redis tokens before triggering edge function
python3 << EOF
import redis
import os

redis_client = redis.Redis(
    host='${REDIS_HOST}',
    port=${REDIS_PORT},
    password='${REDIS_PASSWORD}',
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True
)

print("📋 Tokens in Redis BEFORE edge function call:")
print("-" * 50)
for key in ['token:APEX_266668', 'token:PAAPEX2666680000001']:
    ttl = redis_client.ttl(key)
    token = redis_client.get(key)
    if token:
        print(f"  {key}")
        print(f"    TTL: {ttl}s ({ttl/60:.1f} minutes)")
        print(f"    Token length: {len(token)} chars")
        print(f"    Preview: {token[:50]}...")
    else:
        print(f"  {key}: NOT FOUND or EXPIRED")
print("")
EOF

echo ""
echo "🚀 Step 2: Triggering edge function to refresh tokens..."
echo ""

# Trigger fetch-candles edge function
response=$(curl -s -X POST \
    "${SUPABASE_URL}/functions/v1/fetch-candles" \
    -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"timeframe": 5, "symbol": "MNQZ5"}')

echo "📥 Edge function response:"
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

# Wait a moment for Redis update
sleep 2

echo "📊 Step 3: Checking Redis token TTL AFTER edge function call..."
echo ""

# Check Redis tokens after triggering edge function
python3 << EOF
import redis
import os

redis_client = redis.Redis(
    host='${REDIS_HOST}',
    port=${REDIS_PORT},
    password='${REDIS_PASSWORD}',
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True
)

print("📋 Tokens in Redis AFTER edge function call:")
print("-" * 50)
for key in ['token:APEX_266668', 'token:PAAPEX2666680000001']:
    ttl = redis_client.ttl(key)
    token = redis_client.get(key)
    if token:
        print(f"  {key}")
        print(f"    TTL: {ttl}s ({ttl/60:.1f} minutes)")
        print(f"    Token length: {len(token)} chars")
        print(f"    Preview: {token[:50]}...")
        if ttl > 3500:
            print(f"    ✅ Token refreshed! (TTL reset to near 3600s)")
        elif ttl > 0:
            print(f"    ⚠️  Token not refreshed (TTL not reset)")
        else:
            print(f"    ❌ Token expired")
    else:
        print(f"  {key}: NOT FOUND or EXPIRED")
print("")
EOF

echo ""
echo "=========================================="
echo "✅ Test Complete"
echo "=========================================="
echo ""
echo "If TTL was reset to ~3600s, the fix is working!"
echo "The edge function now automatically refreshes tokens in Redis."
echo ""
