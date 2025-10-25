#!/bin/bash
# Repository Cleanup Script
# Moves old files to archived folder and organizes the project

set -e

echo "=========================================="
echo "🧹 REPOSITORY CLEANUP"
echo "=========================================="

PROJECT_ROOT="/Users/stagnator/Downloads/orca-ven-backend-main"
cd "$PROJECT_ROOT"

# Create archived folder structure
echo "📁 Creating archived folder structure..."
mkdir -p archived/old_scripts
mkdir -p archived/old_docs
mkdir -p archived/old_sql
mkdir -p archived/old_python

# Move old documentation files
echo "📝 Moving old documentation..."
mv -f ACCOUNTS_SUMMARY_REPORT.md archived/old_docs/ 2>/dev/null || true
mv -f BEST_TOKEN_SOLUTION.md archived/old_docs/ 2>/dev/null || true
mv -f CANDLE_FETCHER_README.md archived/old_docs/ 2>/dev/null || true
mv -f CREDENTIALS.md archived/old_docs/ 2>/dev/null || true
mv -f CRON_DIAGNOSIS_AND_FIX.md archived/old_docs/ 2>/dev/null || true
mv -f DAEMON_SETUP.md archived/old_docs/ 2>/dev/null || true
mv -f DEPLOYMENT_SUCCESS.md archived/old_docs/ 2>/dev/null || true
mv -f EDGE_FUNCTIONS_AUTOMATION.md archived/old_docs/ 2>/dev/null || true
mv -f EDGE_FUNCTIONS_COMPLETE_GUIDE.md archived/old_docs/ 2>/dev/null || true
mv -f FRESH_DATA_SETUP.md archived/old_docs/ 2>/dev/null || true
mv -f MCP_ORGANIZATION_COMPLETE.md archived/old_docs/ 2>/dev/null || true
mv -f MCP_TOKENS_STATUS.md archived/old_docs/ 2>/dev/null || true
mv -f MULTI_INSTRUMENT_SETUP_GUIDE.md archived/old_docs/ 2>/dev/null || true
mv -f OHLC_API_RESEARCH.md archived/old_docs/ 2>/dev/null || true
mv -f REDIS_SYNC_COMPLETE.md archived/old_docs/ 2>/dev/null || true
mv -f REORGANIZATION_COMPLETE.md archived/old_docs/ 2>/dev/null || true
mv -f REORGANIZATION_PLAN.md archived/old_docs/ 2>/dev/null || true
mv -f RUN_THESE_SQL_FILES.md archived/old_docs/ 2>/dev/null || true
mv -f SETUP_CANDLE_FETCHER.md archived/old_docs/ 2>/dev/null || true
mv -f SETUP_NOW.md archived/old_docs/ 2>/dev/null || true
mv -f SETUP_SUMMARY.md archived/old_docs/ 2>/dev/null || true
mv -f SUPABASE_SERVERLESS_SETUP.md archived/old_docs/ 2>/dev/null || true
mv -f SUPABASE_TOKEN_MANAGER.md archived/old_docs/ 2>/dev/null || true
mv -f TOKEN_FLOW_DOCUMENTATION.md archived/old_docs/ 2>/dev/null || true
mv -f TRADOVATE_ENDPOINTS.md archived/old_docs/ 2>/dev/null || true

# Move old SQL files
echo "🗄️  Moving old SQL files..."
mv -f create_candle_tables_simple.sql archived/old_sql/ 2>/dev/null || true
mv -f create_insert_functions.sql archived/old_sql/ 2>/dev/null || true
mv -f setup_complete.sql archived/old_sql/ 2>/dev/null || true
mv -f setup_cron_jobs.sql archived/old_sql/ 2>/dev/null || true
mv -f supabase_candle_tables.sql archived/old_sql/ 2>/dev/null || true
mv -f supabase_setup.sql archived/old_sql/ 2>/dev/null || true
mv -f reload_schema.sql archived/old_sql/ 2>/dev/null || true

