'use client';
// BURN, browser side. Nothing here ever leaves the tab: the words live in a ref, the voice note in a Blob URL,
// and both are dropped the moment the note burns (or the page closes). No storage, no network.
import { useCallback, useEffect, useRef, useState } from 'react';

export const HOLD_MS = 1600; // press-and-hold on the match
export const VOICE_MAX_S = 120; // "up to 2 minutes"

export const clock = (s) => {
  const t = Math.max(0, Math.floor(s || 0));
  return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, '0')}`;
};

// Press-and-hold that works with mouse, touch and keyboard (Space / Enter), and ignores the
// emulated mouse events a phone fires right after a touch.
export function useHold(onDone, ms = HOLD_MS) {
  const [holding, setHolding] = useState(false);
  const timer = useRef(null);
  const lastTouch = useRef(0);
  const done = useRef(onDone);
  done.current = onDone;
  const active = useRef(false);

  const cancel = useCallback(() => {
    clearTimeout(timer.current);
    if (active.current) {
      active.current = false;
      setHolding(false);
    }
  }, []);
  const start = useCallback(
    (e, allowed = true) => {
      if (e?.type?.startsWith('touch')) lastTouch.current = Date.now();
      else if (e?.type?.startsWith('mouse') && Date.now() - lastTouch.current < 900) return;
      if (e?.type === 'mousedown' && e.button !== 0) return;
      if (!allowed || active.current) return;
      active.current = true;
      setHolding(true);
      clearTimeout(timer.current);
      timer.current = setTimeout(() => {
        active.current = false;
        setHolding(false);
        done.current();
      }, ms);
    },
    [ms]
  );
  const end = useCallback(
    (e) => {
      if (e?.type?.startsWith('touch')) lastTouch.current = Date.now();
      else if (e?.type?.startsWith('mouse') && Date.now() - lastTouch.current < 900) return;
      cancel();
    },
    [cancel]
  );
  useEffect(() => () => clearTimeout(timer.current), []);
  return { holding, start, end, cancel };
}

function pickMime() {
  if (typeof MediaRecorder === 'undefined') return null;
  return ['audio/webm;codecs=opus', 'audio/mp4', 'audio/webm', 'audio/ogg;codecs=opus'].find((t) => MediaRecorder.isTypeSupported?.(t)) ?? '';
}

// Hold to record a voice note that only plays back here.
// state: idle | asking | recording | done | denied | unsupported
export function useVoiceNote(maxSeconds = VOICE_MAX_S) {
  const [state, setState] = useState('idle');
  const [elapsed, setElapsed] = useState(0);
  const [clip, setClip] = useState(null); // { url, duration }
  const [playing, setPlaying] = useState(false);
  const rec = useRef(null);
  const want = useRef(false); // still holding? (the permission prompt can outlast the press)
  const audio = useRef(null);
  const urlRef = useRef(null);

  const stopStream = () => {
    const r = rec.current;
    if (!r) return;
    clearInterval(r.tick);
    clearTimeout(r.limit);
    r.stream.getTracks().forEach((t) => t.stop());
    rec.current = null;
  };

  const start = useCallback(async () => {
    if (rec.current || want.current) return;
    want.current = true;
    const mime = pickMime();
    if (mime === null || !navigator.mediaDevices?.getUserMedia) {
      want.current = false;
      return setState('unsupported');
    }
    setState('asking');
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch {
      want.current = false;
      return setState('denied');
    }
    if (!want.current) {
      // they let go while the browser was asking: nothing recorded, the mic is ready next time
      stream.getTracks().forEach((t) => t.stop());
      return setState('idle');
    }
    const mr = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
    const chunks = [];
    const at = Date.now();
    mr.ondataavailable = (e) => e.data.size && chunks.push(e.data);
    mr.onstop = () => {
      const duration = Math.min(maxSeconds, (Date.now() - at) / 1000);
      const blob = new Blob(chunks, { type: mr.mimeType || mime || 'audio/webm' });
      chunks.length = 0;
      stopStream();
      if (duration < 0.6 || !blob.size) return setState('idle');
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
      urlRef.current = URL.createObjectURL(blob);
      setClip({ url: urlRef.current, duration });
      setState('done');
    };
    rec.current = {
      mr,
      stream,
      tick: setInterval(() => setElapsed((Date.now() - at) / 1000), 250),
      limit: setTimeout(() => mr.state !== 'inactive' && mr.stop(), maxSeconds * 1000)
    };
    setElapsed(0);
    mr.start(250);
    setState('recording');
  }, [maxSeconds]);

  const stop = useCallback(() => {
    want.current = false;
    const r = rec.current;
    if (r && r.mr.state !== 'inactive') r.mr.stop();
  }, []);

  const pause = () => {
    audio.current?.pause();
    setPlaying(false);
  };

  const togglePlay = useCallback(() => {
    if (!urlRef.current) return;
    let a = audio.current;
    if (!a) {
      a = audio.current = new Audio();
      a.addEventListener('ended', () => setPlaying(false));
      a.addEventListener('pause', () => setPlaying(false));
    }
    if (!a.paused) return pause();
    if (a.src !== urlRef.current) a.src = urlRef.current;
    a.currentTime = 0;
    a.play().then(() => setPlaying(true), () => setPlaying(false));
  }, []);

  // Drop everything: the recording, the player, the URL. Used by RE-RECORD and by the burn.
  const clear = useCallback(() => {
    want.current = false;
    const r = rec.current;
    if (r) {
      r.mr.onstop = null;
      if (r.mr.state !== 'inactive') r.mr.stop();
      stopStream();
    }
    if (audio.current) {
      audio.current.pause();
      audio.current.removeAttribute('src');
      audio.current.load?.();
    }
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    urlRef.current = null;
    setClip(null);
    setPlaying(false);
    setElapsed(0);
    setState((s) => (s === 'denied' || s === 'unsupported' ? s : 'idle'));
  }, []);

  useEffect(() => () => {
    want.current = false;
    const r = rec.current;
    if (r) {
      r.mr.onstop = null;
      try {
        r.mr.stop();
      } catch {}
      stopStream();
    }
    audio.current?.pause();
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
  }, []);

  return { state, elapsed, clip, playing, start, stop, togglePlay, clear };
}
