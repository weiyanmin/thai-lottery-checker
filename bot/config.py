"""Configuration — loads environment variables and defines constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── Telegram ──────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ── Google Gemini (Image OCR) ─────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODELS: list[str] = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# ── Database ──────────────────────────────────────────────────────────
DATABASE_PATH: str = os.getenv(
    "DATABASE_PATH",
    str(Path(__file__).resolve().parent.parent / "lottery_bot.db"),
)

# ── GLO API ───────────────────────────────────────────────────────────
GLO_API_BASE = "https://www.glo.or.th/api/checking"
GLO_CHECK_URL = f"{GLO_API_BASE}/getcheckLotteryResult"
GLO_RESULT_URL = f"{GLO_API_BASE}/getLotteryResult"
GLO_BATCH_SIZE = 10  # Max numbers per API call
GLO_BATCH_DELAY = 0.5  # Seconds between batches

# ── Scheduler ─────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 5  # Poll interval on draw day
DRAW_HOUR = 15  # 3 PM ICT
DRAW_MINUTE = 0

# ── Limits ────────────────────────────────────────────────────────────
MAX_NUMBERS_PER_SUBMISSION = 100
MAX_HISTORY_PER_USER = 10

# ── Timezone ──────────────────────────────────────────────────────────
TIMEZONE = "Asia/Bangkok"
