/** All translations — EN, TH, MY */

const EN: Record<string, string> = {
  welcome:
    "◆ <b>Welcome to Thai Lottery Checker!</b>\n\n" +
    "I can help you check Thai Government Lottery numbers.\n\n" +
    "▸ <b>What I can do:</b>\n" +
    "  • Check single or multiple numbers\n" +
    "  • Scan lottery ticket photos (AI)\n" +
    "  • Upload Excel file with numbers\n" +
    "  • Auto-notify you when results come out\n\n" +
    "Choose your language to get started:",
  help:
    "▸ <b>Available Commands</b>\n\n" +
    "/start — Start the bot & choose language\n" +
    "/check — Check lottery numbers\n" +
    "/lang — Change language\n" +
    "/settings — Bot settings\n" +
    "/help — Show this help\n\n" +
    "▸ <b>Tips:</b>\n" +
    "  • Send a photo of your ticket to scan it\n" +
    "  • Send a .xlsx file to check in bulk\n" +
    "  • Paste numbers separated by commas or newlines",
  language_set: "✓ Language set to English",
  select_date: "▸ <b>Select a lottery draw date:</b>",
  upcoming: "Upcoming",
  past: "Past",
  enter_numbers:
    "▸ <b>Send your lottery number(s)</b>\n\n" +
    "You can:\n  • Type a 6-digit number\n  • Multiple numbers separated by commas\n  • Paste a list\n\n" +
    "Example: <code>123456, 789012, 345678</code>",
  no_valid: "✗ No valid 6-digit numbers found. Please try again.",
  too_many: "⚠ Too many numbers! Maximum is {max} per submission.",
  numbers_found: "✓ Found <b>{count}</b> valid number(s). Now select a draw date:",
  checking: "● Checking your numbers...",
  winner: "★ <b>{number}</b> — {prize}! <b>฿{amount}</b>",
  no_prize: "○ {number} — No prize",
  summary:
    "\n▸ <b>Results Summary</b>\n━━━━━━━━━━━━━━━━━━\nWinners: <b>{winners}/{total}</b>\nTotal Prize: <b>฿{amount}</b>",
  no_results_yet:
    "● Results for <b>{date}</b> are not available yet.\nThe draw hasn't happened or results are still being processed.",
  pending_saved:
    "✓ <b>{count} number(s) saved!</b>\n\nDraw date: <b>{date}</b>\nI'll notify you automatically when results come out.",
  notification_header: "▸ <b>Lottery Results — {date}</b>",
  draw_day_reminder:
    "▸ <b>Draw Day Reminder!</b>\n\nToday's lottery draw ({date}) is at 3:00 PM.\nYou have pending numbers — I'll check them for you!",
  scanning: "● Scanning your lottery ticket...",
  scan_found: "✓ <b>Found {count} number(s) from your ticket:</b>\n\n{numbers}\n\nSelect a draw date to check:",
  scan_no_numbers: "✗ Could not find any lottery numbers in the image. Please try a clearer photo.",
  scan_unavailable: "⚠ Scan feature is temporarily unavailable. Please enter numbers manually.",
  excel_processing: "● Processing your Excel file...",
  excel_found: "✓ <b>Found {count} number(s) from Excel.</b>\n\nSelect a draw date to check:",
  excel_empty: "✗ No valid lottery numbers found in the file.",
  excel_error: "✗ Could not read the Excel file. Please check the format.",
  settings_title: "▸ <b>Settings</b>",
  notif_on: "Notifications: <b>ON</b>",
  notif_off: "Notifications: <b>OFF</b>",
  notif_toggled_on: "✓ Notifications turned <b>ON</b>",
  notif_toggled_off: "✓ Notifications turned <b>OFF</b>",
  error_generic: "✗ Something went wrong. Please try again later.",
  error_api: "✗ Could not connect to the lottery API. Please try again.",
  prize_first: "1st Prize",
  prize_near1: "Near 1st Prize",
  prize_second: "2nd Prize",
  prize_third: "3rd Prize",
  prize_fourth: "4th Prize",
  prize_fifth: "5th Prize",
  prize_last2: "Last 2 Digits",
  prize_last3f: "First 3 Digits",
  prize_last3b: "Last 3 Digits",
};

