'use client';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { attributesToProps } from 'html-react-parser';
import Guard from '@/components/Guard';
import Screen, { useView } from '@/v5/Screen';
import DT from '@/v5/screens/V5EchoThread';
import MT from '@/v5/screens/V5MEchoThread';
import DN from '@/v5/screens/V5EchoNoReplies';
import MN from '@/v5/screens/V5MEchoNoReplies';
import DY from '@/v5/screens/V5EchoYours';
import MY from '@/v5/screens/V5MEchoYours';
import DU from '@/v5/screens/V5UnsentOpen';
import MU from '@/v5/screens/V5MUnsentOpen';
import DX from '@/v5/screens/V5NotFound';
import MX from '@/v5/screens/V5MNotFound';
import { emit, on as onSocket, toast, useWisp } from '@/lib/wisp';
import {
  REPLY_MAX, VOICE_MAX_S, getThread, getAudio, setHeard, replyEcho, reportEcho, takeDown, isMine, mine, heard as heardLocal, useRecorder, usePlayer
} from '@/lib/echoes';
import { Slips, Tally, fadesShort, leftAt, clock, slipHeight } from '../ui';
import { createStore, useStore } from '../write/compose';

const INK = '#221E1A', PENCIL = '#5F584E', RED = '#B8352A';
const styleOf = (node) => attributesToProps({ style: node.attribs?.style || '' }).style || {};
const BARE = { background: 'transparent', border: 0, outline: 'none', resize: 'none', padding: 0, margin: 0, width: '100%', font: 'inherit', color: INK, fontStyle: 'normal' };
const ERR = {
  cooldown: () => 'ONE REPLY EVERY FEW SECONDS. TRY AGAIN IN A MOMENT.',
  too_long: () => 'THAT’S TOO LONG FOR A REPLY.',
  empty: () => 'SAY SOMETHING FIRST.',
  full: () => 'THIS ONE HAS BEEN HEARD ENOUGH. NO MORE REPLIES.',
  not_allowed: () => 'REPLIES ARE OFF ON THIS ONE.',
  not_found: () => 'IT ALREADY LET GO.',
  offline: () => 'YOU’RE OFFLINE. TRY AGAIN IN A MOMENT.'
};
const errText = (r) => (ERR[r?.error] ?? (() => 'SOMETHING WENT WRONG. TRY AGAIN.'))(r);

// How tall the note's paper is: the voice card is the designed size, a written one grows with its words.
function cardHeight(n, phone, base) {
  if (n.mode === 'voice') return base;
  const lines = Math.max(1, Math.ceil((n.text || '').length / (phone ? 30 : 50)) + ((n.text || '').match(/\n/g)?.length ?? 0));
  const h = (phone ? 24 + 18 + 14 + lines * 27 + 92 : 34 + 20 + 18 + lines * 32.5 + 106) + (n.kind === 'unsent' ? 90 : 0); // + the "to …," line
  return Math.round(Math.max(phone ? 220 : 240, Math.min(h, phone ? 620 : 470)));
}

function ReplyText({ node, store }) {
  const text = useStore(store, (s) => s.text);
  const st = styleOf(node);
  return (
    <div style={{ ...st, flex: '1 1 auto', minWidth: 0 }}>
      <textarea
        value={text}
        rows={1}
        maxLength={REPLY_MAX}
        placeholder="say something kind back"
        aria-label="Write a reply"
        className="nt-area nt-reply"
        onChange={(e) => store.set({ text: e.target.value })}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            store.get().send?.();
          }
        }}
        style={{ ...BARE, height: Math.round(parseFloat(st.fontSize || 20) * 1.5), lineHeight: 1.5, caretColor: RED }}
      />
    </div>
  );
}

