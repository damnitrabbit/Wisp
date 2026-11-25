import { test, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, sleep } from './helpers.js';

// Fresh server per test so the queue starts empty.
let srv;
beforeEach(async () => (srv = await startServer()));
afterEach(() => srv.stop());

async function matched() {
  const a = await srv.connect();
  const b = await srv.connect();
  assert.ok((await a.emit('pair:join')).waiting);
  await a.waitFor('pair:waiting');
  await b.emit('pair:join');
  const ma = await a.waitFor('pair:matched');
  const mb = await b.waitFor('pair:matched');
  assert.equal(ma.partner.id, b.session.id);
  assert.equal(mb.partner.id, a.session.id);
  return [a, b];
}

test('longest waiting gets matched first', async () => {
  const a = await srv.connect();
  const b = await srv.connect();
  const c = await srv.connect();
  await a.emit('pair:join');
  await sleep(10);
  await b.emit('pair:join');
  await c.emit('pair:join');
  // a and b match each other (a was waiting), c waits
  assert.equal((await a.waitFor('pair:matched')).partner.id, b.session.id);
  await c.waitFor('pair:waiting');
});

test('messages flow both ways, with the same limits as rooms', async () => {
  const [a, b] = await matched();
  assert.ok((await a.emit('pair:message', { text: 'hey :) chatting from pune. you?' })).ok);
  assert.equal((await b.waitFor('pair:message')).text, 'hey :) chatting from pune. you?');
  assert.equal((await a.emit('pair:message', { text: 'x'.repeat(501) })).error, 'too_long');
});

test('skip: both go back in line, and are not rematched with each other', async () => {
  const [a, b] = await matched();
  await a.emit('pair:skip');
  const left = await b.waitFor('pair:partnerLeft');
  assert.equal(left.reason, 'skip');
  await a.waitFor('pair:waiting');
  await b.waitFor('pair:waiting');
  const c = await srv.connect();
  await c.emit('pair:join');
  const mc = await c.waitFor('pair:matched');
  assert.ok([a.session.id, b.session.id].includes(mc.partner.id));
});

test('voice needs both sides: request, accept, end', async () => {
  const [a, b] = await matched();
  assert.ok((await a.emit('pair:voiceRequest')).ok);
  await b.waitFor('pair:voiceRequested');
  assert.equal((await a.emit('pair:voiceAccept')).error, 'bad_request', 'requester cannot accept their own request');
  await b.emit('pair:voiceAccept');
  assert.equal((await a.waitFor('pair:voiceStarted')).polite, false);
  assert.equal((await b.waitFor('pair:voiceStarted')).polite, true);
  await a.emit('pairRtc:offer', { data: { sdp: 'x' } });
  await b.waitFor('pairRtc:offer');
  await b.emit('pair:voiceEnd');
  await a.waitFor('pair:voiceEnded');
});

test('voice request can be declined or expire', async () => {
  const [a, b] = await matched();
  await a.emit('pair:voiceRequest');
  await b.waitFor('pair:voiceRequested');
  await b.emit('pair:voiceDecline');
  assert.equal((await a.waitFor('pair:voiceDeclined')).reason, 'declined');
  await a.emit('pair:voiceRequest');
  assert.equal((await a.waitFor('pair:voiceDeclined', () => true, 1000)).reason, 'expired');
});

test('three reports remove someone from matchmaking', async () => {
  const bad = await srv.connect();
  for (let i = 0; i < 3; i++) {
    const r = await srv.connect();
    await bad.emit('pair:join');
    await r.emit('pair:join');
    await r.waitFor('pair:matched');
    await r.emit('pair:report');
    await r.emit('pair:leave');
    if (i < 2) await bad.emit('pair:leave');
  }
  await bad.waitFor('pair:blocked');
  assert.equal((await bad.emit('pair:join')).error, 'blocked');
});

test('a dropped connection keeps the chat for the grace period and delivers missed messages', async () => {
  const [a, b] = await matched();
  b.close();
  await a.waitFor('pair:partnerAway');
  await a.emit('pair:message', { text: 'you there?' });
  const back = await srv.connect({ token: b.token });
  assert.equal(back.session.pair.partner.id, a.session.id);
  assert.equal((await back.waitFor('pair:message')).text, 'you there?');
  await a.waitFor('pair:partnerBack');
});

test('if the partner never comes back, you are told and put back in line', async () => {
  const [a, b] = await matched();
  b.close();
  const left = await a.waitFor('pair:partnerLeft', () => true, 1500);
  assert.equal(left.reason, 'left');
  await a.waitFor('pair:waiting');
});

test('wind-down: both land on the notes screen, and the one left behind is not re-queued', async () => {
  const [a, b] = await matched();
  assert.ok((await a.emit('pair:wrap')).ok);
  assert.equal((await a.waitFor('pair:wrap')).by, 'you');
  assert.equal((await b.waitFor('pair:wrap')).by, a.session.name);
  // a leaves for good; b is on the notes screen and should NOT be thrown back in line
  await a.emit('pair:leave');
  assert.equal((await b.waitFor('pair:partnerLeft')).reason, 'wrapped');
  await assert.rejects(b.waitFor('pair:waiting', () => true, 500));
});

test('a parting note crosses once, trimmed and capped, and is kept nowhere', async () => {
  const [a, b] = await matched();
  await a.emit('pair:wrap');
  await b.waitFor('pair:wrap');
  assert.ok((await a.emit('pair:note', { text: '  thanks for\n  staying   ' })).ok);
  const got = await b.waitFor('pair:note');
  assert.equal(got.text, 'thanks for staying');
  assert.equal(got.name, a.session.name);
  // capped at PAIR_NOTE_MAX (140)
  await b.emit('pair:note', { text: 'y'.repeat(300) });
  assert.equal((await a.waitFor('pair:note')).text.length, 140);
  // empty / whitespace-only is refused
  assert.equal((await a.emit('pair:note', { text: '   ' })).error, 'empty');
});

test('a note after the partner has gone just does not land', async () => {
  const [a, b] = await matched();
  await a.emit('pair:wrap');
  await b.waitFor('pair:wrap');
  await b.emit('pair:leave');
  await a.waitFor('pair:partnerLeft');
  assert.equal((await a.emit('pair:note', { text: 'you there?' })).error, 'bad_request');
});
