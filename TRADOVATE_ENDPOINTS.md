# 📡 Tradovate API Endpoints Reference

**Complete documentation of all Tradovate API endpoints used in ORCA Trading System**

---

## 🌐 Base URLs

### Demo Environment (Current)
```
https://tv-demo.tradovateapi.com
```

### Production Environment
```
https://live.tradovateapi.com
```

---

## 🔐 Authentication

### Token Management
- **Storage:** Azure Redis Cache
- **Key Format:** `token:{account_name}`
- **Example:** `token:PAAPEX1361890000010`
- **Token Type:** JWT Bearer Token
- **Expiry:** Auto-refreshed via Redis
- **Header Format:** `Authorization: Bearer {token}`

### Authentication Flow
1. Token stored in Redis by external service
2. System retrieves fresh token from Redis for each request
3. Token included in Authorization header
4. All endpoints require valid JWT token

---

## 📊 Data Retrieval Endpoints

### 1. Get All Accounts
**Fetch all trading accounts associated with the authenticated user**

```http
GET /accounts?locale=en
```

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "id": "D18156785",
      "name": "PAAPEX1361890000010",
      "accountType": "Demo",
      "active": true
    }
  ]
}
```

**Used In:** `broker.py::get_all_accounts()`

---

### 2. Get Price Quotes
**Fetch real-time market quotes for instruments**

```http
GET /quotes?locale=en&symbols={symbol}
```

**Parameters:**
- `symbols` - Instrument symbol (e.g., MNQZ5, ESZ5)

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "s": "ok",
      "n": "MNQZ5",
      "v": {
        "lp": 24758.75,
        "bid": 24758.0,
        "ask": 24758.5,
        "high_price": 25044.5,
        "low_price": 24423.25,
        "volume": 1537274,
        "open_price": 24905.0
      }
    }
  ]
}
```

**Used In:** 
- `broker.py::get_price_quotes()`
- `broker.py::place_order()` - Auto price checking

**Usage:** Real-time price fetching before order placement for smart order type selection

---

### 3. Get Account State
**Retrieve account balance and state information**

```http
GET /accounts/{account_id}/state?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID (e.g., D18156785)

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
If-None-Match: {etag} (optional)
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "accountId": "D18156785",
    "netLiquidatingValue": 50000.00,
    "cashBalance": 48500.00,
    "openPositions": 2,
    "dayTrades": 1
  }
}
```

**Used In:** `broker.py::get_account_state()`

---

### 4. Get All Orders
**Fetch all orders for a specific account**

```http
GET /accounts/{account_id}/orders?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "orderId": "268137614455",
      "accountId": "D18156785",
      "instrument": "MNQZ5",
      "qty": 1,
      "side": "buy",
      "orderType": "Stop",
      "status": "Working",
      "stopPrice": 24900.0
    }
  ]
}
```

**Used In:** `broker.py::get_orders()`

---

### 5. Get Specific Order
**Retrieve details of a single order**

```http
GET /accounts/{account_id}/orders/{order_id}?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID
- `order_id` - Order ID to retrieve

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "orderId": "268137614455",
    "status": "Filled",
    "fillPrice": 24900.0,
    "fillTime": "2025-10-14T17:18:54Z"
  }
}
```

**Used In:** `broker.py::get_order()`

---

### 6. Get Positions
**Fetch all open positions for an account**

