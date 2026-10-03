import { ERRORS } from '@wisp/shared';
import { POD_CLOSED } from '@wisp/shared/pods.js';
import { randomUUID } from 'node:crypto';
import { config } from './config.js';

const L = config.limits;
// Talk pod vs listen pod: a talker is matched with a listener when one is free. If no listener turns up within
// TALK_FALLBACK_MS, two talkers are matched with each other (they listen to each other). Listeners only meet
// talkers. 'any' (old clients, tests) matches whoever has waited longest.
const TALK_FALLBACK_MS = Number(process.env.TALK_FALLBACK_MS ?? 20_000);
const ROLES = new Set(['talk', 'listen', 'any']);

export class Pairs {
  constructor(hub) {
    this.hub = hub;
    this.queue = []; // user ids, oldest first
    this.pairs = new Map();
    this.reports = new Map(); // targetUserId -> { reporters:Set, first:number }
    this.blocked = new Map(); // userId -> until
    // Talkers waiting past the fallback get matched with each other on this sweep.
    this.sweep = setInterval(() => this.fallback(), Math.max(250, Math.min(2000, TALK_FALLBACK_MS / 4 || 250)));
    this.sweep.unref?.();
  }

  stop() {
    clearInterval(this.sweep);
  }

  isBlocked(user) {
    const until = this.blocked.get(user.id);
    if (!until) return false;
    if (until < Date.now()) {
      this.blocked.delete(user.id);
      return false;
    }
    return true;
  }

  waitingCount() {
    return this.queue.length;
  }

  // ---------- queue ----------

  join(user, role) {
    if (this.isBlocked(user)) return { error: ERRORS.BLOCKED };
    if (user.pairId) return { ok: true, pairId: user.pairId };
    if (!this.hub.podsOpen()) return { error: POD_CLOSED };
    const r = ROLES.has(role) ? role : 'any';
    if (this.queue.includes(user.id)) {
      user.podRole = r;
      return { ok: true, waiting: true };
    }
    this.hub.leaveEverything(user, 'switch');
    user.podRole = r;
    this.enqueue(user);
    return { ok: true, waiting: !user.pairId };
  }

  // Can these two be matched right now?
  fits(a, b, now = Date.now()) {
    const ra = a.podRole || 'any', rb = b.podRole || 'any';
    if (ra === 'any' || rb === 'any') return true;
    if (ra !== rb) return true; // a talker and a listener
    if (ra === 'listen') return false;
    // two talkers: only once one of them has waited long enough for a listener
    const waited = Math.max(a.queuedAt ? now - a.queuedAt : 0, b.queuedAt ? now - b.queuedAt : 0);
    return waited >= TALK_FALLBACK_MS;
  }

  enqueue(user) {
    // Whoever has been waiting longest gets you, unless it's the person you just left.
    // A talker takes a waiting listener first.
    const ok = (id) => {
      const other = this.hub.userById(id);
      return other && other.online && id !== user.lastPartnerId && other.lastPartnerId !== user.id && this.fits(user, other);
    };
    let idx = -1;
    if (user.podRole === 'talk') idx = this.queue.findIndex((id) => this.hub.userById(id)?.podRole === 'listen' && ok(id));
    if (idx === -1) idx = this.queue.findIndex(ok);
    if (idx === -1) {
      this.queue.push(user.id);
      user.queuedAt = Date.now();
      this.hub.toUser(user, 'pair:waiting', { since: user.queuedAt });
      return;
    }
    const [otherId] = this.queue.splice(idx, 1);
    this.match(this.hub.userById(otherId), user);
  }

