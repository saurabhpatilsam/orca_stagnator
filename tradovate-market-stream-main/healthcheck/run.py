import redis
import threading
import time
from datetime import datetime
from publisher.client import get_redis_client
from healthcheck.discord import healthcheck_update_blob, send_discord_message
from loguru import logger
import asyncio

REDIS_CLIENT = get_redis_client()

CHANNELS = ["TRADOVATE_MNQU5_PRICE","TRADOVATE_NQU5_PRICE","TRADOVATE_MESU5_PRICE","TRADOVATE_ESU5_PRICE"]
TIMEOUT_SECONDS = 2  # Trigger alert if no message received in this time window

# Internal state tracking
stream_status = {
    channel: {
        "last_tick_time": time.time(),
        "notified": False
    }
    for channel in CHANNELS
}

def handle_message(channel, message):
    stream_status[channel]["last_tick_time"] = time.time()

    # If we had previously sent a downtime alert, reset the flag now
    if stream_status[channel]["notified"]:
        logger.success(f"[{channel}] Stream resumed.")
        stream_status[channel]["notified"] = False
        asyncio.run(
            send_discord_message(
                healthcheck_update_blob(
                    heading=f"Redis stream resumed: **{channel}**", 
                    description=f"Healthcheck service reports price data is working now",
                    color=2067276
                )
            )
        )


def subscriber_thread(channel_name):
    r = REDIS_CLIENT
    pubsub = r.pubsub()
    pubsub.subscribe(channel_name)

    logger.info(f"[{channel_name}] Subscriber started.")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            handle_message(channel_name, message['data'])

def healthcheck_thread():
    while True:
        current_time = time.time()
        for channel, status in stream_status.items():
            time_since_last_tick = current_time - status["last_tick_time"]
            if time_since_last_tick > TIMEOUT_SECONDS and not status["notified"]:
                logger.error(f"[{channel}] No ticks for {time_since_last_tick:.2f}s. Sending alert.")
                asyncio.run(
                    send_discord_message(
                        healthcheck_update_blob(
                            heading=f"Timeout on Redis: **{channel}**", 
                            description=f"Healthcheck service reports no ticks received for {time_since_last_tick:.2f}s",
                            color=15548997
                        )
                    )
                )
                
                # 🔔 Replace this with your Discord notification
                # send_discord_alert(f"{channel} has stopped receiving price ticks.")
                
                status["notified"] = True

        time.sleep(1)


def main():
    # Start a subscriber thread for each channel
    for channel in CHANNELS:
        t = threading.Thread(target=subscriber_thread, args=(channel,), daemon=True)
        t.start()

    # Start the healthcheck thread
    t = threading.Thread(target=healthcheck_thread, daemon=True)
    t.start()

    # Keep main thread alive forever
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()