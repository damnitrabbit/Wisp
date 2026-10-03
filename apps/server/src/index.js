import http from 'node:http';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Server } from 'socket.io';
import { CHANNELS, ERRORS } from '@wisp/shared';
import { podWindowOpen, podMinsToClose } from '@wisp/shared/pods.js';
import { config } from './config.js';
import { makeName, isValidName } from './names.js';
import { Rooms } from './rooms.js';
import { Pairs } from './pairs.js';
import { Echoes } from './echoes.js';
import { capsuleRemind } from './capsule.js';
import { getIceServers, reportRelayBytes, turnStatus } from './turn.js';

const L = config.limits;
const INSTANCE = Math.random().toString(36).slice(2, 8);
const BOOTED = Date.now();
const TOKEN_RE = /^[A-Za-z0-9_-]{16,128}$/;
// Events that are worthless after a delay are not buffered for reconnecting users.
const NO_BUFFER = /^(rtc:|pairRtc:|pair:typing|channels:list|channel:update)/;
// Pods are open 22:00–02:00 India time. PODS_ALWAYS_OPEN=1 keeps them open (testing); outside production
// (local dev) they are always open unless PODS_ALWAYS_OPEN=0.
const alwaysOpen = () => {
  const v = process.env.PODS_ALWAYS_OPEN;
  return v === '1' || (v !== '0' && process.env.NODE_ENV !== 'production');
};
export const podsOpen = (now = new Date()) => alwaysOpen() || podWindowOpen(now);

