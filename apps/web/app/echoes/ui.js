'use client';
// Live pieces of the ECHOES screens: fills the generated card / slip templates (parts.gen.js) with real notes.
import Link from 'next/link';
import parse, { domToReact, attributesToProps } from 'html-react-parser';
import P from './parts.gen';

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ESC[c]);

// {{name}} → escaped value; <sc-if value="{{x}}">…</sc-if> kept only when vals.x is truthy (templates never nest them).
// Links to /… become <Link>; elements with data-act="x" call acts.x.
export function Tpl({ html, vals, acts }) {
  const src = html
    .replace(/<sc-if value="\{\{(\w+)\}\}">([\s\S]*?)<\/sc-if>/g, (m, k, inner) => (vals[k] ? inner : ''))
    .replace(/\{\{(\w+)\}\}/g, (m, k) => esc(vals[k]));
  const options = {
    replace(node) {
      if (node.type !== 'tag') return undefined;
      const a = node.attribs || {};
      if (node.name === 'a' && a.href && a.href.startsWith('/')) {
        const props = attributesToProps(a);
        return <Link {...props} href={a.href}>{domToReact(node.children || [], options)}</Link>;
      }
      if (a['data-act'] && acts?.[a['data-act']]) {
        const props = attributesToProps(a);
        const f = acts[a['data-act']];
        return (
          <button {...props} onClick={(e) => { e.preventDefault(); e.stopPropagation(); f(e); }}>
            {domToReact(node.children || [], options)}
          </button>
        );
      }
      return undefined;
    }
  };
  return <>{parse(src, options)}</>;
}

// ---------- words for times ----------
export const fadesIn = (ms) => {
  if (ms <= 60_000) return 'fading';
  const h = Math.floor(ms / 3600_000);
  return h >= 1 ? `${h}h left` : `${Math.max(1, Math.floor(ms / 60_000))}m left`;
};
export const fadesShort = (ms) => {
  if (ms <= 60_000) return 'A MOMENT';
  const h = Math.floor(ms / 3600_000);
  return h >= 1 ? `${h}H` : `${Math.max(1, Math.floor(ms / 60_000))}M`;
};
export const leftAt = (t) => {
  const d = new Date(t);
  let h = d.getHours();
  const ap = h < 12 ? 'am' : 'pm';
  h = h % 12 || 12;
  return `left here at ${h}:${String(d.getMinutes()).padStart(2, '0')} ${ap}`;
};
export const ago = (t, now = Date.now()) => {
  const m = Math.max(0, Math.round((now - t) / 60_000));
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  return `${Math.floor(m / 60)}h ago`;
};
export const clock = (s) => {
  s = Math.max(0, Math.round(s || 0));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
};

// A soft made-up handle for a reply, from its id. Nobody's name: just so replies read as different voices.
const A = ['quiet', 'moss', 'paper', 'velvet', 'amber', 'hollow', 'slow', 'pale', 'lunar', 'drift', 'ember', 'still', 'cobalt', 'misty', 'linen', 'soft'];
const N = ['otter', 'byte', 'kite', 'moth', 'fern', 'heron', 'wren', 'pebble', 'lantern', 'reed', 'finch', 'tide', 'comet', 'willow', 'owl', 'cedar'];
export function handle(id = '') {
  let h = 0;
  for (const c of id) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return `${A[h % 16]}_${N[(h >>> 4) % 16]}`;
}

// ---------- the wall ----------
function cardVals(n, now, extra = {}) {
  const left = n.expiresAt - now;
  return {
    href: `/echoes/${n.id}`,
    text: n.text ?? '',
    to: n.to || 'you',
    title: leftAt(n.createdAt),
    dur: clock(n.duration),
    fades: fadesIn(left),
    fadeStyle: left < 3600_000 ? 'opacity:.55;filter:saturate(.6);' : '',
    heardCount: n.heardCount ?? 0,
    heartFill: n.heard ? '#B8352A' : 'none',
    isHeard: n.heard,
    replies: n.kind === 'echo' && n.replyCount ? `${n.replyCount} ${n.replyCount === 1 ? 'REPLY' : 'REPLIES'}` : '',
    ...extra
  };
}
const typeOf = (n) => (n.kind === 'unsent' ? 'letter' : n.mode === 'voice' ? 'voice' : 'text');

// Desktop: the eight designed spots, block after block down a board that scrolls inside its frame.
export function DeskWall({ notes, now }) {
  const blocks = Math.ceil(notes.length / 8);
  const height = (blocks - 1) * P.dBlock + 560;
  return (
    <div className="rise nt-wall" style={{ '--w': '.4s', position: 'relative', height: 640, margin: '-20px -40px -80px', overflowY: 'auto', overflowX: 'hidden', scrollbarWidth: 'none' }}>
      <div style={{ position: 'relative', height: height + 40, margin: '20px 40px 0' }}>
        {notes.map((n, i) => {
          const spot = i % 8, t = typeOf(n);
          const top = P.dSpots[spot].top + Math.floor(i / 8) * P.dBlock;
          const lines = P.dLines[`${spot}${t === 'letter' ? 'letter' : 'text'}`];
          return <Tpl key={n.id} html={P.dWall[`${spot}${t}`]} vals={cardVals(n, now, { top, lines })} />;
        })}
      </div>
    </div>
  );
}

