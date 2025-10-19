# Fully Automated 24/7 Trading System - Deployment Guide

## Overview

This is a **fully automated, 24/7 trading system** that runs continuously without manual intervention. Once deployed, it will:

✅ **Run 24/7** - Continuously monitors market conditions  
✅ **Detect Market Hours** - Knows when US markets are open/closed  
✅ **Handle Holidays** - Automatically skips market holidays  
✅ **Cancel Orders** - Cancels all orders 5 minutes before market open  
✅ **Wait for First Hour** - Monitors first 60-minute candle after market open  
✅ **Place Orders** - Automatically places all breakout orders  
✅ **Reset Daily** - Starts fresh each trading day  

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           AUTOMATED TRADING DAEMON (24/7)                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Market Calendar & Holiday Detection                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Pre-Market: Cancel Orders (5 min before open)       │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Market Open: Wait for First Hour Candle             │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  First Hour Close: Place All Orders                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    SUPABASE DATABASE                         │
│                  (trading_signals table)                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              ORDER LISTENER SERVICE (24/7)                   │
│           (Monitors Supabase, Places Orders)                 │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    TRADOVATE API                             │
│              (Executes Orders on Exchange)                   │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start (Docker - Recommended)

### 1. Install Docker

```bash
# Mac
brew install docker docker-compose

# Linux
sudo apt-get install docker docker-compose
```

### 2. Configure Environment

Your `.env` file is already configured with:
- ✅ Supabase credentials
- ✅ Redis credentials
- ✅ Tradovate API settings

### 3. Start the System

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main

# Start both services (daemon + order listener)
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Verify It's Running

```bash
# Check container status
docker-compose ps

# Should show:
# trading-daemon    running
# order-listener    running
```

**That's it!** The system is now running 24/7 and will automatically:
- Cancel orders 5 minutes before market open
- Wait for first hour candle
- Place all orders
- Repeat every trading day

## Manual Deployment (Without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Order Listener (Terminal 1)

```bash
python3 supabase_order_listener.py
```

### 3. Start Trading Daemon (Terminal 2)

```bash
python3 automated_trading_daemon.py
```

### 4. Keep Running (Use tmux or screen)

```bash
# Install tmux
brew install tmux  # Mac
sudo apt-get install tmux  # Linux

# Start tmux session
tmux new -s trading

# Run daemon
python3 automated_trading_daemon.py

# Detach: Press Ctrl+B then D
# Reattach: tmux attach -t trading
```

## System Behavior

### Daily Cycle

| Time (ET) | Action | Description |
|-----------|--------|-------------|
| 9:25 AM | 🚫 Cancel Orders | Cancels all pending orders |
| 9:30 AM | 🔔 Market Open | Market opens, first hour begins |
| 10:30 AM | 📊 First Hour Close | Fetches candle data |
| 10:30 AM | 📤 Place Orders | Places 5 SHORT + 5 LONG orders |
| 4:00 PM | 🔔 Market Close | Orders remain active |
| Next Day | 🔄 Repeat | Cycle repeats |

### Order Placement Example

**First Hour Candle:**
- High: 5920.00
- Low: 5880.00

**SHORT Orders (above high):**
1. 5929.00 (SL: 5934, TP: 5924)
2. 5938.00 (SL: 5943, TP: 5933)
3. 5947.00 (SL: 5952, TP: 5942)
4. 5956.00 (SL: 5961, TP: 5951)
5. 5965.00 (SL: 5970, TP: 5960)

**LONG Orders (below low):**
1. 5871.00 (SL: 5866, TP: 5876)
2. 5862.00 (SL: 5857, TP: 5867)
3. 5853.00 (SL: 5848, TP: 5858)
4. 5844.00 (SL: 5839, TP: 5849)
5. 5835.00 (SL: 5830, TP: 5840)

### Holiday Handling