```http
GET /accounts/{account_id}/positions?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID

**Headers:**
```
Authorization: Bearer {token}
Accept: application/json
If-None-Match: {etag} (optional)
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "id": "12345",
      "accountId": "D18156785",
      "contractId": "MNQZ5",
      "netPos": 1,
      "avgPrice": 24900.0,
      "unrealizedPnL": 250.0
    }
  ]
}
```

**Used In:** `broker.py::get_positions()`

---

## 📤 Order Placement & Management Endpoints

### 7. Place New Order
**Submit a new order with smart order type selection**

```http
POST /accounts/{account_id}/orders?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded
```

**Request Body (URL-encoded):**

**For LIMIT Orders:**
```
instrument=MNQZ5
qty=1
side=buy
type=limit
limitPrice=24700.0
durationType=Day
stopLoss=0.0 (optional)
takeProfit=0.0 (optional)
```

**For STOP Orders:**
```
instrument=MNQZ5
qty=1
side=buy
type=stop
stopPrice=24900.0
durationType=Day
stopLoss=0.0 (optional)
takeProfit=0.0 (optional)
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "orderId": "268137614455"
  }
}
```

**Smart Order Type Logic:**
- **BUY + Target < Current:** LIMIT order (buying below market)
- **BUY + Target > Current:** STOP order (buying above market)
- **SELL + Target > Current:** LIMIT order (selling above market)
- **SELL + Target < Current:** STOP order (selling below market)

**Used In:** 
- `broker.py::place_order()`
- Auto-checks current price before placement
- Auto-selects LIMIT vs STOP based on price relationship

---

### 8. Update Existing Order
**Modify an existing order**

```http
PUT /accounts/{account_id}/orders/{order_id}?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID
- `order_id` - Order ID to update

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/x-www-form-urlencoded
```

**Request Body (URL-encoded):**
```
id={order_id}
limitPrice=24750.0 (optional)
qty=2 (optional)
stopLoss=24600.0 (optional)
takeProfit=25000.0 (optional)
durationType=Day
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "orderId": "268137614455",
    "updated": true
  }
}
```

**Used In:** `broker.py::update_order()`

---

### 9. Cancel Order
**Cancel an existing order**

```http
DELETE /accounts/{account_id}/orders/{order_id}?locale=en
```

**Path Parameters:**
- `account_id` - Trading account ID
- `order_id` - Order ID to cancel

**Headers:**
```
Authorization: Bearer {token}
```

**Response (Success):**
```json
{
  "s": "ok"
}
```

**Response (Error - Too Late):**
```json
{
  "s": "error",
  "errmsg": "Too late"
}
```

**Used In:** `broker.py::cancel_order()`

---

## 🔔 Webhooks & Integrations

### TradingView Webhook Integration

**Purpose:** Receive trading signals from TradingView alerts

**Webhook Endpoint (Our Backend):**
```
POST https://orca-ven-backend-production.up.railway.app/api/webhook/tradingview
```

**Expected Payload:**
```json
{
  "symbol": "MNQZ5",
  "action": "buy",
  "price": 24900.0,
  "quantity": 1,
  "strategy": "first_hour_breakout",
  "timestamp": "2025-10-14T17:18:54Z"
}
```

**Processing Flow:**
1. TradingView alert triggers
2. Webhook sends signal to our backend
3. Backend validates signal
4. Backend places order via Tradovate API
5. Order ID stored in Supabase
6. Status updates sent back to Supabase

**Configuration:**
- **TradingView Alert URL:** Set in TradingView alert settings
- **Authentication:** API key or token-based
- **Format:** JSON

---

### Supabase Signal Listener

**Purpose:** Monitor Supabase for new trading signals

**Supabase Table:** `trading_signals`

**Schema:**
```sql
CREATE TABLE trading_signals (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10),
  action VARCHAR(10),
  price DECIMAL(10,2),
  quantity INTEGER,
  strategy VARCHAR(50),
  status VARCHAR(20),
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Listening Process:**
1. `supabase_order_listener.py` polls Supabase every N seconds
2. Fetches new signals with `status = 'pending'`
3. Calls `order_processor.py` to place order
4. Updates status to 'processing' → 'filled' or 'error'

**Configuration:**
```python
POLL_INTERVAL = 5  # seconds
SUPABASE_URL = os.getenv("SELFHOSTED_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SELFHOSTED_SUPABASE_KEY")
```

---

## 🛠️ Common Request Headers

All Tradovate API requests use these headers:

```http
Host: tv-demo.tradovateapi.com
Connection: keep-alive
Authorization: Bearer {token}
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
Accept: application/json
Content-Type: application/x-www-form-urlencoded
Origin: https://www.tradingview.com
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.tradingview.com/
Accept-Language: en-US,en;q=0.9
```

---

## 📋 Supported Instruments

### ES - E-mini S&P 500
- **Symbol:** ESZ5 (example - Z = December contract)
- **Point Value:** $50 per point
- **Tick Size:** 0.25 points ($12.50)

### NQ - E-mini NASDAQ-100
- **Symbol:** MNQZ5 (example - MNQ = Micro, Z = December)
- **Point Value:** $20 per point (Micro)
- **Tick Size:** 0.25 points ($5)

---

## 🔄 Order Types

### LIMIT Order
- **Use Case:** Enter at specific price or better
- **BUY LIMIT:** Execute at limit price or lower
- **SELL LIMIT:** Execute at limit price or higher

### STOP Order
- **Use Case:** Enter when price breaks level
- **BUY STOP:** Execute when price rises to stop price
- **SELL STOP:** Execute when price falls to stop price

### Market Order
- **Use Case:** Immediate execution at current market price
- **Risk:** Slippage in fast-moving markets

---

## ⚠️ Error Codes

### Common HTTP Status Codes

| Code | Meaning | Cause | Solution |
|------|---------|-------|----------|
| 200 | Success | Request completed | N/A |
| 400 | Bad Request | Invalid parameters | Check payload format |
| 401 | Unauthorized | Invalid/expired token | Refresh token from Redis |
| 404 | Not Found | Invalid endpoint or resource | Verify endpoint path |
| 429 | Rate Limited | Too many requests | Implement backoff |
| 500 | Server Error | Tradovate internal error | Retry after delay |

### API Response Status

```json
{
  "s": "ok",        // Success
  "d": {...}        // Data
}
```

```json
{
  "s": "error",     // Error
  "errmsg": "..."   // Error message
}
```

---

## 📊 Rate Limits

**Tradovate API Rate Limits:**
- **Demo Environment:** ~100 requests/minute
- **Production Environment:** Varies by account type
- **Recommendation:** Implement exponential backoff

---

## 🔗 API Documentation Links

- **Tradovate Official API Docs:** https://api.tradovate.com/
- **TradingView Webhooks:** https://www.tradingview.com/support/solutions/43000529348-i-want-to-know-more-about-webhooks/
- **Support:** support@tradovate.com

---

## 📝 Code References

### Main Implementation
- `app/services/tradingview/broker.py` - TradingViewTradovateBroker class
- `automated_trading/order_processor.py` - Order execution logic
- `automated_trading/supabase_order_listener.py` - Signal monitoring

### Test Scripts
- `tests/test_order_placement.py` - Order placement tests
- `tests/place_order_production.py` - Production order script

---

**Last Updated:** 2025-10-15  
**Version:** 1.0.0  
**Status:** ✅ All Endpoints Documented
