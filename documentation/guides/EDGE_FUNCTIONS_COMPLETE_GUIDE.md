# 🚀 ORCA Supabase Edge Functions - Complete Setup Guide

## ✅ What Has Been Fixed

### 1. **Real-Time Data Fetching**
- ✅ **fetch-candles** function now uses real Tradovate WebSocket API
- ✅ **fetch-historical-candles** function pulls historical data properly
- ✅ Removed all mock/dummy data generation
- ✅ Connected to Redis for token management
- ✅ Proper token renewal flow implemented

### 2. **Timeframe Support**
All functions now support:
- 1 minute candles
- 5 minute candles  
- 10 minute candles
- 15 minute candles
- 30 minute candles
- 60 minute (1 hour) candles

### 3. **Environment Variables**
Fixed the mismatch between variable names:
- Changed `supabase_service_key_orca` → `SUPABASE_SERVICE_ROLE_KEY`
- Standardized all environment variable references
- Created proper configuration scripts

## 📋 Prerequisites

### Required Services
1. **Supabase Account** with a project
2. **Redis Instance** (Azure Cache for Redis)
3. **Tradovate Demo Account** credentials
4. **Node.js & Python 3** installed locally

### Required Environment Variables
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_PROJECT_REF=your-project-ref

# Redis
REDIS_HOST=redismanager.redis.cache.windows.net
REDIS_PORT=6380
REDIS_PASSWORD=your-redis-password
```

## 🛠️ Setup Instructions

### Step 1: Configure Environment Variables
```bash
# Run the environment setup script
./setup_environment_vars.sh

# This will:
# 1. Create/update .env file
# 2. Test Supabase connection
# 3. Test Redis connection
# 4. Optionally generate Tradovate tokens
```

### Step 2: Generate Tradovate Tokens
```bash
# Ensure credentials.json exists with Tradovate accounts
python3 token_generator_and_redis_manager.py

# This will:
# 1. Connect to Tradovate API
# 2. Generate access tokens
# 3. Store tokens in Redis with TTL
```

### Step 3: Deploy Edge Functions
```bash
# Run the deployment script
./setup_and_test_edge_functions.sh

# This will:
# 1. Deploy all three edge functions
# 2. Set environment secrets for each function
# 3. Test each function with different timeframes
# 4. Generate SQL for automated scheduling
```

### Step 4: Enable Automated Scheduling

1. Go to your Supabase SQL Editor:
   ```
   https://supabase.com/dashboard/project/[PROJECT_REF]/sql/new
   ```

2. Run the generated SQL from `setup_cron_job.sql`:
   ```sql
   -- Enable pg_cron extension
   CREATE EXTENSION IF NOT EXISTS pg_cron;

   -- Schedule jobs for each timeframe
   -- (The script generates specific cron jobs for 1, 5, 15, 30, 60 minute intervals)
   ```

### Step 5: Test and Monitor
```bash
# Run comprehensive tests
python3 test_edge_functions.py

# Or run continuous monitoring
python3 test_edge_functions.py --monitor --interval 5
```

## 📊 Edge Functions Overview

### 1. **fetch-candles**
- **Purpose**: Fetches real-time candle data for a specific timeframe
- **Endpoint**: `/functions/v1/fetch-candles`
- **Method**: POST
- **Payload**: `{"timeframe": 30}` (1, 5, 10, 15, 30, or 60)
- **Process**:
  1. Gets token from Redis
  2. Renews token to get MD access token
  3. Connects to Tradovate WebSocket
  4. Fetches latest candles
  5. Stores in Supabase tables

### 2. **fetch-historical-candles**
- **Purpose**: Fetches historical candle data
- **Endpoint**: `/functions/v1/fetch-historical-candles`
- **Method**: POST
- **Payload**: `{"timeframe": 30, "days_back": 5}`
- **Process**:
  1. Calculates number of candles needed
  2. Fetches all historical data via WebSocket
  3. Bulk inserts to Supabase

### 3. **scheduler**
- **Purpose**: Coordinates fetching for multiple timeframes
- **Endpoint**: `/functions/v1/scheduler`
- **Method**: POST
- **Process**:
  1. Checks last fetch time for each timeframe
  2. Triggers fetch-candles for due timeframes
  3. Updates fetch logs

## 🔍 Monitoring & Debugging

### View Function Logs
```bash
# Real-time logs for specific function
supabase functions logs fetch-candles --follow
supabase functions logs fetch-historical-candles --follow
supabase functions logs scheduler --follow
```

### Test Individual Functions
```bash
# Test fetch-candles
curl -X POST https://your-project.supabase.co/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 30}'

