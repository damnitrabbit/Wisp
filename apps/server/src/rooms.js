import { CHANNELS, CHANNEL_BY_ID, ROLES, ERRORS } from '@wisp/shared';
import { randomUUID } from 'node:crypto';
import { config } from './config.js';

const L = config.limits;
const { MOD, SPEAKER, LISTENER } = ROLES;

// Reports needed to remove someone. 5 in a busy room, but never more than half of the others,
// so a small room can still act (with a floor of 2 so one person can't remove anyone alone).
export function reportThreshold(roomSize) {
  const others = roomSize - 1;
  return Math.min(L.ROOM_REPORT_MAX, Math.max(2, Math.ceil(others / 2)));
}

export class Rooms {
  constructor(hub) {
    this.hub = hub;
    this.rooms = new Map();
  }

  counts() {
    return CHANNELS.map((c) => ({ id: c.id, count: this.rooms.get(c.id)?.members.size ?? 0 }));
  }

  get(user) {
    const room = user.roomId && this.rooms.get(user.roomId);
    if (!room) return {};
    return { room, member: room.members.get(user.id) };
  }

  // ---------- state out ----------

  snapshot(room) {
    const now = Date.now();
    return {
      id: room.id,
      name: room.name,
      cap: L.ROOM_CAP,
      serverNow: now,
      reportThreshold: reportThreshold(room.members.size),
      members: [...room.members.values()].map((m) => ({
        id: m.user.id,
        name: m.user.name,
        role: m.role,
        founding: room.foundingId === m.user.id,
        online: m.user.online,
        joinedAt: m.joinedAt,
        stageSince: m.stageSince,
        promoteAt: m.role === SPEAKER ? m.promoteAt : null,
        handUp: room.hands.has(m.user.id),
        handExpiresAt: room.hands.get(m.user.id)?.expiresAt ?? null,
        invitedUntil: room.invites.get(m.user.id)?.expiresAt ?? null
      }))
    };
  }

  broadcast(room) {
    this.hub.toRoom(room.id, 'channel:update', this.snapshot(room));
    this.hub.lobbyChanged();
  }

  system(room, text, kind = 'info') {
    const msg = { id: randomUUID(), system: true, kind, text, at: Date.now() };
    this.pushMessage(room, msg);
  }

  pushMessage(room, msg) {
    room.messages.push(msg);
    if (room.messages.length > L.ROOM_HISTORY) room.messages.shift();
    this.hub.toRoom(room.id, 'chat:new', msg);
  }

  // ---------- join / leave ----------

  join(user, channelId) {
    const channel = CHANNEL_BY_ID.get(channelId);
    if (!channel) return { error: ERRORS.NOT_FOUND };
    if (user.roomId === channelId) {
      const room = this.rooms.get(channelId);
      return { snapshot: this.snapshot(room), history: room.messages };
    }
    let room = this.rooms.get(channelId);
    if (room?.banned.has(user.id)) return { error: ERRORS.REMOVED };
    if (room && room.members.size >= L.ROOM_CAP) return { error: ERRORS.FULL };

    this.hub.leaveEverything(user, 'switch');

    if (!room) {
      room = {
        id: channel.id,
        name: channel.name,
        members: new Map(),
        messages: [],
        banned: new Set(),
        reports: new Map(),
        invites: new Map(),
        hands: new Map(),
        handCooldown: new Map(),
        foundingId: null,
        modsGranted: 0
      };
      this.rooms.set(room.id, room);
    }

    const now = Date.now();
    const member = { user, role: LISTENER, joinedAt: now, stageSince: null, promoteAt: null, promoteTimer: null };
    // The first people into an empty room start it, so they get the keys.
    if (room.members.size === 0) {
      room.foundingId = user.id;
      room.modsGranted = 0;
    }
    if (room.modsGranted < L.FIRST_N_MODS && this.modCount(room) < L.FIRST_N_MODS) {
      member.role = MOD;
      member.stageSince = now;
      room.modsGranted++;
    }
    room.members.set(user.id, member);
    user.roomId = room.id;
    this.hub.joinSocketRoom(user, room.id);

    this.system(room, `${user.name} joined`, 'join');
    this.broadcast(room);
    return { snapshot: this.snapshot(room), history: room.messages };
  }

  leave(user, reason = 'left') {
    const { room, member } = this.get(user);
    if (!room) return;
    this.clearMemberTimers(room, member);
    room.members.delete(user.id);
    room.reports.delete(user.id);
    user.roomId = null;
    this.hub.leaveSocketRoom(user, room.id);

    if (room.members.size === 0) {
      // Nothing about an empty room survives: chat, bans and reports all go with it.
      this.rooms.delete(room.id);
      this.hub.lobbyChanged();
      return;
    }
    const text = reason === 'removed' ? `${user.name} was removed after reports` : `${user.name} left`;
    this.system(room, text, reason === 'removed' ? 'removed' : 'leave');
    if (member.role === MOD) this.ensureMods(room);
    this.broadcast(room);
  }

