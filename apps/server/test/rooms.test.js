import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, sleep, member } from './helpers.js';

let srv;
before(async () => (srv = await startServer()));
after(() => srv.stop());

const ROOM = 'late-night-confessions';
let roomN = 0;
const rooms = ['night-owls', 'debate-arena', 'rant-room', 'deep-questions', 'gaming-lounge', 'just-vent', 'movie-buffs', 'career-talk', 'book-club', 'study-hall', 'travel-tales', 'poetry-and-prose', 'true-crime'];
const freshRoom = () => rooms[roomN++];

async function fill(id, n) {
  const cs = [];
  for (let i = 0; i < n; i++) {
    const c = await srv.connect();
    const r = await c.emit('channel:join', { id });
    assert.ok(r.snapshot, `join ${i} failed: ${JSON.stringify(r)}`);
    cs.push(c);
  }
  return cs;
}

test('session gives a quiet_otter_42 style name, and keeps a remembered one', async () => {
  const a = await srv.connect();
  assert.match(a.session.name, /^[a-z]+_[a-z]+_\d{2}$/);
  const b = await srv.connect({ name: 'quiet_otter_42' });
  assert.equal(b.session.name, 'quiet_otter_42');
  const c = await srv.connect({ name: 'rude_word_99' });
  assert.notEqual(c.session.name, 'rude_word_99', 'names outside our word lists are refused');
});

test('unknown channel is not_found', async () => {
  const a = await srv.connect();
  assert.deepEqual(await a.emit('channel:join', { id: 'nope' }), { error: 'not_found' });
});

test('first two in are mods (first is founding), the rest listeners; room caps at 10', async () => {
  const cs = await fill(ROOM, 10);
  const snap = (await cs[0].emit('channel:join', { id: ROOM })).snapshot;
  const [a, b, c] = cs.map((x) => member(snap, x.session.id));
  assert.equal(a.role, 'mod');
  assert.equal(a.founding, true);
  assert.equal(b.role, 'mod');
  assert.equal(b.founding, false);
  assert.equal(c.role, 'listener');
  const late = await srv.connect();
  assert.deepEqual(await late.emit('channel:join', { id: ROOM }), { error: 'full' });
});

test('raise hand: mods see it, approve brings the listener on stage', async () => {
  const [mod, , listener] = await fill(freshRoom(), 3);
  const r = await listener.emit('hand:raise');
  assert.ok(r.ok && r.expiresAt);
  const up = await mod.waitFor('channel:update', (s) => member(s, listener.session.id)?.handUp);
  assert.ok(up);
  assert.deepEqual(await mod.emit('hand:approve', { to: listener.session.id }), { ok: true });
  await listener.waitFor('hand:approved');
  const s = await mod.waitFor('channel:update', (s) => member(s, listener.session.id)?.role === 'speaker');
  assert.ok(member(s, listener.session.id).promoteAt > Date.now() - 1000);
});

test('only mods can answer hands; declined hand has a cooldown; unanswered hand expires', async () => {
  const [mod, , l1, l2] = await fill(freshRoom(), 4);
  await l1.emit('hand:raise');
  assert.deepEqual(await l2.emit('hand:approve', { to: l1.session.id }), { error: 'not_allowed' });
  await mod.emit('hand:decline', { to: l1.session.id });
  await l1.waitFor('hand:declined');
  assert.equal((await l1.emit('hand:raise')).error, 'cooldown');
  await sleep(350);
  assert.ok((await l1.emit('hand:raise')).ok);
  await l1.waitFor('hand:expired', () => true, 1000);
});

test('stage invite: accept, decline and 30s-style expiry', async () => {
  const [mod, , a, b, c] = await fill(freshRoom(), 5);
  await mod.emit('channel:invite', { to: a.session.id });
  await a.waitFor('channel:speakInviteReceived');
  await a.emit('channel:acceptInvite');
  await mod.waitFor('channel:update', (s) => member(s, a.session.id)?.role === 'speaker');

  await mod.emit('channel:invite', { to: b.session.id });
  await b.waitFor('channel:speakInviteReceived');
  await b.emit('channel:declineInvite');
  await mod.waitFor('channel:inviteDeclined', (p) => p.id === b.session.id);

  await mod.emit('channel:invite', { to: c.session.id });
  await c.waitFor('channel:inviteExpired', () => true, 1000);
  await mod.waitFor('channel:inviteExpired', (p) => p.id === c.session.id);
});

