'use client';
import { useCallback, useRef, useState } from 'react';

let stream = null;

export async function micPermission() {
  try {
    const p = await navigator.permissions.query({ name: 'microphone' });
    return p.state; // granted | denied | prompt
  } catch {
    return 'prompt';
  }
}

export async function openMic() {
  if (stream && stream.getAudioTracks().some((t) => t.readyState === 'live')) return stream;
  stream = await navigator.mediaDevices.getUserMedia({
    audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
  });
  return stream;
}

export function micTrack() {
  return stream?.getAudioTracks().find((t) => t.readyState === 'live') ?? null;
}
export const micStream = () => stream;

export function closeMic() {
  stream?.getTracks().forEach((t) => t.stop());
  stream = null;
}

// Drives the two mic modals from the design: ask first (so the browser prompt isn't a surprise),
// and explain how to unblock if the browser says no.
// ask() resolves true once we have a live mic, false if the person chose to stay without one.
export function useMicFlow() {
  const [modal, setModal] = useState(null); // null | 'ask' | 'blocked'
  const resolver = useRef(null);

  const finish = useCallback((ok) => {
    setModal(null);
    resolver.current?.(ok);
    resolver.current = null;
  }, []);

  const tryOpen = useCallback(async () => {
    try {
      await openMic();
      finish(true);
    } catch {
      setModal('blocked');
    }
  }, [finish]);

  const ask = useCallback(async () => {
    if (micTrack()) return true;
    const perm = await micPermission();
    if (perm === 'granted') {
      try {
        await openMic();
        return true;
      } catch {}
    }
    return new Promise((resolve) => {
      resolver.current = resolve;
      setModal(perm === 'denied' ? 'blocked' : 'ask');
    });
  }, []);

  return { modal, ask, allow: tryOpen, decline: () => finish(false) };
}
