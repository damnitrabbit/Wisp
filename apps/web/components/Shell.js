'use client';
import { useCallback, useEffect, useMemo } from 'react';
import { connect, useWisp, toast, retryNow } from '@/lib/wisp';
import { resumeAudio } from '@/lib/rtc';
import { bus } from '@/lib/wisp';
import Screen from '@/v5/Screen';
import Offline from '@/v5/screens/V5Offline';
import MOffline from '@/v5/screens/V5MOffline';
import Toasts from './Toasts';

export default function Shell({ children }) {
  const status = useWisp((s) => s.status);

  useEffect(() => {
    connect();
    // Browsers block audio until the page has been interacted with; the first tap unblocks it.
    const unlock = () => resumeAudio();
    window.addEventListener('pointerdown', unlock);
    const off = bus.on('audioBlocked', () =>
      toast({ key: 'audio', tag: '[ TAP TO HEAR ]', text: 'YOUR BROWSER PAUSED THE AUDIO. TAP ANYWHERE TO HEAR THE ROOM.' })
    );
    return () => {
      window.removeEventListener('pointerdown', unlock);
      off();
    };
  }, []);

  if (status === 'offline') return (<><OfflineScreen /><Toasts /></>);
  if (status === 'replaced') return <Replaced />;
  return (
    <>
      {children}
      {status === 'reconnecting' && <Reconnecting />}
      <Toasts />
    </>
  );
}

// Lost the signal: the socket keeps retrying on its own; TRY NOW forces an attempt.
function OfflineScreen() {
  useEffect(() => {
    const t = setInterval(() => retryNow(), 5000);
    return () => clearInterval(t);
  }, []);
  const retry = useCallback((e) => { e?.preventDefault?.(); retryNow(); }, []);
  const vals = useMemo(() => ({ retry }), [retry]);
  return <Screen desktop={Offline} phone={MOffline} vals={vals} />;
}

// The designed "reconnecting…" notice (V5 notices sheet): a kraft slip, bottom centre on desktop, under the header on phone.
const LOOP = 'M16 7a6.5 6.5 0 0 0-11.5 1M4 13a6.5 6.5 0 0 0 11.5-1M16 3v4h-4M4 17v-4h4';
function Reconnecting() {
  return (
    <div className="nt-recon" role="status" aria-live="polite">
      <svg className="nt-recon-spin" width="20" height="20" viewBox="0 0 20 20" aria-hidden="true">
        <path d={LOOP} fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span style={{ display: 'flex', flexDirection: 'column', gap: 1, minWidth: 0 }}>
        <span style={{ fontFamily: "'Nothing You Could Do', 'Caveat', cursive", fontSize: 19, lineHeight: 1.15, whiteSpace: 'nowrap' }}>reconnecting…</span>
        <span style={{ fontFamily: "'Courier Prime', 'Courier New', monospace", fontSize: 9.5, letterSpacing: '.12em', textTransform: 'uppercase', color: '#5F584E', whiteSpace: 'nowrap' }}>hold on, nothing is lost</span>
      </span>
      <style>{`
.nt-recon{position:fixed;z-index:9000;left:50%;bottom:28px;transform:translateX(-50%) rotate(-.6deg);display:flex;align-items:center;gap:12px;
  min-width:250px;height:66px;padding:0 18px 0 14px;background:#D8C6A4;color:#221E1A;box-shadow:0 10px 24px rgba(0,0,0,.45);
  clip-path:polygon(0 3%,8% 0,22% 4%,40% 1%,61% 3%,79% 0,100% 4%,99% 52%,100% 97%,82% 100%,63% 96%,41% 100%,20% 97%,3% 100%,1% 48%);
  animation:ntReconIn .6s cubic-bezier(.2,.8,.2,1) both}
.nt-recon-spin{flex-shrink:0;animation:ntSpin 2.4s linear infinite}
@keyframes ntSpin{to{transform:rotate(360deg)}}
@keyframes ntReconIn{from{opacity:0;transform:translate(-50%,14px) rotate(-.6deg)}to{opacity:1;transform:translateX(-50%) rotate(-.6deg)}}
@media (max-width:699px){.nt-recon{top:62px;bottom:auto}}
@media (prefers-reduced-motion:reduce){.nt-recon,.nt-recon-spin{animation:none}}`}</style>
    </div>
  );
}

// Opened in another tab: same paper language, no design board for it.
function Replaced() {
  return (
    <div style={{ minHeight: '100dvh', background: '#0D0D0E', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 22 }}>
      <div style={{ position: 'relative', maxWidth: 420, width: '100%', background: '#F7F2E7', color: '#221E1A', padding: '36px 34px 30px', transform: 'rotate(-1deg)', boxShadow: '0 18px 40px rgba(0,0,0,.55)' }}>
        <div style={{ fontFamily: "'Nothing You Could Do', 'Caveat', cursive", fontSize: 34, lineHeight: 1.2 }}>Open somewhere else.</div>
        <p style={{ fontFamily: "'Newsreader', Georgia, serif", fontSize: 18, lineHeight: 1.55, margin: '12px 0 22px' }}>
          This session was picked up in another tab. One tab at a time, so nobody gets two seats.
        </p>
        <button type="button" onClick={() => window.location.reload()}
          style={{ fontFamily: "'Courier Prime', monospace", fontWeight: 700, fontSize: 12, letterSpacing: '.16em', textTransform: 'uppercase', background: '#221E1A', color: '#F7F2E7', border: 0, padding: '14px 26px', cursor: 'pointer' }}>
          use this tab
        </button>
      </div>
    </div>
  );
}
