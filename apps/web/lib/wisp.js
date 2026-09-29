'use client';
// One socket for the whole app, plus a tiny store the pages subscribe to.
import { io } from 'socket.io-client';
import { useSyncExternalStore } from 'react';

const SIGNAL_URL = process.env.NEXT_PUBLIC_SIGNAL_URL || 'http://localhost:8080';
const OFFLINE_AFTER_MS = 30_000; // matches the server's reconnect grace

let socket = null;
let lostTimer = null;
let toastId = 0;
const subs = new Set();
const INITIAL = {
  status: 'idle', // idle | connecting | online | reconnecting | offline | replaced
  session: null,
  lobby: { channels: [], online: null, waiting: 0 },
  attempt: 0,
  lostAt: null,
  toasts: [],
  clockOffset: 0
};
let state = INITIAL;

function set(patch) {
  state = { ...state, ...(typeof patch === 'function' ? patch(state) : patch) };
  for (const fn of subs) fn();
}

export function useWisp(select = (s) => s) {
  return select(useSyncExternalStore((fn) => (subs.add(fn), () => subs.delete(fn)), () => state, () => INITIAL));
}
export const getState = () => state;

// ---------- storage (sessionStorage for the session, localStorage only if you opt in) ----------

const ss = {
  get: (k) => { try { return sessionStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { sessionStorage.setItem(k, v); } catch {} }
};
const ls = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch {} },
  del: (k) => { try { localStorage.removeItem(k); } catch {} }
};

export const onboarding = {
  done: () => ss.get('wisp.onboarded') === '1',
  finish: () => ss.set('wisp.onboarded', '1'),
  ageOk: () => ss.get('wisp.age') === '1',
  confirmAge: () => ss.set('wisp.age', '1'),
  // Which onboarding screen this tab is on, so leaving and coming Back resumes it.
  getStep: () => {
    const [step, n] = (ss.get('wisp.obstep') || '').split(':');
    if (!['boot', 'age', 'under18', 'slides', 'mode'].includes(step)) return null;
    const slide = Number(n);
    return { step, slide: slide >= 0 && slide <= 2 ? slide : 0 };
  },
  setStep: (step, slide) => ss.set('wisp.obstep', `${step}:${slide}`)
};

export const remember = {
  decided: () => ls.get('wisp.remember') !== null,
  on: () => ls.get('wisp.remember') === '1',
  accept(name) {
    ls.set('wisp.remember', '1');
    if (name) ls.set('wisp.name', name);
  },
  decline() {
    ls.set('wisp.remember', '0');
    ls.del('wisp.name');
  }
};

function token() {
  let t = ss.get('wisp.token');
  if (!t) {
    const bytes = crypto.getRandomValues(new Uint8Array(24));
    t = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
    ss.set('wisp.token', t);
  }
  return t;
}

// ---------- toasts ----------

export function toast({ tag, text, kind = 'outline', ttl, key, pulse = false, sticky = false }) {
  const id = ++toastId;
  set((s) => ({ toasts: [...s.toasts.filter((t) => !key || t.key !== key), { id, tag, text, kind, key, pulse, sticky }].slice(-3) }));
  const life = sticky ? 0 : ttl ?? (kind === 'solid' ? 9000 : 6000);
  if (life > 0) setTimeout(() => dismiss(id), life);
  return id;
}
export const dismiss = (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id && t.key !== id) }));

// ---------- clock ----------

// Server timestamps are converted with this offset so countdowns match across devices.
export function syncClock(serverNow) {
  if (typeof serverNow === 'number') set({ clockOffset: serverNow - Date.now() });
}
export const serverNow = () => Date.now() + state.clockOffset;

// ---------- socket ----------

export function connect() {
  if (socket) return socket;
  set({ status: 'connecting' });
  const name = remember.on() ? ls.get('wisp.name') : undefined;
  socket = io(SIGNAL_URL, {
    auth: { token: token(), name },
    transports: ['websocket', 'polling'],
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 8000
  });

  socket.on('session:ready', (s) => {
    const prev = state.session;
    if (s.token) ss.set('wisp.token', s.token);
    if (remember.on()) ls.set('wisp.name', s.name);
    clearTimeout(lostTimer);
    const wasLost = state.status === 'reconnecting' || state.status === 'offline';
    set({ status: 'online', session: s, attempt: 0, lostAt: null });
    dismiss('reconnecting');
    if (wasLost && prev) {
      if (s.resumed) toast({ key: 'back', tag: '[ BACK ONLINE ]', text: 'RECONNECTED. YOU KEPT YOUR PLACE.' });
      else toast({ key: 'back', tag: '[ BACK ONLINE ]', text: 'RECONNECTED. ANYTHING THAT WAS IN MEMORY STARTED FRESH, SO YOU HAVE A NEW NAME.' });
    }
    bus.emit('session', { resumed: s.resumed, fresh: Boolean(prev) && !s.resumed });
  });

  socket.on('channels:list', (lobby) => set({ lobby }));

  socket.on('disconnect', (reason) => {
    if (state.status === 'replaced') return;
    if (reason === 'io client disconnect') return;
    set({ status: 'reconnecting', lostAt: Date.now() });
    clearTimeout(lostTimer);
    lostTimer = setTimeout(() => {
      if (state.status === 'reconnecting') set({ status: 'offline' });
    }, OFFLINE_AFTER_MS);
  });
  socket.io.on('reconnect_attempt', (n) => set({ attempt: n }));
  socket.on('connect_error', () => {
    if (state.status === 'connecting') {
      set({ status: 'reconnecting', lostAt: state.lostAt ?? Date.now() });
      clearTimeout(lostTimer);
      lostTimer = setTimeout(() => {
        if (state.status === 'reconnecting') set({ status: 'offline' });
      }, OFFLINE_AFTER_MS);
    }
  });
  socket.on('session:replaced', () => {
    set({ status: 'replaced' });
    socket.disconnect();
  });
  return socket;
}

export function retryNow() {
  if (!socket) return connect();
  socket.connect();
}

export function emit(event, payload = {}, timeoutMs = 8000) {
  const s = connect();
  return new Promise((resolve) => {
    if (!s.connected) return resolve({ error: 'offline' });
    s.timeout(timeoutMs).emit(event, payload, (err, res) => resolve(err ? { error: 'timeout' } : res));
  });
}

// Fire-and-forget (signaling messages don't need acks).
export function send(event, payload = {}) {
  connect().emit(event, payload);
}

export function on(event, fn) {
  const s = connect();
  s.on(event, fn);
  return () => s.off(event, fn);
}

// In-app events that aren't socket messages.
export const bus = {
  fns: new Map(),
  on(e, fn) {
    if (!this.fns.has(e)) this.fns.set(e, new Set());
    this.fns.get(e).add(fn);
    return () => this.fns.get(e).delete(fn);
  },
  emit(e, p) {
    for (const fn of this.fns.get(e) ?? []) fn(p);
  }
};

let iceCache = null;
export async function iceServers() {
  if (iceCache && iceCache.at > Date.now() - 6 * 3600_000) return iceCache.list;
  const r = await emit('ice:request');
  const list = r?.iceServers ?? [{ urls: ['stun:stun.cloudflare.com:3478', 'stun:stun.l.google.com:19302'] }];
  iceCache = { list, at: Date.now() };
  return list;
}
