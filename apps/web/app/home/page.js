'use client';
import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5HomeOpen';
import M from '@/v5/screens/V5MHomeOpen';

export default function HomePage() {
  return <Screen desktop={D} phone={M} />;
}
