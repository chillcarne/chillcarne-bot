import logging
import sys
from core.config import LOG_LEVEL, LOG_FILE_PATH

def setup_logger(logger_name: str) -> logging.Logger:
    # Root logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(LOG_LEVEL)

    # Log format
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(fmt)

    # Console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if LOG_FILE_PATH:
        file_handler = logging.FileHandler(LOG_FILE_PATH)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Disable log propagation to avoid duplicate logs
    logger.propagate = False

    return logger
