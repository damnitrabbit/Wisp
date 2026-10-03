'use client';
// Arrival: Boot (tap anywhere) → Story → Age gate. Returning visitors go straight to /home (or ?next=).
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Screen from '@/v5/Screen';
import Boot from '@/v5/screens/V5Boot';
import MBoot from '@/v5/screens/V5MBoot';
import Story from '@/v5/screens/V5Story';
import MStory from '@/v5/screens/V5MStory';
import Age from '@/v5/screens/V5Age';
import MAge from '@/v5/screens/V5MAge';
import { isOnboarded, markOnboarded, safeNext } from '@/lib/v5/prefs';

export default function Arrival() {
  const router = useRouter();
  const [step, setStep] = useState(null); // null until we know who this is
  const [next, setNext] = useState(null);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const n = safeNext(q.get('next'));
    setNext(n);
    if (isOnboarded()) { router.replace(n || '/home'); return; }
    setStep(q.get('age') === '1' ? 'age' : 'boot');
  }, [router]);

  useEffect(() => { if (step) window.scrollTo(0, 0); }, [step]);

  const toStory = useCallback(() => setStep('story'), []);
  const toAge = useCallback(() => setStep('age'), []);
  const bootLinks = useMemo(() => ({ Story: toStory }), [toStory]);
  const storyLinks = useMemo(() => ({ Age: toAge }), [toAge]);
  const ageVals = useMemo(() => ({
    adult: (e) => {
      markOnboarded();
      if (next) { e.preventDefault(); router.push(next); }
    }
  }), [next, router]);
  const ageLinks = useMemo(() => ({ NotYet: '/not-yet' + (next ? `?next=${encodeURIComponent(next)}` : '') }), [next]);

  if (!step) return <div style={{ minHeight: '100dvh', background: '#0D0D0E' }} />;
  if (step === 'boot') return <Screen key="boot" desktop={Boot} phone={MBoot} links={bootLinks} />;
  if (step === 'story') return <Screen key="story" desktop={Story} phone={MStory} links={storyLinks} />;
  return <Screen key="age" desktop={Age} phone={MAge} vals={ageVals} links={ageLinks} />;
}