# Move old Python scripts (not in organized folders)
echo "🐍 Moving old Python scripts..."
mv -f automated_candle_fetcher.py archived/old_python/ 2>/dev/null || true
mv -f candle_daemon.py archived/old_python/ 2>/dev/null || true
mv -f check_all_redis.py archived/old_python/ 2>/dev/null || true
mv -f check_available_accounts.py archived/old_python/ 2>/dev/null || true
mv -f fetch_and_store_candles.py archived/old_python/ 2>/dev/null || true
mv -f fetch_tradovate_accounts.py archived/old_python/ 2>/dev/null || true
mv -f get_accounts_balances.py archived/old_python/ 2>/dev/null || true
mv -f get_all_accounts_from_redis.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_30min_tradingview.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_30min_tradovate.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_30min_websocket.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_30min_working.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_candle_close.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_last_candle_ohlc.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_ohlc.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_ohlc_http.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_ohlc_simple.py archived/old_python/ 2>/dev/null || true
mv -f get_nq_realtime.py archived/old_python/ 2>/dev/null || true
mv -f get_tokens.py archived/old_python/ 2>/dev/null || true
mv -f place_mnq_24980_accounts_10_11.py archived/old_python/ 2>/dev/null || true
mv -f simple_main.py archived/old_python/ 2>/dev/null || true
mv -f store_candles_to_supabase.py archived/old_python/ 2>/dev/null || true
mv -f sync_tokens_to_supabase.py archived/old_python/ 2>/dev/null || true
mv -f sync_tradovate_accounts_to_redis.py archived/old_python/ 2>/dev/null || true
mv -f test_deployment.py archived/old_python/ 2>/dev/null || true
mv -f test_edge_functions.py archived/old_python/ 2>/dev/null || true
mv -f tradovate_socket_working.py archived/old_python/ 2>/dev/null || true
mv -f tradovate_websocket_working.py archived/old_python/ 2>/dev/null || true

# Move old shell scripts
echo "📜 Moving old shell scripts..."
mv -f check_daemon.sh archived/old_scripts/ 2>/dev/null || true
mv -f deploy_supabase_functions.sh archived/old_scripts/ 2>/dev/null || true
mv -f deploy_token_manager.sh archived/old_scripts/ 2>/dev/null || true
mv -f run_token_generator.sh archived/old_scripts/ 2>/dev/null || true
mv -f setup_and_test_edge_functions.sh archived/old_scripts/ 2>/dev/null || true
mv -f setup_environment_vars.sh archived/old_scripts/ 2>/dev/null || true
mv -f setup_mcp_config.sh archived/old_scripts/ 2>/dev/null || true
mv -f start_daemon.sh archived/old_scripts/ 2>/dev/null || true
mv -f stop_daemon.sh archived/old_scripts/ 2>/dev/null || true
mv -f test_functions.sh archived/old_scripts/ 2>/dev/null || true

# Move old folders
echo "📦 Moving old folders..."
mv -f tradovate-market-stream-main archived/ 2>/dev/null || true
mv -f tradovate_data archived/ 2>/dev/null || true

# Remove empty folders
echo "🗑️  Removing empty folders..."
find . -type d -empty -not -path '*/\.*' -delete 2>/dev/null || true

# Clean up duplicate supabase functions folder
echo "🧼 Cleaning up duplicate folders..."
rm -rf supabase/functions/fetch_candles 2>/dev/null || true

echo ""
echo "=========================================="
echo "✅ CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "📊 Summary:"
echo "  - Old docs moved to archived/old_docs/"
echo "  - Old SQL files moved to archived/old_sql/"
echo "  - Old Python scripts moved to archived/old_python/"
echo "  - Old scripts moved to archived/old_scripts/"
echo "  - Empty folders removed"
echo ""
echo "📁 New Structure:"
echo "  ✅ setup/            - Setup scripts"
echo "  ✅ edge-functions/   - Edge functions code"
echo "  ✅ data-collection/  - Data collection tools"
echo "  ✅ documentation/    - Documentation"
echo "  ✅ trading/          - Trading system"
echo "  ✅ app/              - API backend"
echo "  ✅ frontend/         - Frontend code"
echo "  ✅ archived/         - Old files"
echo ""
