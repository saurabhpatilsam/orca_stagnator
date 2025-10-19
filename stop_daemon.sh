#!/bin/bash
# Stop the candle daemon

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

if [ ! -f "daemon.pid" ]; then
    echo "❌ No PID file found. Daemon may not be running."
    exit 1
fi

PID=$(cat daemon.pid)

if ! ps -p $PID > /dev/null 2>&1; then
    echo "❌ Daemon is not running (stale PID: $PID)"
    rm daemon.pid
    exit 1
fi

echo "🛑 Stopping daemon (PID: $PID)..."
kill -TERM $PID

# Wait for graceful shutdown
sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Daemon still running, force killing..."
    kill -9 $PID
    sleep 1
fi

if ! ps -p $PID > /dev/null 2>&1; then
    rm daemon.pid
    echo "✅ Daemon stopped successfully"
else
    echo "❌ Failed to stop daemon"
    exit 1
fi
