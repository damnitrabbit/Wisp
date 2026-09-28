'use client';
// Voice room audio: a small mesh. Everyone on stage is connected to everyone in the room;
// two listeners never connect to each other (neither has anything to send).
import { useEffect, useRef, useState } from 'react';
import { Peer, play, stop, meter, unmeter, speakingIds, reportRelay } from './rtc';
import { on, send, iceServers } from './wisp';

const onStage = (m) => m && m.role !== 'listener';

export function useMesh({ meId, members, track, muted }) {
  const peers = useRef(new Map());
  const [speaking, setSpeaking] = useState(() => new Set());
  const [kick, setKick] = useState(0); // re-run reconcile after a failed peer
  const latest = useRef({ meId, members, track });
  latest.current = { meId, members, track };

  const drop = (id) => {
    peers.current.get(id)?.close();
    peers.current.delete(id);
    stop(id);
    unmeter(id);
  };

  const creating = useRef(new Set());
  const makePeer = async (id, initiator) => {
    creating.current.add(id);
    const ice = await iceServers().finally(() => creating.current.delete(id));
    const cur = latest.current;
    const t = onStage(cur.members.find((m) => m.id === cur.meId)) ? cur.track : null;
    const p = new Peer({
      iceServers: ice,
      initiator,
      signal: (data) => send(data.sdp ? (data.sdp.type === 'offer' ? 'rtc:offer' : 'rtc:answer') : 'rtc:ice', { to: id, data }),
      onStream: (stream) => {
        play(id, stream);
        meter(id, stream);
      },
      onDead: () => {
        if (peers.current.get(id) !== p) return;
        drop(id);
        if (initiator) setTimeout(() => setKick((k) => k + 1), 1500);
      }
    });
    peers.current.set(id, p);
    await p.start(t);
    return p;
  };

  // Keep the set of connections in line with who's in the room and who's on stage.
  useEffect(() => {
    if (!meId) return;
    const me = members.find((m) => m.id === meId);
    const want = new Set(members.filter((m) => m.id !== meId && m.online && (onStage(me) || onStage(m))).map((m) => m.id));
    for (const id of [...peers.current.keys()]) if (!want.has(id)) drop(id);
    for (const id of want) if (!peers.current.has(id) && !creating.current.has(id) && meId < id) makePeer(id, true);
    const out = onStage(me) ? track : null;
    for (const p of peers.current.values()) p.setTrack(out);
  }, [meId, members, track, kick]);

  // Local mic level (for our own speaking bars) and mute.
  useEffect(() => {
    if (track) track.enabled = !muted;
    if (meId && track && !muted) meter(meId, new MediaStream([track]));
    else if (meId) unmeter(meId);
  }, [track, muted, meId]);

  // Offers come from whoever has the lower id; answer them even if our snapshot is a beat behind.
  useEffect(() => {
    const offs = [
      on('rtc:offer', async ({ from, data }) => {
        if (!latest.current.members.some((m) => m.id === from)) return;
        if (peers.current.has(from)) drop(from);
        const p = await makePeer(from, false);
        p.handle(data);
      }),
      on('rtc:answer', ({ from, data }) => peers.current.get(from)?.handle(data)),
      on('rtc:ice', ({ from, data }) => peers.current.get(from)?.handle(data))
    ];
    const lvl = setInterval(() => {
      const next = speakingIds();
      setSpeaking((prev) => (prev.size === next.size && [...next].every((x) => prev.has(x)) ? prev : next));
    }, 200);
    const usage = setInterval(() => reportRelay([...peers.current.values()].map((p) => p.pc)), 30_000);
    return () => {
      offs.forEach((f) => f());
      clearInterval(lvl);
      clearInterval(usage);
      for (const id of [...peers.current.keys()]) drop(id);
      unmeter(latest.current.meId);
    };
  }, []);

  return { speaking };
}
