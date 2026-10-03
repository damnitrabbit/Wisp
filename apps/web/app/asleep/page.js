'use client';
// Pods asleep: static board, with the real time until 10pm India time.
import { useEffect, useMemo, useState } from 'react';
import Screen from '@/v5/Screen';
import D0 from '@/v5/screens/V5Asleep';
import M0 from '@/v5/screens/V5MAsleep';
import { podsInfo } from '@/lib/v5/hours';

const live = (s) => ({ ...s, html: s.html.replace('That\'s in <span style="color:#E9E9E7">1 hour 42 minutes</span>', '{{until}}') });
const D = live(D0), M = live(M0);

function words(mins) {
  const h = Math.floor(mins / 60), m = mins % 60;
  const p = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  if (!h) return p(m, 'minute');
  return m ? `${p(h, 'hour')} ${p(m, 'minute')}` : p(h, 'hour');
}

export default function Asleep() {
  const [info, setInfo] = useState(null);
  useEffect(() => {
    const tick = () => setInfo(podsInfo());
    tick();
    const t = setInterval(tick, 60_000);
    return () => clearInterval(t);
  }, []);
  const vals = useMemo(() => ({
    until: !info ? '' : info.open ? "They're open right now" : `That's in ${words(info.minsToOpen)}`
  }), [info]);
  return <Screen desktop={D} phone={M} vals={vals} />;
}
