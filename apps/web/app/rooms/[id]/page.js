'use client';
import { use } from 'react';
import { CHANNEL_BY_ID } from '@wisp/shared';
import Guard from '@/components/Guard';
import Room from '@/components/Room';
import NotFound from '@/components/NotFound';

export default function Page({ params }) {
  const { id } = use(params);
  const channel = CHANNEL_BY_ID.get(id);
  if (!channel) return <NotFound crumb={`/ROOMS/${String(id).toUpperCase()}`} />;
  return (
    <Guard>
      <Room channel={channel} />
    </Guard>
  );
}
