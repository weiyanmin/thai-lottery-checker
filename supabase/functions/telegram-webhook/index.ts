/** Telegram Webhook — handles all incoming bot updates. */

import { supabase } from "../_shared/supabase.ts";
import { sendMessage, sendChatAction, answerCallbackQuery, downloadFile } from "../_shared/telegram.ts";
import { t } from "../_shared/i18n.ts";
import { parseNumbers } from "../_shared/number-parser.ts";
import { checkNumbers, getDrawDates, isDrawPast, type CheckResult } from "../_shared/glo-api.ts";
import { scanTicket } from "../_shared/gemini.ts";

const MAX_NUMBERS = 100;

// ─── Entry Point ─────────────────────────────────────────────

Deno.serve(async (req) => {
  try {
    if (req.method !== "POST") return new Response("OK");
    const update = await req.json();
    await handleUpdate(update);
  } catch (e) {
    console.error("Webhook error:", e);
  }
  return new Response("OK"); // Always 200 for Telegram
});

// ─── Router ──────────────────────────────────────────────────

async function handleUpdate(update: any) {
  if (update.message) {
    await handleMessage(update.message);
  } else if (update.callback_query) {
    await handleCallback(update.callback_query);
  }
}

async function handleMessage(msg: any) {
  const chatId = msg.chat.id;
  const userId = msg.from.id;
  await ensureUser(userId, msg.from.username, msg.from.first_name);

  if (msg.text) {
    const text = msg.text.trim();
    if (text.startsWith("/")) {
      const cmd = text.split(/\s+/)[0].split("@")[0].toLowerCase();
      switch (cmd) {
        case "/start": return cmdStart(chatId, userId);
        case "/check": return cmdCheck(chatId, userId);
        case "/help": return cmdHelp(chatId, userId);
        case "/lang":
        case "/language": return cmdLang(chatId, userId);
        case "/settings": return cmdSettings(chatId, userId);
      }
    } else {
      return handleTextInput(chatId, userId, text);
    }
  } else if (msg.photo) {
    return handlePhoto(chatId, userId, msg.photo);
  } else if (msg.document) {
    return handleDocument(chatId, userId, msg.document);
  }
}

// ─── Commands ────────────────────────────────────────────────

async function cmdStart(chatId: number, userId: number) {
  const lang = await getLang(userId);
  await sendMessage(chatId, t("welcome", lang), {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "English", callback_data: "l:en" },
          { text: "ไทย", callback_data: "l:th" },
          { text: "မြန်မာ", callback_data: "l:my" },
        ],
      ],
    },
  });
}

async function cmdCheck(chatId: number, userId: number) {
  const lang = await getLang(userId);
  await sendMessage(chatId, t("enter_numbers", lang));
}

async function cmdHelp(chatId: number, userId: number) {
  const lang = await getLang(userId);
  await sendMessage(chatId, t("help", lang));
}

async function cmdLang(chatId: number, userId: number) {
  await sendMessage(chatId, "Choose language / เลือกภาษา / ဘာသာစကားရွေးချယ်ပါ", {
    reply_markup: {
      inline_keyboard: [
        [
          { text: "English", callback_data: "l:en" },
          { text: "ไทย", callback_data: "l:th" },
          { text: "မြန်မာ", callback_data: "l:my" },
        ],
      ],
    },
  });
}

async function cmdSettings(chatId: number, userId: number) {
  const lang = await getLang(userId);
  const { data } = await supabase
    .from("users")
    .select("notifications_enabled")
    .eq("telegram_id", userId)
    .single();
  const notifOn = data?.notifications_enabled ?? true;

  await sendMessage(chatId, t("settings_title", lang) + "\n\n" + t(notifOn ? "notif_on" : "notif_off", lang), {
    reply_markup: {
      inline_keyboard: [
        [{ text: notifOn ? "🔔 Turn OFF" : "🔕 Turn ON", callback_data: "n:toggle" }],
        [{ text: "🌐 Language", callback_data: "n:lang" }],
      ],
    },
  });
}

// ─── Text / Numbers Input ────────────────────────────────────

