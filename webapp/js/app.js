/**
 * Thai Lottery Checker — Telegram Mini App
 * Main application logic, tab routing, and Telegram SDK integration.
 */

/* ── i18n Strings ─────────────────────────────────────────────── */
const I18N = {
  en: {
    check: 'Check', scan: 'Scan', history: 'History', settings: 'Settings',
    selectDate: 'Select Draw Date', upcoming: 'UPCOMING', past: 'PAST',
    enterNumbers: 'Enter lottery numbers',
    placeholder: 'e.g. 123456, 789012, 345678',
    checkBtn: 'Check Numbers', pasteHint: 'Separate numbers with commas, spaces, or new lines',
    orUpload: 'Or upload Excel file (.xlsx)',
    results: 'Results', noResults: 'Results not available yet for this date.',
    winners: 'Winners', totalPrize: 'Total Prize', of: 'of',
    noPrize: 'No prize', pending: 'Saved! You\'ll be notified when results are out.',
    scanTitle: 'Scan Lottery Ticket',
    scanDesc: 'Take a photo or upload an image of your lottery ticket',
    takePhoto: 'Take Photo', uploadImage: 'Upload Image',
    scanning: 'Scanning ticket...', scanFound: 'Numbers found:',
    scanEmpty: 'No numbers found. Try a clearer photo.',
    scanUnavail: 'Scan unavailable due to high demand. Please enter numbers manually.',
    confirmCheck: 'Check These Numbers',
    historyTitle: 'Check History', noHistory: 'No check history yet.',
    won: 'won', date: 'Date',
    settingsTitle: 'Settings', language: 'Language', notifications: 'Notifications',
    clearHistory: 'Clear History', clearConfirm: 'Clear all check history?',
    cleared: 'History cleared.',
    prize_first: '1st Prize', prize_near1: 'Near 1st', prize_second: '2nd Prize',
    prize_third: '3rd Prize', prize_fourth: '4th Prize', prize_fifth: '5th Prize',
    prize_last2: 'Last 2 Digits', prize_last3f: 'First 3 Digits', prize_last3b: 'Last 3 Digits',
    checking: 'Checking...', uploading: 'Processing file...',
  },
  th: {
    check: 'ตรวจ', scan: 'สแกน', history: 'ประวัติ', settings: 'ตั้งค่า',
    selectDate: 'เลือกงวด', upcoming: 'งวดถัดไป', past: 'งวดที่ผ่านมา',
    enterNumbers: 'กรอกหมายเลขสลาก',
    placeholder: 'เช่น 123456, 789012, 345678',
    checkBtn: 'ตรวจหมายเลข', pasteHint: 'คั่นด้วยจุลภาค ช่องว่าง หรือบรรทัดใหม่',
    orUpload: 'หรืออัปโหลดไฟล์ Excel (.xlsx)',
    results: 'ผลรางวัล', noResults: 'ยังไม่มีผลรางวัลสำหรับงวดนี้',
    winners: 'ถูกรางวัล', totalPrize: 'รวมเงินรางวัล', of: 'จาก',
    noPrize: 'ไม่ถูกรางวัล', pending: 'บันทึกแล้ว! จะแจ้งเตือนเมื่อผลออก',
    scanTitle: 'สแกนสลาก',
    scanDesc: 'ถ่ายภาพหรืออัปโหลดรูปภาพสลากของคุณ',
    takePhoto: 'ถ่ายภาพ', uploadImage: 'อัปโหลดรูป',
    scanning: 'กำลังสแกน...', scanFound: 'พบหมายเลข:',
    scanEmpty: 'ไม่พบหมายเลข ลองถ่ายภาพให้ชัดขึ้น',
    scanUnavail: 'ระบบสแกนไม่พร้อมใช้งาน กรุณากรอกหมายเลขด้วยตนเอง',
    confirmCheck: 'ตรวจหมายเลขเหล่านี้',
    historyTitle: 'ประวัติการตรวจ', noHistory: 'ยังไม่มีประวัติ',
    won: 'ถูก', date: 'วันที่',
    settingsTitle: 'ตั้งค่า', language: 'ภาษา', notifications: 'การแจ้งเตือน',
    clearHistory: 'ล้างประวัติ', clearConfirm: 'ล้างประวัติการตรวจทั้งหมด?',
    cleared: 'ล้างประวัติแล้ว',
    prize_first: 'รางวัลที่ 1', prize_near1: 'ข้างเคียง', prize_second: 'รางวัลที่ 2',
    prize_third: 'รางวัลที่ 3', prize_fourth: 'รางวัลที่ 4', prize_fifth: 'รางวัลที่ 5',
    prize_last2: 'เลขท้าย 2 ตัว', prize_last3f: 'เลขหน้า 3 ตัว', prize_last3b: 'เลขท้าย 3 ตัว',
    checking: 'กำลังตรวจ...', uploading: 'กำลังประมวลผล...',
  },
  my: {
    check: 'စစ်ဆေး', scan: 'စကင်', history: 'မှတ်တမ်း', settings: 'ဆက်တင်',
    selectDate: 'ထီထွက်ရက် ရွေးပါ', upcoming: 'လာမည့်', past: 'ပြီးခဲ့သော',
    enterNumbers: 'ထီနံပါတ်များ ထည့်ပါ',
    placeholder: 'ဥပမာ 123456, 789012, 345678',
    checkBtn: 'စစ်ဆေးပါ', pasteHint: 'ကော်မာ၊ နေရာလွတ်၊ စာကြောင်းအသစ်ဖြင့် ပိုင်းခြားပါ',
    orUpload: 'သို့မဟုတ် Excel ဖိုင် တင်ပါ (.xlsx)',
    results: 'ရလဒ်', noResults: 'ဤရက်အတွက် ရလဒ်များ မရရှိသေးပါ',
    winners: 'ဆုရ', totalPrize: 'စုစုပေါင်း ဆုငွေ', of: '/',
    noPrize: 'ဆုမရရှိပါ', pending: 'သိမ်းပြီး! ရလဒ်ထွက်ချိန် အကြောင်းကြားပါမည်',
    scanTitle: 'ထီစကင်ဖတ်ပါ',
    scanDesc: 'ထီလက်မှတ် ဓာတ်ပုံရိုက်ပါ သို့မဟုတ် ရုပ်ပုံတင်ပါ',
    takePhoto: 'ဓာတ်ပုံရိုက်', uploadImage: 'ရုပ်ပုံတင်',
    scanning: 'စကင်ဖတ်နေသည်...', scanFound: 'နံပါတ်များ တွေ့ပါသည်:',
    scanEmpty: 'နံပါတ် မတွေ့ပါ။ ပိုရှင်းသော ဓာတ်ပုံ ထပ်ကြိုးစားပါ',
    scanUnavail: 'စကင်ဖတ်မှု မရနိုင်ပါ။ နံပါတ်ကို ကိုယ်တိုင် ထည့်ပါ',
    confirmCheck: 'ဤနံပါတ်များကို စစ်ဆေးပါ',
    historyTitle: 'စစ်ဆေးမှု မှတ်တမ်း', noHistory: 'မှတ်တမ်း မရှိသေးပါ',
    won: 'ဆုရ', date: 'ရက်',
    settingsTitle: 'ဆက်တင်', language: 'ဘာသာစကား', notifications: 'အကြောင်းကြားမှု',
    clearHistory: 'မှတ်တမ်း ရှင်းပါ', clearConfirm: 'စစ်ဆေးမှုမှတ်တမ်း အားလုံး ရှင်းမလား?',
    cleared: 'မှတ်တမ်း ရှင်းပြီး',
    prize_first: 'ပထမဆု', prize_near1: 'နီးစပ်ဆု', prize_second: 'ဒုတိယဆု',
    prize_third: 'တတိယဆု', prize_fourth: 'စတုတ္ထဆု', prize_fifth: 'ပဉ္စမဆု',
    prize_last2: 'နောက် ၂ လုံး', prize_last3f: 'ရှေ့ ၃ လုံး', prize_last3b: 'နောက် ၃ လုံး',
    checking: 'စစ်ဆေးနေသည်...', uploading: 'စီမံနေသည်...',
  },
};