// Hold to record a reply; let go and it's sent.
function ReplyVoice({ node, recStore, sending }) {
  const rec = useStore(recStore, (s) => s.rec);
  const busy = useStore(recStore, (s) => s.sending);
  const st = styleOf(node);
  const phone = parseFloat(st.marginTop) === 14;
  const label = busy ? 'sending it…'
    : rec.state === 'recording' ? `recording · ${clock(rec.elapsed)}`
      : rec.state === 'denied' ? 'your mic is blocked'
        : rec.state === 'unsupported' ? 'this browser can’t record'
          : rec.state === 'asking' ? 'asking for your mic…' : 'hold to record a reply';
  const down = (e) => {
    e.preventDefault();
    if (busy || rec.state === 'recording' || rec.state === 'asking') return;
    rec.reset();
    rec.start();
  };
  const up = () => rec.state === 'recording' && rec.stop();
  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="Press and hold to record a reply. Let go to send it."
      onPointerDown={down}
      onPointerUp={up}
      onPointerLeave={up}
      onPointerCancel={up}
      onKeyDown={(e) => (e.key === ' ' || e.key === 'Enter') && !e.repeat && down(e)}
      onKeyUp={(e) => (e.key === ' ' || e.key === 'Enter') && up()}
      onContextMenu={(e) => e.preventDefault()}
      style={{ ...st, cursor: 'pointer', touchAction: 'none', userSelect: 'none', WebkitUserSelect: 'none' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: phone ? 10 : 12 }}>
        <span className={rec.state === 'recording' ? 'blink' : ''} style={{ width: phone ? 11 : 12, height: phone ? 11 : 12, borderRadius: '50%', background: RED, flexShrink: 0 }} />
        <span style={{ fontFamily: "'Nothing You Could Do', 'Caveat', cursive", fontSize: phone ? 21 : 24, color: INK }}>{label}</span>
      </div>
      <span style={{ fontFamily: "'Courier Prime', 'Courier New', monospace", fontSize: phone ? 9 : 10, letterSpacing: phone ? '.12em' : '.14em', color: PENCIL, textAlign: 'right' }}>
        {rec.state === 'recording' ? 'LET GO TO SEND' : phone ? <>UP TO<br />{VOICE_MAX_S} SEC</> : `UP TO ${VOICE_MAX_S} SECONDS`}
      </span>
    </div>
  );
}

function PlayTime({ node, store, dur }) {
  const p = useStore(store, (s) => s.progress);
  return <span style={styleOf(node)}>{clock(p * dur)} / {clock(dur)}</span>;
}