export function createWisp() {
  const users = new Map(); // id -> user
  const byToken = new Map(); // resume token -> user
  const names = new Set();

  const httpServer = http.createServer((req, res) => {
    if (req.url === '/healthz') {
      res.writeHead(200, { 'content-type': 'text/plain' });
      return res.end('ok');
    }
    if (req.url === '/status') {
      // Aggregate numbers only. Nothing here identifies anyone.
      res.writeHead(200, { 'content-type': 'application/json', 'cache-control': 'no-store' });
      return res.end(JSON.stringify({ instance: INSTANCE, upSeconds: Math.round((Date.now() - BOOTED) / 1000), online: onlineCount(), rooms: rooms.rooms.size, waiting: pairs.waitingCount(), echoes: echoes.count(), turn: turnStatus(), ipGuard: lastGuard }));
    }
    res.writeHead(200, { 'content-type': 'text/plain' });
    res.end('notrace signaling. nothing to see here.');
  });

  // Abuse guard, per IP: how many sockets are open, and how many were opened in the last minute.
  // Generous on purpose: mobile carriers put many real people behind one IP. Counts live in memory only.
  const PER_IP_OPEN = Number(process.env.PER_IP_OPEN) || 24;
  const PER_IP_PER_MIN = Number(process.env.PER_IP_PER_MIN) || 40;
  const ipOpen = new Map(); // ip -> open sockets
  const ipRecent = new Map(); // ip -> timestamps of recent connects
  // Behind a proxy, the visitor's IP only exists in x-forwarded-for. Without it every visitor would share the
  // proxy's address, so in production the guard stays off rather than locking everyone out.
  const TRUST_SOCKET_IP = process.env.NODE_ENV !== 'production';
  let lastGuard = 'off';
  const ipOf = (req) => {
    const fwd = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim();
    if (fwd) return fwd;
    return TRUST_SOCKET_IP ? req.socket.remoteAddress || null : null;
  };
  const sweep = setInterval(() => {
    const cutoff = Date.now() - 60_000;
    for (const [ip, ts] of ipRecent) {
      const keep = ts.filter((t) => t > cutoff);
      if (keep.length) ipRecent.set(ip, keep);
      else ipRecent.delete(ip);
    }
  }, 60_000);
  sweep.unref?.();

  const io = new Server(httpServer, {
    cors: { origin: config.allowedOrigins, methods: ['GET', 'POST'] },
    pingInterval: 20_000,
    pingTimeout: 20_000, // generous: phones and background tabs answer slowly
    maxHttpBufferSize: 512 * 1024, // room for one ECHOES voice note (capped at ECHO_MAX_BYTES)
    allowRequest(req, done) {
      // Browsers always send Origin; refuse other websites. (Non-browser clients can fake it: the IP caps cover those.)
      const origin = req.headers.origin;
      if (origin && !config.allowedOrigins.includes(origin)) return done('origin not allowed', false);
      const ip = ipOf(req);
      lastGuard = ip ? 'on' : 'off';
      if (!ip) return done(null, true);
      if ((ipOpen.get(ip) || 0) >= PER_IP_OPEN) return done('too many connections', false);
      const now = Date.now();
      const recent = (ipRecent.get(ip) || []).filter((t) => t > now - 60_000);
      if (recent.length >= PER_IP_PER_MIN) return done('slow down', false);
      recent.push(now);
      ipRecent.set(ip, recent);
      done(null, true);
    }
  });

  io.on('connection', (socket) => {
    const ip = ipOf(socket.request);
    if (!ip) return;
    ipOpen.set(ip, (ipOpen.get(ip) || 0) + 1);
    socket.on('disconnect', () => {
      const n = (ipOpen.get(ip) || 1) - 1;
      if (n > 0) ipOpen.set(ip, n);
      else ipOpen.delete(ip);
    });
  });

  // ---------- hub: the small API that rooms and pairs use ----------

  const hub = {
    userById: (id) => users.get(id),
    toUser(user, event, payload) {
      if (!user) return;
      if (user.online && user.socket) return void user.socket.emit(event, payload);
      if (NO_BUFFER.test(event)) return;
      user.missed.push([event, payload]);
      if (user.missed.length > 100) user.missed.shift();
    },
    toRoom(roomId, event, payload) {
      const room = rooms.rooms.get(roomId);
      if (!room) return;
      for (const m of room.members.values()) hub.toUser(m.user, event, payload);
    },
    joinSocketRoom() {},
    leaveSocketRoom() {},
    leaveEverything(user, reason) {
      rooms.leave(user, reason === 'switch' ? 'left' : reason);
      pairs.leave(user);
    },
    checkMessage(user, text) {
      if (typeof text !== 'string') return { error: ERRORS.BAD_REQUEST };
      const clean = text.replace(/\s+/g, ' ').trim();
      if (!clean) return { error: ERRORS.EMPTY };
      if (clean.length > L.MSG_MAX) return { error: ERRORS.TOO_LONG, max: L.MSG_MAX };
      const now = Date.now();
      if (now - user.lastMsgAt < L.CHAT_MIN_INTERVAL_MS) return { error: ERRORS.SLOW };
      user.lastMsgAt = now;
      return { text: clean };
    },
    lobbyChanged,
    echoesChanged,
    podsOpen: () => podsOpen(),
  };

  const rooms = new Rooms(hub);
  const pairs = new Pairs(hub);
  const echoes = new Echoes(hub);

  function onlineCount() {
    let n = 0;
    for (const u of users.values()) if (u.online) n++;
    return n;
  }

  function lobbyPayload() {
    const open = podsOpen();
    return {
      channels: rooms.counts(), online: onlineCount(), waiting: pairs.waitingCount(), echoes: echoes.count(),
      listeners: pairs.queue.filter((id) => users.get(id)?.podRole === 'listen').length,
      question: rooms.questionInfo(),
      pods: { open, minsToClose: open ? (podWindowOpen() ? podMinsToClose() : null) : 0 }
    };
  }

  // The wall changed (new note, reply, removal): tell everyone, at most twice a second.
  let echoesTimer = null;
  function echoesChanged() {
    lobbyChanged();
    if (echoesTimer) return;
    echoesTimer = setTimeout(() => {
      echoesTimer = null;
      io.emit('echoes:changed', { count: echoes.count() });
    }, 500);
    echoesTimer.unref?.();
  }

  let lobbyTimer = null;
  function lobbyChanged() {
    if (lobbyTimer) return;
    lobbyTimer = setTimeout(() => {
      lobbyTimer = null;
      io.emit('channels:list', lobbyPayload());
    }, 500);
    lobbyTimer.unref?.();
  }

  function destroyUser(user) {
    clearTimeout(user.graceTimer);
    hub.leaveEverything(user, 'left');
    users.delete(user.id);
    byToken.delete(user.token);
    names.delete(user.name);
    lobbyChanged();
  }

  function sessionState(user, resumed) {
    const r = rooms.get(user);
    const p = pairs.get(user);
    return {
      id: user.id,
      name: user.name,
      resumed,
      room: r.room ? { ...rooms.snapshot(r.room), history: r.room.messages } : null,
      pair: p.pair ? pairs.view(p.pair, user) : null,
      queued: pairs.queue.includes(user.id),
      limits: L
    };
  }

  // ---------- connections ----------

  io.on('connection', (socket) => {
    const auth = socket.handshake.auth || {};
    const token = TOKEN_RE.test(auth.token || '') ? auth.token : randomUUID();

    let user = byToken.get(token);
    let resumed = false;
    if (user) {
      resumed = true;
      clearTimeout(user.graceTimer);
      if (user.socket && user.socket.id !== socket.id) {
        user.socket.emit('session:replaced', {});
        user.socket.disconnect(true);
      }
    } else {
      const wanted = isValidName(auth.name) && !names.has(auth.name) ? auth.name : makeName(names);
      user = {
        id: randomUUID(),
        token,
        name: wanted,
        socket: null,
        online: false,
        roomId: null,
        pairId: null,
        queuedAt: null,
        lastPartnerId: null,
        lastMsgAt: 0,
        lastUsageAt: 0,
        missed: [],
        graceTimer: null,
        requeueOnResume: false,
        bucket: { tokens: 40, max: 40, rate: 20, at: Date.now() },
        rtcBucket: { tokens: 400, max: 400, rate: 100, at: Date.now() }
      };
      users.set(user.id, user);
      byToken.set(token, user);
      names.add(user.name);
    }
    user.socket = socket;
    user.ip = ipOf(socket.request); // null behind a proxy that hides it; echoes then key on the token
    user.online = true;

    socket.emit('session:ready', { ...sessionState(user, resumed), token });
    const missed = user.missed.splice(0);
    for (const [e, p] of missed) socket.emit(e, p);
    if (user.requeueOnResume) {
      user.requeueOnResume = false;
      if (!user.pairId && !pairs.isBlocked(user)) pairs.enqueue(user);
    }
    if (resumed) {
      rooms.presenceChanged(user);
      const { partner } = pairs.get(user);
      if (partner) hub.toUser(partner, 'pair:partnerBack', {});
    }
    socket.emit('channels:list', lobbyPayload());
    lobbyChanged();

    // Every handler goes through here: rate limit, errors never crash the process, acks optional.
    const on = (event, fn) =>
      socket.on(event, (payload, ack) => {
        if (typeof payload === 'function') [payload, ack] = [undefined, payload];
        const reply = typeof ack === 'function' ? ack : () => {};
        if (user.socket !== socket) return;
        // ICE candidates come in bursts across a 10-person mesh, so signaling gets its own, bigger bucket.
        const b = event.includes('tc:') ? user.rtcBucket : user.bucket;
        const now = Date.now();
        b.tokens = Math.min(b.max, b.tokens + ((now - b.at) / 1000) * b.rate);
        b.at = now;
        if (b.tokens < 1) return reply({ error: ERRORS.SLOW });
        b.tokens -= 1;
        try {
          const out = fn(payload ?? {});
          if (out && typeof out.then === 'function') out.then(reply, () => reply({ error: ERRORS.BAD_REQUEST }));
          else reply(out ?? { ok: true });
        } catch (err) {
          console.error(`[${event}]`, err);
          reply({ error: ERRORS.BAD_REQUEST });
        }
      });

    // lobby
    on('channels:request', () => ({ ok: true, ...lobbyPayload(), catalog: CHANNELS }));
    on('ice:request', async () => ({ ok: true, iceServers: await getIceServers() }));
    on('rtc:usage', ({ relayBytes }) => {
      const now = Date.now();
      if (now - user.lastUsageAt < 10_000) return { ok: true };
      user.lastUsageAt = now;
      const n = Number(relayBytes);
      if (Number.isFinite(n) && n > 0) reportRelayBytes(Math.min(n, 100e6));
      return { ok: true };
    });

    // voice rooms
    on('channel:join', ({ id, voice }) => rooms.join(user, id, { voice: Boolean(voice) }));
    on('question:voice', ({ on: v }) => rooms.questionVoice(user, Boolean(v)));
    on('channel:leave', () => (rooms.leave(user, 'left'), { ok: true }));
    on('channel:invite', ({ to }) => rooms.invite(user, to));
    on('channel:acceptInvite', () => rooms.answerInvite(user, true));
    on('channel:declineInvite', () => rooms.answerInvite(user, false));
    on('hand:raise', () => rooms.raiseHand(user));
    on('hand:lower', () => rooms.lowerHand(user));
    on('hand:approve', ({ to }) => rooms.answerHand(user, to, true));
    on('hand:decline', ({ to }) => rooms.answerHand(user, to, false));
    on('stage:demote', ({ to }) => rooms.demote(user, to));
    on('stage:stepDown', () => rooms.stepDown(user));
    on('stage:mute', ({ muted }) => rooms.setMuted(user, muted));
    on('channel:report', ({ to }) => rooms.report(user, to));
    on('chat:send', ({ text }) => rooms.chat(user, text));
    for (const e of ['rtc:offer', 'rtc:answer', 'rtc:ice']) on(e, (p) => (rooms.relay(user, e, p), { ok: true }));

    // 1:1
    on('pair:join', ({ role }) => pairs.join(user, role));
    on('pair:leave', () => pairs.leave(user));
    on('pair:skip', () => pairs.skip(user));
    on('pair:report', ({ requeue }) => pairs.report(user, requeue !== false));
    on('pair:voiceCancel', () => pairs.voiceCancel(user));
    on('pair:message', ({ text }) => pairs.message(user, text));
    on('pair:typing', ({ on: typing }) => (pairs.typing(user, typing), { ok: true }));
    on('pair:voiceRequest', () => pairs.voiceRequest(user));
    on('pair:voiceAccept', () => pairs.voiceAnswer(user, true));
    on('pair:voiceDecline', () => pairs.voiceAnswer(user, false));
    on('pair:voiceEnd', () => pairs.voiceEnd(user));
    for (const e of ['pairRtc:offer', 'pairRtc:answer', 'pairRtc:ice']) on(e, ({ data }) => (pairs.relay(user, e, data), { ok: true }));

    // ECHOES (the wall of voice notes)
    on('echoes:list', () => echoes.list(user));
    on('echoes:thread', (p) => echoes.thread(user, p));
    on('echoes:audio', (p) => echoes.audio(user, p));
    on('echoes:post', (p) => echoes.post(user, p));
    on('echoes:reply', (p) => echoes.reply(user, p));
    on('echoes:report', (p) => echoes.report(user, p));
    on('echoes:delete', (p) => echoes.remove(user, p));
    on('echoes:deleteReply', (p) => echoes.removeReply(user, p));
    on('echoes:heard', (p) => echoes.hear(user, p));
    on('capsule:remind', (p) => capsuleRemind(user, p)); // TIME CAPSULE: schedule one reminder email; nothing kept

    // explicit goodbye (closing the tab cleanly): no grace period
    on('session:end', () => {
      destroyUser(user);
      return { ok: true };
    });

    socket.on('disconnect', () => {
      if (user.socket !== socket) return; // replaced by a newer tab/connection
      user.online = false;
      user.socket = null;
      if (!users.has(user.id)) return;
      if (pairs.queue.includes(user.id)) {
        pairs.leaveQueue(user);
        user.requeueOnResume = true;
      }
      if (!user.roomId && !user.pairId && !user.requeueOnResume) return destroyUser(user);
      // Hold their seat briefly so a flaky connection doesn't cost them the room or the chat.
      rooms.presenceChanged(user);
      const { partner } = pairs.get(user);
      if (partner) hub.toUser(partner, 'pair:partnerAway', {});
      user.graceTimer = setTimeout(() => destroyUser(user), L.RECONNECT_GRACE_MS);
      user.graceTimer.unref?.();
      lobbyChanged();
    });
  });

  // At closing time every live pod ends together (both people see the same "pods are asleep" note).
  let wasOpen = podsOpen();
  const hours = setInterval(() => {
    const open = podsOpen();
    if (wasOpen && !open) {
      pairs.closeAll();
      rooms.closeAll();
    }
    if (wasOpen !== open) lobbyChanged();
    wasOpen = open;
  }, 15_000);
  hours.unref?.();

  return {
    io,
    httpServer,
    state: { users, rooms, pairs, echoes },
    listen(port = config.port) {
      return new Promise((resolve) => httpServer.listen(port, () => resolve(httpServer.address().port)));
    },
    close() {
      echoes.stop();
      pairs.stop();
      clearInterval(hours);
      return new Promise((resolve) => io.close(() => resolve()));
    }
  };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const wisp = createWisp();
  const port = await wisp.listen();
  console.log(`[wisp] signaling on :${port} · origins: ${config.allowedOrigins.join(', ')}`);
  const shutdown = () => wisp.close().then(() => process.exit(0));
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}
