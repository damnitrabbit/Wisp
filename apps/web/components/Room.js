'use client';
// OPEN POD — inside a room. One design board (V5Room on desktop, V5MRoom on phone); its columns are slots filled with
// the generated parts (stage cards, listeners, the notes on the right), so every state looks like the designed ones:
// mod view (V5Room), invited up (V5RoomHand), moved off stage (V5MovedOffStage), alone in the room (V5RoomAlone).
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import Screen from '@/v5/Screen';
import DRoom from '@/v5/screens/V5Room';
import MRoom from '@/v5/screens/V5MRoom';
import Asleep from '@/app/asleep/page';
import Tpl, { fill, CSS, Wrap } from '@/app/rooms/_parts/Tpl';
import { roomTitle, roomTheme } from '@/app/rooms/_parts/names';
import { useRoom, onStage } from '@/app/rooms/_parts/useRoom';
import MicScreen from '@/app/rooms/_parts/MicScreens';
import { useNow } from '@/lib/time';
import { podsOpen } from '@/lib/v5/hours';

const CAP = 10;
const SEATS = 4;
const m_ss = (ms) => {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
};
// names are drawn at the design's size; long ones shrink a little so they stay on their card
const fitName = (name, phone) => {
  const [size, fits, min] = phone ? [19, 12, 14] : [25, 14, 18];
  const n = String(name).length;
  return n <= fits ? size : Math.max(min, Math.round((size * fits) / n));
};
const ROOM_CSS = CSS + '\n[data-act]{cursor:pointer}';
const NO_VALS = {};

const Ctx = createContext(null);