const PRIZE_AMOUNTS = {
  first: 6000000, near1: 100000, second: 200000, third: 80000,
  fourth: 40000, fifth: 20000, last2: 2000, last3f: 4000, last3b: 4000,
};

/* ── App State ────────────────────────────────────────────────── */
let lang = 'en';
let selectedDate = null;
let scannedNumbers = [];
let dates = { past: [], future: [] };

const tg = window.Telegram?.WebApp;

function t(key) { return (I18N[lang] || I18N.en)[key] || key; }

function formatMoney(n) { return '฿' + Number(n).toLocaleString(); }

function formatDate(d) {
  try {
    const dt = new Date(d + 'T00:00:00');
    return dt.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch { return d; }
}

/* ── Init ─────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', async () => {
  if (tg) {
    tg.ready();
    tg.expand();
    tg.disableVerticalSwipes();

    // Detect language from Telegram
    const userLang = tg.initDataUnsafe?.user?.language_code || 'en';
    if (userLang === 'th') lang = 'th';
    else if (userLang === 'my') lang = 'my';
  }

  // Try to load user settings
  try {
    const settings = await API.getSettings();
    if (settings.language) lang = settings.language;
  } catch { /* first visit */ }

  updateUILanguage();
  switchTab('check');
  await loadDates();
});

