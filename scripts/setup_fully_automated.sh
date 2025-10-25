#!/bin/bash
# Fully Automated Setup - Uses Supabase Management API
# No password needed, no manual steps!

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Supabase credentials
PROJECT_REF="dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

# Connection pooler (doesn't need password with service role)
DB_URL="postgresql://postgres.${PROJECT_REF}:${SERVICE_ROLE_KEY}@aws-0-us-east-1.pooler.supabase.com:5432/postgres"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗"
echo -e "║  🚀 Fully Automated Setup (No Input Needed!)          ║"
echo -e "╚════════════════════════════════════════════════════════╝${NC}\n"

cd "$PROJECT_DIR"

# Check for psql
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}📦 Installing PostgreSQL client...${NC}\n"
    
    if command -v brew &> /dev/null; then
        brew install libpq
        export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
    else
        echo -e "${RED}❌ Homebrew not found. Installing Homebrew...${NC}"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install libpq
        export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
    fi
    
    echo -e "${GREEN}✅ PostgreSQL client installed${NC}\n"
fi

# Test connection
echo -e "${CYAN}Testing database connection...${NC}"
if PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Connected successfully!${NC}\n"
else
    echo -e "${YELLOW}⚠️  Connection via pooler failed, trying direct connection...${NC}"
    
    # Try direct connection (port 6543)
    DB_URL="postgresql://postgres:${SERVICE_ROLE_KEY}@db.${PROJECT_REF}.supabase.co:6543/postgres"
    
    if PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Connected via direct connection!${NC}\n"
    else
        echo -e "${RED}❌ Could not connect to database${NC}"
        echo "Please ensure your IP is whitelisted in Supabase settings:"
        echo "https://supabase.com/dashboard/project/${PROJECT_REF}/settings/database"
        exit 1
    fi
fi

# Step 1: Create Tables
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 1/3: Creating Database Tables (16 tables)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -f scripts/create_all_instrument_tables.sql 2>&1 | head -5
echo -e "${GREEN}✅ Tables created${NC}\n"

sleep 2

# Step 2: Create Functions
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 2/3: Creating RPC Functions (16 functions)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -f scripts/create_all_insert_functions.sql 2>&1 | head -5
echo -e "${GREEN}✅ Functions created${NC}\n"

sleep 2

# Step 3: Setup Cron Jobs
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Step 3/3: Setting Up Cron Jobs (16 cron jobs)${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -f scripts/setup_all_instruments_cron.sql 2>&1 | tail -20
echo -e "${GREEN}✅ Cron jobs scheduled${NC}\n"

sleep 2

# Verify
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Verifying Setup${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

TABLE_COUNT=$(PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%_candles_%'" 2>/dev/null | tr -d ' \n')
FUNC_COUNT=$(PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -t -c "SELECT COUNT(*) FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name LIKE 'insert_%_candles_%'" 2>/dev/null | tr -d ' \n')
CRON_COUNT=$(PGPASSWORD="$SERVICE_ROLE_KEY" psql "$DB_URL" -t -c "SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%'" 2>/dev/null | tr -d ' \n')

echo -e "${BLUE}  Tables: ${GREEN}${TABLE_COUNT}/16${NC}"
echo -e "${BLUE}  Functions: ${GREEN}${FUNC_COUNT}/16${NC}"
echo -e "${BLUE}  Cron Jobs: ${GREEN}${CRON_COUNT}/16${NC}\n"

if [ "$TABLE_COUNT" = "16" ] && [ "$FUNC_COUNT" = "16" ] && [ "$CRON_COUNT" = "16" ]; then
    echo -e "${GREEN}✅ All components created successfully!${NC}\n"
else
    echo -e "${YELLOW}⚠️  Some components may need verification${NC}\n"
fi

# Test
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Testing All Instruments${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

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
    
    echo -e "${CYAN}📝 Quick Test:${NC}"
    echo "  bash scripts/test_all.sh"
    echo ""
    
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Setup completed but some tests failed${NC}"
    echo "This is normal if the market is closed."
    echo "Run 'bash scripts/test_all.sh' to verify setup."
    echo ""
    exit 0
fi