// ---------- what the room looks like right now (shared by the desktop and phone boards) ----------
function useView(room, channel, picked, reporting, now) {
  const { me, members, speaking, invite, note, reported, muted } = room;
  const meMod = me?.role === 'mod';
  const stage = members.filter(onStage).sort((a, b) => (b.founding - a.founding) || ((a.role === 'mod' ? 0 : 1) - (b.role === 'mod' ? 0 : 1)) || a.stageSince - b.stageSince);
  const listeners = members.filter((m) => !onStage(m)).sort((a, b) => a.joinedAt - b.joinedAt);
  const alone = Boolean(me) && members.length === 1;
  const hands = listeners.filter((m) => m.handUp && m.id !== me?.id).sort((a, b) => a.handExpiresAt - b.handExpiresAt);
  const pending = listeners.filter((m) => m.invitedUntil && m.invitedUntil > now);
  const pick = picked && listeners.find((m) => m.id === picked);

  const tag = (m, i, phone) => {
    const state = m.muted ? 'muted' : speaking.has(m.id) ? 'speaking' : 'listening';
    const you = m.id === me?.id;
    return fill(`${phone ? 'm' : 'd'}Tag_${state}_${i}`, {
      name: m.name, id: m.id, mod: m.role === 'mod', me: you, fs: fitName(m.name, phone),
      canMove: meMod && !reporting && !you && m.role === 'speaker',
      canReport: reporting && !you && !reported.has(m.id)
    });
  };
  const stageHtml = (phone) => {
    const tags = stage.slice(0, SEATS).map((m, i) => tag(m, i, phone)).join('')
      + Array.from({ length: Math.max(0, SEATS - stage.length) }, (_, i) => fill(`${phone ? 'm' : 'd'}Empty${stage.length + i}`)).join('');
    const items = listeners.map((m) => {
      const you = m.id === me?.id;
      const canRep = reporting && !you && !reported.has(m.id);
      return fill(phone ? 'mLi' : 'dLi', { name: m.name, id: m.id, hand: m.handUp, you, rep: canRep, act: canRep ? 'report' : meMod && !you && !reporting ? 'pick' : '' });
    }).join('');
    const open = Math.max(0, CAP - members.length);
    const n = stage.length;
    return fill(phone ? 'mStage' : 'dStage', {
      tags,
      count: phone ? (n >= SEATS ? `${n} ON STAGE` : `${n} ON STAGE · ${SEATS - n} OPEN`) : n >= SEATS ? `${n} ON STAGE · MODS CHOOSE WHO COMES UP` : `${n} ON STAGE · ${SEATS - n} SEATS OPEN`,
      listeners: listeners.length ? fill(phone ? 'mLiRow' : 'dLiRow', { items }) : fill(phone ? 'mLiNone' : 'dLiNone'),
      lcount: phone && !listeners.length ? '0 HERE' : `${listeners.length} HERE · ${open} ${open === 1 ? 'SEAT' : 'SEATS'} OPEN`
    });
  };

  // the note on the right (desktop) / the pinned slip (phone)
  let right;
  const first = hands[0];
  if (invite && me && !onStage(me)) right = { kind: 'invite', from: invite.from };
  else if (reporting) right = { kind: 'note', kicker: 'REPORT SOMEONE', title: 'Who is it?', body: "Tap REPORT by their name. Enough reports here and they're removed.", action: 'NEVER MIND', act: 'cancelreport', foot: 'ONE REPORT PER PERSON. NOTHING ELSE IS KEPT.' };
  else if (note) right = noteFor(note, me);
  if (!right && me) {
    if (meMod && alone) right = { kind: 'alone' };
    else if (meMod && pick) right = { kind: 'hand', mark: 'listening', name: pick.name, id: pick.id, body: stage.length >= SEATS ? 'could come up when a seat opens.' : 'could be invited up to speak.', chips: stage.length < SEATS, yes: 'invite up', no: 'not now', yesAct: 'invite', noAct: 'unpick', t: '', foot: 'THEY CHOOSE WHETHER TO COME UP. THEIR MIC IS ASKED ONLY THEN.' };
    else if (meMod && first) right = { kind: 'hand', mark: 'a hand is up', name: first.name, id: first.id, body: stage.length >= SEATS ? 'would like to speak. the stage is full: move someone off first.' : 'would like to come up and speak.', chips: true, yes: 'invite up', no: 'not now', yesAct: 'approve', noAct: 'decline', t: m_ss(first.handExpiresAt - now), next: hands[1]?.name, foot: 'THEY CHOOSE WHETHER TO COME UP. THEIR MIC IS ASKED ONLY THEN.' };
    else if (meMod && pending[0]) right = { kind: 'hand', mark: 'invite sent', name: pending[0].name, id: pending[0].id, body: 'was asked up. waiting for their answer.', chips: false, t: m_ss(pending[0].invitedUntil - now), foot: 'NO ANSWER AND THEY STAY A LISTENER. NOTHING HAPPENS.' };
    else if (meMod) right = { kind: 'note', kicker: 'MOD · ON STAGE', title: 'You let people up.', body: 'Raised hands show here. Tap a name under listening to invite them up.', foot: 'ONLY REPORTS CAN REMOVE A MOD.', under: 'one at a time. no one is rushed off.' };
    else if (me.role === 'speaker') right = { kind: 'note', kicker: muted ? 'ON STAGE · MUTED' : 'ON STAGE · MIC ON', title: 'The room can hear you.', body: 'Say as much or as little as you like. A mod can move you back to listening.', action: 'STEP DOWN', act: 'stepdown', foot: me.promoteAt ? `STAY ${m_ss(me.promoteAt - now)} MORE AND YOU BECOME A MOD.` : 'STEP DOWN ANY TIME.' };
    else if (me.handUp) right = { kind: 'note', kicker: `HAND UP · ${m_ss(me.handExpiresAt - now)}`, title: 'Your hand is up.', body: 'The mods can see it. If one lets you up, your mic is asked then.', action: 'LOWER HAND', act: 'lower', hand: true, foot: 'NO ANSWER IN 30 SECONDS AND IT GOES DOWN ON ITS OWN.' };
    else right = { kind: 'note', kicker: 'YOU · MIC OFF', title: "You're listening.", body: "Nobody can hear you. Raise a hand if you'd like to speak.", action: 'RAISE HAND', act: 'raise', hand: true, foot: "A MOD LETS YOUR HAND UP WHEN THERE'S ROOM.", under: 'listening is enough too.' };
  }

  // the "you" box on the room card (desktop) / words under the title (phone)
  let you = '', youPhone = '';
  if (me) {
    if (invite && !onStage(me)) {
      you = fill('dYouHand', { from: invite.from });
      youPhone = fill('mRightText', { text: "YOU'RE LISTENING" });
    } else if (meMod && alone) {
      you = fill('dYouFirst');
      youPhone = fill('mRightFirst');
    } else if (meMod) {
      you = fill('dYouMod', { body: me.founding ? 'You opened this room. You let people up, and help them down.' : 'Earned by being kind in rooms like this. You let people up, and help them down.' });
      youPhone = fill('mRightMod');
    } else if (me.role === 'speaker') {
      you = fill('dYouPlain', { title: 'on stage', body: me.promoteAt ? `The room can hear you. In ${m_ss(me.promoteAt - now)} you become a mod.` : 'The room can hear you.' });
      youPhone = fill('mRightText', { text: 'ON STAGE' });
    } else {
      you = fill('dYouPlain', { title: 'listening', body: note?.kind === 'demoted' ? "Your mic is off. Raise a hand whenever you'd like to speak again." : "Your mic is off. Raise a hand whenever you'd like to speak." });
      youPhone = fill('mRightText', { text: me.handUp ? 'HAND UP' : "YOU'RE LISTENING" });
    }
  }
  return { me, meMod, stage, listeners, right, you, youPhone, stageHtml, n: members.length, onStageMe: onStage(me) };
}

