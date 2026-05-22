/**
 * API Client — communicates with the FastAPI backend.
 * Sends Telegram initData with every request for auth.
 */

const API = (() => {
  const BASE = window.location.origin;

  function getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    if (window.Telegram?.WebApp?.initData) {
      headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
    }
    return headers;
  }

  async function request(method, path, body = null) {
    const opts = { method, headers: getHeaders() };
    if (body && method !== 'GET') {
      opts.body = JSON.stringify(body);
    }
    const res = await fetch(`${BASE}${path}`, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  async function uploadFile(path, file, fieldName = 'file') {
    const form = new FormData();
    form.append(fieldName, file);
    const headers = {};
    if (window.Telegram?.WebApp?.initData) {
      headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
    }
    const res = await fetch(`${BASE}${path}`, {
      method: 'POST', headers, body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  return {
    getDates:          ()           => request('GET', '/api/dates'),
    checkNumbers:      (numbers, date) => request('POST', '/api/check', { numbers, date }),
    parseText:         (text)        => request('POST', '/api/parse', { text }),
    scanImage:         (file)        => uploadFile('/api/scan', file),
    uploadExcel:       (file)        => uploadFile('/api/upload', file),
    getSettings:       ()            => request('GET', '/api/settings'),
    setLanguage:       (lang)        => request('POST', '/api/settings/language', { language: lang }),
    toggleNotifications: ()          => request('POST', '/api/settings/notifications'),
  };
})();
