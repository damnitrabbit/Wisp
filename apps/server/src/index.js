import http from 'node:http';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Server } from 'socket.io';
import { CHANNELS, ERRORS } from '@wisp/shared';
import { config } from './config.js';
import { makeName, isValidName } from './names.js';
import { Rooms } from './rooms.js';
import { Pairs } from './pairs.js';
import { getIceServers, reportRelayBytes, turnStatus } from './turn.js';

const L = config.limits;
const TOKEN_RE = /^[A-Za-z0-9_-]{16,128}$/;
// Events that are worthless after a delay are not buffered for reconnecting users.
const NO_BUFFER = /^(rtc:|pairRtc:|pair:typing|channels:list|channel:update)/;

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
      return res.end(JSON.stringify({ online: onlineCount(), rooms: rooms.rooms.size, waiting: pairs.waitingCount(), turn: turnStatus() }));
    }
    res.writeHead(200, { 'content-type': 'text/plain' });
    res.end('wisp signaling. nothing to see here.');
  });

  const io = new Server(httpServer, {
    cors: { origin: config.allowedOrigins, methods: ['GET', 'POST'] },
    pingInterval: 10_000,
    pingTimeout: 8_000,
    maxHttpBufferSize: 64 * 1024
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
  };

  const rooms = new Rooms(hub);
  const pairs = new Pairs(hub);

  function onlineCount() {
    let n = 0;
    for (const u of users.values()) if (u.online) n++;
    return n;
  }

  function lobbyPayload() {
    return { channels: rooms.counts(), online: onlineCount(), waiting: pairs.waitingCount() };
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
    on('channel:join', ({ id }) => rooms.join(user, id));
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
    on('pair:join', () => pairs.join(user));
    on('pair:leave', () => pairs.leave(user));
    on('pair:skip', () => pairs.skip(user));
    on('pair:report', () => pairs.report(user));
    on('pair:message', ({ text }) => pairs.message(user, text));
    on('pair:typing', ({ on: typing }) => (pairs.typing(user, typing), { ok: true }));
    on('pair:voiceRequest', () => pairs.voiceRequest(user));
    on('pair:voiceAccept', () => pairs.voiceAnswer(user, true));
    on('pair:voiceDecline', () => pairs.voiceAnswer(user, false));
    on('pair:voiceEnd', () => pairs.voiceEnd(user));
    for (const e of ['pairRtc:offer', 'pairRtc:answer', 'pairRtc:ice']) on(e, ({ data }) => (pairs.relay(user, e, data), { ok: true }));

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

  return {
    io,
    httpServer,
    state: { users, rooms, pairs },
    listen(port = config.port) {
      return new Promise((resolve) => httpServer.listen(port, () => resolve(httpServer.address().port)));
    },
    close() {
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
