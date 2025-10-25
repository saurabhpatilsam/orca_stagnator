#!/bin/bash
# Test all edge functions for all instruments and timeframes

echo "=========================================="
echo "Testing All Edge Functions"
echo "=========================================="

SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Test all instruments
INSTRUMENTS=("NQZ5" "MNQZ5" "ESZ5" "MESZ5")
TIMEFRAMES=(5 15 30 60)

for symbol in "${INSTRUMENTS[@]}"; do
    echo ""
    echo "Testing $symbol..."
    for timeframe in "${TIMEFRAMES[@]}"; do
        echo -n "  ${timeframe}min: "
        response=$(curl -s -X POST \
            "${SUPABASE_URL}/functions/v1/fetch-candles" \
            -H "Authorization: Bearer ${SERVICE_KEY}" \
            -H "Content-Type: application/json" \
            -d "{\"timeframe\": ${timeframe}, \"symbol\": \"${symbol}\"}")
        
        success=$(echo $response | jq -r '.success')
        fetched=$(echo $response | jq -r '.candles_fetched')
        stored=$(echo $response | jq -r '.candles_stored')
        
        if [ "$success" = "true" ]; then
            echo "✅ Fetched: $fetched, Stored: $stored"
        else
            echo "❌ Failed"
        fi
    done
done

echo ""
echo "=========================================="
echo "Testing Complete"
echo "=========================================="