/* ── Tab Navigation ───────────────────────────────────────────── */
function switchTab(tabId) {
  // Update nav
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.tab === tabId);
  });
  // Update pages
  document.querySelectorAll('.tab-page').forEach(el => {
    el.classList.toggle('active', el.id === 'page-' + tabId);
  });
  // Haptic
  if (tg?.HapticFeedback) tg.HapticFeedback.selectionChanged();

  // Load data for tab
  if (tabId === 'history') loadHistory();
  if (tabId === 'settings') loadSettings();
}

// Bind nav clicks
document.querySelectorAll('.nav-item').forEach(el => {
  el.addEventListener('click', () => switchTab(el.dataset.tab));
});

/* ── Language ─────────────────────────────────────────────────── */
function updateUILanguage() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  // Update lang buttons
  document.querySelectorAll('.lang-btn').forEach(el => {
    el.classList.toggle('active', el.dataset.lang === lang);
  });
}

async function setLanguage(newLang) {
  lang = newLang;
  updateUILanguage();
  if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
  try { await API.setLanguage(newLang); } catch { /* ok */ }
}

/* ── Loading Overlay ──────────────────────────────────────────── */
function showLoading(text = '') {
  const overlay = document.getElementById('loading-overlay');
  document.getElementById('loading-text').textContent = text || t('checking');
  overlay.classList.add('active');
}

function hideLoading() {
  document.getElementById('loading-overlay').classList.remove('active');
}

/* ── Dates ────────────────────────────────────────────────────── */
async function loadDates() {
  try {
    dates = await API.getDates();
    renderDates();
  } catch (e) {
    console.error('Failed to load dates:', e);
  }
}

function renderDates() {
  const grid = document.getElementById('date-grid');
  grid.innerHTML = '';

  // Future dates
  if (dates.future?.length) {
    const label = document.createElement('div');
    label.className = 'section-header';
    label.style.gridColumn = '1 / -1';
    label.textContent = t('upcoming');
    grid.appendChild(label);

    dates.future.forEach(d => {
      const btn = createDateBtn(d, false);
      grid.appendChild(btn);
    });
  }

  // Past dates
  if (dates.past?.length) {
    const label = document.createElement('div');
    label.className = 'section-header';
    label.style.gridColumn = '1 / -1';
    label.textContent = t('past');
    grid.appendChild(label);

    [...dates.past].reverse().forEach(d => {
      const btn = createDateBtn(d, true);
      grid.appendChild(btn);
    });
  }
}

