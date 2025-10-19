#!/bin/bash

# 🔧 MCP Configuration Setup Script
# This script helps you set up all MCP servers for Windsurf

echo "🚀 MCP Configuration Setup for Windsurf"
echo "========================================"

# Configuration file paths
MCP_CONFIG_DIR="/Users/stagnator/.codeium/windsurf"
MCP_CONFIG_FILE="$MCP_CONFIG_DIR/mcp_config.json"
TEMPLATE_FILE="./mcp_config_complete.json"

# Create directory if it doesn't exist
echo "📁 Creating MCP config directory..."
mkdir -p "$MCP_CONFIG_DIR"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "❌ Template file not found: $TEMPLATE_FILE"
    echo "Please run this script from the project root directory."
    exit 1
fi

echo "📋 Current MCP configuration template includes:"
echo "   ✅ GitHub MCP Server"
echo "   ✅ Vercel MCP Server" 
echo "   ✅ Supabase MCP Server"
echo "   ✅ MCPify Ninja Trader Python Bridge"
echo "   ✅ MCPify Google Places SERP Tools"
echo ""

# Backup existing config if it exists
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo "💾 Backing up existing config..."
    cp "$MCP_CONFIG_FILE" "$MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   Backup saved to: $MCP_CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

echo "🔑 You need to get the following API tokens:"
echo ""
echo "1. GitHub Token:"
echo "   → Go to: https://github.com/settings/tokens"
echo "   → Generate new token (classic)"
echo "   → Select 'repo' scope"
echo ""
echo "2. Vercel Token:"
echo "   → Go to: https://vercel.com/account/tokens"
echo "   → Create new token"
echo "   → Full Account scope"
echo ""
echo "3. Supabase Token:"
echo "   → Go to: https://supabase.com/dashboard/account/tokens"
echo "   → Generate new token"
echo ""

read -p "Do you want to copy the template to the MCP config location? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cp "$TEMPLATE_FILE" "$MCP_CONFIG_FILE"
    echo "✅ Template copied to: $MCP_CONFIG_FILE"
    echo ""
    echo "📝 Next steps:"
    echo "1. Edit the config file and replace the placeholder tokens:"
    echo "   nano $MCP_CONFIG_FILE"
    echo ""
    echo "2. Replace these placeholders with your actual tokens:"
    echo "   - YOUR_GITHUB_TOKEN_HERE"
    echo "   - YOUR_VERCEL_TOKEN_HERE" 
    echo "   - YOUR_SUPABASE_TOKEN_HERE"
    echo ""
    echo "3. Save the file and restart Windsurf (Cmd+Q, then reopen)"
    echo ""
    echo "4. Start a new chat session to test the MCP servers"
    echo ""
    echo "🎉 After setup, you'll be able to:"
    echo "   • Deploy to Vercel automatically"
    echo "   • Push code to GitHub"
    echo "   • Query Supabase databases"
    echo "   • Use Ninja Trader Python Bridge"
    echo "   • Access Google Places SERP tools"
else
    echo "❌ Setup cancelled. Template is available at: $TEMPLATE_FILE"
fi

echo ""
echo "📚 For detailed instructions, see:"
echo "   • docs/guides/MCP_SETUP_GUIDE.md"
echo "   • docs/guides/MCP_QUICK_SETUP.md"