function noteFor(note, me) {
  const n = note.name;
  switch (note.kind) {
    case 'demoted':
      return onStage(me) ? null : { kind: 'note', kicker: 'OFF STAGE · MIC OFF', title: "You're listening again.", body: 'A mod moved you off stage. It happens, no reason needed.', action: 'RAISE HAND AGAIN', act: 'raise', hand: true, foot: "A MOD LETS YOUR HAND UP WHEN THERE'S ROOM.", under: 'listening is enough too.' };
    case 'declined':
      return { kind: 'note', kicker: 'HAND DOWN', title: 'Not right now.', body: 'A mod said not now. You can raise your hand again in a few seconds.', foot: 'IT HAPPENS. NO REASON NEEDED.', under: 'listening is enough too.' };
    case 'expired':
      return { kind: 'note', kicker: 'HAND DOWN', title: 'Your hand went down.', body: 'Nobody answered in 30 seconds. Raise it again any time.', action: 'RAISE HAND', act: 'raise', hand: true, foot: "A MOD LETS YOUR HAND UP WHEN THERE'S ROOM." };
    case 'cooldown':
      return { kind: 'note', kicker: 'HAND DOWN', title: 'Give it a moment.', body: 'Wait a few seconds before raising your hand again.', foot: 'NO ONE IS RUSHED.' };
    case 'approved':
      return { kind: 'note', kicker: 'ON STAGE · MIC ON', title: "You're on stage.", body: `${n} let you up. The room can hear you now.`, action: 'STEP DOWN', act: 'stepdown', foot: 'STEP DOWN ANY TIME.' };
    case 'promoted':
      return { kind: 'note', kicker: 'MOD', title: "You're a mod now.", body: 'You can let raised hands up, invite listeners, and move speakers back to listening.', foot: 'ONLY REPORTS CAN REMOVE A MOD.' };
    case 'succession':
      return { kind: 'note', kicker: 'NEW MOD', title: `${n} is a mod now.`, body: 'A mod left, so the longest on stage holds the door.', foot: 'NO ONE IS RUSHED OFF.' };
    case 'inviteDeclined':
      return { kind: 'note', kicker: 'INVITE', title: `${n} said not now.`, body: "They're still listening. That's okay.", foot: 'LISTENING IS ENOUGH TOO.' };
    case 'inviteExpired':
      return { kind: 'note', kicker: 'INVITE', title: 'No answer.', body: `${n} didn't answer in time, so they're still listening.`, foot: 'NOTHING HAPPENS IF NOBODY ANSWERS.' };
    case 'stageFull':
      return { kind: 'note', kicker: 'STAGE FULL', title: 'Four on stage.', body: 'A seat opens when a speaker steps down or a mod moves someone off.', foot: 'ONE AT A TIME.' };
    case 'reported':
      return { kind: 'note', kicker: 'REPORTED', title: 'Thank you.', body: `If enough people here report ${n}, they're removed automatically.`, foot: 'NOTHING ELSE IS KEPT.' };
    default:
      return null;
  }
}

function rightHtml(r, phone) {
  if (!r) return '';
  if (r.kind === 'invite') return fill(phone ? 'mSlipInvite' : 'dRightInvite', { FROM: r.from.toUpperCase() });
  if (r.kind === 'alone') return fill(phone ? 'mSlipAlone' : 'dRightAlone');
  if (r.kind === 'hand') {
    const t = phone ? [r.t, r.next ? `NEXT: ${r.next.toUpperCase()}` : ''].filter(Boolean).join(' · ') : r.t;
    return fill(phone ? 'mSlipHand' : 'dRightHand', { ...r, t, NEXT: r.next?.toUpperCase(), no: phone ? r.no : r.no?.toUpperCase() });
  }
  return fill(phone ? 'mSlipNote' : 'dRightNote', r);
}

