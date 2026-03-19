from binance.client import Client

from bot.logging_config import setup_logging
from config import API_KEY, API_SECRET, BASE_URL

logger = setup_logging()


def get_client():
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.FUTURES_URL = BASE_URL
    logger.info("Binance client initialized for testnet")
    return client
