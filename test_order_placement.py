import os
import requests
import json
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TRADING_API_BASE = os.getenv("TRADING_API_BASE", "https://tv-demo.tradovateapi.com")
ACCOUNT_ID = os.getenv("TRADING_ACCOUNT_ID", "PAAPEX1361890000002")  # Default to one of the accounts we found
TOKEN = os.getenv("TRADING_API_TOKEN")  # We'll set this from the token we found

def place_order(order_data, account_id=None, token=None):
    """Place an order using the trading API"""
    if not account_id:
        account_id = ACCOUNT_ID
    if not token:
        token = TOKEN
    
    if not token:
        logger.error("No trading API token provided")
        return None
    
    url = f"{TRADING_API_BASE}/accounts/{account_id}/orders?locale=en"
    
    # Headers matching TradingViewTradovateBroker._make_request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/",
        "Sec-Ch-Ua": '"Google Chrome";v="94", "Chromium";v="94", ";Not A Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
    
    try:
        logger.info(f"Placing order to {url}")
        logger.info(f"Order data: {json.dumps(order_data, indent=2)}")
        
        # Convert the data to URL-encoded format
        from urllib.parse import urlencode
        
        # Ensure all values are strings
        encoded_data = {}
        for key, value in order_data.items():
            if value is not None:
                encoded_data[key] = str(value)
        
        payload = urlencode(encoded_data)
        logger.debug(f"URL-encoded payload: {payload}")
        
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        logger.success(f"Order placed successfully: {json.dumps(result, indent=2)}")
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                error_msg = f"{e}: {error_details}"
            except:
                error_msg = f"{e}: {e.response.text}"
        
        logger.error(f"Failed to place order: {error_msg}")
        return {"s": "error", "errmsg": error_msg}

def test_market_order():
    """Test placing a market order"""
    order_data = {
        "instrument": "MNQZ5",
        "qty": "1",
        "side": "buy",
        "type": "market",
        "stopLoss": "0",
        "takeProfit": "0",
        "durationType": "Day"
    }
    
    print("\n" + "="*60)
    print("TESTING MARKET ORDER")
    print("="*60)
    return place_order(order_data)

def test_limit_order(account_id=None):
    """Test placing a limit order"""
    # Example price, in a real scenario you'd fetch the current price
    current_price = 15000.00
    
    # Format according to TradingViewTradovateBroker implementation
    order_data = {
        "instrument": "MNQZ5",
        "qty": "1",  # Note: as string
        "side": "buy",  # lowercase
        "type": "limit",  # lowercase
        "limitPrice": f"{current_price * 0.95:.2f}",  # 5% below current price
        "stopLoss": "0",  # Required but can be 0 if not used
        "takeProfit": "0",  # Required but can be 0 if not used
        "durationType": "Day"
    }
    
    print("\n" + "="*60)
    print("TESTING LIMIT ORDER")
    print("="*60)
    return place_order(order_data)

def decode_token(token):
    """Decode JWT token to inspect its contents"""
    import jwt
    try:
        # Decode without verification to see the payload
        decoded = jwt.decode(token, options={"verify_signature": False})
        logger.info("Token details:")
        logger.info(f"  Issuer: {decoded.get('iss', 'N/A')}")
        logger.info(f"  Subject: {decoded.get('sub', 'N/A')}")
        logger.info(f"  Expires at: {decoded.get('exp', 'N/A')}")
        logger.info(f"  Issued at: {decoded.get('iat', 'N/A')}")
        logger.info(f"  Account: {decoded.get('phs', 'N/A')}")
        return decoded
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None

def list_all_tokens():
    """List all available tokens in Redis"""
    try:
        from app.services.orca_redis.client import get_redis_client
        redis_client = get_redis_client()
        if not redis_client:
            logger.error("Failed to connect to Redis")
            return {}
        
        tokens = {}
        # Scan for all keys that might contain tokens
        for key in redis_client.scan_iter("*token*"):
            try:
                # Handle both bytes and string keys
                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                token = redis_client.get(key)
                
                if token:
                    # Handle both bytes and string tokens
                    token_str = token.decode('utf-8') if isinstance(token, bytes) else token
                    
                    tokens[key_str] = {
                        'token': token_str[:10] + '...' + token_str[-10:] if len(token_str) > 20 else token_str,
                        'length': len(token_str),
                        'full_token': token_str  # Store the full token for later use
                    }
            except Exception as e:
                logger.warning(f"Error processing key {key}: {e}")
                continue
                
        return tokens
    except Exception as e:
        logger.error(f"Error listing tokens from Redis: {e}")
        return {}

def safe_get_token(redis_client, key):
    """Safely get a token from Redis, handling both string and bytes"""
    try:
        token = redis_client.get(key)
        if token is None:
            return None
            
        # Handle both bytes and string tokens
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return str(token)
    except Exception as e:
        logger.warning(f"Error getting token for key {key}: {e}")
        return None

