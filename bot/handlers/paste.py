"""Paste handler — handles pasted number lists from text messages.

This works as a fallback text handler: if a user sends text that isn't
a command and no conversation is active, it tries to parse lottery numbers.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from bot.database.db import get_user_language, save_tickets, save_check_history
from bot.services.number_parser import parse_text
from bot.services.lottery_api import check_numbers, is_draw_past
from bot.handlers.date_select import build_date_keyboard
from bot.utils.formatters import format_results, format_number_list
from bot.i18n import get_text
from bot.config import MAX_NUMBERS_PER_SUBMISSION

logger = logging.getLogger(__name__)


async def handle_pasted_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle freeform text that might contain lottery numbers."""
    user = update.effective_user
    lang = await get_user_language(user.id)
    text = update.message.text

    result = parse_text(text)

    if not result.numbers:
        # Not lottery numbers — ignore silently
        return

    if len(result.numbers) > MAX_NUMBERS_PER_SUBMISSION:
        result = result._replace(numbers=result.numbers[:MAX_NUMBERS_PER_SUBMISSION])
        await update.message.reply_text(
            get_text("too_many_numbers", lang, max=MAX_NUMBERS_PER_SUBMISSION),
            parse_mode="HTML",
        )

    # Store numbers and show found count
    context.user_data["paste_numbers"] = result.numbers

    msg = get_text("numbers_found", lang, count=len(result.numbers))
    if result.invalid_count > 0:
        msg += "\n" + get_text("numbers_invalid_note", lang, count=result.invalid_count)

    # Show numbers found + date selection
    number_display = format_number_list(result.numbers[:20])  # Show first 20
    if len(result.numbers) > 20:
        number_display += f"\n... and {len(result.numbers) - 20} more"

    keyboard = build_date_keyboard(lang, callback_prefix="pastedate")
    await update.message.reply_text(
        f"{msg}\n\n{number_display}\n\n" + get_text("select_date", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def paste_date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection for pasted numbers."""
    query = update.callback_query
    await query.answer()

    date_str = query.data.replace("pastedate:", "")
    user = update.effective_user
    lang = await get_user_language(user.id)

    numbers = context.user_data.pop("paste_numbers", [])
    if not numbers:
        await query.edit_message_text(
            get_text("no_valid_numbers", lang), parse_mode="HTML"
        )
        return

    await query.edit_message_text(
        get_text("date_selected", lang, date=date_str),
        parse_mode="HTML",
    )

    if is_draw_past(date_str):
        await context.bot.send_message(
            chat_id=user.id,
            text=get_text("checking", lang),
            parse_mode="HTML",
        )

        results = await check_numbers(numbers, date_str)
        response = format_results(results, lang)

        winners = sum(1 for r in results if r.get("prize_type"))
        total_prize = sum(r.get("prize_amount", 0) for r in results if r.get("prize_type"))

        await save_tickets(user.id, numbers, date_str, status="checked")
        await save_check_history(user.id, date_str, len(numbers), winners, total_prize)

        await context.bot.send_message(
            chat_id=user.id, text=response, parse_mode="HTML"
        )
    else:
        await save_tickets(user.id, numbers, date_str, status="pending")
        await context.bot.send_message(
            chat_id=user.id,
            text=get_text("pending_saved", lang, count=len(numbers), date=date_str),
            parse_mode="HTML",
        )


def get_handlers() -> list:
    """Return all handlers for this module."""
    return [
        CallbackQueryHandler(paste_date_selected, pattern=r"^pastedate:"),
        # The text handler is registered with low priority (group=1)
        # so it doesn't interfere with ConversationHandlers
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_pasted_text,
        ),
    ]
