'use client';
// Live pieces of the pod screens (chat lines, room slips, stage cards): generated HTML templates
// (design/v5/v5_pods_parts.py → parts.gen.js) with {{tokens}} filled in here.
import { memo, useMemo } from 'react';
import parse, { domToReact, attributesToProps } from 'html-react-parser';

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
const look = (k, vals) => k.split('.').reduce((o, x) => (o == null ? undefined : o[x]), vals);

// {{x}} is escaped text; {{{x}}} is trusted markup (only ever another generated part).
export function fill(tpl, vals = {}) {
  let s = tpl;
  for (let i = 0; i < 3 && s.includes('<sc-if'); i++) {
    s = s.replace(/<sc-if value="\{\{\s*([\w.!]+)\s*\}\}">((?:(?!<sc-if)[\s\S])*?)<\/sc-if>/g, (m, k, inner) => {
      const neg = k.startsWith('!');
      const v = look(neg ? k.slice(1) : k, vals);
      return (neg ? !v : v) ? inner : '';
    });
  }
  s = s.replace(/\{\{\{\s*([\w.]+)\s*\}\}\}/g, (m, k) => String(look(k, vals) ?? ''));
  return s.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (m, k) => esc(look(k, vals)));
}

// acts: { [data-act]: fn } wires <a href="#" data-act="…">; links whose href is a design screen are left inert.
function render(html, acts) {
  const options = {
    replace(node) {
      if (node.type !== 'tag') return undefined;
      const a = node.attribs || {};
      const f = a['data-act'] && acts && acts[a['data-act']];
      if (f) {
        const props = attributesToProps(a);
        return (
          <a {...props} href="#" role="button" onClick={(e) => { e.preventDefault(); e.stopPropagation(); f(e); }}>
            {domToReact(node.children || [], options)}
          </a>
        );
      }
      return undefined;
    }
  };
  return parse(html, options);
}

const Part = memo(function Part({ html, vals, acts }) {
  const tree = useMemo(() => render(fill(html, vals), acts), [html, vals, acts]);
  return <>{tree}</>;
});
export default Part;

// Clicks on a screen's links by their words: { 'allow mic': fn }. Works for screens whose links are plain
// href="#" (the system screens) as well as design links. Wrap a <Screen> in it.
export function Acts({ acts, children }) {
  const onClickCapture = (e) => {
    const el = e.target.closest && e.target.closest('a,button,[role="button"]');
    if (!el) return;
    const label = (el.textContent || '').replace(/\s+/g, ' ').trim().toLowerCase();
    const f = acts[label];
    if (!f) return;
    e.preventDefault();
    e.stopPropagation();
    f(e);
  };
  return <div style={{ display: 'contents' }} onClickCapture={onClickCapture}>{children}</div>;
}
