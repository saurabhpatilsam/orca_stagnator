#!/usr/bin/env python3
"""
🔐 COMPREHENSIVE TOKEN GENERATOR & REDIS MANAGER
=================================================

This script handles:
1. Token generation from Tradovate API
2. Redis key initialization and management  
3. Token storage with proper TTL
4. Account mapping and sub-account creation
5. Error handling and monitoring

Author: Orca Trading System
Version: 2.0
"""

import json
import requests
import redis
import os
import sys
from loguru import logger
from dotenv import load_dotenv
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import httpx
from enum import Enum

# Load environment variables
load_dotenv()
class AlertType(Enum):
    Pass = "Pass"
    Fail = "Fail"

# Configuration
TTL_SECONDS = 60 * 60  # Azure Redis Configuration - PRODUCTION
REDIS_CONFIG = {
    'host': os.getenv("REDIS_HOST", "redismanager.redis.cache.windows.net"),
    'port': int(os.getenv("REDIS_PORT", 6380)),
    'password': os.getenv("REDIS_PASSWORD", ""),  # Must set REDIS_PASSWORD environment variable
    'ssl': True,
    'ssl_cert_reqs': None,
    'decode_responses': True
}
def setup_logging():
    """Configure logging with proper formatting"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/token_manager_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

def discord_alert(alert_type: AlertType, message: str) -> None:
    """Send Discord notification"""
    try:
        ribbon = 9498256 if alert_type == AlertType.Pass else 16711680
        embed = {
            "title": "🔐 Token Manager Alert",
            "description": message,
            "color": ribbon,
            "footer": {
                "text": f"Alert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            }
        }
        payload = {"embeds": [embed]}
        
        webhook_url = "https://discord.com/api/webhooks/1402811131613020312/sNRHWlMzQM3KQ3Z4522g07AFfOEdCS36i-SleW4NEKByVX0oxWSHxeHSSAXOMl8C_nx-"
        response = httpx.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.debug(f"Discord alert sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send Discord alert: {e}")

def get_redis_client() -> Optional[redis.Redis]:
    """Create and test Redis connection"""
    try:
        client = redis.Redis(**REDIS_CONFIG)
        client.ping()
        logger.info("✅ Redis connection established successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        return None

def get_access_token(username: str, password: str) -> Optional[str]:
    """
    Get access token from Tradovate API
    
    Args:
        username: Tradovate username
        password: Tradovate password
        
    Returns:
        JWT access token or None if failed
    """
    url = "https://tv-demo.tradovateapi.com/authorize?locale=en"
    encoded_username = urllib.parse.quote(username)
    encoded_password = urllib.parse.quote(password)
    payload = f'locale=en&login={encoded_username}&password={encoded_password}'
    
    headers = {
        'Host': 'tv-demo.tradovateapi.com',
        'Connection': 'keep-alive',
        'sec-ch-ua-platform': '"macOS"',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'Origin': 'https://www.tradingview.com',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.tradingview.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        logger.info(f"🔑 Requesting token for: {username}")
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("s") == "ok":
            access_token = data.get("d", {}).get("access_token")
            if access_token:
                logger.success(f"✅ Token obtained for {username} (length: {len(access_token)})")
                return access_token
            else:
                logger.error(f"❌ No access token in response for {username}")
        else:
            logger.error(f"❌ API call failed for {username}: {data}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error for {username}: {e}")
        discord_alert(AlertType.Fail, f"Network error fetching token for {username}: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error for {username}: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error for {username}: {e}")
    
    return None

def generate_sub_accounts(main_username: str) -> List[str]:
    """
    Generate sub-account names based on main username
    
    Args:
        main_username: Main account like 'APEX_272045'
        
    Returns:
        List of sub-account names like ['PAAPEX2720450000001', ...]
    """
    if not main_username.startswith('APEX_'):
        logger.warning(f"Unexpected username format: {main_username}")
        return [main_username]
    
    # Extract number from APEX_XXXXXX
    account_number = main_username.split('_')[1]
    
    # Generate 5 sub-accounts
    sub_accounts = []
    for i in range(1, 6):
        sub_account = f"PAAPEX{account_number}000000{i}"
        sub_accounts.append(sub_account)
    
    logger.debug(f"Generated sub-accounts for {main_username}: {sub_accounts}")
    return sub_accounts

def initialize_redis_keys(redis_client: redis.Redis, username: str, sub_accounts: List[str]) -> bool:
    """
    Initialize Redis key structure for a username and its sub-accounts
    
    Args:
        redis_client: Redis connection
        username: Main username
        sub_accounts: List of sub-account names
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create list of all token keys for this username
        all_keys = [f"token:{username}"] + [f"token:{sub}" for sub in sub_accounts]
        
        # Store the key list under the username
        redis_client.delete(username)  # Clear existing list
        for key in all_keys:
            redis_client.lpush(username, key)
        
        logger.info(f"📝 Initialized {len(all_keys)} keys for {username}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis keys for {username}: {e}")
        return False

