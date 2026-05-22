/** Extract 6-digit lottery numbers from freeform text. */

const STRICT = /^\d{6}$/;

export function parseNumbers(text: string): { numbers: string[]; invalidCount: number } {
  const tokens = text.trim().split(/[,;\s\n\r\t|]+/);
  const numbers: string[] = [];
  const seen = new Set<string>();
  let invalidCount = 0;

  for (let tok of tokens) {
    tok = tok.trim();
    if (!tok) continue;

    // Zero-pad short numeric tokens
    if (/^\d+$/.test(tok) && tok.length <= 6) {
      tok = tok.padStart(6, "0");
    }

    if (STRICT.test(tok)) {
      if (!seen.has(tok)) {
        seen.add(tok);
        numbers.push(tok);
      }
    } else if (/^\d+$/.test(tok) && tok.length > 6) {
      // Try splitting long digit strings into 6-char chunks
      for (let i = 0; i <= tok.length - 6; i += 6) {
        const chunk = tok.substring(i, i + 6);
        if (STRICT.test(chunk) && !seen.has(chunk)) {
          seen.add(chunk);
          numbers.push(chunk);
        }
      }
    } else {
      // Try to find 6-digit sequences within the token
      const matches = tok.match(/\d{6}/g);
      if (matches) {
        for (const m of matches) {
          if (!seen.has(m)) {
            seen.add(m);
            numbers.push(m);
          }
        }
      } else {
        invalidCount++;
      }
    }
  }

  return { numbers, invalidCount };
}