const TH: Record<string, string> = {
  welcome:
    "◆ <b>ยินดีต้อนรับสู่ตรวจสลากกินแบ่งรัฐบาล!</b>\n\n" +
    "ช่วยตรวจหมายเลขสลากกินแบ่งรัฐบาลได้\n\n" +
    "▸ <b>สิ่งที่ทำได้:</b>\n" +
    "  • ตรวจเลขเดียวหรือหลายเลข\n  • สแกนภาพถ่ายสลาก (AI)\n  • อัปโหลดไฟล์ Excel\n  • แจ้งเตือนอัตโนมัติเมื่อผลออก\n\n" +
    "เลือกภาษาเพื่อเริ่มต้น:",
  help:
    "▸ <b>คำสั่งที่ใช้ได้</b>\n\n/start — เริ่มต้น\n/check — ตรวจหมายเลข\n/lang — เปลี่ยนภาษา\n/settings — ตั้งค่า\n/help — ช่วยเหลือ\n\n▸ <b>เคล็ดลับ:</b>\n  • ส่งภาพสลากเพื่อสแกน\n  • ส่ง .xlsx เพื่อตรวจจำนวนมาก\n  • วางหมายเลขคั่นด้วยจุลภาค",
  language_set: "✓ ตั้งค่าภาษาเป็นไทย",
  select_date: "▸ <b>เลือกวันออกรางวัล:</b>",
  upcoming: "งวดถัดไป",
  past: "งวดที่ผ่านมา",
  enter_numbers:
    "▸ <b>ส่งหมายเลขสลาก</b>\n\n• พิมพ์เลข 6 หลัก\n• หลายเลขคั่นด้วยจุลภาค\n• วางรายการ\n\nตัวอย่าง: <code>123456, 789012</code>",
  no_valid: "✗ ไม่พบหมายเลข 6 หลักที่ถูกต้อง กรุณาลองใหม่",
  too_many: "⚠ หมายเลขมากเกินไป! สูงสุด {max} ต่อครั้ง",
  numbers_found: "✓ พบ <b>{count}</b> หมายเลขที่ถูกต้อง เลือกวันออกรางวัล:",
  checking: "● กำลังตรวจหมายเลข...",
  winner: "★ <b>{number}</b> — {prize}! <b>฿{amount}</b>",
  no_prize: "○ {number} — ไม่ถูกรางวัล",
  summary:
    "\n▸ <b>สรุปผล</b>\n━━━━━━━━━━━━━━━━━━\nถูกรางวัล: <b>{winners}/{total}</b>\nรวมเงินรางวัล: <b>฿{amount}</b>",
  no_results_yet: "● ผลรางวัลงวด <b>{date}</b> ยังไม่ออก",
  pending_saved: "✓ <b>บันทึก {count} หมายเลขแล้ว!</b>\n\nงวดวันที่: <b>{date}</b>\nจะแจ้งเตือนอัตโนมัติเมื่อผลออก",
  notification_header: "▸ <b>ผลสลากกินแบ่ง — {date}</b>",
  draw_day_reminder: "▸ <b>แจ้งเตือนวันออกรางวัล!</b>\n\nวันนี้ ({date}) ออกรางวัลเวลา 15:00 น.",
  scanning: "● กำลังสแกนสลาก...",
  scan_found: "✓ <b>พบ {count} หมายเลขจากสลาก:</b>\n\n{numbers}\n\nเลือกวันออกรางวัล:",
  scan_no_numbers: "✗ ไม่พบหมายเลขสลากในภาพ กรุณาถ่ายภาพให้ชัดขึ้น",
  scan_unavailable: "⚠ ระบบสแกนไม่สามารถใช้งานได้ชั่วคราว กรุณากรอกหมายเลขด้วยตนเอง",
  excel_processing: "● กำลังประมวลผลไฟล์ Excel...",
  excel_found: "✓ <b>พบ {count} หมายเลขจาก Excel</b>\n\nเลือกวันออกรางวัล:",
  excel_empty: "✗ ไม่พบหมายเลขสลากที่ถูกต้องในไฟล์",
  excel_error: "✗ ไม่สามารถอ่านไฟล์ Excel ได้",
  settings_title: "▸ <b>ตั้งค่า</b>",
  notif_on: "การแจ้งเตือน: <b>เปิด</b>",
  notif_off: "การแจ้งเตือน: <b>ปิด</b>",
  notif_toggled_on: "✓ เปิดการแจ้งเตือนแล้ว",
  notif_toggled_off: "✓ ปิดการแจ้งเตือนแล้ว",
  error_generic: "✗ เกิดข้อผิดพลาด กรุณาลองใหม่",
  error_api: "✗ ไม่สามารถเชื่อมต่อ API ได้ กรุณาลองใหม่",
  prize_first: "รางวัลที่ 1",
  prize_near1: "รางวัลข้างเคียงรางวัลที่ 1",
  prize_second: "รางวัลที่ 2",
  prize_third: "รางวัลที่ 3",
  prize_fourth: "รางวัลที่ 4",
  prize_fifth: "รางวัลที่ 5",
  prize_last2: "เลขท้าย 2 ตัว",
  prize_last3f: "เลขหน้า 3 ตัว",
  prize_last3b: "เลขท้าย 3 ตัว",
};

