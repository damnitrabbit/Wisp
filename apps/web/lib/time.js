'use client';
import { useEffect, useState } from 'react';
import { serverNow } from './wisp';

export function useNow(active = true, every = 250) {
  const [now, setNow] = useState(() => serverNow());
  useEffect(() => {
    if (!active) return;
    setNow(serverNow());
    const t = setInterval(() => setNow(serverNow()), every);
    return () => clearInterval(t);
  }, [active, every]);
  return now;
}

export const mmss = (ms) => {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
};
export const hhmmss = (ms) => {
  const s = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
};
