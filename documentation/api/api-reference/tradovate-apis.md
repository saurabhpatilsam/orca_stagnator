# Tradovate APIs Reference

Complete reference for Tradovate Trading API endpoints used in ORCA Trading System.

**Demo Base URL:** `https://tv-demo.tradovateapi.com`  
**Live Base URL:** `https://tv-live.tradovateapi.com`  
**REST API URL:** `https://demo.tradovateapi.com/v1` (demo) | `https://live.tradovateapi.com/v1` (live)  
**WebSocket URL:** `wss://md-demo.tradovateapi.com/v1/websocket` (demo)

**Authentication:** Bearer Token (JWT)  
**Token Storage:** Redis (`token:{ACCOUNT_NAME}`)  
**Token TTL:** 5 hours (18000 seconds)

---

## Table of Contents

- [Authentication](#authentication)
- [Account Management](#account-management)
- [Order Management](#order-management)
- [Position Management](#position-management)
- [Market Data](#market-data)
- [WebSocket Connection](#websocket-connection)
- [Error Handling](#error-handling)

---

## Authentication

### 1. Authorize (Trading View)

**Endpoint:** `GET /authorize?locale=en`

**Description:** Authorize Trading View integration. Returns access token for TV platform.

**Headers:**
```
Authorization: Bearer {TV_ACCESS_TOKEN}
```

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/authorize?locale=en" \
  -H "Authorization: Bearer YOUR_TV_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userId": 12345,
    "userName": "APEX_266668",
    "expirationTime": "2025-01-21T20:00:00.000Z"
  }
}
```

**Token Sources:**
- Redis: `token:APEX_266668`, `token:APEX_272045`, `token:APEX_136189`, `token:APEX_265995`
- Individual account tokens: `token:PAAPEX2666680000001`, etc.

---

### 2. Renew Access Token

**Endpoint:** `GET /v1/auth/renewaccesstoken`

**Description:** Renew access token using existing TV token. Returns new accessToken and mdAccessToken.

**Headers:**
```
Authorization: Bearer {TV_ACCESS_TOKEN}
Accept: application/json
```

**Example Request:**
```bash
curl -X GET "https://demo.tradovateapi.com/v1/auth/renewaccesstoken" \
  -H "Authorization: Bearer YOUR_TV_TOKEN" \
  -H "Accept: application/json"
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "mdAccessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expirationTime": "2025-01-21T20:00:00.000Z",
  "userStatus": "Active",
  "userId": 12345,
  "name": "APEX User",
  "hasLive": false
}
```

**Token Types:**
- `accessToken` - For REST API calls
- `mdAccessToken` - For market data WebSocket connection

**Auto-Renewal:** Managed by `token_generator_and_redis_manager.py` (runs every hour)

---

## Account Management

### 1. Get All Accounts

**Endpoint:** `GET /accounts?locale=en`

**Description:** Get all trading accounts for the authenticated user.

**Headers:**
```
Authorization: Bearer {ACCESS_TOKEN}
```

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/accounts?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "id": "D17158695",
      "name": "PAAPEX2666680000001",
      "userId": 12345,
      "accountType": "Demo",
      "active": true,
      "clearingHouseId": 3,
      "riskCategoryId": 1,
      "autoLiqProfileId": 1,
      "marginAccountType": "Futures"
    },
    {
      "id": "D17159229",
      "name": "PAAPEX2666680000003",
      "userId": 12345,
      "accountType": "Demo",
      "active": true,
      "clearingHouseId": 3,
      "riskCategoryId": 1,
      "autoLiqProfileId": 1,
      "marginAccountType": "Futures"
    }
  ]
}
```

**Account Mapping:**
- **APEX_266668:** 4 accounts (PAAPEX2666680000001, 0003, 0004, 0005)
- **APEX_272045:** 5 accounts (PAAPEX2720450000001-0005)
- **APEX_136189:** 3 accounts (PAAPEX1361890000010, 0011, APEX13618900000118)
- **APEX_265995:** 1 account (PAAPEX2659950000005)

---

### 2. Get Account State

**Endpoint:** `GET /accounts/{accountId}/state?locale=en`

**Description:** Get account balance and financial state information.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| accountId | string | Trading account ID (e.g., D17158695) |

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/accounts/D17158695/state?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "accountId": "D17158695",
    "netLiquidatingValue": 50125.00,
    "cashBalance": 49800.00,
    "openRealizedPl": 125.00,
    "realizedPl": 200.00,
    "unrealizedPl": 125.00,
    "totalMargin": 2500.00,
    "availableMargin": 47625.00,
    "riskLevel": "Low",
    "timestamp": "2025-01-21T20:00:00.000Z"
  }
}
```

**Key Fields:**
- `netLiquidatingValue` - Total account value
- `cashBalance` - Available cash
- `openRealizedPl` - P&L from closed positions today
- `realizedPl` - Total realized P&L
- `unrealizedPl` - P&L from open positions
- `availableMargin` - Margin available for new trades

---

## Order Management

### 1. Place Order

**Endpoint:** `POST /accounts/{accountId}/orders?locale=en`

**Description:** Place a new trading order with smart type selection.

**Content-Type:** `application/x-www-form-urlencoded`

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| accountId | string | Trading account ID |

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| instrument | string | Yes | Contract symbol (e.g., MNQZ5) |
| qty | string | Yes | Quantity |
| side | string | Yes | Buy or Sell |
| type | string | Yes | Limit, Market, Stop, StopLimit |
| limitPrice | string | No* | Limit price (for Limit/StopLimit) |
| stopPrice | string | No* | Stop price (for Stop/StopLimit) |
| durationType | string | Yes | Day, GTC, IOC, FOK |
| stopLoss | string | No | Stop loss price |
| takeProfit | string | No | Take profit price |

*Required based on order type

**Example Request (Limit Order):**
```bash
curl -X POST "https://tv-demo.tradovateapi.com/accounts/D17158695/orders?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "instrument=MNQZ5&qty=1&side=Buy&type=Limit&limitPrice=21000&durationType=Day"
```

**Example Request (Stop Order with SL/TP):**
```bash
curl -X POST "https://tv-demo.tradovateapi.com/accounts/D17158695/orders?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "instrument=MNQZ5&qty=1&side=Buy&type=Stop&stopPrice=21050&durationType=Day&stopLoss=20950&takeProfit=21150"
```

**Response (Success):**
```json
{
  "s": "ok",
  "d": {
    "orderId": "98765",
    "accountId": "D17158695",
    "instrument": "MNQZ5",
    "qty": 1,
    "side": "Buy",
    "orderType": "Limit",
    "limitPrice": 21000.00,
    "status": "Working",
    "timestamp": "2025-01-21T20:00:00.000Z"
  }
}
```

**Smart Order Type Selection:**
- **Buy + Target < Market:** Limit order
- **Buy + Target > Market:** Stop order
- **Sell + Target > Market:** Limit order
- **Sell + Target < Market:** Stop order

---

### 2. Get All Orders

**Endpoint:** `GET /accounts/{accountId}/orders?locale=en`

**Description:** Get all orders for the specified account.

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/accounts/D17158695/orders?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "id": "98765",
      "accountId": "D17158695",
      "instrument": "MNQZ5",
      "qty": 1,
      "side": "Buy",
      "orderType": "Limit",
      "limitPrice": 21000.00,
      "status": "Working",
      "filledQty": 0,
      "timestamp": "2025-01-21T19:55:00.000Z"
    }
  ]
}
```

**Order Status Values:**
- `Working` - Active in order book
- `Pending` - Submitted but not yet active
- `Queued` - Waiting to be submitted
- `Filled` - Completely filled
- `Cancelled` - Cancelled by user
- `Rejected` - Rejected by exchange

---

### 3. Get Order by ID

**Endpoint:** `GET /accounts/{accountId}/orders/{orderId}?locale=en`

**Description:** Get status of a specific order.

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/accounts/D17158695/orders/98765?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "id": "98765",
    "accountId": "D17158695",
    "instrument": "MNQZ5",
    "qty": 1,
    "side": "Buy",
    "orderType": "Limit",
    "limitPrice": 21000.00,
    "status": "Working",
    "filledQty": 0,
    "avgFillPrice": 0.00,
    "timestamp": "2025-01-21T19:55:00.000Z",
    "updateTime": "2025-01-21T19:55:00.000Z"
  }
}
```

---

### 4. Update Order

**Endpoint:** `PUT /accounts/{accountId}/orders/{orderId}?locale=en`

**Description:** Update an existing order's price, quantity, or other parameters.

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Order ID to update |
| limitPrice | string | No | New limit price |
| qty | string | No | New quantity |
| durationType | string | Yes | Order duration |

**Example Request:**
```bash
curl -X PUT "https://tv-demo.tradovateapi.com/accounts/D17158695/orders/98765?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "id=98765&limitPrice=21050&qty=2&durationType=Day"
```

**Response:**
```json
{
  "s": "ok",
  "d": {
    "orderId": "98765",
    "updated": true
  }
}
```

---

### 5. Cancel Order

**Endpoint:** `DELETE /accounts/{accountId}/orders/{orderId}?locale=en`

**Description:** Cancel an order.

**Example Request:**
```bash
curl -X DELETE "https://tv-demo.tradovateapi.com/accounts/D17158695/orders/98765?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response (Success):**
```json
{
  "s": "ok"
}
```

