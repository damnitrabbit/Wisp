import { CHANNEL_BY_ID, CHANNELS } from '@wisp/shared';

export function generateStaticParams() {
  return CHANNELS.map((c) => ({ id: c.id }));
}

export async function generateMetadata({ params }) {
  const { id } = await params;
  const c = CHANNEL_BY_ID.get(id);
  if (!c) return { title: 'Room not found', robots: { index: false } };
  return {
    title: `${c.name} · anonymous voice chat room`,
    description: `${c.blurb} An anonymous voice chat room for up to 10 strangers on Wisp. No sign-up, nothing recorded.`,
    alternates: { canonical: `/rooms/${c.id}` }
  };
}

export default function Layout({ children }) {
  return children;
}
