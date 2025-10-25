#!/bin/bash
set -euo pipefail

PROJECT_ID="dcoukhtfcloqpfmijock"

echo "🚀 Refreshing candle data via Supabase Edge Functions"
echo "Project: ${PROJECT_ID}"

if ! command -v supabase >/dev/null 2>&1; then
  echo "supabase CLI not found. Install from https://supabase.com/docs/guides/cli" >&2
  exit 1
fi

supabase link --project-ref "${PROJECT_ID}" >/dev/null 2>&1 || true

function invoke_fetch() {
  local timeframe="$1"
  echo "\n📈 Fetching realtime candles (${timeframe} min)"
  supabase functions invoke fetch-candles --no-verify-jwt --body "{\"timeframe\": ${timeframe}}"
}

function invoke_historical() {
  local timeframe="$1"
  local days="$2"
  echo "\n🕰️ Backfilling historical candles (${timeframe} min, ${days} days)"
  supabase functions invoke fetch-historical-candles --no-verify-jwt --body "{\"timeframe\": ${timeframe}, \"days_back\": ${days}}"
}

echo "\n=== Real-time fetch ==="
invoke_fetch 1
invoke_fetch 5
invoke_fetch 10
invoke_fetch 15
invoke_fetch 30
invoke_fetch 60

echo "\n=== Historical backfill ==="
invoke_historical 1 2
invoke_historical 10 2
invoke_historical 15 3
invoke_historical 30 5
invoke_historical 60 10

echo "\n✅ Candle refresh complete"