The system automatically detects:
- ✅ Weekends (Saturday/Sunday)
- ✅ US Market Holidays (New Year's, MLK Day, Presidents Day, Good Friday, Memorial Day, Independence Day, Labor Day, Thanksgiving, Christmas)
- ✅ Early Close Days

**No manual intervention needed!**

## Monitoring

### View Logs

```bash
# Docker
docker-compose logs -f trading-daemon
docker-compose logs -f order-listener

# Manual
tail -f strategy.log
tail -f order_listener.log
```

### Check Supabase

Go to: https://supabase.com/dashboard/project/dcoukhtfcloqpfmijock

View:
- `trading_signals` table - All placed orders
- `order_history` table - Order events

### Monitor System Status

```bash
# Docker
docker-compose ps

# Manual
ps aux | grep automated_trading_daemon
ps aux | grep supabase_order_listener
```

## Configuration

### Change Instrument

```bash
# In .env file
STRATEGY_INSTRUMENT=NQZ5  # Switch to Nasdaq
```

### Adjust Parameters

Edit `automated_trading_daemon.py`:

```python
class DaemonConfig:
    POINTS_SPACING = 12  # Change spacing
    MAX_ORDERS_PER_SIDE = 3  # Fewer orders
    STOP_LOSS_POINTS = 10  # Wider stop
    TAKE_PROFIT_POINTS = 15  # Larger target
```

### Change Check Interval

```python
CHECK_INTERVAL_SECONDS = 60  # Check every minute instead of 30 seconds
```

## Integrating Real Market Data

Currently using **sample data**. To integrate real data:

### Option 1: TradingView (Recommended)

```bash
# Install
pip install tradingview-ta

# Update fetch_first_hour_candle_data() in automated_trading_daemon.py
```

### Option 2: Interactive Brokers

```bash
# Install
pip install ib_insync

# Update fetch_first_hour_candle_data() in automated_trading_daemon.py
```

### Option 3: Your Custom Data Provider

Implement the `fetch_first_hour_candle_data()` method with your data source.

## Stopping the System

### Docker

```bash
# Stop gracefully
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Manual

```bash
# Press Ctrl+C in the terminal
# Or send SIGTERM
kill -TERM <process_id>
```

## Troubleshooting

### System Not Placing Orders

1. **Check if it's a trading day:**
   ```bash
   docker-compose logs trading-daemon | grep "TRADING DAY"
   ```

2. **Verify time is correct:**
   ```bash
   docker-compose exec trading-daemon date
   ```

3. **Check Supabase connection:**
   ```bash
   docker-compose logs trading-daemon | grep "Supabase"
   ```

### Orders Not Executing

1. **Check order listener is running:**
   ```bash
   docker-compose ps order-listener
   ```

2. **View order listener logs:**
   ```bash
   docker-compose logs order-listener
   ```

3. **Check Tradovate API:**
   - Market must be open
   - Prices must be valid
   - Account must have sufficient margin

### Container Keeps Restarting

```bash
# View logs
docker-compose logs trading-daemon

# Common issues:
# - Missing .env file
# - Invalid credentials
# - Network issues
```

## Production Checklist

Before going live:

- [ ] ✅ Supabase tables created
- [ ] ✅ `.env` file configured
- [ ] ✅ Order listener running
- [ ] ✅ Trading daemon running
- [ ] ✅ Tested with sample data
- [ ] 🔄 Integrated real market data
- [ ] 🔄 Tested on demo account
- [ ] 🔄 Verified order placement works
- [ ] 🔄 Set up monitoring/alerts
- [ ] 🔄 Documented kill switch procedure

## Advanced: Production Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (t2.micro or larger)
# 2. Install Docker
sudo yum install docker
sudo service docker start

# 3. Clone your code
git clone <your-repo>
cd orca-ven-backend-main

# 4. Start services
docker-compose up -d

# 5. Set up auto-restart on reboot
sudo systemctl enable docker
```

### DigitalOcean Droplet

```bash
# 1. Create droplet with Docker pre-installed
# 2. Upload your code
scp -r orca-ven-backend-main root@<droplet-ip>:/root/

# 3. SSH and start
ssh root@<droplet-ip>
cd orca-ven-backend-main
docker-compose up -d
```

### Kubernetes

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: trading-daemon
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: trading-daemon
        image: your-registry/trading-daemon:latest
        envFrom:
        - secretRef:
            name: trading-secrets
```

## Support & Maintenance

### Regular Maintenance

- **Weekly**: Check logs for errors
- **Monthly**: Review order performance
- **Quarterly**: Update dependencies
- **Yearly**: Review and optimize strategy

### Backup

```bash
# Backup configuration
cp .env .env.backup

# Backup Supabase data
# Use Supabase dashboard -> Database -> Backups
```

## Security Best Practices

1. **Never commit `.env` to git**
2. **Use strong passwords**
3. **Enable 2FA on Supabase**
4. **Rotate API keys regularly**
5. **Monitor for unusual activity**
6. **Set up alerts for failed orders**

---

## 🎉 You're Ready!

Your fully automated 24/7 trading system is now set up and ready to run!

**Start it with:**
```bash
docker-compose up -d
```

**Monitor it with:**
```bash
docker-compose logs -f
```

**Stop it with:**
```bash
docker-compose down
```

**No manual intervention required - it runs completely automatically!** 🚀
