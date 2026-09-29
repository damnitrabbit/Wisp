'use client';
import Link from 'next/link';
import Rabbit from './Rabbit';
import { useWisp } from '@/lib/wisp';

// Header (logo, crumb, online count) + a back row that always takes the same space,
// so pages never jump when a back link appears or disappears.
export default function TopBar({ crumb, showOnline = true, back, onBack }) {
  const online = useWisp((s) => s.lobby.online);
  return (
    <div className="topbar">
      <header>
        <div className="left">
          <Link href="/" className="brand" aria-label="NoTrace home">
            <Rabbit />
            <span className="word">N0TRACE</span>
          </Link>
          {crumb && <span className="crumb">{crumb}</span>}
        </div>
        {showOnline && (
          <span className="online" aria-live="off">
            <span className="dot" />
            {online === null ? '—' : online} ONLINE
          </span>
        )}
      </header>
      <nav aria-label="Back">
        {back && onBack && (
          <button type="button" className="back" onClick={onBack}>
            {back.label}
          </button>
        )}
        {back && !onBack && (
          <Link className="back" href={back.href}>
            {back.label}
          </Link>
        )}
      </nav>
    </div>
  );
}
