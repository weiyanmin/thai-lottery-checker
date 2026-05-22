"""GLO Lottery API integration — check numbers and fetch results."""

import httpx
import asyncio
import logging
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

from bot.config import (
    GLO_CHECK_URL,
    GLO_RESULT_URL,
    GLO_BATCH_SIZE,
    GLO_BATCH_DELAY,
    TIMEZONE,
)

logger = logging.getLogger(__name__)

# Prize amounts in THB
PRIZE_AMOUNTS = {
    "first": 6_000_000,
    "near1": 100_000,
    "second": 200_000,
    "third": 80_000,
    "fourth": 40_000,
    "fifth": 20_000,
    "last2": 2_000,
    "last3f": 4_000,
    "last3b": 4_000,
}

# Human-readable prize names (English keys — translated via i18n in formatters)
PRIZE_NAMES = {
    "first": "First Prize",
    "near1": "Near First Prize",
    "second": "Second Prize",
    "third": "Third Prize",
    "fourth": "Fourth Prize",
    "fifth": "Fifth Prize",
    "last2": "Last 2 Digits",
    "last3f": "First 3 Digits",
    "last3b": "Last 3 Digits",
}


async def check_numbers(
    numbers: list[str], period_date: str
) -> list[dict]:
    """
    Check lottery numbers against a draw date via the GLO API.

    Args:
        numbers: List of 6-digit lottery number strings.
        period_date: Draw date in 'YYYY-MM-DD' format.

    Returns:
        List of dicts: {lottery_num, prize_type, prize_amount}
        prize_type is None if no prize.
    """
    results = []

    # Batch into groups of GLO_BATCH_SIZE
    batches = [
        numbers[i : i + GLO_BATCH_SIZE]
        for i in range(0, len(numbers), GLO_BATCH_SIZE)
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for batch_idx, batch in enumerate(batches):
            if batch_idx > 0:
                await asyncio.sleep(GLO_BATCH_DELAY)

            payload = {
                "number": [{"lottery_num": n} for n in batch],
                "period_date": period_date,
            }

            try:
                resp = await client.post(
                    GLO_CHECK_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
                batch_results = _parse_check_response(data, batch)
                results.extend(batch_results)
            except httpx.HTTPStatusError as e:
                logger.error("GLO API HTTP error %s: %s", e.response.status_code, e)
                # Mark all numbers in this batch as error
                for num in batch:
                    results.append(
                        {"lottery_num": num, "prize_type": None, "prize_amount": 0, "error": True}
                    )
            except Exception as e:
                logger.error("GLO API request failed: %s", e)
                for num in batch:
                    results.append(
                        {"lottery_num": num, "prize_type": None, "prize_amount": 0, "error": True}
                    )

    return results


# Map Thai reward names from the API to our internal prize keys
THAI_PRIZE_MAP = {
    "รางวัลที่ 1": "first",
    "รางวัลข้างเคียงรางวัลที่ 1": "near1",
    "รางวัลที่ 2": "second",
    "รางวัลที่ 3": "third",
    "รางวัลที่ 4": "fourth",
    "รางวัลที่ 5": "fifth",
    "รางวัลเลขท้าย 2 ตัว": "last2",
    "รางวัลเลขหน้า 3 ตัว": "last3f",
    "รางวัลเลขท้าย 3 ตัว": "last3b",
}


def _parse_check_response(data: dict, submitted_numbers: list[str]) -> list[dict]:
    """Parse the GLO API check response.

    Actual API response format:
    {
      "response": {
        "result": [
          {
            "number": "251309",
            "statusType": 1,          # 1 = winner, 2 = no prize
            "status_data": [
              {"reward": "รางวัลที่ 1"}
            ]
          }
        ]
      }
    }
    """
    results = []

    try:
        response = data.get("response", {})
        result_list = response.get("result", [])

        if not isinstance(result_list, list):
            result_list = []

        for item in result_list:
            num = str(item.get("number", ""))
            status_type = item.get("statusType", 2)
            status_data = item.get("status_data", [])

            if status_type == 1 and status_data:
                # Winner — extract all prizes (a number can win multiple)
                prize_types = []
                total_amount = 0
                for sd in status_data:
                    reward_name = sd.get("reward", "")
                    prize_key = THAI_PRIZE_MAP.get(reward_name)
                    if prize_key:
                        prize_types.append(prize_key)
                        total_amount += PRIZE_AMOUNTS.get(prize_key, 0)

                if prize_types:
                    results.append({
                        "lottery_num": num,
                        "prize_type": prize_types[0],  # Primary prize
                        "prize_types": prize_types,     # All prizes
                        "prize_amount": total_amount,
                        "reward_names": [sd.get("reward", "") for sd in status_data],
                    })
                else:
                    # Won but couldn't map the reward name
                    logger.warning("Unknown reward name in status_data: %s", status_data)
                    results.append({
                        "lottery_num": num,
                        "prize_type": "unknown",
                        "prize_amount": 0,
                        "reward_names": [sd.get("reward", "") for sd in status_data],
                    })
            else:
                # No prize
                results.append({
                    "lottery_num": num,
                    "prize_type": None,
                    "prize_amount": 0,
                })

    except Exception as e:
        logger.error("Failed to parse GLO API response: %s", e)

    # Ensure we have results for all submitted numbers
    result_nums = {r["lottery_num"] for r in results}
    for num in submitted_numbers:
        if num not in result_nums:
            results.append({
                "lottery_num": num,
                "prize_type": None,
                "prize_amount": 0,
            })

    return results


async def get_lottery_result(draw_date: str) -> dict | None:
    """
    Fetch full lottery results for a specific draw date.

    Args:
        draw_date: Date string in 'YYYY-MM-DD' format.

    Returns:
        Full result dict or None on failure.
    """
    try:
        dt = datetime.strptime(draw_date, "%Y-%m-%d")
    except ValueError:
        logger.error("Invalid date format: %s", draw_date)
        return None

    payload = {
        "date": dt.strftime("%d"),
        "month": dt.strftime("%m"),
        "year": str(dt.year),
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                GLO_RESULT_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error("Failed to fetch lottery results for %s: %s", draw_date, e)
        return None


def get_draw_dates(count_past: int = 5, count_future: int = 2) -> dict:
    """
    Calculate past and future lottery draw dates.

    Thai lottery draws on the 1st and 16th of every month.

    Returns:
        {"past": [list of past date strings], "future": [list of future date strings]}
    """
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()

    all_dates = []
    # Generate dates spanning several months around today
    for month_offset in range(-6, 6):
        year = today.year + (today.month + month_offset - 1) // 12
        month = (today.month + month_offset - 1) % 12 + 1
        for day in (1, 16):
            try:
                d = date(year, month, day)
                all_dates.append(d)
            except ValueError:
                continue

    all_dates.sort()

    past = [d for d in all_dates if d <= today]
    future = [d for d in all_dates if d > today]

    return {
        "past": [d.strftime("%Y-%m-%d") for d in past[-count_past:]],
        "future": [d.strftime("%Y-%m-%d") for d in future[:count_future]],
    }


def is_draw_day(check_date: date | None = None) -> bool:
    """Check if the given date (or today) is a lottery draw day."""
    if check_date is None:
        tz = ZoneInfo(TIMEZONE)
        check_date = datetime.now(tz).date()
    return check_date.day in (1, 16)


def is_draw_past(period_date: str) -> bool:
    """Check if a draw date has already passed."""
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()
    try:
        draw = datetime.strptime(period_date, "%Y-%m-%d").date()
        return draw <= today
    except ValueError:
        return False
