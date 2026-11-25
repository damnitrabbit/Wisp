'use client';
// A small paper calendar for "a date" (replaces the browser's own picker, which on some browsers stays on
// screen after a pick and even follows you to the next screen). It closes when you pick a day, tap outside,
// press Escape, or scroll the page.
import { useEffect, useMemo, useRef, useState } from 'react';

const INK = '#221E1A', PENCIL = '#5F584E', RED = '#B8352A', PAPER = '#F7F2E7', RULE = '#D3C7B0';
const HAND = "'Nothing You Could Do', 'Caveat', cursive";
const TYPE = "'Courier Prime', 'Courier New', monospace";
const MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
const ymd = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
const parse = (s) => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };

export default function DatePicker({ open, anchor, min, max, value, onPick, onClose }) {
  const box = useRef(null);
  const start = value || min;
  const [view, setView] = useState(() => (start ? parse(start) : new Date()));
  useEffect(() => { if (open) setView(start ? parse(start) : new Date()); }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!open) return;
    const down = (e) => { if (box.current && !box.current.contains(e.target)) onClose(); };
    const key = (e) => { if (e.key === 'Escape') onClose(); };
    const t = setTimeout(() => document.addEventListener('pointerdown', down, true), 0); // not the tap that opened it
    document.addEventListener('keydown', key);
    window.addEventListener('resize', onClose);
    window.addEventListener('scroll', onClose, true);
    return () => {
      clearTimeout(t);
      document.removeEventListener('pointerdown', down, true);
      document.removeEventListener('keydown', key);
      window.removeEventListener('resize', onClose);
      window.removeEventListener('scroll', onClose, true);
    };
  }, [open, onClose]);

  useEffect(() => { if (open) box.current?.querySelector('[data-day]:not([disabled])')?.focus({ preventScroll: true }); }, [open, view]);

  const days = useMemo(() => {
    const first = new Date(view.getFullYear(), view.getMonth(), 1);
    const lead = (first.getDay() + 6) % 7; // weeks start on Monday
    const n = new Date(view.getFullYear(), view.getMonth() + 1, 0).getDate();
    return [...Array(lead).fill(null), ...Array.from({ length: n }, (_, i) => new Date(view.getFullYear(), view.getMonth(), i + 1))];
  }, [view]);

  if (!open) return null;
  const minD = min ? parse(min) : null, maxD = max ? parse(max) : null;
  const prevOk = !minD || new Date(view.getFullYear(), view.getMonth(), 0) >= minD;
  const nextOk = !maxD || new Date(view.getFullYear(), view.getMonth() + 1, 1) <= maxD;

  // place it under "a date", kept on screen
  const W = 292;
  const r = anchor;
  let left = r ? r.left + r.width / 2 - W / 2 : window.innerWidth / 2 - W / 2;
  left = Math.max(12, Math.min(left, window.innerWidth - W - 12));
  let top = r ? r.bottom + 10 : window.innerHeight / 2 - 160;
  if (top + 330 > window.innerHeight) top = Math.max(12, (r ? r.top : window.innerHeight / 2) - 340);

  const nav = (dir) => setView((v) => new Date(v.getFullYear(), v.getMonth() + dir, 1));
  const arrow = (dir, ok) => (
    <button type="button" aria-label={dir < 0 ? 'Previous month' : 'Next month'} disabled={!ok} onClick={() => nav(dir)}
      style={{ width: 36, height: 36, fontFamily: TYPE, fontSize: 15, color: ok ? INK : RULE, cursor: ok ? 'pointer' : 'default' }}>
      {dir < 0 ? '←' : '→'}
    </button>
  );

  return (
    <div ref={box} role="dialog" aria-label="Pick the day it opens"
      style={{ position: 'fixed', zIndex: 90, left, top, width: W, padding: '14px 16px 12px', background: PAPER, color: INK,
        transform: 'rotate(-.6deg)', filter: 'drop-shadow(0 16px 24px rgba(0,0,0,.45)) drop-shadow(0 2px 3px rgba(0,0,0,.3))',
        clipPath: 'polygon(0 1%, 18% 0, 41% 1.2%, 63% .2%, 84% 1%, 100% 0, 99.4% 34%, 100% 67%, 99.2% 100%, 72% 99%, 47% 100%, 22% 98.8%, 0 100%, .8% 66%, 0 33%)' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        {arrow(-1, prevOk)}
        <span style={{ fontFamily: HAND, fontSize: 22 }}>{MONTHS[view.getMonth()]} {view.getFullYear()}</span>
        {arrow(1, nextOk)}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', marginTop: 6, borderTop: `1px dashed ${RULE}`, paddingTop: 8 }}>
        {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((d, i) => (
          <span key={i} style={{ fontFamily: TYPE, fontSize: 10, letterSpacing: '.1em', color: PENCIL, textAlign: 'center', paddingBottom: 4 }}>{d}</span>
        ))}
        {days.map((d, i) => {
          if (!d) return <span key={i} />;
          const s = ymd(d);
          const off = (minD && d < minD) || (maxD && d > maxD);
          const on = s === value;
          return (
            <button key={i} type="button" data-day={s} disabled={off} aria-pressed={on}
              onClick={() => { onPick(s); onClose(); }}
              style={{ position: 'relative', height: 36, fontFamily: TYPE, fontSize: 13, color: off ? RULE : INK, cursor: off ? 'default' : 'pointer' }}>
              {on && (
                <svg aria-hidden="true" viewBox="0 0 40 34" style={{ position: 'absolute', inset: 0, margin: 'auto', width: 34, height: 30, overflow: 'visible' }}>
                  <path d="M20 3 C33 2 39 10 37 19 C35 29 22 33 11 30 C3 27 1 18 5 11 C9 4 18 2 27 5" fill="none" stroke={RED} strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              )}
              <span style={{ position: 'relative' }}>{d.getDate()}</span>
            </button>
          );
        })}
      </div>
      <div style={{ fontFamily: TYPE, fontSize: 9.5, letterSpacing: '.14em', color: PENCIL, marginTop: 6, textAlign: 'center' }}>
        {maxD && (maxD - (minD || new Date())) < 40 * 86400000 ? 'WITH AN EMAIL, UP TO 30 DAYS OUT' : 'UP TO A YEAR OUT'}
      </div>
    </div>
  );
}