async function handleTextInput(chatId: number, userId: number, text: string) {
  const lang = await getLang(userId);
  const { numbers, invalidCount } = parseNumbers(text);

  if (numbers.length === 0) {
    return sendMessage(chatId, t("no_valid", lang));
  }
  if (numbers.length > MAX_NUMBERS) {
    return sendMessage(chatId, t("too_many", lang, { max: MAX_NUMBERS }));
  }

  await savePending(userId, numbers);
  await sendMessage(chatId, t("numbers_found", lang, { count: numbers.length }), {
    reply_markup: buildDateKeyboard(lang),
  });
}

// ─── Photo (AI Scan) ────────────────────────────────────────

async function handlePhoto(chatId: number, userId: number, photos: any[]) {
  const lang = await getLang(userId);
  await sendChatAction(chatId, "typing");
  await sendMessage(chatId, t("scanning", lang));

  const largest = photos[photos.length - 1];
  const imageBytes = await downloadFile(largest.file_id);
  if (!imageBytes) {
    return sendMessage(chatId, t("scan_unavailable", lang));
  }

  const numbers = await scanTicket(imageBytes);
  if (numbers === null) {
    return sendMessage(chatId, t("scan_unavailable", lang));
  }
  if (numbers.length === 0) {
    return sendMessage(chatId, t("scan_no_numbers", lang));
  }

  await savePending(userId, numbers);
  const numList = numbers.map((n) => `<code>${n}</code>`).join(", ");
  await sendMessage(chatId, t("scan_found", lang, { count: numbers.length, numbers: numList }), {
    reply_markup: buildDateKeyboard(lang),
  });
}

// ─── Document (Excel) ───────────────────────────────────────

async function handleDocument(chatId: number, userId: number, doc: any) {
  const lang = await getLang(userId);
  const name = (doc.file_name ?? "").toLowerCase();
  if (!name.endsWith(".xlsx") && !name.endsWith(".xls")) return;

  await sendChatAction(chatId, "typing");
  await sendMessage(chatId, t("excel_processing", lang));

  const fileBytes = await downloadFile(doc.file_id);
  if (!fileBytes) {
    return sendMessage(chatId, t("excel_error", lang));
  }

  try {
    // Dynamic import for SheetJS
    const XLSX = await import("https://cdn.sheetjs.com/xlsx-0.20.3/package/xlsx.mjs");
    const wb = XLSX.read(fileBytes, { type: "array" });
    const ws = wb.Sheets[wb.SheetNames[0]];
    if (!ws) return sendMessage(chatId, t("excel_empty", lang));

    const rows: any[][] = XLSX.utils.sheet_to_json(ws, { header: 1 });
    const allText = rows.flat().filter(Boolean).map(String).join(",");
    const { numbers } = parseNumbers(allText);

    if (numbers.length === 0) {
      return sendMessage(chatId, t("excel_empty", lang));
    }

    await savePending(userId, numbers);
    await sendMessage(chatId, t("excel_found", lang, { count: numbers.length }), {
      reply_markup: buildDateKeyboard(lang),
    });
  } catch (e) {
    console.error("Excel parse error:", e);
    return sendMessage(chatId, t("excel_error", lang));
  }
}

// ─── Callback Queries ────────────────────────────────────────

async function handleCallback(cb: any) {
  const chatId = cb.message?.chat?.id;
  const userId = cb.from.id;
  const data = cb.data ?? "";
  await answerCallbackQuery(cb.id);
  if (!chatId) return;

  if (data.startsWith("l:")) {
    // Language selection
    const lang = data.slice(2);
    await supabase.from("users").update({ language: lang }).eq("telegram_id", userId);
    await sendMessage(chatId, t("language_set", lang));
  } else if (data.startsWith("d:")) {
    // Date selection — check numbers
    const periodDate = data.slice(2);
    await handleDateSelected(chatId, userId, periodDate);
  } else if (data === "n:toggle") {
    // Toggle notifications
    const { data: user } = await supabase
      .from("users")
      .select("notifications_enabled, language")
      .eq("telegram_id", userId)
      .single();
    const newVal = !(user?.notifications_enabled ?? true);
    await supabase.from("users").update({ notifications_enabled: newVal }).eq("telegram_id", userId);
    const lang = user?.language ?? "en";
    await sendMessage(chatId, t(newVal ? "notif_toggled_on" : "notif_toggled_off", lang));
  } else if (data === "n:lang") {
    await cmdLang(chatId, userId);
  }
}

