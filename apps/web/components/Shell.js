'use client';
import { useEffect, useState } from 'react';
import { connect, useWisp, toast, dismiss, retryNow } from '@/lib/wisp';
import { resumeAudio } from '@/lib/rtc';
import { bus } from '@/lib/wisp';
import Toasts from './Toasts';
import TopBar from './TopBar';
import Footer from './Footer';
import Rabbit from './Rabbit';

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

  useEffect(() => {
    if (status === 'reconnecting') {
      toast({
        key: 'reconnecting',
        kind: 'solid',
        pulse: true,
        sticky: true,
        tag: '[ RECONNECTING ]',
        text: 'LOST THE SERVER. TRYING AGAIN… IF THE DROP LASTS MORE THAN 30 SECONDS, ROOMS AND CHATS START FRESH.'
      });
    } else dismiss('reconnecting');
  }, [status]);

  if (status === 'offline') return (<><Offline /><Toasts /></>);
  if (status === 'replaced') return <Replaced />;
  return (
    <>
      {children}
      <Toasts />
    </>
  );
}

function Offline() {
  const attempt = useWisp((s) => s.attempt);
  const [left, setLeft] = useState(5);
  useEffect(() => {
    const t = setInterval(() => {
      setLeft((n) => {
        if (n <= 1) {
          retryNow();
          return 5;
        }
        return n - 1;
      });
    }, 1000);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="page">
      <TopBar showOnline={false} />
      <main role="alert" className="center">
        <div aria-hidden="true"><Rabbit className="rabbit-xl" mode="sleep" /></div>
        <h1>LOST THE SIGNAL.<span className="cursor">_</span></h1>
        <p>WE CAN&apos;T REACH THE NOTRACE SERVER RIGHT NOW. IT MIGHT BE RESTARTING, OR YOUR CONNECTION DROPPED. WHEN IT COMES BACK, EVERY ROOM AND CHAT STARTS FRESH. NOTHING WAS SAVED, SO NOTHING WAS LOST.</p>
        <div className="retry">
          <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span className="dot pulse" />RETRYING IN 00:0{left}</span>
          <span>ATTEMPT {Math.max(1, attempt)}</span>
        </div>
        <button type="button" className="btn solid" style={{ width: 240, height: 52 }} onClick={() => { setLeft(5); retryNow(); }}>
          [ TRY NOW ]
        </button>
      </main>
      <Footer />
    </div>
  );
}

function Replaced() {
  return (
    <div className="page">
      <TopBar showOnline={false} />
      <main className="center">
        <h1>OPEN SOMEWHERE ELSE.</h1>
        <p>THIS SESSION WAS PICKED UP IN ANOTHER TAB. ONE TAB AT A TIME, SO NOBODY GETS TWO SEATS.</p>
        <button type="button" className="btn solid" style={{ width: 240, height: 52 }} onClick={() => window.location.reload()}>
          [ USE THIS TAB ]
        </button>
      </main>
      <Footer />
    </div>
  );
}
