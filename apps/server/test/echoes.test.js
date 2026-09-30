import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, sleep } from './helpers.js';

const MIME = 'audio/webm;codecs=opus';
const clip = (n = 2000) => Buffer.alloc(n, 7);
const ticket = (n = 0) => `ticket-${n}-abcdefghijklmnop`;
const note = (extra = {}) => ({ audio: clip(), mime: MIME, duration: 4.2, tag: 'rant', ticket: ticket(), ...extra });

test('a posted note shows up on everyone\'s wall, plays back byte for byte, and announces itself', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const b = await s.connect();
    const posted = await a.emit('echoes:post', note({ audio: Buffer.from('hello-voice-bytes') }));
    assert.ok(posted.ok && posted.id);
    await b.waitFor('echoes:changed', (p) => p.count === 1);
    const list = await b.emit('echoes:list');
    assert.equal(list.notes.length, 1);
    const n = list.notes[0];
    assert.equal(n.tag, 'rant');
    assert.equal(n.replyCount, 0);
    assert.equal(n.listenOnly, false);
    assert.ok(n.expiresAt > Date.now());
    assert.equal(n.ticket, undefined, 'the owner ticket never leaves the server');
    const audio = await b.emit('echoes:audio', { id: n.id });
    assert.equal(Buffer.from(audio.audio).toString(), 'hello-voice-bytes');
    assert.equal(audio.mime, MIME);
  } finally {
    await s.stop();
  }
});

test('bad posts are refused: tag, ticket, empty, too big, too long', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    assert.equal((await a.emit('echoes:post', note({ tag: 'nope' }))).error, 'bad_request');
    assert.equal((await a.emit('echoes:post', note({ ticket: 'short' }))).error, 'bad_request');
    assert.equal((await a.emit('echoes:post', note({ audio: Buffer.alloc(0) }))).error, 'empty');
    assert.equal((await a.emit('echoes:post', note({ audio: clip(410_000) }))).error, 'too_long');
    assert.equal((await a.emit('echoes:post', note({ duration: 45 }))).error, 'too_long');
    assert.equal((await a.emit('echoes:post', note({ mime: 'text/html' }))).error, 'bad_request');
    assert.equal((await a.emit('echoes:list')).notes.length, 0);
  } finally {
    await s.stop();
  }
});

test('one note per session per cooldown, and one network can\'t flood the wall', async () => {
  const s = await startServer();
  try {
    const a = await s.connect({ ip: '10.9.9.9' });
    assert.ok((await a.emit('echoes:post', note())).ok);
    const again = await a.emit('echoes:post', note());
    assert.equal(again.error, 'cooldown');
    assert.ok(again.retryInMs > 0);
    // Someone else on the same network (a shared carrier IP) is not blocked by a's cooldown...
    const b = await s.connect({ ip: '10.9.9.9' });
    const c = await s.connect({ ip: '10.9.9.9' });
    assert.ok((await b.emit('echoes:post', note())).ok);
    assert.ok((await c.emit('echoes:post', note())).ok);
    // ...but a network gets ECHO_IP_POSTS per window (3 in tests), however many tabs it opens.
    const d = await s.connect({ ip: '10.9.9.9' });
    assert.equal((await d.emit('echoes:post', note())).error, 'cooldown');
    const elsewhere = await s.connect({ ip: '10.9.9.10' });
    assert.ok((await elsewhere.emit('echoes:post', note())).ok);
    await sleep(350);
    assert.ok((await a.emit('echoes:post', note())).ok);
  } finally {
    await s.stop();
  }
});

test('reports count one per network, so extra tabs don\'t add up', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note());
    for (let i = 0; i < 3; i++) await (await s.connect({ ip: '10.7.7.7' })).emit('echoes:report', { id });
    assert.equal((await a.emit('echoes:list')).notes.length, 1);
  } finally {
    await s.stop();
  }
});

