'use client';
// TIME CAPSULE, browser side. The letter is sealed in this browser's localStorage under 'nt-capsule'
// ({ text, openAt, sealedAt } as ISO dates) and nowhere else. The home page reads the same key to say
// "a letter from you arrived". An optional email reminder only sends the address and the opening time
// to the server, which schedules one email (Resend, at most 30 days ahead) and keeps nothing.
import { connect } from '@/lib/wisp';

export const KEY = 'nt-capsule';
export const MAX_DAYS = 29; // with an email reminder: Resend schedules at most 30 days out; letters open at 9:00 local time
export const MAX_DAYS_NO_EMAIL = 365; // without one, the letter just waits in this browser
const DAY = 86400_000;

export function storageOk() {
  try {
    const k = '__nt_probe';
    localStorage.setItem(k, '1');
    localStorage.removeItem(k);
    return true;
  } catch {
    return false;
  }
}

export function readCapsule() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const c = JSON.parse(raw);
    if (!c || typeof c.text !== 'string' || !Number.isFinite(Date.parse(c.openAt))) return null;
    return { text: c.text, openAt: c.openAt, sealedAt: Number.isFinite(Date.parse(c.sealedAt)) ? c.sealedAt : c.openAt };
  } catch {
    return null;
  }
}

export function sealCapsule(text, openAt) {
  try {
    localStorage.setItem(KEY, JSON.stringify({ text, openAt: new Date(openAt).toISOString(), sealedAt: new Date().toISOString() }));
    return true;
  } catch {
    return false;
  }
}

export function clearCapsule() {
  try {
    localStorage.removeItem(KEY);
  } catch {}
}

// ---------- dates ----------

const at9 = (d) => {
  const x = new Date(d);
  x.setHours(9, 0, 0, 0);
  return x;
};
export function openTime(pick, dateStr, now = new Date()) {
  if (pick === 'Week') return at9(now.getTime() + 7 * DAY);
  if (pick === 'Month') return at9(now.getTime() + MAX_DAYS * DAY);
  if (pick === 'Date' && /^\d{4}-\d{2}-\d{2}$/.test(dateStr || '')) {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d, 9, 0, 0, 0);
  }
  return null;
}
const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
export const dateBounds = (now = new Date(), withEmail = true) => ({
  min: ymd(new Date(now.getTime() + DAY)),
  max: ymd(new Date(now.getTime() + (withEmail ? MAX_DAYS : MAX_DAYS_NO_EMAIL) * DAY))
});
// the reminder can be scheduled for this opening time (Resend: up to 30 days ahead)
export const remindable = (openAt, now = Date.now()) => new Date(openAt).getTime() - now <= 30 * DAY - 60_000;

const fmt = (d, o) => new Intl.DateTimeFormat('en-GB', o).format(new Date(d));
export const longDate = (d) => fmt(d, { day: 'numeric', month: 'long' }); // 15 October
export const shortDate = (d) => fmt(d, { day: 'numeric', month: 'short' }).toLowerCase().replace('.', '').replace('sept', 'sep'); // 15 oct
export const lowerDate = (d) => longDate(d).toLowerCase(); // 15 october
export const upperDate = (d) => longDate(d).toUpperCase(); // 15 OCTOBER
export const upperDay = (d) => `${fmt(d, { weekday: 'long' })}, ${longDate(d)}`.toUpperCase(); // SUNDAY, 11 OCTOBER

export function agoText(sealedAt, now = Date.now()) {
  const days = Math.floor((now - Date.parse(sealedAt)) / DAY);
  if (days < 1) return 'earlier today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days} days ago`;
  if (days < 14) return 'a week ago';
  if (days < 21) return 'two weeks ago';
  if (days < 28) return 'three weeks ago';
  if (days < 45) return 'a month ago';
  return `${Math.round(days / 30)} months ago`;
}

export function leftText(openAt, now = Date.now()) {
  const ms = Date.parse(openAt) - now;
  const days = Math.ceil(ms / DAY);
  if (ms < 12 * 3600_000) return 'a few more hours';
  if (days <= 1) return '1 more day';
  return `${days} more days`;
}

export const isEmail = (e) =>
  typeof e === 'string' && e.length <= 254 && /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/.test(e);

// Ask the server to schedule the reminder. Resolves { ok } or { error }.
export function remindByEmail(email, openAt, waitMs = 6000) {
  return new Promise((resolve) => {
    let s;
    try {
      s = connect();
    } catch {
      return resolve({ error: 'offline' });
    }
    const send = () => s.timeout(8000).emit('capsule:remind', { email, openAt: new Date(openAt).toISOString() }, (err, res) => resolve(err ? { error: 'timeout' } : res || { error: 'unavailable' }));
    if (s.connected) return send();
    const t = setTimeout(() => {
      s.off('connect', go);
      resolve({ error: 'offline' });
    }, waitMs);
    function go() {
      clearTimeout(t);
      send();
    }
    s.once('connect', go);
  });
}
