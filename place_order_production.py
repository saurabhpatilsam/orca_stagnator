"""
Production-ready order placement script for Tradovate API via TradingView integration.
This script demonstrates the correct flow for placing orders using the existing broker implementation.
"""

import os
import sys
from datetime import datetime
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker
from app.services.orca_max.schemas import Order

def place_order_with_broker(
    instrument: str = "MNQZ5",
    quantity: int = 1,
    side: str = "buy",
    order_type: str = "limit",
    limit_price: float = None,
    stop_loss: float = 0.0,
    take_profit: float = 0.0
):
    """
    Place an order using the TradingViewTradovateBroker.
    
    Args:
        instrument: Trading instrument symbol (e.g., 'MNQZ5')
        quantity: Order quantity
        side: 'buy' or 'sell'
        order_type: 'limit' or 'market'
        limit_price: Limit price (if None, will fetch current price and adjust)
        stop_loss: Stop loss price (0.0 for none)
        take_profit: Take profit price (0.0 for none)
    
    Returns:
        str: Order ID if successful, None otherwise
    """
    print("\n" + "="*70)
    print("TRADOVATE ORDER PLACEMENT - PRODUCTION SCRIPT")
    print("="*70)
    
    # Step 1: Connect to Redis
    print("\n[1/6] 🔍 Connecting to Redis...")
    redis_client = get_redis_client()
    if not redis_client:
        print("❌ Failed to connect to Redis")
        return None
    print("✅ Connected to Redis")
    
    # Step 2: Initialize broker
    print("\n[2/6] 🔧 Initializing broker...")
    account_name = "PAAPEX1361890000010"
    
    try:
        broker = TradingViewTradovateBroker(
            redis_client=redis_client,
            account_name=account_name,
            base_url="https://tv-demo.tradovateapi.com"
        )
        print(f"✅ Broker initialized for account: {account_name}")
    except Exception as e:
        print(f"❌ Failed to initialize broker: {str(e)}")
        logger.error(f"Broker initialization error: {str(e)}", exc_info=True)
        return None
    
    # Step 3: Get accounts
    print("\n[3/6] 📋 Fetching accounts...")
    try:
        accounts = broker.get_all_accounts()
        if not accounts:
            print("❌ No accounts found")
            return None
        
        account_id = accounts[0]['id']
        print(f"✅ Using account: {accounts[0]['name']} (ID: {account_id})")
    except Exception as e:
        print(f"❌ Failed to get accounts: {str(e)}")
        logger.error(f"Get accounts error: {str(e)}", exc_info=True)
        return None
    
    # Step 4: Get current price if limit_price not provided
    if limit_price is None:
        print(f"\n[4/6] 💹 Fetching current price for {instrument}...")
        try:
            quote = broker.get_price_quotes(symbol=instrument)
            if quote and 'd' in quote and len(quote['d']) > 0:
                current_price = float(quote['d'][0].get('price', 0))
                # Set limit price slightly below current for buy, above for sell
                if side.lower() == "buy":
                    limit_price = current_price * 0.999  # 0.1% below current
                else:
                    limit_price = current_price * 1.001  # 0.1% above current
                print(f"✅ Current price: ${current_price:.2f}")
                print(f"   Limit price set to: ${limit_price:.2f}")
            else:
                print("⚠️  Could not fetch current price, using default")
                limit_price = 21000.0
        except Exception as e:
            print(f"⚠️  Error fetching price: {str(e)}")
            limit_price = 21000.0
    else:
        print(f"\n[4/6] 💹 Using provided limit price: ${limit_price:.2f}")
    
    # Step 5: Create order object
    print(f"\n[5/6] 📝 Creating order...")
    try:
        order = Order(
            instrument=instrument,
            quantity=quantity,
            price=limit_price,
            position=side.lower(),
            order_type=order_type.lower(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now(),
            order_dict_all={}
        )
        
        print(f"Order details:")
        print(f"   Instrument: {order.instrument}")
        print(f"   Side: {order.position}")
        print(f"   Type: {order.order_type}")
        print(f"   Quantity: {order.quantity}")
        print(f"   Price: ${order.price:.2f}")
        if order.stop_loss > 0:
            print(f"   Stop Loss: ${order.stop_loss:.2f}")
        if order.take_profit > 0:
            print(f"   Take Profit: ${order.take_profit:.2f}")
    except Exception as e:
        print(f"❌ Failed to create order: {str(e)}")
        logger.error(f"Order creation error: {str(e)}", exc_info=True)
        return None
    
    # Step 6: Place the order
    print(f"\n[6/6] 🚀 Placing order...")
    try:
        order_id = broker.place_order(
            order=order,
            account_id=account_id
        )
        
        if order_id:
            print(f"\n✅ SUCCESS! Order placed!")
            print(f"   Order ID: {order_id}")
            print(f"\n💡 You can now:")
            print(f"   - Check order status with broker.get_order('{order_id}', '{account_id}')")
            print(f"   - Cancel order with broker.cancel_order('{order_id}', '{account_id}')")
            return order_id
        else:
            print(f"\n❌ Order placement failed - no order ID returned")
            print(f"\n💡 Possible reasons:")
            print(f"   - Market is closed")
            print(f"   - Price is too far from market")
            print(f"   - Insufficient margin")
            print(f"   - Demo account restrictions")
            return None
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Order placement failed: {error_msg}")
        logger.error(f"Order placement error: {error_msg}", exc_info=True)
        
        # Provide helpful troubleshooting tips
        print(f"\n💡 Troubleshooting tips:")
        if "modification rejected" in error_msg.lower():
            print(f"   - Try a price closer to current market price")
            print(f"   - Check if the market is open")
            print(f"   - Verify the instrument symbol is correct")
        elif "401" in error_msg:
            print(f"   - Token may have expired, check Redis")
        elif "404" in error_msg:
            print(f"   - Verify account ID is correct")
        
        return None
    
    finally:
        print("\n" + "="*70)

def main():
    """Main function with example usage"""
    
    # Example 1: Place a limit buy order with auto-price
    print("\n📌 Example 1: Limit Buy Order (auto-price)")
    order_id = place_order_with_broker(
        instrument="MNQZ5",
        quantity=1,
        side="buy",
        order_type="limit",
        limit_price=None  # Will fetch current price
    )
    
    if order_id:
        print(f"\n🎉 Order placed successfully with ID: {order_id}")
    else:
        print(f"\n⚠️  Order placement unsuccessful. Check logs above for details.")
    
    # Uncomment to test other order types:
    
    # # Example 2: Place a limit sell order with specific price
    # print("\n📌 Example 2: Limit Sell Order (specific price)")
    # order_id = place_order_with_broker(
    #     instrument="MNQZ5",
    #     quantity=1,
    #     side="sell",
    #     order_type="limit",
    #     limit_price=21500.0
    # )
    
    # # Example 3: Place order with stop loss and take profit
    # print("\n📌 Example 3: Order with SL/TP")
    # order_id = place_order_with_broker(
    #     instrument="MNQZ5",
    #     quantity=1,
    #     side="buy",
    #     order_type="limit",
    #     limit_price=21000.0,
    #     stop_loss=20900.0,
    #     take_profit=21100.0
    # )

if __name__ == "__main__":
    main()
