import logging
import os
from logging.handlers import RotatingFileHandler

from .config import LOG_DIR


def get_logger(name: str = "editgenius") -> logging.Logger:
    """Return a configured logger instance (singleton per name)."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # already configured

    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # Console handler
    console_hdlr = logging.StreamHandler()
    console_hdlr.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(console_hdlr)

    # Rotating file handler (5 MB per file, keep 3 backups)
    os.makedirs(LOG_DIR, exist_ok=True)
    file_hdlr = RotatingFileHandler(
        os.path.join(LOG_DIR, "editgenius.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_hdlr.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    )
    logger.addHandler(file_hdlr)

    return logger