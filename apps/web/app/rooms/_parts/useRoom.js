'use client';
// Being in a voice room (an open pod room or tonight's question): join, follow the room's state, the mic, the audio mesh.
// Same server events and WebRTC as before V5; the screens decide how it looks.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { emit, on, bus, syncClock, useWisp } from '@/lib/wisp';
import { useMicFlow, micTrack, closeMic } from '@/lib/mic';
import { useMesh } from '@/lib/mesh';

export const onStage = (m) => Boolean(m) && m.role !== 'listener';
export const voiceSupported = () =>
  typeof window !== 'undefined' && Boolean(navigator.mediaDevices?.getUserMedia && window.RTCPeerConnection);

const NOTE_MS = 7000;

export function useRoom(roomId, { onGone } = {}) {
  const session = useWisp((s) => s.session);
  const meId = session?.id;
  const [snap, setSnap] = useState(null);
  const [phase, setPhase] = useState('joining'); // joining | in | full | removed | closed
  const [invite, setInvite] = useState(null); // { from, expiresAt }
  const [note, setNoteState] = useState(null); // a passing event worth a note: { kind, name, at }
  const [reported, setReported] = useState(() => new Set());
  const [muted, setMuted] = useState(false);
  const [track, setTrack] = useState(null);
  const [noVoice, setNoVoice] = useState(false);
  const mic = useMicFlow();
  const left = useRef(false);
  const asking = useRef(false);
  const noteTimer = useRef(null);
  const goneRef = useRef(onGone);
  goneRef.current = onGone;

  const setNote = useCallback((n, ms = NOTE_MS) => {
    clearTimeout(noteTimer.current);
    setNoteState(n ? { ...n, at: Date.now() } : null);
    if (n && ms) noteTimer.current = setTimeout(() => setNoteState(null), ms);
  }, []);

  const members = useMemo(() => snap?.members ?? [], [snap]);
  const me = members.find((m) => m.id === meId);

  // ---------- join / leave ----------
  const join = useCallback(async () => {
    const r = await emit('channel:join', { id: roomId });
    if (r.error === 'full') return setPhase('full');
    if (r.error === 'removed') return setPhase('removed');
    if (r.error === 'closed') return setPhase('closed');
    if (r.error) return; // offline: the session handler rejoins
    syncClock(r.snapshot.serverNow);
    setSnap(r.snapshot);
    setReported(new Set(r.reported ?? []));
    setPhase('in');
  }, [roomId]);

  useEffect(() => {
    if (meId && (phase === 'joining' || phase === 'full')) join();
  }, [meId, join, phase]);

  useEffect(() => {
    const offs = [
      on('channel:update', (s) => {
        if (s.id !== roomId) return;
        syncClock(s.serverNow);
        setSnap(s);
      }),
      on('channel:speakInviteReceived', (p) => {
        syncClock(p.serverNow);
        setInvite(p);
      }),
      on('channel:inviteExpired', (p) => {
        if (p.id) setNote({ kind: 'inviteExpired', name: p.name });
        else setInvite(null);
      }),
      on('channel:inviteDeclined', (p) => setNote({ kind: 'inviteDeclined', name: p.name })),
      on('hand:approved', (p) => setNote({ kind: 'approved', name: p.by })),
      on('hand:declined', () => setNote({ kind: 'declined' })),
      on('hand:expired', () => setNote({ kind: 'expired' })),
      on('stage:demoted', () => setNote({ kind: 'demoted' }, 0)),
      on('channel:modPromoted', (p) => {
        if (p.id === meId) setNote({ kind: 'promoted' });
        else if (p.why === 'succession') setNote({ kind: 'succession', name: p.name });
      }),
      on('channel:youWereKicked', () => {
        left.current = true;
        setPhase('removed');
      }),
      on('pods:closed', () => {
        left.current = true;
        setPhase('closed');
      }),
      bus.on('session', ({ fresh }) => {
        if (fresh) {
          setSnap(null);
          setPhase('joining');
        }
      })
    ];
    return () => offs.forEach((f) => f());
  }, [roomId, meId, setNote]);

  useEffect(
    () => () => {
      clearTimeout(noteTimer.current);
      if (!left.current) emit('channel:leave');
      closeMic();
    },
    []
  );

  // ---------- the mic follows the stage ----------
  useEffect(() => {
    if (!me) return;
    if (onStage(me) && !track && !asking.current) {
      asking.current = true;
      (voiceSupported() ? mic.ask() : Promise.resolve(false)).then((ok) => {
        asking.current = false;
        if (ok) {
          setTrack(micTrack());
          setMuted(false);
        } else emit(roomId === 'question' ? 'question:voice' : 'stage:stepDown', { on: false });
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
  const needMic = useCallback(async () => {
    if (!voiceSupported()) {
      setNoVoice(true);
      return false;
    }
    const ok = await mic.ask();
    if (ok) setTrack(micTrack());
    return ok;
  }, [mic]);

  const toggleMute = useCallback(() => {
    setMuted((m) => {
      emit('stage:mute', { muted: !m });
      return !m;
    });
  }, []);

  const raiseHand = useCallback(async () => {
    const r = await emit('hand:raise');
    if (r.error === 'cooldown') setNote({ kind: 'cooldown' });
  }, [setNote]);
  const lowerHand = useCallback(() => emit('hand:lower'), []);

  const answerInvite = useCallback(async (yes) => {
    setInvite(null);
    if (!yes) return emit('channel:declineInvite');
    const ok = await needMic();
    if (!ok) return emit('channel:declineInvite');
    const r = await emit('channel:acceptInvite');
    if (r.error === 'stage_full') setNote({ kind: 'stageFull' });
  }, [needMic, setNote]);

  const modAct = useCallback(async (event, id) => {
    const r = await emit(event, { to: id });
    if (r.error === 'stage_full') setNote({ kind: 'stageFull' });
    return r;
  }, [setNote]);

  const report = useCallback(async (id) => {
    const m = members.find((x) => x.id === id);
    if (!m || reported.has(id)) return;
    setReported((s) => new Set(s).add(id));
    await emit('channel:report', { to: id });
    setNote({ kind: 'reported', name: m.name });
  }, [members, reported, setNote]);

  const stepDown = useCallback(() => emit('stage:stepDown'), []);

  // tonight's question: switch your own voice on and off
  const questionVoice = useCallback(async (onv) => {
    if (onv) {
      const ok = await needMic();
      if (!ok) return;
    }
    await emit('question:voice', { on: onv });
  }, [needMic]);

  const leave = useCallback(() => {
    left.current = true;
    emit('channel:leave');
    closeMic();
    goneRef.current?.();
  }, []);

  return {
    meId, me, snap, members, phase, setPhase, invite, note, setNote, reported, muted, track, speaking, mic, noVoice, setNoVoice,
    toggleMute, raiseHand, lowerHand, answerInvite, modAct, report, stepDown, questionVoice, leave, rejoin: join
  };
}