**Response (Too Late):**
```json
{
  "s": "error",
  "errmsg": "Too late to cancel - order already filled"
}
```

---

## Position Management

### 1. Get All Positions

**Endpoint:** `GET /accounts/{accountId}/positions?locale=en`

**Description:** Get all active positions for the account.

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/accounts/D17158695/positions?locale=en" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "id": "12345",
      "accountId": "D17158695",
      "contractId": "MNQZ5",
      "timestamp": "2025-01-21T19:30:00.000Z",
      "netPos": 2,
      "avgPrice": 21000.50,
      "netPrice": 21000.50,
      "bought": 2,
      "boughtValue": 42001.00,
      "sold": 0,
      "soldValue": 0.00,
      "prevPos": 0,
      "prevPrice": 0.00,
      "unrealizedPl": 125.00
    }
  ]
}
```

**Key Fields:**
- `netPos` - Net position (positive = long, negative = short)
- `avgPrice` - Average entry price
- `unrealizedPl` - Unrealized profit/loss
- `bought` - Total quantity bought
- `sold` - Total quantity sold

---

## Market Data

### 1. Get Price Quotes

**Endpoint:** `GET /quotes?locale=en&symbols={symbols}`

**Description:** Get real-time price quotes for specified symbols.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| symbols | string | Comma-separated list of symbols |
| locale | string | Locale (default: en) |

**Example Request:**
```bash
curl -X GET "https://tv-demo.tradovateapi.com/quotes?locale=en&symbols=MNQZ5,ESH5" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "s": "ok",
  "d": [
    {
      "k": "MNQZ5",
      "v": {
        "lp": 21025.50,
        "ask": 21026.00,
        "bid": 21025.00,
        "volume": 125000,
        "high": 21100.00,
        "low": 20950.00,
        "open": 21000.00,
        "timestamp": "2025-01-21T20:00:00.000Z"
      }
    }
  ]
}
```

**Price Fields:**
- `lp` - Last price
- `ask` - Ask price
- `bid` - Bid price
- `volume` - Trading volume
- `high` - Day high
- `low` - Day low
- `open` - Opening price

---

### 2. Contract Suggest (Symbol Discovery)

**Endpoint:** `GET /v1/contract/suggest?t={symbol}`

**Description:** Discover available contracts for a symbol prefix. Used to find current front-month contracts.

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| t | string | Symbol prefix (NQ, ES, etc.) |

**Example Request:**
```bash
curl -X GET "https://demo.tradovateapi.com/v1/contract/suggest?t=NQ" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 3018319,
    "name": "MNQZ5",
    "contractMaturityId": 54,
    "status": "Verified",
    "months": "HMUZ",
    "isActive": true,
    "description": "E-mini Nasdaq-100 Dec 2025"
  },
  {
    "id": 3018320,
    "name": "MNQH6",
    "contractMaturityId": 53,
    "status": "Verified",
    "months": "HMUZ",
    "isActive": true,
    "description": "E-mini Nasdaq-100 Mar 2026"
  }
]
```

**Month Codes:**
- H = March
- M = June
- U = September
- Z = December

**Current Symbol:** MNQZ5 (Micro E-mini Nasdaq, December 2025)

---

## WebSocket Connection

### Connection Details

**URL:** `wss://md-demo.tradovateapi.com/v1/websocket`  
**Protocol:** SockJS over WebSocket  
**Heartbeat:** Send `[]` every 2.4 seconds

