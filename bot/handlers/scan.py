"""Scan handler — lottery ticket image scanning via Gemini Vision."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from bot.database.db import get_user_language, save_tickets, save_check_history
from bot.services.gemini_ocr import gemini_ocr
from bot.services.lottery_api import check_numbers, is_draw_past
from bot.handlers.date_select import build_date_keyboard
from bot.utils.formatters import format_results, format_number_list
from bot.i18n import get_text

logger = logging.getLogger(__name__)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages — scan lottery ticket."""
    user = update.effective_user
    lang = await get_user_language(user.id)

    await update.message.reply_text(
        get_text("scanning", lang), parse_mode="HTML"
    )

    # Download the photo (get the highest resolution)
    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_bytes = await file.download_as_bytearray()

    # Extract numbers using Gemini OCR
    numbers = await gemini_ocr.extract_numbers(bytes(image_bytes))

    if numbers is None:
        # All models exhausted
        await update.message.reply_text(
            get_text("scan_unavailable", lang), parse_mode="HTML"
        )
        return

    if not numbers:
        await update.message.reply_text(
            get_text("scan_no_numbers", lang), parse_mode="HTML"
        )
        return

    # Store scanned numbers for confirmation
    context.user_data["scan_numbers"] = numbers

    # Show found numbers with confirm/cancel buttons
    number_display = format_number_list(numbers)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                get_text("scan_confirm", lang), callback_data="scanconfirm:yes"
            ),
            InlineKeyboardButton(
                get_text("scan_cancel", lang), callback_data="scanconfirm:no"
            ),
        ]
    ])

    await update.message.reply_text(
        get_text("scan_found", lang, count=len(numbers), numbers=number_display),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def handle_image_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image files sent as documents (not compressed photos)."""
    document = update.message.document
    if not document:
        return

    mime = document.mime_type or ""
    if not mime.startswith("image/"):
        return  # Not an image

    user = update.effective_user
    lang = await get_user_language(user.id)

    await update.message.reply_text(
        get_text("scanning", lang), parse_mode="HTML"
    )

    file = await document.get_file()
    image_bytes = await file.download_as_bytearray()

    numbers = await gemini_ocr.extract_numbers(bytes(image_bytes))

    if numbers is None:
        await update.message.reply_text(
            get_text("scan_unavailable", lang), parse_mode="HTML"
        )
        return

    if not numbers:
        await update.message.reply_text(
            get_text("scan_no_numbers", lang), parse_mode="HTML"
        )
        return

    context.user_data["scan_numbers"] = numbers

    number_display = format_number_list(numbers)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                get_text("scan_confirm", lang), callback_data="scanconfirm:yes"
            ),
            InlineKeyboardButton(
                get_text("scan_cancel", lang), callback_data="scanconfirm:no"
            ),
        ]
    ])

    await update.message.reply_text(
        get_text("scan_found", lang, count=len(numbers), numbers=number_display),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def scan_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirm/cancel of scanned numbers."""
    query = update.callback_query
    await query.answer()

    action = query.data.replace("scanconfirm:", "")
    user = update.effective_user
    lang = await get_user_language(user.id)

    if action == "no":
        context.user_data.pop("scan_numbers", None)
        await query.edit_message_text("Cancelled.", parse_mode="HTML")
        return

    numbers = context.user_data.get("scan_numbers", [])
    if not numbers:
        await query.edit_message_text(
            get_text("no_valid_numbers", lang), parse_mode="HTML"
        )
        return

    # Ask for date selection
    keyboard = build_date_keyboard(lang, callback_prefix="scandate")
    await query.edit_message_text(
        get_text("select_date", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def scan_date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection for scanned numbers."""
    query = update.callback_query
    await query.answer()

    date_str = query.data.replace("scandate:", "")
    user = update.effective_user
    lang = await get_user_language(user.id)

    numbers = context.user_data.pop("scan_numbers", [])
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
        MessageHandler(filters.PHOTO, handle_photo),
        MessageHandler(
            filters.Document.IMAGE,
            handle_image_file,
        ),
        CallbackQueryHandler(scan_confirm_callback, pattern=r"^scanconfirm:"),
        CallbackQueryHandler(scan_date_selected, pattern=r"^scandate:"),
    ]
