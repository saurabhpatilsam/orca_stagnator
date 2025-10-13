"""
Trading Signal Sender
=====================
Use this script in your trading strategy or Docker container to send signals to Supabase.
The signals will be automatically picked up by the order placement service.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class TradingSignalSender:
    """Send trading signals to Supabase for automated order placement"""
    
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError(
                "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in .env file"
            )
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        logger.info("TradingSignalSender initialized")
    
    def send_signal(
        self,
        instrument: str,
        side: str,
        quantity: int,
        strategy_name: str,
        order_type: str = "limit",
        price: Optional[float] = None,
        stop_loss: float = 0.0,
        take_profit: float = 0.0,
        account_name: str = "PAAPEX1361890000010",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a trading signal to Supabase.
        
        Args:
            instrument: Trading instrument (e.g., 'MNQZ5')
            side: 'buy' or 'sell'
            quantity: Number of contracts
            strategy_name: Name of your strategy
            order_type: 'market', 'limit', or 'stop'
            price: Limit price (required for limit orders)
            stop_loss: Stop loss price (0.0 for none)
            take_profit: Take profit price (0.0 for none)
            account_name: Tradovate account name
            metadata: Additional strategy-specific data
        
        Returns:
            Dict with signal details and status
        """
        try:
            # Generate unique signal ID
            signal_id = f"{strategy_name}_{instrument}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Prepare signal data
            signal_data = {
                "signal_id": signal_id,
                "strategy_name": strategy_name,
                "instrument": instrument,
                "side": side.lower(),
                "order_type": order_type.lower(),
                "quantity": quantity,
                "price": price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "account_name": account_name,
                "status": "pending",
                "metadata": metadata or {}
            }
            
            # Insert into Supabase
            logger.info(f"Sending signal: {signal_id}")
            response = self.supabase.table("trading_signals").insert(signal_data).execute()
            
            if response.data:
                logger.success(f"✅ Signal sent successfully: {signal_id}")
                return {
                    "success": True,
                    "signal_id": signal_id,
                    "data": response.data[0]
                }
            else:
                logger.error(f"Failed to send signal: No data returned")
                return {
                    "success": False,
                    "error": "No data returned from Supabase"
                }
                
        except Exception as e:
            logger.error(f"Error sending signal: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_signal_status(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Check the status of a previously sent signal.
        
        Args:
            signal_id: The signal ID returned when sending the signal
        
        Returns:
            Dict with signal status or None if not found
        """
        try:
            response = self.supabase.table("trading_signals")\
                .select("*")\
                .eq("signal_id", signal_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting signal status: {str(e)}")
            return None
    
    def cancel_signal(self, signal_id: str) -> bool:
        """
        Cancel a pending signal.
        
        Args:
            signal_id: The signal ID to cancel
        
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            response = self.supabase.table("trading_signals")\
                .update({"status": "cancelled"})\
                .eq("signal_id", signal_id)\
                .eq("status", "pending")\
                .execute()
            
            if response.data:
                logger.info(f"Signal {signal_id} cancelled")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling signal: {str(e)}")
            return False


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_strategy_signal():
    """Example: Send a signal from your trading strategy"""
    
    # Initialize sender
    sender = TradingSignalSender()
    
    # Example 1: Send a limit buy signal
    print("\n📊 Example 1: Limit Buy Order")
    result = sender.send_signal(
        instrument="MNQZ5",
        side="buy",
        quantity=1,
        strategy_name="momentum_strategy",
        order_type="limit",
        price=21000.0,
        stop_loss=20900.0,
        take_profit=21100.0,
        metadata={
            "indicator": "RSI",
            "rsi_value": 35,
            "confidence": 0.85
        }
    )
    
    if result["success"]:
        print(f"✅ Signal sent: {result['signal_id']}")
        signal_id = result['signal_id']
        
        # Check status after a few seconds
        import time
        time.sleep(2)
        
        status = sender.get_signal_status(signal_id)
        if status:
            print(f"📋 Signal status: {status['status']}")
            if status.get('tradovate_order_id'):
                print(f"🎯 Tradovate Order ID: {status['tradovate_order_id']}")
    else:
        print(f"❌ Failed to send signal: {result.get('error')}")
    
    # Example 2: Send a market sell signal
    print("\n📊 Example 2: Market Sell Order")
    result = sender.send_signal(
        instrument="MNQZ5",
        side="sell",
        quantity=1,
        strategy_name="breakout_strategy",
        order_type="market",
        metadata={
            "trigger": "resistance_break",
            "level": 21200
        }
    )
    
    if result["success"]:
        print(f"✅ Signal sent: {result['signal_id']}")


def example_docker_container_signal():
    """Example: Send signal from a Docker container"""
    
    sender = TradingSignalSender()
    
    # Simulate a strategy running in Docker
    print("\n🐳 Docker Container Strategy Signal")
    
    # Your strategy logic here...
    # When you detect a trading opportunity:
    
    result = sender.send_signal(
        instrument="MNQZ5",
        side="buy",
        quantity=2,
        strategy_name="docker_ml_strategy",
        order_type="limit",
        price=20950.0,
        account_name="PAAPEX1361890000010",
        metadata={
            "model": "LSTM",
            "prediction_confidence": 0.92,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"Signal result: {result}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TRADING SIGNAL SENDER - EXAMPLES")
    print("="*70)
    
    # Run examples
    try:
        example_strategy_signal()
        # example_docker_container_signal()  # Uncomment to test
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Make sure to:")
        print("   1. Run supabase_setup.sql in your Supabase SQL Editor")
        print("   2. Set SUPABASE_URL and SUPABASE_KEY in .env file")
        print("   3. Install required packages: pip install supabase python-dotenv loguru")
