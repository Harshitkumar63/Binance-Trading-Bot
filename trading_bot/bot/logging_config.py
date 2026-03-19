import logging
import os
from logging.handlers import RotatingFileHandler

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log")


def setup_logging():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    logger = logging.getLogger("trading_bot")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")

    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=2_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
