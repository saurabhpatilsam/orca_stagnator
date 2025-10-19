# 🚀 High-Frequency Trading API Guide

**Complete guide for the ORCA HFT Trading API**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [API Endpoints](#api-endpoints)
4. [Performance Optimization](#performance-optimization)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)

---

## 🎯 Overview

The ORCA HFT Trading API is optimized for **High-Frequency Trading** and **Medium-Frequency Trading** bots with:

- ⚡ **Ultra-fast response times**: <50ms for cached data, <1000ms for fresh data
- 🔄 **Redis caching**: Configurable TTLs for different data types
- 📦 **Minimal payloads**: ID-only endpoints for maximum speed
- 🔗 **Batch operations**: Single call for complete trading snapshot
- 🎯 **Real-time data**: 1-2 second cache TTL for orders and positions

### Base URL

```
http://localhost:8000/api/v1/trading
```

### Authentication

All endpoints use Redis-stored JWT tokens. Default account: `PAAPEX2666680000001`

---

## ⚡ Quick Start

### 1. Start the API Server

```bash
cd /Users/stagnator/Downloads/orca-ven-backend-main
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Health Check

```bash
curl http://localhost:8000/api/v1/trading/health
```

### 3. Get All Accounts

```bash
curl http://localhost:8000/api/v1/trading/accounts
```

---

## 📡 API Endpoints

### 1. Get All Accounts

**Endpoint:** `GET /api/v1/trading/accounts`

**Description:** Retrieve all Tradovate accounts for the authenticated user.

**Parameters:**
- `use_cache` (bool, optional): Use cached data. Default: `true`
- `account_name` (string, optional): Account name for auth. Default: `PAAPEX2666680000001`

**Cache TTL:** 5 minutes (accounts rarely change)

**Response Time:** <50ms (cached), <500ms (fresh)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/accounts?use_cache=true"
```

**Example Response:**
```json
{
  "accounts": [
    {
      "name": "PAAPEX2666680000001",
      "id": "D17158695",
      "active": true
    },
    {
      "name": "PAAPEX2666680000003",
      "id": "D17159229",
      "active": true
    }
  ],
  "count": 2,
  "cached": true,
  "timestamp": 1697400000.123
}
```

---

### 2. Get All Active Positions

**Endpoint:** `GET /api/v1/trading/positions`

**Description:** Get all active positions across accounts.

**Parameters:**
- `use_cache` (bool, optional): Use cached data. Default: `false`
- `account_ids` (string, optional): Comma-separated account IDs (e.g., `D17158695,D17159229`)
- `account_name` (string, optional): Account name for auth

**Cache TTL:** 1 second (positions change frequently)

**Response Time:** <100ms (cached), <800ms (fresh)

**Example Request:**
```bash
# All accounts
curl "http://localhost:8000/api/v1/trading/positions"

# Specific accounts
curl "http://localhost:8000/api/v1/trading/positions?account_ids=D17158695,D17159229"
```

**Example Response:**
```json
{
  "positions": [
    {
      "id": "12345",
      "account_id": "D17158695",
      "instrument": "MNQZ5",
      "quantity": 2,
      "side": "long",
      "avg_price": 24900.0,
      "unrealized_pnl": 450.0
    }
  ],
  "count": 1,
  "cached": false,
  "timestamp": 1697400000.123
}
```

---

### 3. Get Pending Orders

**Endpoint:** `GET /api/v1/trading/orders/pending`

**Description:** Get all pending orders (Working, Pending, Queued status).

**Parameters:**
- `use_cache` (bool, optional): Use cached data. Default: `false`
- `account_ids` (string, optional): Comma-separated account IDs
- `account_name` (string, optional): Account name for auth

**Cache TTL:** 1 second

**Response Time:** <100ms (cached), <1000ms (fresh)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/orders/pending"
```

**Example Response:**
```json
{
  "orders": [
    {
      "order_id": "268137614455",
      "account_id": "D17158695",
      "instrument": "MNQZ5",
      "side": "buy",
      "quantity": 1,
      "price": 24900.0,
      "status": "Working",
      "order_type": "Stop"
    }
  ],
  "count": 1,
  "cached": false,
  "timestamp": 1697400000.123
}
```

---

### 4. Get Pending Order IDs Only (HFT Optimized)

**Endpoint:** `GET /api/v1/trading/orders/pending/ids`

**Description:** Ultra-fast endpoint returning only order IDs (minimal payload).

**Parameters:** Same as pending orders endpoint

**Response Time:** <50ms

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/orders/pending/ids"
```

**Example Response:**
```json
{
  "order_ids": [
    "268137614455",
    "268137614456",
    "268137614457"
  ],
  "count": 3,
  "cached": false,
  "timestamp": 1697400000.123
}
```

**Use Cases:**
- Quick order existence checks before cancellation
- High-frequency order monitoring
- Rapid order count checks

---

### 5. Get Position IDs Only (HFT Optimized)

**Endpoint:** `GET /api/v1/trading/positions/ids`

**Description:** Ultra-fast endpoint returning only position IDs.

**Parameters:** Same as positions endpoint

**Response Time:** <50ms

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/positions/ids"
```

**Example Response:**
```json
{
  "position_ids": [
    "12345",
    "12346",
    "12347"
  ],
  "count": 3,
  "cached": false,
  "timestamp": 1697400000.123
}
```

---

### 6. Get Account Balances

**Endpoint:** `GET /api/v1/trading/balances`

**Description:** Get account balance information for all or specific accounts.

**Parameters:**
- `use_cache` (bool, optional): Use cached data. Default: `true`
- `account_ids` (string, optional): Comma-separated account IDs
- `account_name` (string, optional): Account name for auth

**Cache TTL:** 2 seconds

**Response Time:** <100ms (cached), <1200ms (fresh)

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/balances"
```

**Example Response:**
```json
{
  "balances": [
    {
      "account_id": "D17158695",
      "account_name": "PAAPEX2666680000001",
      "balance": 50000.0,
      "net_liquidating_value": 50450.0,
      "cash_balance": 48000.0,
      "open_pl": 450.0,
      "realized_pl": 2000.0
    }
  ],
  "total_balance": 50450.0,
  "count": 1,
  "cached": true,
  "timestamp": 1697400000.123
}
```

---

### 7. Get Trading Snapshot (Batch Endpoint)

**Endpoint:** `GET /api/v1/trading/batch/snapshot`

**Description:** Get complete trading snapshot in a single call. **Most efficient for bot initialization.**

**Parameters:**
- `include_accounts` (bool, optional): Include accounts. Default: `true`
- `include_positions` (bool, optional): Include positions. Default: `true`
- `include_orders` (bool, optional): Include orders. Default: `true`
- `include_balances` (bool, optional): Include balances. Default: `true`
- `use_cache` (bool, optional): Use cached data. Default: `false`
- `account_ids` (string, optional): Comma-separated account IDs
- `account_name` (string, optional): Account name for auth

**Response Time:** <200ms (cached), <2000ms (fresh)

**Example Request:**
```bash
# Full snapshot
curl "http://localhost:8000/api/v1/trading/batch/snapshot"

# Positions and orders only
curl "http://localhost:8000/api/v1/trading/batch/snapshot?include_accounts=false&include_balances=false"
```

**Example Response:**
```json
{
  "accounts": { ... },
  "positions": { ... },
  "orders": { ... },
  "balances": { ... },
  "metadata": {
    "response_time_ms": 156.7,
    "timestamp": 1697400000.123,
    "datetime": "2025-10-15T20:30:00.123456"
  }
}
```

**Use Cases:**
- Bot initialization/startup
- Dashboard full refresh
- Monitoring system updates
- Risk management checks

---

### 8. Health Check

**Endpoint:** `GET /api/v1/trading/health`

**Description:** Check API health and connectivity.

**Example Request:**
```bash
curl "http://localhost:8000/api/v1/trading/health"
```

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": 1697400000.123,
  "datetime": "2025-10-15T20:30:00.123456",
  "checks": {
    "redis": "healthy",
    "broker": "healthy"
  },
  "response_time_ms": 15.3
}
```

---

## 🚀 Performance Optimization

### Cache Strategy

| Data Type | Cache TTL | Recommended for HFT |
|-----------|-----------|---------------------|
| Accounts | 5 minutes | ✅ Always cache |
| Positions | 1 second | ⚠️ Cache optional |
| Orders | 1 second | ⚠️ Cache optional |
| Balances | 2 seconds | ✅ Cache recommended |

### Response Time Targets

| Endpoint | Target (Cached) | Target (Fresh) |
|----------|----------------|----------------|
| Accounts | <50ms | <500ms |
| Positions | <100ms | <800ms |
| Orders | <100ms | <1000ms |
| Order IDs | <50ms | <300ms |
| Position IDs | <50ms | <300ms |
| Balances | <100ms | <1200ms |
| Snapshot | <200ms | <2000ms |

### Best Practices

1. **Use ID-only endpoints** when you only need to check existence
2. **Enable caching** for dashboard/monitoring (not critical for HFT decisions)
3. **Use batch endpoint** for bot initialization to reduce round trips
4. **Filter by specific accounts** when you don't need all data
5. **Monitor health endpoint** to detect connectivity issues

---

## 💡 Usage Examples

### Python Example (HFT Bot)

```python
import requests
import time

BASE_URL = "http://localhost:8000/api/v1/trading"

class HFTBot:
    def __init__(self):
        self.base_url = BASE_URL
    
    def get_pending_order_ids(self):
        """Ultra-fast order check"""
        response = requests.get(f"{self.base_url}/orders/pending/ids")
        data = response.json()
        return data["order_ids"]
    
    def get_positions(self, account_id=None):
        """Get current positions"""
        url = f"{self.base_url}/positions"
        params = {"account_ids": account_id} if account_id else {}
        response = requests.get(url, params=params)
        return response.json()["positions"]
    
    def initialize(self):
        """Fast bot initialization using batch endpoint"""
        response = requests.get(f"{self.base_url}/batch/snapshot")
        snapshot = response.json()
        
        print(f"Accounts: {snapshot['accounts']['count']}")
        print(f"Positions: {snapshot['positions']['count']}")
        print(f"Pending Orders: {snapshot['orders']['count']}")
        print(f"Total Balance: ${snapshot['balances']['total_balance']:,.2f}")
        
        return snapshot
    
    def trading_loop(self):
        """Main HFT loop"""
        while True:
            # Check positions (real-time, no cache)
            positions = self.get_positions()
            
            # Check pending orders (fast ID check)
            order_ids = self.get_pending_order_ids()
            
            # Your trading logic here
            print(f"Positions: {len(positions)}, Orders: {len(order_ids)}")
            
            time.sleep(0.1)  # 100ms loop for HFT

# Usage
bot = HFTBot()
bot.initialize()
# bot.trading_loop()
```

### JavaScript Example (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000/api/v1/trading';

class TradingBot {
  async getSnapshot() {
    const response = await axios.get(`${BASE_URL}/batch/snapshot`);
    return response.data;
  }
  
  async getPendingOrders(accountIds = null) {
    const params = accountIds ? { account_ids: accountIds } : {};
    const response = await axios.get(`${BASE_URL}/orders/pending`, { params });
    return response.data.orders;
  }
  
  async getPositions(accountIds = null) {
    const params = accountIds ? { account_ids: accountIds } : {};
    const response = await axios.get(`${BASE_URL}/positions`, { params });
    return response.data.positions;
  }
  
  async getBalances() {
    const response = await axios.get(`${BASE_URL}/balances`, {
      params: { use_cache: true }
    });
    return response.data;
  }
}

// Usage
const bot = new TradingBot();

bot.getSnapshot().then(snapshot => {
  console.log('Trading Snapshot:', snapshot);
});
```

### cURL Examples

```bash
# Get all accounts (cached)
curl "http://localhost:8000/api/v1/trading/accounts"

# Get positions for specific accounts (no cache)
curl "http://localhost:8000/api/v1/trading/positions?account_ids=D17158695,D17159229&use_cache=false"

# Get pending order IDs (ultra-fast)
curl "http://localhost:8000/api/v1/trading/orders/pending/ids"

# Get complete snapshot
curl "http://localhost:8000/api/v1/trading/batch/snapshot"

# Get balances (with cache)
curl "http://localhost:8000/api/v1/trading/balances?use_cache=true"

# Health check
curl "http://localhost:8000/api/v1/trading/health"
```

---

## 🎯 Best Practices for HFT Bots

### 1. Initialization Phase
- Use `batch/snapshot` endpoint to load all data in one call
- Cache account IDs locally
- Build initial state from snapshot

### 2. Main Trading Loop
- Use ID-only endpoints for quick checks
- Disable cache for real-time trading decisions
- Enable cache for risk management checks (balances)

### 3. Error Handling
- Monitor `health` endpoint
- Implement exponential backoff on failures
- Have fallback logic for cache misses

### 4. Network Optimization
- Use HTTP keep-alive connections
- Implement connection pooling
- Consider WebSocket for real-time updates (future enhancement)

### 5. Monitoring
- Track response times
- Alert on degraded performance
- Log all API calls for debugging

---

## 📊 API Performance Metrics

The API includes response time metrics in all responses:

```json
{
  "data": { ... },
  "cached": false,
  "timestamp": 1697400000.123
}
```

- `cached`: Whether data came from cache
- `timestamp`: Unix timestamp of response
- Response time can be calculated client-side

---

## 🔧 Troubleshooting

### Slow Response Times

1. **Check Redis connectivity**: `GET /api/v1/trading/health`
2. **Enable caching** where appropriate
3. **Filter to specific accounts** to reduce data volume
4. **Use ID-only endpoints** for quick checks

### Stale Data

1. **Disable caching** for real-time requirements: `use_cache=false`
2. **Check cache TTL** settings in the router
3. **Clear Redis cache** manually if needed

### Authentication Errors

1. **Verify token exists** in Redis: `token:PAAPEX2666680000001`
2. **Check account name** parameter
3. **Review token expiration**

---

## 📝 API Changelog

### Version 2.0.0 (Current)
- ✅ Added HFT-optimized endpoints
- ✅ Implemented Redis caching
- ✅ Added batch snapshot endpoint
- ✅ Added ID-only endpoints
- ✅ Performance optimization (<50ms cached responses)

---

## 🆘 Support

For issues or questions:
1. Check logs in the server console
2. Review the health endpoint
3. Verify Redis and broker connectivity
4. Contact the development team

---

**Last Updated:** 2025-10-15  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
