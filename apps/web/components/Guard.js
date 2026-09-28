'use client';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { onboarding } from '@/lib/wisp';

// Rooms and chat are behind the age gate. A deep link goes through onboarding first, then lands here.
export default function Guard({ children }) {
  const [ok, setOk] = useState(false);
  const router = useRouter();
  const path = usePathname();
  useEffect(() => {
    if (onboarding.done()) setOk(true);
    else router.replace(`/?next=${encodeURIComponent(path)}`);
  }, [router, path]);
  return ok ? children : <div className="page" />;
}
