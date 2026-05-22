"""Check handler — /check command and manual number input flow."""

import logging

from telegram import Update, CallbackQuery
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from bot.database.db import (
    upsert_user, get_user_language, save_tickets, save_check_history,
)
from bot.services.lottery_api import check_numbers, is_draw_past
from bot.services.number_parser import parse_text
from bot.handlers.date_select import build_date_keyboard
from bot.utils.formatters import format_results, format_number_list
from bot.i18n import get_text
from bot.config import MAX_NUMBERS_PER_SUBMISSION

logger = logging.getLogger(__name__)

# Conversation states
WAITING_DATE, WAITING_NUMBERS = range(2)


async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /check — start the number checking flow."""
    user = update.effective_user
    await upsert_user(user.id, user.username, user.first_name)
    lang = await get_user_language(user.id)

    keyboard = build_date_keyboard(lang, callback_prefix="checkdate")
    await update.message.reply_text(
        get_text("select_date", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    return WAITING_DATE


async def start_check_flow(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Start check flow from a menu callback."""
    keyboard = build_date_keyboard(lang, callback_prefix="checkdate")
    await query.edit_message_text(
        get_text("select_date", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection callback for checking."""
    query = update.callback_query
    await query.answer()

    date_str = query.data.replace("checkdate:", "")
    context.user_data["check_date"] = date_str

    user = update.effective_user
    lang = await get_user_language(user.id)

    await query.edit_message_text(
        get_text("date_selected", lang, date=date_str) + "\n\n" +
        get_text("enter_numbers", lang),
        parse_mode="HTML",
    )
    return WAITING_NUMBERS


async def numbers_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input containing lottery numbers."""
    user = update.effective_user
    lang = await get_user_language(user.id)
    text = update.message.text

    # Parse numbers from text
    result = parse_text(text)

    if not result.numbers:
        await update.message.reply_text(
            get_text("no_valid_numbers", lang),
            parse_mode="HTML",
        )
        return WAITING_NUMBERS

    if len(result.numbers) > MAX_NUMBERS_PER_SUBMISSION:
        await update.message.reply_text(
            get_text("too_many_numbers", lang, max=MAX_NUMBERS_PER_SUBMISSION),
            parse_mode="HTML",
        )
        return WAITING_NUMBERS

    # Get the selected date
    period_date = context.user_data.get("check_date")
    if not period_date:
        keyboard = build_date_keyboard(lang, callback_prefix="checkdate")
        await update.message.reply_text(
            get_text("select_date", lang),
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return WAITING_DATE

    numbers = result.numbers

    # Notify about found numbers
    msg = get_text("numbers_found", lang, count=len(numbers))
    if result.invalid_count > 0:
        msg += "\n" + get_text("numbers_invalid_note", lang, count=result.invalid_count)
    await update.message.reply_text(msg, parse_mode="HTML")

    # Check if draw has already happened
    if is_draw_past(period_date):
        # Check immediately
        await update.message.reply_text(get_text("checking", lang), parse_mode="HTML")

        results = await check_numbers(numbers, period_date)
        response = format_results(results, lang)

        # Save to history
        winners = sum(1 for r in results if r.get("prize_type"))
        total_prize = sum(r.get("prize_amount", 0) for r in results if r.get("prize_type"))

        await save_tickets(user.id, numbers, period_date, status="checked")
        await save_check_history(user.id, period_date, len(numbers), winners, total_prize)

        await update.message.reply_text(response, parse_mode="HTML")
    else:
        # Save for future notification
        await save_tickets(user.id, numbers, period_date, status="pending")
        await update.message.reply_text(
            get_text("pending_saved", lang, count=len(numbers), date=period_date),
            parse_mode="HTML",
        )

    # Clean up
    context.user_data.pop("check_date", None)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the current conversation."""
    context.user_data.pop("check_date", None)
    user = update.effective_user
    lang = await get_user_language(user.id)
    await update.message.reply_text("Cancelled.", parse_mode="HTML")
    return ConversationHandler.END


def get_handlers() -> list:
    """Return all handlers for this module."""
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("check", check_command)],
        states={
            WAITING_DATE: [
                CallbackQueryHandler(date_selected, pattern=r"^checkdate:"),
            ],
            WAITING_NUMBERS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, numbers_received),
                CallbackQueryHandler(date_selected, pattern=r"^checkdate:"),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
        per_message=False,
    )
    return [
        conv_handler,
        CallbackQueryHandler(date_selected, pattern=r"^checkdate:"),
    ]
