'use client';
// Live pieces of the open pod and group pod screens: generated HTML templates (design/v5/v5_rooms_parts.py → parts.gen.js)
// filled with real names. `fill` makes a string (so parts can nest with {{{x}}}); <Tpl> renders one and wires its actions.
import { memo, useMemo } from 'react';
import Link from 'next/link';
import parse, { domToReact, attributesToProps } from 'html-react-parser';
import P, { CSS } from './parts.gen';

export { P, CSS };

const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
export const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
const look = (k, vals) => k.split('.').reduce((o, x) => (o == null ? undefined : o[x]), vals);

// {{x}} is escaped text; {{{x}}} is trusted markup (only ever another filled part).
export function fill(name, vals = {}) {
  let s = P[name];
  if (s == null) throw new Error(`no part ${name}`);
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

// Elements with data-act="x" (and optional data-id) call onAct(x, id). Everything else renders as generated.
function render(html, onAct) {
  const options = {
    replace(node) {
      if (node.type !== 'tag') return undefined;
      const a = node.attribs || {};
      if (node.name === 'a' && a.href && a.href.startsWith('/')) {
        return <Link {...attributesToProps(a)} href={a.href}>{domToReact(node.children || [], options)}</Link>;
      }
      if (!a['data-act'] || !onAct) return undefined;
      const props = attributesToProps(a);
      const go = (e) => { e.preventDefault(); e.stopPropagation(); onAct(a['data-act'], a['data-id'] || null, e); };
      const extra = node.name === 'a' ? { href: '#' } : { role: 'button', tabIndex: 0, onKeyDown: (e) => { if (e.key === 'Enter' || e.key === ' ') go(e); } };
      const Tag = node.name;
      return <Tag {...props} {...extra} onClick={go}>{domToReact(node.children || [], options)}</Tag>;
    }
  };
  return parse(html, options);
}

const Tpl = memo(function Tpl({ html, onAct }) {
  const tree = useMemo(() => render(html, onAct), [html, onAct]);
  return <>{tree}</>;
});
export default Tpl;

// Re-create a slot's own wrapper element (its class and inline style) around live content.
export function Wrap({ node, children }) {
  const props = attributesToProps({ ...(node.attribs || {}) });
  delete props['data-slot'];
  const Tag = node.name || 'div';
  return <Tag {...props}>{children}</Tag>;
}
