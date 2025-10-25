# Redis Operations Reference

Complete reference for Redis cache operations used in ORCA Trading System.

**Host:** `redismanager.redis.cache.windows.net`  
**Port:** `6380` (SSL/TLS)  
**Protocol:** Redis 6.x with SSL  
**Client Library:** redis-py (Python), deno-redis (TypeScript/Deno)

---

## Table of Contents

- [Connection Configuration](#connection-configuration)
- [Token Management](#token-management)
- [HFT Cache Operations](#hft-cache-operations)
- [Price Data Storage](#price-data-storage)
- [Common Operations](#common-operations)
- [Utility Scripts](#utility-scripts)

---

## Connection Configuration

### Python Connection

```python
import redis
import os

# Standard connection
redis_client = redis.Redis(
    host='redismanager.redis.cache.windows.net',
    port=6380,
    password=os.getenv('REDIS_PASSWORD'),
    ssl=True,
    ssl_cert_reqs=None,
    decode_responses=True,
    socket_keepalive=True,
    socket_connect_timeout=5
)

# Test connection
try:
    redis_client.ping()
    print("✅ Redis connected")
except redis.ConnectionError as e:
    print(f"❌ Redis connection failed: {e}")
```

### Using Helper Function

```python
from app.services.orca_redis.client import get_redis_client

redis_client = get_redis_client()
if redis_client:
    # Use redis_client for operations
    token = redis_client.get('token:APEX_266668')
```

### Deno/TypeScript Connection

```typescript
import { connect } from 'https://deno.land/x/redis@v0.31.0/mod.ts';

const redis = await connect({
  hostname: 'redismanager.redis.cache.windows.net',
  port: 6380,
  password: Deno.env.get('REDIS_PASSWORD'),
  tls: true,
});

// Test connection
const pong = await redis.ping();
console.log('Redis connected:', pong);
```

### Connection Pool Settings

```python
import redis

pool = redis.ConnectionPool(
    host='redismanager.redis.cache.windows.net',
    port=6380,
    password=os.getenv('REDIS_PASSWORD'),
    ssl=True,
    max_connections=10,
    socket_keepalive=True,
    socket_connect_timeout=5,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=pool)
```

---

## Token Management

### Key Naming Convention

**Pattern:** `token:{ACCOUNT_NAME}`

**Examples:**
- `token:APEX_266668`
- `token:APEX_272045`
- `token:APEX_136189`
- `token:APEX_265995`
- `token:PAAPEX2666680000001`

### 1. Get Token

**Redis Command:** `GET token:{ACCOUNT_NAME}`

**Python:**
```python
# Get token
token = redis_client.get('token:APEX_266668')

if token:
    print(f"Token: {token[:20]}...")
else:
    print("Token not found")
```

**Returns:** JWT access token string or `None`

**Use Cases:**
- Authentication for Tradovate API calls
- WebSocket connection authorization
- Trading operations

---

### 2. Store Token

**Redis Command:** `SETEX token:{ACCOUNT_NAME} {TTL} {TOKEN}`

**Python:**
```python
# Store token with 5-hour TTL
redis_client.setex(
    'token:APEX_266668',
    18000,  # 5 hours = 18000 seconds
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
)
```

**Parameters:**
- **Key:** token:{ACCOUNT_NAME}
- **TTL:** 18000 seconds (5 hours)
- **Value:** JWT token string

**Managed By:** `token_generator_and_redis_manager.py`

---

### 3. Check Token Expiration

**Redis Command:** `TTL token:{ACCOUNT_NAME}`

**Python:**
```python
# Check time to live
ttl = redis_client.ttl('token:APEX_266668')

if ttl > 0:
    hours = ttl / 3600
    print(f"Token expires in {hours:.2f} hours")
elif ttl == -1:
    print("Token has no expiration")
elif ttl == -2:
    print("Token does not exist")
```

**Returns:**
- Positive number: Seconds until expiration
- -1: Key exists but no expiration set
- -2: Key does not exist

---

### 4. Check Token Exists

**Redis Command:** `EXISTS token:{ACCOUNT_NAME}`

**Python:**
```python
# Check if token exists
exists = redis_client.exists('token:APEX_266668')

if exists:
    print("✅ Token exists")
else:
    print("❌ Token not found")
```

---

### 5. Delete Token

**Redis Command:** `DEL token:{ACCOUNT_NAME}`

**Python:**
```python
# Delete token (force refresh)
redis_client.delete('token:APEX_266668')
print("Token deleted - will be refreshed on next cycle")
```

---

### 6. Get All Tokens

**Python:**
```python
# Get all token keys
token_keys = []
for key in redis_client.scan_iter('token:*'):
    token_keys.append(key)
    token = redis_client.get(key)
    ttl = redis_client.ttl(key)
    print(f"{key}: TTL={ttl}s")

print(f"\nTotal tokens: {len(token_keys)}")
```

**Expected Tokens:**
- APEX_266668 (4 sub-accounts)
- APEX_272045 (5 sub-accounts)
- APEX_136189 (3 sub-accounts)
- APEX_265995 (1 sub-account)
- Total: ~13 tokens

---

## HFT Cache Operations

### Key Naming Convention

**Pattern:** `hft:{endpoint}:{params}`

**Examples:**
- `hft:accounts:PAAPEX2666680000001`
- `hft:positions:PAAPEX2666680000001:all`
- `hft:orders:pending:PAAPEX2666680000001:D17158695`
- `hft:balances:PAAPEX2666680000001:all`

### Cache TTL Guidelines

| Cache Type | TTL | Reason |
|------------|-----|--------|
| Accounts | 300s (5 min) | Rarely changes |
| Positions | 1s | Real-time data needed |
| Orders | 1s | Real-time data needed |
| Balances | 2s | Near real-time |

---

### 1. Cache Account Data

**Python:**
```python
import json

# Prepare data
accounts_data = {
    "accounts": [
        {"name": "PAAPEX2666680000001", "id": "D17158695", "active": True}
    ],
    "count": 1,
    "cached": False,
    "timestamp": time.time()
}

# Store in cache
cache_key = 'hft:accounts:PAAPEX2666680000001'
redis_client.setex(
    cache_key,
    300,  # 5 minutes
    json.dumps(accounts_data)
)
```

---

### 2. Retrieve Cached Data

**Python:**
```python
import json

# Get from cache
cache_key = 'hft:accounts:PAAPEX2666680000001'
cached_data = redis_client.get(cache_key)

if cached_data:
    data = json.loads(cached_data)
    print(f"✅ Cache hit - {data['count']} accounts")
else:
    print("❌ Cache miss - fetch from API")
```

---

### 3. Clear Cache

**Python:**
```python
# Clear specific cache
redis_client.delete('hft:accounts:PAAPEX2666680000001')

# Clear all HFT cache
for key in redis_client.scan_iter('hft:*'):
    redis_client.delete(key)
    print(f"Deleted: {key}")
```

---

### 4. Cache Statistics

**Python:**
```python
# Get cache statistics
def get_cache_stats():
    stats = {
        'accounts': 0,
        'positions': 0,
        'orders': 0,
        'balances': 0,
        'total': 0
    }
    
    for key in redis_client.scan_iter('hft:*'):
        stats['total'] += 1
        if 'accounts' in key:
            stats['accounts'] += 1
        elif 'positions' in key:
            stats['positions'] += 1
        elif 'orders' in key:
            stats['orders'] += 1
        elif 'balances' in key:
            stats['balances'] += 1
    
    return stats

stats = get_cache_stats()
print(f"Cache Stats: {stats}")
```

---

## Price Data Storage

### Key Naming Convention

**Pattern:** `price:{symbol}:latest`

**Example:** `price:MNQZ5:latest`

### 1. Store Latest Price

**Python:**
```python
import json
import time

# Prepare price data
price_data = {
    "Last": 21000.25,
    "Bid": 21000.00,
    "Ask": 21000.50,
    "Volume": 12345,
    "High": 21100.00,
    "Low": 20950.00,
    "Timestamp": int(time.time() * 1000)
}

# Store with short TTL (5 seconds)
redis_client.setex(
    'price:MNQZ5:latest',
    5,
    json.dumps(price_data)
)
```

---

### 2. Get Latest Price

**Python:**
```python
import json

# Get latest price
price_json = redis_client.get('price:MNQZ5:latest')

if price_json:
    price_data = json.loads(price_json)
    print(f"Last: ${price_data['Last']:.2f}")
    print(f"Bid: ${price_data['Bid']:.2f}")
    print(f"Ask: ${price_data['Ask']:.2f}")
else:
    print("Price data not available")
```

---

### 3. Stream Price Updates

**Python:**
```python
import time
import json

def stream_prices(symbol, interval=1):
    """Stream price updates from Redis"""
    while True:
        price_json = redis_client.get(f'price:{symbol}:latest')
        if price_json:
            price_data = json.loads(price_json)
            print(f"{symbol}: ${price_data['Last']:.2f} | "
                  f"Bid: ${price_data['Bid']:.2f} | "
                  f"Ask: ${price_data['Ask']:.2f}")
        time.sleep(interval)

# Usage
stream_prices('MNQZ5', interval=1)
```

---

## Common Operations

### 1. List All Keys

**Python:**
```python
# Get all keys (development only - use SCAN in production)
all_keys = redis_client.keys('*')
print(f"Total keys: {len(all_keys)}")

# Better: Use SCAN (non-blocking)
keys = []
for key in redis_client.scan_iter('*'):
    keys.append(key)
print(f"Total keys: {len(keys)}")
```

**Warning:** `KEYS *` blocks Redis. Always use `SCAN` in production!

---

### 2. Get Key Type

**Python:**
```python
# Check key type
key_type = redis_client.type('token:APEX_266668')
print(f"Key type: {key_type}")  # Output: string
```

---

### 3. Set Key with No Expiration

**Python:**
```python
# Store without expiration
redis_client.set('persistent:config', 'some_value')

# Later add expiration
redis_client.expire('persistent:config', 3600)
```

---

### 4. Atomic Increment

**Python:**
```python
# Increment counter
redis_client.incr('counter:api_calls')

# Increment by specific amount
redis_client.incrby('counter:api_calls', 10)

# Get counter value
count = redis_client.get('counter:api_calls')
print(f"API calls: {count}")
```

---

### 5. Batch Operations

**Python:**
```python
# Use pipeline for batch operations
pipe = redis_client.pipeline()

# Queue multiple operations
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.setex('key3', 60, 'value3')
pipe.get('key1')

# Execute all at once
results = pipe.execute()
print(f"Results: {results}")
```

---

### 6. Pattern Matching

**Python:**
```python
# Find all account tokens
for key in redis_client.scan_iter('token:APEX_*'):
    print(key)

# Find all position caches
for key in redis_client.scan_iter('hft:positions:*'):
    print(key)

# Count keys by pattern
token_count = len(list(redis_client.scan_iter('token:*')))
print(f"Total tokens: {token_count}")
```

---

## Utility Scripts

### 1. Check All Redis Keys

**Script:** `check_all_redis.py`

**Usage:**
```bash
python check_all_redis.py
```

**Output:**
```
Redis Connection: ✅ Connected
================================

Token Keys:
-----------
token:APEX_266668 | TTL: 14523s (4.03h) | ✅ Valid
token:APEX_272045 | TTL: 14890s (4.14h) | ✅ Valid
token:APEX_136189 | TTL: 15123s (4.20h) | ✅ Valid

HFT Cache Keys:
--------------
hft:accounts:PAAPEX2666680000001 | TTL: 245s
hft:positions:PAAPEX2666680000001:all | TTL: 0s
hft:orders:pending:PAAPEX2666680000001 | TTL: 0s

Total Keys: 25
```

---

### 2. Get All Accounts from Redis

**Script:** `get_all_accounts_from_redis.py`

**Usage:**
```bash
python get_all_accounts_from_redis.py
```

**Functionality:**
- Retrieves all tokens from Redis
- Tests connectivity to Tradovate API
- Fetches account details for each token
- Displays account mapping

---

### 3. Token Generator and Manager

**Script:** `token_generator_and_redis_manager.py`

**Usage:**
```bash
# Run once
python token_generator_and_redis_manager.py

# Run as daemon (recommended)
nohup python token_generator_and_redis_manager.py &
```

**Functionality:**
- Authenticates with Tradovate (all APEX accounts)
- Generates fresh JWT tokens
- Stores in Redis with 5-hour TTL
- Auto-refreshes every hour
- Monitors token health

**Accounts Managed:**
- APEX_266668 (4 accounts)
- APEX_272045 (5 accounts)
- APEX_136189 (3 accounts)
- APEX_265995 (1 account)

---

### 4. Sync Tokens to Supabase

**Script:** `sync_tokens_to_supabase.py`

**Usage:**
```bash
python sync_tokens_to_supabase.py
```

**Functionality:**
- Reads tokens from Redis
- Backs up to Supabase database
- Maintains token history
- Useful for audit trail

---

## Best Practices

### 1. Connection Management

```python
# ✅ Good: Use connection pool
from app.services.orca_redis.client import get_redis_client
redis_client = get_redis_client()

# ❌ Bad: Create new connection each time
redis_client = redis.Redis(host='...', port=6380)
```

### 2. Error Handling

```python
try:
    token = redis_client.get('token:APEX_266668')
except redis.ConnectionError:
    logger.error("Redis connection failed")
    token = None
except redis.TimeoutError:
    logger.error("Redis timeout")
    token = None
```

### 3. Use SCAN Instead of KEYS

```python
# ✅ Good: Non-blocking SCAN
for key in redis_client.scan_iter('token:*'):
    process_key(key)

# ❌ Bad: Blocking KEYS (only use in development)
keys = redis_client.keys('token:*')
```

### 4. Set Appropriate TTLs

```python
# Real-time data: 1-5 seconds
redis_client.setex('price:MNQZ5:latest', 5, data)

# Frequently changing: 1-2 seconds
redis_client.setex('hft:positions:*', 1, data)

# Rarely changing: 5 minutes
redis_client.setex('hft:accounts:*', 300, data)

# Tokens: 5 hours
redis_client.setex('token:*', 18000, token)
```

### 5. JSON Serialization

```python
import json

# ✅ Good: Serialize complex objects
data = {"key": "value", "nested": {"a": 1}}
redis_client.set('mykey', json.dumps(data))
retrieved = json.loads(redis_client.get('mykey'))

# ❌ Bad: Store Python objects directly
redis_client.set('mykey', str(data))  # Loses type information
```

---

## Performance Tips

1. **Use Pipelining:** Batch multiple operations
2. **Connection Pooling:** Reuse connections
3. **Appropriate TTLs:** Reduce memory usage
4. **Use SCAN:** Don't block with KEYS
5. **Monitor Memory:** Track Redis memory usage

---

## Monitoring

### Memory Usage

```python
# Get memory stats
info = redis_client.info('memory')
print(f"Used Memory: {info['used_memory_human']}")
print(f"Max Memory: {info['maxmemory_human']}")
```

### Connection Stats

```python
# Get client list
clients = redis_client.client_list()
print(f"Active connections: {len(clients)}")
```

### Key Statistics

```python
# Get database stats
db_info = redis_client.info('keyspace')
print(f"Database info: {db_info}")
```

---

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to Redis

**Solutions:**
1. Check REDIS_PASSWORD environment variable
2. Verify SSL is enabled (`ssl=True`)
3. Check network connectivity to Azure
4. Verify port 6380 is accessible

### Token Not Found

**Problem:** Token retrieval returns None

**Solutions:**
1. Check if token_generator_and_redis_manager.py is running
2. Verify token key name (case-sensitive)
3. Check token TTL (may have expired)
4. Manually refresh tokens

### Memory Issues

**Problem:** Redis running out of memory

**Solutions:**
1. Set appropriate TTLs on all keys
2. Clear old cache data
3. Increase Redis memory limit
4. Implement eviction policy

---

## Support

**Redis Documentation:** https://redis.io/documentation  
**redis-py Documentation:** https://redis-py.readthedocs.io/  
**Azure Redis Cache:** https://docs.microsoft.com/azure/azure-cache-for-redis/
