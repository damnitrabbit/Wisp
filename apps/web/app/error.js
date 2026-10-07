'use client';
// Something broke while drawing a page: the designed "something broke" board, with a working "try again".
import { useEffect, useMemo } from 'react';
import Screen from '@/v5/Screen';
import D0 from '@/v5/screens/V5SomethingBroke';
import M0 from '@/v5/screens/V5MSomethingBroke';

const act = (s) => ({ ...s, html: s.html.replace('<a href="#" class="chip inkc"', '<a href="#" data-act="retry" class="chip inkc"') });
const D = act(D0), M = act(M0);

export default function Error({ reset }) {
  // the board says "trying again on its own": it does, once, after a breath
  useEffect(() => { const t = setTimeout(() => reset(), 8000); return () => clearTimeout(t); }, [reset]);
  const links = useMemo(() => ({ retry: () => reset() }), [reset]);
  return <Screen desktop={D} phone={M} links={links} />;
}
