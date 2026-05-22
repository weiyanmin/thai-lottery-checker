"""Date selection — reusable inline keyboard for picking draw dates."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.services.lottery_api import get_draw_dates
from bot.utils.formatters import format_date_display
from bot.i18n import get_text


def build_date_keyboard(lang: str = "en", callback_prefix: str = "date") -> InlineKeyboardMarkup:
    """Build an inline keyboard with upcoming and past draw dates."""
    dates = get_draw_dates(count_past=5, count_future=2)
    buttons = []

    # Future draws
    if dates["future"]:
        buttons.append([
            InlineKeyboardButton(
                f"── {get_text('upcoming_draws', lang)} ──",
                callback_data="noop"
            )
        ])
        for d in dates["future"]:
            label = f"◇ {format_date_display(d)}"
            buttons.append([
                InlineKeyboardButton(label, callback_data=f"{callback_prefix}:{d}")
            ])

    # Past draws
    if dates["past"]:
        buttons.append([
            InlineKeyboardButton(
                f"── {get_text('past_draws', lang)} ──",
                callback_data="noop"
            )
        ])
        for d in reversed(dates["past"]):
            label = f"■ {format_date_display(d)}"
            buttons.append([
                InlineKeyboardButton(label, callback_data=f"{callback_prefix}:{d}")
            ])

    return InlineKeyboardMarkup(buttons)
