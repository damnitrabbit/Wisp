import { ImageResponse } from 'next/og';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

export const alt = 'N0TRACE · Leave no trace.';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

// Social preview: the 8-bit rabbit on black, set in the site's own font.
export default async function OG() {
  const [light, medium] = await Promise.all([
    readFile(join(process.cwd(), 'assets/plex-mono-300.ttf')),
    readFile(join(process.cwd(), 'assets/plex-mono-500.ttf'))
  ]);
  const px = 20;
  const block = (x, y, w, h) => (
    <div style={{ position: 'absolute', left: x * px, top: y * px, width: w * px, height: h * px, background: '#E6E3D8' }} />
  );
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', background: '#000', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 72, color: '#EDEDED', fontFamily: 'Plex' }}>
        <div style={{ position: 'relative', width: 24 * px, height: 15 * px, display: 'flex' }}>
          {block(2, 2, 6, 6)}
          {block(16, 2, 6, 6)}
          {block(9.5, 12, 1, 1)}
          {block(11.5, 12, 1, 1)}
          {block(13.5, 12, 1, 1)}
          {block(10.5, 13, 1, 1)}
          {block(12.5, 13, 1, 1)}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ fontSize: 84, fontWeight: 500, letterSpacing: 14 }}>N0TRACE</div>
          <div style={{ fontSize: 40, fontWeight: 300 }}>LEAVE NO TRACE.</div>
          <div style={{ fontSize: 22, fontWeight: 300, color: '#8C8C8C' }}>ANONYMOUS VOICE ROOMS + RANDOM 1:1 CHAT · KEPT: NOTHING</div>
        </div>
      </div>
    ),
    { ...size, fonts: [{ name: 'Plex', data: light, weight: 300 }, { name: 'Plex', data: medium, weight: 500 }] }
  );
}
