'use client';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import TopBar from './TopBar';
import Modal from './Modal';
import MicModals from './MicModals';
import { emit, on, bus, toast, syncClock, useWisp } from '@/lib/wisp';
import { useMicFlow, micTrack, closeMic } from '@/lib/mic';
import { useMesh } from '@/lib/mesh';
import { useNow, mmss } from '@/lib/time';

const initials = (name) => name.split('_').slice(0, 2).map((w) => w[0]).join('').toUpperCase();
const onStage = (m) => m && m.role !== 'listener';
const SYS_TAG = { join: '[ JOINED ]', leave: '[ LEFT ]', mod: '[ MOD ]', stage: '[ STAGE ]', removed: '[ REMOVED ]', info: '[ ROOM ]' };

export default function Room({ channel }) {
  const router = useRouter();
  const session = useWisp((s) => s.session);
  const status = useWisp((s) => s.status);
  const meId = session?.id;

  const [snap, setSnap] = useState(null);
  const [feed, setFeed] = useState([]);
  const [invite, setInvite] = useState(null); // { from, expiresAt }
  const [muted, setMuted] = useState(false);
  const [track, setTrack] = useState(null);
  const [tab, setTab] = useState('stage');
  const [sheet, setSheet] = useState(null); // member id for the mobile action sheet
  const [draft, setDraft] = useState('');
  const mic = useMicFlow();
  const left = useRef(false);
  const asking = useRef(false);

  const members = snap?.members ?? [];
  const me = members.find((m) => m.id === meId);
  const meMod = me?.role === 'mod';

  // ---------- join / leave ----------

  const join = useCallback(async () => {
    const r = await emit('channel:join', { id: channel.id });
    if (r.error === 'full') {
      toast({ kind: 'solid', tag: '[ ROOM FULL ]', text: `${channel.name.toUpperCase()} FILLED UP (10/10) BEFORE YOU GOT IN. TRY ANOTHER ROOM.` });
      return router.replace('/rooms');
    }
    if (r.error === 'removed') {
      toast({ kind: 'solid', tag: '[ REMOVED ]', text: `YOU WERE REMOVED FROM ${channel.name.toUpperCase()} AFTER MULTIPLE REPORTS. OTHER ROOMS ARE STILL OPEN TO YOU.` });
      return router.replace('/rooms');
    }
    if (r.error) return; // offline: the reconnect handler rejoins
    syncClock(r.snapshot.serverNow);
    setSnap(r.snapshot);
    setFeed(r.history ?? []);
  }, [channel, router]);

  useEffect(() => {
    if (!meId) return;
    join();
  }, [meId, join]);

  useEffect(() => {
    document.title = `${channel.name} · wisp`;
    const offs = [
      on('channel:update', (s) => {
        if (s.id !== channel.id) return;
        syncClock(s.serverNow);
        setSnap(s);
      }),
      on('chat:new', (m) => setFeed((f) => (f.some((x) => x.id === m.id) ? f : [...f, m].slice(-200)))),
      on('channel:speakInviteReceived', (p) => {
        syncClock(p.serverNow);
        setInvite(p);
      }),
      on('channel:inviteExpired', (p) => {
        if (p.id) toast({ tag: '[ INVITE ]', text: <><span className="nc">{p.name}</span> DIDN&apos;T ANSWER IN TIME. THE INVITE EXPIRED.</> });
        else setInvite(null);
      }),
      on('channel:inviteDeclined', (p) => toast({ tag: '[ INVITE ]', text: <><span className="nc">{p.name}</span> SAID NO. THEY&apos;RE STILL LISTENING.</> })),
      on('hand:approved', (p) =>
        toast({ kind: 'solid', tag: '[ ON STAGE ]', text: <><span className="nc">{p.by}</span> BROUGHT YOU UP. THE ROOM CAN HEAR YOU NOW. STAY 2:30 AND YOU BECOME A MOD.</> })
      ),
      on('hand:declined', () => toast({ tag: '[ HAND DOWN ]', text: 'NOT RIGHT NOW. YOUR HAND IS DOWN. YOU CAN RAISE IT AGAIN IN A FEW SECONDS.' })),
      on('hand:expired', () => toast({ tag: '[ HAND DOWN ]', text: 'NOBODY ANSWERED IN 30 SECONDS, SO YOUR HAND WENT DOWN. RAISE IT AGAIN ANYTIME.' })),
      on('stage:demoted', () =>
        toast({ kind: 'solid', tag: '[ BACK TO LISTENING ]', text: 'A MOD MOVED YOU BACK TO LISTENERS. YOUR MIC IS OFF. IF YOU’RE INVITED UP AGAIN, YOUR 2:30 STARTS OVER.' })
      ),
      on('channel:modPromoted', (p) => {
        if (p.id === meId) {
          toast({ kind: 'solid', tag: '[ YOU’RE A MOD ]', text: 'YOU CAN NOW INVITE LISTENERS ON STAGE, ANSWER RAISED HANDS, AND MOVE SPEAKERS BACK TO LISTENERS. NOBODY CAN MOVE YOU NOW.' });
        } else if (p.why === 'succession') {
          toast({ tag: '[ SUCCESSION ]', text: <>A MOD LEFT. <span className="nc">{p.name}</span> IS NOW A MOD — LONGEST ON STAGE.</> });
        }
      }),
      on('channel:youWereKicked', (p) => {
        left.current = true;
        toast({ kind: 'solid', tag: '[ REMOVED ]', text: `YOU WERE REMOVED FROM ${String(p.name).toUpperCase()} AFTER MULTIPLE REPORTS. OTHER ROOMS ARE STILL OPEN TO YOU.` });
        router.replace('/rooms');
      }),
      bus.on('session', ({ fresh }) => {
        if (fresh) {
          setSnap(null);
          setFeed([]);
          join();
        }
      })
    ];
    return () => offs.forEach((f) => f());
  }, [channel, meId, join, router]);

  useEffect(
    () => () => {
      if (!left.current) emit('channel:leave');
      closeMic();
    },
    []
  );

  // ---------- mic follows the stage ----------

  useEffect(() => {
    if (!me) return;
    if (onStage(me) && !track && !asking.current) {
      asking.current = true;
      mic.ask().then((ok) => {
        asking.current = false;
        if (ok) {
          setTrack(micTrack());
          setMuted(false);
        } else emit('stage:stepDown');
      });
    }
    if (!onStage(me) && track) {
      closeMic();
      setTrack(null);
      setMuted(false);
    }
  }, [me?.role]); // eslint-disable-line react-hooks/exhaustive-deps

  const { speaking } = useMesh({ meId, members, track, muted });

  // ---------- actions ----------

  const toggleMute = () => {
    const next = !muted;
    setMuted(next);
    emit('stage:mute', { muted: next });
  };

  const toggleHand = async () => {
    if (me?.handUp) return emit('hand:lower');
    const ok = await mic.ask();
    if (!ok) return;
    setTrack(micTrack());
    const r = await emit('hand:raise');
    if (r.error === 'cooldown') toast({ tag: '[ HAND DOWN ]', text: 'GIVE IT A FEW SECONDS BEFORE RAISING YOUR HAND AGAIN.' });
  };

  const answerInvite = async (yes) => {
    setInvite(null);
    if (!yes) return emit('channel:declineInvite');
    const ok = await mic.ask();
    if (!ok) return emit('channel:declineInvite');
    setTrack(micTrack());
    const r = await emit('channel:acceptInvite');
    if (r.ok) toast({ kind: 'solid', tag: '[ ON STAGE ]', text: 'THE ROOM CAN HEAR YOU NOW. STAY 2:30 AND YOU BECOME A MOD.' });
  };

  const report = async (m) => {
    setSheet(null);
    const r = await emit('channel:report', { to: m.id });
    if (r.ok) toast({ tag: '[ REPORTED ]', text: <>THANKS. IF ENOUGH PEOPLE HERE REPORT <span className="nc">{m.name}</span>, THEY&apos;RE REMOVED AUTOMATICALLY.</> });
  };
  const act = (event, m) => {
    setSheet(null);
    return emit(event, { to: m.id });
  };

  const sendChat = async (e) => {
    e?.preventDefault();
    const text = draft.trim();
    if (!text) return;
    const r = await emit('chat:send', { text });
    if (r.ok) setDraft('');
    else if (r.error === 'slow') toast({ key: 'slow', tag: '[ SLOW DOWN ]', text: 'ONE MESSAGE AT A TIME. TRY AGAIN IN A SECOND.' });
    else if (r.error === 'too_long') toast({ key: 'long', tag: '[ TOO LONG ]', text: 'KEEP IT UNDER 500 CHARACTERS.' });
  };

  // keyboard: M mic, H hand, Y/N on an invite
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.metaKey || e.ctrlKey || mic.modal) return;
      const k = e.key.toLowerCase();
      if (invite) {
        if (k === 'y') answerInvite(true);
        if (k === 'n') answerInvite(false);
        return;
      }
      if (k === 'm' && onStage(me) && track) toggleMute();
      if (k === 'h' && me && !onStage(me)) toggleHand();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  // ---------- derived ----------

  const now = useNow(true, 500);
  const speakers = useMemo(() => {
    const rank = (m) => (snap?.members && m.founding ? 0 : m.role === 'mod' ? 1 : 2);
    return members.filter(onStage).sort((a, b) => rank(a) - rank(b) || a.stageSince - b.stageSince);
  }, [members, snap]);
  const listeners = useMemo(
    () =>
      members
        .filter((m) => !onStage(m))
        .sort((a, b) => (b.id === meId) - (a.id === meId) || b.handUp - a.handUp || a.joinedAt - b.joinedAt),
    [members, meId]
  );
  const hands = listeners.filter((m) => m.handUp).length;
  const alone = members.length === 1 && meMod;

  let stripTag, stripText, roleLine;
  if (!me) {
    stripTag = '[ JOINING ]';
    stripText = 'WALKING IN…';
    roleLine = 'JOINING';
  } else if (alone) {
    stripTag = '[ YOU OPENED THIS ROOM ]';
    stripText = 'IT’S JUST YOU. THE NEXT PERSON IN BECOMES THE OTHER MOD. TALK TO THE ROOM OR WAIT — IT STAYS OPEN WHILE YOU’RE HERE.';
    roleLine = me.founding ? 'YOU ARE A FOUNDING MOD' : 'YOU ARE A MOD';
  } else if (meMod) {
    stripTag = '[ YOU’RE A MOD ]';
    stripText = 'THE ROOM CAN HEAR YOU. YOU DECIDE WHO SPEAKS: BRING UP RAISED HANDS, INVITE LISTENERS, OR MOVE SPEAKERS BACK TO LISTENERS.';
    roleLine = me.founding ? 'YOU ARE A FOUNDING MOD' : 'YOU ARE A MOD';
  } else if (me.role === 'speaker') {
    stripTag = '[ ON STAGE ]';
    stripText = `THE ROOM CAN HEAR YOU. IN ${mmss(me.promoteAt - now)} YOU BECOME A MOD. UNTIL THEN, A MOD CAN MOVE YOU BACK TO LISTENERS.`;
    roleLine = 'YOU ARE ON STAGE';
  } else if (me.handUp) {
    stripTag = '[ HAND UP ]';
    stripText = 'THE MODS CAN SEE YOUR HAND. IF ONE BRINGS YOU UP, YOUR MIC TURNS ON. NO ANSWER IN 30 SECONDS AND IT GOES DOWN ON ITS OWN.';
    roleLine = 'YOU ARE LISTENING';
  } else {
    stripTag = '[ YOU’RE LISTENING ]';
    stripText = 'NOBODY CAN HEAR YOU. RAISE YOUR HAND TO ASK FOR THE STAGE, OR WAIT FOR A MOD TO INVITE YOU. YOU CAN ALWAYS TYPE IN THE ROOM CHAT.';
    roleLine = 'YOU ARE LISTENING';
  }

  const bigButton = !me ? (
    <button type="button" className="bigbtn" disabled>…</button>
  ) : onStage(me) ? (
    muted || !track ? (
      <button type="button" className="bigbtn" aria-pressed="true" onClick={toggleMute} disabled={!track}>
        [ M ] MIC OFF — UNMUTE
      </button>
    ) : (
      <button type="button" className="bigbtn solid" aria-pressed="false" onClick={toggleMute}>
        <span aria-hidden="true" className="bars">
          <span className="bar" style={{ height: 8, background: '#000' }} />
          <span className="bar" style={{ height: 14, background: '#000', animationDelay: '.2s' }} />
          <span className="bar" style={{ height: 10, background: '#000', animationDelay: '.35s' }} />
        </span>
        [ M ] MIC ON — MUTE
      </button>
    )
  ) : me.handUp ? (
    <button type="button" className="bigbtn solid" aria-pressed="true" onClick={toggleHand}>
      <span className="dot pulse" style={{ background: '#000' }} />
      HAND UP · {mmss(me.handExpiresAt - now)} — [ H ] LOWER
    </button>
  ) : (
    <button type="button" className="bigbtn" aria-pressed="false" onClick={toggleHand}>
      [ H ] RAISE HAND TO SPEAK
    </button>
  );

  const sheetMember = sheet && members.find((m) => m.id === sheet);

  return (
    <div className="page fixed room-page">
      <TopBar crumb={`/ROOMS/${channel.id.toUpperCase()}`} back={{ label: '← LEAVE ROOM', href: '/rooms' }} />
      <div className="room" data-tab={tab}>
        <div className="room-top">
          <div role="status" aria-live="polite" className="strip">
            <span className="tag">{stripTag}</span>
            <span className="txt">{stripText}</span>
          </div>
          <div className="room-title">
            <div>
              <h1>{channel.name}</h1>
              <div className="sub">
                <span className="blurb nc" style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{channel.blurb}</span>
                <span>{String(members.length).padStart(2, '0')}/10 IN ROOM · {roleLine}</span>
              </div>
            </div>
            {bigButton}
          </div>
          <div className="tabs" role="tablist" aria-label="Room view">
            <button type="button" role="tab" aria-selected={tab === 'stage'} onClick={() => setTab('stage')}>STAGE + LISTENERS</button>
            <button type="button" role="tab" aria-selected={tab === 'chat'} onClick={() => setTab('chat')}>ROOM CHAT · {feed.filter((f) => !f.system).length}</button>
          </div>
        </div>

        <div className="people">
          <People
            speakers={speakers}
            listeners={listeners}
            me={me}
            meMod={meMod}
            alone={alone}
            hands={hands}
            speaking={speaking}
            now={now}
            onAct={act}
            onReport={report}
            onMore={setSheet}
          />
        </div>

        <aside aria-label="Room chat" className="room-chat">
          <div className="hd"><span>ROOM CHAT</span><span className="dim3">CLEARS WHEN ROOM EMPTIES</span></div>
          <Feed feed={feed} meId={meId} />
          <form className="compose" onSubmit={sendChat}>
            <span>&gt;</span>
            <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="SAY SOMETHING TO THE ROOM" aria-label="Message the room" maxLength={500} />
            {draft.length >= 400 ? <span className={`count ${draft.length >= 450 ? 'warn' : ''}`}>{draft.length}/500</span> : <span className="dim" style={{ fontSize: 11 }}>↵</span>}
          </form>
        </aside>
      </div>
      <div className="bottombar">
        {tab === 'chat' ? (
          <form className="compose" onSubmit={sendChat}>
            <span>&gt;</span>
            <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="SAY SOMETHING" aria-label="Message the room" maxLength={500} />
            <span className="dim">↵</span>
          </form>
        ) : (
          bigButton
        )}
      </div>

      {invite && (
        <InviteModal invite={invite} now={now} onAnswer={answerInvite} />
      )}
      <MicModals flow={mic} where="room" />
      {sheetMember && (
        <Modal label={`Actions for ${sheetMember.name}`} onEscape={() => setSheet(null)}>
          <div className="head"><span className="nc" style={{ color: 'var(--fg)', fontSize: 16 }}>{sheetMember.name}</span><span>{sheetMember.role.toUpperCase()}</span></div>
          <div className="more-sheet">
            {meMod && sheetMember.role === 'listener' && !sheetMember.invitedUntil && !sheetMember.handUp && (
              <button type="button" className="btn tall" onClick={() => act('channel:invite', sheetMember)}>[ ↑ ] INVITE ON STAGE</button>
            )}
            {meMod && sheetMember.role === 'speaker' && (
              <button type="button" className="btn tall" onClick={() => act('stage:demote', sheetMember)}>[ ↓ ] MOVE TO LISTENERS</button>
            )}
            <button type="button" className="btn tall" onClick={() => report(sheetMember)}>[ ! ] REPORT</button>
            <button type="button" className="btn tall dim" onClick={() => setSheet(null)}>CLOSE</button>
          </div>
        </Modal>
      )}
      {status === 'reconnecting' && <div aria-hidden="true" style={{ position: 'fixed', inset: 0, top: 'calc(var(--top) + 72px)', background: 'rgba(0,0,0,.7)', zIndex: 35 }} />}
    </div>
  );
}

