"""FastAPI server — REST API for the Telegram Mini App.

Privacy: No images or check history are stored server-side.
Only pending tickets for future draws are kept temporarily.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth import validate_init_data
from bot.config import BOT_TOKEN
from bot.database.db import (
    get_db, close_db, upsert_user, get_user_language, set_user_language,
    get_user_notifications, toggle_user_notifications,
    save_tickets, delete_user_tickets,
)
from bot.services.lottery_api import (
    check_numbers, get_draw_dates, is_draw_past,
)
from bot.services.gemini_ocr import gemini_ocr
from bot.services.number_parser import parse_text
from bot.services.excel_parser import parse_excel

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_db()
    logger.info("Database initialised.")
    yield
    await close_db()
    logger.info("Database closed.")


app = FastAPI(title="Thai Lottery Checker", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth ──────────────────────────────────────────────────────
def get_user(request: Request) -> dict:
    """Extract and validate user from initData header."""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    user = validate_init_data(init_data)
    if not user:
        if os.getenv("DEV_MODE") == "1":
            return {"id": 1, "first_name": "Dev", "language_code": "en"}
        raise HTTPException(status_code=401, detail="Invalid initData")
    return user


# ── Endpoints ─────────────────────────────────────────────────

@app.get("/api/dates")
async def api_dates():
    """Get available draw dates."""
    return get_draw_dates(count_past=5, count_future=2)


@app.post("/api/check")
async def api_check(request: Request):
    """Check lottery numbers against a draw date.

    For past draws: check and return results immediately. No data stored.
    For future draws: save tickets to DB for auto-notification, then delete
    after the draw is checked.
    """
    user = get_user(request)
    body = await request.json()

    numbers = body.get("numbers", [])
    period_date = body.get("date", "")

    if not numbers or not period_date:
        raise HTTPException(400, "Missing numbers or date")
    if len(numbers) > 100:
        raise HTTPException(400, "Too many numbers (max 100)")

    await upsert_user(user["id"], user.get("username"), user.get("first_name"))

    past = is_draw_past(period_date)

    if past:
        # Past draw: check now, return results, don't store anything
        results = await check_numbers(numbers, period_date)

        winners = sum(1 for r in results if r.get("prize_type"))
        total_prize = sum(r.get("prize_amount", 0) for r in results if r.get("prize_type"))

        return {
            "results": results,
            "summary": {
                "total": len(results),
                "winners": winners,
                "total_prize": total_prize,
            },
            "status": "checked",
        }
    else:
        # Future draw: save tickets for auto-notification
        await save_tickets(user["id"], numbers, period_date, status="pending")

        return {
            "results": [],
            "summary": {"total": len(numbers), "winners": 0, "total_prize": 0},
            "status": "pending",
        }


@app.post("/api/parse")
async def api_parse(request: Request):
    """Parse lottery numbers from text input."""
    body = await request.json()
    result = parse_text(body.get("text", ""))
    return {"numbers": result.numbers, "invalid_count": result.invalid_count}


@app.post("/api/scan")
async def api_scan(request: Request, file: UploadFile = File(...)):
    """Scan a lottery ticket image using Gemini Vision.

    The image is processed in memory only — never saved to disk or DB.
    """
    get_user(request)

    image_bytes = await file.read()
    numbers = await gemini_ocr.extract_numbers(image_bytes)

    if numbers is None:
        return {"numbers": [], "unavailable": True}
    return {"numbers": numbers, "unavailable": False}


@app.post("/api/upload")
async def api_upload(request: Request, file: UploadFile = File(...)):
    """Parse lottery numbers from an Excel file.

    The file is processed in memory only — never saved to disk or DB.
    """
    get_user(request)

    file_bytes = await file.read()
    result = parse_excel(file_bytes)

    return {
        "numbers": result.numbers,
        "invalid_count": result.invalid_count,
        "total_rows": result.total_rows,
    }


@app.get("/api/settings")
async def api_settings(request: Request):
    """Get user settings (language + notifications only)."""
    user = get_user(request)
    await upsert_user(user["id"], user.get("username"), user.get("first_name"))

    lang = await get_user_language(user["id"])
    notif = await get_user_notifications(user["id"])

    return {"language": lang, "notifications": notif}


@app.post("/api/settings/language")
async def api_set_language(request: Request):
    """Update user language preference."""
    user = get_user(request)
    body = await request.json()
    lang = body.get("language", "en")

    if lang not in ("en", "th", "my"):
        raise HTTPException(400, "Invalid language")

    await set_user_language(user["id"], lang)
    return {"language": lang}


@app.post("/api/settings/notifications")
async def api_toggle_notifications(request: Request):
    """Toggle notifications."""
    user = get_user(request)
    new_state = await toggle_user_notifications(user["id"])
    return {"notifications": new_state}


# ── Static files (serve webapp) ───────────────────────────────
webapp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "webapp")
if os.path.isdir(webapp_dir):
    app.mount("/", StaticFiles(directory=webapp_dir, html=True), name="webapp")
