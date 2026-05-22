"""Formatters — message building helpers."""

from bot.i18n import get_text
from bot.services.lottery_api import PRIZE_AMOUNTS


def format_results(results: list[dict], lang: str = "en") -> str:
    """Format a list of check results into a user-facing message."""
    lines = []
    winners = 0
    total_prize = 0

    for res in results:
        num = res["lottery_num"]
        if res.get("prize_type"):
            winners += 1
            amount = res.get("prize_amount", PRIZE_AMOUNTS.get(res["prize_type"], 0))
            total_prize += amount
            prize_name = get_text(f"prize_{res['prize_type']}", lang)
            lines.append(get_text("winner", lang,
                                  number=num, prize=prize_name,
                                  amount=f"{amount:,}"))
        else:
            lines.append(get_text("no_prize", lang, number=num))

    detail = "\n".join(lines)
    summary = get_text("summary", lang,
                       winners=winners, total=len(results),
                       amount=f"{total_prize:,}")
    return f"{detail}{summary}"


def format_number_list(numbers: list[str]) -> str:
    """Format a list of numbers for display."""
    return "\n".join(f"• <code>{n}</code>" for n in numbers)


def format_date_display(date_str: str) -> str:
    """Format a YYYY-MM-DD date for user display."""
    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except ValueError:
        return date_str
