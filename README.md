# 🎰 Thai Lottery Checker — Telegram Bot

A Telegram bot for checking Thai Government Lottery numbers. Built entirely on **Supabase Edge Functions** (TypeScript/Deno).

## Features

- **Check Numbers** — Send numbers directly in chat
- **AI Ticket Scan** — Send a photo of your lottery ticket (Gemini Vision)
- **Excel Upload** — Upload `.xlsx` files with lottery numbers
- **Auto Notifications** — Submit numbers for future draws, get notified automatically
- **Multi-Language** — English, Thai (ไทย), Myanmar (မြန်မာ)
- **Privacy First** — No history stored. Pending tickets auto-deleted after checking.

## Architecture

```
supabase/
  functions/
    telegram-webhook/   → Handles all bot interactions (webhook)
    check-results/      → Scheduled: checks pending tickets on draw days
    _shared/            → Shared modules (API, i18n, parsers)
  migrations/           → PostgreSQL schema
```

## Deploy

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your **Project URL** and **Service Role Key** from Settings → API

### 2. Install Supabase CLI
```bash
brew install supabase/tap/supabase
```

### 3. Link & Deploy
```bash
cd "Lottery Checker"
supabase init        # (if not already initialized)
supabase link --project-ref YOUR_PROJECT_REF
supabase db push     # Apply migrations
supabase functions deploy telegram-webhook --no-verify-jwt
supabase functions deploy check-results
```

### 4. Set Secrets
```bash
supabase secrets set BOT_TOKEN=your_bot_token
supabase secrets set GEMINI_API_KEY=your_gemini_api_key
```

### 5. Set Telegram Webhook
```bash
curl "https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook?url=https://YOUR_PROJECT.supabase.co/functions/v1/telegram-webhook"
```

### 6. Schedule Result Checking (optional)
In Supabase SQL Editor, run:
```sql
SELECT cron.schedule(
  'check-lottery-results',
  '*/5 8-12 1,16 * *',
  $$
  SELECT net.http_post(
    url := 'https://YOUR_PROJECT.supabase.co/functions/v1/check-results',
    headers := jsonb_build_object(
      'Authorization', 'Bearer YOUR_ANON_KEY',
      'Content-Type', 'application/json'
    )
  );
  $$
);
```

## License

MIT
