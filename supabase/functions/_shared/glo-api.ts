/** GLO Lottery API — check numbers and calculate draw dates. */

const GLO_CHECK_URL = "https://www.glo.or.th/api/checking/getcheckLotteryResult";
const GLO_RESULT_URL = "https://www.glo.or.th/api/checking/getLotteryResult";
const BATCH_SIZE = 10;
const BATCH_DELAY = 500; // ms

const PRIZE_AMOUNTS: Record<string, number> = {
  first: 6_000_000, near1: 100_000, second: 200_000,
  third: 80_000, fourth: 40_000, fifth: 20_000,
  last2: 2_000, last3f: 4_000, last3b: 4_000,
};

const THAI_PRIZE_MAP: Record<string, string> = {
  "รางวัลที่ 1": "first",
  "รางวัลข้างเคียงรางวัลที่ 1": "near1",
  "รางวัลที่ 2": "second",
  "รางวัลที่ 3": "third",
  "รางวัลที่ 4": "fourth",
  "รางวัลที่ 5": "fifth",
  "รางวัลเลขท้าย 2 ตัว": "last2",
  "รางวัลเลขหน้า 3 ตัว": "last3f",
  "รางวัลเลขท้าย 3 ตัว": "last3b",
};

export interface CheckResult {
  number: string;
  prizeKey: string | null;
  prizeAmount: number;
  error?: boolean;
}

export async function checkNumbers(numbers: string[], periodDate: string): Promise<CheckResult[]> {
  const results: CheckResult[] = [];
  const batches: string[][] = [];
  for (let i = 0; i < numbers.length; i += BATCH_SIZE) {
    batches.push(numbers.slice(i, i + BATCH_SIZE));
  }

  for (let i = 0; i < batches.length; i++) {
    if (i > 0) await delay(BATCH_DELAY);
    const batch = batches[i];
    try {
      const res = await fetch(GLO_CHECK_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          number: batch.map((n) => ({ lottery_num: n })),
          period_date: periodDate,
        }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      results.push(...parseCheckResponse(data, batch));
    } catch (e) {
      console.error("GLO API error:", e);
      for (const n of batch) {
        results.push({ number: n, prizeKey: null, prizeAmount: 0, error: true });
      }
    }
  }
  return results;
}

function parseCheckResponse(data: any, submitted: string[]): CheckResult[] {
  const results: CheckResult[] = [];
  const resultList = data?.response?.result ?? [];

  for (const item of resultList) {
    const num = String(item.number ?? "");
    const statusType = item.statusType ?? 2;
    const statusData = item.status_data ?? [];

    if (statusType === 1 && statusData.length > 0) {
      let totalAmount = 0;
      let primaryKey: string | null = null;
      for (const sd of statusData) {
        const key = THAI_PRIZE_MAP[sd.reward ?? ""];
        if (key) {
          if (!primaryKey) primaryKey = key;
          totalAmount += PRIZE_AMOUNTS[key] ?? 0;
        }
      }
      results.push({ number: num, prizeKey: primaryKey, prizeAmount: totalAmount });
    } else {
      results.push({ number: num, prizeKey: null, prizeAmount: 0 });
    }
  }

  // Ensure all submitted numbers have a result
  const found = new Set(results.map((r) => r.number));
  for (const n of submitted) {
    if (!found.has(n)) {
      results.push({ number: n, prizeKey: null, prizeAmount: 0 });
    }
  }
  return results;
}

export async function hasResultsAvailable(periodDate: string): Promise<boolean> {
  try {
    const dt = new Date(periodDate + "T00:00:00+07:00");
    const res = await fetch(GLO_RESULT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: String(dt.getDate()).padStart(2, "0"),
        month: String(dt.getMonth() + 1).padStart(2, "0"),
        year: String(dt.getFullYear()),
      }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    return !!data?.response;
  } catch {
    return false;
  }
}

/** Get past and future Thai lottery draw dates (1st & 16th of each month). */
export function getDrawDates(pastCount = 5, futureCount = 2) {
  const now = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Bangkok" }));
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const all: Date[] = [];

  for (let offset = -6; offset < 6; offset++) {
    const m = today.getMonth() + offset;
    const y = today.getFullYear() + Math.floor(m / 12);
    const month = ((m % 12) + 12) % 12;
    for (const day of [1, 16]) {
      try {
        all.push(new Date(y, month, day));
      } catch { /* skip */ }
    }
  }

  all.sort((a, b) => a.getTime() - b.getTime());
  const fmt = (d: Date) =>
    `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;

  const past = all.filter((d) => d <= today).slice(-pastCount).map(fmt);
  const future = all.filter((d) => d > today).slice(0, futureCount).map(fmt);
  return { past, future };
}

export function isDrawDay(d?: Date): boolean {
  const now = d ?? new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Bangkok" }));
  return now.getDate() === 1 || now.getDate() === 16;
}

export function isDrawPast(periodDate: string): boolean {
  const now = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Bangkok" }));
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const draw = new Date(periodDate + "T00:00:00+07:00");
  return draw <= today;
}

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
