"""Notification service — scheduled checking and user notifications."""

import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict

from telegram import Bot

from bot.config import TIMEZONE, CHECK_INTERVAL_MINUTES
from bot.database import db
from bot.services import lottery_api
from bot.i18n import get_text

logger = logging.getLogger(__name__)


async def check_and_notify(bot: Bot):
    """Check all pending tickets for today's draw and notify users."""
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()
    period_date = today.strftime("%Y-%m-%d")

    if not lottery_api.is_draw_day(today):
        return

    # Verify results are actually available
    result = await lottery_api.get_lottery_result(period_date)
    if not result:
        logger.info("Results not yet available for %s.", period_date)
        return

    pending = await db.get_pending_tickets(period_date)
    if not pending:
        logger.info("No pending tickets for %s.", period_date)
        return

    # Group by user
    user_tickets = defaultdict(list)
    for ticket in pending:
        user_tickets[ticket["user_id"]].append(ticket)

    for user_id, tickets in user_tickets.items():
        numbers = [t["lottery_num"] for t in tickets]
        lang = tickets[0].get("language", "en")

        try:
            results = await lottery_api.check_numbers(numbers, period_date)

            winners = 0
            total_prize = 0
            lines = []

            for res in results:
                num = res["lottery_num"]

                if res["prize_type"]:
                    winners += 1
                    total_prize += res["prize_amount"]
                    lines.append(get_text("winner", lang,
                        number=num,
                        prize=get_text(f"prize_{res['prize_type']}", lang),
                        amount=f"{res['prize_amount']:,}"))
                else:
                    lines.append(get_text("no_prize", lang, number=num))

            # Build notification message
            header = get_text("notification_header", lang, date=period_date)
            summary = get_text("summary", lang,
                winners=winners, total=len(numbers),
                amount=f"{total_prize:,}")
            detail = "\n".join(lines)
            msg = f"{header}\n\n{detail}\n\n{summary}"

            await bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
            logger.info("Notified user %d: %d/%d winners.", user_id, winners, len(numbers))

            # Auto-delete tickets after notification (privacy)
            await db.delete_user_tickets(user_id, period_date)

        except Exception as e:
            logger.error("Failed to notify user %d: %s", user_id, e)

    # Cleanup any remaining checked tickets
    await db.cleanup_checked_tickets()
    logger.info("Notification round complete for %s.", period_date)


async def send_draw_day_reminder(bot: Bot):
    """Send a reminder to all users with pending tickets on draw day morning."""
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()
    period_date = today.strftime("%Y-%m-%d")

    if not lottery_api.is_draw_day(today):
        return

    pending = await db.get_pending_tickets(period_date)
    if not pending:
        return

    notified_users = set()
    for ticket in pending:
        uid = ticket["user_id"]
        if uid in notified_users:
            continue
        notified_users.add(uid)
        lang = ticket.get("language", "en")
        try:
            msg = get_text("draw_day_reminder", lang, date=period_date)
            await bot.send_message(chat_id=uid, text=msg)
        except Exception as e:
            logger.error("Reminder failed for user %d: %s", uid, e)