  clearMemberTimers(room, member) {
    if (!member) return;
    clearTimeout(member.promoteTimer);
    const inv = room.invites.get(member.user.id);
    if (inv) clearTimeout(inv.timer);
    room.invites.delete(member.user.id);
    const hand = room.hands.get(member.user.id);
    if (hand) clearTimeout(hand.timer);
    room.hands.delete(member.user.id);
  }

  // ---------- roles ----------

  modCount(room) {
    let n = 0;
    for (const m of room.members.values()) if (m.role === MOD) n++;
    return n;
  }

  promote(room, member, why) {
    clearTimeout(member.promoteTimer);
    member.promoteTimer = null;
    member.promoteAt = null;
    member.role = MOD;
    member.stageSince ??= Date.now();
    this.hub.toRoom(room.id, 'channel:modPromoted', { id: member.user.id, name: member.user.name, why });
    this.system(
      room,
      why === 'time' ? `${member.user.name} is now a mod (on stage long enough)` : `${member.user.name} is now a mod`,
      'mod'
    );
  }

  // Keep the room steerable when mods leave: promote the longest-serving speakers first,
  // and if nobody is on stage at all, hand the keys to whoever has been here longest.
  ensureMods(room) {
    const byStage = (a, b) => a.stageSince - b.stageSince;
    const speakers = [...room.members.values()].filter((m) => m.role === SPEAKER).sort(byStage);
    while (this.modCount(room) < L.MIN_STAGE_MODS && speakers.length) this.promote(room, speakers.shift(), 'succession');
    if (this.modCount(room) === 0) {
      const oldest = [...room.members.values()].sort((a, b) => a.joinedAt - b.joinedAt)[0];
      if (oldest) {
        this.clearMemberTimers(room, oldest);
        this.promote(room, oldest, 'succession');
      }
    }
  }

  toStage(room, member) {
    const now = Date.now();
    this.clearMemberTimers(room, member);
    member.role = SPEAKER;
    member.stageSince = now;
    member.promoteAt = now + L.MOD_PROMOTION_MS;
    member.promoteTimer = setTimeout(() => {
      if (room.members.get(member.user.id) === member && member.role === SPEAKER) {
        this.promote(room, member, 'time');
        this.broadcast(room);
      }
    }, L.MOD_PROMOTION_MS);
    member.promoteTimer.unref?.();
    this.system(room, `${member.user.name} is on stage`, 'stage');
  }

  requireMod(user) {
    const { room, member } = this.get(user);
    if (!room || member.role !== MOD) return { error: ERRORS.NOT_ALLOWED };
    return { room, member };
  }

  target(room, id) {
    return typeof id === 'string' ? room.members.get(id) : undefined;
  }

  // ---------- stage invites (mod → listener) ----------

  invite(user, targetId) {
    const { room, error } = this.requireMod(user);
    if (error) return { error };
    const t = this.target(room, targetId);
    if (!t || t.role !== LISTENER) return { error: ERRORS.BAD_REQUEST };
    if (room.invites.has(t.user.id)) return { ok: true };
    const expiresAt = Date.now() + L.INVITE_EXPIRY_MS;
    const timer = setTimeout(() => {
      if (room.invites.get(t.user.id)?.timer !== timer) return;
      room.invites.delete(t.user.id);
      this.hub.toUser(t.user, 'channel:inviteExpired', {});
      this.hub.toUser(user, 'channel:inviteExpired', { id: t.user.id, name: t.user.name });
      this.broadcast(room);
    }, L.INVITE_EXPIRY_MS);
    timer.unref?.();
    room.invites.set(t.user.id, { by: user.id, expiresAt, timer });
    this.hub.toUser(t.user, 'channel:speakInviteReceived', { from: user.name, expiresAt, serverNow: Date.now() });
    this.broadcast(room);
    return { ok: true };
  }

  answerInvite(user, accept) {
    const { room, member } = this.get(user);
    const inv = room?.invites.get(user.id);
    if (!inv) return { error: ERRORS.BAD_REQUEST };
    clearTimeout(inv.timer);
    room.invites.delete(user.id);
    const inviter = this.hub.userById(inv.by);
    if (accept) {
      this.toStage(room, member);
    } else if (inviter) {
      this.hub.toUser(inviter, 'channel:inviteDeclined', { id: user.id, name: user.name });
    }
    this.broadcast(room);
    return { ok: true };
  }

  // ---------- raise hand (listener → mods) ----------

