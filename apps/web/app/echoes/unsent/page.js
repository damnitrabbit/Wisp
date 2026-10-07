'use client';
// An unsent letter: addressed to someone, put up on the wall, heard only (nobody can reply).
import Guard from '@/components/Guard';
import Writer from '../write/Writer';

export default function Page() {
  return (
    <Guard>
      <Writer kind="unsent" />
    </Guard>
  );
}
