'use client';
import Link from 'next/link';
import { CHANNELS } from '@wisp/shared';
import TopBar from '@/components/TopBar';
import Footer from '@/components/Footer';
import { useWisp } from '@/lib/wisp';

function Rooms() {
  const counts = useWisp((s) => s.lobby.channels);
  const byId = new Map(counts.map((c) => [c.id, c.count]));
  // Busiest first; ties keep the catalog order so the grid doesn't shuffle.
  const list = CHANNELS.map((c, i) => ({ ...c, i, n: byId.get(c.id) ?? 0 })).sort((a, b) => b.n - a.n || a.i - b.i);

  return (
    <div className="page">
      <TopBar crumb="/ROOMS" back={{ label: '← LOBBY', href: '/' }} />
      <main className="main" style={{ paddingTop: 0, display: 'flex', flexDirection: 'column', gap: 28 }}>
        <div className="rooms-head">
          <h1>25 THEMED ROOMS, BUSIEST FIRST. PICK ONE AND WALK IN.</h1>
          <dl className="kv">
            <dt>YOU JOIN AS</dt><dd>A LISTENER. MIC OFF.</dd>
            <dt>WANT TO TALK?</dt><dd>RAISE YOUR HAND. A MOD DECIDES.</dd>
            <dt>EMPTY ROOM?</dt><dd>YOU + THE NEXT PERSON BECOME ITS MODS.</dd>
          </dl>
        </div>
        <div className="grid5">
          {list.map((c, idx) => {
            const no = String(idx + 1).padStart(2, '0');
            const count = String(c.n).padStart(2, '0');
            const label = `${c.name}, ${c.n} of 10 in room`;
            if (c.n >= 10) {
              return (
                <div key={c.id} className="ch full" aria-label={label}>
                  <div className="r1"><span className="no">{no}</span><span className="st">[ FULL ]</span></div>
                  <div className="r2"><span className="name">{c.name}</span><span className="blurb nc">{c.blurb}</span></div>
                  <div className="r3"><span className="meter">{'■'.repeat(10)}</span><span>{count}/10</span></div>
                </div>
              );
            }
            const status = c.n === 0 ? 'EMPTY · START IT' : c.n === 9 ? '1 SEAT LEFT' : 'LIVE';
            return (
              <Link key={c.id} href={`/rooms/${c.id}`} className="ch" aria-label={label}>
                <div className="r1"><span className="no">{no}</span><span className="st" style={{ color: c.n === 0 ? 'var(--fg-2)' : 'var(--fg)' }}>{status}</span></div>
                <div className="r2"><span className="name">{c.name}</span><span className="blurb nc">{c.blurb}</span></div>
                <div className="r3">
                  <span className="meter"><span className="on">{'■'.repeat(c.n)}</span><span className="off">{'■'.repeat(10 - c.n)}</span></span>
                  <span className="dim">{count}/10</span>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
      <Footer />
    </div>
  );
}

// The list is public (and crawlable); walking into a room goes through the age gate.
export default function Page() {
  return <Rooms />;
}