  raiseHand(user) {
    const { room, member } = this.get(user);
    if (!room || member.role !== LISTENER) return { error: ERRORS.NOT_ALLOWED };
    if (room.hands.has(user.id)) return { ok: true };
    const until = room.handCooldown.get(user.id);
    if (until && until > Date.now()) return { error: ERRORS.COOLDOWN, retryAt: until };
    const expiresAt = Date.now() + L.HAND_EXPIRY_MS;
    const timer = setTimeout(() => {
      if (room.hands.get(user.id)?.timer !== timer) return;
      room.hands.delete(user.id);
      this.hub.toUser(user, 'hand:expired', {});
      this.broadcast(room);
    }, L.HAND_EXPIRY_MS);
    timer.unref?.();
    room.hands.set(user.id, { expiresAt, timer });
    this.broadcast(room);
    return { ok: true, expiresAt };
  }

  lowerHand(user) {
    const { room } = this.get(user);
    const hand = room?.hands.get(user.id);
    if (!hand) return { ok: true };
    clearTimeout(hand.timer);
    room.hands.delete(user.id);
    this.broadcast(room);
    return { ok: true };
  }

  answerHand(user, targetId, approve) {
    const { room, error } = this.requireMod(user);
    if (error) return { error };
    const t = this.target(room, targetId);
    const hand = t && room.hands.get(t.user.id);
    if (!hand) return { error: ERRORS.BAD_REQUEST };
    clearTimeout(hand.timer);
    room.hands.delete(t.user.id);
    if (approve) {
      this.toStage(room, t);
      this.hub.toUser(t.user, 'hand:approved', { by: user.name });
    } else {
      room.handCooldown.set(t.user.id, Date.now() + L.HAND_COOLDOWN_MS);
      this.hub.toUser(t.user, 'hand:declined', { by: user.name, retryAt: Date.now() + L.HAND_COOLDOWN_MS });
    }
    this.broadcast(room);
    return { ok: true };
  }

  // ---------- demote (mod → non-mod speaker only) ----------

  demote(user, targetId) {
    const { room, error } = this.requireMod(user);
    if (error) return { error };
    const t = this.target(room, targetId);
    if (!t || t.role !== SPEAKER) return { error: ERRORS.NOT_ALLOWED };
    clearTimeout(t.promoteTimer);
    t.role = LISTENER;
    t.stageSince = null;
    t.promoteAt = null;
    t.promoteTimer = null;
    this.hub.toUser(t.user, 'stage:demoted', { by: user.name });
    this.system(room, `${t.user.name} moved to listeners`, 'stage');
    this.broadcast(room);
    return { ok: true };
  }

  // Speakers can step down themselves.
  stepDown(user) {
    const { room, member } = this.get(user);
    if (!room || member.role === LISTENER) return { error: ERRORS.BAD_REQUEST };
    const wasMod = member.role === MOD;
    clearTimeout(member.promoteTimer);
    member.role = LISTENER;
    member.stageSince = null;
    member.promoteAt = null;
    this.system(room, `${user.name} moved to listeners`, 'stage');
    if (wasMod) this.ensureMods(room);
    this.broadcast(room);
    return { ok: true };
  }

  // ---------- reports (anyone, against anyone, including mods) ----------

  report(user, targetId) {
    const { room } = this.get(user);
    if (!room) return { error: ERRORS.BAD_REQUEST };
    const t = this.target(room, targetId);
    if (!t || t.user.id === user.id) return { error: ERRORS.BAD_REQUEST };
    let set = room.reports.get(t.user.id);
    if (!set) room.reports.set(t.user.id, (set = new Set()));
    set.add(user.id);
    if (set.size >= reportThreshold(room.members.size)) {
      room.banned.add(t.user.id);
      this.hub.toUser(t.user, 'channel:youWereKicked', { id: room.id, name: room.name });
      this.leave(t.user, 'removed');
    }
    return { ok: true };
  }

  // ---------- chat ----------

  chat(user, text) {
    const { room } = this.get(user);
    if (!room) return { error: ERRORS.BAD_REQUEST };
    const clean = this.hub.checkMessage(user, text);
    if (clean.error) return clean;
    this.pushMessage(room, { id: randomUUID(), from: { id: user.id, name: user.name }, text: clean.text, at: Date.now() });
    return { ok: true };
  }

  // ---------- signaling ----------

  relay(user, event, payload) {
    const { room } = this.get(user);
    const t = room && payload && this.target(room, payload.to);
    if (!t || t.user.id === user.id) return;
    this.hub.toUser(t.user, event, { from: user.id, data: payload.data });
  }

  // ---------- presence ----------

  presenceChanged(user) {
    const { room } = this.get(user);
    if (room) this.broadcast(room);
  }
}
