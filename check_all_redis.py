#!/usr/bin/env python3
import os
import redis

def get_redis_client():
    try:
        REDIS_HOST = "redismanager.redis.cache.windows.net"
        REDIS_PORT = 6380
        REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')  # Set REDIS_PASSWORD environment variable
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            ssl=True,
            ssl_cert_reqs=None,
            decode_responses=True
        )
        r.ping()
        return r
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None

def main():
    print("🔍 COMPLETE REDIS INSPECTION")
    print("=" * 50)
    
    redis_client = get_redis_client()
    if not redis_client:
        return
    
    # Get ALL keys
    all_keys = redis_client.keys('*')
    print(f"📊 Total keys in Redis: {len(all_keys)}")
    
    # Categorize keys
    token_keys = [k for k in all_keys if k.startswith('token:')]
    auth_keys = [k for k in all_keys if k.startswith('auth:')]
    username_keys = [k for k in all_keys if k.startswith('APEX_')]
    other_keys = [k for k in all_keys if not any(k.startswith(prefix) for prefix in ['token:', 'auth:', 'APEX_'])]
    
    print(f"🔑 Token keys: {len(token_keys)}")
    print(f"🔐 Auth keys: {len(auth_keys)}")
    print(f"👤 Username keys: {len(username_keys)}")
    print(f"📦 Other keys: {len(other_keys)}")
    
    print("\n🔑 ALL TOKEN KEYS:")
    for key in sorted(token_keys):
        ttl = redis_client.ttl(key)
        print(f"  {key} (TTL: {ttl}s)")
    
    print("\n🔐 ALL AUTH KEYS:")
    for key in sorted(auth_keys):
        ttl = redis_client.ttl(key)
        print(f"  {key} (TTL: {ttl}s)")
    
    print("\n👤 USERNAME KEYS (Lists):")
    for key in sorted(username_keys):
        list_items = redis_client.lrange(key, 0, -1)
        print(f"  {key}: {list_items}")
    
    if other_keys:
        print("\n📦 OTHER KEYS:")
        for key in sorted(other_keys)[:10]:  # Show first 10
            key_type = redis_client.type(key)
            print(f"  {key} (type: {key_type})")
    
    # Test a specific token retrieval
    print("\n🧪 TEST TOKEN RETRIEVAL:")
    test_key = "token:APEX_136189"
    token = redis_client.get(test_key)
    if token:
        print(f"✅ Successfully retrieved {test_key}")
        print(f"   Length: {len(token)} characters")
        print(f"   Preview: {token[:50]}...")
    else:
        print(f"❌ Could not retrieve {test_key}")

if __name__ == "__main__":
    main()
