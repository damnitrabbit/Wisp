'use client';
// A voice-note waveform that fills from the left as `frac` (0..1) grows — smoothly, via a width-revealed
// overlay. Used two ways: while recording (frac = seconds / 2 min, so the note draws in as you speak) and
// while playing back (frac = played / duration, so it flows left→right like a normal player). The bars are
// deterministic for a given seed/size, so the shape is stable across renders; only the reveal moves.
import { useMemo } from 'react';

function mulberry(seed) {
  let a = seed >>> 0;
  return () => {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// one set of vertical stroke bars across the whole strip (same maths as the design's live_wave)
function barsPath(w, h, seed) {
  const mid = h / 2, step = w > 300 ? 5 : 4;
  const r = mulberry(seed);
  let d = '';
  for (let x = 3; x < w - 2; x += step) {
    const t = x / w;
    let env = (0.35 + 0.65 * Math.abs(Math.sin(t * 17 + 1.1))) * (0.6 + 0.4 * Math.sin(t * 41));
    if (r() < 0.08) env *= 0.25;
    const a = Math.max(0.1, Math.min(1, env * (0.6 + r() * 0.5))) * (mid - 4);
    d += `M${x} ${(mid - a).toFixed(1)}L${x} ${(mid + a).toFixed(1)}`;
  }
  return d;
}

export default function VoiceWave({
  frac = 0, w = 512, h = 80, sw = 2, seed = 404,
  trackColor = '#9A9186', fillColor = '#221E1A', playhead = true, playheadColor = '#B8352A',
  pencilRest = true, trackBars = false, animate = true,
}) {
  const d = useMemo(() => barsPath(w, h, seed), [w, h, seed]);
  const f = Math.max(0, Math.min(1, frac));
  const mid = h / 2, pct = `${(f * 100).toFixed(2)}%`;
  const svg = (children, extra) => (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} aria-hidden="true" style={{ display: 'block', overflow: 'visible', ...extra }}>{children}</svg>
  );
  const barPath = (color) => <path d={d} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" />;
  const rest = pencilRest ? <path d={`M3 ${mid} L${w - 2} ${mid}`} stroke={trackColor} strokeWidth="1.3" strokeDasharray="2 6" opacity="0.55" /> : null;
  return (
    <div style={{ position: 'relative', width: w, height: h }}>
      {/* the track: a pencil line ahead (recording), and/or the whole note faint (playback) */}
      {svg(<>{rest}{trackBars && barPath(trackColor)}</>)}
      {/* the part reached so far, in full ink, revealed left→right */}
      <div style={{ position: 'absolute', inset: 0, width: pct, overflow: 'hidden', transition: animate ? 'width .22s linear' : 'none' }}>
        {svg(barPath(fillColor), { position: 'absolute', left: 0, top: 0 })}
      </div>
      {/* the moving edge */}
      {playhead && (
        <div aria-hidden="true" style={{ position: 'absolute', top: -4, bottom: -4, left: pct, width: 2, background: playheadColor, borderRadius: 1, transform: 'translateX(-1px)', transition: animate ? 'left .22s linear' : 'none' }} />
      )}
    </div>
  );
}
