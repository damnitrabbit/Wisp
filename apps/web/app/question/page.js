'use client';
// GROUP POD — tonight's question: one room, one question, up to eight people. You come in listening; join with voice
// when you like. Boards: V5Question / V5MQuestion, and V5QuestionEmpty when you're the first one here.
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { QUESTION_ROOM, questionFor } from '@wisp/shared/pods.js';
import Guard from '@/components/Guard';
import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Question';
import M from '@/v5/screens/V5MQuestion';
import DE from '@/v5/screens/V5QuestionEmpty';
import ME from '@/v5/screens/V5MQuestionEmpty';
import Asleep from '@/app/asleep/page';
import Tpl, { fill, CSS, Wrap } from '@/app/rooms/_parts/Tpl';
import { useRoom } from '@/app/rooms/_parts/useRoom';
import MicScreen from '@/app/rooms/_parts/MicScreens';
import { useWisp } from '@/lib/wisp';
import { podsOpen } from '@/lib/v5/hours';

const Ctx = createContext(null);
const CROWD = 6; // rows the paper is drawn for; it grows past that

function People({ node }) {
  const { room, phone } = useContext(Ctx);
  const { members, meId, speaking, snap } = room;
  const cap = snap?.cap ?? QUESTION_ROOM.cap;
  const list = [...members].sort((a, b) => (a.id === meId) - (b.id === meId) || a.joinedAt - b.joinedAt);
  const people = list.map((m) => {
    const st = m.role === 'listener' ? 'listening' : m.muted ? 'muted' : speaking.has(m.id) ? 'speaking' : 'listening';
    return fill(`${phone ? 'm' : 'd'}Person_${st}`, { name: m.name + (m.id === meId ? ' (you)' : '') });
  }).join('');
  const n = members.length;
  const count = n >= cap ? `${n} OF ${cap} · FULL` : `${n} OF ${cap} · ${cap - n} ${cap - n === 1 ? 'SEAT' : 'SEATS'} OPEN`;
  const html = fill(phone ? 'mQRoom' : 'dQRoom', { people, count, h: 410 + Math.max(0, n - CROWD) * 46 });
  return <Wrap node={node}><Tpl html={html} /></Wrap>;
}

function Buttons({ phone }) {
  const { room, onAct, full } = useContext(Ctx);
  const me = room.me;
  const voice = me && me.role !== 'listener';
  const a = full ? 'waiting for a seat' : voice ? (room.muted ? 'unmute' : 'mute') : 'join with voice';
  const b = voice ? 'just listen' : 'leave gently';
  return <Tpl html={fill(phone ? 'mQDock' : 'dQBtns', { a, b })} onAct={onAct} />;
}

const SLOTS = {
  qroom: (node) => <People node={node} />,
  qbtns: () => <Buttons />,
  qdock: () => <Buttons phone />
};

function Question() {
  const router = useRouter();
  const home = useCallback(() => router.push('/home'), [router]);
  const room = useRoom(QUESTION_ROOM.id, { onGone: home });
  const lobbyQ = useWisp((s) => s.lobby.question);
  const [stayed, setStayed] = useState(false);
  const [open, setOpen] = useState(true);
  const [phone, setPhone] = useState(false);
  useEffect(() => {
    document.title = "Tonight's question · NoTrace";
    const t = () => {
      setOpen(podsOpen());
      setPhone(window.innerWidth < 700 || (window.innerWidth < 1000 && window.innerHeight > window.innerWidth));
    };
    t();
    window.addEventListener('resize', t);
    const id = setInterval(t, 30_000);
    return () => { clearInterval(id); window.removeEventListener('resize', t); };
  }, []);

  // full: wait here, walk in when a seat opens
  const { phase, setPhase } = room;
  useEffect(() => {
    if (phase === 'full' && lobbyQ && lobbyQ.count < (lobbyQ.cap ?? QUESTION_ROOM.cap)) setPhase('joining');
  }, [phase, lobbyQ, setPhase]);
  useEffect(() => {
    if (phase === 'removed') router.replace('/home');
  }, [phase, router]);

  const { questionVoice, toggleMute, leave } = room;
  const voice = room.me && room.me.role !== 'listener';
  const full = phase === 'full';
  const onAct = useCallback((act) => {
    if (full) return null;
    if (act === 'a') return voice ? toggleMute() : questionVoice(true);
    if (act === 'b') return voice ? questionVoice(false) : leave();
    return null;
  }, [full, voice, toggleMute, questionVoice, leave]);

  const question = room.snap?.question || lobbyQ?.question || questionFor();
  const vals = useMemo(() => ({ question, me: room.me?.name ?? '' }), [question, room.me?.name]);
  const links = useMemo(() => ({ 'stay-a-while': () => setStayed(true) }), []);
  // while full, show who's in from the lobby
  const shown = useMemo(() => (full && lobbyQ ? { ...room, members: lobbyQ.members.map((m, i) => ({ ...m, id: `l${i}`, joinedAt: i })) } : room), [full, lobbyQ, room]);
  const ctx = useMemo(() => ({ room: shown, onAct, full, phone }), [shown, onAct, full, phone]);

  if (!open || phase === 'closed') return <Asleep />;
  if (room.noVoice) return <MicScreen which="novoice" crumb="tonight's question" mic={room.mic} onBack={() => room.setNoVoice(false)} />;
  if (room.mic.modal) return <MicScreen which={room.mic.modal} crumb="tonight's question" mic={room.mic} />;
  const alone = phase === 'in' && room.members.length === 1 && !stayed;
  if (alone) return <Screen desktop={DE} phone={ME} vals={vals} links={links} css={CSS} />;
  return (
    <Ctx.Provider value={ctx}>
      <Screen desktop={D} phone={M} vals={vals} slots={SLOTS} css={CSS} />
    </Ctx.Provider>
  );
}

export default function Page() {
  return (
    <Guard>
      <Question />
    </Guard>
  );
}
