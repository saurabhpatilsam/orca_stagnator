#!/bin/bash
# Setup Multi-Instrument via Supabase API
# This bypasses the Supabase CLI and runs SQL directly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Supabase credentials
PROJECT_REF="dcoukhtfcloqpfmijock"
SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"
SUPABASE_URL="https://${PROJECT_REF}.supabase.co"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗"
echo -e "║  🚀 Complete Multi-Instrument Setup (API Method)      ║"
echo -e "╚════════════════════════════════════════════════════════╝${NC}\n"

cd "$PROJECT_DIR"

# Function to execute SQL via Supabase REST API
execute_sql() {
    local sql_file=$1
    local step_name=$2
    
    echo -e "${CYAN}${step_name}${NC}"
    
    # Read SQL file and escape it for JSON
    local sql_content=$(cat "$sql_file")
    
    # Execute via PostgREST rpc endpoint
    local response=$(curl -s -X POST \
        "${SUPABASE_URL}/rest/v1/rpc/exec_sql" \
        -H "apikey: ${SERVICE_ROLE_KEY}" \
        -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=minimal" \
        -d "{\"query\": $(echo "$sql_content" | jq -Rs .)}" 2>&1)
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ ${step_name} completed${NC}\n"
        return 0
    else
        echo -e "${RED}❌ ${step_name} failed${NC}"
        echo -e "${YELLOW}Response: ${response}${NC}\n"
        return 1
    fi
}

# Alternative: Use PostgreSQL connection string directly
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}Method: Running SQL files in Supabase SQL Editor${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}The automated script can't run SQL files with your Supabase CLI version.${NC}"
echo -e "${YELLOW}Please follow these manual steps:${NC}\n"

echo -e "${CYAN}Step 1: Open Supabase SQL Editor${NC}"
echo -e "Go to: ${BLUE}https://supabase.com/dashboard/project/${PROJECT_REF}/sql/new${NC}\n"

echo -e "${CYAN}Step 2: Run Table Creation SQL${NC}"
echo -e "1. Copy contents of: ${GREEN}scripts/create_all_instrument_tables.sql${NC}"
echo -e "2. Paste in SQL Editor and click 'Run'"
echo -e "3. Wait for completion (should see 16 tables created)\n"

echo -e "${CYAN}Step 3: Run Function Creation SQL${NC}"
echo -e "1. Copy contents of: ${GREEN}scripts/create_all_insert_functions.sql${NC}"
echo -e "2. Paste in SQL Editor and click 'Run'"
echo -e "3. Wait for completion (should see 16 functions created)\n"

echo -e "${CYAN}Step 4: Run Cron Setup SQL${NC}"
echo -e "1. Copy contents of: ${GREEN}scripts/setup_all_instruments_cron.sql${NC}"
echo -e "2. Paste in SQL Editor and click 'Run'"
echo -e "3. Wait for completion (should see 16 cron jobs scheduled)\n"

echo -e "${CYAN}Step 5: Test the Setup${NC}"
echo -e "Run: ${GREEN}bash scripts/init_all_instruments.sh${NC}"
echo -e "This will test all 16 combinations and fetch initial data\n"

echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📁 Files are ready at:${NC}"
echo -e "  • ${GREEN}scripts/create_all_instrument_tables.sql${NC}"
echo -e "  • ${GREEN}scripts/create_all_insert_functions.sql${NC}"
echo -e "  • ${GREEN}scripts/setup_all_instruments_cron.sql${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}Would you like me to open the SQL files for you? (y/n)${NC}"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "\n${CYAN}Opening SQL files...${NC}\n"
    
    echo -e "${GREEN}File 1: Tables${NC}"
    echo "---"
    head -50 scripts/create_all_instrument_tables.sql
    echo "... (truncated, see full file)"
    echo ""
    
    echo -e "${BLUE}Press Enter to continue...${NC}"
    read
fi

echo -e "${GREEN}✅ Setup instructions provided!${NC}"
echo -e "${CYAN}After running the SQL in Supabase, test with:${NC}"
echo -e "${GREEN}bash scripts/init_all_instruments.sh${NC}\n"
