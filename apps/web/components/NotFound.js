import Link from 'next/link';
import TopBar from './TopBar';
import Footer from './Footer';

export default function NotFound({ crumb = '/404', room = true }) {
  return (
    <div className="page">
      <TopBar crumb={crumb} back={{ label: '← LOBBY', href: '/' }} />
      <main className="main" style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
        <div className="big404">404</div>
        <h1 className="h-40">{room ? 'NO ROOM HERE.' : 'NOTHING HERE.'}<span className="cursor">_</span></h1>
        <p className="p-16" style={{ maxWidth: 680 }}>
          {room
            ? "THIS ROOM DOESN'T EXIST. THE LINK MIGHT BE WRONG, OR SOMEONE MADE IT UP. THERE ARE 25 REAL ONES."
            : "THIS PAGE DOESN'T EXIST. NOTHING IS KEPT HERE, SO MAYBE IT NEVER DID."}
        </p>
        <Link href={room ? '/rooms' : '/'} className="btn" style={{ alignSelf: 'flex-start', height: 52, padding: '0 24px' }}>
          {room ? '[ SEE ALL ROOMS → ]' : '[ BACK TO THE LOBBY → ]'}
        </Link>
      </main>
      <Footer />
    </div>
  );
}
