"""Text number parser — extracts lottery numbers from pasted text."""

import re
import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)

_LOTTERY_PATTERN = re.compile(r"\d{6}")
_STRICT_PATTERN = re.compile(r"^\d{6}$")


class ParseResult(NamedTuple):
    numbers: list[str]
    invalid_count: int


def parse_text(text: str) -> ParseResult:
    """Extract 6-digit lottery numbers from freeform text."""
    text = text.strip()
    if not text:
        return ParseResult(numbers=[], invalid_count=0)

    tokens = re.split(r"[,;\s\n\r\t|]+", text)

    numbers = []
    seen = set()
    invalid_count = 0

    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.isdigit() and len(token) <= 6:
            token = token.zfill(6)
        if _STRICT_PATTERN.match(token):
            if token not in seen:
                seen.add(token)
                numbers.append(token)
        elif token.isdigit() and len(token) > 6:
            matches = [token[i:i+6] for i in range(0, len(token) - 5, 6)]
            for m in matches:
                if _STRICT_PATTERN.match(m) and m not in seen:
                    seen.add(m)
                    numbers.append(m)
        else:
            found = _LOTTERY_PATTERN.findall(token)
            if found:
                for f in found:
                    if f not in seen:
                        seen.add(f)
                        numbers.append(f)
            else:
                invalid_count += 1

    return ParseResult(numbers=numbers, invalid_count=invalid_count)
