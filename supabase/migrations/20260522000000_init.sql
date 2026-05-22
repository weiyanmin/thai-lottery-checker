-- Users
CREATE TABLE IF NOT EXISTS users (
  telegram_id BIGINT PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  language TEXT DEFAULT 'en' CHECK (language IN ('en', 'th', 'my')),
  notifications_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Temporary storage between number input and date selection
CREATE TABLE IF NOT EXISTS pending_checks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT NOT NULL,
  numbers TEXT[] NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Future draw subscriptions (auto-deleted after checking)
CREATE TABLE IF NOT EXISTS tickets (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  telegram_id BIGINT NOT NULL,
  numbers TEXT[] NOT NULL,
  draw_date DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pending_telegram ON pending_checks(telegram_id);
CREATE INDEX IF NOT EXISTS idx_tickets_date ON tickets(draw_date);
CREATE INDEX IF NOT EXISTS idx_tickets_telegram ON tickets(telegram_id);
