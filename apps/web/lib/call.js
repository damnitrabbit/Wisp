'use client';
// 1:1 voice: one peer connection, started only after both people said yes.
import { useEffect, useRef, useState } from 'react';
import { Peer, play, stop, meter, unmeter, speakingIds, reportRelay } from './rtc';
import { on, send, iceServers } from './wisp';

export function usePairCall({ active, polite, track, muted }) {
  const peer = useRef(null);
  const queue = useRef([]);
  const [speaking, setSpeaking] = useState(() => new Set());
  const [state, setState] = useState('idle'); // idle | connecting | live | failed

  useEffect(() => {
    if (!active) return;
    let dead = false;
    setState('connecting');
    const offs = ['pairRtc:offer', 'pairRtc:answer', 'pairRtc:ice'].map((ev) =>
      on(ev, ({ data }) => (peer.current ? peer.current.handle(data) : queue.current.push(data)))
    );
    (async () => {
      const ice = await iceServers();
      if (dead) return;
      const p = new Peer({
        iceServers: ice,
        initiator: !polite,
        signal: (data) => send(data.sdp ? (data.sdp.type === 'offer' ? 'pairRtc:offer' : 'pairRtc:answer') : 'pairRtc:ice', { data }),
        onStream: (stream) => {
          play('partner', stream);
          meter('partner', stream);
        },
        onDead: () => setState('failed')
      });
      p.pc.addEventListener('connectionstatechange', () => {
        if (p.pc.connectionState === 'connected') setState('live');
      });
      peer.current = p;
      await p.start(track);
      for (const d of queue.current.splice(0)) await p.handle(d);
    })();
    const lvl = setInterval(() => {
      const next = speakingIds();
      setSpeaking((prev) => (prev.size === next.size && [...next].every((x) => prev.has(x)) ? prev : next));
    }, 200);
    const usage = setInterval(() => peer.current && reportRelay([peer.current.pc]), 30_000);
    return () => {
      dead = true;
      offs.forEach((f) => f());
      clearInterval(lvl);
      clearInterval(usage);
      peer.current?.close();
      peer.current = null;
      queue.current = [];
      stop('partner');
      unmeter('partner');
      unmeter('me');
      setState('idle');
    };
  }, [active, polite]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (track) track.enabled = !muted;
    if (active && track && !muted) meter('me', new MediaStream([track]));
    else unmeter('me');
  }, [active, track, muted]);

  return { speaking, state };
}