// Phone: rows of one wide note or two narrow ones, the way the designed wall alternates.
const PATTERN = ['full', 'pair', 'full', 'pair', 'full', 'full', 'pair'];
function phoneH(n, w) {
  const half = w < 200;
  const t = typeOf(n);
  if (t === 'voice') return { h: half ? 156 : 164, lines: 1 };
  const size = half ? 15 : 16.5;
  const lh = t === 'letter' ? 24 : size * 1.45;
  const perLine = Math.max(8, Math.floor((w - (half ? 32 : 40)) / (size * 0.47)));
  const want = Math.ceil((n.text || '').length / perLine) + ((n.text || '').match(/\n/g)?.length ?? 0);
  const lines = Math.max(1, Math.min(want, half ? 7 : 8));
  const top = t === 'letter' ? 18 + 26 + 30 : 20;
  return { h: Math.round(top + lines * lh + 52), lines };
}
export function PhoneWall({ notes, now }) {
  const rows = [];
  let i = 0, r = 0, full = 0, half = 0;
  while (i < notes.length) {
    const kind = PATTERN[r % PATTERN.length];
    const a = notes[i], b = notes[i + 1];
    if (kind === 'pair' && b && typeOf(a) !== 'letter' && typeOf(b) !== 'letter') {
      rows.push({ pair: [a, b], v: [half % 6, (half + 1) % 6] });
      half += 2; i += 2;
    } else {
      rows.push({ one: a, v: full % 4 });
      full += 1; i += 1;
    }
    r += 1;
  }
  return (
    <div className="rise" style={{ '--w': '.4s', position: 'relative', marginTop: 22, display: 'flex', flexDirection: 'column', gap: 34, paddingTop: 16 }}>
      {rows.map((row) => {
        if (row.one) {
          const n = row.one, t = typeOf(n), w = P.mFullW[row.v];
          const { h, lines } = phoneH(n, w);
          const dx = Math.round((346 - w) / 2 + ((n.id.charCodeAt(0) % 13) - 6));
          return (
            <div key={n.id} style={{ display: 'flex' }}>
              <Tpl html={P.mFull[row.v][t]} vals={cardVals(n, now, { h, lines, dx, dy: 0, stampTop: h - 84 })} />
            </div>
          );
        }
        const [a, b] = row.pair;
        const [wa, wb] = [P.mHalfW[row.v[0]], P.mHalfW[row.v[1]]];
        const ha = phoneH(a, wa), hb = phoneH(b, wb);
        return (
          <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Tpl html={P.mHalf[row.v[0]][typeOf(a)]} vals={cardVals(a, now, { ...ha, dx: 0, dy: 6, stampTop: ha.h - 84 })} />
            <Tpl html={P.mHalf[row.v[1]][typeOf(b)]} vals={cardVals(b, now, { ...hb, dx: 0, dy: 0, stampTop: hb.h - 84 })} />
          </div>
        );
      })}
    </div>
  );
}

// ---------- replies ----------
export function slipHeight(r, phone) {
  if (r.kind === 'voice') return phone ? 96 : 112;
  const size = phone ? 16.5 : 19, lh = size * (phone ? 1.45 : 1.5);
  const perLine = Math.floor((phone ? 284 : 508) / (size * 0.47));
  const lines = Math.max(1, Math.ceil((r.text || '').length / perLine));
  return Math.round((phone ? 16 + 14 + 6 : 20 + 16 + 8) + lines * lh + (phone ? 20 : 24));
}

export function Slips({ replies, phone, now, playing, onPlay, onReport, onRemove, canRemove, scroll }) {
  const T = phone ? P.mSlip : P.dSlip;
  const list = replies.map((r, i) => (
    <Tpl
      key={r.id}
      html={T[i % 3][r.kind === 'voice' ? 'voice' : 'text']}
      vals={{
        h: slipHeight(r, phone),
        name: handle(r.id),
        when: `${r.kind === 'voice' ? 'VOICE · ' : ''}${ago(r.createdAt, now).toUpperCase()}`,
        text: r.text ?? '',
        dur: clock(r.duration),
        secs: Math.max(1, r.duration || 1),
        cls: playing === r.id ? 'playing' : '',
        playLabel: playing === r.id ? 'Pause' : 'Play',
        canRemove,
        canReport: !canRemove,
        reportLabel: r.reported ? 'REPORTED' : 'REPORT'
      }}
      acts={{ play: () => onPlay?.(r), report: () => !r.reported && onReport?.(r), remove: () => onRemove?.(r) }}
    />
  ));
  if (!scroll) return <>{list}</>;
  return list;
}

export function Tally({ n, phone }) {
  const t = phone ? P.mTally : P.dTally;
  return <span dangerouslySetInnerHTML={{ __html: t[Math.min(n, t.length - 1)] }} />;
}
