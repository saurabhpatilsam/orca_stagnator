# Supabase Edge Functions Reference

Complete reference for Supabase serverless edge functions used in ORCA Trading System.

**Base URL:** `https://dcoukhtfcloqpfmijock.supabase.co/functions/v1`  
**Authentication:** Bearer Token (Supabase Service Role Key)  
**Project ID:** dcoukhtfcloqpfmijock

---

## Table of Contents

- [Overview](#overview)
- [Candle Data Fetchers](#candle-data-fetchers)
- [Historical Data](#historical-data)
- [Automation](#automation)
- [Database Integration](#database-integration)
- [Deployment](#deployment)

---

## Overview

### What Are Edge Functions?

Supabase Edge Functions are serverless TypeScript/Deno functions that run close to users globally. In ORCA, they fetch real-time candlestick data from Tradovate and store it in Supabase database.

### Architecture

```
Tradovate WebSocket → Edge Function → Supabase Database
         ↑                                    ↓
    Redis Tokens                    Candle Tables (1min-60min)
```

### Key Features

- Real-time WebSocket connections to Tradovate
- Automatic token management via Redis
- Duplicate prevention (unique index on symbol + time)
- Multiple timeframe support (1, 5, 10, 15, 30, 60 minutes)
- Automated scheduling via pg_cron

---

## Candle Data Fetchers

### 1. Fetch Real-Time Candles

**Endpoint:** `POST /functions/v1/fetch-candles`

**Description:** Fetch real-time candlestick data via WebSocket for specified timeframe. Stores last 10 candles in database with automatic duplicate prevention.

**Headers:**
```
Authorization: Bearer {SUPABASE_SERVICE_ROLE_KEY}
Content-Type: application/json
```

**Request Body:**
```json
{
  "timeframe": 30
}
```

**Timeframe Options:**
- `1` - 1 minute candles
- `5` - 5 minute candles
- `10` - 10 minute candles
- `15` - 15 minute candles
- `30` - 30 minute candles
- `60` - 60 minute (1 hour) candles

**Example Request:**
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 30}'
```

**Response (Success):**
```json
{
  "success": true,
  "timeframe": 30,
  "symbol": "MNQZ5",
  "candles_fetched": 10,
  "candles_stored": 10,
  "errors": 0,
  "timestamp": "2025-01-21T20:00:00.000Z"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "No Tradovate TV token found in Redis",
  "timestamp": "2025-01-21T20:00:00.000Z"
}
```

### How It Works

1. **Get Token from Redis:** Retrieves Tradovate token from Redis (tries multiple accounts)
2. **Renew Token:** Calls Tradovate token renewal API to get mdAccessToken
3. **Connect WebSocket:** Establishes connection to `wss://md-demo.tradovateapi.com/v1/websocket`
4. **Authorize:** Sends authorization message with mdAccessToken
5. **Request Chart:** Requests last 10 candles for timeframe
6. **Process Data:** Receives candle bars, excludes current incomplete candle
7. **Store in DB:** Calls RPC function to insert candles (skips duplicates)

### Current Symbol

**Symbol:** MNQZ5 (Micro E-mini Nasdaq, December 2025)

**Auto-Discovery:** Functions use contract suggest API to find current front-month contract (switches to next month when < 7 days to expiration)

### Database Tables

| Timeframe | Table Name | RPC Function |
|-----------|------------|--------------|
| 1 min | nq_candles_1min | insert_nq_candles_1min |
| 5 min | nq_candles_5min | insert_nq_candles_5min |
| 10 min | nq_candles_10min | insert_nq_candles_10min |
| 15 min | nq_candles_15min | insert_nq_candles_15min |
| 30 min | nq_candles_30min | insert_nq_candles_30min |
| 60 min | nq_candles_1hour | insert_nq_candles_1hour |

### Table Schema

```sql
CREATE TABLE nq_candles_30min (
  id BIGSERIAL PRIMARY KEY,
  symbol TEXT NOT NULL,
  candle_time TIMESTAMPTZ NOT NULL,
  open NUMERIC(10,2) NOT NULL,
  high NUMERIC(10,2) NOT NULL,
  low NUMERIC(10,2) NOT NULL,
  close NUMERIC(10,2) NOT NULL,
  volume BIGINT NOT NULL DEFAULT 0,
  up_volume BIGINT NOT NULL DEFAULT 0,
  down_volume BIGINT NOT NULL DEFAULT 0,
  up_ticks BIGINT NOT NULL DEFAULT 0,
  down_ticks BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(symbol, candle_time)
);

CREATE INDEX idx_nq_candles_30min_time ON nq_candles_30min(candle_time);
CREATE INDEX idx_nq_candles_30min_symbol ON nq_candles_30min(symbol);
```

---

## Historical Data

### 1. Fetch Historical Candles

**Endpoint:** `POST /functions/v1/fetch-historical-candles`

**Description:** Fetch historical candlestick data for backfilling. Makes multiple API calls to retrieve large date ranges.

**Request Body:**
```json
{
  "timeframe": 30,
  "symbol": "MNQZ5",
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-21T23:59:59Z",
  "barsPerRequest": 100
}
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| timeframe | number | Yes | Timeframe in minutes (1, 5, 10, 15, 30, 60) |
| symbol | string | No | Contract symbol (default: auto-discover) |
| startDate | string | Yes | Start date (ISO 8601 format) |
| endDate | string | Yes | End date (ISO 8601 format) |
| barsPerRequest | number | No | Bars per API call (default: 100, max: 500) |

**Example Request:**
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-historical-candles" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "timeframe": 30,
    "symbol": "MNQZ5",
    "startDate": "2025-01-01T00:00:00Z",
    "endDate": "2025-01-21T23:59:59Z",
    "barsPerRequest": 100
  }'
```

**Response:**
```json
{
  "success": true,
  "timeframe": 30,
  "symbol": "MNQZ5",
  "date_range": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-21T23:59:59Z"
  },
  "total_candles_fetched": 672,
  "total_candles_stored": 670,
  "duplicates_skipped": 2,
  "api_calls_made": 7,
  "duration_seconds": 45.2,
  "timestamp": "2025-01-21T20:00:00.000Z"
}
```

**Use Cases:**
- Initial database population
- Backfilling missing data
- Historical analysis preparation

**Performance:**
- Typical: 100 candles per API call
- Processing: ~6 seconds per call
- Rate limiting: Built-in delays between calls

---

## Automation

### 1. Scheduler

**Endpoint:** `POST /functions/v1/scheduler`

**Description:** Orchestrates automatic fetching for all timeframes. Triggers fetch-candles sequentially.

**Request Body:**
```json
{
  "action": "fetch_all"
}
```

**Actions:**
- `fetch_all` - Fetch all timeframes (1, 5, 10, 15, 30, 60 min)
- `fetch_selective` - Fetch specific timeframes (future feature)

**Example Request:**
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/scheduler" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"action": "fetch_all"}'
```

**Response:**
```json
{
  "success": true,
  "action": "fetch_all",
  "results": [
    {
      "timeframe": 1,
      "success": true,
      "candles_stored": 10
    },
    {
      "timeframe": 5,
      "success": true,
      "candles_stored": 10
    },
    {
      "timeframe": 10,
      "success": true,
      "candles_stored": 10
    },
    {
      "timeframe": 15,
      "success": true,
      "candles_stored": 10
    },
    {
      "timeframe": 30,
      "success": true,
      "candles_stored": 10
    },
    {
      "timeframe": 60,
      "success": true,
      "candles_stored": 10
    }
  ],
  "total_duration_seconds": 62.5,
  "timestamp": "2025-01-21T20:00:00.000Z"
}
```

### Automated Scheduling (pg_cron)

**Location:** `setup_cron_jobs.sql`

**Cron Jobs:**
```sql
-- 1 minute candles (every minute)
SELECT cron.schedule('fetch-1min-candles', '* * * * *', 
  $$SELECT net.http_post(...fetch-candles...timeframe:1)$$);

-- 5 minute candles (every 5 minutes)
SELECT cron.schedule('fetch-5min-candles', '*/5 * * * *',
  $$SELECT net.http_post(...fetch-candles...timeframe:5)$$);

-- 10 minute candles (every 10 minutes)
SELECT cron.schedule('fetch-10min-candles', '*/10 * * * *',
  $$SELECT net.http_post(...fetch-candles...timeframe:10)$$);

-- 15 minute candles (every 15 minutes)
SELECT cron.schedule('fetch-15min-candles', '*/15 * * * *',
  $$SELECT net.http_post(...fetch-candles...timeframe:15)$$);

-- 30 minute candles (every 30 minutes)
SELECT cron.schedule('fetch-30min-candles', '*/30 * * * *',
  $$SELECT net.http_post(...fetch-candles...timeframe:30)$$);

-- 60 minute candles (every hour)
SELECT cron.schedule('fetch-60min-candles', '0 * * * *',
  $$SELECT net.http_post(...fetch-candles...timeframe:60)$$);
```

**View Active Jobs:**
```sql
SELECT * FROM cron.job;
```

**Check Job History:**
```sql
SELECT * FROM cron.job_run_details 
ORDER BY start_time DESC 
LIMIT 10;
```

---

### 2. Token Manager

**Endpoint:** `POST /functions/v1/token-manager`

**Description:** Manually trigger token refresh for all Tradovate accounts (normally handled by server-side script).

**Request Body:**
```json
{
  "action": "refresh"
}
```

**Example Request:**
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/token-manager" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

**Response:**
```json
{
  "success": true,
  "tokens_refreshed": 4,
  "accounts": [
    "APEX_266668",
    "APEX_272045", 
    "APEX_136189",
    "APEX_265995"
  ],
  "timestamp": "2025-01-21T20:00:00.000Z"
}
```

**Note:** Token management is primarily handled by `token_generator_and_redis_manager.py` running on the server. This function is for manual intervention only.

---

## Database Integration

### RPC Functions

Each timeframe has a dedicated RPC function for inserting candles:

```sql
CREATE OR REPLACE FUNCTION insert_nq_candles_30min(
  p_symbol TEXT,
  p_candle_time TIMESTAMPTZ,
  p_open NUMERIC,
  p_high NUMERIC,
  p_low NUMERIC,
  p_close NUMERIC,
  p_volume BIGINT,
  p_up_volume BIGINT DEFAULT 0,
  p_down_volume BIGINT DEFAULT 0,
  p_up_ticks BIGINT DEFAULT 0,
  p_down_ticks BIGINT DEFAULT 0
) RETURNS VOID AS $$
BEGIN
  INSERT INTO nq_candles_30min (
    symbol, candle_time, open, high, low, close, 
    volume, up_volume, down_volume, up_ticks, down_ticks
  )
  VALUES (
    p_symbol, p_candle_time, p_open, p_high, p_low, p_close,
    p_volume, p_up_volume, p_down_volume, p_up_ticks, p_down_ticks
  )
  ON CONFLICT (symbol, candle_time) DO NOTHING;
END;
$$ LANGUAGE plpgsql;
```

**Key Feature:** `ON CONFLICT DO NOTHING` prevents duplicate insertions

### Query Examples

**Get Latest 100 Candles:**
```sql
SELECT * FROM nq_candles_30min
WHERE symbol = 'MNQZ5'
ORDER BY candle_time DESC
LIMIT 100;
```

**Get Candles for Date Range:**
```sql
SELECT * FROM nq_candles_30min
WHERE symbol = 'MNQZ5'
  AND candle_time >= '2025-01-01'
  AND candle_time < '2025-01-22'
ORDER BY candle_time ASC;
```

**Get Candles with Volume Filter:**
```sql
SELECT * FROM nq_candles_30min
WHERE symbol = 'MNQZ5'
  AND volume > 1000
ORDER BY candle_time DESC
LIMIT 50;
```

**JavaScript/TypeScript Client:**
```typescript
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://dcoukhtfcloqpfmijock.supabase.co',
  'YOUR_SUPABASE_KEY'
);

// Fetch latest 100 candles
const { data, error } = await supabase
  .from('nq_candles_30min')
  .select('*')
  .eq('symbol', 'MNQZ5')
  .order('candle_time', { ascending: false })
  .limit(100);
```

---

## Deployment

### Deploy Edge Functions

**Prerequisites:**
- Supabase CLI installed
- Project linked to Supabase
- Environment variables configured

**Deploy Command:**
```bash
# Deploy single function
supabase functions deploy fetch-candles --no-verify-jwt

# Deploy all functions
supabase functions deploy fetch-candles --no-verify-jwt
supabase functions deploy fetch-historical-candles --no-verify-jwt
supabase functions deploy scheduler --no-verify-jwt
supabase functions deploy token-manager --no-verify-jwt
```

**Set Environment Secrets:**
```bash
supabase secrets set REDIS_HOST=redismanager.redis.cache.windows.net
supabase secrets set REDIS_PORT=6380
supabase secrets set REDIS_PASSWORD=your_redis_password
```

**View Logs:**
```bash
# Real-time logs
supabase functions logs fetch-candles --tail

# Recent logs
supabase functions logs fetch-candles --limit 100
```

### Testing Functions

**Test Locally:**
```bash
# Serve function locally
supabase functions serve fetch-candles

# Test with curl
curl -X POST http://localhost:54321/functions/v1/fetch-candles \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 30}'
```

**Test in Production:**
```bash
# Use test_edge_functions.py
python test_edge_functions.py

# Or use provided shell script
./setup_and_test_edge_functions.sh
```

### Monitoring Script

**Location:** `test_edge_functions.py`

**Usage:**
```bash
python test_edge_functions.py
```

**Output:**
```
Testing Supabase Edge Functions
================================

Testing 1-minute candles...
✅ 1min: Success - 10 candles stored

Testing 5-minute candles...
✅ 5min: Success - 10 candles stored

Testing 30-minute candles...
✅ 30min: Success - 10 candles stored

All tests completed!
```

---

## Performance Metrics

**Response Times:**
- fetch-candles: 5-10 seconds (WebSocket connection + data fetch)
- fetch-historical-candles: 6-8 seconds per 100 candles
- scheduler: 60-70 seconds (all timeframes)

**Resource Usage:**
- Memory: ~50MB per function invocation
- CPU: Minimal (mostly I/O waiting)
- Network: ~10KB per candle

**Reliability:**
- Success rate: >99.5%
- Automatic retry on failure
- Duplicate prevention via unique constraints

---

## Troubleshooting

### Common Issues

**1. "No Tradovate TV token found in Redis"**
- Check Redis connectivity
- Verify token_generator_and_redis_manager.py is running
- Manually refresh tokens

**2. "WebSocket timeout"**
- Tradovate API may be down
- Check network connectivity
- Retry after 30 seconds

**3. "Candles not being stored"**
- Check database permissions
- Verify RPC functions exist
- Check for table schema changes

### Debug Mode

Enable detailed logging in function code:
```typescript
console.log('Debug info:', { token, symbol, timeframe });
```

View logs:
```bash
supabase functions logs fetch-candles --tail
```

---

## Best Practices

1. **Always use service role key** for edge function authentication
2. **Monitor cron job status** regularly via `cron.job_run_details`
3. **Handle duplicates gracefully** (already implemented)
4. **Set reasonable timeouts** for WebSocket connections (30s)
5. **Log all errors** for troubleshooting
6. **Test locally** before deploying to production
7. **Use historical fetcher** for backfilling, not real-time fetcher

---

## Support

**Documentation:** `/EDGE_FUNCTIONS_COMPLETE_GUIDE.md`  
**Setup Script:** `setup_and_test_edge_functions.sh`  
**Test Script:** `test_edge_functions.py`  
**Cron Jobs:** `setup_cron_jobs.sql`
