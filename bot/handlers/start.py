"""Start handler — /start, /help, /language commands."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

from bot.database.db import upsert_user, get_user_language, set_user_language
from bot.i18n import get_text, LANGUAGE_NAMES

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — welcome message with language selection."""
    user = update.effective_user
    await upsert_user(user.id, user.username, user.first_name)
    lang = await get_user_language(user.id)

    keyboard = _language_keyboard()
    await update.message.reply_text(
        get_text("welcome", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help — show available commands."""
    user = update.effective_user
    lang = await get_user_language(user.id)
    await update.message.reply_text(
        get_text("help", lang),
        parse_mode="HTML",
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /language — show language selection keyboard."""
    keyboard = _language_keyboard()
    user = update.effective_user
    lang = await get_user_language(user.id)
    await update.message.reply_text(
        get_text("select_date", lang).replace("draw date", "language"),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang:", "")
    if lang_code not in LANGUAGE_NAMES:
        return

    user = update.effective_user
    await set_user_language(user.id, lang_code)

    # Show main menu in the new language
    keyboard = _main_menu_keyboard(lang_code)
    await query.edit_message_text(
        get_text("language_set", lang_code),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


def _language_keyboard() -> InlineKeyboardMarkup:
    """Build inline keyboard for language selection."""
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"lang:{code}")]
        for code, name in LANGUAGE_NAMES.items()
    ]
    return InlineKeyboardMarkup(buttons)


def _main_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Build main menu inline keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(get_text("btn_check_numbers", lang), callback_data="menu:check")],
        [
            InlineKeyboardButton(get_text("btn_upload_excel", lang), callback_data="menu:upload"),
            InlineKeyboardButton(get_text("btn_scan_ticket", lang), callback_data="menu:scan"),
        ],
        [
            InlineKeyboardButton(get_text("btn_history", lang), callback_data="menu:history"),
            InlineKeyboardButton(get_text("btn_settings", lang), callback_data="menu:settings"),
        ],
    ])


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu button presses."""
    query = update.callback_query
    await query.answer()
    action = query.data.replace("menu:", "")
    user = update.effective_user
    lang = await get_user_language(user.id)

    if action == "check":
        from bot.handlers.check import start_check_flow
        await start_check_flow(query, context, lang)
    elif action == "upload":
        await query.edit_message_text(
            get_text("enter_numbers", lang).replace(
                "Enter your lottery number(s)",
                "Upload your Excel file (.xlsx)"
            ),
            parse_mode="HTML",
        )
    elif action == "scan":
        await query.edit_message_text(
            "Send me a photo of your lottery ticket!",
            parse_mode="HTML",
        )
    elif action == "history":
        from bot.handlers.history import show_history
        await show_history(query, context, lang)
    elif action == "settings":
        from bot.handlers.settings import show_settings
        await show_settings(query, context, lang)


def get_handlers() -> list:
    """Return all handlers for this module."""
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
        CommandHandler("language", language_command),
        CallbackQueryHandler(language_callback, pattern=r"^lang:"),
        CallbackQueryHandler(menu_callback, pattern=r"^menu:"),
        CallbackQueryHandler(lambda u, c: u.callback_query.answer(), pattern=r"^noop$"),
    ]
