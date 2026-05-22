/** Gemini Vision OCR — extract lottery numbers from ticket images. */

const GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"];
const GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent";

const PROMPT =
  "You are an OCR assistant for Thai government lottery tickets. " +
  "Extract ALL 6-digit lottery numbers visible in this image. " +
  "Thai lottery tickets have a 6-digit number printed prominently. " +
  'Return ONLY a valid JSON array of strings containing the 6-digit numbers. ' +
  'Example: ["123456", "789012"]. ' +
  "If no valid 6-digit lottery numbers are found, return an empty array []. " +
  "Do NOT include any explanation, markdown, or text outside the JSON array.";

export async function scanTicket(imageBytes: Uint8Array): Promise<string[] | null> {
  const apiKey = Deno.env.get("GEMINI_API_KEY");
  if (!apiKey) {
    console.error("GEMINI_API_KEY not set");
    return null;
  }

  const b64 = btoa(String.fromCharCode(...imageBytes));

  for (const model of GEMINI_MODELS) {
    const url = GEMINI_URL.replace("{model}", model) + `?key=${apiKey}`;
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                { text: PROMPT },
                { inline_data: { mime_type: "image/jpeg", data: b64 } },
              ],
            },
          ],
          generationConfig: { temperature: 0.1, maxOutputTokens: 256 },
        }),
      });

      if (res.status === 429) {
        console.warn(`Rate limited on ${model}, trying next...`);
        continue;
      }
      if (!res.ok) {
        console.error(`Gemini ${model} error: ${res.status}`);
        continue;
      }

      const data = await res.json();
      return parseGeminiResponse(data);
    } catch (e) {
      console.error(`Gemini ${model} failed:`, e);
      continue;
    }
  }

  return null; // All models exhausted
}

function parseGeminiResponse(data: any): string[] {
  try {
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text?.trim() ?? "";
    // Strip markdown fences
    const clean = text.replace(/^```(?:json)?\s*/, "").replace(/\s*```$/, "").trim();
    const arr = JSON.parse(clean);
    if (!Array.isArray(arr)) return [];
    return arr.map(String).filter((s: string) => /^\d{6}$/.test(s));
  } catch {
    return [];
  }
}
