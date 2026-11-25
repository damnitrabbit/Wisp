import { test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, sleep } from './helpers.js';
import { podWindowOpen, podMinsToClose, questionFor, podNight } from '@wisp/shared/pods.js';

let srv;
beforeEach(async () => (srv = await startServer()));
afterEach(() => {
  process.env.PODS_ALWAYS_OPEN = '1';
  return srv.stop();
});

// 22:00 IST = 16:30 UTC; 02:00 IST = 20:30 UTC
const at = (utc) => new Date(`2026-10-03T${utc}:00Z`);

test('pod hours: open 22:00 to 02:00 India time', () => {
  assert.equal(podWindowOpen(at('16:29')), false);
  assert.equal(podWindowOpen(at('16:30')), true);
  assert.equal(podWindowOpen(at('19:00')), true); // 00:30 IST
  assert.equal(podWindowOpen(at('20:29')), true);
  assert.equal(podWindowOpen(at('20:30')), false);
  assert.equal(Math.round(podMinsToClose(at('20:20'))), 10);
  assert.equal(podMinsToClose(at('12:00')), 0);
});

test("tonight's question stays the same across midnight", () => {
  assert.equal(podNight(at('17:00')), podNight(at('19:30')));
  assert.equal(questionFor(at('17:00')), questionFor(at('19:30')));
  assert.equal(typeof questionFor(), 'string');
});

test('outside pod hours, joins are refused', async () => {
  process.env.PODS_ALWAYS_OPEN = '0';
  const a = await srv.connect();
  if (podWindowOpen()) return; // the real clock is inside the window: nothing to assert
  assert.equal((await a.emit('pair:join', { role: 'talk' })).error, 'closed');
  assert.equal((await a.emit('channel:join', { id: 'question' })).error, 'closed');
});

test('a talker is matched with a waiting listener first', async () => {
  const t1 = await srv.connect();
  const l = await srv.connect();
  const t2 = await srv.connect();
  await t1.emit('pair:join', { role: 'talk' });
  await t1.waitFor('pair:waiting');
  await l.emit('pair:join', { role: 'listen' });
  const m = await l.waitFor('pair:matched');
  assert.equal(m.partner.id, t1.session.id);
  assert.equal(m.partner.role, 'talk');
  assert.equal(m.role, 'listen');
  await t2.emit('pair:join', { role: 'talk' });
  await t2.waitFor('pair:waiting');
});

test('two talkers meet each other once nobody listens for a while', async () => {
  const a = await srv.connect();
  const b = await srv.connect();
  await a.emit('pair:join', { role: 'talk' });
  await b.emit('pair:join', { role: 'talk' });
  await sleep(150);
  assert.ok(!a.log.some(([e]) => e === 'pair:matched'), 'not straight away');
  const m = await a.waitFor('pair:matched', () => true, 3000);
  assert.equal(m.partner.id, b.session.id);
});

test('two listeners are never matched', async () => {
  const a = await srv.connect();
  const b = await srv.connect();
  await a.emit('pair:join', { role: 'listen' });
  await b.emit('pair:join', { role: 'listen' });
  await sleep(1200);
  assert.ok(!a.log.some(([e]) => e === 'pair:matched'));
});

test("tonight's question: join with voice or just listen, cap of 8", async () => {
  const a = await srv.connect();
  const b = await srv.connect();
  const ra = await a.emit('channel:join', { id: 'question', voice: true });
  assert.equal(ra.snapshot.members[0].role, 'speaker');
  assert.equal(typeof ra.snapshot.question, 'string');
  const rb = await b.emit('channel:join', { id: 'question' });
  assert.equal(rb.snapshot.members.find((m) => m.id === b.session.id).role, 'listener');
  assert.ok((await b.emit('question:voice', { on: true })).ok);
  const up = await a.waitFor('channel:update', (s) => s.members.length === 2 && s.members.every((m) => m.role === 'speaker'));
  assert.equal(up.members.length, 2);
  for (let i = 0; i < 6; i++) await (await srv.connect()).emit('channel:join', { id: 'question' });
  assert.equal((await (await srv.connect()).emit('channel:join', { id: 'question' })).error, 'full');
});
