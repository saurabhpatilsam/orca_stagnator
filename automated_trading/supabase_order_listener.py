"""
Supabase Order Listener Service
================================
This service listens for new trading signals in Supabase and automatically
places orders via the Tradovate API.

Run this as a background service to enable automated order placement.
"""

import os
import sys
import time
import signal as sys_signal
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.orca_redis.client import get_redis_client
from app.services.tradingview.broker import TradingViewTradovateBroker
from app.services.orca_max.schemas import Order

# Load environment variables
load_dotenv()

class SupabaseOrderListener:
    """Listen for trading signals in Supabase and place orders via Tradovate API"""
    
    def __init__(self):
        """Initialize the listener service"""
        logger.info("Initializing Supabase Order Listener...")
        
        # Initialize Supabase client
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in .env file"
            )
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Initialize Redis and broker
        self.redis_client = get_redis_client()
        if not self.redis_client:
            raise Exception("Failed to connect to Redis")
        
        # Store brokers by account name for reuse
        self.brokers: Dict[str, TradingViewTradovateBroker] = {}
        
        # Service control
        self.running = True
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "2"))  # seconds
        
        logger.success("✅ Supabase Order Listener initialized")
    
    def get_broker(self, account_name: str) -> TradingViewTradovateBroker:
        """Get or create a broker instance for the given account"""
        if account_name not in self.brokers:
            logger.info(f"Creating broker for account: {account_name}")
            self.brokers[account_name] = TradingViewTradovateBroker(
                redis_client=self.redis_client,
                account_name=account_name,
                base_url=os.getenv("TRADING_API_BASE", "https://tv-demo.tradovateapi.com")
            )
        return self.brokers[account_name]
    
    def update_signal_status(
        self,
        signal_id: str,
        status: str,
        tradovate_order_id: Optional[str] = None,
        error_message: Optional[str] = None,
        account_id: Optional[str] = None
    ):
        """Update the status of a signal in Supabase"""
        try:
            update_data = {
                "status": status,
                "last_attempt_at": datetime.now().isoformat()
            }
            
            if tradovate_order_id:
                update_data["tradovate_order_id"] = tradovate_order_id
            if error_message:
                update_data["error_message"] = error_message
            if account_id:
                update_data["account_id"] = account_id
            
            # Increment placement attempts
            self.supabase.rpc(
                "increment_placement_attempts",
                {"signal_uuid": signal_id}
            ).execute()
            
            # Update status
            self.supabase.table("trading_signals")\
                .update(update_data)\
                .eq("id", signal_id)\
                .execute()
            
            # Log to order history
            self.supabase.table("order_history").insert({
                "signal_id": signal_id,
                "event_type": status,
                "event_data": {
                    "tradovate_order_id": tradovate_order_id,
                    "error_message": error_message,
                    "timestamp": datetime.now().isoformat()
                }
            }).execute()
            
        except Exception as e:
            logger.error(f"Error updating signal status: {str(e)}")
    
    def place_order_from_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Place an order based on a signal from Supabase.
        
        Args:
            signal: Signal data from Supabase
        
        Returns:
            True if order placed successfully, False otherwise
        """
        signal_id = signal["id"]
        
        try:
            logger.info(f"Processing signal: {signal['signal_id']}")
            
            # Update status to processing
            self.update_signal_status(signal_id, "processing")
            
            # Get broker for this account
            broker = self.get_broker(signal["account_name"])
            
            # Get accounts to find the account ID
            accounts = broker.get_all_accounts()
            if not accounts:
                raise Exception("No accounts found")
            
            # Find the account ID
            account_id = None
            for acc in accounts:
                if acc["name"] == signal["account_name"]:
                    account_id = acc["id"]
                    break
            
            if not account_id:
                raise Exception(f"Account not found: {signal['account_name']}")
            
            logger.info(f"Using account ID: {account_id}")
            
            # Create Order object
            order = Order(
                instrument=signal["instrument"],
                quantity=signal["quantity"],
                price=signal["price"] or 0.0,
                position=signal["side"].lower(),
                order_type=signal["order_type"].lower(),
                stop_loss=signal.get("stop_loss", 0.0),
                take_profit=signal.get("take_profit", 0.0),
                timestamp=datetime.now(),
                order_dict_all=signal.get("metadata", {})
            )
            
            # Place the order
            logger.info(f"Placing order: {signal['instrument']} {signal['side']} {signal['quantity']}")
            tradovate_order_id = broker.place_order(
                order=order,
                account_id=account_id
            )
            
            if tradovate_order_id:
                logger.success(f"✅ Order placed successfully: {tradovate_order_id}")
                self.update_signal_status(
                    signal_id,
                    "placed",
                    tradovate_order_id=tradovate_order_id,
                    account_id=account_id
                )
                return True
            else:
                logger.error("Order placement failed - no order ID returned")
                self.update_signal_status(
                    signal_id,
                    "failed",
                    error_message="No order ID returned from Tradovate API"
                )
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error placing order: {error_msg}")
            self.update_signal_status(
                signal_id,
                "failed",
                error_message=error_msg
            )
            return False
    
    def poll_for_signals(self):
        """Poll Supabase for pending signals"""
        try:
            # Query for pending signals
            response = self.supabase.table("trading_signals")\
                .select("*")\
                .eq("status", "pending")\
                .order("created_at", desc=False)\
                .limit(10)\
                .execute()
            
            if response.data:
                logger.info(f"Found {len(response.data)} pending signal(s)")
                
                for signal in response.data:
                    logger.info(f"Processing signal: {signal['signal_id']}")
                    self.place_order_from_signal(signal)
                    
        except Exception as e:
            logger.error(f"Error polling for signals: {str(e)}")
    
    def start(self):
        """Start the listener service"""
        logger.info("🚀 Starting Supabase Order Listener Service")
        logger.info(f"   Polling interval: {self.poll_interval} seconds")
        logger.info(f"   Trading API: {os.getenv('TRADING_API_BASE', 'https://tv-demo.tradovateapi.com')}")
        logger.info("   Press Ctrl+C to stop")
        
        try:
            while self.running:
                self.poll_for_signals()
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping service...")
            self.running = False
        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            raise
    
    def stop(self):
        """Stop the listener service"""
        logger.info("Stopping Supabase Order Listener...")
        self.running = False


# ============================================================================
# SERVICE ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the service"""
    print("\n" + "="*70)
    print("SUPABASE ORDER LISTENER SERVICE")
    print("="*70)
    print("\nThis service monitors Supabase for new trading signals and")
    print("automatically places orders via the Tradovate API.")
    print("="*70 + "\n")
    
    try:
        # Create and start the listener
        listener = SupabaseOrderListener()
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            logger.info("\nReceived shutdown signal")
            listener.stop()
            sys.exit(0)
        
        sys_signal.signal(sys_signal.SIGINT, signal_handler)
        sys_signal.signal(sys_signal.SIGTERM, signal_handler)
        
        # Start listening
        listener.start()
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        print("\n💡 Setup Instructions:")
        print("   1. Run supabase_setup.sql in your Supabase SQL Editor")
        print("   2. Add to .env file:")
        print("      SUPABASE_URL=your_supabase_url")
        print("      SUPABASE_KEY=your_supabase_anon_key")
        print("      TRADING_API_BASE=https://tv-demo.tradovateapi.com")
        print("      POLL_INTERVAL=2  # seconds")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
