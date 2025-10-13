import os
import sys
import json
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker
from app.services.orca_max.schemas import Order

def main():
    """Test the existing TradingViewTradovateBroker implementation"""
    print("\n" + "="*60)
    print("TESTING EXISTING BROKER IMPLEMENTATION")
    print("="*60)
    
    # Connect to Redis
    print("\n🔍 Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Failed to connect to Redis")
        return
    print("✅ Connected to Redis")
    
    # Initialize the broker
    print("\n🔧 Initializing TradingViewTradovateBroker...")
    account_name = "PAAPEX1361890000010"  # This is the account name used as Redis key
    
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        print(f"✅ Broker initialized for account: {account_name}")
    except Exception as e:
        print(f"❌ Failed to initialize broker: {str(e)}")
        return
    
    # Get all accounts
    print("\n📋 Fetching all accounts...")
    try:
        accounts = broker.get_all_accounts()
        print(f"✅ Found {len(accounts)} accounts:")
        for acc in accounts:
            print(f"   - ID: {acc.get('id')}, Name: {acc.get('name')}, Type: {acc.get('type')}")
        
        if not accounts:
            print("❌ No accounts found")
            return
        
        # Use the first account ID for testing
        account_id = accounts[0]['id']
        print(f"\n📋 Using account ID for testing: {account_id}")
        
    except Exception as e:
        print(f"❌ Failed to get accounts: {str(e)}")
        logger.error(f"Error getting accounts: {str(e)}", exc_info=True)
        return
    
    # Test placing an order
    print("\n🚀 Testing order placement...")
    try:
        from datetime import datetime
        
        # Create an Order object matching the schema with all required fields
        test_order = Order(
            instrument="MNQZ5",
            quantity=1,
            price=21000.0,
            position="buy",  # lowercase as per broker implementation
            order_type="limit",
            stop_loss=0.0,
            take_profit=0.0,
            timestamp=datetime.now(),
            order_dict_all={}  # Empty dict for now
        )
        
        print(f"Order details:")
        print(f"   - Instrument: {test_order.instrument}")
        print(f"   - Quantity: {test_order.quantity}")
        print(f"   - Price: {test_order.price}")
        print(f"   - Position: {test_order.position}")
        print(f"   - Order Type: {test_order.order_type}")
        
        # Place the order
        order_id = broker.place_order(
            order=test_order,
            account_id=account_id
        )
        
        if order_id:
            print(f"\n✅ Order placed successfully!")
            print(f"   Order ID: {order_id}")
        else:
            print(f"\n❌ Order placement failed - no order ID returned")
            
    except Exception as e:
        print(f"\n❌ Failed to place order: {str(e)}")
        logger.error(f"Error placing order: {str(e)}", exc_info=True)
    
    # Get account state
    print("\n💰 Fetching account state...")
    try:
        account_state = broker.get_account_state(account_id=account_id)
        print(f"✅ Account state retrieved:")
        print(f"   Balance: ${account_state.balance:.2f}")
        # Print all available attributes
        if hasattr(account_state, '__dict__'):
            for key, value in account_state.__dict__.items():
                if not key.startswith('_'):
                    print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Failed to get account state: {str(e)}")
        logger.error(f"Error getting account state: {str(e)}", exc_info=True)
    
    # Get current orders
    print("\n📝 Fetching current orders...")
    try:
        orders_result = broker.get_orders(account_id=account_id)
        # Handle if it returns a list directly
        if isinstance(orders_result, list):
            print(f"✅ Found {len(orders_result)} orders")
            for order in orders_result:
                if isinstance(order, dict):
                    print(f"   - Order ID: {order.get('id')}, Status: {order.get('status')}, Instrument: {order.get('instrument')}")
                else:
                    print(f"   - Order: {order}")
        else:
            print(f"✅ Found {len(orders_result.orders)} orders")
            for order in orders_result.orders:
                print(f"   - Order ID: {order.id}, Status: {order.status}, Instrument: {order.instrument}")
    except Exception as e:
        print(f"❌ Failed to get orders: {str(e)}")
        logger.error(f"Error getting orders: {str(e)}", exc_info=True)
    
    # Get positions
    print("\n📊 Fetching positions...")
    try:
        positions_result = broker.get_positions(account_id=account_id)
        # Handle if it returns a list directly
        if isinstance(positions_result, list):
            print(f"✅ Found {len(positions_result)} positions")
            for pos in positions_result:
                if isinstance(pos, dict):
                    print(f"   - Instrument: {pos.get('instrument')}, Quantity: {pos.get('netPos')}, PnL: ${pos.get('netPrice', 0):.2f}")
                else:
                    print(f"   - Position: {pos}")
        else:
            print(f"✅ Found {len(positions_result.positions)} positions")
            for pos in positions_result.positions:
                print(f"   - Instrument: {pos.instrument}, Quantity: {pos.qty}, PnL: ${pos.pl:.2f}")
    except Exception as e:
        print(f"❌ Failed to get positions: {str(e)}")
        logger.error(f"Error getting positions: {str(e)}", exc_info=True)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
