'use client';
// An audio-reactive waveform for the voice pod. The line's height tracks the live mic/stream
// loudness of one participant (rtc.level(id)), so it only moves while that person is actually
// speaking and sits flat when they're quiet. A muted participant gets a visibly distinct, still
// dashed line instead — no metered stream means no motion at all.
import { useEffect, useMemo, useRef } from 'react';
import { level } from '@/lib/rtc';

// A hand-drawn-ish wave path at full amplitude, centred on h/2. Deterministic from `seed` so the
// shape is stable across renders; we only scale it vertically at runtime.
function wavePath(w, h, seed) {
  const mid = h / 2;
  const n = 46;
  let s = (seed % 2147483647) || 1;
  const rnd = () => ((s = (s * 48271) % 2147483647), s / 2147483647);
  const bumps = Array.from({ length: 3 }, () => [0.12 + rnd() * 0.76, 0.06 + rnd() * 0.1, 0.5 + rnd() * 0.5]);
  let d = `M0 ${mid.toFixed(1)}`;
  for (let i = 1; i <= n; i++) {
    const t = i / n;
    let env = 0;
    for (const [c, sg, a] of bumps) env += a * Math.exp(-(((t - c) / sg) ** 2));
    env = Math.min(1, env) * Math.sqrt(Math.max(0, Math.sin(Math.PI * t)));
    const jitter = (rnd() - 0.5) * 1.6;
    const y = mid + (i % 2 ? -1 : 1) * env * (h * 0.44) + jitter;
    d += ` L${(t * w).toFixed(1)} ${y.toFixed(1)}`;
  }
  return d;
}

export default function LiveWave({ id, muted = false, w = 760, h = 120, color = '#221E1A' }) {
  const gRef = useRef(null);
  const cur = useRef(0.06);
  const seed = useMemo(() => {
    let n = w * 131 + h;
    for (let i = 0; i < (id || '').length; i++) n = (n * 31 + id.charCodeAt(i)) >>> 0;
    return n;
  }, [id, w, h]);
  const d = useMemo(() => wavePath(w, h, seed), [w, h, seed]);

  useEffect(() => {
    if (muted) return undefined;
    let raf = 0;
    const tick = () => {
      const lv = level(id); // RMS, ~0 silent, ~0.05–0.18 speaking
      const target = Math.max(0.06, Math.min(1, (lv - 0.012) / 0.14));
      cur.current += (target - cur.current) * 0.3;
      const g = gRef.current;
      if (g) g.setAttribute('transform', `translate(0 ${h / 2}) scale(1 ${cur.current.toFixed(3)}) translate(0 ${-h / 2})`);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [id, muted, h]);

  const svgStyle = { display: 'block', width: '100%', height: h, overflow: 'visible' };

  if (muted) {
    // Distinct from a quiet-but-live line: dashed and dimmed, perfectly still.
    return (
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true" style={svgStyle}>
        <path d={`M0 ${h / 2} L${w} ${h / 2}`} fill="none" stroke={color} strokeWidth="2"
          strokeDasharray="2 8" strokeLinecap="round" opacity="0.4" />
      </svg>
    );
  }
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true" style={svgStyle}>
      <g ref={gRef} fill="none" stroke={color} strokeLinecap="round" strokeLinejoin="round"
        style={{ transition: 'none' }}>
        <path d={d} strokeWidth="2.6" />
      </g>
    </svg>
  );
}
