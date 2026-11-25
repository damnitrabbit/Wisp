'use client';
// Pods asleep: static board, with the real time until 10pm India time, and "EMAIL ME AT 10PM" (one scheduled
// email via the capsule reminder; the server keeps nothing).
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Screen from '@/v5/Screen';
import D0 from '@/v5/screens/V5Asleep';
import M0 from '@/v5/screens/V5MAsleep';
import { podsInfo } from '@/lib/v5/hours';
import { isEmail, remindByEmail } from '@/lib/v5/capsule';

// the countdown becomes live text; the reminder's ruled line becomes the address field, its link the action
const live = (s) => ({
  ...s,
  html: s.html
    .replace('That\'s in <span style="color:#E9E9E7">1 hour 42 minutes</span>', '{{until}}')
    .replace(/<span style="((?:width:240px|flex-grow:1);border-bottom:1px solid [^"]+;height:1[46]px)"><\/span><a href="#" class="ul"/,
      '<span data-slot="mail" style="$1"></span><a href="#" data-act="remind" class="ul"')
});
const D = live(D0), M = live(M0);

function words(mins) {
  const h = Math.floor(mins / 60), m = mins % 60;
  const p = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  if (!h) return p(m, 'minute');
  return m ? `${p(h, 'hour')} ${p(m, 'minute')}` : p(h, 'hour');
}

// the next 22:00 India time (UTC+5:30) from now
function nextOpening(now = Date.now()) {
  const day = 86400_000, ist = 330 * 60_000;
  const midnight = Math.floor((now + ist) / day) * day - ist;
  let t = midnight + 22 * 3600_000;
  if (t <= now + 60_000) t += day;
  return new Date(t);
}

const NOTE = {
  sending: 'one moment…',
  ok: "we'll write at 10pm",
  unavailable: 'not switched on yet',
  fail: "didn't work. try again"
};

function MailField({ node, store, onEnter }) {
  const [v, setV] = useState(store.current.value);
  const { 'data-slot': _, ...attrs } = node.attribs || {};
  const p = attributesToProps(attrs);
  const st = store.current.status;
  const box = { ...p.style, display: 'flex', alignItems: 'flex-end', minWidth: 0, height: 'auto', paddingBottom: 2 };
  if (st && st !== 'bad') {
    return <span style={{ ...box, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', color: st === 'ok' ? '#E9E9E7' : '#F0A08F' }} role="status">{NOTE[st]}</span>;
  }
  return (
    <span style={box}>
      <input
        type="email"
        inputMode="email"
        autoComplete="email"
        aria-label="Email me at 10pm (optional)"
        placeholder="you@somewhere.com"
        aria-invalid={st === 'bad' || undefined}
        value={v}
        maxLength={254}
        onChange={(e) => { setV(e.target.value); store.current.value = e.target.value; }}
        onKeyDown={(e) => e.key === 'Enter' && onEnter(e)}
        className="nt-mail"
        style={{ width: '100%', minWidth: 0, background: 'transparent', border: 0, outline: 'none', padding: 0, margin: 0, font: 'inherit', letterSpacing: '.06em', textTransform: 'none', color: st === 'bad' ? '#F0A08F' : '#E9E9E7' }}
      />
    </span>
  );
}
const CSS = `.nt-mail::placeholder{color:#8A8A8F;opacity:.7}.nt-mail:focus-visible{outline:none;box-shadow:none}`;

export default function Asleep() {
  const [info, setInfo] = useState(null);
  const [status, setStatus] = useState(null); // null | bad | sending | ok | unavailable | fail
  const store = useRef({ value: '', status: null });
  store.current.status = status;
  useEffect(() => {
    const tick = () => setInfo(podsInfo());
    tick();
    const t = setInterval(tick, 60_000);
    return () => clearInterval(t);
  }, []);

  const remind = useCallback(async () => {
    if (store.current.status === 'sending' || store.current.status === 'ok') return;
    const mail = store.current.value.trim();
    if (!isEmail(mail)) { setStatus('bad'); return; }
    setStatus('sending');
    const r = await remindByEmail(mail, nextOpening(), 'pods');
    store.current.value = '';
    setStatus(r?.ok ? 'ok' : r?.error === 'unavailable' ? 'unavailable' : 'fail');
  }, []);

  // a failed try (or an address that looks off, shown in red) goes back to the plain field after a moment
  useEffect(() => {
    if (status !== 'fail' && status !== 'bad') return;
    const t = setTimeout(() => setStatus(null), status === 'fail' ? 3500 : 6000);
    return () => clearTimeout(t);
  }, [status]);

  const vals = useMemo(() => ({
    until: !info ? '' : info.open ? "They're open right now" : `That's in ${words(info.minsToOpen)}`
  }), [info]);
  const links = useMemo(() => ({ remind }), [remind]);
  const slots = useMemo(() => ({ mail: (node) => <MailField key={status || 'idle'} node={node} store={store} onEnter={remind} /> }), [status, remind]);
  return <Screen desktop={D} phone={M} vals={vals} slots={slots} links={links} css={CSS} />;
}
