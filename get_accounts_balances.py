"""
Get all accounts and their balances
"""

import os
import sys
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker

def get_accounts_and_balances():
    """Fetch all accounts and their balances"""
    
    print("\n" + "="*80)
    print("FETCHING ACCOUNTS AND BALANCES")
    print("="*80)
    
    # Connect to Redis
    print("\n[1/3] 🔍 Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Failed to connect to Redis")
        return
    print("✅ Connected to Redis")
    
    # Initialize broker with any available token
    print("\n[2/3] 🔧 Initializing broker...")
    account_name = "PAAPEX2666680000001"  # Using available token
    
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        print(f"✅ Broker initialized")
    except Exception as e:
        print(f"❌ Failed to initialize broker: {str(e)}")
        return
    
    # Fetch all accounts
    print("\n[3/3] 📋 Fetching accounts and balances...")
    try:
        accounts = broker.get_all_accounts()
        
        if not accounts:
            print("❌ No accounts found")
            return
        
        print(f"\n✅ Found {len(accounts)} accounts\n")
        print("="*80)
        
        total_balance = 0.0
        
        for i, account in enumerate(accounts, 1):
            account_id = account.get('id')
            account_name = account.get('name')
            
            print(f"\n{'='*80}")
            print(f"ACCOUNT #{i}")
            print(f"{'='*80}")
            print(f"📝 Account Name: {account_name}")
            print(f"🆔 Account ID:   {account_id}")
            print(f"📊 Type:         {account.get('accountType', 'Demo')}")
            print(f"✅ Status:       {'Active' if account.get('active', True) else 'Inactive'}")
            
            # Try to get balance
            try:
                state = broker.get_account_state(account_id)
                
                if state:
                    print(f"\n💰 BALANCE INFORMATION:")
                    
                    # Handle different field names
                    balance = getattr(state, 'balance', 0.0)
                    equity = getattr(state, 'equity', 0.0)
                    unrealized_pl = getattr(state, 'unrealizedPl', 0.0)
                    
                    print(f"   Balance:               ${balance:,.2f}")
                    print(f"   Equity:                ${equity:,.2f}")
                    print(f"   Unrealized P&L:        ${unrealized_pl:,.2f}")
                    
                    # Try to get additional fields if they exist
                    if hasattr(state, 'cashBalance'):
                        print(f"   Cash Balance:          ${state.cashBalance:,.2f}")
                    if hasattr(state, 'realizedPl'):
                        print(f"   Realized P&L:          ${state.realizedPl:,.2f}")
                    if hasattr(state, 'openRealizedPl'):
                        print(f"   Open P&L:              ${state.openRealizedPl:,.2f}")
                    if hasattr(state, 'marginUsed'):
                        print(f"   Margin Used:           ${state.marginUsed:,.2f}")
                    if hasattr(state, 'availableBalance'):
                        print(f"   Available Balance:     ${state.availableBalance:,.2f}")
                    
                    # Use equity as the primary balance metric
                    total_balance += equity
                else:
                    print(f"\n⚠️  Could not fetch balance for this account")
                    
            except Exception as e:
                print(f"\n⚠️  Error fetching balance: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"📊 Total Accounts: {len(accounts)}")
        print(f"💰 Total Balance:  ${total_balance:,.2f}")
        print(f"{'='*80}\n")
        
        return accounts
        
    except Exception as e:
        print(f"\n❌ Error fetching accounts: {str(e)}")
        logger.error(f"Error details: {str(e)}", exc_info=True)
        return None


if __name__ == "__main__":
    get_accounts_and_balances()