function People({ speakers, listeners, me, meMod, alone, hands, speaking, now, onAct, onReport, onMore }) {
  return (
    <>
      <section aria-label="On stage" className="sec">
        <div className="lbl">
          <span>ON STAGE<br /><span className="dim3 cnt">{String(speakers.length).padStart(2, '0')}</span></span>
        </div>
        <div className="stage">
          {speakers.map((s) => {
            const you = s.id === me?.id;
            const talking = speaking.has(s.id) && !s.muted;
            const roleName = s.founding && s.role === 'mod' ? 'FOUNDING MOD' : s.role === 'mod' ? 'MOD' : 'SPEAKER';
            return (
              <div key={s.id} className="sp">
                <span className={`av ${you ? 'me' : ''} ${s.online ? '' : 'away'}`}>{initials(s.name)}</span>
                <span className="namecol">
                  <span className="nm nc">{s.name}{you && <span className="dim3"> (you)</span>}</span>
                  <span className="mstate">
                    {roleName}
                    {s.muted && ' · MUTED'}
                    {!s.online && ' · RECONNECTING'}
                    {talking && <Bars small />}
                    {s.role === 'speaker' && s.promoteAt && <span style={{ color: 'var(--fg)' }}>{mmss(s.promoteAt - now)} TO MOD</span>}
                  </span>
                </span>
                <span className="role">
                  {roleName === 'FOUNDING MOD' && <span className="badge solid">FOUNDING MOD</span>}
                  {roleName === 'MOD' && <span className="badge outline">MOD</span>}
                  {roleName === 'SPEAKER' && <span className="dim" style={{ fontSize: 11 }}>SPEAKER</span>}
                </span>
                <span className="state" style={{ fontSize: 12 }}>
                  {!s.online ? (
                    <span className="dim3">RECONNECTING…</span>
                  ) : talking ? (
                    <Bars />
                  ) : s.muted ? (
                    <span className="dim3">MUTED</span>
                  ) : s.role === 'speaker' && s.promoteAt ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span className="dot pulse" />{mmss(s.promoteAt - now)} TO MOD</span>
                  ) : null}
                </span>
                <div className="acts">
                  {you && !alone && (
                    <button type="button" className="ctl" onClick={() => emit('stage:stepDown')}>
                      <span className="wide">[ ↓ ] LEAVE STAGE</span><span className="narrow">↓</span>
                    </button>
                  )}
                  {!you && meMod && s.role === 'speaker' && (
                    <button type="button" className="ctl hi" onClick={() => onAct('stage:demote', s)} aria-label={`Move ${s.name} to listeners`}>
                      <span className="wide">[ ↓ ] TO LISTENERS</span><span className="narrow">↓</span>
                    </button>
                  )}
                  {!you && meMod && s.role === 'mod' && <span className="wide fixed-note dim3">CAN&apos;T BE MOVED</span>}
                  {!you && (
                    <>
                      <button type="button" className="ctl wide" aria-label={`Report ${s.name}`} onClick={() => onReport(s)}>[ ! ]</button>
                      <button type="button" className="ctl narrow" aria-label={`More for ${s.name}`} onClick={() => onMore(s.id)}>···</button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
          {meMod && !alone && <div className="hint">MODS CAN MOVE SPEAKERS DOWN UNTIL THEY BECOME MODS. AFTER THAT, ONLY REPORTS CAN REMOVE THEM.</div>}
        </div>
      </section>

      <section aria-label="Listening" className="sec" style={{ fontSize: 13, color: 'var(--fg-2)', marginTop: 24 }}>
        <div className="lbl" style={{ paddingTop: 16 }}>
          <span>LISTENING<br /><span className="dim3 cnt">{String(listeners.length).padStart(2, '0')}</span></span>
          {hands > 0 && meMod && <><br /><span className="handsbadge">{hands} HAND{hands > 1 ? 'S' : ''} UP</span></>}
        </div>
        <div className="listen">
          {listeners.map((l) => {
            const you = l.id === me?.id;
            const invited = l.invitedUntil && l.invitedUntil > now;
            const note = l.handUp ? `HAND UP · ${mmss(l.handExpiresAt - now)}` : invited && meMod ? `INVITE SENT · ${mmss(l.invitedUntil - now)} TO ANSWER` : !l.online ? 'RECONNECTING…' : '';
            return (
              <div key={l.id} className="li">
                <span className={`av ${you ? 'me' : ''}`} style={you ? { background: 'var(--fg)', borderColor: 'var(--fg)' } : undefined}>{initials(l.name)}</span>
                <span className="namecol">
                  <span className="nm nc" style={{ color: you || l.handUp ? 'var(--fg)' : undefined }}>{l.name}{you && <span className="dim3"> (you)</span>}</span>
                </span>
                <span className="note">{l.handUp && <span className="dot pulse" />}{note}</span>
                <div className="acts">
                  {meMod && l.handUp && (
                    <>
                      <button type="button" className="ctl solid" onClick={() => onAct('hand:approve', l)} aria-label={`Bring ${l.name} up`}>
                        <span className="wide">[ ✓ ] BRING UP</span><span className="narrow">✓ UP</span>
                      </button>
                      <button type="button" className="ctl" onClick={() => onAct('hand:decline', l)} aria-label="Not now">
                        <span className="wide">[ ✕ ] NOT NOW</span><span className="narrow">✕</span>
                      </button>
                    </>
                  )}
                  {meMod && !l.handUp && !invited && !you && (
                    <button type="button" className="ctl hi wide" onClick={() => onAct('channel:invite', l)}>[ ↑ ] INVITE ON STAGE</button>
                  )}
                  {!you && (
                    <>
                      <button type="button" className="ctl wide" aria-label={`Report ${l.name}`} onClick={() => onReport(l)}>[ ! ]</button>
                      {!(meMod && l.handUp) && <button type="button" className="ctl narrow" aria-label={`More for ${l.name}`} onClick={() => onMore(l.id)}>···</button>}
                    </>
                  )}
                </div>
              </div>
            );
          })}
          {listeners.length === 0 && (
            <div style={{ minHeight: 50, display: 'flex', alignItems: 'center', fontSize: 12 }} className="dim3">
              NOBODY LISTENING YET. THE ROOM IS LIVE IN THE LIST, SO PEOPLE CAN FIND IT.
            </div>
          )}
        </div>
      </section>
    </>
  );
}

function Bars({ small }) {
  const h = small ? [7, 13, 9, 11] : [8, 16, 11, 14, 6];
  return (
    <span aria-label="Speaking" className="speaking" style={small ? { height: 12, gap: 2 } : undefined}>
      {h.map((x, i) => <span key={i} className="bar" style={{ height: x, background: 'var(--accent)', animationDelay: `${i * 0.13}s` }} />)}
    </span>
  );
}

function Feed({ feed, meId }) {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [feed]);
  return (
    <div role="log" className="feed" ref={ref}>
      {feed.map((f) =>
        f.system ? (
          <div key={f.id} className="sys">
            <span className="t">{SYS_TAG[f.kind] ?? '[ ROOM ]'}</span>
            <span className="nc">{f.text}.</span>
          </div>
        ) : (
          <div key={f.id} className={`msg ${f.from.id === meId ? 'mine' : ''}`}>
            <span className="who nc">{f.from.id === meId ? `${f.from.name} (you)` : f.from.name}</span>
            <span className="txt nc">{f.text}</span>
          </div>
        )
      )}
    </div>
  );
}

function InviteModal({ invite, now, onAnswer }) {
  const left = Math.max(0, invite.expiresAt - now);
  return (
    <Modal label="Stage invite" onEscape={() => onAnswer(false)}>
      <div className="head">
        <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}><span className="dot pulse" />STAGE INVITE</span>
        <span>EXPIRES IN <span style={{ color: 'var(--fg)' }}>{mmss(left)}</span></span>
      </div>
      <div className="progress" role="progressbar" aria-label="Time left to answer" aria-valuemin={0} aria-valuemax={30} aria-valuenow={Math.round(left / 1000)}>
        <div style={{ width: `${Math.min(100, (left / 30000) * 100)}%` }} />
      </div>
      <h1><span className="nc">{invite.from}</span> INVITED YOU ON STAGE.<span className="cursor">_</span></h1>
      <dl className="kv" style={{ gridTemplateColumns: '150px 1fr', rowGap: 12 }}>
        <dt>IF YOU ACCEPT</dt><dd>YOUR MIC TURNS ON. THE ROOM CAN HEAR YOU.</dd>
        <dt>STAY 2:30</dt><dd>AND YOU BECOME A MOD YOURSELF.</dd>
        <dt>NO ANSWER</dt><dd>YOU STAY A LISTENER. NOTHING HAPPENS.</dd>
      </dl>
      <div className="two">
        <button type="button" className="btn solid tall" onClick={() => onAnswer(true)}>[ Y ] GO ON STAGE</button>
        <button type="button" className="btn tall" onClick={() => onAnswer(false)}>[ N ] KEEP LISTENING</button>
      </div>
    </Modal>
  );
}
