'use client';
import Guard from '@/components/Guard';
import Chat from '@/components/Chat';

export default function Page() {
  return (
    <Guard>
      <Chat />
    </Guard>
  );
}
