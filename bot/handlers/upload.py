"""Upload handler — Excel file upload processing."""

import logging

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from bot.database.db import get_user_language, save_tickets, save_check_history
from bot.services.excel_parser import parse_excel
from bot.services.lottery_api import check_numbers, is_draw_past
from bot.handlers.date_select import build_date_keyboard
from bot.utils.formatters import format_results
from bot.i18n import get_text
from bot.config import MAX_NUMBERS_PER_SUBMISSION

logger = logging.getLogger(__name__)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded Excel files."""
    document = update.message.document
    if not document:
        return

    filename = document.file_name or ""
    if not filename.lower().endswith((".xlsx", ".xls")):
        return  # Not an Excel file — let other handlers deal with it

    user = update.effective_user
    lang = await get_user_language(user.id)

    await update.message.reply_text(
        get_text("excel_processing", lang), parse_mode="HTML"
    )

    try:
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()

        result = parse_excel(bytes(file_bytes))

        if not result.numbers:
            await update.message.reply_text(
                get_text("excel_empty", lang), parse_mode="HTML"
            )
            return

        if len(result.numbers) > MAX_NUMBERS_PER_SUBMISSION:
            result = result._replace(numbers=result.numbers[:MAX_NUMBERS_PER_SUBMISSION])
            await update.message.reply_text(
                get_text("too_many_numbers", lang, max=MAX_NUMBERS_PER_SUBMISSION),
                parse_mode="HTML",
            )

        # Show parse results
        await update.message.reply_text(
            get_text("excel_parsed", lang,
                     valid=len(result.numbers),
                     invalid=result.invalid_count,
                     total=result.total_rows),
            parse_mode="HTML",
        )

        # Store numbers and ask for date
        context.user_data["excel_numbers"] = result.numbers
        keyboard = build_date_keyboard(lang, callback_prefix="exceldate")
        await update.message.reply_text(
            get_text("select_date", lang),
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    except Exception as e:
        logger.error("Excel processing error: %s", e)
        await update.message.reply_text(
            get_text("excel_error", lang), parse_mode="HTML"
        )


async def excel_date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection for Excel upload."""
    query = update.callback_query
    await query.answer()

    date_str = query.data.replace("exceldate:", "")
    user = update.effective_user
    lang = await get_user_language(user.id)

    numbers = context.user_data.pop("excel_numbers", [])
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
        MessageHandler(
            filters.Document.MimeType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            | filters.Document.FileExtension("xlsx")
            | filters.Document.FileExtension("xls"),
            handle_document,
        ),
        CallbackQueryHandler(excel_date_selected, pattern=r"^exceldate:"),
    ]
