'use client';
// The talk pod (and the listen pod): 1:1 text with an optional voice upgrade, drawn with the V5 screens.
// Logic (queue, voice consent, WebRTC) is the same as before; only the UI is new.
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { domToReact } from 'html-react-parser';
import Screen from '@/v5/Screen';
import Part, { Acts } from '@/app/talk/_pods/Part';
import P, { CSS as PART_CSS } from '@/app/talk/_pods/parts.gen';
import { emit, on, bus, syncClock, serverNow, useWisp } from '@/lib/wisp';
import { useMicFlow, micTrack, closeMic } from '@/lib/mic';
import { usePairCall } from '@/lib/call';
import { podsOpen as clientPodsOpen } from '@/lib/v5/hours';
import { podMinsToClose, POD_CLOSING_WARN_MIN } from '@wisp/shared/pods.js';

import DMatching from '@/v5/screens/V5Matching';
import MMatching from '@/v5/screens/V5MMatching';
import DPod from '@/v5/screens/V5Pod';
import MPod from '@/v5/screens/V5MPod';
import DNudge from '@/v5/screens/V5PodNudge';
import MNudge from '@/v5/screens/V5MPodNudge';
import DEnd from '@/v5/screens/V5PodEnd';
import MEnd from '@/v5/screens/V5MPodEnd';
import DRequeue from '@/v5/screens/V5Requeue';
import MRequeue from '@/v5/screens/V5MRequeue';
import DReported from '@/v5/screens/V5Reported';
import MReported from '@/v5/screens/V5MReported';
import DVoiceWait from '@/v5/screens/V5VoiceWait';
import MVoiceWait from '@/v5/screens/V5MVoiceWait';
import DVoiceAsk from '@/v5/screens/V5VoiceAsk';
import MVoiceAsk from '@/v5/screens/V5MVoiceAsk';
import DCall from '@/v5/screens/V5Call';
import MCall from '@/v5/screens/V5MCall';
import DDropped from '@/v5/screens/V5CallDropped';
import MDropped from '@/v5/screens/V5MCallDropped';
import DClosing from '@/v5/screens/V5PodsClosing';
import MClosing from '@/v5/screens/V5MPodsClosing';
import DClosedMid from '@/v5/screens/V5PodsClosedMidChat';
import MClosedMid from '@/v5/screens/V5MPodsClosedMidChat';
import DNoOne from '@/v5/screens/V5NoOneFree';
import MNoOne from '@/v5/screens/V5MNoOneFree';
import DListener from '@/v5/screens/V5Listener';
import MListener from '@/v5/screens/V5MListener';
import DPaused from '@/v5/screens/V5Paused';
import MPaused from '@/v5/screens/V5MPaused';
import DReconnect from '@/v5/screens/V5Reconnect';
import MReconnect from '@/v5/screens/V5MReconnect';
import DMicAsk from '@/v5/screens/V5MicAsk';
import MMicAsk from '@/v5/screens/V5MMicAsk';
import DMicBlocked from '@/v5/screens/V5MicBlocked';
import MMicBlocked from '@/v5/screens/V5MMicBlocked';
import DNoVoice from '@/v5/screens/V5NoVoice';
import MNoVoice from '@/v5/screens/V5MNoVoice';

const NOBODY_AFTER_MS = 3 * 60_000; // "nobody's free right now" after this long looking
const NUDGE_EVERY_MS = 10 * 60_000; // the 10 minute check-in

let seq = 0;
const nid = () => `l${++seq}`;
const clock = (t = Date.now()) => {
  const d = new Date(t);
  return `${d.getHours() % 12 || 12}:${String(d.getMinutes()).padStart(2, '0')}`;
};
const clockAmPm = (t = Date.now()) => `${clock(t)} ${new Date(t).getHours() < 12 ? 'AM' : 'PM'}`;
const mmss = (ms) => {
  const s = Math.max(0, Math.round(ms / 1000));
  return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
};
const m_ss = (ms) => {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
};

export function styleObj(css = '') {
  const o = {};
  for (const decl of css.split(';')) {
    const i = decl.indexOf(':');
    if (i < 0) continue;
    const k = decl.slice(0, i).trim();
    if (!k) continue;
    const key = k.startsWith('--') ? k : k.replace(/^-(webkit|moz|ms)-/, (m, p) => `${p[0].toUpperCase()}${p.slice(1)}-`).replace(/-([a-z])/g, (m, c) => c.toUpperCase());
    o[key] = decl.slice(i + 1).trim();
  }
  return o;
}
const tags = (node) => (node.children || []).filter((c) => c.type === 'tag');

