'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Onboarding from '@/components/Onboarding';
import Lobby from '@/components/Lobby';
import { onboarding } from '@/lib/wisp';

export default function Home() {
  // Server render (and first paint) is the boot screen; returning visitors switch to the lobby.
  const [ready, setReady] = useState(false);
  const [next, setNext] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const n = new URLSearchParams(window.location.search).get('next');
    setNext(n && n.startsWith('/') && !n.startsWith('//') ? n : null);
    setReady(onboarding.done());
  }, []);

  if (!ready) {
    return (
      <Onboarding
        next={next}
        onDone={(to) => {
          onboarding.finish();
          if (to) router.push(to);
          else setReady(true);
        }}
      />
    );
  }
  return <Lobby />;
}
