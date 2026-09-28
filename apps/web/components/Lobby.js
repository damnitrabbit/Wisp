'use client';
import { useEffect, useState } from 'react';
import TopBar from './TopBar';
import Footer from './Footer';
import { ModeCard } from './Onboarding';
import { useWisp, remember } from '@/lib/wisp';

export default function Lobby() {
  const { lobby, session } = useWisp((s) => s);
  const [askRemember, setAskRemember] = useState(false);
  useEffect(() => setAskRemember(!remember.decided()), []);

  const live = lobby.channels.filter((c) => c.count > 0).length;

  return (
    <div className="page">
      <TopBar />
      <main className="main lobby">
        <div className="lead">
          <div className="copy">
            <p>WISP IS A PLACE TO TALK TO STRANGERS. NO ACCOUNTS. NO HISTORY. A NEW NAME EVERY TIME YOU JOIN.</p>
            <p>WHEN YOU LEAVE, THE SERVER FORGETS YOU. THERE IS NOTHING TO DELETE, BECAUSE NOTHING WAS KEPT.</p>
          </div>
          <dl className="kv" style={{ gridTemplateColumns: '180px 1fr', rowGap: 20, fontSize: 14 }}>
            <dt>ON WISP NOW</dt>
            <dd style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="dot" />
              {lobby.online ?? '—'} {lobby.online === 1 ? 'PERSON (YOU)' : 'PEOPLE'}
            </dd>
            <dt>YOUR NAME</dt>
            <dd>
              {session ? <span className="nc">{session.name}</span> : 'GIVEN TO YOU WHEN YOU JOIN.'}
              <br />
              <span className="dim">{remember.on() ? 'KEPT ON THIS DEVICE.' : 'NEW EVERY TIME.'}</span>
            </dd>
            <dt>STORAGE</dt>
            <dd>NONE. MEMORY ONLY.</dd>
          </dl>
        </div>
        <div className="pick">
          <div className="eyebrow">CHOOSE HOW TO ENTER</div>
          <ModeCard href="/rooms" no="01" meta={`${live} ROOM${live === 1 ? '' : 'S'} LIVE`} title="VOICE ROOMS"
            text={<>25 THEMED ROOMS. UP TO 10 PEOPLE EACH.<br />JOIN AS A LISTENER. RAISE YOUR HAND TO SPEAK.</>} />
          <ModeCard href="/chat" no="02" meta={lobby.waiting ? `${lobby.waiting} WAITING` : 'NO FILTERS'} title="1:1 CHAT"
            text={<>ONE RANDOM STRANGER. TEXT FIRST.<br />VOICE ONLY IF YOU BOTH SAY YES.</>} />
        </div>
      </main>
      <Footer />
      {askRemember && (
        <div role="dialog" aria-label="Remember your name" className="consent">
          <div className="t">
            <span style={{ fontSize: 14 }}>KEEP THE SAME NAME ON THIS DEVICE?</span>
            <span className="dim" style={{ fontSize: 12, lineHeight: 1.6 }}>
              WE&apos;LL REUSE YOUR GENERATED NAME ON FUTURE VISITS INSTEAD OF A NEW ONE EACH TIME. IT&apos;S SAVED IN YOUR BROWSER ONLY. CLEAR YOUR BROWSER DATA TO FORGET IT. NOTHING ELSE IS TRACKED.
            </span>
          </div>
          <div className="actions">
            <button type="button" className="btn solid" onClick={() => { remember.accept(session?.name); setAskRemember(false); }}>
              [ Y ] REMEMBER ME
            </button>
            <button type="button" className="btn" onClick={() => { remember.decline(); setAskRemember(false); }}>
              [ N ] NO THANKS
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
