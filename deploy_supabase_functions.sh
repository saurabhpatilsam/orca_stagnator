#!/bin/bash
# Deploy Supabase Edge Functions for automated candle fetching

set -e

echo "🚀 Deploying Supabase Edge Functions for Candle Fetching"
echo "========================================================"

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    npm install -g supabase
fi

# Check if we're in a Supabase project
if [ ! -f "supabase/config.toml" ]; then
    echo "❌ Not in a Supabase project directory"
    echo "💡 Run 'supabase init' first"
    exit 1
fi

# Login to Supabase (if not already logged in)
echo "🔐 Checking Supabase authentication..."
if ! supabase projects list &> /dev/null; then
    echo "🔑 Please login to Supabase:"
    supabase login
fi

# Link to project (if not already linked)
echo "🔗 Linking to Supabase project..."
if [ ! -f ".supabase/config.toml" ]; then
    echo "📋 Available projects:"
    supabase projects list
    echo ""
    read -p "Enter your project reference ID: " PROJECT_REF
    supabase link --project-ref "$PROJECT_REF"
else
    echo "✅ Already linked to project"
fi

# Deploy the database migration
echo "📊 Deploying database migration..."
supabase db push

# Deploy Edge Functions
echo "🌐 Deploying Edge Functions..."

echo "  📦 Deploying fetch-candles function..."
supabase functions deploy fetch-candles --no-verify-jwt

echo "  📊 Deploying fetch-historical-candles function..."
supabase functions deploy fetch-historical-candles --no-verify-jwt

echo "  ⏰ Deploying scheduler function..."
supabase functions deploy scheduler --no-verify-jwt

# Set environment variables for functions
echo "🔧 Setting up environment variables..."

# Get project details
PROJECT_REF=$(cat .supabase/config.toml | grep project_id | cut -d'"' -f2)
SUPABASE_URL="https://${PROJECT_REF}.supabase.co"

echo "📝 Please set these environment variables in your Supabase dashboard:"
echo "   Go to: https://supabase.com/dashboard/project/${PROJECT_REF}/settings/functions"
echo ""
echo "   Required variables:"
echo "   SUPABASE_URL=${SUPABASE_URL}"
echo "   SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>"
echo "   SUPABASE_ANON_KEY=<your-anon-key>"
echo "   REDIS_HOST=redismanager.redis.cache.windows.net"
echo "   REDIS_PORT=6380"
echo "   REDIS_PASSWORD=<your-redis-password>"
echo ""

# Test the functions
echo "🧪 Testing functions..."

echo "  Testing scheduler function..."
SCHEDULER_RESPONSE=$(supabase functions invoke scheduler --method POST --body '{"action": "init"}')
echo "  Scheduler response: $SCHEDULER_RESPONSE"

echo "  Testing fetch-candles function..."
FETCH_RESPONSE=$(supabase functions invoke fetch-candles --method POST --body '{"timeframe": 30}')
echo "  Fetch response: $FETCH_RESPONSE"

echo "  Testing fetch-historical-candles function..."
HISTORICAL_RESPONSE=$(supabase functions invoke fetch-historical-candles --method POST --body '{"timeframe": 30, "days_back": 2}')
echo "  Historical response: $HISTORICAL_RESPONSE"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Set environment variables in Supabase dashboard"
echo "2. Enable pg_cron extension in your database"
echo "3. Run the setup function to create cron job"
echo ""
echo "📋 Manual setup commands:"
echo "   -- Enable pg_cron (run in SQL editor):"
echo "   CREATE EXTENSION IF NOT EXISTS pg_cron;"
echo ""
echo "   -- Setup automated scheduler (run in SQL editor):"
echo "   SELECT cron.schedule("
echo "     'candle-scheduler-every-5min',"
echo "     '*/5 * * * *',"
echo "     \$\$SELECT net.http_post("
echo "       url := '${SUPABASE_URL}/functions/v1/scheduler',"
echo "       headers := '{\"Content-Type\": \"application/json\", \"Authorization\": \"Bearer <YOUR_ANON_KEY>\"}'::jsonb,"
echo "       body := '{\"action\": \"auto\"}'::jsonb"
echo "     );\$\$"
echo "   );"
echo ""
echo "   -- Initial data load (run once after setup):"
echo "   SELECT net.http_post("
echo "     url := '${SUPABASE_URL}/functions/v1/scheduler',"
echo "     headers := '{\"Content-Type\": \"application/json\", \"Authorization\": \"Bearer <YOUR_ANON_KEY>\"}'::jsonb,"
echo "     body := '{\"action\": \"init\"}'::jsonb"
echo "   );"
echo ""
echo "🔍 Monitor functions:"
echo "   supabase functions logs scheduler --follow"
echo "   supabase functions logs fetch-candles --follow"
echo "   supabase functions logs fetch-historical-candles --follow"
echo ""
echo "🌐 Function URLs:"
echo "   Scheduler: ${SUPABASE_URL}/functions/v1/scheduler"
echo "   Fetch Candles: ${SUPABASE_URL}/functions/v1/fetch-candles"
echo "   Fetch Historical: ${SUPABASE_URL}/functions/v1/fetch-historical-candles"
