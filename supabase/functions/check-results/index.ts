/** Scheduled function — check pending tickets on draw days and notify users. */

import { supabase } from "../_shared/supabase.ts";
import { sendMessage } from "../_shared/telegram.ts";
import { t } from "../_shared/i18n.ts";
import { checkNumbers, isDrawDay, hasResultsAvailable, type CheckResult } from "../_shared/glo-api.ts";

Deno.serve(async (req) => {
  // Verify this is an authorized call (from pg_cron or manual trigger)
  const authHeader = req.headers.get("Authorization");
  if (!authHeader?.startsWith("Bearer ")) {
    return new Response("Unauthorized", { status: 401 });
  }

  try {
    await checkAndNotify();
    // Also clean up old pending checks (> 1 hour)
    await supabase
      .from("pending_checks")
      .delete()
      .lt("created_at", new Date(Date.now() - 3600_000).toISOString());

    return new Response(JSON.stringify({ ok: true }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("Check-results error:", e);
    return new Response(JSON.stringify({ error: String(e) }), { status: 500 });
  }
});

async function checkAndNotify() {
  // Get today in Bangkok timezone
  const now = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Bangkok" }));
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;

  if (!isDrawDay(now)) {
    console.log("Not a draw day, skipping.");
    return;
  }

  // Check if results are available
  const available = await hasResultsAvailable(today);
  if (!available) {
    console.log(`Results not yet available for ${today}.`);
    return;
  }

  // Get all pending tickets for today
  const { data: tickets, error } = await supabase
    .from("tickets")
    .select("id, telegram_id, numbers")
    .eq("draw_date", today);

  if (error) {
    console.error("DB error:", error);
    return;
  }
  if (!tickets?.length) {
    console.log("No pending tickets for today.");
    return;
  }

  // Group by user
  const userTickets = new Map<number, { ids: string[]; numbers: string[] }>();
  for (const ticket of tickets) {
    const existing = userTickets.get(ticket.telegram_id) ?? { ids: [], numbers: [] };
    existing.ids.push(ticket.id);
    existing.numbers.push(...ticket.numbers);
    userTickets.set(ticket.telegram_id, existing);
  }

  // Process each user
  for (const [userId, { ids, numbers }] of userTickets) {
    // Get user language
    const { data: user } = await supabase
      .from("users")
      .select("language, notifications_enabled")
      .eq("telegram_id", userId)
      .single();

    if (!user?.notifications_enabled) {
      // Delete tickets but don't notify
      await supabase.from("tickets").delete().in("id", ids);
      continue;
    }

    const lang = user?.language ?? "en";
    const unique = [...new Set(numbers)];

    try {
      const results = await checkNumbers(unique, today);

      let winners = 0;
      let totalPrize = 0;
      const lines: string[] = [];

      for (const r of results) {
        if (r.prizeKey) {
          winners++;
          totalPrize += r.prizeAmount;
          const prizeName = t(`prize_${r.prizeKey}`, lang);
          lines.push(t("winner", lang, { number: r.number, prize: prizeName, amount: r.prizeAmount.toLocaleString() }));
        } else {
          lines.push(t("no_prize", lang, { number: r.number }));
        }
      }

      const header = t("notification_header", lang, { date: today });
      const summary = t("summary", lang, {
        winners,
        total: results.length,
        amount: totalPrize.toLocaleString(),
      });

      const msg = header + "\n\n" + lines.join("\n") + summary;
      await sendMessage(userId, msg);
      console.log(`Notified user ${userId}: ${winners}/${results.length} winners.`);
    } catch (e) {
      console.error(`Failed to notify user ${userId}:`, e);
    }

    // Delete tickets after notification (privacy)
    await supabase.from("tickets").delete().in("id", ids);
  }

  console.log(`Notification round complete for ${today}.`);
}
