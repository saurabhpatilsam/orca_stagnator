import os
import sys
import json
import logging
from typing import Dict, Optional, Any
from urllib.parse import urljoin
import redis
import requests
from loguru import logger

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# TradingView API endpoints
TRADINGVIEW_BASE_URL = "https://www.tradingview.com/"
TRADOVATE_AUTH_ENDPOINT = "tradovate/api/v1/account/login"
TRADOVATE_ORDER_ENDPOINT = "tradovate/api/v1/order/placeorder"

class TradingViewTradovateAuth:
    """
    Handles authentication with TradingView's Tradovate integration
    and provides methods to place orders through TradingView's API.
    """
    
    def __init__(self, username: str, password: str, account_id: str):
        """
        Initialize with TradingView credentials and Tradovate account ID.
        
        Args:
            username: TradingView username/email
            password: TradingView password
            account_id: Tradovate account ID (e.g., 'PAAPEX1361890000002')
        """
        self.username = username
        self.password = password
        self.account_id = account_id
        self.access_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://www.tradingview.com',
            'Referer': 'https://www.tradingview.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        })
    
    def login(self) -> bool:
        """
        Authenticate with TradingView and get a bearer token for Tradovate API access.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        try:
            # First, get the TradingView session
            logger.info("Getting TradingView session...")
            response = self.session.get('https://www.tradingview.com/', timeout=10)
            response.raise_for_status()
            
            # Now authenticate with TradingView
            auth_url = urljoin(TRADINGVIEW_BASE_URL, 'accounts/signin/')
            auth_data = {
                'username': self.username,
                'password': self.password,
                'remember': 'on'
            }
            
            logger.info("Authenticating with TradingView...")
            response = self.session.post(
                auth_url,
                data=auth_data,  # Use data instead of json for form data
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Referer': 'https://www.tradingview.com/',
                },
                allow_redirects=True
            )
            
            logger.info(f"TradingView auth response status: {response.status_code}")
            logger.info(f"TradingView auth response: {response.text[:500]}")
            
            if response.status_code != 200:
                logger.error(f"Failed to authenticate with TradingView: {response.status_code} - {response.text}")
                return False
            
            # Now get the Tradovate token through TradingView
            tradovate_auth_url = urljoin(TRADINGVIEW_BASE_URL, TRADOVATE_AUTH_ENDPOINT)
            tradovate_auth_data = {
                'accountId': self.account_id,
                'isPaperTrading': True  # Set to False for live trading
            }
            
            logger.info("Getting Tradovate token from TradingView...")
            response = self.session.post(
                tradovate_auth_url,
                json=tradovate_auth_data,
                headers={
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.tradingview.com/chart/'
                }
            )
            
            logger.info(f"Tradovate auth response status: {response.status_code}")
            logger.info(f"Tradovate auth response: {response.text[:500]}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get Tradovate token: {response.status_code} - {response.text}")
                return False
            
            auth_data = response.json()
            if 'accessToken' not in auth_data:
                logger.error(f"No access token in response: {auth_data}")
                return False
            
            self.access_token = auth_data['accessToken']
            logger.info("Successfully authenticated with TradingView-Tradovate")
            return True
            
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}", exc_info=True)
            return False
    
    def place_order(self, symbol: str, side: str, qty: int, order_type: str = "market", 
                   limit_price: Optional[float] = None, stop_price: Optional[float] = None) -> Dict:
        """
        Place an order through TradingView's Tradovate integration.
        
        Args:
            symbol: Trading symbol (e.g., 'MNQZ5')
            side: 'buy' or 'sell'
            qty: Order quantity
            order_type: 'market', 'limit', or 'stop'
            limit_price: Required for limit orders
            stop_price: Required for stop orders
            
        Returns:
            Dict containing order response or error information
        """
        if not self.access_token:
            if not self.login():
                return {"s": "error", "errmsg": "Authentication failed"}
        
        try:
            # Prepare order data according to Tradovate API spec
            order_data = {
                "accountId": self.account_id,
                "symbol": symbol,
                "action": "Buy" if side.lower() == "buy" else "Sell",
                "orderQty": qty,
                "orderType": order_type.upper(),
                "timeInForce": "Day",
                "isAutomated": True
            }
            
            # Add price fields based on order type
            if order_type.lower() == "limit" and limit_price is not None:
                order_data["limitPrice"] = limit_price
            elif order_type.lower() == "stop" and stop_price is not None:
                order_data["stopPrice"] = stop_price
            
            # Place the order through TradingView's Tradovate endpoint
            order_url = urljoin(TRADINGVIEW_BASE_URL, TRADOVATE_ORDER_ENDPOINT)
            
            logger.info(f"Placing {order_type} order: {symbol} {side} {qty}")
            
            response = self.session.post(
                order_url,
                json=order_data,
                headers={
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json',
                    'Referer': 'https://www.tradingview.com/chart/'
                }
            )
            
            logger.info(f"Order placement response status: {response.status_code}")
            logger.info(f"Order placement response: {response.text}")
            
            if response.status_code == 401:  # Token expired, try to refresh
                logger.info("Token expired, attempting to re-authenticate...")
                if self.login():
                    response = self.session.post(
                        order_url,
                        json=order_data,
                        headers={
                            'Authorization': f'Bearer {self.access_token}',
                            'Content-Type': 'application/json',
                            'Referer': 'https://www.tradingview.com/chart/'
                        }
                    )
            
            response.raise_for_status()
            result = response.json()
            
            if "s" not in result:
                result["s"] = "ok" if "orderId" in result else "error"
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_msg = f"{e.response.status_code} - {e.response.text}"
                except:
                    pass
            logger.error(f"Error placing order: {error_msg}")
            return {"s": "error", "errmsg": error_msg}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return {"s": "error", "errmsg": str(e)}

def main():
    """Main function to test order placement with credentials"""
    print("\n" + "="*60)
    print("TRADINGVIEW-TRADOVATE ORDER PLACEMENT TEST")
    print("="*60)
    
    # Use credentials directly
    username = "saurabh@infignity.com"
    password = "St@gnator2695"
    account_id = "PAAPEX1361890000010"
    
    print(f"\n📋 Using credentials:")
    print(f"   Username: {username}")
    print(f"   Account ID: {account_id}")
    
    # Initialize the client
    client = TradingViewTradovateAuth(
        username=username,
        password=password,
        account_id=account_id
    )
    
    # Authenticate
    print("\n🔐 Authenticating with TradingView-Tradovate...")
    if not client.login():
        print("❌ Failed to authenticate with TradingView-Tradovate")
        return
    
    print("✅ Successfully authenticated with TradingView-Tradovate")
    
    # Example: Place a market order
    print("\n🚀 Placing test market order...")
    result = client.place_order(
        symbol="MNQZ5",
        side="buy",
        qty=1,
        order_type="market"
    )
    
    # Print the result
    print("\n📝 Order Result:")
    print(json.dumps(result, indent=2))
    
    if result.get("s") == "ok":
        print("\n✅ Order placed successfully!")
    else:
        print("\n❌ Failed to place order")

if __name__ == "__main__":
    main()