function createDateBtn(dateStr, isPast) {
  const btn = document.createElement('button');
  btn.className = 'date-btn';
  if (selectedDate === dateStr) btn.classList.add('selected');
  btn.innerHTML = `
    <div class="date-label">${formatDate(dateStr)}</div>
    <div class="date-status">${isPast ? '✓ ' + t('past') : '◇ ' + t('upcoming')}</div>
  `;
  btn.addEventListener('click', () => selectDate(dateStr));
  return btn;
}

function selectDate(dateStr) {
  selectedDate = dateStr;
  if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
  renderDates();
}

/* ── Check Numbers ────────────────────────────────────────────── */
async function checkNumbers() {
  const textarea = document.getElementById('numbers-input');
  const text = textarea.value.trim();

  if (!text) return;
  if (!selectedDate) {
    if (tg) tg.showAlert(t('selectDate'));
    else alert(t('selectDate'));
    return;
  }

  showLoading(t('checking'));
  if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');

  try {
    // Parse numbers first
    const parsed = await API.parseText(text);
    if (!parsed.numbers?.length) {
      hideLoading();
      if (tg) tg.showAlert('No valid 6-digit numbers found.');
      return;
    }

    // Check numbers
    const data = await API.checkNumbers(parsed.numbers, selectedDate);
    hideLoading();
    renderResults(data);
    // Save to local history (client-side only)
    if (data.status === 'checked') saveToLocalHistory(selectedDate, data);
    textarea.value = '';
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    hideLoading();
    console.error(e);
    if (tg) tg.showAlert(e.message);
  }
}

/* ── Upload Excel ─────────────────────────────────────────────── */
function triggerExcelUpload() {
  const input = document.getElementById('excel-input');
  input.click();
}

async function handleExcelUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  if (!selectedDate) {
    if (tg) tg.showAlert(t('selectDate'));
    else alert(t('selectDate'));
    return;
  }

  showLoading(t('uploading'));
  try {
    const parsed = await API.uploadExcel(file);
    if (!parsed.numbers?.length) {
      hideLoading();
      if (tg) tg.showAlert('No valid numbers found in file.');
      return;
    }

    const data = await API.checkNumbers(parsed.numbers, selectedDate);
    hideLoading();
    renderResults(data);
    if (data.status === 'checked') saveToLocalHistory(selectedDate, data);
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    hideLoading();
    if (tg) tg.showAlert(e.message);
  }
  event.target.value = '';
}

