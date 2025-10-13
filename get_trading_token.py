import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.orca_redis.client import get_redis_client

def get_trading_token(account_names):
    """
    Try to get a trading token for any of the provided account names.
    
    Args:
        account_names: List of account names to try
        
    Returns:
        Tuple of (account_name, token) if successful, (None, None) otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        logger.error("Failed to connect to Redis")
        return None, None
    
    for account_name in account_names:
        token_key = f"token:{account_name}"
        try:
            token = redis_client.get(token_key)
            if token:
                logger.info(f"Found token for account {account_name}")
                return account_name, token
        except Exception as e:
            logger.error(f"Error checking account {account_name}: {e}")
    
    logger.error("No valid tokens found for any account")
    return None, None

if __name__ == "__main__":
    # List of account names found in the codebase
    account_names_to_try = [
        "PAAPEX1361890000002",
        "PAAPEX1361890000008",
        "PAAPEX2659950000004"
    ]
    
    account_name, token = get_trading_token(account_names_to_try)
    
    if token:
        print("\n" + "="*60)
        print("TRADING TOKEN FOUND")
        print("="*60)
        print(f"Account: {account_name}")
        print("-"*60)
        print("Token:")
        print(token)
        print("-"*60)
        print("Sample Postman Authorization header:")
        print(f"Authorization: Bearer {token}")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("NO VALID TOKENS FOUND")
        print("="*60)
        print("Tried the following accounts:")
        for name in account_names_to_try:
            print(f"- {name}")
        print("\nPlease check if any of these accounts are valid or provide a different account name.")
        print("="*60 + "\n")
