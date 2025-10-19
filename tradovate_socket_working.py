from datetime import datetime, timedelta

import websocket
import json
import threading
import time
from helper.logging_setup import logger
from helper.orca_enums import UnderlyingType


class TradovateSocket:
    def __init__(
        self, md_access_token, contracts: [str], price_callback=None, bars_callback=None, ticks_callback=None
    ):
        self.websocket = None
        self.ws_url = "wss://md-demo.tradovateapi.com/v1/websocket"
        self.authorized = False
        self.stop_flag = False
        self.connection_closed = False
        self.heartbeat_timer = None
        self.last_heartbeat_time = None
        self.ws_thread = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 20
        self.reconnect_lock = threading.Lock()
        self.price_data = {}
        self.request_id = 1

        self.chart_data = {}  # Store chart data by request_id
        self.chart_bar_data_timestamp = {}  # Store chart data by request_id
        self.chart_data_ready = {}  # track when chart data is complete
        self.chart_data_event = {}  # track when chart data is complete

        for contract in contracts:
            self.price_data[contract["id"]] = {}

        self.md_access_token = md_access_token
        self.contracts = contracts
        self.price_callback = price_callback
        self.bars_callback = bars_callback

        self.ticks_callback = ticks_callback

    def connect_websocket(self):
        """Connect or reconnect to WebSocket"""
        if not self.md_access_token:
            logger.info("No MD access token available")
            return None

        logger.info("Connecting to Market Data WebSocket...")
        websocket.enableTrace(False)
        self.connection_closed = False
        self.websocket = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

        self.ws_thread = threading.Thread(target=self.websocket.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

        return self.ws_thread

    def start_heartbeat(self):
        """Start proactive heartbeat sending every 2.5 seconds"""

        def send_heartbeat():
            if not self.connection_closed and self.websocket:
                try:
                    self.websocket.send("[]")
                    self.last_heartbeat_time = time.time()
                    logger.debug("Proactive heartbeat sent")

                    # schedule next heartbeat
                    if not self.connection_closed:
                        self.heartbeat_timer = threading.Timer(
                            2.4, send_heartbeat
                        )  # Slightly less than 2.5s
                        self.heartbeat_timer.daemon = True
                        self.heartbeat_timer.start()
                except Exception as e:
                    logger.error(f"Failed to send proactive heartbeat: {e}")
                    self.connection_closed = True

        # Start the heartbeat cycle
        self.heartbeat_timer = threading.Timer(2.4, send_heartbeat)
        self.heartbeat_timer.daemon = True
        self.heartbeat_timer.start()
        logger.info("Started proactive heartbeat timer")

    def stop_heartbeat(self):
        """Stop the heartbeat timer"""
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
            self.heartbeat_timer = None
            logger.debug("Stopped heartbeat timer")

    def on_open(self, ws):
        logger.info("WebSocket connection opened")
        self.reconnect_attempts = 0
        self.authorized = False
        self.connection_closed = False
        self.authorize_md_websocket()
        # start heartbeat immediately after connection
        self.start_heartbeat()
        # delay data requests to ensure authorization completes
        threading.Timer(3.0, self.start_data_requests).start()

    def authorize_md_websocket(self):
        if not self.websocket or not self.md_access_token:
            logger.error("WebSocket not connected or no MD token")
            return

        message = f"authorize\n{self.request_id}\n\n{self.md_access_token}"
        logger.info("Authorizing WebSocket...")
        try:
            self.websocket.send(message)
            self.request_id += 1
        except Exception as e:
            logger.error(f"Failed to send authorization: {e}")
            self.connection_closed = True

    def start_data_requests(self):
        if self.connection_closed or not self.websocket or not self.authorized:
            logger.warning(
                f"Connection not ready for data requests. Closed: {self.connection_closed}, WS: {bool(self.websocket)}, Auth: {self.authorized}"
            )
            return

        logger.info("Starting market data subscriptions...")
        for contract in self.contracts:
            if self.connection_closed:
                break
            self.request_quote(contract["name"])
            time.sleep(0.1)

    def on_message(self, ws, message):
        logger.debug(f"Raw message received: {message}")

        try:
            if message == "h":
                try:
                    ws.send("[]")
                    logger.debug("Responded to server heartbeat")
                except Exception as e:
                    logger.error(f"Failed to respond to server heartbeat: {e}")
                return

            elif message == "o":
                logger.debug("Opening frame received")
                return

            elif message == "c":
                logger.debug("Close frame received")
                return

            # Handle data messages
            elif message.startswith("a["):
                auth_data = json.loads(message[2:-1])

                if auth_data.get("s") == 200 and not self.authorized:
                    self.authorized = True
                    logger.info("WebSocket AUTHORIZED")
                    return

                elif auth_data.get("e") == "shutdown":
                    reason_code = auth_data.get("d", {}).get("reasonCode", "Unknown")
                    logger.error(f"Server shutdown connection: {reason_code}")

                    if reason_code == "DeviceQuotaReached":
                        logger.error(
                            "DEVICE QUOTA REACHED - Check for other running instances Ex: NT8!"
                        )
                    else:
                        logger.error(f"Server shutdown : {reason_code}")

                    self.stop_flag = True
                    self.connection_closed = True
                    return

                elif auth_data.get("e") == "md":
                    self.get_price(auth_data)
                elif auth_data.get("e") == "chart":
                    self.process_chart_message(auth_data)
            else:
                logger.warning(f"Unhandled message: {repr(message)}")

        except Exception as e:
            logger.error(f"Error parsing message: {e}")

    def get_price(self, auth_data):
        md_data = auth_data.get("d", {})
        for quote in md_data.get("quotes", []):
            entries = quote.get("entries", {})
            contract_id = quote.get("contractId")  # Get the contract ID

            if not contract_id:
                logger.warning("Received quote without contract ID")
                continue

            self.price_data[contract_id] = {
                "Bid": entries.get("Bid", {}).get("price"),
                "Ask": entries.get("Offer", {}).get("price"),
                "Last": entries.get("Trade", {}).get("price"),
            }

            if self.price_callback:
                self.price_callback(self.price_data)

    def on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.authorized = False
        self.connection_closed = True
        self.stop_heartbeat()  # Stop heartbeat timer

        logger.warning(f"WebSocket closed with code {close_status_code}: {close_msg}")

        # Only reconnect if we haven't been explicitly stopped
        if not self.stop_flag:
            self.reconnect()

    def reconnect(self):
        with self.reconnect_lock:
            if self.stop_flag:
                logger.info("Stop flag set, not reconnecting")
                return

            if self.reconnect_attempts >= self.max_reconnect_attempts:
                logger.error("Max reconnect attempts reached. Giving up.")
                return

            delay = min(2**self.reconnect_attempts, 60)  # Cap at 60 seconds
            logger.info(
                f"Reconnecting in {delay} seconds... (attempt {self.reconnect_attempts + 1})"
            )
            time.sleep(delay)

            self.reconnect_attempts += 1
            self.connect_websocket()

    def request_quote(self, symbol):
        if not self.websocket or self.connection_closed:
            logger.warning("WebSocket not connected or connection closed")
            return

        try:
            subscribe_quote = "md/subscribeQuote"
            message = f"{subscribe_quote}\n{self.request_id}\n\n{json.dumps({'symbol': symbol})}"
            logger.info(f"Subscribing to quote for {symbol}")
            self.websocket.send(message)
            self.request_id += 1

        except Exception as e:
            logger.error(f"Failed to send quote request for {symbol}: {e}")
            self.connection_closed = True

    def request_historical_chart(
        self, symbol, bar_size_minutes, starting_time, number_of_bars, store_data=True
    ):
        """
        Request historical chart data for a specific symbol with custom parameters.

        Parameters:
        - symbol (str): Contract symbol (e.g., "ESU9") or contract ID
        - bar_size_minutes (int): Size of each bar in minutes (e.g., 1, 5, 15, 30, 60)
        - starting_time (datetime): Starting point for historical data
        - number_of_bars (int): Number of bars to retrieve
        - store_data (bool): Whether to store data in self.chart_data for later retrieval
        - callback (function, optional): Custom callback function to process chart data

        Returns:
        - request_id (int): The ID of this request for tracking
        """
        if not self.websocket or self.connection_closed:
            logger.warning("WebSocket not connected or connection closed")
            return None

        if not self.authorized:
            logger.warning("WebSocket not authorized yet")
            return None

        try:
            # Convert datetime to ISO format string
            closest_timestamp = starting_time.isoformat()
            closest_timestamp_to_send = (
                starting_time + timedelta(minutes=bar_size_minutes)
            ).isoformat()
            number_of_bars_to_send = number_of_bars + 1

            if not closest_timestamp.endswith("Z") and "+" not in closest_timestamp:
                closest_timestamp += "Z"
                closest_timestamp_to_send += "Z"

            # Build the request body
            request_body = {
                "symbol": symbol,
                "chartDescription": {
                    "underlyingType": UnderlyingType.TICK.value,
                    "elementSize": bar_size_minutes,
                    "elementSizeUnit": "UnderlyingUnits",
                },
                "timeRange": {
                    "closestTimestamp": closest_timestamp_to_send,
                    "asMuchAsElements": number_of_bars_to_send,
                },
            }

            current_request_id = self.request_id
            self.chart_bar_data_timestamp[current_request_id] = starting_time
            # Store callback and data storage preference
            self.chart_data_ready[current_request_id] = self.bars_callback

            if store_data:
                self.chart_data[current_request_id] = {
                    "symbol": symbol,
                    "bars": [],
                    "complete": False,
                    "request_params": {
                        "bar_size_minutes": bar_size_minutes,
                        "starting_time": starting_time,
                        "number_of_bars": number_of_bars,
                    },
                }
                self.chart_data_ready[current_request_id] = threading.Event()

            # Send the request
            message = f"md/getChart\n{self.request_id}\n\n{json.dumps(request_body)}"
            logger.info(
                f"Requesting historical chart for {symbol}: {bar_size_minutes}min bars, starting from {starting_time}, {number_of_bars} bars"
            )
            self.websocket.send(message)

            self.request_id += 1
            return current_request_id

        except Exception as e:
            logger.error(f"Failed to request historical chart for {symbol}: {e}")
            return None

    def request_historical_tick_data(
        self, symbol,starting_date ,ending_date , store_data=True
    ):
        """
        Request historical chart data for a specific symbol with custom parameters.

        Parameters:
        - symbol (str): Contract symbol (e.g., "ESU9") or contract ID
        - bar_size_minutes (int): Size of each bar in minutes (e.g., 1, 5, 15, 30, 60)
        - starting_time (datetime): Starting point for historical data
        - number_of_bars (int): Number of bars to retrieve
        - store_data (bool): Whether to store data in self.chart_data for later retrieval
        - callback (function, optional): Custom callback function to process chart data

        Returns:
        - request_id (int): The ID of this request for tracking
        """
        if not self.websocket or self.connection_closed:
            logger.warning("WebSocket not connected or connection closed")
            return None

        if not self.authorized:
            logger.warning("WebSocket not authorized yet")
            return None

        try:

            # Build the request body
            request_body = {
                "symbol": symbol,
                "chartDescription": {
                    "underlyingType": UnderlyingType.TICK.value,
                    "elementSize": 1,
                    "elementSizeUnit": "UnderlyingUnits",
                },
                "timeRange": {
                    "closestTimestamp": ending_date,
                    "asFarAsTimestamp":  starting_date,
                },
            }

            print(request_body)

            current_request_id = self.request_id
            self.chart_bar_data_timestamp[current_request_id] = starting_date
            # Store callback and data storage preference
            self.chart_data_ready[current_request_id] = self.bars_callback

            if store_data:
                self.chart_data[current_request_id] = {
                    "symbol": symbol,
                    "bars": [],
                    "complete": False,
                    "request_params": {
                        "starting_time": starting_date,
                    },
                }
                self.chart_data_ready[current_request_id] = threading.Event()

            # Send the request
            message = f"md/getChart\n{self.request_id}\n\n{json.dumps(request_body)}"
            logger.info(
                f"Requesting Tick data for {symbol}  starting from {starting_date} to {ending_date} bars"
            )
            self.websocket.send(message)

            self.request_id += 1
            return current_request_id

        except Exception as e:
            logger.error(f"Failed to request tick by tick data for {symbol}: {e}")
            return None

    def get_historical_chart_data(self, request_id, timeout=30):
        """
        Get the historical chart data for a specific request.
        This method blocks until data is received or timeout occurs.

        Parameters:
        - request_id (int): The request ID returned by get_historical_chart_data
        - timeout (int): Maximum seconds to wait for data

        Returns:
        - dict: Chart data with bars, or None if timeout/error
        """
        if request_id not in self.chart_data_ready:
            logger.error(f"No chart request found for ID {request_id}")
            return None

        # Wait for data to be ready
        if self.chart_data_ready[request_id].wait(timeout):
            return self.chart_data.get(request_id)
        else:
            logger.warning(f"Timeout waiting for chart data for request {request_id}")
            return None

    def is_chart_data_ready(self, request_id):
        """Check if chart data is ready for a specific request ID"""
        return request_id in self.chart_data and self.chart_data[request_id]["complete"]

    def process_chart_message(self, message_data):
        """
        Process incoming chart data messages.
        Update your existing on_message method to call this.
        """
        if message_data.get("e") == "chart":
            chart_data = message_data.get("d", {})
            # bar_data = {"bars": []}
            for chart in chart_data.get("charts", []):
                chart_id = chart.get("id")
                trade_date = chart.get("td")

                # Check if this is end of historical data
                if chart.get("eoh", False):
                    logger.info(f"End of historical data reached for chart {chart_id}")
                    # Mark as complete
                    for req_id, data in self.chart_data.items():
                        if not data["complete"]:  # Find the incomplete request
                            data["complete"] = True
                            self.chart_data_ready[req_id].set()  # Signal data is ready
                            break
                    continue

                # Process bars
                bars = chart.get("bars", [])
                if bars:
                    logger.info(
                        f"Received {len(bars)} bars for chart {chart_id}, trade date: {trade_date}"
                    )

                    processed_bars = []
                    if len(bars) < 1:
                        logger.warning(f"No bars for chart {chart_id}")
                        return

                    for bar in bars[:-1]:
                        processed_bar = {
                            "timestamp": bar["timestamp"],
                            "datetime": datetime.fromisoformat(
                                bar["timestamp"].replace("Z", "+00:00")
                            ),
                            "open": bar["open"],
                            "high": bar["high"],
                            "low": bar["low"],
                            "close": bar["close"],
                            "volume": {
                                "up": bar.get("upVolume", 0),
                                "down": bar.get("downVolume", 0),
                                "bid": bar.get("bidVolume", 0),
                                "offer": bar.get("offerVolume", 0),
                            },
                            "ticks": {
                                "up": bar.get("upTicks", 0),
                                "down": bar.get("downTicks", 0),
                            },
                        }
                        processed_bars.append(processed_bar)

                    # Store data in the appropriate request
                    for req_id, bar_data in self.chart_data.items():
                        if not bar_data["complete"]:  # Find the incomplete request
                            bar_data["bars"].extend(processed_bars)
                            break

                    if self.bars_callback:
                        bar_starting_time = self.chart_bar_data_timestamp.get(req_id)
                        logger.info(
                            "Received {} bars for {}".format(
                                len(bar_data["bars"]), bar_starting_time
                            )
                        )
                        self.bars_callback(bar_data, chart["id"])

                    # Call custom callbacks
                    # for request_id, callback in self.bars_callback.items():
                    #     try:
                    #         sle(processed_bars, chart_id)
                    #     except Exception as e:
                    #         logger.error(f"Error in chart callback: {e}")

    def stop(self):
        logger.info("Stopping TradovateSocket...")
        self.stop_flag = True
        self.connection_closed = True
        self.stop_heartbeat()
        if self.websocket:
            self.websocket.close()
