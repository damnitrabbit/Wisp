'use client';
import Guard from '@/components/Guard';
import Echoes from '@/components/Echoes';

export default function Page() {
  return (
    <Guard>
      <Echoes />
    </Guard>
  );
}
