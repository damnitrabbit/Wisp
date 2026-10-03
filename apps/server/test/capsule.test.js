import { test } from 'node:test';
import assert from 'node:assert/strict';
import { makeCapsuleRemind, isEmail, MAX_AHEAD_MS } from '../src/capsule.js';
import { startServer } from './helpers.js';

const NOW = Date.parse('2026-10-03T10:00:00Z');
const user = { token: 'tok-aaaaaaaaaaaaaaaa' };
const inDays = (d) => new Date(NOW + d * 86400_000).toISOString();

function fakeFetch(status = 200) {
  const calls = [];
  const f = async (url, init) => {
    calls.push({ url, init, body: JSON.parse(init.body) });
    return { ok: status >= 200 && status < 300, status, json: async () => ({ id: 'x' }) };
  };
  f.calls = calls;
  return f;
}

test('schedules one Resend email at the opening time, without the letter', async () => {
  const f = fakeFetch();
  const remind = makeCapsuleRemind({ fetchImpl: f, env: { RESEND_API_KEY: 're_test' }, now: () => NOW });
  const r = await remind(user, { email: 'sam@example.com', openAt: inDays(7), text: 'my secret letter' });
  assert.equal(r.ok, true);
  assert.equal(f.calls.length, 1);
  const { url, init, body } = f.calls[0];
  assert.equal(url, 'https://api.resend.com/emails');
  assert.equal(init.headers.authorization, 'Bearer re_test');
  assert.deepEqual(body.to, ['sam@example.com']);
  assert.equal(body.from, 'N0TRACE <letters@notrace.chat>');
  assert.equal(body.subject, 'a letter from you arrived');
  assert.equal(body.scheduled_at, inDays(7));
  assert.match(body.text, /notrace\.chat\/capsule\/open/);
  assert.match(body.text, /same browser/);
  assert.ok(!JSON.stringify(body).includes('secret'), 'the letter never goes into the email');
});

test('RESEND_FROM overrides the sender', async () => {
  const f = fakeFetch();
  const remind = makeCapsuleRemind({ fetchImpl: f, env: { RESEND_API_KEY: 'k', RESEND_FROM: 'X <x@y.z>' }, now: () => NOW });
  await remind(user, { email: 'a@b.co', openAt: inDays(1) });
  assert.equal(f.calls[0].body.from, 'X <x@y.z>');
});

test('refuses bad addresses, past dates and anything past the 30-day window', async () => {
  const f = fakeFetch();
  const remind = makeCapsuleRemind({ fetchImpl: f, env: { RESEND_API_KEY: 'k' }, now: () => NOW, perHour: 100 });
  assert.equal((await remind(user, { email: 'sam@gmial', openAt: inDays(7) })).error, 'bad_request');
  assert.equal((await remind(user, { email: 'not an email', openAt: inDays(7) })).error, 'bad_request');
  assert.equal((await remind(user, { email: 'a@b.co', openAt: inDays(-1) })).error, 'bad_request');
  assert.equal((await remind(user, { email: 'a@b.co', openAt: 'soon' })).error, 'bad_request');
  assert.equal((await remind(user, { email: 'a@b.co', openAt: inDays(31) })).error, 'too_long');
  assert.equal((await remind(user, { email: 'a@b.co', openAt: new Date(NOW + MAX_AHEAD_MS).toISOString() })).ok, true);
  assert.equal(f.calls.length, 1);
  assert.ok(isEmail('first.last+tag@sub.example.org'));
});

test('rate limited per session, and a missing key or a Resend error is a soft "unavailable"', async () => {
  const f = fakeFetch();
  const remind = makeCapsuleRemind({ fetchImpl: f, env: { RESEND_API_KEY: 'k' }, now: () => NOW, perHour: 2 });
  assert.ok((await remind(user, { email: 'a@b.co', openAt: inDays(2) })).ok);
  assert.ok((await remind(user, { email: 'a@b.co', openAt: inDays(2) })).ok);
  assert.equal((await remind(user, { email: 'a@b.co', openAt: inDays(2) })).error, 'slow');
  assert.ok((await remind({ token: 'someone-else-xxxxxx' }, { email: 'a@b.co', openAt: inDays(2) })).ok);

  const noKey = makeCapsuleRemind({ fetchImpl: f, env: {}, now: () => NOW });
  assert.equal((await noKey(user, { email: 'a@b.co', openAt: inDays(2) })).error, 'unavailable');
  const down = makeCapsuleRemind({ fetchImpl: fakeFetch(500), env: { RESEND_API_KEY: 'k' }, now: () => NOW });
  assert.equal((await down(user, { email: 'a@b.co', openAt: inDays(2) })).error, 'unavailable');
  const offline = makeCapsuleRemind({ fetchImpl: async () => { throw new Error('net'); }, env: { RESEND_API_KEY: 'k' }, now: () => NOW });
  assert.equal((await offline(user, { email: 'a@b.co', openAt: inDays(2) })).error, 'unavailable');
});

test('capsule:remind over the socket acks (no key in tests: unavailable)', async () => {
  const saved = process.env.RESEND_API_KEY;
  delete process.env.RESEND_API_KEY;
  const s = await startServer();
  try {
    const a = await s.connect();
    const bad = await a.emit('capsule:remind', { email: 'nope', openAt: new Date(Date.now() + 86400_000).toISOString() });
    assert.equal(bad.error, 'bad_request');
    const r = await a.emit('capsule:remind', { email: 'a@b.co', openAt: new Date(Date.now() + 86400_000).toISOString() });
    assert.equal(r.error, 'unavailable');
  } finally {
    if (saved !== undefined) process.env.RESEND_API_KEY = saved;
    await s.stop();
  }
});
