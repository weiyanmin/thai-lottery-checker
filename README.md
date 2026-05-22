# 🎰 Thai Lottery Checker — Telegram Mini App

A Telegram Mini App for checking Thai Government Lottery numbers in bulk. Features AI-powered ticket scanning, Excel upload, and multi-language support.

## Features

- **Bulk Check** — Enter multiple lottery numbers at once
- **AI Ticket Scan** — Upload a photo of your lottery ticket for automatic number extraction (powered by Gemini Vision)
- **Excel Upload** — Upload `.xlsx` files with lottery numbers
- **Auto Notifications** — Submit numbers for upcoming draws, get notified when results are out
- **Multi-Language** — English, Thai (ไทย), Myanmar (မြန်မာ)
- **Privacy First** — No data stored after checking. History saved locally on your device only.

## Architecture

```
webapp/          → Frontend (HTML/CSS/JS) — deployed to Vercel
api/             → REST API (FastAPI) — deployed to Railway
bot/             → Telegram Bot (notifications only) — deployed to Railway
```

## Setup

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `DEV_MODE=1 uvicorn api.server:app --port 8080`

## Deploy

- **Frontend** → Push `webapp/` to Vercel
- **Backend** → Push to Railway (auto-detects `railway.json`)
- **Bot** → Configure via BotFather: `/mybots` → Configure Mini App

## License

MIT
