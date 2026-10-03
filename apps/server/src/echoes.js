import { randomUUID } from 'node:crypto';
import { ECHO_TAGS, ERRORS } from '@wisp/shared';
import { config } from './config.js';

const L = config.limits;
const TICKET_RE = /^[A-Za-z0-9_-]{16,128}$/;
const MIME_RE = /^audio\/[a-z0-9.+-]{1,30}(;\s?codecs=[a-z0-9.,"' -]{1,40})?$/i;
// A written echo or unsent letter (V5): up to this many characters. "to" is who an unsent letter is for.
export const NOTE_TEXT_MAX = L.ECHO_NOTE_TEXT_MAX ?? 400;
export const TO_MAX = 40;
export const KINDS = Object.freeze(['echo', 'unsent']);
const clean = (t) => t.replace(/[\u0000-\u0008\u000B-\u001F\u007F]/g, '').replace(/[ \t]+/g, ' ').replace(/\n{3,}/g, '\n\n').trim();

// ECHOES: a public wall of short voice notes that strangers can listen to and answer by voice or text.
// Everything here lives in this process's memory only. Notes (and their replies) are deleted
// 24 hours after they were posted, when enough people report them, when their poster deletes
// them, or when the server restarts. Nothing is ever written to disk.
export class Echoes {
  constructor(hub) {
    this.hub = hub;
    this.notes = new Map(); // id -> note; Map keeps insertion order, so the first entry is the oldest
    this.lastPost = new Map(); // person key -> when they last posted
    this.lastReply = new Map();
    this.ipPosts = new Map(); // ip -> recent post times
    this.sweeper = setInterval(() => this.sweep(), 60_000);
    this.sweeper.unref?.();
  }

  // Who counts as "one person" depends on what's at stake:
  // - reports key on the network (IP) when we have it, so nobody can take a note down by opening three tabs;
  // - cooldowns key on the session, because mobile carriers put many strangers behind one IP.
  //   A per-IP cap on posts (below) keeps one network from flooding the wall.
  key(user) {
    return user.ip || user.token;
  }
  session(user) {
    return user.token;
  }

  count() {
    return this.notes.size;
  }

  sweep(now = Date.now()) {
    let changed = false;
    for (const [id, note] of this.notes) {
      if (note.expiresAt <= now) {
        this.notes.delete(id);
        changed = true;
      }
    }
    for (const [map, ms] of [[this.lastPost, L.ECHO_POST_COOLDOWN_MS], [this.lastReply, L.ECHO_REPLY_COOLDOWN_MS]]) {
      for (const [k, t] of map) if (t + ms <= now) map.delete(k);
    }
    for (const [ip, ts] of this.ipPosts) {
      const keep = ts.filter((t) => t + L.ECHO_POST_COOLDOWN_MS > now);
      if (keep.length) this.ipPosts.set(ip, keep);
      else this.ipPosts.delete(ip);
    }
    if (changed) this.hub.echoesChanged();
  }

  // ---------- reading ----------

  view(note, user) {
    const rk = this.key(user);
    return {
      id: note.id,
      kind: note.kind, // 'echo' (anyone can reply) | 'unsent' (a letter: heard only)
      mode: note.text != null ? 'text' : 'voice',
      text: note.text ?? undefined,
      to: note.to ?? undefined,
      tag: note.tag,
      createdAt: note.createdAt,
      expiresAt: note.expiresAt,
      duration: note.duration,
      listenOnly: note.listenOnly,
      replyCount: note.replies.length,
      heardCount: note.heard.size,
      heard: note.heard.has(rk),
      reported: note.reports.has(rk)
    };
  }

  list(user) {
    this.sweep();
    // Newest first; the client re-orders per viewer (new to you, then unanswered).
    const notes = [...this.notes.values()].reverse().map((n) => this.view(n, user));
    return { ok: true, now: Date.now(), notes };
  }

  thread(user, { id } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    const k = this.key(user);
    return {
      ok: true,
      note: this.view(note, user),
      replies: note.replies.map((r) => ({
        id: r.id,
        kind: r.kind,
        text: r.kind === 'text' ? r.text : undefined,
        duration: r.kind === 'voice' ? r.duration : undefined,
        createdAt: r.createdAt,
        reported: r.reports.has(k)
      }))
    };
  }

  audio(user, { id, replyId } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    const src = replyId ? note.replies.find((r) => r.id === replyId) : note;
    if (!src || !src.audio) return { error: ERRORS.NOT_FOUND };
    return { ok: true, mime: src.mime, audio: src.audio };
  }

  live(id) {
    const note = typeof id === 'string' ? this.notes.get(id) : null;
    if (!note) return null;
    if (note.expiresAt <= Date.now()) {
      this.notes.delete(id);
      this.hub.echoesChanged();
      return null;
    }
    return note;
  }

  // ---------- writing ----------

  checkAudio({ audio, mime, duration }) {
    const buf = Buffer.isBuffer(audio) ? audio : audio instanceof Uint8Array || audio instanceof ArrayBuffer ? Buffer.from(audio) : null;
    if (!buf || buf.length === 0) return { error: ERRORS.EMPTY };
    if (buf.length > L.ECHO_MAX_BYTES) return { error: ERRORS.TOO_LONG };
    if (typeof mime !== 'string' || !MIME_RE.test(mime)) return { error: ERRORS.BAD_REQUEST };
    const d = Number(duration);
    if (!Number.isFinite(d) || d < 0.3) return { error: ERRORS.EMPTY };
    if (d > L.ECHO_MAX_SECONDS + 1) return { error: ERRORS.TOO_LONG };
    return { buf, mime, duration: Math.round(Math.min(d, L.ECHO_MAX_SECONDS) * 10) / 10 };
  }

  cooldown(map, user, ms) {
    const last = map.get(this.session(user));
    const wait = last ? last + ms - Date.now() : 0;
    return wait > 0 ? { error: ERRORS.COOLDOWN, retryInMs: wait } : null;
  }

  // kind 'echo': anyone can listen and reply (unless listenOnly). kind 'unsent': a letter to someone who will
  // never read it; strangers can only tap "heard", never reply. A note is either written (text) or spoken (audio).
  post(user, { kind = 'echo', text, to, audio, mime, duration, tag, ticket, listenOnly = false } = {}) {
    if (!KINDS.includes(kind)) return { error: ERRORS.BAD_REQUEST };
    if (tag != null && !ECHO_TAGS.includes(tag)) return { error: ERRORS.BAD_REQUEST };
    if (typeof ticket !== 'string' || !TICKET_RE.test(ticket)) return { error: ERRORS.BAD_REQUEST };
    let body;
    if (text !== undefined && audio === undefined) {
      if (typeof text !== 'string') return { error: ERRORS.BAD_REQUEST };
      const t = clean(text);
      if (!t) return { error: ERRORS.EMPTY };
      if (t.length > NOTE_TEXT_MAX) return { error: ERRORS.TOO_LONG, max: NOTE_TEXT_MAX };
      body = { text: t, duration: 0, mime: null, audio: null };
    } else {
      const a = this.checkAudio({ audio, mime, duration });
      if (a.error) return a;
      body = { text: null, duration: a.duration, mime: a.mime, audio: a.buf };
    }
    let who = null;
    if (kind === 'unsent' && to != null) {
      if (typeof to !== 'string') return { error: ERRORS.BAD_REQUEST };
      who = clean(to).replace(/\n/g, ' ').replace(/,+$/, '').slice(0, TO_MAX) || null;
    }
    const slow = this.cooldown(this.lastPost, user, L.ECHO_POST_COOLDOWN_MS);
    if (slow) return slow;
    const now = Date.now();
    const recent = user.ip ? (this.ipPosts.get(user.ip) || []).filter((t) => t + L.ECHO_POST_COOLDOWN_MS > now) : [];
    if (recent.length >= L.ECHO_IP_POSTS) return { error: ERRORS.COOLDOWN, retryInMs: recent[0] + L.ECHO_POST_COOLDOWN_MS - now };

    while (this.notes.size >= L.ECHO_MAX_NOTES) this.notes.delete(this.notes.keys().next().value);
    const note = {
      id: randomUUID(),
      kind,
      tag: tag ?? null,
      to: who,
      createdAt: now,
      expiresAt: now + L.ECHO_TTL_MS,
      ...body,
      ticket,
      listenOnly: kind === 'unsent' || listenOnly === true,
      replies: [],
      heard: new Set(),
      reports: new Set()
    };
    this.notes.set(note.id, note);
    this.lastPost.set(this.session(user), now);
    if (user.ip) this.ipPosts.set(user.ip, [...recent, now]);
    this.hub.echoesChanged();
    return { ok: true, id: note.id, expiresAt: note.expiresAt };
  }

  // "heard" is the only reaction: one per person (network), and it can be taken back.
  hear(user, { id, on = true } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    const k = this.key(user);
    const had = note.heard.has(k);
    if (on && !had) note.heard.add(k);
    if (!on && had) note.heard.delete(k);
    if (had !== note.heard.has(k)) this.hub.echoesChanged();
    return { ok: true, heard: note.heard.has(k), heardCount: note.heard.size };
  }

  reply(user, { id, audio, mime, duration, text } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    if (note.listenOnly) return { error: ERRORS.NOT_ALLOWED };
    if (note.replies.length >= L.ECHO_MAX_REPLIES) return { error: ERRORS.FULL };

    let r;
    if (audio !== undefined) {
      const a = this.checkAudio({ audio, mime, duration });
      if (a.error) return a;
      r = { kind: 'voice', audio: a.buf, mime: a.mime, duration: a.duration };
    } else {
      if (typeof text !== 'string') return { error: ERRORS.BAD_REQUEST };
      const clean = text.replace(/\s+/g, ' ').trim();
      if (!clean) return { error: ERRORS.EMPTY };
      if (clean.length > L.ECHO_TEXT_MAX) return { error: ERRORS.TOO_LONG, max: L.ECHO_TEXT_MAX };
      r = { kind: 'text', text: clean };
    }
    const slow = this.cooldown(this.lastReply, user, L.ECHO_REPLY_COOLDOWN_MS);
    if (slow) return slow;

    Object.assign(r, { id: randomUUID(), createdAt: Date.now(), reports: new Set() });
    note.replies.push(r);
    this.lastReply.set(this.session(user), r.createdAt);
    this.hub.echoesChanged();
    return { ok: true, id: r.id };
  }

  // Anyone can report a note or a reply, once. Enough distinct reports take it down for everyone.
  report(user, { id, replyId } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    const target = replyId ? note.replies.find((r) => r.id === replyId) : note;
    if (!target) return { error: ERRORS.NOT_FOUND };
    const k = this.key(user);
    if (target.reports.has(k)) return { ok: true, already: true };
    target.reports.add(k);
    let removed = false;
    if (target.reports.size >= L.ECHO_REPORT_HIDE) {
      if (replyId) note.replies.splice(note.replies.indexOf(target), 1);
      else this.notes.delete(note.id);
      removed = true;
    }
    this.hub.echoesChanged();
    return { ok: true, removed };
  }

  // The poster can take their own note down. The ticket lives only in their browser.
  remove(user, { id, ticket } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    if (typeof ticket !== 'string' || ticket !== note.ticket) return { error: ERRORS.NOT_ALLOWED };
    this.notes.delete(note.id);
    this.hub.echoesChanged();
    return { ok: true };
  }

  // The poster can remove any reply on their own note, no reports needed. It's their space.
  removeReply(user, { id, replyId, ticket } = {}) {
    const note = this.live(id);
    if (!note) return { error: ERRORS.NOT_FOUND };
    if (typeof ticket !== 'string' || ticket !== note.ticket) return { error: ERRORS.NOT_ALLOWED };
    const i = note.replies.findIndex((r) => r.id === replyId);
    if (i === -1) return { error: ERRORS.NOT_FOUND };
    note.replies.splice(i, 1);
    this.hub.echoesChanged();
    return { ok: true };
  }

  stop() {
    clearInterval(this.sweeper);
  }
}
