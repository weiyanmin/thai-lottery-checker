"""Telegram initData validation — HMAC-SHA256 signature verification."""

import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qs, unquote

from bot.config import BOT_TOKEN

logger = logging.getLogger(__name__)


def validate_init_data(init_data: str) -> dict | None:
    """Validate Telegram WebApp initData and return user info.

    Returns:
        User dict if valid, None if invalid.
    """
    if not init_data:
        return None

    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        received_hash = parsed.get("hash", [None])[0]

        if not received_hash:
            return None

        # Build data-check-string
        data_pairs = []
        for key, values in parsed.items():
            if key == "hash":
                continue
            data_pairs.append(f"{key}={values[0]}")
        data_pairs.sort()
        data_check_string = "\n".join(data_pairs)

        # Create secret key & verify
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
        expected_hash = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_hash, received_hash):
            return None

        # Extract user
        user_json = parsed.get("user", [None])[0]
        if user_json:
            return json.loads(unquote(user_json))
        return {"id": 0, "first_name": "Unknown"}

    except Exception as e:
        logger.error("initData validation failed: %s", e)
        return None
