'use client';
import Guard from '@/components/Guard';
import Writer from './Writer';

export default function Page() {
  return (
    <Guard>
      <Writer kind="echo" />
    </Guard>
  );
}