// ---------- live slots (they read the pod from context, so the screen itself doesn't re-parse) ----------
const PodCtx = createContext(null);

function Msgs(node) {
  return <MsgList base={node.attribs.style} />;
}
function MsgList({ base }) {
  const c = useContext(PodCtx);
  const ref = useRef(null);
  const pin = useRef(true);
  const k = c.phone ? 'm' : 'd';
  useEffect(() => {
    const el = ref.current;
    if (el && pin.current) el.scrollTop = el.scrollHeight;
  }, [c.items, c.typing]);
  const style = { ...styleObj(base), overflowY: 'auto', overflowX: 'hidden', justifyContent: 'flex-start', scrollbarWidth: 'none', overscrollBehavior: 'contain' };
  const pv = { partner: c.partner, PARTNER: c.partner.toUpperCase() };
  return (
    <div className="scroll" ref={ref} style={style} role="log" aria-label="Conversation" aria-live="polite"
      onScroll={(e) => { const el = e.currentTarget; pin.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40; }}>
      <div style={{ marginTop: 'auto' }} />
      {c.items.map((m) => {
        const tpl = m.kind === 'me' ? P[k + 'Mine'] : m.kind === 'them' ? P[k + 'Theirs'] : m.kind === 'sys' ? P[k + 'Sys'] : m.kind === 'fail' ? P[k + 'Fail'] : P[k + 'Pencil'];
        return <Part key={m.id} html={tpl} vals={{ ...pv, text: m.text, t: m.t }} acts={m.kind === 'fail' ? { retry: () => c.retry(m) } : undefined} />;
      })}
      {c.typing && <Part html={P[k + 'Typing']} vals={pv} />}
    </div>
  );
}

function Composer(node) {
  return <ComposerRow node={node} />;
}
function ComposerRow({ node }) {
  const c = useContext(PodCtx);
  const kids = tags(node);
  const ph = kids[0];
  const right = kids[kids.length - 1];
  const input = useRef(null);
  const phStyle = styleObj(ph?.attribs?.style);
  const submit = (e) => {
    e?.preventDefault();
    c.send();
    input.current?.focus();
  };
  return (
    <form data-slot-live="composer" style={styleObj(node.attribs.style)} onSubmit={submit}>
      <input ref={input} value={c.draft} onChange={(e) => c.onDraft(e.target.value)} maxLength={500} autoComplete="off" enterKeyHint="send"
        aria-label="Message" placeholder="say it however it comes out…" className="pod-input"
        style={{ ...phStyle, flex: '1 1 auto', minWidth: 0, background: 'transparent', border: 0, outline: 'none', padding: '6px 0', color: '#221E1A', fontStyle: c.draft ? 'normal' : 'italic' }} />
      <span style={{ display: 'contents' }} onClickCapture={(e) => { if (e.target.closest('a')) submit(e); }}>
        {right && right !== ph ? domToReact([right]) : null}
      </span>
    </form>
  );
}

function Checkin() {
  const c = useContext(PodCtx);
  const [, tick] = useState(0);
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 1000);
    return () => clearInterval(t);
  }, []);
  return <span>{c.nudgeAt ? m_ss(c.nudgeAt - Date.now()) : '—'}</span>;
}
function CallTimer() {
  const c = useContext(PodCtx);
  const [, tick] = useState(0);
  useEffect(() => {
    const t = setInterval(() => tick((n) => n + 1), 1000);
    return () => clearInterval(t);
  }, []);
  return <span>{c.callSince ? mmss(Date.now() - c.callSince) : '00:00'}</span>;
}
const SLOTS = { msgs: Msgs, composer: Composer, checkin: <Checkin />, calltimer: <CallTimer /> };
const POD_EXTRA_CSS = PART_CSS + `
.pod-input::placeholder{color:#5F584E;font-style:italic;opacity:1}
[data-slot-live="composer"] .blink{display:none}`;