def store_tokens_in_redis(redis_client: redis.Redis, username: str, access_token: str, sub_accounts: List[str]) -> bool:
    """
    Store access token in Redis for username and all sub-accounts
    
    Args:
        redis_client: Redis connection
        username: Main username
        access_token: JWT token to store
        sub_accounts: List of sub-account names
        
    Returns:
        True if successful, False otherwise
    """
    try:
        stored_count = 0
        
        # Store token for main account
        main_key = f"token:{username}"
        redis_client.setex(main_key, TTL_SECONDS, access_token)
        redis_client.setex(f"auth:{username}", TTL_SECONDS, access_token)
        stored_count += 1
        
        # Store token for all sub-accounts
        for sub_account in sub_accounts:
            sub_key = f"token:{sub_account}"
            redis_client.setex(sub_key, TTL_SECONDS, access_token)
            stored_count += 1
        
        # Set expiration info
        expiry_time = datetime.now() + timedelta(seconds=TTL_SECONDS)
        redis_client.setex(f"token_expiry:{username}", TTL_SECONDS, expiry_time.isoformat())
        
        logger.success(f"💾 Stored token in {stored_count} Redis keys for {username} (TTL: {TTL_SECONDS}s)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to store tokens for {username}: {e}")
        return False

def process_account(creds: Dict, redis_client: redis.Redis) -> Tuple[str, bool]:
    """
    Process a single account: generate token and store in Redis
    
    Args:
        creds: Dictionary with 'username' and 'password'
        redis_client: Redis connection
        
    Returns:
        Tuple of (username, success_status)
    """
    username = creds.get('username')
    password = creds.get('password')
    
    if not username or not password:
        logger.warning(f"⚠️ Skipping invalid credentials: {creds}")
        return username or "unknown", False

    try:
        # Step 1: Generate sub-accounts
        sub_accounts = generate_sub_accounts(username)
        
        # Step 2: Initialize Redis key structure
        if not initialize_redis_keys(redis_client, username, sub_accounts):
            return username, False
        
        # Step 3: Get access token
        access_token = get_access_token(username, password)
        if not access_token:
            logger.error(f"❌ Failed to get token for {username}")
            return username, False
        
        # Step 4: Store tokens in Redis
        if not store_tokens_in_redis(redis_client, username, access_token, sub_accounts):
            return username, False
        
        logger.success(f"🎉 Successfully processed {username} with {len(sub_accounts)} sub-accounts")
        return username, True
        
    except Exception as e:
        logger.error(f"❌ Exception processing {username}: {e}")
        return username, False

