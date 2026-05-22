"""History handler — /history command."""

import logging

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes, CommandHandler

from bot.database.db import get_user_language, get_user_history
from bot.utils.formatters import format_date_display
from bot.i18n import get_text

logger = logging.getLogger(__name__)


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /history — show past check results."""
    user = update.effective_user
    lang = await get_user_language(user.id)

    history = await get_user_history(user.id)
    if not history:
        await update.message.reply_text(
            get_text("history_empty", lang), parse_mode="HTML"
        )
        return

    lines = [get_text("history_title", lang)]
    for entry in history:
        lines.append(get_text("history_entry", lang,
            date=format_date_display(entry["period_date"]),
            winners=entry["winners"],
            total=entry["total_numbers"],
            prize=f"{entry['total_prize']:,}",
        ))

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def show_history(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show history from a callback query (menu)."""
    user = query.from_user
    history = await get_user_history(user.id)

    if not history:
        await query.edit_message_text(
            get_text("history_empty", lang), parse_mode="HTML"
        )
        return

    lines = [get_text("history_title", lang)]
    for entry in history:
        lines.append(get_text("history_entry", lang,
            date=format_date_display(entry["period_date"]),
            winners=entry["winners"],
            total=entry["total_numbers"],
            prize=f"{entry['total_prize']:,}",
        ))

    await query.edit_message_text("\n".join(lines), parse_mode="HTML")


def get_handlers() -> list:
    """Return all handlers for this module."""
    return [CommandHandler("history", history_command)]
