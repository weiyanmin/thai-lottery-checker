"""Database operations — async SQLite via aiosqlite."""

import aiosqlite
import logging
from datetime import datetime
from typing import Optional

from bot.config import DATABASE_PATH

logger = logging.getLogger(__name__)

_db: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    """Return the shared database connection, creating it if needed."""
    global _db
    if _db is None:
        _db = await aiosqlite.connect(DATABASE_PATH)
        _db.row_factory = aiosqlite.Row
        await _db.execute("PRAGMA journal_mode=WAL")
        await _db.execute("PRAGMA foreign_keys=ON")
        await init_tables(_db)
    return _db


async def close_db():
    """Close the database connection."""
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def init_tables(db: aiosqlite.Connection):
    """Create tables if they do not exist."""
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id       INTEGER PRIMARY KEY,
            username      TEXT,
            first_name    TEXT,
            language      TEXT    DEFAULT 'en',
            notifications_enabled INTEGER DEFAULT 1,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(user_id),
            lottery_num   TEXT    NOT NULL,
            period_date   TEXT    NOT NULL,
            status        TEXT    DEFAULT 'pending',
            prize_type    TEXT,
            prize_amount  INTEGER DEFAULT 0,
            checked_at    TEXT,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_tickets_user_period
            ON tickets(user_id, period_date);
        CREATE INDEX IF NOT EXISTS idx_tickets_status
            ON tickets(status);

    """)
    await db.commit()
    logger.info("Database tables initialised.")


# ── User operations ───────────────────────────────────────────────────


async def upsert_user(
    user_id: int,
    username: str | None = None,
    first_name: str | None = None,
    language: str = "en",
):
    """Create or update a user record."""
    db = await get_db()
    await db.execute(
        """
        INSERT INTO users (user_id, username, first_name, language)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username   = COALESCE(excluded.username, users.username),
            first_name = COALESCE(excluded.first_name, users.first_name)
        """,
        (user_id, username, first_name, language),
    )
    await db.commit()


async def get_user_language(user_id: int) -> str:
    """Return the user's language code, defaulting to 'en'."""
    db = await get_db()
    async with db.execute(
        "SELECT language FROM users WHERE user_id = ?", (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return row["language"] if row else "en"


async def set_user_language(user_id: int, language: str):
    """Update a user's preferred language."""
    db = await get_db()
    await db.execute(
        "UPDATE users SET language = ? WHERE user_id = ?", (language, user_id)
    )
    await db.commit()


async def get_user_notifications(user_id: int) -> bool:
    """Check if notifications are enabled for a user."""
    db = await get_db()
    async with db.execute(
        "SELECT notifications_enabled FROM users WHERE user_id = ?", (user_id,)
    ) as cursor:
        row = await cursor.fetchone()
        return bool(row["notifications_enabled"]) if row else True


async def toggle_user_notifications(user_id: int) -> bool:
    """Toggle notifications on/off, returns new state."""
    db = await get_db()
    await db.execute(
        """
        UPDATE users
        SET notifications_enabled = CASE WHEN notifications_enabled = 1 THEN 0 ELSE 1 END
        WHERE user_id = ?
        """,
        (user_id,),
    )
    await db.commit()
    return await get_user_notifications(user_id)


# ── Ticket operations ────────────────────────────────────────────────


async def save_tickets(
    user_id: int,
    numbers: list[str],
    period_date: str,
    status: str = "pending",
):
    """Save multiple lottery tickets for a user."""
    db = await get_db()
    await db.executemany(
        """
        INSERT INTO tickets (user_id, lottery_num, period_date, status)
        VALUES (?, ?, ?, ?)
        """,
        [(user_id, num, period_date, status) for num in numbers],
    )
    await db.commit()


async def update_ticket_result(
    ticket_id: int,
    prize_type: str | None,
    prize_amount: int,
):
    """Update a ticket with its check result."""
    db = await get_db()
    await db.execute(
        """
        UPDATE tickets
        SET status = 'checked', prize_type = ?, prize_amount = ?,
            checked_at = datetime('now')
        WHERE id = ?
        """,
        (prize_type, prize_amount, ticket_id),
    )
    await db.commit()


async def get_pending_tickets(period_date: str) -> list[dict]:
    """Get all pending tickets for a specific draw date."""
    db = await get_db()
    async with db.execute(
        """
        SELECT t.id, t.user_id, t.lottery_num, t.period_date, u.language
        FROM tickets t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.period_date = ? AND t.status = 'pending'
          AND u.notifications_enabled = 1
        """,
        (period_date,),
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_user_tickets(
    user_id: int, period_date: str
) -> list[dict]:
    """Get all tickets for a user on a given draw date."""
    db = await get_db()
    async with db.execute(
        """
        SELECT id, lottery_num, status, prize_type, prize_amount, checked_at
        FROM tickets
        WHERE user_id = ? AND period_date = ?
        ORDER BY created_at DESC
        """,
        (user_id, period_date),
    ) as cursor:
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# ── Cleanup operations ────────────────────────────────────────────────


async def delete_user_tickets(user_id: int, period_date: str):
    """Delete all tickets for a user on a specific draw date."""
    db = await get_db()
    await db.execute(
        "DELETE FROM tickets WHERE user_id = ? AND period_date = ?",
        (user_id, period_date),
    )
    await db.commit()
    logger.info("Deleted tickets for user %d, date %s.", user_id, period_date)


async def cleanup_checked_tickets():
    """Delete all tickets that have been checked (status='checked')."""
    db = await get_db()
    async with db.execute(
        "SELECT COUNT(*) as cnt FROM tickets WHERE status = 'checked'"
    ) as cursor:
        row = await cursor.fetchone()
        count = row["cnt"] if row else 0

    if count > 0:
        await db.execute("DELETE FROM tickets WHERE status = 'checked'")
        await db.commit()
        logger.info("Cleaned up %d checked tickets.", count)