def load_credentials(file_path: str = 'credentials.json') -> Optional[List[Dict]]:
    """Load credentials from JSON file"""
    try:
        # Try multiple possible paths
        possible_paths = [
            file_path,
            f'tradovate-market-stream-main/{file_path}',
            f'/Users/stagnator/Downloads/orca-ven-backend-main/tradovate-market-stream-main/{file_path}'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    credentials = json.load(f)
                logger.info(f"📂 Loaded {len(credentials)} accounts from {path}")
                return credentials
        
        logger.error(f"❌ Credentials file not found in any of: {possible_paths}")
        return None
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in credentials file: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading credentials: {e}")
        return None

def verify_redis_data(redis_client: redis.Redis) -> Dict:
    """Verify what's stored in Redis after token generation"""
    try:
        all_keys = redis_client.keys('*')
        token_keys = redis_client.keys('token:*')
        auth_keys = redis_client.keys('auth:*')
        
        verification = {
            'total_keys': len(all_keys),
            'token_keys': len(token_keys),
            'auth_keys': len(auth_keys),
            'sample_tokens': {}
        }
        
        # Get sample tokens
        for key in token_keys[:5]:  # First 5 token keys
            token = redis_client.get(key)
            if token:
                verification['sample_tokens'][key] = {
                    'length': len(token),
                    'preview': token[:50] + '...' if len(token) > 50 else token,
                    'ttl': redis_client.ttl(key)
                }
        
        return verification
        
    except Exception as e:
        logger.error(f"❌ Error verifying Redis data: {e}")
        return {}

def main():
    """Main execution function"""
    print("\n" + "="*80)
    print("🔐 ORCA TOKEN GENERATOR & REDIS MANAGER")
    print("="*80)
    
    # Setup logging
    setup_logging()
    
    # Load credentials
    logger.info("📂 Loading credentials...")
    credentials_list = load_credentials()
    if not credentials_list:
        logger.error("❌ No credentials loaded. Exiting.")
        return
    
    # Connect to Redis
    logger.info("🔌 Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        logger.error("❌ Redis connection failed. Exiting.")
        return
    
    # Process all accounts
    logger.info(f"🚀 Processing {len(credentials_list)} accounts with {MAX_WORKERS} workers...")
    
    results = {'success': [], 'failed': []}
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_account, creds, redis_client): creds 
            for creds in credentials_list
        }
        
        # Collect results
        for future in as_completed(futures):
            creds = futures[future]
            try:
                username, success = future.result()
                if success:
                    results['success'].append(username)
                else:
                    results['failed'].append(username)
            except Exception as exc:
                username = creds.get('username', 'unknown')
                logger.error(f"❌ Exception for {username}: {exc}")
                results['failed'].append(username)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Verify Redis data
    logger.info("🔍 Verifying Redis data...")
    verification = verify_redis_data(redis_client)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 EXECUTION SUMMARY")
    print("="*80)
    print(f"⏱️  Execution time: {execution_time:.2f} seconds")
    print(f"✅ Successful: {len(results['success'])} accounts")
    print(f"❌ Failed: {len(results['failed'])} accounts")
    
    if results['success']:
        print(f"\n🎉 Successfully processed:")
        for username in results['success']:
            print(f"   • {username}")
    
    if results['failed']:
        print(f"\n💥 Failed to process:")
        for username in results['failed']:
            print(f"   • {username}")
    
    print(f"\n📊 Redis Verification:")
    print(f"   • Total keys: {verification.get('total_keys', 0)}")
    print(f"   • Token keys: {verification.get('token_keys', 0)}")
    print(f"   • Auth keys: {verification.get('auth_keys', 0)}")
    
    if verification.get('sample_tokens'):
        print(f"\n🔑 Sample tokens:")
        for key, info in verification['sample_tokens'].items():
            print(f"   • {key}: {info['length']} chars, TTL: {info['ttl']}s")
    
    # Send Discord notification
    if results['failed']:
        discord_alert(
            AlertType.Fail, 
            f"Token generation completed with {len(results['failed'])} failures: {', '.join(results['failed'])}"
        )
    else:
        discord_alert(
            AlertType.Pass, 
            f"🎉 All {len(results['success'])} accounts processed successfully! Generated {verification.get('token_keys', 0)} tokens."
        )
    
    print("\n" + "="*80)
    print("🏁 TOKEN GENERATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
