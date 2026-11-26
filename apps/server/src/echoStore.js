// Durable 24h storage for the echoes wall, so a server restart no longer wipes it.
//
// Write-through: the in-memory Map (see echoes.js) stays the fast, synchronous read path; every change is
// mirrored to Redis with a TTL that matches the note's own 24-hour expiry, and the wall is reloaded from
// Redis once on boot. Nothing is kept past 24 hours (Redis expires it on its own), nothing is written to
// disk by us, nothing is tied to an identity — the same "nothing kept" promise, it just survives a restart.
//
// With no REDIS_URL the whole module is inert (makeEchoStore returns null) and echoes stay purely in memory,
// exactly as before. If Redis is configured but unreachable, writes fail quietly and the wall keeps working
// from memory; it simply won't survive the next restart until Redis is back.
import Redis from 'ioredis';

const NOTE = (id) => `echo:note:${id}`;
const AUDIO = (id) => `echo:audio:${id}`;
const RAUDIO = (id, rid) => `echo:audio:${id}:${rid}`;

// The note without its binary audio (that lives in its own key so a "heard" tap doesn't rewrite the blob),
// with the Sets flattened to arrays so it is plain JSON.
function meta(note) {
  return {
    id: note.id,
    kind: note.kind,
    tag: note.tag,
    to: note.to,
    createdAt: note.createdAt,
    expiresAt: note.expiresAt,
    text: note.text,
    duration: note.duration,
    mime: note.mime,
    ticket: note.ticket,
    listenOnly: note.listenOnly,
    hasAudio: note.audio != null,
    heard: [...note.heard],
    reports: [...note.reports],
    replies: note.replies.map((r) => ({
      id: r.id,
      kind: r.kind,
      text: r.text ?? null,
      mime: r.mime ?? null,
      duration: r.duration ?? 0,
      createdAt: r.createdAt,
      reports: [...r.reports]
    }))
  };
}

const withTimeout = (p, ms, fallback) =>
  Promise.race([p, new Promise((resolve) => setTimeout(() => resolve(fallback), ms))]);

export function makeEchoStore(url, warn = () => {}) {
  if (!url) return null;
  const redis = new Redis(url, {
    maxRetriesPerRequest: 2,
    // keep commands queued across a brief reconnect (so boot-load and a hiccup don't just drop)
    enableOfflineQueue: true,
    retryStrategy: (times) => Math.min(times * 500, 5000)
  });
  let loggedDown = false;
  redis.on('error', (e) => {
    if (!loggedDown) warn(`[echoes] redis unavailable, serving from memory: ${e.message}`);
    loggedDown = true;
  });
  redis.on('ready', () => {
    if (loggedDown) warn('[echoes] redis reconnected');
    loggedDown = false;
  });

  const ttl = (note) => note.expiresAt - Date.now();
  const quiet = (p, where) => Promise.resolve(p).catch((e) => warn(`[echoes] ${where}: ${e.message}`));

  async function saveMeta(note) {
    const px = ttl(note);
    if (px <= 0) return;
    await redis.set(NOTE(note.id), JSON.stringify(meta(note)), 'PX', px);
  }
  async function saveAudio(note) {
    const px = ttl(note);
    if (px <= 0) return;
    const p = redis.pipeline();
    if (note.audio) p.set(AUDIO(note.id), note.audio, 'PX', px);
    for (const r of note.replies) if (r.audio) p.set(RAUDIO(note.id, r.id), r.audio, 'PX', px);
    await p.exec();
  }

  // Boot load in a handful of round trips regardless of wall size (so it stays fast on a remote Redis):
  // SCAN for keys, one MGET for all metadata, one pipeline for all audio blobs.
  async function loadAll() {
    const keys = [];
    let cursor = '0';
    do {
      const [next, batch] = await redis.scan(cursor, 'MATCH', NOTE('*'), 'COUNT', 500);
      cursor = next;
      keys.push(...batch);
    } while (cursor !== '0');
    if (!keys.length) return [];

    const now = Date.now();
    const raws = await redis.mget(keys); // all metadata at once
    const metas = [];
    for (const raw of raws) {
      if (!raw) continue;
      let m;
      try {
        m = JSON.parse(raw);
      } catch {
        continue;
      }
      if (m && m.expiresAt > now) metas.push(m);
    }
    if (!metas.length) return [];

    // every audio blob (note + voice replies) in one pipeline
    const audioKeys = [];
    for (const m of metas) {
      if (m.hasAudio) audioKeys.push(AUDIO(m.id));
      for (const r of m.replies || []) if (r.kind === 'voice') audioKeys.push(RAUDIO(m.id, r.id));
    }
    const blobs = new Map();
    if (audioKeys.length) {
      const pipe = redis.pipeline();
      for (const k of audioKeys) pipe.getBuffer(k);
      const res = await pipe.exec();
      (res || []).forEach(([err, buf], i) => {
        if (!err && buf) blobs.set(audioKeys[i], buf);
      });
    }

    const out = metas.map((m) => ({
      id: m.id,
      kind: m.kind,
      tag: m.tag,
      to: m.to,
      createdAt: m.createdAt,
      expiresAt: m.expiresAt,
      text: m.text ?? null,
      duration: m.duration,
      mime: m.mime ?? null,
      audio: m.hasAudio ? (blobs.get(AUDIO(m.id)) ?? null) : null,
      ticket: m.ticket,
      listenOnly: m.listenOnly,
      replies: (m.replies || []).map((r) => ({
        id: r.id,
        kind: r.kind,
        text: r.kind === 'text' ? (r.text ?? '') : undefined,
        mime: r.kind === 'voice' ? (r.mime ?? undefined) : undefined,
        duration: r.duration,
        audio: r.kind === 'voice' ? (blobs.get(RAUDIO(m.id, r.id)) ?? undefined) : undefined,
        createdAt: r.createdAt,
        reports: new Set(r.reports || [])
      })),
      heard: new Set(m.heard || []),
      reports: new Set(m.reports || [])
    }));
    // oldest first: the Map relies on insertion order for "oldest drops off" and newest-first display
    out.sort((a, b) => a.createdAt - b.createdAt);
    return out;
  }

  return {
    // post, or a voice reply: metadata plus the binary blob(s). Other changes ("heard", a text reply,
    // a report, a removed reply) only rewrite the small metadata key.
    save(note, withAudio = false) {
      return quiet(withAudio ? Promise.all([saveMeta(note), saveAudio(note)]) : saveMeta(note), `save ${note.id}`);
    },
    remove(note) {
      const keys = [NOTE(note.id), AUDIO(note.id), ...note.replies.filter((r) => r.audio).map((r) => RAUDIO(note.id, r.id))];
      return quiet(redis.del(...keys), `remove ${note.id}`);
    },
    // eviction when the wall is full: only the id is to hand, so clear what we can (audio keys expire on TTL)
    removeId(id) {
      return quiet(redis.del(NOTE(id), AUDIO(id)), `evict ${id}`);
    },
    // boot: hand back every live note, oldest first; never hang the server if Redis is slow/unreachable
    load() {
      return withTimeout(
        loadAll().catch((e) => {
          warn(`[echoes] load from redis failed, starting empty: ${e.message}`);
          return [];
        }),
        8000,
        []
      );
    },
    close() {
      return redis.quit().catch(() => {});
    }
  };
}
