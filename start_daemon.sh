#!/bin/bash
# Start the candle daemon

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Create logs directory
mkdir -p logs

# Check if already running
if [ -f "daemon.pid" ]; then
    PID=$(cat daemon.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Daemon is already running (PID: $PID)"
        exit 1
    else
        echo "⚠️  Stale PID file found, removing..."
        rm daemon.pid
    fi
fi

echo "🚀 Starting NQ Candle Daemon..."

# Start daemon in background
nohup python3 candle_daemon.py > logs/daemon_stdout.log 2>&1 &
PID=$!

# Save PID
echo $PID > daemon.pid

echo "✅ Daemon started with PID: $PID"
echo "📋 Logs: logs/candle_daemon_$(date +%Y-%m-%d).log"
echo "📋 stdout: logs/daemon_stdout.log"
echo ""
echo "To stop: ./stop_daemon.sh"
echo "To check status: ./check_daemon.sh"
