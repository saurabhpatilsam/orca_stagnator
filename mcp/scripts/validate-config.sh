#!/bin/bash

# 🔍 MCP Configuration Validator
# Validates MCP configuration and checks token accessibility

set -e

echo "🔍 MCP Configuration Validator"
echo "============================="

WINDSURF_CONFIG_FILE="/Users/stagnator/.codeium/windsurf/mcp_config.json"
MCP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$MCP_DIR/keys/.env"

# Check if config file exists
if [ ! -f "$WINDSURF_CONFIG_FILE" ]; then
    echo "❌ MCP config file not found: $WINDSURF_CONFIG_FILE"
    echo "💡 Run setup.sh first"
    exit 1
fi

echo "✅ Config file found: $WINDSURF_CONFIG_FILE"

# Validate JSON syntax
echo "🔍 Validating JSON syntax..."
if jq empty "$WINDSURF_CONFIG_FILE" 2>/dev/null; then
    echo "✅ JSON syntax is valid"
else
    echo "❌ Invalid JSON syntax in config file"
    exit 1
fi

# Load environment if available
if [ -f "$ENV_FILE" ]; then
    echo "🔄 Loading environment variables..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Check MCP servers in config
echo "🔍 Checking configured MCP servers..."
servers=$(jq -r '.mcpServers | keys[]' "$WINDSURF_CONFIG_FILE")

for server in $servers; do
    echo "  📡 $server"
    
    # Check if server has required fields
    server_config=$(jq ".mcpServers.\"$server\"" "$WINDSURF_CONFIG_FILE")
    
    if echo "$server_config" | jq -e '.serverUrl' >/dev/null 2>&1; then
        url=$(echo "$server_config" | jq -r '.serverUrl')
        echo "    🌐 URL: $url"
        
        # Check if URL contains token placeholder
        if [[ "$url" == *'${GITHUB_TOKEN}'* ]] || [[ "$url" == *'${VERCEL_TOKEN}'* ]]; then
            echo "    ⚠️  URL contains unresolved token placeholder"
        fi
    fi
    
    if echo "$server_config" | jq -e '.command' >/dev/null 2>&1; then
        command=$(echo "$server_config" | jq -r '.command')
        echo "    🔧 Command: $command"
    fi
done

echo ""
echo "🎯 Validation Summary:"
echo "✅ Configuration file exists and is valid JSON"
echo "✅ Found $(echo "$servers" | wc -l | tr -d ' ') MCP server(s)"
echo ""
echo "💡 To test the configuration:"
echo "1. Restart Windsurf (Cmd+Q, then reopen)"
echo "2. Start a new chat session"
echo "3. Try MCP commands"
