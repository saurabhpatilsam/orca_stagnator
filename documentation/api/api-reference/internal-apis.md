# Internal Backend APIs Reference

Complete reference for ORCA Trading System FastAPI endpoints.

**Base URL (Development):** `http://localhost:8000`  
**Base URL (Production):** `https://your-domain.com`

---

## Table of Contents

- [Health Check APIs](#health-check-apis)
- [HFT Trading API](#hft-trading-api)
- [Max Trading Bot API](#max-trading-bot-api)
- [Data Upload API](#data-upload-api)
- [Error Handling](#error-handling)

---

## Health Check APIs

### 1. Root Health Check

**Endpoint:** `GET /api/health/`

**Description:** Basic health check endpoint for the main API server.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-21T20:00:00.000000"
}
```

---

### 2. Trading API Health

**Endpoint:** `GET /api/v1/trading/health`

**Description:** Comprehensive health check that verifies Redis and broker connectivity.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1737488400.123,
  "datetime": "2025-01-21T20:00:00.000000",
  "checks": {
    "redis": "healthy",
    "broker": "healthy"
  },
  "response_time_ms": 45.23
}
```

**Possible Status Values:**
- `healthy` - All systems operational
- `degraded` - Some systems unavailable but API functional
- `unhealthy` - Critical systems down

---

## HFT Trading API

High-performance trading endpoints optimized for low latency (<50ms cached, <1000ms fresh).

### 1. Get All Accounts

**Endpoint:** `GET /api/v1/trading/accounts`

**Description:** Retrieve all Tradovate accounts for the authenticated user.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| use_cache | boolean | true | Use cached data if available |
| account_name | string | PAAPEX2666680000001 | Account name for authentication |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/trading/accounts?use_cache=true&account_name=PAAPEX2666680000001"
```

**Response:**
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
  "timestamp": 1737488400.123
}
```

**Cache TTL:** 300 seconds (5 minutes)  
**Response Time:** <50ms (cached), <500ms (fresh)

---

### 2. Get All Positions

**Endpoint:** `GET /api/v1/trading/positions`

**Description:** Get all active positions across specified accounts.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| use_cache | boolean | false | Use cached data (not recommended for HFT) |
| account_ids | string | null | Comma-separated account IDs (e.g., D17158695,D17159229) |
| account_name | string | PAAPEX2666680000001 | Account name for authentication |

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/trading/positions?account_ids=D17158695,D17159229&account_name=PAAPEX2666680000001"
```

**Response:**
```json
{
  "positions": [
    {
      "id": "12345",
      "account_id": "D17158695",
      "instrument": "MNQZ5",
      "quantity": 2,
      "side": "long",
      "avg_price": 21000.50,
      "unrealized_pnl": 125.00
    }
  ],
  "count": 1,
  "cached": false,
  "timestamp": 1737488400.123
}
```

**Cache TTL:** 1 second  
**Response Time:** <100ms (cached), <800ms (fresh)

---

### 3. Get Position IDs Only

**Endpoint:** `GET /api/v1/trading/positions/ids`

**Description:** Ultra-fast endpoint returning only position IDs (minimal payload).

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| use_cache | boolean | false | Use cached data |
| account_ids | string | null | Comma-separated account IDs |
| account_name | string | PAAPEX2666680000001 | Account name |

**Response:**
```json
{
  "position_ids": ["12345", "12346"],
  "count": 2,
  "cached": false,
  "timestamp": 1737488400.123
}
```

**Response Time:** <50ms

---

### 4. Get Pending Orders

**Endpoint:** `GET /api/v1/trading/orders/pending`

**Description:** Retrieve all pending orders (Working, Pending, Queued status).

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| use_cache | boolean | false | Use cached data |
| account_ids | string | null | Comma-separated account IDs |
| account_name | string | PAAPEX2666680000001 | Account name |

**Response:**
```json
{
  "orders": [
    {
      "order_id": "98765",
      "account_id": "D17158695",
      "instrument": "MNQZ5",
      "side": "Buy",
      "quantity": 1,
      "price": 21000.00,
      "status": "Working",
      "order_type": "Limit"
    }
  ],
  "count": 1,
  "cached": false,
  "timestamp": 1737488400.123
}
```

**Cache TTL:** 1 second  
**Response Time:** <100ms (cached), <1000ms (fresh)

---

### 5. Get Pending Order IDs Only

**Endpoint:** `GET /api/v1/trading/orders/pending/ids`

**Description:** Ultra-fast endpoint returning only order IDs.

**Response:**
```json
{
  "order_ids": ["98765", "98766"],
  "count": 2,
  "cached": false,
  "timestamp": 1737488400.123
}
```

**Response Time:** <50ms

---

### 6. Get Account Balances

**Endpoint:** `GET /api/v1/trading/balances`

**Description:** Get account balances and financial state for all accounts.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| use_cache | boolean | true | Use cached data |
| account_ids | string | null | Comma-separated account IDs |
| account_name | string | PAAPEX2666680000001 | Account name |

**Response:**
```json
{
  "balances": [
    {
      "account_id": "D17158695",
      "account_name": "PAAPEX2666680000001",
      "balance": 50000.00,
      "net_liquidating_value": 50125.00,
      "cash_balance": 49800.00,
      "open_pl": 125.00,
      "realized_pl": 200.00
    }
  ],
  "total_balance": 50125.00,
  "count": 1,
  "cached": true,
  "timestamp": 1737488400.123
}
```

**Cache TTL:** 2 seconds  
**Response Time:** <100ms (cached), <1200ms (fresh)

---

### 7. Get Trading Snapshot (Batch)

**Endpoint:** `GET /api/v1/trading/batch/snapshot`

**Description:** Get complete trading snapshot in a single API call. Ideal for dashboard updates and bot initialization.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| include_accounts | boolean | true | Include accounts data |
| include_positions | boolean | true | Include positions data |
| include_orders | boolean | true | Include orders data |
| include_balances | boolean | true | Include balances data |
| use_cache | boolean | false | Use cached data where possible |
| account_ids | string | null | Comma-separated account IDs |
| account_name | string | PAAPEX2666680000001 | Account name |

**Response:**
```json
{
  "accounts": { /* accounts response */ },
  "positions": { /* positions response */ },
  "orders": { /* orders response */ },
  "balances": { /* balances response */ },
  "metadata": {
    "response_time_ms": 1250.45,
    "timestamp": 1737488400.123,
    "datetime": "2025-01-21T20:00:00.000000"
  }
}
```

**Response Time:** <200ms (cached), <2000ms (fresh)

---

## Max Trading Bot API

### 1. Run Max Backtest

**Endpoint:** `POST /api/v1/run-bot/max-backtest`

**Description:** Run Max trading bot in backtesting mode with historical data.

**Content-Type:** `multipart/form-data`

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountName | string | Yes | Trading account name |
| mode | string | Yes | Trading mode (always "backtesting") |
| contract | string | Yes | Contract symbol (NQ, ES, etc.) |
| maxMode | string | Yes | Max mode (long, short, both) |
| point_key | string | Yes | Point strategy key (e.g., "15_7_5_2") |
| exit_strategy_key | string | Yes | Exit strategy key (e.g., "15_15") |
| notes | string | No | Optional notes |
| dateFrom | string | No* | Start date (YYYY-MM-DD) |
| dateTo | string | No* | End date (YYYY-MM-DD) |
| file | file | No* | CSV file with tick data |

*Either provide `file` OR both `dateFrom` and `dateTo`

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/run-bot/max-backtest" \
  -F "accountName=APEX_136189" \
  -F "mode=backtesting" \
  -F "contract=NQ" \
  -F "maxMode=both" \
  -F "point_key=15_7_5_2" \
  -F "exit_strategy_key=15_15" \
  -F "dateFrom=2025-01-01" \
  -F "dateTo=2025-01-21" \
  -F "notes=Test backtest"
```

**Response:**
```json
{
  "result": {
    "total_trades": 45,
    "winning_trades": 28,
    "losing_trades": 17,
    "win_rate": 0.622,
    "total_profit": 1250.50,
    "max_drawdown": -450.25
  },
  "trades": [
    {
      "entry_time": "2025-01-01T09:30:00",
      "entry_price": 21000.00,
      "exit_time": "2025-01-01T10:15:00",
      "exit_price": 21025.50,
      "profit": 25.50,
      "side": "long"
    }
  ],
  "meta": {
    "source": "date_range",
    "dateFrom": "2025-01-01",
    "dateTo": "2025-01-21",
    "accountName": "APEX_136189",
    "mode": "backtesting",
    "notes": "Test backtest"
  }
}
```

---

### 2. Run Max Live Trading

**Endpoint:** `POST /api/v1/run-bot/max`

**Description:** Run Max trading bot in live trading mode.

**Content-Type:** `multipart/form-data`

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| accountName | string | No | Main account (default: APEX_136189) |
| contract | string | Yes | Contract to trade (NQ, ES) |
| maxMode | string | Yes | Max mode value |
| trading_mode | string | Yes | Trading mode (long, short, both) |
| trading_side | string | Yes | Trading side |
| point_strategy_key | string | No | Point strategy (default: "15_7_5_2") |
| exit_strategy_key | string | No | Exit strategy (default: "15_15") |
| quantity | integer | No | Quantity (default: 1) |
| environment | string | Yes | DEMO or LIVE |
| accounts_ids | string | No | JSON array of account IDs |
| notes | string | No | Optional notes |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/run-bot/max" \
  -F "accountName=APEX_136189" \
  -F "contract=NQ" \
  -F "trading_mode=both" \
  -F "trading_side=both" \
  -F "quantity=1" \
  -F "environment=DEMO" \
  -F 'accounts_ids=[{"tv_id":"D18156785","ta_id":"PAAPEX1361890000010"}]'
```

**Response:**
```json
{
  "status": "running",
  "bot_id": "max-001",
  "config": { /* run configuration */ },
  "message": "Max bot started successfully"
}
```

---

## Data Upload API

### 1. Upload Tick Data

**Endpoint:** `POST /api/upload-tick-data`

**Description:** Upload tick data CSV with real-time progress streaming (Server-Sent Events).

**Content-Type:** `multipart/form-data`

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| file | file | Yes* | CSV/TXT file (max 300MB) |
| file_path | string | Yes* | File path (alternative to file) |
| instrument | string | Yes | Instrument symbol (ES or NQ) |
| has_header | boolean | No | CSV has header row (default: true) |
| skip_duplicates | boolean | No | Skip duplicate records (default: true) |
| supabase_target | string | No | Target (default: selfhosted) |

*Either `file` or `file_path` required

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/upload-tick-data" \
  -F "file=@/path/to/tick-data.csv" \
  -F "instrument=NQ" \
  -F "has_header=true" \
  -F "skip_duplicates=true"
```

**Response (Server-Sent Events):**
```
data: {"status":"started","message":"Upload started"}

data: {"status":"progress","batch":1,"uploaded":1000,"skipped":0}

data: {"status":"progress","batch":2,"uploaded":2000,"skipped":5}

data: {"status":"completed","success":true,"total_rows":10000,"uploaded_rows":9995,"skipped_rows":5,"duration":"45.2s"}
```

**Supported Instruments:** ES, NQ  
**Max File Size:** 300MB  
**File Formats:** CSV, TXT

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message description",
  "status_code": 400
}
```

### Common HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable (Redis/Broker down) |

---

## Rate Limiting

**Current Status:** No rate limiting implemented

**Planned Limits:**
- HFT endpoints: 1000 req/minute per IP
- Batch endpoints: 100 req/minute per IP
- Upload endpoints: 10 req/hour per IP

---

## Best Practices

1. **Use caching for non-critical data** - Set `use_cache=true` for accounts and balances
2. **Disable cache for real-time data** - Set `use_cache=false` for positions and orders
3. **Use batch endpoints** - `/batch/snapshot` reduces network overhead
4. **Use ID-only endpoints** - Faster response times for quick checks
5. **Handle 503 errors** - Implement retry logic with exponential backoff
6. **Monitor response times** - Alert if response time > 2000ms

---

## Support

For API issues or questions:
- Check `/api/v1/trading/health` for system status
- Review error logs in `/logs/` directory
- Contact development team
