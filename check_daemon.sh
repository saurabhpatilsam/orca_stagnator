#!/bin/bash
# Check daemon status

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "================================"
echo "NQ Candle Daemon Status"
echo "================================"

if [ ! -f "daemon.pid" ]; then
    echo "Status: ❌ NOT RUNNING (no PID file)"
    exit 0
fi

PID=$(cat daemon.pid)

if ps -p $PID > /dev/null 2>&1; then
    echo "Status: ✅ RUNNING"
    echo "PID: $PID"
    echo ""
    
    # Show uptime
    START_TIME=$(ps -p $PID -o lstart=)
    echo "Started: $START_TIME"
    
    # Show memory usage
    MEM=$(ps -p $PID -o rss= | awk '{print $1/1024 " MB"}')
    echo "Memory: $MEM"
    
    # Show CPU usage
    CPU=$(ps -p $PID -o %cpu=)
    echo "CPU: ${CPU}%"
    
    echo ""
    echo "Recent logs:"
    echo "================================"
    tail -20 logs/candle_daemon_$(date +%Y-%m-%d).log 2>/dev/null || echo "No logs found for today"
else
    echo "Status: ❌ NOT RUNNING (stale PID: $PID)"
    rm daemon.pid
fi

echo "================================"
