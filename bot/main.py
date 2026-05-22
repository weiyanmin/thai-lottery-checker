"""Minimal bot — launches the Mini App and handles scheduled notifications."""

import asyncio
import logging
import sys
import os
from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update, BotCommand, MenuButtonWebApp, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

from bot.config import BOT_TOKEN, TIMEZONE, CHECK_INTERVAL_MINUTES
from bot.database.db import get_db, close_db

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# The URL where the Mini App is hosted (set via env or default)
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://your-app.vercel.app")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start — send a button to open the Mini App."""
    await update.message.reply_text(
        "◆ <b>Thai Lottery Checker</b>\n\n"
        "Tap the button below to open the app.",
        parse_mode="HTML",
        reply_markup={
            "inline_keyboard": [[{
                "text": "▸ Open Lottery Checker",
                "web_app": {"url": WEBAPP_URL},
            }]]
        },
    )


def main():
    """Build, configure, and run the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not set.")
        sys.exit(1)

    app = Application.builder().token(BOT_TOKEN).build()

    # Register only /start
    app.add_handler(CommandHandler("start", start_command))

    # Scheduled jobs
    _setup_scheduled_jobs(app)

    # Hooks
    app.post_init = _on_startup
    app.post_shutdown = _on_shutdown

    logger.info("Bot starting (Mini App launcher mode)...")
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    app.run_polling(drop_pending_updates=True)


async def _on_startup(app: Application):
    await get_db()
    logger.info("Database initialised.")

    me = await app.bot.get_me()
    logger.info("Bot running as @%s", me.username)

    # Set commands
    await app.bot.set_my_commands([
        BotCommand("start", "Open the lottery checker"),
    ])

    # Set menu button to open Mini App
    try:
        await app.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="Open App",
                web_app=WebAppInfo(url=WEBAPP_URL),
            )
        )
        logger.info("Menu button set to Mini App: %s", WEBAPP_URL)
    except Exception as e:
        logger.warning("Could not set menu button: %s", e)


async def _on_shutdown(app: Application):
    await close_db()
    logger.info("Database closed.")


def _setup_scheduled_jobs(app: Application):
    tz = ZoneInfo(TIMEZONE)
    job_queue = app.job_queue
    if not job_queue:
        logger.warning("Job queue not available.")
        return

    job_queue.run_daily(
        _reminder_job,
        time=time(hour=9, minute=0, tzinfo=tz),
        name="draw_day_reminder",
    )
    job_queue.run_repeating(
        _check_results_job,
        interval=CHECK_INTERVAL_MINUTES * 60,
        first=10,
        name="check_results",
    )
    logger.info("Scheduled jobs ready.")


async def _reminder_job(context):
    from bot.services.notification import send_draw_day_reminder
    await send_draw_day_reminder(context.bot)


async def _check_results_job(context):
    from datetime import datetime
    from bot.services.lottery_api import is_draw_day
    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    if not is_draw_day(now.date()) or now.hour < 15:
        return
    from bot.services.notification import check_and_notify
    await check_and_notify(context.bot)


if __name__ == "__main__":
    main()
