#!/usr/bin/env python3
import os
import redis

def get_redis_client():
    try:
        r = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'redismanager.redis.cache.windows.net'),
            port=int(os.environ.get('REDIS_PORT', 6380)),
            password=os.environ.get('REDIS_PASSWORD', ''),  # Must set REDIS_PASSWORD environment variable
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
    print("🔑 RETRIEVING ALL TOKENS FROM REDIS")
    print("=" * 50)
    
    redis_client = get_redis_client()
    if not redis_client:
        return
    
    # Get all token keys
    token_keys = redis_client.keys('token:*')
    print(f"Found {len(token_keys)} token keys\n")
    
    # Group by account type
    main_accounts = []
    sub_accounts = []
    
    for key in sorted(token_keys):
        token = redis_client.get(key)
        ttl = redis_client.ttl(key)
        
        account_name = key.replace('token:', '')
        
        if account_name.startswith('APEX_'):
            main_accounts.append((account_name, token, ttl))
        else:
            sub_accounts.append((account_name, token, ttl))
    
    print("🏦 MAIN ACCOUNTS:")
    print("-" * 50)
    for account, token, ttl in main_accounts:
        print(f"Account: {account}")
        print(f"Token:   {token}")
        print(f"TTL:     {ttl} seconds")
        print(f"Postman: Authorization: Bearer {token}")
        print()
    
    print("🔗 SUB-ACCOUNTS:")
    print("-" * 50)
    for account, token, ttl in sub_accounts[:10]:  # Show first 10
        print(f"Account: {account}")
        print(f"Token:   {token[:50]}...")
        print(f"TTL:     {ttl} seconds")
        print()
    
    if len(sub_accounts) > 10:
        print(f"... and {len(sub_accounts) - 10} more sub-accounts")

if __name__ == "__main__":
    main()
