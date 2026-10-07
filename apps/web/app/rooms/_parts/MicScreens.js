'use client';
// The mic screens (V5MicAsk / V5MicBlocked / V5NoVoice) are drawn for the talk pod; in a room the same boards say room words.
import { useMemo } from 'react';
import Screen from '@/v5/Screen';
import DAsk0 from '@/v5/screens/V5MicAsk';
import MAsk0 from '@/v5/screens/V5MMicAsk';
import DBlocked0 from '@/v5/screens/V5MicBlocked';
import MBlocked0 from '@/v5/screens/V5MMicBlocked';
import DNoVoice0 from '@/v5/screens/V5NoVoice';
import MNoVoice0 from '@/v5/screens/V5MNoVoice';

const WORDS = [
  ["It's only so moss_byte can hear you, now that you both said yes. Your voice goes straight between you, and it's never recorded.",
    "It's only so the room can hear you while you're on stage. Your voice goes straight to the people here, and it's never recorded."],
  ['just the two of you.', 'listening needs no mic.'],
  ['nobody else listening.', 'only speaking does.'],
  ['STAY ON TEXT', 'KEEP LISTENING'],
  ['stay on text', 'keep listening'],
  ['no rush. text works', 'no rush. listening works'],
  ['text works just as well.', 'listening works just as well.'],
  ['Text works just the same. For voice, open N0TRACE', 'Voice rooms need it. Open N0TRACE'],
  ['continue on text', 'back to the rooms']
];
function roomWords(scr, crumb) {
  let html = scr.html.split('>talk pod<').join(`>${crumb}<`);
  for (const [a, b] of WORDS) html = html.split(a).join(b);
  return { ...scr, html };
}
const cache = new Map();
function boards(crumb) {
  if (!cache.has(crumb)) {
    cache.set(crumb, {
      ask: [roomWords(DAsk0, crumb), roomWords(MAsk0, crumb)],
      blocked: [roomWords(DBlocked0, crumb), roomWords(MBlocked0, crumb)],
      novoice: [roomWords(DNoVoice0, crumb), roomWords(MNoVoice0, crumb)]
    });
  }
  return cache.get(crumb);
}

// which: 'ask' | 'blocked' | 'novoice'. Clicks are matched by the link's words.
export default function MicScreen({ which, crumb = 'open pod', mic, onBack }) {
  const [D, M] = boards(crumb)[which];
  const acts = useMemo(() => ({
    'allow mic': () => mic.allow(),
    'keep listening': () => mic.decline(),
    reload: () => window.location.reload(),
    'back to the rooms': () => onBack?.()
  }), [mic, onBack]);
  const onClickCapture = (e) => {
    const el = e.target.closest && e.target.closest('a,button,[role="button"]');
    if (!el) return;
    const f = acts[(el.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase()];
    if (!f) return;
    e.preventDefault();
    e.stopPropagation();
    f(e);
  };
  return (
    <div style={{ display: 'contents' }} onClickCapture={onClickCapture}>
      <Screen desktop={D} phone={M} />
    </div>
  );
}
