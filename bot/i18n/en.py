"""English language strings (default)."""

STRINGS = {
    # ── Welcome & Help ────────────────────────────────────────────
    "welcome": (
        "◆ <b>Welcome to Thai Lottery Checker!</b>\n\n"
        "I can help you check Thai Government Lottery numbers.\n\n"
        "▸ <b>What I can do:</b>\n"
        "  • Check single or multiple numbers\n"
        "  • Upload Excel file with numbers\n"
        "  • Paste a list of numbers\n"
        "  • Scan lottery ticket photos (AI)\n"
        "  • Auto-notify you when results come out\n\n"
        "Choose your language to get started:"
    ),
    "help": (
        "▸ <b>Available Commands</b>\n\n"
        "/start — Start the bot & choose language\n"
        "/check — Check lottery numbers\n"
        "/history — View past results\n"
        "/language — Change language\n"
        "/settings — Bot settings\n"
        "/help — Show this help message\n\n"
        "▸ <b>Tips:</b>\n"
        "  • Send a photo of your ticket to scan it\n"
        "  • Send a .xlsx file to check in bulk\n"
        "  • Paste numbers separated by commas or newlines"
    ),
    "language_set": "✓ Language set to English",

    # ── Date Selection ────────────────────────────────────────────
    "select_date": "▸ <b>Select a lottery draw date:</b>",
    "upcoming_draws": "Upcoming Draws",
    "past_draws": "Past Draws",
    "date_selected": "▸ Selected draw: <b>{date}</b>",

    # ── Number Input ──────────────────────────────────────────────
    "enter_numbers": (
        "▸ <b>Enter your lottery number(s)</b>\n\n"
        "You can:\n"
        "  • Type a single 6-digit number\n"
        "  • Type multiple numbers separated by commas\n"
        "  • Paste a list of numbers\n\n"
        "Example: <code>123456, 789012, 345678</code>"
    ),
    "no_valid_numbers": "✗ No valid 6-digit numbers found. Please try again.",
    "too_many_numbers": "⚠ Too many numbers! Maximum is {max} per submission.",
    "numbers_found": "✓ Found <b>{count}</b> valid number(s).",
    "numbers_invalid_note": "⚠ {count} invalid entries were skipped.",

    # ── Checking ──────────────────────────────────────────────────
    "checking": "● Checking your numbers...",
    "checking_batch": "● Checking batch {current}/{total}...",

    # ── Results ───────────────────────────────────────────────────
    "winner": "★ <b>Number {number}</b> — {prize}! <b>฿{amount}</b>",
    "no_prize": "○ Number {number} — No prize",
    "summary": (
        "\n▸ <b>Results Summary</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Winners: <b>{winners}/{total}</b>\n"
        "Total Prize: <b>฿{amount}</b>"
    ),
    "no_results_yet": (
        "● Results for <b>{date}</b> are not available yet.\n"
        "The draw hasn't happened or results are still being processed."
    ),

    # ── Pending (Future Draw) ─────────────────────────────────────
    "pending_saved": (
        "✓ <b>{count} number(s) saved!</b>\n\n"
        "Draw date: <b>{date}</b>\n"
        "I'll notify you automatically when results come out."
    ),

    # ── Notifications ─────────────────────────────────────────────
    "notification_header": "▸ <b>Lottery Results — {date}</b>",
    "draw_day_reminder": (
        "▸ <b>Draw Day Reminder!</b>\n\n"
        "Today's lottery draw ({date}) is at 3:00 PM.\n"
        "You have pending numbers — I'll check them for you!"
    ),

    # ── Image Scan ────────────────────────────────────────────────
    "scanning": "● Scanning your lottery ticket...",
    "scan_found": (
        "✓ <b>Found {count} number(s) from your ticket:</b>\n\n"
        "{numbers}\n\n"
        "Would you like to check these numbers?"
    ),
    "scan_no_numbers": "✗ Could not find any lottery numbers in the image. Please try a clearer photo.",
    "scan_unavailable": "⚠ Sorry, scan feature is currently unavailable due to number of users. Please enter your numbers manually.",
    "scan_confirm": "✓ Check these numbers",
    "scan_cancel": "✗ Cancel",

    # ── Excel Upload ──────────────────────────────────────────────
    "excel_processing": "● Processing your Excel file...",
    "excel_parsed": (
        "✓ <b>Excel file processed!</b>\n\n"
        "Found: <b>{valid}</b> valid numbers\n"
        "Skipped: <b>{invalid}</b> invalid entries\n"
        "Total rows: <b>{total}</b>"
    ),
    "excel_empty": "✗ No valid lottery numbers found in the file.",
    "excel_error": "✗ Could not read the Excel file. Please check the format.",

    # ── History ───────────────────────────────────────────────────
    "history_title": "▸ <b>Your Check History</b>\n",
    "history_entry": (
        "  {date} — {winners}/{total} won "
        "(฿{prize})"
    ),
    "history_empty": "○ No check history yet.",

    # ── Settings ──────────────────────────────────────────────────
    "settings_title": "▸ <b>Settings</b>",
    "notifications_on": "Notifications: <b>ON</b>",
    "notifications_off": "Notifications: <b>OFF</b>",
    "notifications_toggled_on": "✓ Notifications turned <b>ON</b>",
    "notifications_toggled_off": "✓ Notifications turned <b>OFF</b>",
    "clear_history": "Clear History",
    "history_cleared": "✓ History cleared!",
    "change_language": "Change Language",

    # ── Prize Names ───────────────────────────────────────────────
    "prize_first": "1st Prize",
    "prize_near1": "Near 1st Prize",
    "prize_second": "2nd Prize",
    "prize_third": "3rd Prize",
    "prize_fourth": "4th Prize",
    "prize_fifth": "5th Prize",
    "prize_last2": "Last 2 Digits",
    "prize_last3f": "First 3 Digits",
    "prize_last3b": "Last 3 Digits",

    # ── Errors ────────────────────────────────────────────────────
    "error_generic": "✗ Something went wrong. Please try again later.",
    "error_api": "✗ Could not connect to the lottery API. Please try again.",

    # ── Buttons ───────────────────────────────────────────────────
    "btn_check_numbers": "▸ Check Numbers",
    "btn_upload_excel": "▸ Upload Excel",
    "btn_scan_ticket": "▸ Scan Ticket",
    "btn_history": "▸ History",
    "btn_settings": "▸ Settings",
    "btn_back": "◂ Back",
}
