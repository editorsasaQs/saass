import logging
import os
from urllib.parse import quote_plus

import requests

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .logger import get_logger

logger = get_logger(__name__)


def send_telegram_message(text: str):
    """Send a Telegram message if credentials are provided."""
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        logger.debug("Telegram credentials not provided; skipping notification.")
        return

    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id="
        f"{TELEGRAM_CHAT_ID}&text={quote_plus(text)}"
    )
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            logger.warning("Telegram send failed: %s", resp.text)
        else:
            logger.info("Telegram message sent")
    except Exception as exc:
        logger.exception("Telegram send exception: %s", exc)