# Test fetch-historical-candles
curl -X POST https://your-project.supabase.co/functions/v1/fetch-historical-candles \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 30, "days_back": 5}'

# Test scheduler
curl -X POST https://your-project.supabase.co/functions/v1/scheduler \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🗃️ Database Tables

The functions store data in these Supabase tables:
- `nq_candles_1min` - 1-minute candle data
- `nq_candles_5min` - 5-minute candle data
- `nq_candles_10min` - 10-minute candle data
- `nq_candles_15min` - 15-minute candle data
- `nq_candles_30min` - 30-minute candle data
- `nq_candles_1hour` - 1-hour candle data
- `candle_fetch_log` - Tracking last fetch times

## ⚠️ Important Notes

### Token Management
- Tokens expire every hour (TTL: 3600 seconds)
- Run `token_generator_and_redis_manager.py` periodically
- Consider setting up a cron job for token refresh

### Rate Limiting
- Tradovate has rate limits on their API
- The functions include proper delays and throttling
- Monitor for 429 errors in logs

### Market Hours
- Futures markets closed: Friday 5PM ET to Sunday 6PM ET
- Functions will still run but may not get new data during closed hours
- Consider scheduling accordingly

## 🐛 Troubleshooting

### Function Not Working
1. Check environment variables are set correctly:
   ```bash
   supabase secrets list
   ```

2. Check Redis connection and tokens:
   ```python
   python3 -c "from app.services.orca_redis.client import get_redis_client; r = get_redis_client(); print(r.keys('token:*'))"
   ```

3. Check function logs for errors:
   ```bash
   supabase functions logs fetch-candles --follow
   ```

### No Data Being Stored
1. Verify Supabase RPC functions exist:
   - `insert_nq_candles_1min`
   - `insert_nq_candles_5min`
   - etc.

2. Check table permissions in Supabase

3. Verify contract symbol is correct (currently using `MNQZ5`)

### WebSocket Connection Issues
1. Token may be expired - regenerate tokens
2. Check network connectivity
3. Verify Tradovate demo API is accessible

## 📚 File Structure

```
orca-ven-backend-main/
├── supabase/
│   └── functions/
│       ├── fetch-candles/          # Real-time candle fetcher
│       ├── fetch-historical-candles/ # Historical data fetcher
│       └── scheduler/               # Orchestrator function
├── setup_environment_vars.sh       # Environment configuration
├── setup_and_test_edge_functions.sh # Deployment and testing
├── test_edge_functions.py          # Python testing utility
├── token_generator_and_redis_manager.py # Token management
└── credentials.json                # Tradovate credentials
```

## ✅ Success Checklist

- [ ] Environment variables configured in `.env`
- [ ] Redis connection working
- [ ] Tradovate tokens generated and stored in Redis
- [ ] Edge functions deployed to Supabase
- [ ] Environment secrets set for all functions
- [ ] Test all timeframes working
- [ ] Automated scheduling SQL executed
- [ ] Monitoring shows continuous data flow

## 🎯 Next Steps

1. **Set up token refresh automation**:
   ```bash
   # Add to crontab
   0 * * * * cd /path/to/project && python3 token_generator_and_redis_manager.py
   ```

2. **Monitor data quality**:
   - Check for gaps in candle data
   - Verify OHLC values are accurate
   - Compare with TradingView charts

3. **Scale if needed**:
   - Add more symbols (ES, YM, etc.)
   - Add more timeframes
   - Implement data validation

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review function logs
3. Test individual components
4. Verify all prerequisites are met

---

**Last Updated**: October 2024
**Version**: 2.0
**Status**: ✅ Production Ready
