from concurrent.futures import ThreadPoolExecutor

import requests

from tradovate.api import TradovateAuth
from helper.logging_setup import logger
import time
from publisher.client import get_redis_client
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
from dotenv import load_dotenv
import os

load_dotenv()


def fetch_and_publish_price(instrument_dict, auth_client, redis_client):
    instrument = instrument_dict["name"]
    logger.success(f"Started publishing price for: {instrument}")
    while True:
        try:
            contract = auth_client.get_latest_prices(instrument_dict["id"])
            last_price = contract.get("Last", -1)
            if last_price == -1:
                logger.error(f"No price found for {instrument}")
                continue
            msg = f"Instrument: {instrument_dict} - Last: {last_price}"
            # logger.info(msg)

            uk_time_now = (
                datetime.now(timezone.utc)
                .astimezone(ZoneInfo("Europe/London"))
                .strftime("%Y-%m-%d %H:%M:%S.%f")
            )

            price_data = {
                "TIMESTAMP": uk_time_now,
                "LAST": last_price,
                "INSTRUMENT": instrument,
            }
            channel_name = f"TRADOVATE_{instrument}_PRICE"
            redis_client.publish(channel_name, json.dumps(price_data))
            time.sleep(0.01)  # or increase to reduce Redis load
        except Exception as e:
            logger.error(f"Error for {instrument}: {e}")
            time.sleep(1)  # backoff in case of repeated errors


if __name__ == "__main__":

    instruments = ["MNQ", "MES", "NQ", "ES"]
    try:
        RedisPublisher = get_redis_client()
        # This will now retry authentication up to 2 times before raising
        auth_client = TradovateAuth(instruments=instruments)

        time.sleep(5)  # wait for auth/session to stabilize

        with ThreadPoolExecutor(max_workers=len(auth_client.contracts)) as executor:
            for instrument_dict in auth_client.contracts:
                executor.submit(
                    fetch_and_publish_price,
                    instrument_dict,
                    auth_client,
                    RedisPublisher,
                )

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if "auth_client" in locals():
            auth_client.stop_token_renewal_scheduler()
    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"Authentication failed after 2 retry attempts: {e}")
        if "auth_client" in locals():
            auth_client.stop_token_renewal_scheduler()
    except Exception as e:
        logger.exception(f"Application error: {e}")
        if "auth_client" in locals():
            auth_client.stop_token_renewal_scheduler()
