"""
Check which accounts are available with the current token
"""

import os
import sys
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def check_accounts():
    """Check all available accounts"""
    
    print("\n" + "="*70)
    print("CHECKING AVAILABLE ACCOUNTS")
    print("="*70)
    
    # Connect to Redis
    print("\n[1/2] 🔍 Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Failed to connect to Redis")
        return
    print("✅ Connected to Redis")
    
    # Try with one of the available account tokens
    available_accounts = [
        "PAAPEX2666680000001",
        "PAAPEX2666680000002",
        "PAAPEX2666680000003",
        "PAAPEX2666680000004",
        "PAAPEX2666680000005",
    ]
    
    print(f"\n[2/2] 📋 Fetching all accounts...")
    
    for account_name in available_accounts:
        try:
            broker = TradingViewTradovateBroker(
                redis_client=redis_client,
                account_name=account_name,
                base_url="https://tv-demo.tradovateapi.com"
            )
            
            accounts = broker.get_all_accounts()
            
            if accounts:
                print(f"\n✅ Successfully fetched accounts using token for: {account_name}")
                print("\n" + "-"*70)
                print("AVAILABLE ACCOUNTS:")
                print("-"*70)
                
                for i, acc in enumerate(accounts, 1):
                    print(f"\nAccount {i}:")
                    print(f"   Name: {acc.get('name')}")
                    print(f"   ID: {acc.get('id')}")
                    print(f"   Type: {acc.get('accountType', 'N/A')}")
                    print(f"   Active: {acc.get('active', 'N/A')}")
                
                print("\n" + "="*70)
                return accounts
                
        except Exception as e:
            logger.debug(f"Failed with account {account_name}: {str(e)}")
            continue
    
    print("\n❌ Could not fetch accounts with any available token")
    print("\n" + "="*70)
    return None

if __name__ == "__main__":
    check_accounts()
