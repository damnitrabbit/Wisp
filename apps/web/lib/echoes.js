'use client';
// ECHOES, browser side. Two small lists live in this browser's localStorage and never leave it:
//   seen:  notes that were on the wall when you last looked, so only newer ones are marked NEW
//   heard: notes you've already played
//   mine:  notes you posted, with the secret ticket that lets you delete them or their replies
// Both drop entries once the note has expired. Clearing your browser data forgets them.
import { useCallback, useEffect, useRef, useState } from 'react';
import { LIMITS } from '@wisp/shared';
import { emit, getState, connect, on as onSocket, useWisp } from '@/lib/wisp';

// ---------- limits (mirrors apps/server/src/echoes.js) ----------
export const NOTE_MAX = LIMITS.ECHO_NOTE_TEXT_MAX ?? 400; // a written echo / unsent letter
export const REPLY_MAX = LIMITS.ECHO_TEXT_MAX; // a written reply
export const VOICE_MAX_S = LIMITS.ECHO_MAX_SECONDS;
export const TO_MAX = 40;

const read = (k) => {
  try {
    return JSON.parse(localStorage.getItem(k) || '{}') || {};
  } catch {
    return {};
  }
};
const write = (k, v) => {
  try {
    localStorage.setItem(k, JSON.stringify(v));
  } catch {}
};
const fresh = (o) => {
  const now = Date.now();
  for (const k of Object.keys(o)) if ((o[k]?.exp ?? 0) < now) delete o[k];
  return o;
};

const HEARD = 'wisp.echoes.heard';
const MINE = 'wisp.echoes.mine';

export const heard = {
  all: () => fresh(read(HEARD)),
  add(id, exp) {
    const o = heard.all();
    o[id] = { exp };
    write(HEARD, o);
  }
};

// Notes that were on the wall when you last looked. NEW means "posted since you last looked",
// so a note you scrolled past and ignored stops calling for attention on your next visit.
const SEEN = 'wisp.echoes.seen';
export const seen = {
  all: () => fresh(read(SEEN)),
  addMany(notes) {
    const o = seen.all();
    for (const n of notes) o[n.id] = { exp: n.expiresAt };
    write(SEEN, o);
  }
};

export const mine = {
  all: () => fresh(read(MINE)),
  add(id, ticket, exp) {
    const o = mine.all();
    o[id] = { ticket, exp, seen: 0 };
    write(MINE, o);
  },
  seen(id, n) {
    const o = mine.all();
    if (o[id]) {
      o[id].seen = n;
      write(MINE, o);
    }
  },
  remove(id) {
    const o = mine.all();
    delete o[id];
    write(MINE, o);
  }
};

