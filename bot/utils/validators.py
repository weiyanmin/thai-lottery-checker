"""Validators — number and input validation utilities."""

import re

_LOTTERY_PATTERN = re.compile(r"^\d{6}$")


def is_valid_lottery_number(number: str) -> bool:
    """Check if a string is a valid 6-digit lottery number."""
    return bool(_LOTTERY_PATTERN.match(number.strip()))


def sanitize_number(number: str) -> str | None:
    """Clean and validate a lottery number. Returns None if invalid."""
    s = number.strip()
    if s.isdigit():
        s = s.zfill(6)
    if _LOTTERY_PATTERN.match(s):
        return s
    return None


def validate_number_list(numbers: list[str]) -> tuple[list[str], int]:
    """Validate a list of numbers, returning (valid, invalid_count)."""
    valid = []
    seen = set()
    invalid = 0
    for n in numbers:
        s = sanitize_number(n)
        if s and s not in seen:
            seen.add(s)
            valid.append(s)
        elif not s:
            invalid += 1
    return valid, invalid