  // Talkers who waited past the fallback meet each other (and anyone else who fits by now).
  fallback() {
    if (this.queue.length < 2) return;
    const now = Date.now();
    for (let i = 0; i < this.queue.length; i++) {
      const a = this.hub.userById(this.queue[i]);
      if (!a || !a.online) continue;
      for (let j = i + 1; j < this.queue.length; j++) {
        const b = this.hub.userById(this.queue[j]);
        if (!b || !b.online || a.lastPartnerId === b.id || b.lastPartnerId === a.id || !this.fits(a, b, now)) continue;
        this.queue.splice(j, 1);
        this.queue.splice(i, 1);
        this.match(a, b);
        return this.fallback();
      }
    }
  }

  // Pods closed for the night: every live pod ends at once, the line empties.
  closeAll() {
    for (const pair of [...this.pairs.values()]) {
      clearTimeout(pair.voiceTimer);
      this.pairs.delete(pair.id);
      for (const u of [pair.a, pair.b]) {
        u.pairId = null;
        this.hub.toUser(u, 'pods:closed', { where: 'pair' });
      }
    }
    for (const id of this.queue.splice(0)) {
      const u = this.hub.userById(id);
      if (u) {
        u.queuedAt = null;
        this.hub.toUser(u, 'pods:closed', { where: 'queue' });
      }
    }
  }

  leaveQueue(user) {
    const i = this.queue.indexOf(user.id);
    if (i !== -1) this.queue.splice(i, 1);
    user.queuedAt = null;
  }

  match(a, b) {
    const pair = {
      id: randomUUID(),
      a,
      b,
      startedAt: Date.now(),
      voice: 'off', // off | requested | on
      voiceBy: null,
      voiceTimer: null
    };
    this.pairs.set(pair.id, pair);
    for (const u of [a, b]) {
      u.pairId = pair.id;
      u.queuedAt = null;
      u.lastPartnerId = (u === a ? b : a).id;
    }
    this.hub.toUser(a, 'pair:matched', this.view(pair, a));
    this.hub.toUser(b, 'pair:matched', this.view(pair, b));
  }

  view(pair, user) {
    const partner = pair.a === user ? pair.b : pair.a;
    return {
      pairId: pair.id,
      partner: { id: partner.id, name: partner.name, role: partner.podRole || 'any' },
      role: user.podRole || 'any',
      startedAt: pair.startedAt,
      serverNow: Date.now(),
      voice: pair.voice,
      voiceRequestedByMe: pair.voiceBy === user.id
    };
  }

  get(user) {
    const pair = user.pairId && this.pairs.get(user.pairId);
    if (!pair) return {};
    return { pair, partner: pair.a === user ? pair.b : pair.a };
  }

  // Ends the pair. The partner is put back in line automatically; so is the leaver if they skipped.
  end(user, reason) {
    const { pair, partner } = this.get(user);
    if (!pair) return;
    clearTimeout(pair.voiceTimer);
    this.pairs.delete(pair.id);
    user.pairId = null;
    partner.pairId = null;
    this.hub.toUser(partner, 'pair:partnerLeft', { name: user.name, reason: reason === 'report' ? 'skip' : reason });
    if (this.isBlocked(partner)) return;
    if (partner.online) this.enqueue(partner);
    else partner.requeueOnResume = true;
  }

  skip(user) {
    if (!user.pairId) return { error: ERRORS.BAD_REQUEST };
    this.end(user, 'skip');
    this.enqueue(user);
    return { ok: true };
  }

  leave(user) {
    this.leaveQueue(user);
    if (user.pairId) this.end(user, 'left');
    return { ok: true };
  }

  report(user, requeue = true) {
    const { partner } = this.get(user);
    if (!partner) return { error: ERRORS.BAD_REQUEST };
    const now = Date.now();
    let r = this.reports.get(partner.id);
    if (!r || now - r.first > L.PAIR_BLOCK_MS) this.reports.set(partner.id, (r = { reporters: new Set(), first: now }));
    r.reporters.add(user.id);
    const blockNow = r.reporters.size >= L.PAIR_REPORT_THRESHOLD;
    this.end(user, 'report');
    if (requeue) this.enqueue(user);
    if (blockNow) {
      this.blocked.set(partner.id, now + L.PAIR_BLOCK_MS);
      this.reports.delete(partner.id);
      this.leaveQueue(partner);
      this.hub.toUser(partner, 'pair:blocked', { until: now + L.PAIR_BLOCK_MS });
    }
    return { ok: true };
  }