// ---------- the pod ----------
export default function Chat({ role = 'talk' }) {
  const router = useRouter();
  const session = useWisp((s) => s.session);
  const status = useWisp((s) => s.status);
  const lobby = useWisp((s) => s.lobby);
  const me = session?.name ?? 'you';

  const [phase, setPhase] = useState(role === 'listen' ? 'intro' : 'matching');
  // intro | matching | requeue | nobody | chat | ended | reported | closed | paused
  const [since, setSince] = useState(() => Date.now());
  const [pair, setPair] = useState(null);
  const [items, setItems] = useState([]);
  const [typing, setTyping] = useState(false);
  const [draft, setDraft] = useState('');
  const [voice, setVoice] = useState('off'); // off | asked | incoming | on
  const [polite, setPolite] = useState(true);
  const [track, setTrack] = useState(null);
  const [muted, setMuted] = useState(false);
  const [away, setAway] = useState(false);
  const [dropped, setDropped] = useState(null); // time the voice line dropped
  const [callSince, setCallSince] = useState(null);
  const [nudgeAt, setNudgeAt] = useState(null);
  const [nudge, setNudge] = useState(false);
  const [noVoice, setNoVoice] = useState(false);
  const [left, setLeft] = useState(null); // { name, at } when they left
  const [ended, setEnded] = useState(null); // PodEnd numbers
  const [closingAt, setClosingAt] = useState(null);
  const mic = useMicFlow();
  const sentTyping = useRef(0);
  const typingTimer = useRef(null);
  const phaseRef = useRef(phase);
  phaseRef.current = phase;
  const itemsRef = useRef(items);
  itemsRef.current = items;

  const open = lobby?.pods ? lobby.pods.open : clientPodsOpen();

  const add = (kind, text, t) => setItems((l) => [...l, { id: nid(), kind, text, t: t ?? clock() }]);

  const resetChat = useCallback(() => {
    setPair(null);
    setItems([]);
    setTyping(false);
    setVoice('off');
    setTrack(null);
    setMuted(false);
    setAway(false);
    setDropped(null);
    setCallSince(null);
    setNudge(false);
    setNudgeAt(null);
    setClosingAt(null);
    closeMic();
  }, []);

  const startLooking = useCallback(async (next = 'matching') => {
    const r = await emit('pair:join', { role });
    if (r.error === 'blocked') return setPhase('paused');
    if (r.error === 'closed') return router.replace('/asleep');
    if (r.error) return;
    if (!r.pairId) {
      setSince(Date.now());
      setPhase((p) => (p === 'chat' ? p : next));
    }
  }, [role, router]);

  // ---------- server events ----------
  useEffect(() => {
    document.title = role === 'listen' ? 'Listen pod · NoTrace' : 'Talk pod · NoTrace';
    const offs = [
      on('pair:waiting', () => setSince((s) => s ?? Date.now())),
      on('pair:matched', (p) => {
        syncClock(p.serverNow);
        resetChat();
        setPair(p);
        setNudgeAt(Date.now() + NUDGE_EVERY_MS - (serverNow() - p.startedAt));
        setPhase('chat');
      }),
      on('pair:message', (m) => {
        setTyping(false);
        setItems((l) => [...l, { id: m.id, kind: 'them', text: m.text, t: clock(m.at) }]);
      }),
      on('pair:typing', ({ on: t }) => {
        setTyping(t);
        clearTimeout(typingTimer.current);
        if (t) typingTimer.current = setTimeout(() => setTyping(false), 5000);
      }),
      on('pair:partnerLeft', (p) => {
        resetChat();
        setLeft({ name: p.name, at: Date.now() });
        setSince(Date.now());
        setPhase('requeue'); // the server already put us back in line
      }),
      on('pair:partnerAway', () => setAway(true)),
      on('pair:partnerBack', () => setAway(false)),
      on('pair:blocked', () => {
        resetChat();
        setPhase('paused');
      }),
      on('pair:voiceRequested', (p) => {
        syncClock(p.serverNow);
        setVoice('incoming');
        add('sys', `${clock()} · ${p.name} asked for voice`);
      }),
      on('pair:voiceWithdrawn', () => setVoice((v) => (v === 'incoming' ? 'off' : v))),
      on('pair:voiceDeclined', (p) => {
        setVoice('off');
        add('pencil', p.reason === 'expired' ? "no answer this time. you can ask again later." : "they'd like to keep it to text. that's okay.");
        closeMic();
        setTrack(null);
      }),
      on('pair:voiceStarted', ({ polite: pol }) => {
        setPolite(pol);
        setVoice('on');
        setDropped(null);
        setCallSince(Date.now());
      }),
      on('pair:voiceEnded', ({ by }) => {
        setVoice('off');
        setMuted(false);
        setCallSince(null);
        closeMic();
        setTrack(null);
        add('sys', `${clock()} · ${by === 'you' ? 'back to text' : 'they went back to text'}`);
      }),
      on('pods:closed', () => {
        closeMic();
        setPhase((p) => (p === 'chat' ? 'closed' : p));
        if (phaseRef.current !== 'chat') router.replace('/asleep');
      }),
      bus.on('session', ({ fresh }) => {
        // The server forgot us (a long drop): whatever pod we had is gone. Look again.
        if (fresh && ['chat', 'matching', 'requeue', 'nobody'].includes(phaseRef.current)) {
          resetChat();
          startLooking();
        }
      })
    ];
    return () => offs.forEach((f) => f());
  }, [role, resetChat, startLooking, router]);

  // First visit: start looking (talk), or wait for "I'm ready" (listen). Resume a live pod after a reload.
  const started = useRef(false);
  useEffect(() => {
    if (started.current || !session) return;
    started.current = true;
    if (session.pair) {
      setPair(session.pair);
      setNudgeAt(Date.now() + NUDGE_EVERY_MS - (serverNow() - session.pair.startedAt));
      setPhase('chat');
    } else if (role !== 'listen') startLooking();
  }, [session, role, startLooking]);

  // Outside pod hours there's nothing to join.
  useEffect(() => {
    if (lobby?.pods && !lobby.pods.open && phaseRef.current !== 'closed' && phaseRef.current !== 'ended' && phaseRef.current !== 'reported') router.replace('/asleep');
  }, [lobby?.pods, router]);

  useEffect(() => () => {
    emit('pair:leave');
    closeMic();
  }, []);

  // looking for a long time -> "nobody's free"; the 10 minute check-in; the closing slip
  useEffect(() => {
    const t = setInterval(() => {
      const p = phaseRef.current;
      if ((p === 'matching' || p === 'requeue') && Date.now() - since > NOBODY_AFTER_MS) setPhase('nobody');
      if (p === 'chat' && nudgeAt && Date.now() >= nudgeAt) {
        setNudge(true);
        setNudgeAt(Date.now() + NUDGE_EVERY_MS);
      }
      if (p === 'chat' && !closingAt) {
        const left = lobby?.pods?.minsToClose ?? podMinsToClose();
        if (left && left <= POD_CLOSING_WARN_MIN && (lobby?.pods?.minsToClose != null)) setClosingAt(clockAmPm());
      }
    }, 1000);
    return () => clearInterval(t);
  }, [since, nudgeAt, closingAt, lobby?.pods]);

  const call = usePairCall({ active: voice === 'on', polite, track, muted });
  // The line couldn't hold: back to text, say so.
  useEffect(() => {
    if (voice === 'on' && call.state === 'failed') {
      emit('pair:voiceEnd');
      setDropped(clockAmPm());
      add('sys', `${clock()} · the voice line dropped`);
    }
  }, [call.state, voice]);

  // ---------- actions ----------
  const send = useCallback(async (retryOf) => {
    const text = (retryOf ? retryOf.text : draft).trim();
    if (!text) return;
    if (!retryOf) setDraft('');
    sentTyping.current = 0;
    const r = await emit('pair:message', { text });
    if (r.ok) {
      setItems((l) => {
        const rest = retryOf ? l.filter((m) => m.id !== retryOf.id) : l;
        return [...rest, { id: r.id, kind: 'me', text: text.replace(/\s+/g, ' '), t: clock(r.at) }];
      });
      setDropped(null);
    } else if (r.error === 'slow') {
      if (!retryOf) setDraft(text);
    } else if (r.error === 'too_long') {
      if (!retryOf) setDraft(text.slice(0, 500));
    } else if (!retryOf) {
      add('fail', text);
    }
  }, [draft]);
  const onDraft = useCallback((v) => {
    setDraft(v);
    const now = Date.now();
    if (v && now - sentTyping.current > 2500) {
      sentTyping.current = now;
      emit('pair:typing', { on: true });
    }
  }, []);

  const leaveGently = useCallback(() => {
    const list = itemsRef.current;
    const lastTheirs = [...list].reverse().find((m) => m.kind === 'them');
    const n = list.filter((m) => m.kind === 'me' || m.kind === 'them').length;
    const mins = pair ? Math.max(1, Math.round((serverNow() - pair.startedAt) / 60000)) : 0;
    setEnded({ mins, n, last: lastTheirs?.text ?? null, partner: pair?.partner?.name ?? 'them' });
    emit('pair:leave');
    resetChat();
    setPhase('ended');
  }, [pair, resetChat]);
  const report = useCallback(async () => {
    await emit('pair:report', { requeue: false });
    resetChat();
    setPhase('reported');
  }, [resetChat]);
  const again = useCallback(() => {
    resetChat();
    setLeft(null);
    setSince(Date.now());
    setPhase('matching');
    startLooking();
  }, [resetChat, startLooking]);

  const voiceSupported = () => typeof window !== 'undefined' && !!(navigator.mediaDevices?.getUserMedia && window.RTCPeerConnection);
  const askVoice = useCallback(async () => {
    if (voice !== 'off') return;
    if (!voiceSupported()) return setNoVoice(true);
    const ok = await mic.ask();
    if (!ok) return;
    setTrack(micTrack());
    const r = await emit('pair:voiceRequest');
    if (r.ok) {
      setVoice('asked');
      setDropped(null);
      add('sys', `${clock()} · you asked for voice`);
    }
  }, [voice, mic]);
  const cancelVoice = useCallback(() => {
    emit('pair:voiceCancel');
    setVoice('off');
    closeMic();
    setTrack(null);
  }, []);
  const answerVoice = useCallback(async (yes) => {
    if (!yes || !voiceSupported()) {
      setVoice('off');
      if (yes) setNoVoice(true);
      return emit('pair:voiceDecline');
    }
    const ok = await mic.ask();
    if (!ok) {
      setVoice('off');
      return emit('pair:voiceDecline');
    }
    setTrack(micTrack());
    emit('pair:voiceAccept');
  }, [mic]);
  const endCall = useCallback(() => emit('pair:voiceEnd'), []);

  // ---------- what's on screen ----------
  const partner = pair?.partner?.name ?? '…';
  const myRole = pair?.role ?? role;
  const theirRole = pair?.partner?.role;
  const lead = myRole === 'listen' ? 'they lead.' : theirRole === 'talk' && myRole === 'talk' ? 'take turns.' : 'you lead.';
  const statusText = away ? 'RECONNECTING…' : myRole === 'listen' ? "YOU'RE LISTENING" : theirRole === 'talk' && myRole === 'talk' ? 'TAKING TURNS' : "THEY'RE LISTENING";

  const vals = useMemo(() => ({
    partner, PARTNER: partner.toUpperCase(), me, ME: me.toUpperCase(),
    joined: pair ? clockAmPm(pair.startedAt - (serverNow() - Date.now())) : clockAmPm(),
    status: statusText, lead,
    slipAt: dropped || closingAt || clockAmPm(),
    together: pair ? `${Math.max(1, Math.round((serverNow() - pair.startedAt) / 60000))} MIN TOGETHER` : '',
    callState: call.state === 'live' ? 'ON VOICE' : call.state === 'failed' ? 'LINE DROPPED' : 'CONNECTING…',
    themState: call.speaking.has('partner') ? 'SPEAKING' : 'LISTENING',
    meState: muted ? 'MUTED' : call.speaking.has('me') ? 'SPEAKING' : 'LISTENING',
    muteLabel: muted ? 'unmute' : 'mute',
    // matching / requeue / end
    matchTitle: role === 'listen' ? 'Finding someone to listen to…' : "Finding someone who'll listen…",
    awake: role === 'listen'
      ? `${Math.max(0, (lobby?.waiting ?? 0) - (lobby?.listeners ?? 0))} WAITING TO TALK`
      : lobby?.listeners ? `${lobby.listeners} ${lobby.listeners === 1 ? 'LISTENER' : 'LISTENERS'} AWAKE` : 'A QUIET NIGHT SO FAR',
    leftAt: left ? clockAmPm(left.at) : '',
    looked: `LOOKED FOR ${Math.max(1, Math.round((Date.now() - since) / 60000))} MINUTES`,
    stats: ended ? `${ended.mins} ${ended.mins === 1 ? 'MINUTE' : 'MINUTES'} · ${ended.n} ${ended.n === 1 ? 'MESSAGE' : 'MESSAGES'} · 0 KEPT` : '',
    lastLabel: ended?.last ? `${ended.partner.toUpperCase()}'S LAST WORDS` : 'FROM US',
    lastWords: ended?.last ?? 'you showed up tonight. that counts.'
  }), [partner, me, pair, statusText, lead, dropped, closingAt, call.state, call.speaking, muted, role, lobby?.waiting, lobby?.listeners, left, since, ended]);
  // the requeue screen talks about the person who left
  const requeueVals = useMemo(() => ({ ...vals, partner: left?.name ?? 'they', PARTNER: (left?.name ?? 'they').toUpperCase() }), [vals, left]);

  const ctx = useMemo(() => ({
    phone: false, items, typing: typing && voice !== 'on', partner, draft, onDraft, send: () => send(), retry: (m) => send(m), nudgeAt, callSince
  }), [items, typing, voice, partner, draft, onDraft, send, nudgeAt, callSince]);

  const links = useMemo(() => ({
    VoiceWait: askVoice,
    PodEnd: leaveGently,
    Reported: report,
    Matching: again,
    'keep-going': () => setNudge(false),
    mutelabel: () => setMuted((m) => !m),
    Pod: voice === 'incoming' ? () => answerVoice(false) : voice === 'asked' ? cancelVoice : voice === 'on' ? endCall : () => {},
    Call: () => answerVoice(true)
  }), [askVoice, leaveGently, report, again, voice, answerVoice, cancelVoice, endCall]);

  const micActs = useMemo(() => ({
    'allow mic': () => mic.allow(),
    'stay on text': () => mic.decline(),
    reload: () => window.location.reload(),
    'continue on text': () => setNoVoice(false)
  }), [mic]);
  const reconnectActs = useMemo(() => ({ 'leave gently': leaveGently }), [leaveGently]);

  // which board
  let D, M, v = vals, acts = null;
  if (phase === 'intro') [D, M] = [DListener, MListener];
  else if (phase === 'matching') [D, M] = [DMatching, MMatching];
  else if (phase === 'requeue') [D, M, v] = [DRequeue, MRequeue, requeueVals];
  else if (phase === 'nobody') [D, M] = [DNoOne, MNoOne];
  else if (phase === 'ended') [D, M] = [DEnd, MEnd];
  else if (phase === 'reported') [D, M] = [DReported, MReported];
  else if (phase === 'paused') [D, M] = [DPaused, MPaused];
  else if (phase === 'closed') [D, M] = [DClosedMid, MClosedMid];
  else if (status === 'reconnecting') [D, M, acts] = [DReconnect, MReconnect, reconnectActs];
  else if (mic.modal === 'ask') [D, M, acts] = [DMicAsk, MMicAsk, micActs];
  else if (mic.modal === 'blocked') [D, M, acts] = [DMicBlocked, MMicBlocked, micActs];
  else if (noVoice) [D, M, acts] = [DNoVoice, MNoVoice, micActs];
  else if (voice === 'on') [D, M] = [DCall, MCall];
  else if (voice === 'incoming') [D, M] = [DVoiceAsk, MVoiceAsk];
  else if (nudge) [D, M] = [DNudge, MNudge];
  else if (voice === 'asked') [D, M] = [DVoiceWait, MVoiceWait];
  else if (dropped) [D, M] = [DDropped, MDropped];
  else if (closingAt) [D, M] = [DClosing, MClosing];
  else [D, M] = [DPod, MPod];

  return (
    <PodCtxBridge ctx={ctx}>
      <Acts acts={acts || {}}>
        <Screen desktop={D} phone={M} vals={v} slots={SLOTS} links={links} css={POD_EXTRA_CSS} />
      </Acts>
    </PodCtxBridge>
  );
}

// Tells the slots whether the phone or desktop board is showing (their markup differs).
function PodCtxBridge({ ctx, children }) {
  const [phone, setPhone] = useState(false);
  useEffect(() => {
    const f = () => {
      const w = window.innerWidth, h = window.innerHeight;
      setPhone(w < 700 || (w < 1000 && h > w));
    };
    f();
    window.addEventListener('resize', f);
    return () => window.removeEventListener('resize', f);
  }, []);
  const value = useMemo(() => ({ ...ctx, phone }), [ctx, phone]);
  return <PodCtx.Provider value={value}>{children}</PodCtx.Provider>;
}