async function handleDateSelected(chatId: number, userId: number, periodDate: string) {
  const lang = await getLang(userId);

  // Get pending numbers
  const { data: pending } = await supabase
    .from("pending_checks")
    .select("numbers")
    .eq("telegram_id", userId)
    .order("created_at", { ascending: false })
    .limit(1)
    .single();

  if (!pending?.numbers?.length) {
    return sendMessage(chatId, t("enter_numbers", lang));
  }

  const numbers: string[] = pending.numbers;

  // Clean up pending
  await supabase.from("pending_checks").delete().eq("telegram_id", userId);

  if (isDrawPast(periodDate)) {
    // Check immediately
    await sendMessage(chatId, t("checking", lang));
    await sendChatAction(chatId, "typing");

    try {
      const results = await checkNumbers(numbers, periodDate);
      await sendResults(chatId, lang, results);
    } catch (e) {
      console.error("Check error:", e);
      await sendMessage(chatId, t("error_api", lang));
    }
  } else {
    // Save for future notification
    await supabase.from("tickets").insert({
      telegram_id: userId,
      numbers,
      draw_date: periodDate,
    });
    await sendMessage(chatId, t("pending_saved", lang, { count: numbers.length, date: periodDate }));
  }
}

// ─── Results Formatting ─────────────────────────────────────

async function sendResults(chatId: number, lang: string, results: CheckResult[]) {
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

  const summary = t("summary", lang, {
    winners,
    total: results.length,
    amount: totalPrize.toLocaleString(),
  });

  const msg = lines.join("\n") + summary;
  // Split if too long (Telegram max is 4096 chars)
  if (msg.length > 4000) {
    const mid = Math.ceil(lines.length / 2);
    await sendMessage(chatId, lines.slice(0, mid).join("\n"));
    await sendMessage(chatId, lines.slice(mid).join("\n") + summary);
  } else {
    await sendMessage(chatId, msg);
  }
}

// ─── Helpers ─────────────────────────────────────────────────

function buildDateKeyboard(lang: string) {
  const { past, future } = getDrawDates();
  const rows: any[][] = [];

  if (future.length) {
    rows.push([{ text: `── ${t("upcoming", lang)} ──`, callback_data: "noop" }]);
    rows.push(future.map((d) => ({ text: d, callback_data: `d:${d}` })));
  }
  if (past.length) {
    rows.push([{ text: `── ${t("past", lang)} ──`, callback_data: "noop" }]);
    // Show past dates in reverse (newest first), 2 per row
    const reversed = [...past].reverse();
    for (let i = 0; i < reversed.length; i += 2) {
      const row = [{ text: reversed[i], callback_data: `d:${reversed[i]}` }];
      if (reversed[i + 1]) {
        row.push({ text: reversed[i + 1], callback_data: `d:${reversed[i + 1]}` });
      }
      rows.push(row);
    }
  }

  return { inline_keyboard: rows };
}

async function ensureUser(userId: number, username?: string, firstName?: string) {
  await supabase.from("users").upsert(
    { telegram_id: userId, username, first_name: firstName },
    { onConflict: "telegram_id", ignoreDuplicates: false }
  );
}

async function getLang(userId: number): Promise<string> {
  const { data } = await supabase
    .from("users")
    .select("language")
    .eq("telegram_id", userId)
    .single();
  return data?.language ?? "en";
}

async function savePending(userId: number, numbers: string[]) {
  // Remove old pending for this user
  await supabase.from("pending_checks").delete().eq("telegram_id", userId);
  // Insert new
  await supabase.from("pending_checks").insert({ telegram_id: userId, numbers });
}
