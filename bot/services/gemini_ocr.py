"""Gemini Vision OCR — extract lottery numbers from ticket images.

Implements a 3-model fallback chain:
  gemini-2.5-flash → gemini-2.0-flash → gemini-1.5-flash
Each model has 1,500 free requests/day, giving 4,500 total daily scans.
"""

import asyncio
import base64
import json
import logging
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from bot.config import GEMINI_API_KEY, GEMINI_MODELS, TIMEZONE

logger = logging.getLogger(__name__)

_GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

_PROMPT = (
    "You are an OCR assistant for Thai government lottery tickets. "
    "Extract ALL 6-digit lottery numbers visible in this image. "
    "Thai lottery tickets have a 6-digit number printed prominently. "
    "Return ONLY a valid JSON array of strings containing the 6-digit numbers. "
    'Example: ["123456", "789012"]. '
    "If no valid 6-digit lottery numbers are found, return an empty array []. "
    "Do NOT include any explanation, markdown, or text outside the JSON array."
)


class GeminiOCR:
    """Manages Gemini Vision API calls with automatic model fallback."""

    def __init__(self):
        self._models = list(GEMINI_MODELS)
        self._current_index = 0
        self._lock = asyncio.Lock()
        self._last_reset_date: str = ""
        self._all_exhausted = False

    async def extract_numbers(self, image_bytes: bytes) -> list[str] | None:
        """
        Extract 6-digit lottery numbers from an image.

        Returns:
            list[str]: Extracted numbers, or empty list if none found.
            None: If ALL model quotas are exhausted (caller shows 'unavailable').
        """
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured.")
            return None

        # Reset model index at midnight ICT each day
        await self._maybe_daily_reset()

        if self._all_exhausted:
            return None

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        # Try each model in the fallback chain starting from current index
        async with self._lock:
            start_index = self._current_index

        for attempt in range(len(self._models)):
            async with self._lock:
                if self._current_index >= len(self._models):
                    self._all_exhausted = True
                    return None
                model = self._models[self._current_index]

            url = _GEMINI_BASE_URL.format(model=model)
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": _PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": b64_image,
                                }
                            },
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 256,
                },
            }

            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    resp = await client.post(
                        url,
                        json=payload,
                        params={"key": GEMINI_API_KEY},
                        headers={"Content-Type": "application/json"},
                    )

                    if resp.status_code == 429:
                        logger.warning(
                            "Rate limited (429) on %s — switching to next model.",
                            model,
                        )
                        async with self._lock:
                            # Only advance if we haven't already
                            if self._models[self._current_index] == model:
                                self._current_index += 1
                                if self._current_index >= len(self._models):
                                    self._all_exhausted = True
                                    logger.error(
                                        "All Gemini models exhausted for today."
                                    )
                                    return None
                        continue

                    resp.raise_for_status()
                    data = resp.json()
                    return self._parse_response(data)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(
                        "Rate limited (429) on %s — switching to next model.",
                        model,
                    )
                    async with self._lock:
                        if self._models[self._current_index] == model:
                            self._current_index += 1
                            if self._current_index >= len(self._models):
                                self._all_exhausted = True
                                return None
                    continue
                else:
                    logger.error("Gemini API error on %s: %s", model, e)
                    return []
            except Exception as e:
                logger.error("Gemini request failed on %s: %s", model, e)
                return []

        # All models tried
        return None

    def _parse_response(self, data: dict) -> list[str]:
        """Parse the Gemini API response to extract lottery numbers."""
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                return []

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                return []

            text = parts[0].get("text", "").strip()

            # Try to parse as JSON
            # Remove markdown code fences if present
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            text = text.strip()

            numbers = json.loads(text)

            if not isinstance(numbers, list):
                return []

            # Validate: keep only strings that are exactly 6 digits
            valid = []
            for n in numbers:
                s = str(n).strip()
                if re.match(r"^\d{6}$", s):
                    valid.append(s)

            logger.info("Gemini OCR extracted %d valid numbers.", len(valid))
            return valid

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error("Failed to parse Gemini response: %s", e)
            return []

    async def _maybe_daily_reset(self):
        """Reset model index to the first model at the start of each new day (ICT)."""
        tz = ZoneInfo(TIMEZONE)
        today = datetime.now(tz).strftime("%Y-%m-%d")

        async with self._lock:
            if today != self._last_reset_date:
                self._last_reset_date = today
                self._current_index = 0
                self._all_exhausted = False
                logger.info("Daily reset: Gemini model index reset to %s.", self._models[0])

    @property
    def current_model(self) -> str | None:
        """Return the current active model name, or None if exhausted."""
        if self._all_exhausted or self._current_index >= len(self._models):
            return None
        return self._models[self._current_index]


# Module-level singleton
gemini_ocr = GeminiOCR()