function Thread() {
  const { id } = useParams();
  const router = useRouter();
  const view = useView();
  const phone = view?.phone ?? true;
  const status = useWisp((s) => s.status);
  const [data, setData] = useState(null); // { note, replies } | { gone: true }
  const [mode, setMode] = useState('write');
  const [now, setNow] = useState(Date.now());
  const mineHere = useMemo(() => (typeof window !== 'undefined' ? isMine(id) : false), [id, data]); // eslint-disable-line react-hooks/exhaustive-deps
  const player = usePlayer();
  const playerRef = useRef(player); // the player object is new every render; actions read it through this
  playerRef.current = player;
  const rec = useRecorder(VOICE_MAX_S);

  const load = useCallback(async () => {
    const r = await getThread(id);
    if (r?.ok) {
      setData({ note: r.note, replies: r.replies });
      setNow(Date.now());
      if (mine.all()[id]) mine.seen(id, r.replies.length);
    } else if (r?.error === 'not_found' || r?.error === 'bad_request') setData({ gone: true });
  }, [id]);
  useEffect(() => {
    if (status === 'online') load();
  }, [status, load]);
  useEffect(() => {
    let t = null;
    const off = onSocket('echoes:changed', () => {
      clearTimeout(t);
      t = setTimeout(load, 300);
    });
    return () => {
      off();
      clearTimeout(t);
    };
  }, [load]);

  const note = data?.note;
  const replies = data?.replies;

  // ---- stores for fast-changing parts (typing, recording, playback) ----
  const textStore = useMemo(() => createStore({ text: '', send: null }), []);
  const recStore = useMemo(() => createStore({ rec, sending: false }), []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => recStore.set({ rec }), [rec, recStore]);
  const playStore = useMemo(() => createStore({ progress: 0 }), []);
  useEffect(() => playStore.set({ progress: player.playing === id ? player.progress : 0 }), [player.playing, player.progress, id, playStore]);

  // ---- actions ----
  const sendReply = useCallback(async (payload) => {
    const body = payload ?? { text: textStore.get().text.trim() };
    if (!payload && !body.text) return toast({ tag: '[ NOTHING YET ]', text: ERR.empty() });
    const r = await replyEcho(id, body);
    if (!r?.ok) return toast({ tag: '[ NOT SENT ]', text: errText(r) });
    if (!payload) textStore.set({ text: '' });
    load();
  }, [id, load, textStore]);
  useEffect(() => textStore.set({ send: () => sendReply() }), [sendReply, textStore]);

  // a voice reply goes out as soon as you let go
  useEffect(() => {
    if (rec.state !== 'done' || !rec.clip || recStore.get().sending) return;
    const clip = rec.clip;
    recStore.set({ sending: true });
    sendReply({ clip }).finally(() => {
      recStore.set({ sending: false });
      rec.reset();
    });
  }, [rec.state, rec.clip]); // eslint-disable-line react-hooks/exhaustive-deps

  const tapHeard = useCallback(async () => {
    if (!note) return;
    const on = !note.heard;
    setData((d) => d && d.note ? { ...d, note: { ...d.note, heard: on, heardCount: Math.max(0, d.note.heardCount + (on ? 1 : -1)) } } : d);
    const r = await setHeard(id, on);
    if (r?.ok) setData((d) => d && d.note ? { ...d, note: { ...d.note, heard: r.heard, heardCount: r.heardCount } } : d);
    if (on) heardLocal.add(id, note.expiresAt);
  }, [id, note]);

  const togglePlay = useCallback(() => {
    if (note?.mode !== 'voice') return;
    playerRef.current.toggle(id, () => getAudio(id)).then((ok) => ok && heardLocal.add(id, note.expiresAt));
  }, [id, note]);

  const playReply = useCallback((r) => playerRef.current.toggle(`${id}:${r.id}`, () => getAudio(id, r.id)), [id]);
  const reportReply = useCallback(async (r) => {
    const res = await reportEcho(id, r.id);
    if (res?.ok) {
      toast({ tag: '[ REPORTED ]', text: 'THANK YOU. ENOUGH REPORTS TAKE IT DOWN FOR EVERYONE.' });
      load();
    }
  }, [id, load]);
  const removeReply = useCallback(async (r) => {
    const m = mine.all()[id];
    if (!m) return;
    const res = await emit('echoes:deleteReply', { id, replyId: r.id, ticket: m.ticket });
    if (res?.ok) load();
  }, [id, load]);
  const takeItDown = useCallback(async () => {
    const r = await takeDown(id);
    if (r?.ok || r?.error === 'not_found') {
      toast({ tag: '[ LET GO ]', text: 'IT’S DOWN. THE REPLIES WENT WITH IT.' });
      router.push('/echoes');
    } else toast({ tag: '[ NOT YET ]', text: errText(r) });
  }, [id, router]);

  // ---- what the screens read ----
  const playing = player.playing === id;
  const vals = useMemo(() => {
    if (!note) return {};
    const left = note.expiresAt - now;
    const n = note.heardCount ?? 0;
    return {
      rootClass: playing ? 'playing' : '',
      isPlaying: playing, notPlaying: !playing, playLabel: playing ? 'Pause' : 'Play', togglePlay,
      isHeard: note.heard, notHeard: !note.heard, heardCount: n, heartFill: note.heard ? RED : 'none',
      heardHint: note.heard ? (note.kind === 'unsent' ? 'whoever wrote it will know it reached someone' : 'they will know it reached someone')
        : note.kind === 'unsent' ? 'tap once you have read it' : note.mode === 'voice' ? 'tap once you have listened' : 'tap once you have read it',
      tapHeard,
      writeMode: mode === 'write', speakMode: mode === 'speak',
      writeColor: mode === 'write' ? INK : PENCIL, speakColor: mode === 'speak' ? INK : PENCIL,
      writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,
      toWrite: () => setMode('write'), toSpeak: () => setMode('speak'),
      isVoice: note.mode === 'voice', isText: note.mode !== 'voice', modeLabel: note.mode === 'voice' ? 'VOICE' : 'TEXT',
      kindLabel: note.kind === 'unsent' ? 'AN UNSENT LETTER' : 'AN ECHO',
      fadesShort: fadesShort(left), timeTitle: leftAt(note.createdAt), noteText: note.text ?? '',
      letterTo: note.to || 'you', letterText: note.text ?? (note.mode === 'voice' ? `(a voice note · ${clock(note.duration)})` : ''),
      cardH: cardHeight(note, false, note.kind === 'unsent' ? 384 : mineHere ? 250 : 336),
      mcardH: cardHeight(note, true, 362),
      repliesTitle: replies?.length ? `${replies.length} ${replies.length === 1 ? 'reply' : 'replies'}` : note.kind === 'unsent' ? 'no replies' : 'no replies yet',
      heardBy: n ? `heard by ${n}` : 'not heard yet',
      takeDownLabel: 'take it down now',
      sendReply: () => sendReply()
    };
  }, [note, replies, now, playing, mode, mineHere, togglePlay, tapHeard, sendReply]);

  const slots = useMemo(() => {
    if (!note) return {};
    return {
      replies: (node) => (
        <div style={{ ...styleOf(node), ...(phone ? null : { flex: '1 1 auto', minHeight: 0, overflowY: 'auto', overflowX: 'hidden', scrollbarWidth: 'none', padding: '14px 12px 12px', margin: '8px -12px 0' }) }}>
          {replies?.length ? (
            <Slips replies={replies} phone={phone} now={now} playing={player.playing?.startsWith(`${id}:`) ? player.playing.slice(id.length + 1) : null}
              onPlay={playReply} onReport={reportReply} onRemove={removeReply} canRemove={mineHere} />
          ) : (
            <div style={{ fontFamily: "'Nothing You Could Do', 'Caveat', cursive", fontSize: phone ? 19 : 22, color: '#A39A8C', padding: '4px 4px' }}>nobody has replied yet. heard is enough too.</div>
          )}
        </div>
      ),
      replyText: (node) => <ReplyText node={node} store={textStore} />,
      replyVoice: (node) => <ReplyVoice node={node} recStore={recStore} />,
      playTime: (node) => <PlayTime node={node} store={playStore} dur={note.duration} />,
      tally: () => <Tally n={note.heardCount ?? 0} phone={phone} />,
      yoursBody: (node) =>
        note.mode === 'voice' ? (
          <div style={styleOf(node)}>
            <button type="button" onClick={togglePlay} className="ul" style={{ fontFamily: "'Nothing You Could Do', 'Caveat', cursive", fontSize: phone ? 22 : 28, color: INK }}>
              {playing ? '❚❚ listening…' : `▶ your voice · ${clock(note.duration)}`}
            </button>
          </div>
        ) : (
          <div style={{ ...styleOf(node), whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>{note.kind === 'unsent' && note.to ? `to ${note.to}, ` : ''}{note.text}</div>
        )
    };
  }, [note, replies, phone, now, player.playing, id, playReply, reportReply, removeReply, mineHere, textStore, recStore, playStore, togglePlay, playing]);

  const links = useMemo(() => ({ takeDown: takeItDown }), [takeItDown]);
  // The phone thread is one long board inside an absolutely placed frame, so it has to be told how tall
  // tonight's version is: header, the note, the replies, the composer. (Yours / unsent fit one screen.)
  const phoneMin = useMemo(() => {
    if (!note || !replies || mineHere || note.kind === 'unsent') return 0;
    const slips = replies.length ? replies.reduce((a, r) => a + slipHeight(r, true) + 22, 0) : 150;
    return Math.round(64 + 120 + cardHeight(note, true, 362) + 100 + 80 + slips + 132 + 40 + 60);
  }, [note, replies, mineHere]);
  const css = useMemo(() => {
    const d = Math.max(1, note?.duration || 29);
    return `.v5-phone{min-height:max(100dvh, ${phoneMin}px) !important}
.playing .played.main,.playing .phead{animation-duration:${d}s !important}
.slip .played.main{animation:none !important}
.slip.playing .played.main{animation:prog var(--dur,29s) linear forwards !important}
.nt-area::placeholder{color:${PENCIL};font-style:italic;opacity:1}`;
  }, [note?.duration, phoneMin]);

  if (data?.gone) return <Screen desktop={DX} phone={MX} />;
  if (!note) return <div style={{ minHeight: '100dvh', background: '#0D0D0E' }} />;
  if (mineHere) return <Screen desktop={DY} phone={MY} vals={vals} slots={slots} links={links} css={css} />;
  if (note.kind === 'unsent') return <Screen desktop={DU} phone={MU} vals={vals} slots={slots} css={css} />;
  if (!replies.length) return <Screen desktop={DN} phone={MN} vals={vals} slots={slots} css={css} />;
  return <Screen desktop={DT} phone={MT} vals={vals} slots={slots} css={css} />;
}

export default function Page() {
  return (
    <Guard>
      <Thread />
    </Guard>
  );
}
