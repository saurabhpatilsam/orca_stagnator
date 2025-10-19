#!/bin/bash

# 🚀 MCP Configuration Setup Script
# Organized setup with separated keys and modular configurations

set -e

echo "🔧 MCP Configuration Setup"
echo "=========================="

# Configuration paths
MCP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WINDSURF_CONFIG_DIR="/Users/stagnator/.codeium/windsurf"
WINDSURF_CONFIG_FILE="$WINDSURF_CONFIG_DIR/mcp_config.json"
ENV_FILE="$MCP_DIR/keys/.env"
ENV_EXAMPLE="$MCP_DIR/keys/.env.example"

echo "📁 MCP Directory: $MCP_DIR"
echo "🎯 Windsurf Config: $WINDSURF_CONFIG_FILE"
echo ""

# Create Windsurf config directory
echo "📁 Creating Windsurf config directory..."
mkdir -p "$WINDSURF_CONFIG_DIR"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "⚠️  Environment file not found!"
    echo "📋 Copying template..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo ""
    echo "🔑 Please edit the environment file with your API tokens:"
    echo "   nano $ENV_FILE"
    echo ""
    echo "📚 Get your tokens from:"
    echo "   • GitHub: https://github.com/settings/tokens"
    echo "   • Vercel: https://vercel.com/account/tokens"
    echo "   • Supabase: https://supabase.com/dashboard/account/tokens"
    echo ""
    read -p "Press Enter after you've added your tokens to continue..."
fi

# Load environment variables
echo "🔄 Loading environment variables..."
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
    echo "✅ Environment loaded"
else
    echo "❌ Environment file not found: $ENV_FILE"
    exit 1
fi

# Validate required tokens
echo "🔍 Validating tokens..."
missing_tokens=()

if [ -z "$GITHUB_TOKEN" ] || [ "$GITHUB_TOKEN" = "your_github_token_here" ]; then
    missing_tokens+=("GITHUB_TOKEN")
fi

if [ -z "$VERCEL_TOKEN" ] || [ "$VERCEL_TOKEN" = "your_vercel_token_here" ]; then
    missing_tokens+=("VERCEL_TOKEN")
fi

if [ -z "$SUPABASE_TOKEN" ] || [ "$SUPABASE_TOKEN" = "your_supabase_token_here" ]; then
    missing_tokens+=("SUPABASE_TOKEN")
fi

if [ ${#missing_tokens[@]} -gt 0 ]; then
    echo "❌ Missing or placeholder tokens:"
    for token in "${missing_tokens[@]}"; do
        echo "   • $token"
    done
    echo ""
    echo "Please edit: $ENV_FILE"
    exit 1
fi

echo "✅ All required tokens found"

# Configuration selection
echo ""
echo "📋 Select MCP configuration:"
echo "1. Complete (All MCP servers)"
echo "2. Minimal (GitHub, Vercel, Supabase only)"
echo "3. Custom (Select individual servers)"

read -p "Choose option (1-3): " config_choice

case $config_choice in
    1)
        template_file="$MCP_DIR/configs/templates/complete-mcp-template.json"
        echo "📦 Using complete configuration"
        ;;
    2)
        template_file="$MCP_DIR/configs/templates/minimal-mcp-template.json"
        echo "📦 Using minimal configuration"
        ;;
    3)
        echo "🔧 Custom configuration not implemented yet"
        echo "📦 Using complete configuration as fallback"
        template_file="$MCP_DIR/configs/templates/complete-mcp-template.json"
        ;;
    *)
        echo "📦 Using complete configuration (default)"
        template_file="$MCP_DIR/configs/templates/complete-mcp-template.json"
        ;;
esac

# Backup existing config
if [ -f "$WINDSURF_CONFIG_FILE" ]; then
    backup_file="$WINDSURF_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing config to: $backup_file"
    cp "$WINDSURF_CONFIG_FILE" "$backup_file"
fi

# Process template and substitute environment variables
echo "🔄 Processing configuration template..."
envsubst < "$template_file" > "$WINDSURF_CONFIG_FILE"

echo "✅ Configuration applied to: $WINDSURF_CONFIG_FILE"
echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Next steps:"
echo "1. 🔄 Restart Windsurf (Cmd+Q, then reopen)"
echo "2. 💬 Start a new chat session"
echo "3. 🧪 Test with commands like:"
echo "   • 'Deploy my frontend to Vercel'"
echo "   • 'Push code to GitHub'"
echo "   • 'Query Supabase database'"
echo ""
echo "📚 For troubleshooting, see: $MCP_DIR/docs/"