test('demote: speakers can be moved down and are told; mods cannot be', async () => {
  const [mod, mod2, a] = await fill(freshRoom(), 3);
  await mod.emit('channel:invite', { to: a.session.id });
  await a.waitFor('channel:speakInviteReceived');
  await a.emit('channel:acceptInvite');
  assert.deepEqual(await mod.emit('stage:demote', { to: a.session.id }), { ok: true });
  const n = await a.waitFor('stage:demoted');
  assert.equal(n.by, mod.session.name);
  assert.deepEqual(await mod.emit('stage:demote', { to: mod2.session.id }), { error: 'not_allowed' });
});

test('speaker becomes a mod after staying on stage long enough', async () => {
  const [mod, , a] = await fill(freshRoom(), 3);
  await mod.emit('channel:invite', { to: a.session.id });
  await a.waitFor('channel:speakInviteReceived');
  await a.emit('channel:acceptInvite');
  const p = await mod.waitFor('channel:modPromoted', (p) => p.id === a.session.id, 1500);
  assert.equal(p.why, 'time');
  // and now nobody can demote them
  assert.deepEqual(await mod.emit('stage:demote', { to: a.session.id }), { error: 'not_allowed' });
});

test('succession: when a mod leaves, the longest-serving speaker becomes a mod', async () => {
  const [m1, , s1, s2] = await fill(freshRoom(), 4);
  for (const s of [s1, s2]) {
    await m1.emit('channel:invite', { to: s.session.id });
    await s.waitFor('channel:speakInviteReceived');
    await s.emit('channel:acceptInvite');
    await sleep(20);
  }
  await m1.emit('channel:leave');
  const p = await s1.waitFor('channel:modPromoted');
  assert.equal(p.id, s1.session.id);
  assert.equal(p.why, 'succession');
});

test('reports remove anyone, mods included, and they cannot come back', async () => {
  const id = freshRoom();
  const [mod, ...others] = await fill(id, 6); // 6 in room -> threshold min(5, max(2, ceil(5/2)=3)) = 3
  for (const o of others.slice(0, 3)) await o.emit('channel:report', { to: mod.session.id });
  const k = await mod.waitFor('channel:youWereKicked');
  assert.equal(k.id, id);
  assert.deepEqual(await mod.emit('channel:join', { id }), { error: 'removed' });
});

test('chat: slow down, too long, empty', async () => {
  const [a] = await fill(freshRoom(), 1);
  assert.deepEqual(await a.emit('chat:send', { text: 'hi' }), { ok: true });
  assert.equal((await a.emit('chat:send', { text: 'again' })).error, 'slow');
  await sleep(60);
  assert.equal((await a.emit('chat:send', { text: 'x'.repeat(501) })).error, 'too_long');
  assert.equal((await a.emit('chat:send', { text: '   ' })).error, 'empty');
});

test('reconnect within grace keeps your seat and role; after grace you are gone', async () => {
  const id = freshRoom();
  const [mod, other] = await fill(id, 2);
  mod.close();
  const away = await other.waitFor('channel:update', (s) => member(s, mod.session.id)?.online === false);
  assert.ok(away);
  const back = await srv.connect({ token: mod.token });
  assert.equal(back.session.resumed, true);
  assert.equal(back.session.name, mod.session.name);
  assert.equal(member(back.session.room, mod.session.id).role, 'mod');

  back.close();
  await sleep(600);
  const again = await srv.connect({ token: mod.token });
  assert.equal(again.session.resumed, false);
  assert.equal(again.session.room, null);
});

test('rtc signaling only reaches people in the same room', async () => {
  const [a, b] = await fill(freshRoom(), 2);
  const [x] = await fill(freshRoom(), 1);
  await a.emit('rtc:offer', { to: b.session.id, data: { sdp: 'o' } });
  const got = await b.waitFor('rtc:offer');
  assert.equal(got.from, a.session.id);
  await x.emit('rtc:offer', { to: b.session.id, data: { sdp: 'evil' } });
  await sleep(100);
  assert.equal(b.log.filter(([e]) => e === 'rtc:offer').length, 1);
});

test('a mod who steps down alone is not handed the keys back; the next person in gets them', async () => {
  const id = 'music-production';
  const a = await srv.connect();
  await a.emit('channel:join', { id });
  assert.deepEqual(await a.emit('stage:stepDown'), { ok: true });
  const s1 = await a.waitFor('channel:update', (s) => member(s, a.session.id)?.role === 'listener');
  assert.ok(s1);
  const b = await srv.connect();
  const r = await b.emit('channel:join', { id });
  assert.equal(member(r.snapshot, b.session.id).role, 'mod');
  assert.equal(member(r.snapshot, a.session.id).role, 'listener');
});
