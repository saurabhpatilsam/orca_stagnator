# ORCA Trading System - API Documentation

This directory contains comprehensive API documentation for all APIs used in the ORCA Trading System, organized for easy import into Postman.

## 📁 Directory Structure

```
api-documentation/
├── README.md                           # This file
├── postman-collections/                # Postman collection JSON files
│   ├── 1-internal-backend-apis.json    # Internal FastAPI endpoints
│   ├── 2-tradovate-apis.json          # Tradovate broker APIs
│   ├── 3-supabase-edge-functions.json # Supabase edge functions
│   └── 4-redis-operations.json        # Redis cache operations
├── api-reference/                      # Detailed API documentation
│   ├── internal-apis.md                # Internal API reference
│   ├── tradovate-apis.md              # Tradovate API reference
│   ├── supabase-functions.md          # Supabase functions reference
│   └── redis-operations.md            # Redis operations reference
└── environments/                       # Postman environment files
    ├── development.json                # Dev environment variables
    └── production.json                 # Prod environment variables
```

## 🚀 Quick Start

### Import to Postman

1. Open Postman
2. Click **Import** button (top left)
3. Select **Folder** tab
4. Navigate to `api-documentation/postman-collections/`
5. Select all collection files and click **Import**

### Environment Setup

1. Import environment files from `api-documentation/environments/`
2. Select the appropriate environment (development/production)
3. Update environment variables with your credentials:
   - `BASE_URL` - Your API base URL
   - `TRADOVATE_TOKEN` - Tradovate access token
   - `SUPABASE_URL` - Supabase project URL
   - `SUPABASE_KEY` - Supabase service role key
   - `REDIS_HOST` - Redis host
   - `REDIS_PASSWORD` - Redis password

## 📊 API Collections Overview

### 1. Internal Backend APIs (`1-internal-backend-apis.json`)
FastAPI endpoints for trading operations, backtesting, and health checks.

**Base URL:** `http://localhost:8000` (dev) | `https://your-domain.com` (prod)

**Categories:**
- Health Checks
- HFT Trading API
- Max Trading Bot API
- Data Upload API

**Total Endpoints:** 15+

---

### 2. Tradovate APIs (`2-tradovate-apis.json`)
External Tradovate broker API for trading operations.

**Base URL:** `https://tv-demo.tradovateapi.com` (demo) | `https://tv-live.tradovateapi.com` (live)

**Categories:**
- Authentication
- Account Management
- Order Management
- Market Data
- Position Management

**Total Endpoints:** 12+

---

### 3. Supabase Edge Functions (`3-supabase-edge-functions.json`)
Serverless functions for candle data fetching and storage.

**Base URL:** `https://dcoukhtfcloqpfmijock.supabase.co/functions/v1`

**Categories:**
- Candle Fetchers
- Historical Data
- Scheduler
- Token Manager

**Total Endpoints:** 4

---

### 4. Redis Operations (`4-redis-operations.json`)
Redis cache operations for tokens and data storage.

**Host:** `redismanager.redis.cache.windows.net:6380`

**Categories:**
- Token Management
- Cache Operations
- Data Retrieval

**Note:** These are documented as pseudo-HTTP operations for reference

---

## 🔑 Authentication

### Tradovate API
- **Type:** Bearer Token
- **Token Location:** Redis (`token:{ACCOUNT_NAME}`)
- **Renewal:** Every 5 hours via token manager
- **Accounts:** APEX_266668, APEX_272045, APEX_136189, APEX_265995

### Supabase
- **Type:** API Key
- **Header:** `apikey` or `Authorization: Bearer {key}`
- **Service Role Key:** Used for edge functions

### Internal APIs
- **Type:** Optional (currently open for development)
- **Future:** JWT or API key authentication

---

## 📝 API Reference Documentation

Detailed documentation for each API is available in the `api-reference/` directory:

- **[Internal APIs Reference](api-reference/internal-apis.md)** - Complete FastAPI endpoint documentation
- **[Tradovate APIs Reference](api-reference/tradovate-apis.md)** - Tradovate broker API documentation
- **[Supabase Functions Reference](api-reference/supabase-functions.md)** - Edge function documentation
- **[Redis Operations Reference](api-reference/redis-operations.md)** - Redis cache operations

---

## 🛠️ Usage Examples

### Example 1: Get All Trading Accounts
```bash
curl -X GET "http://localhost:8000/api/v1/trading/accounts" \
  -H "Content-Type: application/json"
```

### Example 2: Fetch Real-Time Candles
```bash
curl -X POST "https://dcoukhtfcloqpfmijock.supabase.co/functions/v1/fetch-candles" \
  -H "Authorization: Bearer YOUR_SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"timeframe": 5}'
```

### Example 3: Place Order via Tradovate
```bash
curl -X POST "https://tv-demo.tradovateapi.com/accounts/{accountId}/orders" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "instrument=MNQZ5&qty=1&side=Buy&type=Limit&limitPrice=21000&durationType=Day"
```

---

## 📚 Additional Resources

- **System Architecture:** See `/docs/SYSTEM_ARCHITECTURE.md`
- **Deployment Guide:** See `/docs/guides/AUTOMATED_DEPLOYMENT_GUIDE.md`
- **Edge Functions Guide:** See `/EDGE_FUNCTIONS_COMPLETE_GUIDE.md`
- **Token Management:** See `/TOKEN_FLOW_DOCUMENTATION.md`

---

## 🔄 API Versioning

- **Internal APIs:** v1 (current), v2 (planned)
- **Tradovate:** v1 (stable)
- **Supabase:** Edge Functions (stable)

---

## 📞 Support

For issues or questions:
1. Check the detailed API reference docs
2. Review the main project README
3. Contact the development team

---

## 📅 Last Updated

**Date:** 2025-01-21  
**Version:** 1.0.0  
**Maintainer:** ORCA Development Team
