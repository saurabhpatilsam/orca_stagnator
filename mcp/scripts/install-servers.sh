#!/bin/bash

# 📦 MCP Servers Installation Script
# Installs required MCP server packages

set -e

echo "📦 MCP Servers Installation"
echo "=========================="

echo "🔍 Checking Node.js and npm..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js first."
    echo "💡 Visit: https://nodejs.org/"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm first."
    exit 1
fi

echo "✅ Node.js $(node --version)"
echo "✅ npm $(npm --version)"
echo ""

echo "📦 Installing MCP server packages..."

# Supabase MCP Server
echo "🔄 Installing Supabase MCP Server..."
if npm list -g @supabase/mcp-server-supabase &> /dev/null; then
    echo "✅ @supabase/mcp-server-supabase already installed"
else
    echo "📥 Installing @supabase/mcp-server-supabase..."
    npm install -g @supabase/mcp-server-supabase@latest
    echo "✅ Supabase MCP Server installed"
fi

# Railway MCP Server
echo "🔄 Installing Railway MCP Server..."
if npm list -g @railway/mcp-server &> /dev/null; then
    echo "✅ @railway/mcp-server already installed"
else
    echo "📥 Installing @railway/mcp-server..."
    npm install -g @railway/mcp-server
    echo "✅ Railway MCP Server installed"
fi

# Composio MCP (for MCPify servers)
echo "🔄 Installing Composio MCP..."
if npm list -g @composio/mcp &> /dev/null; then
    echo "✅ @composio/mcp already installed"
else
    echo "📥 Installing @composio/mcp..."
    npm install -g @composio/mcp@latest
    echo "✅ Composio MCP installed"
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 Installed packages:"
echo "  ✅ @supabase/mcp-server-supabase"
echo "  ✅ @railway/mcp-server"
echo "  ✅ @composio/mcp"
echo ""
echo "💡 Next steps:"
echo "1. Run setup.sh to configure MCP servers"
echo "2. Add your API tokens to the environment file"
echo "3. Restart Windsurf"
