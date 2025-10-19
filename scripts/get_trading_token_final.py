import os
from loguru import logger

def get_redis_client():
    """Create a Redis client with the working configuration"""
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
        logger.error(f"Failed to connect to Redis: {e}")
        return None

def get_trading_tokens():
    """Get all trading tokens from Redis"""
    redis_client = get_redis_client()
    if not redis_client:
        return {}
    
    # Get all token keys
    token_keys = redis_client.keys('token:*')
    tokens = {}
    
    for key in token_keys:
        account_name = key.split(':', 1)[1]
        token = redis_client.get(key)
        if token:
            tokens[account_name] = token
    
    return tokens

if __name__ == "__main__":
    print("\n" + "="*60)
    print("FETCHING TRADING TOKENS")
    print("="*60)
    
    tokens = get_trading_tokens()
    
    if tokens:
        for account, token in tokens.items():
            print("\n" + "-"*60)
            print(f"ACCOUNT: {account}")
            print("-"*60)
            print(f"TOKEN: {token}")
            print("-"*60)
            print("Sample Postman Authorization header:")
            print(f"Authorization: Bearer {token}")
        
        print("\n" + "="*60)
        print("TOKEN RETRIEVAL COMPLETE")
        print("="*60)
        print("\nUse one of these tokens in your Postman Authorization header.")
        print("Example:")
        print("  - Add header: 'Authorization: Bearer YOUR_TOKEN_HERE'")
        print("  - Make sure to include 'Content-Type: application/json'")
    else:
        print("\nNo tokens found. Please check your Redis connection and credentials.")
