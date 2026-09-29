import { ImageResponse } from 'next/og';

export const alt = 'N0TRACE';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

// Link preview (WhatsApp, iMessage, Slack, X…): just the 8-bit rabbit, centred on black.
// Centred so it still reads when an app crops the preview to a square.
const PX = 14; // one rabbit pixel
const W = 20; // the rabbit spans x 2..22
const H = 12; // and y 2..14 of its 24×18 grid
const LEFT = (size.width - W * PX) / 2 - 2 * PX;
const TOP = (size.height - H * PX) / 2 - 2 * PX;

export default function OG() {
  const block = (x, y, w, h) => (
    <div style={{ position: 'absolute', left: LEFT + x * PX, top: TOP + y * PX, width: w * PX, height: h * PX, background: '#E6E3D8' }} />
  );
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', background: '#000', display: 'flex', position: 'relative' }}>
        {block(2, 2, 6, 6)}
        {block(16, 2, 6, 6)}
        {block(9.5, 12, 1, 1)}
        {block(11.5, 12, 1, 1)}
        {block(13.5, 12, 1, 1)}
        {block(10.5, 13, 1, 1)}
        {block(12.5, 13, 1, 1)}
      </div>
    ),
    size
  );
}
