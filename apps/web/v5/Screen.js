'use client';
// Renders a generated design screen (design/v5 → apps/web/v5/screens) as live React.
//   <Screen phone={MHome} desktop={Home} vals={{ writeMode: true, toSpeak }} slots={{ input: <textarea/> }} />
// - links to "V5X.dc.html" become routes (see routes.js); `links` overrides a link with a route or a function
// - {{name}} in text and attributes reads from `vals`; on* attributes call the function in `vals`
// - <sc-if value="{{x}}"> shows its children when vals.x is truthy
// - an element with data-slot="name" is replaced by slots[name] (left as designed when no slot is given)
import { createElement, useEffect, useLayoutEffect, useMemo, useState, Fragment } from 'react';
import Link from 'next/link';
import parse, { domToReact, attributesToProps } from 'html-react-parser';
import { routeFor } from './routes';

const useIso = typeof window === 'undefined' ? useEffect : useLayoutEffect;

// phone layout below this width, or on a portrait tablet
export function pickPhone() {
  if (typeof window === 'undefined') return true;
  const w = window.innerWidth, h = window.innerHeight;
  return w < 700 || (w < 1000 && h > w);
}

export function useView() {
  const [v, setV] = useState(null); // null until we know, so nothing renders at the wrong size
  useIso(() => {
    const f = () => setV({ phone: pickPhone(), w: window.innerWidth, h: window.innerHeight });
    f();
    window.addEventListener('resize', f);
    return () => window.removeEventListener('resize', f);
  }, []);
  return v;
}

const EV = { onclick: 'onClick', onpointerdown: 'onPointerDown', onpointerup: 'onPointerUp', onpointerleave: 'onPointerLeave',
  onpointercancel: 'onPointerCancel', onkeydown: 'onKeyDown', onkeyup: 'onKeyUp', onmousedown: 'onMouseDown', onmouseup: 'onMouseUp',
  onmouseleave: 'onMouseLeave', ontouchstart: 'onTouchStart', ontouchend: 'onTouchEnd', oncontextmenu: 'onContextMenu', oninput: 'onInput', onchange: 'onChange' };

const ONE = /^\s*\{\{\s*([^}]+?)\s*\}\}\s*$/;
function look(expr, vals) {
  expr = expr.trim();
  if (expr === 'true') return true;
  if (expr === 'false') return false;
  if (/^-?\d+(\.\d+)?$/.test(expr)) return +expr;
  return expr.split('.').reduce((o, k) => (o == null ? undefined : o[k]), vals);
}
function interp(s, vals) {
  return s.replace(/\{\{\s*([^}]+?)\s*\}\}/g, (m, e) => { const v = look(e, vals); return v == null ? '' : String(v); });
}

function build(html, vals, slots, links, router) {
  const options = {
    replace(node) {
      if (node.type === 'text' && node.data.includes('{{')) return <>{interp(node.data, vals)}</>;
      if (node.type !== 'tag') return undefined;
      const a = node.attribs || {};
      const kids = () => domToReact(node.children || [], options);

      if (node.name === 'sc-if') {
        const m = ONE.exec(a.value || '');
        return m && look(m[1], vals) ? <>{kids()}</> : <></>;
      }
      if (a['data-slot'] && slots && Object.prototype.hasOwnProperty.call(slots, a['data-slot'])) {
        const s = slots[a['data-slot']];
        return <>{typeof s === 'function' ? s(node) : s}</>;
      }

      // attributes: events from vals, {{ }} values, then React-ise the rest
      const plain = {}, ev = {};
      for (const k in a) {
        const v = a[k];
        if (k.startsWith('on')) {
          const m = ONE.exec(v);
          const name = EV[k.toLowerCase()];
          if (m && name) { const f = look(m[1], vals); if (typeof f === 'function') ev[name] = f; }
          continue;
        }
        plain[k] = typeof v === 'string' && v.includes('{{') ? interp(v, vals) : v;
      }

      // links between screens
      if (node.name === 'a' && plain.href && plain.href.endsWith('.dc.html') || (node.name === 'a' && /\.dc\.html/.test(plain.href || ''))) {
        const key = plain.href.replace(/^V5M?/, '').replace(/\.dc\.html.*$/, '');
        const over = links && (links[key] ?? links[plain.href]);
        const props = attributesToProps({ ...plain, href: undefined });
        delete props.href;
        if (typeof over === 'function') {
          return <a {...props} {...ev} href="#" role="button" onClick={(e) => { e.preventDefault(); over(e); }}>{kids()}</a>;
        }
        const to = typeof over === 'string' ? over : routeFor(plain.href);
        return <Link {...props} {...ev} href={to || '/home'}>{kids()}</Link>;
      }
      if (node.name === 'a' && (plain.href === '#' || !plain.href) && !Object.keys(ev).length && links && a['data-act'] && links[a['data-act']]) {
        const f = links[a['data-act']];
        return <a {...attributesToProps(plain)} href="#" onClick={(e) => { e.preventDefault(); f(e); }}>{kids()}</a>;
      }
      if (!Object.keys(ev).length && !Object.keys(plain).some((k) => a[k] !== plain[k])) return undefined;
      const props = { ...attributesToProps(plain), ...ev };
      if (ev.onClick && !props.role && node.name !== 'button' && node.name !== 'a') { props.role = 'button'; props.tabIndex = 0; }
      return createElement(node.name, props, node.children && node.children.length ? kids() : undefined);
    }
  };
  return parse(html, options);
}

// The board itself: the phone variant fills the phone; the desktop variant is a 1440-wide board scaled to the window.
export default function Screen({ phone, desktop, vals = {}, slots, links, css = '', className = '' }) {
  const view = useView();
  const scr = view ? (view.phone ? phone || desktop : desktop || phone) : null;
  const tree = useMemo(() => (scr ? build(scr.html, vals, slots, links) : null), [scr, vals, slots, links]);
  if (!scr) return <div style={{ minHeight: '100dvh', background: '#0D0D0E' }} />;
  const style = <style dangerouslySetInnerHTML={{ __html: scr.css + '\n' + css }} />;
  if (scr.phone) {
    const fill = scr.h <= 844;
    return (
      <div className={`v5-phone ${className}`} style={{ position: 'relative', width: '100%', minWidth: 320, height: fill ? '100dvh' : 'auto', minHeight: fill ? 568 : scr.h, background: scr.bg, color: '#E9E9E7', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {style}{tree}
      </div>
    );
  }
  const tall = scr.h > 900;
  const s = tall ? Math.min(view.w / scr.w, 1.4) : Math.min(view.w / scr.w, view.h / scr.h, 1.4);
  return (
    <div className={`v5-desk ${className}`} style={{ minHeight: '100dvh', background: '#070707', display: 'flex', alignItems: tall ? 'flex-start' : 'center', justifyContent: 'center', overflow: 'hidden' }}>
      <div style={{ width: scr.w * s, height: scr.h * s, position: 'relative', flexShrink: 0 }}>
        <div style={{ position: 'absolute', left: 0, top: 0, width: scr.w, height: scr.h, transform: `scale(${s})`, transformOrigin: '0 0', background: scr.bg, color: '#E9E9E7', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {style}{tree}
        </div>
      </div>
    </div>
  );
}