### Connection Flow

1. **Connect to WebSocket**
2. **Send Authorization:**
   ```
   authorize
   1
   
   {mdAccessToken}
   ```
3. **Wait for Authorization Response:**
   ```json
   {"s": 200, "i": 1}
   ```
4. **Subscribe to Data**

### Subscribe to Real-Time Quotes

**Message Format:**
```
md/subscribeQuote
2

{"symbol": "MNQZ5"}
```

### Get Chart Data

**Message Format:**
```
md/getChart
3

{
  "symbol": "MNQZ5",
  "chartDescription": {
    "underlyingType": "MinuteBar",
    "elementSize": 30,
    "elementSizeUnit": "UnderlyingUnits",
    "withHistogram": false
  },
  "timeRange": {
    "closestTimestamp": "2025-01-21T20:00:00Z",
    "asMuchAsElements": 10
  }
}
```

**Response:**
```json
{
  "e": "chart",
  "d": {
    "charts": [
      {
        "id": 1,
        "symbol": "MNQZ5",
        "bars": [
          {
            "timestamp": "2025-01-21T19:30:00Z",
            "open": 21000.00,
            "high": 21025.00,
            "low": 20995.00,
            "close": 21020.00,
            "upVolume": 1250,
            "downVolume": 850,
            "upTicks": 125,
            "downTicks": 85
          }
        ],
        "eoh": false
      }
    ]
  }
}
```

