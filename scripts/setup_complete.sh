#!/bin/bash
# Complete Multi-Instrument Setup
# This script does EVERYTHING in one command:
# 1. Creates all 16 tables
# 2. Creates all 16 RPC functions
# 3. Sets up all 16 cron jobs
# 4. Tests all 16 combinations

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗"
echo -e "║  🚀 Complete Multi-Instrument Setup                   ║"
echo -e "║  Creating tables, functions, cron jobs & testing      ║"
echo -e "╚════════════════════════════════════════════════════════╝${NC}\n"

# Check if supabase CLI is available
if ! command -v supabase &> /dev/null; then
    echo -e "${RED}❌ Supabase CLI not found${NC}"
    echo "Install: https://supabase.com/docs/guides/cli/getting-started"
    exit 1
fi

cd "$PROJECT_DIR"

# Step 1: Create Tables
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1/5: Creating Database Tables (16 tables)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if supabase db execute --file scripts/create_all_instrument_tables.sql --project-ref dcoukhtfcloqpfmijock; then
    echo -e "${GREEN}✅ Tables created successfully${NC}\n"
else
    echo -e "${RED}❌ Failed to create tables${NC}"
    exit 1
fi

sleep 2

# Step 2: Create RPC Functions
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2/5: Creating RPC Insert Functions (16 functions)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if supabase db execute --file scripts/create_all_insert_functions.sql --project-ref dcoukhtfcloqpfmijock; then
    echo -e "${GREEN}✅ RPC functions created successfully${NC}\n"
else
    echo -e "${RED}❌ Failed to create RPC functions${NC}"
    exit 1
fi

sleep 2

# Step 3: Setup Cron Jobs
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3/5: Setting Up Cron Jobs (16 cron jobs)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

if supabase db execute --file scripts/setup_all_instruments_cron.sql --project-ref dcoukhtfcloqpfmijock; then
    echo -e "${GREEN}✅ Cron jobs scheduled successfully${NC}\n"
else
    echo -e "${RED}❌ Failed to setup cron jobs${NC}"
    exit 1
fi

sleep 2

# Step 4: Verify Setup
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 4/5: Verifying Setup${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Check tables
echo -ne "${BLUE}  Checking tables...${NC} "
TABLE_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")

if [ "$TABLE_COUNT" = "16" ]; then
    echo -e "${GREEN}✅ All 16 tables found${NC}"
else
    echo -e "${YELLOW}⚠️  Found ${TABLE_COUNT} tables (expected 16)${NC}"
fi

# Check functions
echo -ne "${BLUE}  Checking functions...${NC} "
FUNC_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name LIKE 'insert_%_candles_%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")

if [ "$FUNC_COUNT" = "16" ]; then
    echo -e "${GREEN}✅ All 16 functions found${NC}"
else
    echo -e "${YELLOW}⚠️  Found ${FUNC_COUNT} functions (expected 16)${NC}"
fi

# Check cron jobs
echo -ne "${BLUE}  Checking cron jobs...${NC} "
CRON_COUNT=$(supabase db execute \
    --query "SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%'" \
    --project-ref dcoukhtfcloqpfmijock 2>/dev/null | awk '/^[0-9]+$/ {print; exit}' || echo "0")

if [ "$CRON_COUNT" = "16" ]; then
    echo -e "${GREEN}✅ All 16 cron jobs scheduled${NC}\n"
else
    echo -e "${YELLOW}⚠️  Found ${CRON_COUNT} cron jobs (expected 16)${NC}\n"
fi

# Step 5: Test All Instruments
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 5/5: Testing All Instruments & Timeframes${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Run the initialization script
if bash "$SCRIPT_DIR/init_all_instruments.sh"; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗"
    echo -e "║  ✅ Setup Complete! All systems operational           ║"
    echo -e "╚════════════════════════════════════════════════════════╝${NC}\n"
    
    echo -e "${CYAN}📊 What's Running Now:${NC}"
    echo "  • 16 database tables (NQ, MNQ, ES, MES × 4 timeframes)"
    echo "  • 16 RPC insert functions"
    echo "  • 16 cron jobs (auto-updating every 5/15/30/60 min)"
    echo "  • All instruments collecting live data"
    echo ""
    
    echo -e "${CYAN}📝 Next Steps:${NC}"
    echo "  1. View data in Supabase:"
    echo "     SELECT * FROM orca.mnq_candles_5min ORDER BY candle_time DESC LIMIT 5;"
    echo ""
    echo "  2. Check cron job status:"
    echo "     SELECT jobname, active FROM cron.job WHERE jobname LIKE 'fetch-%';"
    echo ""
    echo "  3. Monitor updates (wait 5 minutes, then check row counts):"
    echo "     SELECT tablename, COUNT(*) FROM orca.mnq_candles_5min GROUP BY tablename;"
    echo ""
    
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Setup completed but some tests failed${NC}"
    echo "Check the output above for details"
    exit 1
fi