def get_fresh_token(account_name=None, token_key=None):
    """Get a fresh JWT token from Redis
    
    Args:
        account_name: Specific account name to get token for (e.g., 'PAAPEX1361890000002')
        token_key: Specific token key to get (e.g., 'order_token:PAAPEX1361890000002')
    """
    try:
        from app.services.orca_redis.client import get_redis_client
        redis_client = get_redis_client()
        if not redis_client:
            logger.error("Failed to connect to Redis")
            return None
            
        # If a specific token key is provided, try to get that token
        if token_key:
            token = safe_get_token(redis_client, token_key)
            if token:
                logger.info(f"Found token with key: {token_key}")
                decode_token(token)
                return token
            else:
                logger.error(f"No token found with key: {token_key}")
                return None
                
        # If a specific account name is provided, try to get a token for that account
        if account_name:
            # Try different key patterns for this account
            possible_keys = [
                f"token:{account_name}",
                f"order_token:{account_name}",
                f"auth_token:{account_name}",
                f"trading_token:{account_name}",
                f"{account_name}:token",
                account_name  # Sometimes the account name itself is the key
            ]
            
            for key in possible_keys:
                token = safe_get_token(redis_client, key)
                if token:
                    logger.info(f"Found token with key: {key}")
                    decode_token(token)
                    return token
            
            logger.error(f"No token found for account: {account_name}")
            return None
            
        # If no specific account or token key is provided, try to find any token
        logger.info("No specific account or token key provided, searching for any token...")
        
        # Try different patterns to find tokens
        token_patterns = [
            "token:*",
            "*_token:*",
            "*:token*",
            "*token*"  # Catch-all pattern as last resort
        ]
        
        for pattern in token_patterns:
            try:
                for key in redis_client.scan_iter(pattern):
                    # Handle both bytes and string keys
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                    
                    # Skip keys we've already tried
                    if key_str.startswith('__') or ':' not in key_str:
                        continue
                        
                    token = safe_get_token(redis_client, key)
                    if token:
                        logger.info(f"Found token with key: {key_str}")
                        decode_token(token)
                        return token
            except Exception as e:
                logger.warning(f"Error scanning with pattern '{pattern}': {e}")
                continue
        
        logger.error("No tokens found in Redis")
        return None
        
    except Exception as e:
        logger.error(f"Error in get_fresh_token: {e}")
        return None

def get_account_info(token):
    """Get account information using the provided token"""
    url = f"{TRADING_API_BASE}/accounts?locale=en"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Origin": "https://www.tradingview.com",
        "Referer": "https://www.tradingview.com/",
    }
    
    try:
        logger.info(f"Fetching account information from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Account information: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch account information: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return None

def test_token_with_operation(token, operation_name, operation_func, *args, **kwargs):
    """Test a token with a specific operation and return the result"""
    print(f"\nTesting token with {operation_name} operation...")
    try:
        result = operation_func(*args, **kwargs, token=token)
        print(f"✅ Success with {operation_name} using token: {token[:10]}...{token[-10:]}")
        return True, result
    except Exception as e:
        print(f"❌ Failed {operation_name} with error: {str(e)}")
        return False, str(e)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TRADING API TOKEN TESTER")
    print("="*60)
    print(f"API Base: {TRADING_API_BASE}")
    print("="*60 + "\n")
    
    # List all available tokens in Redis
    print("🔍 Searching for all available tokens in Redis...")
    tokens = list_all_tokens()
    
    if not tokens:
        print("❌ No tokens found in Redis. Please check your Redis connection and data.")
        exit(1)
    
    print("\n" + "="*60)
    print("AVAILABLE TOKENS")
    print("="*60)
    for i, (key, token_info) in enumerate(tokens.items(), 1):
        print(f"{i}. {key} (length: {token_info['length']} chars)")
        print(f"   Token: {token_info['token']}")
    
    # Get account information using different tokens
    print("\n" + "="*60)
    print("TESTING TOKENS WITH ACCOUNT INFO ENDPOINT")
    print("="*60)
    
    working_tokens = {}
    
    for key, token_info in tokens.items():
        # Extract the actual token value (we'll need to get it again since we only stored a preview)
        token = get_fresh_token(token_key=key)
        if not token:
            continue
            
        # Test if this token can be used to get account info
        success, result = test_token_with_operation(token, "account_info", get_account_info)
        if success:
            working_tokens[key] = {
                'token': token,
                'capabilities': ['account_info']
            }
            
            # If we got account info, try to use this token for order placement
            if result and 'd' in result and result['d']:
                selected_account = result['d'][0]['name']
                print(f"\nTesting order placement with token from {key}...")
                
                # Create a test order
                test_order = {
                    "instrument": "MNQZ5",
                    "qty": "1",
                    "side": "buy",
                    "type": "limit",
                    "limitPrice": "14250.00",
                    "stopLoss": "0",
                    "takeProfit": "0",
                    "durationType": "Day"
                }
                
                # Test order placement
                success, _ = test_token_with_operation(
                    token, 
                    "order_placement", 
                    place_order, 
                    test_order,
                    account_id=selected_account
                )
                
                if success:
                    working_tokens[key]['capabilities'].append('order_placement')
    
    # Print summary of working tokens and their capabilities
    print("\n" + "="*60)
    print("TOKEN CAPABILITIES SUMMARY")
    print("="*60)
    
    if not working_tokens:
        print("❌ No working tokens found for any operation.")
    else:
        for key, info in working_tokens.items():
            capabilities = ", ".join(info['capabilities'])
            print(f"✅ {key}: Can perform {capabilities}")
    
    # If we have working tokens, show account information
    if working_tokens:
        # Use the first working token that can access account info
        for key, info in working_tokens.items():
            if 'account_info' in info['capabilities']:
                token = info['token']
                print("\n" + "="*60)
                print("ACCOUNT INFORMATION")
                print("="*60)
                account_info = get_account_info(token)
                if account_info and 'd' in account_info and account_info['d']:
                    for i, acc in enumerate(account_info['d'], 1):
                        print(f"Account {i}:")
                        print(f"  ID: {acc.get('id')}")
                        print(f"  Name: {acc.get('name')}")
                        print(f"  Type: {acc.get('type')}")
                        print(f"  Currency: {acc.get('currency')} {acc.get('currencySign', '')}")
                        print()
                break
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
