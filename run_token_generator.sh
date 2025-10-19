#!/bin/bash

# 🔐 ORCA TOKEN GENERATOR RUNNER SCRIPT
# =====================================
# This script runs the token generator with proper environment setup

echo "🔐 ORCA TOKEN GENERATOR & REDIS MANAGER"
echo "======================================="

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if credentials file exists
CREDS_FILE="tradovate-market-stream-main/credentials.json"
if [ ! -f "$CREDS_FILE" ]; then
    echo "❌ Error: Credentials file not found at $CREDS_FILE"
    echo "Please ensure the credentials.json file exists with your Tradovate accounts."
    exit 1
fi

echo "✅ Found credentials file: $CREDS_FILE"

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install required packages if needed
echo "📦 Installing required packages..."
pip3 install -q redis loguru requests python-dotenv httpx

# Run the token generator
echo "🚀 Starting token generation..."
echo ""

python3 token_generator_and_redis_manager.py

echo ""
echo "🏁 Token generation script completed."
echo "Check the logs/ directory for detailed logs."
