'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Guard from '@/components/Guard';
import Screen from '@/v5/Screen';
import DW from '@/v5/screens/V5EchoWrite';
import MW from '@/v5/screens/V5MEchoWrite';
import DL from '@/v5/screens/V5EchoTooLong';
import ML from '@/v5/screens/V5MEchoTooLong';
import DP from '@/v5/screens/V5EchoPinned';
import MP from '@/v5/screens/V5MEchoPinned';
import { toast } from '@/lib/wisp';
import { NOTE_MAX, VOICE_MAX_S, postEcho, useRecorder } from '@/lib/echoes';
import { createStore, useStore, NoteText, NoteCount, NoteVoice } from './compose';
import { clock } from '../ui';

const INK = '#221E1A', PENCIL = '#5F584E';
const ERR = {
  cooldown: (r) => `One note every few minutes. Try again in ${Math.max(1, Math.ceil((r.retryInMs || 0) / 60_000))} min.`,
  too_long: () => 'That’s too long for a note.',
  empty: () => 'Write something first, or hold to speak.',
  offline: () => 'You’re offline. Try again in a moment.',
  timeout: () => 'That took too long. Try again.'
};
const errText = (r) => (ERR[r?.error] ?? (() => 'Something went wrong. Try again.'))(r || {});

function Write() {
  const store = useMemo(() => createStore({ text: '', focus: false }), []);
  const over = useStore(store, (s) => s.text.length > NOTE_MAX);
  const [mode, setMode] = useState('write');
  const [busy, setBusy] = useState(false);
  const [pinned, setPinned] = useState(null); // what went up: { text } | { voice }
  const rec = useRecorder(VOICE_MAX_S);
  // the recorder changes every tick; slots must stay put, so the voice slot reads it from a store
  const recStore = useMemo(() => createStore({ rec }), []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => recStore.set({ rec }), [rec, recStore]);

  const pin = useCallback(async () => {
    if (busy) return;
    const text = store.get().text.trim();
    const rec = recStore.get().rec;
    let payload;
    if (mode === 'speak') {
      if (!rec.clip) return toast({ tag: '[ NOTHING YET ]', text: 'HOLD TO SPEAK, THEN PIN IT UP.' });
      payload = { kind: 'echo', clip: rec.clip };
    } else {
      if (!text) return toast({ tag: '[ NOTHING YET ]', text: errText({ error: 'empty' }).toUpperCase() });
      if (text.length > NOTE_MAX) return;
      payload = { kind: 'echo', text };
    }
    setBusy(true);
    const r = await postEcho(payload);
    setBusy(false);
    if (!r?.ok) return toast({ tag: '[ NOT YET ]', text: errText(r).toUpperCase() });
    setPinned(mode === 'speak' ? { voice: rec.clip.duration } : { text });
    store.set({ text: '' });
    rec.reset();
  }, [busy, mode, recStore, store]);

  const vals = useMemo(
    () => ({
      writeMode: mode === 'write', speakMode: mode === 'speak',
      writeColor: mode === 'write' ? INK : PENCIL, speakColor: mode === 'speak' ? INK : PENCIL,
      writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,
      toWrite: () => setMode('write'), toSpeak: () => setMode('speak')
    }),
    [mode]
  );
  const links = useMemo(() => ({ EchoPinned: pin }), [pin]);
  const slots = useMemo(
    () => ({
      noteText: (node) => <NoteText node={node} store={store} placeholder="say it here. no name on it." />,
      noteCount: (node) => <NoteCount node={node} store={store} />,
      noteVoice: (node) => <NoteVoice node={node} recStore={recStore} maxS={VOICE_MAX_S} />
    }),
    [store, recStore]
  );
  const pinnedSlots = useMemo(
    () => ({
      pinnedText: (node) => (
        <div style={attributesToProps({ style: node.attribs?.style || '' }).style}>{pinned?.text ?? `a voice note · ${clock(pinned?.voice)}`}</div>
      )
    }),
    [pinned]
  );

  if (pinned) return <Screen desktop={DP} phone={MP} slots={pinnedSlots} />;
  if (over && mode === 'write') return <Screen desktop={DL} phone={ML} slots={slots} />;
  return <Screen desktop={DW} phone={MW} vals={vals} slots={slots} links={links} css={busy ? '.chip{opacity:.6;pointer-events:none}' : ''} />;
}

export default function Page() {
  return (
    <Guard>
      <Write />
    </Guard>
  );
}
