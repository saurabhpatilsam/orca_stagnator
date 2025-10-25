# Edge Functions Automation Guide

## 🔍 Problem Identified

**Issue**: Edge functions fail with "No Tradovate TV token found in Redis"

**Root Cause**: Tradovate tokens expire after 1 hour (TTL: 3600 seconds) and need to be refreshed regularly.

## ✅ Solution Implemented

### 1. Automatic Token Refresh
- **Script**: `scripts/auto_refresh_tokens.sh`
- **Frequency**: Every 50 minutes (before 1-hour expiry)
- **Purpose**: Automatically refreshes tokens in Redis to prevent edge function failures

### 2. Health Monitoring
- **Script**: `scripts/health_check.sh`
- **Purpose**: Tests all edge functions and reports their status
- **Usage**: Run manually or set up as a monitoring cron job

### 3. Setup Automation
- **Script**: `scripts/setup_token_automation.sh`
- **Purpose**: One-time setup to enable automatic token refresh via cron

## 🚀 Quick Start

### Enable Automatic Token Refresh

```bash
# Run this once to set up automation
bash scripts/setup_token_automation.sh
```

This will:
- Make all scripts executable
- Add a cron job to refresh tokens every 50 minutes
- Create a logs directory for tracking

### Verify Setup

```bash
# Check if cron job is running
crontab -l | grep auto_refresh_tokens

# Run health check
bash scripts/health_check.sh
```

### Manual Token Refresh

If you need to refresh tokens manually:

```bash
# Option 1: Run the automated script
bash scripts/auto_refresh_tokens.sh

# Option 2: Run the Python script directly
python3 token_generator_and_redis_manager.py
```

## 📊 Monitoring & Logs

### Log Locations

All logs are stored in the `logs/` directory:

- **Token Refresh Logs**: `logs/token_refresh_YYYYMMDD.log`
- **Health Check Logs**: `logs/health_check_YYYYMMDD.log`

### View Recent Logs

```bash
# View today's token refresh log
tail -f logs/token_refresh_$(date +%Y%m%d).log

# View latest health check
cat logs/health_check_$(date +%Y%m%d).log
```

### Log Retention

- Logs older than 7 days are automatically deleted
- Each script run creates timestamped entries

## 🧪 Testing

### Test Individual Edge Functions

```bash
# Test 5-minute candles
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5}'

# Test scheduler
curl -X POST https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/scheduler \
  -H "Authorization: Bearer YOUR_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Run Comprehensive Health Check

```bash
bash scripts/health_check.sh
```

Expected output:
```
🏥 Edge Functions Health Check
==========================================
✅ 5min candles: WORKING
✅ 15min candles: WORKING
✅ 30min candles: WORKING
✅ 60min candles: WORKING
✅ Scheduler: WORKING

📊 Health Check Summary
==========================================
Passed: 5
Failed: 0

✅ All edge functions are healthy!
```

## 🔧 Troubleshooting

### Edge Functions Still Failing

1. **Check if cron job is running**:
   ```bash
   crontab -l
   ```

2. **Manually refresh tokens**:
   ```bash
   bash scripts/auto_refresh_tokens.sh
   ```

3. **Check logs for errors**:
   ```bash
   tail -20 logs/token_refresh_$(date +%Y%m%d).log
   ```

4. **Verify Redis connection**:
   ```bash
   python3 token_generator_and_redis_manager.py
   ```

### Cron Job Not Running

Check system logs:
```bash
# macOS
log show --predicate 'eventMessage contains "cron"' --last 1h

# Linux
grep CRON /var/log/syslog
```

### Disable Automation

To remove the automatic token refresh:
```bash
crontab -e
# Delete the line containing auto_refresh_tokens.sh
```

## 📋 Current Configuration

### Edge Functions
- **Project**: dcoukhtfcloqpfmijock
- **URL**: https://dcoukhtfcloqpfmijock.supabase.co
- **Functions**:
  - `fetch-candles` - Real-time candle fetching
  - `fetch-historical-candles` - Historical data backfill
  - `scheduler` - Automated scheduling

### Token Configuration
- **Redis Host**: redismanager.redis.cache.windows.net:6380
- **Accounts**: APEX_266668, APEX_272045, APEX_136189, APEX_265995
- **Token TTL**: 3600 seconds (1 hour)
- **Refresh Interval**: 50 minutes

### Timeframes Supported
- ✅ 5 minutes
- ✅ 15 minutes
- ✅ 30 minutes
- ✅ 60 minutes (1 hour)
- ⏸️  1 minute (tables/RPCs not created)
- ⏸️  10 minutes (tables/RPCs not created)

## 🎯 Best Practices

1. **Regular Health Checks**: Run `bash scripts/health_check.sh` daily
2. **Monitor Logs**: Check logs weekly for any recurring issues
3. **Token Alerts**: Set up alerts if token refresh fails
4. **Backup Credentials**: Keep credentials.json backed up securely

## 🔐 Security Notes

- Service role keys are in scripts but should be in environment variables
- Credentials are stored in `.env.configured` (gitignored)
- Redis password is secured with TLS
- Tokens auto-expire after 1 hour

## 📞 Support

If edge functions continue to fail after automation:
1. Check logs in `logs/` directory
2. Run health check: `bash scripts/health_check.sh`
3. Manually refresh: `bash scripts/auto_refresh_tokens.sh`
4. Verify cron job: `crontab -l`

---

**Last Updated**: October 22, 2025
**Status**: ✅ Automation Active
