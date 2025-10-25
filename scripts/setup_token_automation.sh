#!/bin/bash
# Setup Token Automation - Adds cron job for automatic token refresh
# Run this once to set up automatic token refresh every 50 minutes

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REFRESH_SCRIPT="$SCRIPT_DIR/auto_refresh_tokens.sh"

echo "=========================================="
echo "🔧 Setting up automatic token refresh"
echo "=========================================="

# Make the refresh script executable
chmod +x "$REFRESH_SCRIPT"
echo "✅ Made refresh script executable"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "auto_refresh_tokens.sh"; then
    echo "⚠️  Cron job already exists. Removing old one..."
    crontab -l | grep -v "auto_refresh_tokens.sh" | crontab -
fi

# Add new cron job (every 50 minutes)
(crontab -l 2>/dev/null || true; echo "*/50 * * * * $REFRESH_SCRIPT") | crontab -

echo "✅ Added cron job to run every 50 minutes"
echo ""
echo "📋 Current crontab:"
crontab -l | grep "auto_refresh_tokens.sh"
echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "1. Tokens will now refresh automatically every 50 minutes"
echo "2. Check logs in: $PROJECT_DIR/logs/"
echo "3. To manually refresh tokens now, run: $REFRESH_SCRIPT"
echo "4. To remove automation, run: crontab -e and delete the auto_refresh_tokens.sh line"
echo ""
