# 🔐 Token Management Flow - Broker Authentication & Redis Storage

## Overview
This document explains how trading tokens are obtained from the Tradovate broker API and stored in Redis for each username/account.

## 🏗️ Architecture Flow

```mermaid
graph TD
    A[credentials.json] --> B[Token Refresher Service]
    B --> C[Tradovate API Login]
    C --> D[Access Token Response]
    D --> E[Redis Storage]
    E --> F[Application Usage]
    
    G[Redis Key Structure] --> H[token:username]
    G --> I[auth:username]
    
    J[TTL Management] --> K[1 Hour Expiration]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#e8f5e8
```

## 📁 Key Components

### 1. **Credentials Storage** (`credentials.json`)
```json
[
  {
    "username": "APEX_272045",
    "password": "AFz222v#65Fe"
  },
  {
    "username": "APEX_136189", 
    "password": "AG@2s#6$03M1"
  },
  // ... more accounts
]
```

### 2. **Token Acquisition Process** (`credentialsmanager/client.py`)

#### 🔄 Main Flow:
1. **Load Credentials** → Read from `credentials.json`
2. **Parallel Processing** → Use ThreadPoolExecutor (10 workers)
3. **API Authentication** → Call Tradovate API for each account
4. **Redis Storage** → Store tokens with TTL

#### 🌐 API Call Details:
```python
def get_access_token(username, password):
    url = "https://tv-demo.tradovateapi.com/authorize?locale=en"
    payload = f'locale=en&login={username}&password={password}'
    
    # Returns JWT token from response.json()["d"]["access_token"]
```

### 3. **Redis Storage Strategy**

#### 📊 Key Structure:
- **Primary Keys**: `token:{username}` (e.g., `token:APEX_272045`)
- **Auth Keys**: `auth:{username}` (backup/alternative access)
- **Account Lists**: `{username}` → List of associated token keys

#### 🔧 Storage Implementation:
```python
def update_redis_tokens(redis_client, username, access_token):
    # Get list of keys associated with this username
    keys_to_update = redis_client.lrange(username, 0, -1)
    
    for key in keys_to_update:
        # Set token with 1-hour TTL
        redis_client.setex(key, TTL_SECONDS, access_token)
        redis_client.setex(f"auth:{username}", TTL_SECONDS, access_token)
```

## 🔍 Current Redis Data (Live Results)

Based on the Redis scan, here are the current tokens:

### 📋 Token Inventory:
- **Total Tokens**: 25 unique token entries
- **Unique Token Values**: 1 (all accounts share same token currently)
- **Token Length**: 215 characters (JWT format)

### 🏦 Active Accounts:
```
APEX_272045, APEX_136189, APEX_265995, APEX_266668
PAAPEX1361890000001, PAAPEX1361890000002, PAAPEX1361890000003
PAAPEX1361890000004, PAAPEX1361890000005, PAAPEX2659950000001
PAAPEX2659950000002, PAAPEX2659950000003, PAAPEX2659950000004
PAAPEX2659950000005, PAAPEX2720450000001, PAAPEX2720450000002
PAAPEX2720450000003, PAAPEX2720450000004, PAAPEX2720450000005
PAAPEX2666680000001, PAAPEX2666680000002, PAAPEX2666680000003
PAAPEX2666680000004, PAAPEX2666680000005
```

### 🎫 Sample Token (JWT):
```
eyJraWQiOiI0IiwiYWxnIjoiRWREU0EifQ.eyJzdWIiOiIzODY1NjUxIiwiZXhwIjoxNzYwNzg5NzA3LCJqdGkiOiItNDM4MjEwOTUxMjgyOTcwNTM4NC0xNjMyMDc2ODcwNDU4NzM2NDMiLCJwaHMiOjk4NTY5MzU1MH0.dh1SjFQfE2vN6aixpz3aveEb7p_ElqMfnl9V3bc16zBXmX8IM0zaduP2cS25ZtCBb5CEsMFcKQVKiRoMl2k8Dw
```

## 🔄 Token Usage in Applications

### 📖 Token Retrieval Pattern:
```python
# Standard pattern used across the codebase
redis_client = get_redis_client()
token = redis_client.get(f"token:{account_name}")

# Alternative pattern
from credentialsmanager.client import get_token_from_redis
token = get_token_from_redis(redis_client, f"token:{account_name}")
```

### 🎯 Usage Examples:

#### 1. **Trading Operations**:
```python
# In trading_api_router.py, broker.py, etc.
tv_token = redis_client.get(f"token:{account_name}")
headers = {"Authorization": f"Bearer {tv_token}"}
```

#### 2. **WebSocket Connections**:
```python
# In tradovate_websocket_working.py
self.tv_access_token = get_token_from_redis(
    redis_client, f"token:{self.account_name}"
)
```

#### 3. **Data Fetching**:
```python
# In automated_candle_fetcher.py, get_nq_realtime.py
tv_token = redis_client.get(f"token:{account_name}")
```

## ⚙️ Configuration & Management

### 🔧 Redis Connection:
```python
# From app/services/orca_redis/client.py
REDIS_HOST = "redismanager.redis.cache.windows.net"
REDIS_PORT = 6380
REDIS_PASSWORD = "[REDACTED - Use environment variable REDIS_PASSWORD]"
```

### ⏰ TTL Management:
- **Token Expiration**: 1 hour (3600 seconds)
- **Auto-Refresh**: Handled by credentials manager daemon
- **Fallback**: Multiple account tokens available

### 🚨 Error Handling:
- **Discord Alerts**: Sent on token refresh failures
- **Logging**: Comprehensive logging with loguru
- **Fallback Accounts**: Multiple accounts per user for redundancy

## 🔍 Key Files Reference:

| File | Purpose |
|------|---------|
| `tradovate-market-stream-main/credentialsmanager/client.py` | Main token management logic |
| `tradovate-market-stream-main/credentials.json` | Account credentials storage |
| `app/services/orca_redis/client.py` | Redis connection management |
| `scripts/get_trading_token_final.py` | Token retrieval utility |
| `get_all_redis_data.py` | Redis data analysis tool |

## 🎯 Postman Usage:

For API testing, use any of these authorization headers:
```
Authorization: Bearer eyJraWQiOiI0IiwiYWxnIjoiRWREU0EifQ.eyJzdWIiOiIzODY1NjUxIiwiZXhwIjoxNzYwNzg5NzA3LCJqdGkiOiItNDM4MjEwOTUxMjgyOTcwNTM4NC0xNjMyMDc2ODcwNDU4NzM2NDMiLCJwaHMiOjk4NTY5MzU1MH0.dh1SjFQfE2vN6aixpz3aveEb7p_ElqMfnl9V3bc16zBXmX8IM0zaduP2cS25ZtCBb5CEsMFcKQVKiRoMl2k8Dw
Content-Type: application/json
```
