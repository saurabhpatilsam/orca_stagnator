import websocket
import threading
import json
import time
import random
import string

# Generate a random session ID
def generate_session(prefix='qs_'):
    return prefix + ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

def on_message(ws, message):
    if 'ping' in message:
        return
    print("[RECV]:", message)

def on_error(ws, error):
    print("[ERROR]:", error)

def on_close(ws, close_status_code, close_msg):
    print("[CLOSED]:", close_status_code, close_msg)

def on_open(ws):
    print("[CONNECTED]")
    # Create session
    chart_session = generate_session("cs_")
    quote_session = generate_session("qs_")

    # Send init and session setup messages
    def send_initial_messages():
        def send(msg):
            ws.send(msg)

        send('~m~36~m~{"m":"set_auth_token","p":["eyJhbGciOiJSUzUxMiIsImtpZCI6IkdaeFUiLCJ0eXAiOiJKV1QifQ.eyJ1c2VyX2lkIjoyNjY2MzYxMSwiZXhwIjoxNzU0NjA0OTg0LCJpYXQiOjE3NTQ1OTA1ODQsInBsYW4iOiIiLCJwcm9zdGF0dXMiOiJub25fcHJvIiwiZXh0X2hvdXJzIjoxLCJwZXJtIjoiY29tZXhfbWluaSxueW1leCxjbWUsY2JvdF9taW5pLG55bWV4X21pbmksY21lX21pbmksY2JvdCxjb21leCIsInN0dWR5X3Blcm0iOiIiLCJtYXhfc3R1ZGllcyI6MiwibWF4X2Z1bmRhbWVudGFscyI6MSwibWF4X2NoYXJ0cyI6MSwibWF4X2FjdGl2ZV9hbGVydHMiOjMsIm1heF9zdHVkeV9vbl9zdHVkeSI6MSwiZmllbGRzX3Blcm1pc3Npb25zIjpbXSwibWF4X2FsZXJ0X2NvbmRpdGlvbnMiOm51bGwsIm1heF9vdmVyYWxsX2FsZXJ0cyI6MjAwMCwibWF4X2FjdGl2ZV9wcmltaXRpdmVfYWxlcnRzIjozLCJtYXhfYWN0aXZlX2NvbXBsZXhfYWxlcnRzIjowLCJtYXhfY29ubmVjdGlvbnMiOjJ9.UAxx63DpsLouqnOMicLuxiX9rUnWazXUVCdgUFUK81aCrJ1PGsedZ3ufqIWZv9DE9ev3BWihvKXb7jsXvb0xWycVN54cRpCly5CgS6QmelI1hPcMEkGZia35Ziak9lrtwrk1sOuvXjmkNvOBYvhVlK10IPrUsMVIKAnsIeYayhQ"]}')
        send(f'~m~42~m~{{"m":"chart_create_session","p":["{chart_session}",""]}}')
        send(f'~m~73~m~{{"m":"quote_create_session","p":["{quote_session}"]}}')
        send(f'~m~87~m~{{"m":"quote_add_symbols","p":["{quote_session}","AAPL",""]}}')  # Example: AAPL
        send(f'~m~74~m~{{"m":"quote_fast_symbols","p":["{quote_session}","AAPL"]}}')

        # Add a chart symbol
        send(f'~m~97~m~{{"m":"resolve_symbol","p":["{chart_session}","symbol_1","AAPL",""]}}')
        send(f'~m~109~m~{{"m":"create_series","p":["{chart_session}","s1","s1","symbol_1","1",300]}}')  # 1-minute bars

    threading.Thread(target=send_initial_messages).start()


# WebSocket URL
ws_url = "wss://data.tradingview.com/socket.io/websocket?from=chart%2FTDdioRhW%2F&date=2025-08-07T09%3A00%3A11&type=chart"

# Define headers
headers = {
    "Origin": "https://www.tradingview.com",
    "User-Agent": "Mozilla/5.0",
    "Connection": "Upgrade",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "Upgrade": "websocket",
}

# If you’re using a proxy, define it here
proxy_host = "localhost"
proxy_port = 9090

ws = websocket.WebSocketApp(
    ws_url,
    header=headers,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

# Run the socket
ws.run_forever(http_proxy_host=proxy_host, http_proxy_port=proxy_port)