const MY: Record<string, string> = {
  welcome:
    "◆ <b>ထိုင်းအစိုးရထီစစ်ဆေးစနစ်မှ ကြိုဆိုပါသည်!</b>\n\n" +
    "ထိုင်းအစိုးရထီနံပါတ်များကို စစ်ဆေးပေးနိုင်ပါသည်။\n\n" +
    "▸ <b>လုပ်ဆောင်နိုင်သည်များ:</b>\n" +
    "  • နံပါတ်တစ်ခုသို့မဟုတ်အများအပြား စစ်ဆေးခြင်း\n  • ထီလက်မှတ်ဓာတ်ပုံ စကင်ဖတ်ခြင်း (AI)\n  • Excel ဖိုင်တင်ခြင်း\n  • ရလဒ်ထွက်လာသောအခါ အလိုအလျောက်အကြောင်းကြားခြင်း\n\n" +
    "ဘာသာစကားကိုရွေးချယ်ပါ:",
  help:
    "▸ <b>ကွန်မန်းများ</b>\n\n/start — စတင်ပါ\n/check — ထီနံပါတ်စစ်ဆေးပါ\n/lang — ဘာသာစကားပြောင်းပါ\n/settings — ဆက်တင်\n/help — အကူအညီ",
  language_set: "✓ ဘာသာစကား မြန်မာ သို့ပြောင်းပြီး",
  select_date: "▸ <b>ထီထွက်ရက် ရွေးချယ်ပါ:</b>",
  upcoming: "လာမည့်အကြိမ်",
  past: "ပြီးခဲ့သောအကြိမ်",
  enter_numbers:
    "▸ <b>ထီနံပါတ်(များ) ထည့်ပါ</b>\n\n• ဂဏန်း ၆ လုံး ရိုက်ထည့်ပါ\n• ကော်မာဖြင့် ပိုင်းခြားပါ\n\nဥပမာ: <code>123456, 789012</code>",
  no_valid: "✗ မှန်ကန်သော ဂဏန်း ၆ လုံး မတွေ့ပါ။",
  too_many: "⚠ နံပါတ်အများကြီးထည့်လွန်းပါသည်! အများဆုံး {max} ခု",
  numbers_found: "✓ နံပါတ် <b>{count}</b> ခုတွေ့ပါသည်။ ထီထွက်ရက်ရွေးချယ်ပါ:",
  checking: "● စစ်ဆေးနေပါသည်...",
  winner: "★ <b>{number}</b> — {prize}! <b>฿{amount}</b>",
  no_prize: "○ {number} — ဆုမရရှိပါ",
  summary:
    "\n▸ <b>ရလဒ်အနှစ်ချုပ်</b>\n━━━━━━━━━━━━━━━━━━\nဆုရ: <b>{winners}/{total}</b>\nစုစုပေါင်းဆုငွေ: <b>฿{amount}</b>",
  no_results_yet: "● <b>{date}</b> ရလဒ်များ မရရှိသေးပါ။",
  pending_saved: "✓ <b>နံပါတ် {count} ခုသိမ်းဆည်းပြီး!</b>\n\nထီထွက်ရက်: <b>{date}</b>\nရလဒ်ထွက်လာသောအခါ အကြောင်းကြားပါမည်။",
  notification_header: "▸ <b>ထီရလဒ်များ — {date}</b>",
  draw_day_reminder: "▸ <b>ထီထွက်ရက်သတိပေးချက်!</b>\n\nယနေ့ ({date}) ထီဖွင့်ချိန် ညနေ ၃:၀၀",
  scanning: "● စကင်ဖတ်နေပါသည်...",
  scan_found: "✓ <b>နံပါတ် {count} ခုတွေ့ပါသည်:</b>\n\n{numbers}\n\nထီထွက်ရက်ရွေးချယ်ပါ:",
  scan_no_numbers: "✗ ဓာတ်ပုံတွင် ထီနံပါတ်မတွေ့ပါ။",
  scan_unavailable: "⚠ စကင်ဖတ်မှု ယာယီမရနိုင်ပါ။",
  excel_processing: "● Excel ဖိုင်စီမံနေပါသည်...",
  excel_found: "✓ <b>Excel မှနံပါတ် {count} ခုတွေ့ပါသည်။</b>\n\nထီထွက်ရက်ရွေးချယ်ပါ:",
  excel_empty: "✗ ဖိုင်တွင် ထီနံပါတ်မတွေ့ပါ။",
  excel_error: "✗ Excel ဖိုင်ဖတ်၍မရပါ။",
  settings_title: "▸ <b>ဆက်တင်များ</b>",
  notif_on: "အကြောင်းကြားမှု: <b>ဖွင့်</b>",
  notif_off: "အကြောင်းကြားမှု: <b>ပိတ်</b>",
  notif_toggled_on: "✓ အကြောင်းကြားမှုဖွင့်ပြီး",
  notif_toggled_off: "✓ အကြောင်းကြားမှုပိတ်ပြီး",
  error_generic: "✗ တစ်ခုခုမှားယွင်းသွားပါသည်။",
  error_api: "✗ API နှင့်ချိတ်ဆက်၍မရပါ။",
  prize_first: "ပထမဆု",
  prize_near1: "ပထမဆုနီးစပ်ဆု",
  prize_second: "ဒုတိယဆု",
  prize_third: "တတိယဆု",
  prize_fourth: "စတုတ္ထဆု",
  prize_fifth: "ပဉ္စမဆု",
  prize_last2: "နောက်ဆုံး ဂဏန်း ၂ လုံး",
  prize_last3f: "ရှေ့ ဂဏန်း ၃ လုံး",
  prize_last3b: "နောက် ဂဏန်း ၃ လုံး",
};

const LANGS: Record<string, Record<string, string>> = { en: EN, th: TH, my: MY };

export function t(key: string, lang = "en", params?: Record<string, string | number>): string {
  const strings = LANGS[lang] ?? EN;
  let text = strings[key] ?? EN[key] ?? `[${key}]`;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      text = text.replaceAll(`{${k}}`, String(v));
    }
  }
  return text;
}
