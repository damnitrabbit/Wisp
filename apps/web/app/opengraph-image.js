import { ImageResponse } from 'next/og';

export const alt = 'Wisp · Talk to strangers. Leave no trace.';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

// Social preview: the 8-bit rabbit on black, in the site's terminal style.
export default function OG() {
  const px = 22;
  const cream = '#E6E3D8';
  const block = (x, y, w, h) => (
    <div style={{ position: 'absolute', left: x * px, top: y * px, width: w * px, height: h * px, background: cream }} />
  );
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', background: '#000', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 72, color: '#EDEDED', fontFamily: 'monospace' }}>
        <div style={{ position: 'relative', width: 24 * px, height: 15 * px, display: 'flex' }}>
          {block(2, 2, 6, 6)}
          {block(16, 2, 6, 6)}
          {block(9.5, 12, 1, 1)}
          {block(11.5, 12, 1, 1)}
          {block(13.5, 12, 1, 1)}
          {block(10.5, 13, 1, 1)}
          {block(12.5, 13, 1, 1)}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div style={{ fontSize: 76, letterSpacing: 12 }}>WISP</div>
          <div style={{ fontSize: 34, color: '#8C8C8C' }}>TALK TO STRANGERS. LEAVE NO TRACE.</div>
          <div style={{ fontSize: 24, color: '#5E5E5E' }}>ANONYMOUS VOICE ROOMS + RANDOM 1:1 CHAT · NO ACCOUNTS · NOTHING STORED</div>
        </div>
      </div>
    ),
    size
  );
}
