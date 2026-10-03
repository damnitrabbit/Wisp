'use client';
// Small on-device flags for the V5 site. Every storage call is wrapped: private windows can throw.
import { onboarding } from '@/lib/wisp';

const ls = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch {} }
};

// When the browser blocks storage (some private windows), the age gate is remembered for this page's life only.
let memOnboarded = false;

// Passed the age gate on this device (localStorage), or at least in this tab (the older sessionStorage flag).
export function isOnboarded() {
  return memOnboarded || ls.get('nt-onboarded') === '1' || onboarding.done();
}
export function markOnboarded() {
  memOnboarded = true;
  ls.set('nt-onboarded', '1');
  onboarding.confirmAge();
  onboarding.finish();
}

// A capsule letter that has come due: localStorage 'nt-capsule' = {text, openAt (ISO), sealedAt}.
export function dueCapsule(now = Date.now()) {
  try {
    const c = JSON.parse(ls.get('nt-capsule') || 'null');
    if (!c || !c.openAt) return null;
    const t = Date.parse(c.openAt);
    return Number.isFinite(t) && t <= now ? c : null;
  } catch {
    return null;
  }
}

// Can this browser keep anything at all? (false in a storage-blocked private window)
export function storageWorks() {
  try {
    localStorage.setItem('__nt_probe', '1');
    localStorage.removeItem('__nt_probe');
    return true;
  } catch {
    return false;
  }
}

// Only allow same-site paths for ?next=
export function safeNext(n) {
  return n && n.startsWith('/') && !n.startsWith('//') ? n : null;
}
