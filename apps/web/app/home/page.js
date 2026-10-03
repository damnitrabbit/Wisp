'use client';
// Home: pods closed (V5Home) or open (V5HomeOpen), with the live count, the real countdown,
// the capsule letter when one is due, and the one-time "keep this name?" note.
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { attributesToProps } from 'html-react-parser';
import Screen from '@/v5/Screen';
import Closed from '@/v5/screens/V5Home';
import MClosed from '@/v5/screens/V5MHome';
import Open from '@/v5/screens/V5HomeOpen';
import MOpen from '@/v5/screens/V5MHomeOpen';
import Remember from '@/v5/screens/V5Remember';
import MRemember from '@/v5/screens/V5MRemember';
import WelcomeBack from '@/v5/screens/V5WelcomeBack';
import MWelcomeBack from '@/v5/screens/V5MWelcomeBack';
import { useWisp, remember } from '@/lib/wisp';
import { podsInfo } from '@/lib/v5/hours';
import { isOnboarded, dueCapsule } from '@/lib/v5/prefs';

const ss = {
  get: (k) => { try { return sessionStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { sessionStorage.setItem(k, v); } catch {} }
};

// keep the designed element (its tag and inline style), swap its text. Names longer than the designed
// "quiet_otter" are set a little smaller so they still fit the slip on one line.
const DESIGNED = 11;
const keepEl = (text) => (node) => {
  const Tag = node.name;
  const { 'data-slot': _, ...attrs } = node.attribs || {};
  const props = attributesToProps(attrs);
  if (text.length > DESIGNED) {
    const k = DESIGNED / text.length;
    const px = parseFloat(props.style?.fontSize);
    props.style = { ...props.style, fontSize: px ? `${(px * k).toFixed(1)}px` : `${k.toFixed(3)}em` };
  }
  return <Tag {...props}>{text}</Tag>;
};

export default function HomePage() {
  const router = useRouter();
  const [ok, setOk] = useState(false);
  const [info, setInfo] = useState(null);
  const [letter, setLetter] = useState(false);
  const [note, setNote] = useState(null); // 'remember' | 'welcome' | null
  const online = useWisp((s) => s.lobby.online);
  const name = useWisp((s) => s.session?.name);

  useEffect(() => {
    if (!isOnboarded()) { router.replace('/?next=/home'); return; }
    setOk(true);
    const tick = () => { setInfo(podsInfo()); setLetter(Boolean(dueCapsule())); };
    tick();
    const t = setInterval(tick, 60_000);
    return () => clearInterval(t);
  }, [router]);

  // first home visit after arriving: ask once whether to keep the name; later visits with a kept name get a welcome back
  useEffect(() => {
    if (!ok || !name || note !== null) return;
    if (!remember.decided()) setNote('remember');
    else if (remember.on() && !ss.get('nt-welcomed')) { ss.set('nt-welcomed', '1'); setNote('welcome'); }
    else setNote('');
  }, [ok, name, note]);

  const keep = useCallback(() => { remember.accept(name); ss.set('nt-welcomed', '1'); setNote(''); }, [name]);
  const fresh = useCallback((e) => { e?.preventDefault?.(); remember.decline(); setNote(''); }, []);

  const open = info?.open ?? false;
  const label = info?.label || '';
  const vals = useMemo(() => ({ letter, noLetter: !letter, keep, fresh }), [letter, keep, fresh]);
  const slots = useMemo(() => ({
    here: online == null ? null : <span>{` · ${online} HERE`}</span>,
    // the closed-home status line; the remember note sits on that board, so while pods are open it says so instead
    pods: <span>{open ? 'PODS OPEN · UNTIL 2AM' : label ? `PODS OPEN AT 10PM · ${label}` : 'PODS OPEN AT 10PM'}</span>,
    name: keepEl(name || '')
  }), [online, label, name, open]);

  if (!ok || !info) return <div style={{ minHeight: '100dvh', background: '#0D0D0E' }} />;
  if (note === 'remember') return <Screen key="rem" desktop={Remember} phone={MRemember} vals={vals} slots={slots} />;
  if (note === 'welcome' && !open) return <Screen key="wb" desktop={WelcomeBack} phone={MWelcomeBack} vals={vals} slots={slots} />;
  return open
    ? <Screen key="open" desktop={Open} phone={MOpen} vals={vals} slots={slots} />
    : <Screen key="closed" desktop={Closed} phone={MClosed} vals={vals} slots={slots} />;
}