  // ---------- messages ----------

  message(user, text) {
    const { pair, partner } = this.get(user);
    if (!pair) return { error: ERRORS.BAD_REQUEST };
    const clean = this.hub.checkMessage(user, text);
    if (clean.error) return clean;
    const msg = { id: randomUUID(), from: user.id, text: clean.text, at: Date.now() };
    this.hub.toUser(partner, 'pair:message', msg); // buffered by the hub if they're reconnecting
    return { ok: true, id: msg.id, at: msg.at };
  }

  typing(user, on) {
    const { partner } = this.get(user);
    if (partner) this.hub.toUser(partner, 'pair:typing', { on: Boolean(on) });
  }

  // ---------- voice upgrade (both must agree) ----------

  voiceRequest(user) {
    const { pair, partner } = this.get(user);
    if (!pair || pair.voice !== 'off') return { error: ERRORS.BAD_REQUEST };
    pair.voice = 'requested';
    pair.voiceBy = user.id;
    const expiresAt = Date.now() + L.VOICE_REQUEST_EXPIRY_MS;
    pair.voiceTimer = setTimeout(() => {
      if (pair.voice !== 'requested') return;
      pair.voice = 'off';
      pair.voiceBy = null;
      this.hub.toUser(user, 'pair:voiceDeclined', { reason: 'expired' });
      this.hub.toUser(partner, 'pair:voiceWithdrawn', {});
    }, L.VOICE_REQUEST_EXPIRY_MS);
    pair.voiceTimer.unref?.();
    this.hub.toUser(partner, 'pair:voiceRequested', { name: user.name, expiresAt, serverNow: Date.now() });
    return { ok: true, expiresAt };
  }

  // The asker changed their mind before an answer.
  voiceCancel(user) {
    const { pair, partner } = this.get(user);
    if (!pair || pair.voice !== 'requested' || pair.voiceBy !== user.id) return { error: ERRORS.BAD_REQUEST };
    clearTimeout(pair.voiceTimer);
    pair.voice = 'off';
    pair.voiceBy = null;
    this.hub.toUser(partner, 'pair:voiceWithdrawn', {});
    return { ok: true };
  }

  voiceAnswer(user, accept) {
    const { pair, partner } = this.get(user);
    if (!pair || pair.voice !== 'requested' || pair.voiceBy === user.id) return { error: ERRORS.BAD_REQUEST };
    clearTimeout(pair.voiceTimer);
    if (!accept) {
      pair.voice = 'off';
      pair.voiceBy = null;
      this.hub.toUser(partner, 'pair:voiceDeclined', { reason: 'declined' });
      return { ok: true };
    }
    pair.voice = 'on';
    // The requester makes the offer (impolite peer); the accepter yields on glare.
    this.hub.toUser(partner, 'pair:voiceStarted', { polite: false });
    this.hub.toUser(user, 'pair:voiceStarted', { polite: true });
    return { ok: true };
  }

  voiceEnd(user) {
    const { pair, partner } = this.get(user);
    if (!pair || pair.voice === 'off') return { error: ERRORS.BAD_REQUEST };
    clearTimeout(pair.voiceTimer);
    pair.voice = 'off';
    pair.voiceBy = null;
    this.hub.toUser(partner, 'pair:voiceEnded', { by: 'partner' });
    this.hub.toUser(user, 'pair:voiceEnded', { by: 'you' });
    return { ok: true };
  }

  relay(user, event, data) {
    const { pair, partner } = this.get(user);
    if (pair && pair.voice === 'on') this.hub.toUser(partner, event, { data });
  }
}
