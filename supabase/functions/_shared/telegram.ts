const BOT_TOKEN = Deno.env.get("BOT_TOKEN")!;
const API = `https://api.telegram.org/bot${BOT_TOKEN}`;

async function call(method: string, body: Record<string, unknown>) {
  const res = await fetch(`${API}/${method}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text();
    console.error(`Telegram ${method} failed: ${res.status} ${text}`);
  }
  return res.json();
}

export async function sendMessage(
  chatId: number,
  text: string,
  options?: Record<string, unknown>
) {
  return call("sendMessage", {
    chat_id: chatId,
    text,
    parse_mode: "HTML",
    ...options,
  });
}

export async function editMessageText(
  chatId: number,
  messageId: number,
  text: string,
  options?: Record<string, unknown>
) {
  return call("editMessageText", {
    chat_id: chatId,
    message_id: messageId,
    text,
    parse_mode: "HTML",
    ...options,
  });
}

export async function answerCallbackQuery(
  callbackQueryId: string,
  text?: string
) {
  return call("answerCallbackQuery", {
    callback_query_id: callbackQueryId,
    text,
  });
}

export async function sendChatAction(chatId: number, action: string) {
  return call("sendChatAction", { chat_id: chatId, action });
}

export async function getFileUrl(fileId: string): Promise<string | null> {
  const res = await call("getFile", { file_id: fileId });
  const filePath = res?.result?.file_path;
  if (!filePath) return null;
  return `https://api.telegram.org/file/bot${BOT_TOKEN}/${filePath}`;
}

export async function downloadFile(fileId: string): Promise<Uint8Array | null> {
  const url = await getFileUrl(fileId);
  if (!url) return null;
  const res = await fetch(url);
  if (!res.ok) return null;
  return new Uint8Array(await res.arrayBuffer());
}

export async function setWebhook(url: string) {
  return call("setWebhook", { url, allowed_updates: ["message", "callback_query"] });
}