export function newTicket() {
  const b = new Uint8Array(24);
  crypto.getRandomValues(b);
  return btoa(String.fromCharCode(...b)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

export const timeLeft = (ms) => {
  if (ms <= 0) return 'FADING';
  const h = Math.floor(ms / 3600_000);
  const m = Math.floor((ms % 3600_000) / 60_000);
  return h > 0 ? `${h}H ${String(m).padStart(2, '0')}M LEFT` : `${Math.max(1, m)}M LEFT`;
};
export const secs = (s) => `0:${String(Math.round(s)).padStart(2, '0')}`;

// ---------- recording ----------

function pickMime() {
  if (typeof MediaRecorder === 'undefined') return null;
  return ['audio/webm;codecs=opus', 'audio/mp4', 'audio/webm', 'audio/ogg;codecs=opus'].find((t) => MediaRecorder.isTypeSupported(t)) ?? '';
}

// state: idle | asking | recording | done | denied | unsupported
export function useRecorder(maxSeconds) {
  const [state, setState] = useState('idle');
  const [elapsed, setElapsed] = useState(0);
  const [clip, setClip] = useState(null); // { blob, mime, duration, url }
  const rec = useRef(null);

  const cleanup = () => {
    const r = rec.current;
    if (!r) return;
    clearInterval(r.tick);
    clearTimeout(r.limit);
    r.stream.getTracks().forEach((t) => t.stop());
    rec.current = null;
  };

  const stop = useCallback(() => {
    const r = rec.current;
    if (r && r.mr.state !== 'inactive') r.mr.stop();
  }, []);

  const start = useCallback(async () => {
    const mime = pickMime();
    if (mime === null || !navigator.mediaDevices?.getUserMedia) return setState('unsupported');
    setState('asking');
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    } catch {
      return setState('denied');
    }
    const mr = new MediaRecorder(stream, mime ? { mimeType: mime, audioBitsPerSecond: 32000 } : { audioBitsPerSecond: 32000 });
    const chunks = [];
    const startedAt = Date.now();
    mr.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    mr.onstop = () => {
      const duration = Math.min(maxSeconds, (Date.now() - startedAt) / 1000);
      const type = mr.mimeType || mime || 'audio/webm';
      const blob = new Blob(chunks, { type });
      cleanup();
      if (duration < 0.5 || !blob.size) {
        setState('idle');
        return;
      }
      setClip((old) => {
        if (old?.url) URL.revokeObjectURL(old.url);
        return { blob, mime: type, duration, url: URL.createObjectURL(blob) };
      });
      setState('done');
    };
    rec.current = {
      mr,
      stream,
      tick: setInterval(() => setElapsed((Date.now() - startedAt) / 1000), 200),
      limit: setTimeout(() => mr.state !== 'inactive' && mr.stop(), maxSeconds * 1000)
    };
    setElapsed(0);
    mr.start(250);
    setState('recording');
  }, [maxSeconds]);

  const reset = useCallback(() => {
    cleanup();
    setClip((old) => {
      if (old?.url) URL.revokeObjectURL(old.url);
      return null;
    });
    setElapsed(0);
    setState('idle');
  }, []);

  useEffect(() => () => cleanup(), []);
  return { state, elapsed, clip, start, stop, reset };
}

// ---------- playback: one sound at a time across the whole wall ----------

export function usePlayer() {
  const audio = useRef(null);
  const cache = useRef(new Map()); // key -> object URL
  const [playing, setPlaying] = useState(null); // key
  const [progress, setProgress] = useState(0); // 0..1

  useEffect(() => {
    const a = new Audio();
    audio.current = a;
    const tick = () => setProgress(a.duration && Number.isFinite(a.duration) ? a.currentTime / a.duration : 0);
    const end = () => {
      setPlaying(null);
      setProgress(0);
    };
    a.addEventListener('timeupdate', tick);
    a.addEventListener('ended', end);
    return () => {
      a.pause();
      a.removeEventListener('timeupdate', tick);
      a.removeEventListener('ended', end);
      for (const url of cache.current.values()) URL.revokeObjectURL(url);
    };
  }, []);

  // load: () => Promise<{ audio, mime } | { error }>, or a ready object URL string
  const toggle = useCallback(
    async (key, load) => {
      const a = audio.current;
      if (!a) return false;
      if (playing === key) {
        a.pause();
        setPlaying(null);
        setProgress(0);
        return false;
      }
      a.pause();
      let url = typeof load === 'string' ? load : cache.current.get(key);
      if (!url) {
        setPlaying(key);
        const r = await load();
        if (!r?.audio) {
          setPlaying(null);
          return false;
        }
        url = URL.createObjectURL(new Blob([r.audio], { type: r.mime }));
        cache.current.set(key, url);
      }
      a.src = url;
      setPlaying(key);
      setProgress(0);
      try {
        await a.play();
        return true;
      } catch {
        setPlaying(null);
        return false;
      }
    },
    [playing]
  );

  const stopAll = useCallback(() => {
    audio.current?.pause();
    setPlaying(null);
    setProgress(0);
  }, []);

  return { playing, progress, toggle, stopAll };
}

// ---------- the client API (one place every page posts / reads through) ----------

// Wait (briefly) for the socket, so a page opened cold can still post.
async function online(ms = 6000) {
  connect();
  const t0 = Date.now();
  while (getState().status !== 'online' && Date.now() - t0 < ms) await new Promise((r) => setTimeout(r, 150));
  return getState().status === 'online';
}
const call = async (event, payload, timeout) => ((await online()) ? emit(event, payload, timeout) : { error: 'offline' });

// postEcho({ kind: 'echo' | 'unsent', text, to? })          a written echo or unsent letter (text ≤ NOTE_MAX)
// postEcho({ kind: 'echo' | 'unsent', clip, to? })          a voice note; clip = useRecorder().clip ({ blob, mime, duration })
// Resolves { ok: true, id, expiresAt } or { error: 'cooldown' | 'too_long' | 'empty' | 'offline' | ..., retryInMs? }.
// On success the note is remembered as yours in this browser (the ticket lets you take it down early).
// kind 'unsent' = heard only: nobody can reply. `to` (unsent only) is who it's for, e.g. "grandpa" (≤ 40 chars).
export async function postEcho({ kind = 'echo', text, to, clip, listenOnly } = {}) {
  const ticket = newTicket();
  const payload = { kind, ticket };
  if (to != null && kind === 'unsent') payload.to = String(to);
  if (listenOnly) payload.listenOnly = true;
  if (clip) {
    payload.audio = await clip.blob.arrayBuffer();
    payload.mime = clip.mime;
    payload.duration = clip.duration;
  } else payload.text = text ?? '';
  const r = await call('echoes:post', payload, 15000);
  if (r?.ok) mine.add(r.id, ticket, r.expiresAt);
  return r ?? { error: 'timeout' };
}

export const listEchoes = () => call('echoes:list');
export const getThread = (id) => call('echoes:thread', { id });
export const getAudio = (id, replyId) => call('echoes:audio', replyId ? { id, replyId } : { id }, 15000);
export const setHeard = (id, on = true) => call('echoes:heard', { id, on });
export const reportEcho = (id, replyId) => call('echoes:report', replyId ? { id, replyId } : { id });
export async function replyEcho(id, { text, clip } = {}) {
  const p = { id };
  if (clip) Object.assign(p, { audio: await clip.blob.arrayBuffer(), mime: clip.mime, duration: clip.duration });
  else p.text = text ?? '';
  return call('echoes:reply', p, 15000);
}
// Take your own note down early (needs the ticket this browser kept when you posted).
export async function takeDown(id) {
  const m = mine.all()[id];
  if (!m) return { error: 'not_allowed' };
  const r = await call('echoes:delete', { id, ticket: m.ticket });
  if (r?.ok || r?.error === 'not_found') mine.remove(id);
  return r;
}
export const isMine = (id) => Boolean(mine.all()[id]);

// ---------- live wall: the list, kept fresh as notes come and go ----------
export function useEchoList() {
  const status = useWisp((s) => s.status);
  const [notes, setNotes] = useState(null);
  const [skew, setSkew] = useState(0);
  const load = useCallback(async () => {
    const r = await listEchoes();
    if (!r?.ok) return;
    setSkew(r.now - Date.now());
    setNotes(r.notes);
  }, []);
  useEffect(() => {
    if (status === 'online') load();
  }, [status, load]);
  useEffect(() => {
    let t = null;
    const off = onSocket('echoes:changed', () => {
      clearTimeout(t);
      t = setTimeout(load, 300);
    });
    const tick = setInterval(load, 60_000); // fades and "left" labels move on even when nothing changes
    return () => {
      off();
      clearTimeout(t);
      clearInterval(tick);
    };
  }, [load]);
  return { notes, skew, reload: load };
}