**Implementation:** See `supabase/functions/fetch-candles/index.ts`

---

## Error Handling

### Response Format

**Success:**
```json
{
  "s": "ok",
  "d": { /* data */ }
}
```

**Error:**
```json
{
  "s": "error",
  "errmsg": "Error description",
  "errorCode": 1001
}
```

### Common Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 1001 | Invalid token | Token expired or invalid |
| 1002 | Account not found | Invalid account ID |
| 1003 | Insufficient margin | Not enough margin for order |
| 1004 | Invalid order | Order parameters invalid |
| 1005 | Market closed | Cannot trade when market closed |

---

## Best Practices

1. **Token Management**
   - Tokens expire after 5 hours
   - Use token_generator_and_redis_manager.py for auto-renewal
   - Check TTL before making requests

2. **Order Placement**
   - Always check account state before placing orders
   - Use smart order type selection (implemented in broker.py)
   - Include stop loss and take profit for risk management

3. **Market Data**
   - Use WebSocket for real-time data
   - Cache quote data in Redis (TTL: 5 seconds)
   - Subscribe only to needed symbols

4. **Error Handling**
   - Implement retry logic with exponential backoff
   - Handle 401 errors by refreshing token
   - Log all API errors for debugging

---

## Rate Limits

**Demo Environment:**
- 100 requests per minute per account
- 10 WebSocket connections per account

**Live Environment:**
- Contact Tradovate for limits
- Higher limits available on request

---

## Support

**Tradovate Documentation:** https://api.tradovate.com/  
**Support Email:** support@tradovate.com  
**Trading Hours:** Sunday 6 PM ET - Friday 5 PM ET
