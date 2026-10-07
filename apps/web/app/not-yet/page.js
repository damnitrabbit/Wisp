'use client';
import { useEffect, useMemo, useState } from 'react';
import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5NotYet';
import M from '@/v5/screens/V5MNotYet';
import { safeNext } from '@/lib/v5/prefs';

export default function NotYet() {
  const [next, setNext] = useState(null);
  useEffect(() => { setNext(safeNext(new URLSearchParams(window.location.search).get('next'))); }, []);
  // back goes to the age gate (not the boot screen); home is gated too, so the logo leads there as well
  const links = useMemo(() => {
    const age = '/?age=1' + (next ? `&next=${encodeURIComponent(next)}` : '');
    return { Age: age, Home: age };
  }, [next]);
  return <Screen desktop={D} phone={M} links={links} />;
}
