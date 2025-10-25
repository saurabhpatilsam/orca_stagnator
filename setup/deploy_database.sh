#!/bin/bash
# Automated Database Deployment Script
# Deploys all tables, functions, and cron jobs to Supabase

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "=========================================="
echo "🚀 AUTOMATED DATABASE DEPLOYMENT"
echo "=========================================="
echo ""

# Check if database password is provided
if [ -z "$1" ]; then
    echo "❌ Database password required!"
    echo ""
    echo "Usage: bash setup/deploy_database.sh <database_password>"
    echo ""
    echo "Get your database password from:"
    echo "https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/settings/database"
    echo ""
    echo "Or run SQL files manually:"
    echo "https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock/sql/new"
    exit 1
fi

DB_PASSWORD="$1"
DB_HOST="db.dcoukhtfcloqpfmijock.supabase.co"
DB_PORT="5432"
DB_NAME="postgres"
DB_USER="postgres"

DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

echo "📊 Database Configuration:"
echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo ""

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "❌ psql not found!"
    echo "   Please install PostgreSQL client:"
    echo "   brew install postgresql"
    exit 1
fi

echo "🔌 Testing database connection..."
if psql "$DATABASE_URL" -c "SELECT 1;" &> /dev/null; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed!"
    echo "   Check your password and try again."
    exit 1
fi

echo ""
echo "=========================================="
echo "📋 STEP 1: Creating Tables"
echo "=========================================="
echo ""

psql "$DATABASE_URL" -f setup/database/01_create_schema_and_tables.sql
echo "✅ Tables created"

echo ""
echo "=========================================="
echo "📋 STEP 2: Creating RPC Functions"
echo "=========================================="
echo ""

psql "$DATABASE_URL" -f setup/database/02_create_rpc_functions.sql
echo "✅ RPC Functions created"

echo ""
echo "=========================================="
echo "📋 STEP 3: Creating Cron Jobs"
echo "=========================================="
echo ""

psql "$DATABASE_URL" -f setup/database/03_create_cron_jobs.sql
echo "✅ Cron Jobs created"

echo ""
echo "=========================================="
echo "✅ VERIFICATION"
echo "=========================================="
echo ""

# Verify tables
TABLE_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'orca' AND tablename LIKE '%candles%';")
echo "Tables created: ${TABLE_COUNT}/16"

# Verify functions
FUNCTION_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM pg_proc WHERE proname LIKE 'insert_%_candles_%';")
echo "Functions created: ${FUNCTION_COUNT}/16"

# Verify cron jobs
CRON_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM cron.job WHERE jobname LIKE 'fetch-%';")
echo "Cron jobs created: ${CRON_COUNT}/16"

echo ""
if [ "$TABLE_COUNT" -eq 16 ] && [ "$FUNCTION_COUNT" -eq 16 ] && [ "$CRON_COUNT" -eq 16 ]; then
    echo "✅ ALL SYSTEMS DEPLOYED SUCCESSFULLY!"
    echo ""
    echo "🎉 Your automated data collection is now running!"
    echo ""
    echo "Test it:"
    echo "  bash data-collection/verification/test_all_edge_functions.sh"
else
    echo "⚠️  Some components may not have been created properly"
    echo "   Check the output above for errors"
fi

echo ""
echo "=========================================="
echo "🏁 DEPLOYMENT COMPLETE"
echo "=========================================="
