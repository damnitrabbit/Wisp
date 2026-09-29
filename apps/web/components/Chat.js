'use client';
import { useCallback, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import TopBar from './TopBar';
import Footer from './Footer';
import Rabbit from './Rabbit';
import Modal from './Modal';
import MicModals from './MicModals';
import { emit, on, bus, toast, syncClock, useWisp } from '@/lib/wisp';
import { useMicFlow, micTrack, closeMic } from '@/lib/mic';
import { usePairCall } from '@/lib/call';
import { useNow, mmss, hhmmss } from '@/lib/time';

let msgId = 0;
const sysMsg = (text) => ({ id: `s${++msgId}`, from: 'sys', text });

export default function Chat() {
  const session = useWisp((s) => s.session);
  const [phase, setPhase] = useState('idle'); // idle | searching | chat | blocked
  const [since, setSince] = useState(null); // when we started looking
  const [pair, setPair] = useState(null); // { pairId, partner, startedAt }
  const [msgs, setMsgs] = useState([]);
  const [voice, setVoice] = useState('off'); // off | asked | incoming | on
  const [incoming, setIncoming] = useState(null);
  const [polite, setPolite] = useState(true);
  const [track, setTrack] = useState(null);
  const [muted, setMuted] = useState(false);
  const [away, setAway] = useState(false);
  const [typing, setTyping] = useState(false);
  const [draft, setDraft] = useState('');
  const mic = useMicFlow();
  const escAt = useRef(0);
  const typingTimer = useRef(null);
  const sentTyping = useRef(0);

  const resetChat = () => {
    setPair(null);
    setMsgs([]);
    setVoice('off');
    setIncoming(null);
    setAway(false);
    setTyping(false);
    setMuted(false);
    setTrack(null);
    closeMic();
  };

  const startLooking = useCallback(async () => {
    const r = await emit('pair:join');
    if (r.error === 'blocked') return setPhase('blocked');
    if (r.error) return;
    if (!r.pairId) {
      setSince(Date.now());
      setPhase((p) => (p === 'chat' ? p : 'searching'));
    }
  }, []);

  // ---------- server events ----------

  useEffect(() => {
    document.title = '1:1 chat · NoTrace';
    const offs = [
      on('pair:waiting', () => {
        setPhase('searching');
        setSince((s) => s ?? Date.now());
      }),
      on('pair:matched', (p) => {
        syncClock(p.serverNow);
        resetChat();
        setPair(p);
        setPhase('chat');
        setSince(null);
      }),
      on('pair:message', (m) => {
        setTyping(false);
        setMsgs((l) => [...l, { id: m.id, from: 'them', text: m.text }]);
      }),
      on('pair:typing', ({ on: t }) => {
        setTyping(t);
        clearTimeout(typingTimer.current);
        if (t) typingTimer.current = setTimeout(() => setTyping(false), 5000);
      }),
      on('pair:partnerLeft', (p) => {
        resetChat();
        setPhase('searching');
        setSince(Date.now());
        toast({ kind: 'solid', tag: '[ STRANGER LEFT ]', text: <><span className="nc">{p.name}</span> {p.reason === 'skip' ? 'SKIPPED' : 'LEFT'}. THE CHAT IS GONE. YOU&apos;RE BACK IN LINE AUTOMATICALLY.</> });
      }),
      on('pair:partnerAway', () => setAway(true)),
      on('pair:partnerBack', () => setAway(false)),
      on('pair:blocked', () => {
        resetChat();
        setPhase('blocked');
      }),
      on('pair:voiceRequested', (p) => {
        syncClock(p.serverNow);
        setIncoming(p);
        setVoice('incoming');
      }),
      on('pair:voiceWithdrawn', () => {
        setIncoming(null);
        setVoice('off');
      }),
      on('pair:voiceDeclined', (p) => {
        setVoice('off');
        setMsgs((l) => [...l, sysMsg(p.reason === 'expired' ? 'NO ANSWER, SO THE VOICE REQUEST EXPIRED. YOU CAN ASK AGAIN.' : 'THEY WOULD RATHER KEEP IT TEXT FOR NOW.')]);
        closeMic();
        setTrack(null);
      }),
      on('pair:voiceStarted', ({ polite: pol }) => {
        setPolite(pol);
        setIncoming(null);
        setVoice('on');
        setMsgs((l) => [...l, sysMsg('CALL STARTED. TEXT STILL WORKS. END THE CALL ANYTIME TO GO BACK TO TEXT ONLY.')]);
      }),
      on('pair:voiceEnded', () => {
        setVoice('off');
        setMuted(false);
        closeMic();
        setTrack(null);
        setMsgs((l) => [...l, sysMsg('CALL ENDED. YOU’RE BACK TO TEXT ONLY.')]);
      }),
      bus.on('session', ({ fresh }) => {
        // The server forgot us (long drop): whatever chat we had is gone.
        setPhase((p) => {
          if (fresh && (p === 'chat' || p === 'searching')) {
            if (p === 'chat') toast({ kind: 'solid', tag: '[ CHAT LOST ]', text: 'THE CONNECTION DROPPED, SO THAT CHAT IS GONE. PICK UP WITH SOMEONE NEW.' });
            resetChat();
            startLooking();
            return 'searching';
          }
          return p;
        });
      })
    ];
    return () => offs.forEach((f) => f());
  }, [startLooking]);

  // Came back to the page mid-chat (resumed session)?
  useEffect(() => {
    if (session?.pair && phase === 'idle') {
      setPair(session.pair);
      setPhase('chat');
    } else if (session?.queued && phase === 'idle') {
      setPhase('searching');
      setSince(Date.now());
    }
  }, [session]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(
    () => () => {
      emit('pair:leave');
      closeMic();
    },
    []
  );

  const call = usePairCall({ active: voice === 'on', polite, track, muted });

  // ---------- actions ----------

  const skip = async () => {
    await emit('pair:skip');
    resetChat();
    setPhase('searching');
    setSince(Date.now());
  };
  const report = async () => {
    await emit('pair:report');
    resetChat();
    setPhase('searching');
    setSince(Date.now());
    toast({ kind: 'solid', tag: '[ REPORTED ]', text: 'THANKS. THAT CHAT IS OVER. FINDING SOMEONE NEW.' });
  };
  const askVoice = async () => {
    if (voice !== 'off') return;
    const ok = await mic.ask();
    if (!ok) return;
    setTrack(micTrack());
    const r = await emit('pair:voiceRequest');
    if (r.ok) setVoice('asked');
  };
  const answerVoice = async (yes) => {
    if (!yes) {
      setIncoming(null);
      setVoice('off');
      return emit('pair:voiceDecline');
    }
    const ok = await mic.ask();
    if (!ok) {
      setIncoming(null);
      setVoice('off');
      return emit('pair:voiceDecline');
    }
    setTrack(micTrack());
    emit('pair:voiceAccept');
  };
  const endCall = () => emit('pair:voiceEnd');

  const sendMsg = async (e) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text) return;
    const r = await emit('pair:message', { text });
    if (r.ok) {
      setMsgs((l) => [...l, { id: r.id, from: 'me', text: text.replace(/\s+/g, ' ') }]);
      setDraft('');
      sentTyping.current = 0;
    } else if (r.error === 'slow') toast({ key: 'slow', tag: '[ SLOW DOWN ]', text: 'ONE MESSAGE AT A TIME. TRY AGAIN IN A SECOND.' });
    else if (r.error === 'too_long') toast({ key: 'long', tag: '[ TOO LONG ]', text: 'KEEP IT UNDER 500 CHARACTERS.' });
  };
  const onDraft = (v) => {
    setDraft(v);
    const now = Date.now();
    if (v && now - sentTyping.current > 2500) {
      sentTyping.current = now;
      emit('pair:typing', { on: true });
    }
  };

  // keys: Esc Esc skip, S skip, V voice, M mute, E end call
  useEffect(() => {
    const onKey = (e) => {
      if (phase !== 'chat' || mic.modal || incoming) return;
      const inInput = e.target.tagName === 'INPUT';
      if (e.key === 'Escape') {
        if (Date.now() - escAt.current < 1500) {
          escAt.current = 0;
          skip();
        } else {
          escAt.current = Date.now();
          toast({ key: 'esc', tag: '[ SKIP? ]', text: 'PRESS ESC AGAIN TO SKIP TO SOMEONE NEW.', ttl: 1500 });
        }
        return;
      }
      if (inInput || e.metaKey || e.ctrlKey) return;
      const k = e.key.toLowerCase();
      if (k === 's') skip();
      if (k === 'v') askVoice();
      if (k === 'm' && voice === 'on') setMuted((m) => !m);
      if (k === 'e' && voice === 'on') endCall();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  // ---------- views ----------

  if (phase === 'blocked') return <Blocked />;
  if (phase === 'idle') return <Idle onStart={startLooking} />;
  if (phase === 'searching') return <Searching name={session?.name} since={since} onCancel={() => { emit('pair:leave'); setPhase('idle'); }} />;

  return (
    <ChatView
      pair={pair}
      me={session?.name}
      msgs={msgs}
      typing={typing}
      away={away}
      voice={voice}
      call={call}
      muted={muted}
      draft={draft}
      onDraft={onDraft}
      onSend={sendMsg}
      onSkip={skip}
      onReport={report}
      onAskVoice={askVoice}
      onEndCall={endCall}
      onMute={() => setMuted((m) => !m)}
      overlays={
        <>
          {incoming && voice === 'incoming' && <VoiceConsent from={incoming} onAnswer={answerVoice} />}
          <MicModals flow={mic} where="call" />
        </>
      }
    />
  );
}

function Idle({ onStart }) {
  return (
    <div className="page">
      <TopBar crumb="/CHAT" back={{ label: '← LOBBY', href: '/' }} />
      <main className="main split" style={{ paddingTop: 20 }}>
        <div className="lead" style={{ width: 600 }}>
          <div className="eyebrow">1:1 CHAT</div>
          <h1 className="h-40">ONE STRANGER. PICKED AT RANDOM. NO FILTERS.<span className="cursor">_</span></h1>
          <p className="p-16">YOU&apos;LL BE MATCHED WITH WHOEVER HAS BEEN WAITING LONGEST. IT STARTS AS TEXT. IF IT&apos;S NOT CLICKING, SKIP AND MEET SOMEONE ELSE.</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 8 }}>
            <button type="button" className="btn solid tall" style={{ alignSelf: 'flex-start', gap: 40, padding: '0 24px' }} onClick={onStart}>
              <span>[ START CHATTING ]</span><span>→</span>
            </button>
            <Link href="/rooms" className="dim" style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', height: 44, fontSize: 12 }}>PREFER VOICE ROOMS? →</Link>
          </div>
        </div>
        <div className="side box" style={{ display: 'flex', flexDirection: 'column', gap: 24, padding: '36px 40px' }}>
          <div className="dim" style={{ fontSize: 12 }}>HOW A 1:1 WORKS</div>
          <dl className="kv" style={{ gridTemplateColumns: '130px 1fr', rowGap: 18, lineHeight: 1.55 }}>
            <dt>YOUR NAME</dt><dd>NEW FOR THIS VISIT, LIKE <span className="nc">quiet_otter_42</span></dd>
            <dt>MESSAGES</dt><dd>GO ONLY TO THEM. NEVER SAVED.</dd>
            <dt>VOICE</dt><dd>EITHER OF YOU CAN ASK. IT ONLY STARTS IF THE OTHER SAYS YES.</dd>
            <dt>SKIP</dt><dd>[ S ] OR ESC TWICE. YOU&apos;RE MATCHED WITH SOMEONE NEW.</dd>
            <dt>REPORT</dt><dd>ENDS THE CHAT RIGHT AWAY.</dd>
          </dl>
        </div>
      </main>
      <Footer />
    </div>
  );
}

function Searching({ name, since, onCancel }) {
  const now = useNow(true, 1000);
  const slow = since && Date.now() - since > 30_000;
  void now;
  return (
    <div className="page fixed">
      <TopBar crumb="/CHAT" back={{ label: '← CANCEL' }} onBack={onCancel} />
      <main role="status" aria-live="polite" className="match">
        <div aria-hidden="true"><Rabbit className="rabbit-md" mode="look" label="Rabbit looking for someone" /></div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
          <h1>{slow ? 'STILL LOOKING' : 'LOOKING FOR A STRANGER'}<span className="cursor">_</span></h1>
          <p className="dim" style={{ fontSize: 14 }}>
            {slow ? 'IT’S TAKING LONGER THAN USUAL. YOU’RE FIRST IN LINE FOR THE NEXT PERSON.' : 'WHOEVER HAS BEEN WAITING LONGEST GETS YOU. THIS USUALLY TAKES A MOMENT.'}
          </p>
        </div>
        <dl className="kv">
          <dt>YOU ARE</dt><dd className="nc">{name ?? '—'}</dd>
          <dt>STARTS AS</dt><dd>TEXT</dd>
          <dt>KEPT</dt><dd>NOTHING</dd>
        </dl>
        <div style={{ minHeight: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {slow && (
            <div role="status" className="quiet">
              <span style={{ color: 'var(--soft)' }}>IT&apos;S QUIET RIGHT NOW. KEEP WAITING, OR:</span>
              <Link href="/rooms">TRY A VOICE ROOM →</Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function ChatView({ pair, me, msgs, typing, away, voice, call, muted, draft, onDraft, onSend, onSkip, onReport, onAskVoice, onEndCall, onMute, overlays }) {
  const now = useNow(true, 1000);
  const thread = useRef(null);
  useEffect(() => {
    const el = thread.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [msgs, typing, voice]);
  const partner = pair?.partner?.name ?? '…';
  const live = voice === 'on';
  const [narrow, setNarrow] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 760px)');
    const f = () => setNarrow(mq.matches);
    f();
    mq.addEventListener('change', f);
    return () => mq.removeEventListener('change', f);
  }, []);

  return (
    <div className="page fixed chat-page">
      <TopBar crumb="/CHAT" back={{ label: '← LEAVE CHAT', href: '/' }} />
      <div className="chatwrap">
        <aside aria-label="Session" className="session">
          <p className="lead">YOU&apos;RE TALKING TO SOMEONE YOU WILL NEVER MEET.</p>
          <dl className="kv" style={{ rowGap: 16 }}>
            <dt>STRANGER</dt><dd className="nc">{partner}{away && <span className="dim3"> · reconnecting…</span>}</dd>
            <dt className="opt">YOU</dt><dd className="nc opt">{me}</dd>
            <dt>MATCHED</dt><dd>{pair ? hhmmss(now - pair.startedAt) : '—'} AGO</dd>
            <dt>MODE</dt><dd style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span className={`dot ${live ? 'pulse' : ''}`} />{live ? 'TEXT + VOICE' : 'TEXT'}</dd>
            <dt className="opt">KEPT</dt><dd className="opt">NOTHING</dd>
          </dl>
          <div className="m-chatbtns">
            <button type="button" className="btn" onClick={onSkip}>SKIP</button>
            <button type="button" className="btn dim" onClick={onReport}>REPORT</button>
            {live ? (
              <button type="button" className="btn solid" onClick={onEndCall}>END CALL</button>
            ) : voice === 'asked' ? (
              <button type="button" className="btn dash" disabled>ASKED…</button>
            ) : (
              <button type="button" className="btn" onClick={onAskVoice}>VOICE</button>
            )}
          </div>
          <div className="sidebtns">
            <button type="button" className="sidebtn" onClick={onSkip}><span>[ S ] SKIP</span><span className="sub">MEET SOMEONE NEW →</span></button>
            <button type="button" className="sidebtn" style={{ color: 'var(--fg-2)' }} onClick={onReport}><span>[ ! ] REPORT</span><span className="sub">ENDS THIS NOW</span></button>
          </div>
        </aside>

        <main className="convo">
          {live && (
            <section aria-label="Voice call" className="call">
              <div className="top">
                <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span className="dot pulse" />
                  VOICE · {call.state === 'live' ? 'LIVE' : call.state === 'failed' ? 'COULDN’T CONNECT' : 'CONNECTING…'}
                </span>
                <span className="dim3">DIRECT CONNECTION</span>
              </div>
              <div className="peers">
                <div className="peer"><span className="nc">{partner}</span>{call.speaking.has('partner') ? <Bars /> : <IdleDots />}</div>
                <div className="peer"><span>YOU{muted ? ' · MUTED' : ''}</span>{call.speaking.has('me') && !muted ? <Bars /> : <IdleDots />}</div>
              </div>
              {call.state === 'failed' && (
                <p className="dim" style={{ fontSize: 12, lineHeight: 1.6 }}>YOUR NETWORKS COULDN&apos;T REACH EACH OTHER DIRECTLY. TEXT STILL WORKS. YOU CAN END THE CALL AND TRY AGAIN LATER.</p>
              )}
              <div className="btns">
                <button type="button" className="btn" onClick={onMute}>{muted ? (narrow ? 'UNMUTE' : '[ M ] UNMUTE') : narrow ? 'MUTE' : '[ M ] MUTE'}</button>
                <button type="button" className="btn solid" onClick={onEndCall}>{narrow ? 'END CALL' : '[ E ] END CALL — BACK TO TEXT'}</button>
              </div>
            </section>
          )}
          <div role="log" aria-label="Conversation" className="thread" ref={thread}>
            <div className="line first">
              <span className="who">MATCHED</span>
              <span className="txt">SAY HI, AND MAYBE ASK WHERE THEY&apos;RE CHATTING FROM.</span>
            </div>
            {msgs.map((m) =>
              m.from === 'sys' ? (
                <div key={m.id} className="line sysl"><span>VOICE</span><span>{m.text}</span></div>
              ) : m.from === 'me' ? (
                <div key={m.id} className="line me"><span className="who">YOU</span><span className="txt nc">{m.text}</span></div>
              ) : (
                <div key={m.id} className="line"><span className="who nc">{partner}</span><span className="txt nc">{m.text}</span></div>
              )
            )}
            {typing && !live && (
              <div className="line" style={{ color: 'var(--fg-3)' }}><span className="nc">{partner}</span><span>TYPING<span className="cursor">_</span></span></div>
            )}
            {voice === 'asked' && (
              <div role="status" className="line pending">
                <span style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--fg-2)' }}><span className="dot pulse" />VOICE</span>
                <span>REQUEST SENT. WAITING FOR <span className="nc">{partner}</span> TO ACCEPT. KEEP TYPING MEANWHILE.</span>
              </div>
            )}
          </div>
          <form className="chat-compose" onSubmit={onSend}>
            <label>
              <span>&gt;</span>
              <input
                value={draft}
                onChange={(e) => onDraft(e.target.value)}
                placeholder={live ? 'TYPE WHILE YOU TALK' : narrow ? 'SAY SOMETHING…' : 'SAY SOMETHING… (ESC ESC TO SKIP)'}
                aria-label="Message"
                maxLength={500}
                autoComplete="off"
              />
              {draft.length >= 400 && <span className="dim3" style={{ fontSize: 11, color: draft.length >= 450 ? 'var(--fg)' : undefined }}>{draft.length}/500</span>}
            </label>
            {live ? (
              <button type="button" className="btn dash voice-slot" disabled style={{ color: 'var(--fg-2)' }}>VOICE IS ON</button>
            ) : voice === 'asked' ? (
              <button type="button" className="btn dash voice-slot" disabled>VOICE REQUESTED…</button>
            ) : (
              <button type="button" className="btn voice-slot" onClick={onAskVoice}>[ V ] ASK FOR VOICE</button>
            )}
            <button type="submit" className="btn solid send" style={{ height: 44 }}>SEND ↵</button>
          </form>
        </main>
      </div>
      {overlays}
    </div>
  );
}

function VoiceConsent({ from, onAnswer }) {
  const now = useNow(true, 500);
  const left = Math.max(0, from.expiresAt - now);
  return (
    <Modal label="Voice request">
      <div className="head">
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span className="dot ring" />INCOMING REQUEST · {mmss(left)}</span>
        <span>NOTHING STARTS UNTIL YOU SAY YES</span>
      </div>
      <h1 style={{ fontSize: 32 }}><span className="nc">{from.name}</span> WANTS TO SWITCH TO VOICE.<span className="cursor">_</span></h1>
      <dl className="kv" style={{ rowGap: 14 }}>
        <dt>AUDIO</dt><dd>DEVICE TO DEVICE. NOT THROUGH US.</dd>
        <dt>YOUR MIC</dt><dd>OFF UNTIL YOU ACCEPT</dd>
        <dt>TEXT</dt><dd>STAYS OPEN THE WHOLE TIME</dd>
        <dt>ENDING IT</dt><dd>EITHER OF YOU, ANYTIME</dd>
      </dl>
      <div className="two">
        <button type="button" className="btn solid tall" onClick={() => onAnswer(true)}>[ Y ] ACCEPT</button>
        <button type="button" className="btn tall" onClick={() => onAnswer(false)}>[ N ] DECLINE, STAY IN TEXT</button>
      </div>
    </Modal>
  );
}

function Blocked() {
  return (
    <div className="page">
      <TopBar crumb="/CHAT" showOnline={false} back={{ label: '← LOBBY', href: '/' }} />
      <main className="main split">
        <div className="lead" style={{ width: 760 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 13 }}><span className="tagbox">[ BLOCKED ]</span><span className="dim">1:1 MATCHMAKING</span></div>
          <h1 className="h-40">YOU&apos;VE BEEN REMOVED FROM 1:1 MATCHMAKING AFTER MULTIPLE REPORTS.</h1>
          <p className="p-16">SEVERAL DIFFERENT PEOPLE REPORTED YOU IN THIS SESSION. YOU WON&apos;T BE MATCHED WITH ANYONE ELSE FOR THE REST OF IT.</p>
          <Link href="/" className="btn" style={{ alignSelf: 'flex-start', height: 52, padding: '0 24px' }}>[ BACK TO LOBBY ]</Link>
        </div>
        <dl className="side kv" style={{ padding: '32px 36px', gridTemplateColumns: '120px 1fr', border: '1px solid var(--rule-2)', fontSize: 12, lineHeight: 1.6 }}>
          <dt className="dim3">WHY</dt><dd className="dim">ENOUGH REPORTS FROM DIFFERENT PEOPLE TRIGGER THIS AUTOMATICALLY. NO HUMAN DECIDED IT.</dd>
          <dt className="dim3">WHAT&apos;S KEPT</dt><dd className="dim">NOTHING. REPORTS LIVE IN MEMORY AND DISAPPEAR WITH THE SESSION.</dd>
          <dt className="dim3">RULES</dt><dd><Link href="/terms" className="dim" style={{ textDecoration: 'underline', textUnderlineOffset: 3 }}>READ THE TERMS →</Link></dd>
        </dl>
      </main>
      <Footer />
    </div>
  );
}

function Bars() {
  return (
    <span aria-label="Speaking" className="speaking" style={{ height: 22 }}>
      {[10, 22, 14, 18, 8, 16].map((h, i) => <span key={i} className="bar" style={{ height: h, background: 'var(--accent)', animationDelay: `${i * 0.1}s` }} />)}
    </span>
  );
}
function IdleDots() {
  return <span className="idle-dots" aria-hidden="true">{[0, 1, 2, 3, 4, 5].map((i) => <span key={i} />)}</span>;
}
