#!/bin/bash
# Install ONLY the RPC functions (tables already exist)

set -e

echo "=========================================="
echo "📦 INSTALLING RPC FUNCTIONS ONLY"
echo "=========================================="
echo ""

SUPABASE_URL="https://dcoukhtfcloqpfmijock.supabase.co"
SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRjb3VraHRmY2xvcXBmbWlqb2NrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzcwMTgwMywiZXhwIjoyMDY5Mjc3ODAzfQ.iNzNrB0z64m8cINx0DeVCuAbcStWpMPx_bDos_vgO7w"

echo "⚠️  This will install the RPC functions using Supabase SQL Editor"
echo ""
echo "📋 Instructions:"
echo "1. Open: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new"
echo "2. Copy the SQL from: setup/database/02_create_rpc_functions.sql"
echo "3. Paste and click 'Run'"
echo "4. Come back and run: bash data-collection/verification/test_all_edge_functions.sh"
echo ""
echo "Or I can show you the SQL content now..."
echo ""

read -p "Press Enter to see the SQL content (or Ctrl+C to cancel)..."

echo ""
echo "=========================================="
echo "📄 SQL CONTENT TO RUN"
echo "=========================================="
echo ""

cat setup/database/02_create_rpc_functions.sql

echo ""
echo "=========================================="
echo "✅ Copy the above SQL and run it in Supabase SQL Editor"
echo "=========================================="
