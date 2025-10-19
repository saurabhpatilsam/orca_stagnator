# 🚀 Continuous Candle Data Daemon Setup

## Overview
This daemon continuously fetches and stores NQ candle data from Tradovate to Supabase every few minutes, running 24/7 without intervention.

## Features
- ✅ Automatic fetching every 5/15/30/60 minutes
- ✅ Auto-reconnect on failures
- ✅ Graceful shutdown handling
- ✅ Rotating log files (30-day retention)
- ✅ Error recovery and retry logic
- ✅ Memory efficient

---

## 🎯 Quick Start

### 1. Start the Daemon
```bash
./start_daemon.sh
```

Expected output:
```
🚀 Starting NQ Candle Daemon...
✅ Daemon started with PID: 12345
📋 Logs: logs/candle_daemon_2025-10-16.log
```

### 2. Check Status
```bash
./check_daemon.sh
```

Output shows:
- Running status
- PID
- Uptime
- Memory/CPU usage
- Recent logs

### 3. Stop the Daemon
```bash
./stop_daemon.sh
```

---

## 📊 What Gets Fetched

| Timeframe | Fetch Interval | Bars per Fetch |
|-----------|----------------|----------------|
| 5-minute  | Every 5 min    | 5 bars         |
| 15-minute | Every 15 min   | 5 bars         |
| 30-minute | Every 30 min   | 5 bars         |
| 1-hour    | Every 60 min   | 5 bars         |

---

## 📋 Log Files

Logs are stored in the `logs/` directory:

- **`logs/candle_daemon_YYYY-MM-DD.log`** - Daily rotating logs (kept for 30 days)
- **`logs/daemon_stdout.log`** - Process stdout/stderr

### View Logs:
```bash
# Today's logs
tail -f logs/candle_daemon_$(date +%Y-%m-%d).log

# Last 100 lines
tail -100 logs/candle_daemon_$(date +%Y-%m-%d).log

# Search for errors
grep ERROR logs/candle_daemon_*.log

# Watch live
tail -f logs/daemon_stdout.log
```

---

## 🔧 Advanced Options

### Run in Foreground (for debugging)
```bash
python3 candle_daemon.py
```
Press `Ctrl+C` to stop.

### Custom Configuration

Edit `candle_daemon.py` to customize:
```python
# Number of bars to fetch each time
num_bars=5  # Change this value

# Fetch intervals (in minutes)
TIMEFRAMES = {
    5: {"interval_minutes": 5, ...},   # 5-min candles every 5 mins
    15: {"interval_minutes": 15, ...}, # 15-min candles every 15 mins
    ...
}
```

---

## 🌐 Option 2: Deploy to Railway (Cloud)

For 24/7 uptime without managing a server:

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login
```bash
railway login
```

### 3. Initialize Project
```bash
railway init
```

### 4. Add Environment Variables
```bash
railway variables set SUPABASE_URL="https://your-project.supabase.co"
railway variables set SUPABASE_ANON_KEY="your-anon-key"
```

### 5. Create Procfile
```bash
echo "worker: python3 candle_daemon.py" > Procfile
```

### 6. Deploy
```bash
railway up
```

Your daemon will now run 24/7 on Railway's infrastructure!

**Costs**: Free tier includes $5/month credit (sufficient for this workload)

---

## 🐳 Option 3: Docker (Any Platform)

### Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run daemon
CMD ["python3", "candle_daemon.py"]
```

### Build and Run
```bash
# Build
docker build -t nq-candle-daemon .

# Run
docker run -d \
  --name nq-candles \
  --restart unless-stopped \
  -v $(pwd)/logs:/app/logs \
  -e SUPABASE_URL="https://your-project.supabase.co" \
  -e SUPABASE_ANON_KEY="your-key" \
  nq-candle-daemon

# Check logs
docker logs -f nq-candles

# Stop
docker stop nq-candles
```

---

## 🔄 Auto-Restart on System Reboot

### macOS (launchd)

Create: `~/Library/LaunchAgents/com.orca.candle-daemon.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.orca.candle-daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/path/to/candle_daemon.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/path/to/orca-ven-backend-main</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/path/to/logs/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/path/to/logs/daemon.err</string>
</dict>
</plist>
```

Load service:
```bash
launchctl load ~/Library/LaunchAgents/com.orca.candle-daemon.plist
launchctl start com.orca.candle-daemon
```

### Linux (systemd)

Create: `/etc/systemd/system/nq-candle-daemon.service`
```ini
[Unit]
Description=NQ Candle Data Daemon
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/orca-ven-backend-main
ExecStart=/usr/bin/python3 /path/to/candle_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable nq-candle-daemon
sudo systemctl start nq-candle-daemon
sudo systemctl status nq-candle-daemon
```

---

## 📈 Monitoring

### Check if Data is Being Updated
```sql
-- In Supabase SQL Editor
SELECT 
    '5min' as timeframe,
    MAX(candle_time) as latest_candle,
    COUNT(*) as total_candles
FROM orca.nq_candles_5min
UNION ALL
SELECT 
    '15min',
    MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_15min
UNION ALL
SELECT 
    '30min',
    MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_30min
UNION ALL
SELECT 
    '1hour',
    MAX(candle_time),
    COUNT(*)
FROM orca.nq_candles_1hour;
```

### Python Monitoring Script
```python
from supabase import create_client
import os
from datetime import datetime, timedelta

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Check if data is fresh (within last 10 minutes)
result = supabase.rpc("get_nq_candles", {
    "p_timeframe": "5min",
    "p_limit": 1
}).execute()

if result.data:
    latest = datetime.fromisoformat(result.data[0]['candle_time'])
    age = datetime.now(latest.tzinfo) - latest
    
    if age < timedelta(minutes=10):
        print(f"✅ Data is fresh! Latest: {latest}")
    else:
        print(f"⚠️  Data is stale! Latest: {latest} ({age} old)")
```

---

## 🆘 Troubleshooting

### Daemon Won't Start
```bash
# Check if Python is available
which python3

# Check dependencies
pip3 list | grep -E "supabase|loguru|websocket"

# Run in foreground to see errors
python3 candle_daemon.py
```

### No Data Being Stored
```bash
# Check logs for errors
tail -50 logs/candle_daemon_$(date +%Y-%m-%d).log

# Verify Supabase connection
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
s = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
print('✅ Supabase connected')
"
```

### High Memory Usage
```bash
# Check memory
./check_daemon.sh

# Restart if needed
./stop_daemon.sh
./start_daemon.sh
```

---

## 📝 Summary

**Local Daemon** (Option 1):
- ✅ Free
- ✅ Full control
- ❌ Requires server running 24/7

**Railway** (Option 2):
- ✅ Managed hosting
- ✅ Auto-scaling
- ✅ Free tier available
- ❌ Small cost after free tier

**Docker** (Option 3):
- ✅ Portable
- ✅ Isolated environment
- ✅ Easy deployment

Choose the option that best fits your infrastructure! 🚀