// ---------- slot components (stable; they read the live room from context) ----------
function Card({ node }) {
  const { view, channel, reporting, muted } = useContext(Ctx);
  const html = fill('dCard', {
    title: roomTitle(channel), theme: roomTheme(channel), n: view.n, cdots: fill(`dCDots${Math.min(CAP, view.n)}`),
    you: view.you, btns: view.onStageMe ? fill('dBtnMute', { muteLabel: muted ? 'unmute' : 'mute' }) : '',
    h: view.onStageMe ? 600 : 520, reportLabel: reporting ? 'never mind' : 'report someone'
  });
  return <Wrap node={node}><Act html={html} /></Wrap>;
}
function Stage({ node, phone }) {
  const { view } = useContext(Ctx);
  return <Wrap node={node}><Act html={view.stageHtml(phone)} /></Wrap>;
}
function Right({ node, phone }) {
  const { view } = useContext(Ctx);
  const html = rightHtml(view.right, phone);
  if (!html) return null;
  return <Wrap node={node}><Act html={html} /></Wrap>;
}
function Head() {
  const { view, channel } = useContext(Ctx);
  return <Act html={fill('mHead', { title: roomTitle(channel), theme: roomTheme(channel), n: view.n, right: view.youPhone })} />;
}
function Bar() {
  const { view, reporting, muted } = useContext(Ctx);
  const left = view.onStageMe ? fill('mBarMute', { muteLabel: muted ? 'unmute' : 'mute' }) : fill('mBarText', { text: view.me?.handUp ? 'HAND UP' : 'MIC OFF' });
  return <Act html={fill('mBar', { left, reportLabel: reporting ? 'never mind' : 'report' })} />;
}
function Act({ html }) {
  const { onAct } = useContext(Ctx);
  return <Tpl html={html} onAct={onAct} />;
}

const SLOTS = {
  card: (node) => <Card node={node} />,
  stage: (node) => <Stage node={node} phone={/flex:1 0 auto/.test(node.attribs?.style || '')} />,
  right: (node) => <Right node={node} />,
  head: () => <Head />,
  slip: (node) => <Right node={node} phone />,
  bar: () => <Bar />
};

export default function Room({ channel }) {
  const router = useRouter();
  const back = useCallback(() => router.push('/rooms'), [router]);
  const room = useRoom(channel.id, { onGone: back });
  const [picked, setPicked] = useState(null);
  const [reporting, setReporting] = useState(false);
  const now = useNow(true, 500);
  const [open, setOpen] = useState(true);
  useEffect(() => {
    document.title = `${roomTitle(channel)} · open pod · NoTrace`;
    const t = () => setOpen(podsOpen());
    t();
    const id = setInterval(t, 30_000);
    return () => clearInterval(id);
  }, [channel]);

  // leaving a room you were removed from (or one that filled up) goes back to the list
  useEffect(() => {
    if (room.phase === 'removed' || room.phase === 'full') router.replace('/rooms');
  }, [room.phase, router]);

  const view = useView(room, channel, picked, reporting, now);
  const { modAct, report, raiseHand, lowerHand, answerInvite, stepDown, toggleMute, leave, setNote } = room;

  const onAct = useCallback((act, id) => {
    switch (act) {
      case 'leave': return leave();
      case 'report': // the card's "report someone" toggles report mode; a REPORT by a name reports them
        if (id) {
          setReporting(false);
          return report(id);
        }
        return setReporting((r) => !r);
      case 'cancelreport': return setReporting(false);
      case 'mute': return toggleMute();
      case 'raise': setNote(null); return raiseHand();
      case 'lower': return lowerHand();
      case 'stepdown': setNote(null); return stepDown();
      case 'accept': return answerInvite(true);
      case 'refuse': return answerInvite(false);
      case 'move': return modAct('stage:demote', id);
      case 'pick': return setPicked((p) => (p === id ? null : id));
      case 'unpick': return setPicked(null);
      case 'yes': // the hand note's first chip: let a raised hand up, or invite the picked listener
        setPicked(null);
        return view.right?.yesAct === 'invite' ? modAct('channel:invite', id) : modAct('hand:approve', id);
      case 'no':
        setPicked(null);
        return view.right?.noAct === 'decline' ? modAct('hand:decline', id) : null;
      default: return null;
    }
  }, [leave, report, toggleMute, raiseHand, lowerHand, stepDown, answerInvite, modAct, setNote, view.right]);

  const ctx = useMemo(() => ({ view, channel, reporting, muted: room.muted, onAct }), [view, channel, reporting, room.muted, onAct]);

  if (!open || room.phase === 'closed') return <Asleep />;
  if (room.noVoice) return <MicScreen which="novoice" mic={room.mic} onBack={() => room.setNoVoice(false)} />;
  if (room.mic.modal) return <MicScreen which={room.mic.modal} mic={room.mic} />;
  return (
    <Ctx.Provider value={ctx}>
      <Screen desktop={DRoom} phone={MRoom} vals={NO_VALS} slots={SLOTS} css={ROOM_CSS} />
    </Ctx.Provider>
  );
}
