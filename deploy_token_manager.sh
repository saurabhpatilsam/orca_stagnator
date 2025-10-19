#!/bin/bash

# 🚀 DEPLOY SUPABASE TOKEN MANAGER
# ================================
# This script deploys the token manager Edge Function and sets up the database

echo "🚀 DEPLOYING SUPABASE TOKEN MANAGER"
echo "===================================="

# Check if supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Installing..."
    npm install -g supabase
fi

echo "✅ Supabase CLI found: $(supabase --version)"

# Check if we're in a Supabase project
if [ ! -f "supabase/config.toml" ]; then
    echo "❌ Not in a Supabase project directory"
    echo "Please run this script from the root of your project"
    exit 1
fi

echo "✅ Found Supabase project configuration"

# Start Supabase (if not already running)
echo "🔌 Starting Supabase services..."
supabase start

# Apply database migrations
echo "📊 Applying database migrations..."
supabase db reset

# Deploy the Edge Function
echo "🔧 Deploying token-manager Edge Function..."
supabase functions deploy token-manager

# Check deployment status
if [ $? -eq 0 ]; then
    echo "✅ Edge Function deployed successfully!"
    
    # Get the function URL
    FUNCTION_URL=$(supabase status | grep "Functions URL" | awk '{print $3}')
    if [ -n "$FUNCTION_URL" ]; then
        echo ""
        echo "🔗 EDGE FUNCTION ENDPOINTS:"
        echo "================================"
        echo "Base URL: ${FUNCTION_URL}/token-manager"
        echo ""
        echo "Available endpoints:"
        echo "  • Sync tokens:    GET ${FUNCTION_URL}/token-manager?action=sync"
        echo "  • Get status:     GET ${FUNCTION_URL}/token-manager?action=status"
        echo "  • Get token:      GET ${FUNCTION_URL}/token-manager?action=get&account=APEX_136189"
        echo "  • Cleanup:        GET ${FUNCTION_URL}/token-manager?action=cleanup"
        echo ""
    fi
    
    # Test the function
    echo "🧪 Testing Edge Function..."
    echo "Testing status endpoint..."
    
    if [ -n "$FUNCTION_URL" ]; then
        curl -s "${FUNCTION_URL}/token-manager?action=status" | jq '.' || echo "Response received (jq not available for formatting)"
    fi
    
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo "======================="
    echo ""
    echo "Next steps:"
    echo "1. Update your Supabase URL and API key in sync_tokens_to_supabase.py"
    echo "2. Run: python3 sync_tokens_to_supabase.py sync"
    echo "3. Check status: python3 sync_tokens_to_supabase.py status"
    
else
    echo "❌ Edge Function deployment failed"
    echo "Please check the error messages above"
    exit 1
fi
