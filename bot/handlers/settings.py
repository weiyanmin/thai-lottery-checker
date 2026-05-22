"""Settings handler — /settings command, notifications toggle, clear history."""

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from bot.database.db import (
    get_user_language, get_user_notifications, toggle_user_notifications,
    clear_user_history,
)
from bot.i18n import get_text

logger = logging.getLogger(__name__)


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings — show settings menu."""
    user = update.effective_user
    lang = await get_user_language(user.id)
    notif = await get_user_notifications(user.id)

    keyboard = _settings_keyboard(lang, notif)
    await update.message.reply_text(
        get_text("settings_title", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def show_settings(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, lang: str):
    """Show settings from a callback query (menu)."""
    user = query.from_user
    notif = await get_user_notifications(user.id)
    keyboard = _settings_keyboard(lang, notif)
    await query.edit_message_text(
        get_text("settings_title", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def toggle_notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle notifications on/off."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = await get_user_language(user.id)
    new_state = await toggle_user_notifications(user.id)

    key = "notifications_toggled_on" if new_state else "notifications_toggled_off"
    keyboard = _settings_keyboard(lang, new_state)
    await query.edit_message_text(
        get_text("settings_title", lang) + "\n\n" + get_text(key, lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def clear_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear user's check history."""
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    lang = await get_user_language(user.id)

    await clear_user_history(user.id)

    notif = await get_user_notifications(user.id)
    keyboard = _settings_keyboard(lang, notif)
    await query.edit_message_text(
        get_text("settings_title", lang) + "\n\n" + get_text("history_cleared", lang),
        reply_markup=keyboard,
        parse_mode="HTML",
    )


async def change_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection from settings."""
    query = update.callback_query
    await query.answer()

    from bot.i18n import LANGUAGE_NAMES
    buttons = [
        [InlineKeyboardButton(name, callback_data=f"lang:{code}")]
        for code, name in LANGUAGE_NAMES.items()
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        "Select language:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


def _settings_keyboard(lang: str, notifications_on: bool) -> InlineKeyboardMarkup:
    """Build settings inline keyboard."""
    notif_text = get_text("notifications_on" if notifications_on else "notifications_off", lang)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(notif_text, callback_data="settings:toggle_notif")],
        [InlineKeyboardButton(get_text("change_language", lang), callback_data="settings:language")],
        [InlineKeyboardButton(get_text("clear_history", lang), callback_data="settings:clear")],
    ])


def get_handlers() -> list:
    """Return all handlers for this module."""
    return [
        CommandHandler("settings", settings_command),
        CallbackQueryHandler(toggle_notifications_callback, pattern=r"^settings:toggle_notif$"),
        CallbackQueryHandler(clear_history_callback, pattern=r"^settings:clear$"),
        CallbackQueryHandler(change_language_callback, pattern=r"^settings:language$"),
    ]
