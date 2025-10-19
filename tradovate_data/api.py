import time
import random
from datetime import datetime, timezone, timedelta, date
from typing import List, Dict
from zoneinfo import ZoneInfo
from dateutil import parser

import requests
import threading

from helper.logging_setup import logger
from tradovate.tradovatesocket import TradovateSocket
from publisher.client import get_redis_client
from credentialsmanager.client import get_token_from_redis


month_codes = {
    "H": 3,  # March
    "M": 6,  # June
    "U": 9,  # September
    "Z": 12,  # December
}

tradovate_usernames = ["APEX_136189", "APEX_272045", "APEX_265995", "APEX_266668"]


class TradovateAuth:
    def __init__(self, locale="en", instruments=None):

        # Randomly select an account name from the list
        self.account_name = random.choice(tradovate_usernames)
        logger.info(f"Tradovate account: {format(self.account_name)}")
        self.rest_base_url = "https://demo.tradovateapi.com/v1"
        # For trading viewer
        self.tv_auth_url = "https://tv-demo.tradovateapi.com/authorize?locale=en"

        self.auth_url = f"{self.rest_base_url}/auth/accesstokenrequest"
        self.auth_renew_url = f"{self.rest_base_url}/auth/renewaccesstoken"

        self.locale = locale

        self._price_lock = threading.Lock()
        self._chart_lock = threading.Lock()
        self.tv_access_token = None
        self.tv_access_token_expiration = None

        self.access_token = None
        self.access_token_expiration = None
        self.md_access_token = None
        self.md_access_token_expiration = None
        self.latest_prices_contracts = {}
        self.response_data = {}

        # Token renewal management
        self.renewal_timer = None
        self.stop_renewal = False

        self.chart_results = {}
        self.chart_completion_events = {}

        self._authenticate_all()
        self.contracts = self.discover_current_contracts(instruments)

        # Start token renewal scheduler
        self._start_token_renewal_scheduler()

        self.socket = TradovateSocket(
            md_access_token=self.md_access_token,
            contracts=self.contracts,
            price_callback=self.handle_price_update,
            bars_callback=self.handle_bars_data,
        )
        self.socket.connect_websocket()

    @property
    def socket_connect(self):
        return self.socket and self.socket.authorized

    def _authenticate_all(self):
        """Authenticate and validate all tokens are obtained with retry logic"""
        max_retries = 2

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Starting authentication attempt {attempt}/{max_retries}")
                self._tv_authenticate()
                self._renew_tokens()

                # Final validation that all required tokens are present
                if not all(
                    [self.tv_access_token, self.access_token, self.md_access_token]
                ):
                    missing_tokens = []
                    if not self.tv_access_token:
                        missing_tokens.append("tv_access_token")
                    if not self.access_token:
                        missing_tokens.append("access_token")
                    if not self.md_access_token:
                        missing_tokens.append("md_access_token")

                    raise ValueError(
                        f"Authentication failed: Missing tokens: {', '.join(missing_tokens)}"
                    )

                logger.info("All authentication tokens obtained successfully")
                return  # Success, exit the method

            except Exception as e:
                logger.error(
                    f"Authentication attempt {attempt}/{max_retries} failed: {e}"
                )

                if attempt < max_retries:
                    logger.info(f"Retrying full authentication in 3 seconds...")
                    time.sleep(3)
                else:
                    logger.error(
                        f"All authentication attempts failed after {max_retries} tries"
                    )
                    raise

    def _tv_authenticate(self, retry_attempt=1, max_retries=3):
        try:
            # Use Redis to get the token
            redis_client = get_redis_client()
            self.tv_access_token = get_token_from_redis(
                redis_client, f"token:{self.account_name}"
            )

            # Validate that we actually got a token
            if not self.tv_access_token:
                raise ValueError(
                    f"TV authentication failed with {self.account_name}: No access token received from Redis"
                )
                self.account_name = random.choice(tradovate_usernames)

            # For Redis-based tokens, we'll set a default expiration time
            # since the actual expiration is managed by Redis TTL
            current_time = datetime.now(timezone.utc)
            self.tv_access_token_expiration = current_time + timedelta(
                hours=5
            )  # Default 5 hour TTL

            logger.info("TV Authentication successful (using Redis)")
            logger.info(
                f"Access token retrieved from Redis for user: {self.account_name}"
            )
        except Exception as e:
            logger.exception(
                "TV Authentication failed (attempt %d/%d): %s",
                retry_attempt,
                max_retries,
                e,
            )

            if retry_attempt < max_retries:
                logger.info("Retrying TV authentication in 2 seconds...")
                time.sleep(2)
                self.account_name = random.choice(tradovate_usernames)
                return self._tv_authenticate(retry_attempt + 1, max_retries)
            else:
                logger.error("TV Authentication failed after %d attempts", max_retries)
                raise  # Re-raise the exception after all retries exhausted

    def _renew_tokens(self, retry_attempt=1, max_retries=2):
        try:
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.tv_access_token}",
            }
            response = requests.get(self.auth_renew_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # this is a different token from the one in Trading view
            self.access_token = data.get("accessToken")
            self.access_token_expiration = (
                data.get("expirationTime").split(".")[0] + "Z"
            )
            self.md_access_token = data.get(
                "mdAccessToken"
            )  # Fixed: was missing this line
            self.md_access_token_expiration = (
                data.get("expirationTime").split(".")[0] + "Z"
            )

            # Validate that we actually got the tokens
            if not self.access_token:
                raise ValueError("Token renewal failed: No access token received")
            if not self.md_access_token:
                raise ValueError("Token renewal failed: No MD access token received")

            self.md_access_token_expiration = self.get_london_time_from_utc_str(
                self.md_access_token_expiration
            )

            self.response_data = data

            logger.info("Access tokens renewed successfully")

            logger.debug(
                f"Raw expiration data: {self.access_token_expiration} (type: {type(self.access_token_expiration)})"
            )

            logger.info(f"Access token expires at: {self.access_token_expiration}")
            logger.info(
                f"MD Access token expires at: {self.md_access_token_expiration}"
            )

        except Exception as e:
            logger.exception(
                "Failed to renew access tokens (attempt %d/%d): %s",
                retry_attempt,
                max_retries,
                e,
            )

            if retry_attempt < max_retries:
                logger.info("Retrying token renewal in 2 seconds...")
                time.sleep(2)  # Wait before retry
                return self._renew_tokens(retry_attempt + 1, max_retries)
            else:
                logger.error("Token renewal failed after %d attempts", max_retries)
                raise  # Re-raise the exception after all retries exhausted

    def get_london_time_from_timestamp_ms(self, timestamp_ms: int) -> str:
        # convert to seconds
        timestamp_s = timestamp_ms / 1000
        # Convert to UTC datetime
        dt_utc = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)
        formatted = dt_utc.astimezone(ZoneInfo("Europe/London"))
        formatted = formatted.strftime("%Y-%m-%dT%H:%M:%S%z")
        return formatted

        # Convert to London time

    def get_london_time_from_utc_str(self, dt_end) -> str:
        dt_utc = datetime.strptime(dt_end, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
        # for debugging
        # dt_minus_10 = dt_utc - timedelta(minutes=70)
        # dt_london = dt_minus_10.astimezone(ZoneInfo("Europe/London"))

        dt_london = dt_utc.astimezone(ZoneInfo("Europe/London"))
        # Format result (ISO-like with timezone offset)
        formatted = dt_london.strftime("%Y-%m-%dT%H:%M:%S%z")

        return formatted

    def _format_timestamp(self, timestamp):
        """Convert millisecond timestamp to readable format"""
        if timestamp:
            try:
                # Handle both string and int timestamps
                if isinstance(timestamp, str):
                    timestamp = int(timestamp)
                return datetime.fromtimestamp(
                    timestamp / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d %H:%M:%S UTC")
            except (ValueError, TypeError) as e:
                logger.warning(f"Error formatting timestamp {timestamp}: {e}")
                return f"Invalid timestamp: {timestamp}"
        return "Unknown"

    def _parse_iso_timestamp(self, iso_string):
        """Parse ISO timestamp string to datetime object"""
        if iso_string:
            return datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return None

    def _get_seconds_until_expiry(self, expiration_time, token_type):
        """Calculate seconds until token expires (always non-negative integer)"""
        now = datetime.now(timezone.utc)

        if token_type == "TV":
            # already a datetime
            expiry_dt = expiration_time
        else:
            # string in ISO8601
            expiry_dt = parser.isoparse(expiration_time)

        in_seconds = (expiry_dt - now).seconds
        return in_seconds

    def _should_renew_tokens(self, token_expiration_time, token_type: str):
        """Check if tokens need renewal (renew 5 minutes before expiry)"""
        renewal_buffer = 480  # 8 minutes in seconds

        # Check MD access token
        if token_expiration_time:

            token_seconds_left = self._get_seconds_until_expiry(
                token_expiration_time, token_type
            )

            if token_seconds_left <= renewal_buffer:
                logger.info(
                    f"{token_type} Access token expires in {token_seconds_left} seconds, needs renewal"
                )
                return True

        return False

    def _start_token_renewal_scheduler(self):
        """Start the token renewal scheduler"""

        def renewal_checker():
            while not self.stop_renewal:
                try:
                    if self._should_renew_tokens(self.md_access_token_expiration, "MD"):
                        logger.info("Renewing MD tokens...")
                        self._renew_tokens()

                        # Update socket with new MD token if needed
                        if self.socket and hasattr(self.socket, "md_access_token"):
                            self.socket.md_access_token = self.md_access_token
                            logger.info("Updated socket with new MD access token")

                    # Check every 60 seconds
                    time.sleep(60)

                except Exception as e:
                    logger.error(f"Error in token renewal checker: {e}")
                    time.sleep(60)  # Wait before retrying

        def renewal_tv_checker():
            while not self.stop_renewal:
                try:
                    if self._should_renew_tokens(self.tv_access_token_expiration, "TV"):
                        logger.info("Renewing TV tokens...")
                        self._tv_authenticate()
                    # Check every 60 seconds
                    time.sleep(60)

                except Exception as e:
                    logger.error(f"Error in token renewal checker: {e}")
                    time.sleep(60)  # Wait before retrying

        self.tv_renewal_timer = threading.Thread(target=renewal_tv_checker, daemon=True)
        self.tv_renewal_timer.start()

        self.renewal_timer = threading.Thread(target=renewal_checker, daemon=True)
        self.renewal_timer.start()

        logger.info("Tokens renewal scheduler started")

    def stop_token_renewal_scheduler(self):
        """Stop the token renewal scheduler"""
        self.stop_renewal = True
        if self.renewal_timer:
            self.renewal_timer.join(timeout=5)
        logger.info("Token renewal scheduler stopped")

    def handle_price_update(self, price_data: dict) -> None:
        """Fixed: Handle price updates per contract"""
        with self._price_lock:
            self.latest_prices_contracts = price_data

    def get_latest_prices(self, contract_id: str) -> dict:
        with self._price_lock:
            return self.latest_prices_contracts.copy().get(contract_id, {})

    def handle_bars_data(self, bars_list, chart_id):
        """Store bars data for retrieval and trigger completion event"""
        logger.info(
            f"Got {len(bars_list.get('bars'))} bars for chart {bars_list.get('symbol')}"
        )

        # Find which request this data belongs to
        for request_id, data in self.socket.chart_data.items():
            if not data["complete"]:
                # Store the bars in our results
                if request_id not in self.chart_results:
                    self.chart_results[request_id] = []
                self.chart_results[request_id].extend(bars_list)
                break

        return bars_list

    def get_access_token(self):
        return self.access_token

    def get_response_data(self):
        return self.response_data

    def discover_current_contracts(self, contracts: List[str]) -> List[Dict[str, str]]:
        """
        Discover the current front-month futures contract for each instrument.
        If the front contract is within 7 days of expiry, return the next one.
        Returns a list of dicts with 'id' and 'name'.
        """
        results = []
        now = datetime.utcnow()

        for symbol_prefix in contracts:
            try:
                suggest_url = f"{self.rest_base_url}/contract/suggest?t={symbol_prefix}"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(suggest_url, headers=headers)
                response.raise_for_status()
                contracts = response.json()

                parsed_contracts = []

                for contract in contracts:
                    name = contract.get("name")
                    contract_id = contract.get("id")

                    if not name or len(name) < 3:
                        continue

                    month_code = name[-2]
                    year_digit = name[-1]

                    if month_code not in month_codes or not year_digit.isdigit():
                        continue

                    month = month_codes[month_code]

                    year = 2020 + int(year_digit)  # Adjust if needed

                    expiry_estimate = datetime(year, month, 19)
                    parsed_contracts.append((expiry_estimate, contract_id, name))

                # Sort by expiry date
                parsed_contracts.sort(key=lambda x: x[0])

                if not parsed_contracts:
                    continue

                # Check if front-month is within 7 days of expiry
                first_expiry, first_id, first_name = parsed_contracts[0]
                if (first_expiry - now).days <= 7 and len(parsed_contracts) > 1:
                    _, next_id, next_name = parsed_contracts[1]
                    results.append({"id": next_id, "name": next_name})
                else:
                    results.append({"id": first_id, "name": first_name})

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching contracts for {symbol_prefix}: {e}")
                continue

        logger.info(f"Contracts for fetch: {results}")
        return results

    def get_bars(
        self, symbol, bar_size_minutes, starting_time, number_of_bars, timeout=30
    ):
        """
        Get historical chart data synchronously (blocking until data is received).

        Parameters:
        - symbol (str): Contract symbol (e.g., "NQU5")
        - bar_size_minutes (int): Size of each bar in minutes
        - starting_time (datetime): Starting point for historical data
        - number_of_bars (int): Number of bars to retrieve
        - timeout (int): Maximum seconds to wait for data

        Returns:
        - List[Dict]: List of bar dictionaries with OHLC data, or None if failed
        """
        if not self.socket or not self.socket.authorized:
            logger.error("Socket not connected or not authorized")
            return None

        # Make the request
        request_id = self.socket.request_historical_chart(
            symbol, bar_size_minutes, starting_time, number_of_bars, store_data=True
        )

        if request_id is None:
            logger.error("Failed to send chart request")
            return None

        logger.info(
            f"Waiting for chart data (request {request_id}) with timeout {timeout}s..."
        )

        try:
            # Wait for the data to be complete
            chart_data = self.socket.get_historical_chart_data(request_id, timeout)

            if chart_data and chart_data["complete"]:
                bars = chart_data["bars"]
                logger.info(f"Successfully retrieved {len(bars)} bars for {symbol}")
                return bars
            else:
                logger.warning(
                    f"Failed to get complete chart data for request {request_id}"
                )
                return None

        except Exception as e:
            logger.error(f"Exception getting bars: {e}")
            return None

    def get_bars_async(self, symbol, bar_size_minutes, starting_time, number_of_bars):
        request_id = self.socket.request_historical_chart(
            symbol, bar_size_minutes, starting_time, number_of_bars
        )
        return request_id

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_token_renewal_scheduler()


def price_monitoring_loop(auth_client, stop_event):
    """Price monitoring loop that runs in a separate thread"""
    while not stop_event.is_set():
        try:
            for instrument_dict in auth_client.contracts:
                if stop_event.is_set():  # Check stop condition
                    break

                d = auth_client.get_latest_prices(instrument_dict["id"])
                MSG = f"Instrument: {instrument_dict} - Last: {d.get('Last', -1)}"
                logger.info(MSG)

                # Use wait instead of sleep to allow immediate stopping
                if stop_event.wait(timeout=1):
                    break

        except Exception as e:
            logger.error(f"Error in price monitoring: {e}")
            if stop_event.wait(timeout=5):  # Wait 5 seconds before retry
                break


if __name__ == "__main__":

    instruments = ["NQ", "ES"]
    stop_event = threading.Event()

    count = 8
    try:
        auth_client = TradovateAuth(instruments=instruments)

        price_thread = threading.Thread(
            target=price_monitoring_loop,
            args=(auth_client, stop_event),
            daemon=True,  # Thread will exit when main program exits
        )
        price_thread.start()

        time.sleep(10)
        # Today's date with 2:30 PM
        starting_time2 = datetime.now().replace(
            hour=14, minute=30, second=0, microsecond=0
        )

        starting_time = datetime(year=2025, month=8, day=29, hour=14, minute=30)
        # starting_time = datetime.now(timezone.utc) - timedelta(hours=6)

        # starting_time = datetime.combine(date.today(), datetime.time(14, 30))
        symbol = "NQU5"
        bar_size = 30
        number_of_bars = 1
        bars = auth_client.get_bars(symbol, bar_size, starting_time, number_of_bars)
        print(bars)

        while True:
            time.sleep(30)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if "auth_client" in locals():
            auth_client.stop_token_renewal_scheduler()
    except Exception as e:
        logger.exception(f"Application error: {e}")
        if "auth_client" in locals():
            auth_client.stop_token_renewal_scheduler()
