#!/bin/bash
# Open All Files Needed for Setup

echo "🚀 Opening Supabase SQL Editor and all SQL files..."
echo ""

# Open Supabase SQL Editor
open "https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new"
sleep 1

# Open all 3 SQL files
open scripts/create_all_instrument_tables.sql
sleep 0.5
open scripts/create_all_insert_functions.sql
sleep 0.5
open scripts/setup_all_instruments_cron.sql

echo "✅ Opened:"
echo "   1. Supabase SQL Editor (browser)"
echo "   2. create_all_instrument_tables.sql"
echo "   3. create_all_insert_functions.sql"
echo "   4. setup_all_instruments_cron.sql"
echo ""
echo "📋 Now just:"
echo "   - Copy each file (Cmd+A, Cmd+C)"
echo "   - Paste in Supabase SQL Editor"
echo "   - Click 'Run'"
echo "   - Repeat for all 3 files"
echo ""
echo "🧪 After running all 3, test with:"
echo "   bash scripts/init_all_instruments.sh"
