import os
import json
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
import requests
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class OrderProcessor:
    def __init__(self):
        # Initialize Supabase client
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Trading API configuration
        self.trading_api_base = os.getenv("TRADING_API_BASE", "https://tv-demo.tradovateapi.com")
        self.trading_account_id = os.getenv("TRADING_ACCOUNT_ID")
        
        # Order status mapping
        self.status_mapping = {
            "pending": "PENDING",
            "filled": "FILLED",
            "rejected": "REJECTED",
            "cancelled": "CANCELLED"
        }
    
    def format_order_for_trading_api(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format order data for the trading API"""
        return {
            "instrument": order_data.get("symbol"),
            "qty": str(order_data.get("quantity", 1)),
            "side": order_data.get("side", "").lower(),
            "type": order_data.get("order_type", "limit").lower(),
            "limitPrice": str(order_data.get("price")),
            "stopLoss": str(order_data.get("stop_loss", "")),
            "takeProfit": str(order_data.get("take_profit", "")),
            "durationType": "Day"
        }
    
    async def place_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Place an order using the trading API"""
        try:
            # Format order data for the trading API
            payload = self.format_order_for_trading_api(order_data)
            
            # Get authentication token (you'll need to implement this based on your auth flow)
            auth_token = self._get_auth_token()
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            }
            
            # Send request to trading API
            url = f"{self.trading_api_base}/accounts/{self.trading_account_id}/orders?locale=en"
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Update order status in Supabase
            self._update_order_status(
                order_id=order_data["id"],
                status="FILLED" if result.get("s") == "ok" else "REJECTED",
                external_id=result.get("d", {}).get("orderId")
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            self._update_order_status(
                order_id=order_data["id"],
                status="ERROR",
                error_message=str(e)
            )
            return None
    
    def _get_auth_token(self) -> str:
        """Get authentication token for the trading API"""
        # TODO: Implement your authentication logic here
        # This could be from Redis, environment variables, or another source
        token = os.getenv("TRADING_API_TOKEN")
        if not token:
            raise ValueError("Trading API token not found")
        return token
    
    def _update_order_status(self, order_id: str, status: str, external_id: str = None, error_message: str = None):
        """Update order status in Supabase"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if external_id:
                update_data["external_id"] = external_id
            
            if error_message:
                update_data["error_message"] = error_message
            
            # Update the order in Supabase
            result = self.supabase.table("orders").update(update_data).eq("id", order_id).execute()
            logger.info(f"Updated order {order_id} status to {status}")
            return result
        except Exception as e:
            logger.error(f"Failed to update order status: {str(e)}")
    
    async def process_new_orders(self):
        """Process new orders from Supabase"""
        try:
            # Subscribe to realtime changes on the orders table
            subscription = self.supabase.channel('realtime_orders')\
                .on('postgres_changes', 
                    event='*',
                    schema='public',
                    table='orders',
                    callback=self._handle_order_change
                )\
                .subscribe()
            
            logger.info("Listening for order changes...")
            
            # Keep the script running
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in order processing: {str(e)}")
        finally:
            # Cleanup
            if 'subscription' in locals():
                self.supabase.remove_channel(subscription)
    
    def _handle_order_change(self, payload):
        """Handle order changes from Supabase realtime"""
        try:
            event_type = payload.event_type
            record = payload.record
            
            logger.info(f"Received {event_type} event for order {record.get('id')}")
            
            # Only process INSERT and UPDATE events
            if event_type in ('INSERT', 'UPDATE'):
                # Check if this is a new order that needs processing
                if record.get('status') == 'PENDING':
                    # Process the order in a separate task
                    asyncio.create_task(self.place_order(record))
                    
        except Exception as e:
            logger.error(f"Error handling order change: {str(e)}")

async def main():
    # Create and start the order processor
    processor = OrderProcessor()
    await processor.process_new_orders()

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "TRADING_ACCOUNT_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please create a .env file with the following variables:")
        logger.info("SUPABASE_URL=your_supabase_url")
        logger.info("SUPABASE_ANON_KEY=your_supabase_anon_key")
        logger.info("TRADING_ACCOUNT_ID=your_trading_account_id")
        logger.info("TRADING_API_TOKEN=your_trading_api_token")
        exit(1)
    
    # Run the order processor
    asyncio.run(main())
