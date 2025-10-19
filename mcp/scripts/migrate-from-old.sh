#!/bin/bash

# 🔄 Migration Script: Old MCP Setup → New Organized Structure
# Migrates from the old mcp_config_complete.json to the new organized structure

set -e

echo "🔄 MCP Migration Script"
echo "======================"

MCP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OLD_CONFIG="../mcp_config_complete.json"
OLD_SETUP_SCRIPT="../setup_mcp_config.sh"
WINDSURF_CONFIG_FILE="/Users/stagnator/.codeium/windsurf/mcp_config.json"

echo "📁 MCP Directory: $MCP_DIR"
echo ""

# Check if old files exist
if [ -f "$OLD_CONFIG" ]; then
    echo "✅ Found old config: $OLD_CONFIG"
else
    echo "❌ Old config not found: $OLD_CONFIG"
    echo "💡 Nothing to migrate"
    exit 0
fi

# Backup old files
echo "💾 Creating backups..."
if [ -f "$OLD_CONFIG" ]; then
    cp "$OLD_CONFIG" "$OLD_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   📄 Backed up: $OLD_CONFIG"
fi

if [ -f "$OLD_SETUP_SCRIPT" ]; then
    cp "$OLD_SETUP_SCRIPT" "$OLD_SETUP_SCRIPT.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   📄 Backed up: $OLD_SETUP_SCRIPT"
fi

# Extract tokens from old config
echo "🔍 Extracting tokens from old configuration..."

if command -v jq &> /dev/null; then
    # Use jq if available
    GITHUB_TOKEN=$(jq -r '.mcpServers.github.headers.Authorization' "$OLD_CONFIG" | sed 's/Bearer //')
    VERCEL_TOKEN=$(jq -r '.mcpServers.vercel.headers.Authorization' "$OLD_CONFIG" | sed 's/Bearer //')
    SUPABASE_TOKEN=$(jq -r '.mcpServers."supabase-mcp-server".args[3]' "$OLD_CONFIG")
else
    # Fallback to grep/sed
    GITHUB_TOKEN=$(grep -A 3 '"github"' "$OLD_CONFIG" | grep 'Bearer' | sed 's/.*Bearer //' | sed 's/"//' | tr -d ' ')
    VERCEL_TOKEN=$(grep -A 3 '"vercel"' "$OLD_CONFIG" | grep 'Bearer' | sed 's/.*Bearer //' | sed 's/"//' | tr -d ' ')
    SUPABASE_TOKEN=$(grep -A 10 '"supabase-mcp-server"' "$OLD_CONFIG" | grep -A 1 '"--access-token"' | tail -1 | sed 's/.*"//' | sed 's/".*//')
fi

echo "   🔑 GitHub token: ${GITHUB_TOKEN:0:10}..."
echo "   🔑 Vercel token: ${VERCEL_TOKEN:0:10}..."
echo "   🔑 Supabase token: ${SUPABASE_TOKEN:0:20}..."

# Create new environment file
ENV_FILE="$MCP_DIR/keys/.env"
echo "📝 Creating new environment file: $ENV_FILE"

cat > "$ENV_FILE" << EOF
# 🔑 MCP API Keys and Tokens
# Migrated from old mcp_config_complete.json on $(date)

# GitHub Token
GITHUB_TOKEN=$GITHUB_TOKEN

# Vercel Token  
VERCEL_TOKEN=$VERCEL_TOKEN

# Supabase Access Token
SUPABASE_TOKEN=$SUPABASE_TOKEN

# Railway Token (optional - Railway MCP uses CLI authentication by default)
RAILWAY_TOKEN=

# Supabase Project Details (add if needed)
SUPABASE_URL=https://supabase.magicpitch.ai
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
EOF

echo "✅ Environment file created"

# Run the new setup
echo "🚀 Running new setup process..."
cd "$MCP_DIR/scripts"
./setup.sh

echo ""
echo "🎉 Migration Complete!"
echo ""
echo "📋 What was migrated:"
echo "   ✅ API tokens extracted and secured"
echo "   ✅ New modular configuration structure"
echo "   ✅ Organized directory layout"
echo "   ✅ Setup scripts and documentation"
echo ""
echo "📁 Old files backed up with timestamp"
echo "🔧 New structure ready to use"
echo ""
echo "💡 Next steps:"
echo "1. 🔄 Restart Windsurf (Cmd+Q, then reopen)"
echo "2. 💬 Start a new chat session"
echo "3. 🧪 Test MCP commands"
echo ""
echo "📚 Documentation available in: $MCP_DIR/docs/"