test('replies by voice or text build a thread, capped at ten', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note());
    const b = await s.connect();
    assert.ok((await b.emit('echoes:reply', { id, text: '  you are  not alone  ' })).ok);
    await sleep(120);
    const voice = await b.emit('echoes:reply', { id, audio: Buffer.from('reply-bytes'), mime: MIME, duration: 3 });
    assert.ok(voice.ok);
    const t = await a.emit('echoes:thread', { id });
    assert.equal(t.replies.length, 2);
    assert.equal(t.replies[0].kind, 'text');
    assert.equal(t.replies[0].text, 'you are not alone');
    assert.equal(t.replies[1].kind, 'voice');
    const audio = await a.emit('echoes:audio', { id, replyId: voice.id });
    assert.equal(Buffer.from(audio.audio).toString(), 'reply-bytes');
    assert.equal((await b.emit('echoes:reply', { id, text: 'x'.repeat(281) })).error, 'too_long');
    for (let i = 0; i < 8; i++) {
      const c = await s.connect();
      assert.ok((await c.emit('echoes:reply', { id, text: `reply ${i}` })).ok);
    }
    const late = await s.connect();
    assert.equal((await late.emit('echoes:reply', { id, text: 'one too many' })).error, 'full');
  } finally {
    await s.stop();
  }
});

test('a "just listen" note can be played but not answered', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note({ listenOnly: true }));
    const b = await s.connect();
    assert.equal((await b.emit('echoes:reply', { id, text: 'advice!' })).error, 'not_allowed');
    assert.equal((await b.emit('echoes:thread', { id })).note.listenOnly, true);
    assert.ok((await b.emit('echoes:audio', { id })).audio);
  } finally {
    await s.stop();
  }
});

test('three different people reporting takes a note down; one person counts once', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note());
    const [b, c, d] = [await s.connect(), await s.connect(), await s.connect()];
    assert.equal((await b.emit('echoes:report', { id })).removed, false);
    assert.equal((await b.emit('echoes:report', { id })).already, true);
    assert.equal((await c.emit('echoes:report', { id })).removed, false);
    assert.equal((await b.emit('echoes:list')).notes[0].reported, true);
    assert.equal((await d.emit('echoes:report', { id })).removed, true);
    assert.equal((await a.emit('echoes:list')).notes.length, 0);
    assert.equal((await a.emit('echoes:audio', { id })).error, 'not_found');
  } finally {
    await s.stop();
  }
});

test('reports take down a single reply without touching the note', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note());
    const troll = await s.connect();
    const { id: replyId } = await troll.emit('echoes:reply', { id, text: 'something cruel' });
    for (let i = 0; i < 3; i++) await (await s.connect()).emit('echoes:report', { id, replyId });
    const t = await a.emit('echoes:thread', { id });
    assert.equal(t.replies.length, 0);
    assert.equal(t.note.id, id);
  } finally {
    await s.stop();
  }
});

test('only the poster (holding the ticket) can delete the note or a reply on it', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note({ ticket: ticket(1) }));
    const b = await s.connect();
    const { id: replyId } = await b.emit('echoes:reply', { id, text: 'hmm' });
    assert.equal((await b.emit('echoes:deleteReply', { id, replyId, ticket: ticket(2) })).error, 'not_allowed');
    assert.ok((await a.emit('echoes:deleteReply', { id, replyId, ticket: ticket(1) })).ok);
    assert.equal((await a.emit('echoes:thread', { id })).replies.length, 0);
    assert.equal((await b.emit('echoes:delete', { id, ticket: ticket(2) })).error, 'not_allowed');
    // The ticket works from any tab or device that holds it: it's the only proof of authorship.
    const a2 = await s.connect();
    assert.ok((await a2.emit('echoes:delete', { id, ticket: ticket(1) })).ok);
    assert.equal((await a.emit('echoes:list')).notes.length, 0);
  } finally {
    await s.stop();
  }
});

test('notes and their replies are gone after the time limit', async () => {
  const s = await startServer();
  try {
    const a = await s.connect();
    const { id } = await a.emit('echoes:post', note());
    await (await s.connect()).emit('echoes:reply', { id, text: 'still here?' });
    assert.equal((await a.emit('echoes:list')).notes.length, 1);
    await sleep(4100); // ECHO_TTL_MS is 4s in tests (24h live)
    assert.equal((await a.emit('echoes:list')).notes.length, 0);
    assert.equal((await a.emit('echoes:thread', { id })).error, 'not_found');
    assert.equal(s.wisp.state.echoes.count(), 0);
  } finally {
    await s.stop();
  }
});