/* ── Results Rendering ────────────────────────────────────────── */
function renderResults(data) {
  const container = document.getElementById('results-container');
  const section = document.getElementById('results-section');

  if (data.status === 'pending') {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">◇</div>
        <p>${t('pending')}</p>
      </div>`;
    section.classList.remove('hidden');
    return;
  }

  const { results, summary } = data;

  let html = '';

  // Summary card
  if (summary.total_prize > 0) {
    html += `
      <div class="summary-card">
        <div class="summary-detail">${t('winners')}: ${summary.winners} ${t('of')} ${summary.total}</div>
        <div class="summary-prize">${formatMoney(summary.total_prize)}</div>
        <div class="summary-detail">${t('totalPrize')}</div>
      </div>`;
  }

  // Individual results
  results.forEach(r => {
    const isWin = !!r.prize_type && r.prize_type !== 'unknown';
    const prizeKey = 'prize_' + (r.prize_type || '');
    const prizeName = isWin ? t(prizeKey) || r.prize_type : t('noPrize');
    const amount = isWin ? formatMoney(r.prize_amount) : '';

    html += `
      <div class="result-item">
        <div class="result-icon ${isWin ? 'win' : 'lose'}">${isWin ? '★' : '○'}</div>
        <div class="result-info">
          <div class="result-number">${r.lottery_num}</div>
          <div class="result-prize">${prizeName}</div>
        </div>
        ${amount ? `<div class="result-amount">${amount}</div>` : ''}
      </div>`;
  });

  container.innerHTML = html;
  section.classList.remove('hidden');

  // Scroll to results
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ── Scan ─────────────────────────────────────────────────────── */
function triggerScan(useCamera) {
  const input = document.getElementById('scan-input');
  input.setAttribute('accept', 'image/*');
  if (useCamera) input.setAttribute('capture', 'environment');
  else input.removeAttribute('capture');
  input.click();
}

async function handleScanUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  showLoading(t('scanning'));
  try {
    const data = await API.scanImage(file);
    hideLoading();

    if (data.unavailable) {
      renderScanResult(null, true);
    } else if (!data.numbers?.length) {
      renderScanResult([], false);
    } else {
      scannedNumbers = data.numbers;
      renderScanResult(data.numbers, false);
    }
    if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
  } catch (e) {
    hideLoading();
    if (tg) tg.showAlert(e.message);
  }
  event.target.value = '';
}

function renderScanResult(numbers, unavailable) {
  const container = document.getElementById('scan-results');

  if (unavailable) {
    container.innerHTML = `<div class="empty-state"><p>${t('scanUnavail')}</p></div>`;
    container.classList.remove('hidden');
    return;
  }

  if (!numbers || !numbers.length) {
    container.innerHTML = `<div class="empty-state"><p>${t('scanEmpty')}</p></div>`;
    container.classList.remove('hidden');
    return;
  }

  const chips = numbers.map(n => `<span class="number-chip">${n}</span>`).join('');
  container.innerHTML = `
    <div class="section mt-12">
      <div class="section-header">${t('scanFound')}</div>
      <div class="mb-12">${chips}</div>
      <button class="btn btn-primary" onclick="checkScannedNumbers()">
        ${t('confirmCheck')}
      </button>
    </div>`;
  container.classList.remove('hidden');
}

async function checkScannedNumbers() {
  if (!scannedNumbers.length) return;
  if (!selectedDate) {
    // Switch to check tab to select date
    switchTab('check');
    document.getElementById('numbers-input').value = scannedNumbers.join(', ');
    if (tg) tg.showAlert(t('selectDate'));
    return;
  }

  showLoading(t('checking'));
  try {
    const data = await API.checkNumbers(scannedNumbers, selectedDate);
    hideLoading();
    switchTab('check');
    renderResults(data);
    if (data.status === 'checked') saveToLocalHistory(selectedDate, data);
    scannedNumbers = [];
  } catch (e) {
    hideLoading();
    if (tg) tg.showAlert(e.message);
  }
}

/* ── History (localStorage) ───────────────────────────────────── */
const HISTORY_KEY = 'lottery_history';
const MAX_HISTORY = 20;

function getLocalHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
  } catch { return []; }
}

function saveToLocalHistory(date, data) {
  const history = getLocalHistory();
  history.unshift({
    date,
    total: data.summary.total,
    winners: data.summary.winners,
    total_prize: data.summary.total_prize,
    checked_at: new Date().toISOString(),
  });
  // Keep only the latest entries
  if (history.length > MAX_HISTORY) history.length = MAX_HISTORY;
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function loadHistory() {
  const container = document.getElementById('history-list');
  const history = getLocalHistory();

  if (!history.length) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">○</div><p>${t('noHistory')}</p></div>`;
    return;
  }

  container.innerHTML = history.map(h => `
    <div class="history-item">
      <div>
        <div class="history-date">${formatDate(h.date)}</div>
        <div class="history-stats">${h.winners} ${t('won')} ${t('of')} ${h.total}</div>
      </div>
      <div class="history-prize ${h.total_prize === 0 ? 'zero' : ''}">${formatMoney(h.total_prize)}</div>
    </div>
  `).join('');
}

/* ── Settings ─────────────────────────────────────────────────── */
async function loadSettings() {
  try {
    const data = await API.getSettings();
    if (data.language) {
      lang = data.language;
      updateUILanguage();
    }
    document.getElementById('notif-toggle').checked = data.notifications;
  } catch { /* ok */ }
}

async function toggleNotifications() {
  try {
    const data = await API.toggleNotifications();
    document.getElementById('notif-toggle').checked = data.notifications;
    if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
  } catch { /* ok */ }
}

function clearHistoryAction() {
  const confirmed = confirm(t('clearConfirm'));
  if (!confirmed) return;
  localStorage.removeItem(HISTORY_KEY);
  loadHistory();
  if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
  if (tg) tg.showAlert(t('cleared'));
}
