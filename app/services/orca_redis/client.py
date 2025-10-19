import os
import redis
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def get_redis_client():
    """
    Establishes a connection to Azure Cache for Redis and returns the client object.
    """
    # Working configuration from test_redis_connection.py
    REDIS_HOST = "redismanager.redis.cache.windows.net"
    REDIS_PORT = 6380
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')  # Must set REDIS_PASSWORD environment variable

    try:
        r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True,
            ssl=True,
            ssl_cert_reqs=None,  # Disable SSL certificate verification for Azure Cache
        )

        # Test the connection
        r.ping()
        logger.info(
            f"Connected to Azure Cache for Redis at {REDIS_HOST}:{REDIS_PORT} successfully!"
        )
        return r
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Failed to connect to Azure Cache for Redis: {e}")
        return None
    except ValueError as e:
        logger.error(f"Invalid Redis port number in environment variables: {e}")
        return None


if __name__ == "__main__":
    get_redis_client()
