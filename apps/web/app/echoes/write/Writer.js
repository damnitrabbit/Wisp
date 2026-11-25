'use client';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Screen from '@/v5/Screen';
import DW from '@/v5/screens/V5EchoWrite';
import MW from '@/v5/screens/V5MEchoWrite';
import DL from '@/v5/screens/V5EchoTooLong';
import ML from '@/v5/screens/V5MEchoTooLong';
import DP from '@/v5/screens/V5EchoPinned';
import MP from '@/v5/screens/V5MEchoPinned';
import DUW from '@/v5/screens/V5UnsentWrite';
import MUW from '@/v5/screens/V5MUnsentWrite';
import DUP from '@/v5/screens/V5UnsentPinned';
import MUP from '@/v5/screens/V5MUnsentPinned';
import { toast } from '@/lib/wisp';
import { NOTE_MAX, VOICE_MAX_S, postEcho, useRecorder } from '@/lib/echoes';
import { createStore, useStore, NoteText, NoteCount, NoteVoice, NoteTo, TO_MAX } from './compose';
import { clock } from '../ui';

const INK = '#221E1A', PENCIL = '#5F584E';
const ERR = {
  cooldown: (r) => `One note every few minutes. Try again in ${Math.max(1, Math.ceil((r.retryInMs || 0) / 60_000))} min.`,
  too_long: () => 'That’s too long for a note.',
  empty: () => 'Write something first, or hold to speak.',
  offline: () => 'You’re offline. Try again in a moment.',
  timeout: () => 'That took too long. Try again.'
};
// the textarea writes straight on the paper: no focus box, a pencil placeholder.
// Coming back from "too long" (or flipping modes) the board is already up: don't replay its entrance.
const CSS = `.nt-area::placeholder{color:${PENCIL};font-style:italic;opacity:1}.nt-area:focus-visible,.nt-area:focus{outline:none;box-shadow:none}`;
const STILL = `.nt-still .rise,.nt-still .write,.nt-still .draw,.nt-still .drop,.nt-still .slap,.nt-still .thud{animation-duration:0s !important;animation-delay:0s !important}`;
const BUSY = '.chip{opacity:.6;pointer-events:none}';
const errText = (r) => (ERR[r?.error] ?? (() => 'Something went wrong. Try again.'))(r || {});

// kind 'echo' (/echoes/write) or 'unsent' (/echoes/unsent): same desk, different paper
export default function Writer({ kind = 'echo' }) {
  const letter = kind === 'unsent';
  const store = useMemo(() => createStore({ text: '', to: '', focus: false }), []);
  const over = useStore(store, (s) => s.text.length > NOTE_MAX);
  const [mode, setMode] = useState('write');
  const [busy, setBusy] = useState(false);
  const [settled, setSettled] = useState(false); // the entrance has played once
  useEffect(() => { const t = setTimeout(() => setSettled(true), 3500); return () => clearTimeout(t); }, []);
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
    const to = store.get().to.trim().replace(/,+$/, '').slice(0, TO_MAX) || 'you';
    if (mode === 'speak') {
      if (!rec.clip) return toast({ tag: '[ NOTHING YET ]', text: `HOLD TO SPEAK, THEN ${letter ? 'PUT' : 'PIN'} IT UP.` });
      payload = { kind, clip: rec.clip };
    } else {
      if (!text) return toast({ tag: '[ NOTHING YET ]', text: errText({ error: 'empty' }).toUpperCase() });
      if (text.length > NOTE_MAX) return toast({ tag: '[ TOO LONG ]', text: `KEEP IT UNDER ${NOTE_MAX} CHARACTERS. CUT THE PART UNDERLINED IN RED.` });
      payload = { kind, text };
    }
    if (letter) payload.to = to;
    setBusy(true);
    const r = await postEcho(payload);
    setBusy(false);
    if (!r?.ok) return toast({ tag: '[ NOT YET ]', text: errText(r).toUpperCase() });
    setPinned(mode === 'speak' ? { voice: rec.clip.duration, to } : { text, to });
    store.set({ text: '', to: '' });
    rec.reset();
  }, [busy, mode, recStore, store, kind, letter]);

  const vals = useMemo(
    () => ({
      writeMode: mode === 'write', speakMode: mode === 'speak',
      writeColor: mode === 'write' ? INK : PENCIL, speakColor: mode === 'speak' ? INK : PENCIL,
      writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,
      toWrite: () => setMode('write'), toSpeak: () => setMode('speak')
    }),
    [mode]
  );
  const links = useMemo(() => ({ EchoPinned: pin, UnsentPinned: pin }), [pin]);
  const slots = useMemo(
    () => ({
      noteText: (node) => <NoteText node={node} store={store} placeholder={letter ? 'say what you never got to say.' : 'say it here. no name on it.'} />,
      noteTo: (node) => <NoteTo node={node} store={store} />,
      noteCount: (node) => <NoteCount node={node} store={store} />,
      noteVoice: (node) => <NoteVoice node={node} recStore={recStore} maxS={VOICE_MAX_S} />
    }),
    [store, recStore, letter]
  );
  // too long: the sheet shows more of the words, so the part to cut is in view
  const longSlots = useMemo(
    () => ({ ...slots, noteText: (node) => <NoteText node={node} store={store} minLines={7} placeholder="say it here. no name on it." /> }),
    [slots, store]
  );
  const pinnedSlots = useMemo(
    () => ({
      pinnedText: (node) => (
        <div style={attributesToProps({ style: node.attribs?.style || '' }).style}>{pinned?.text ?? `a voice note · ${clock(pinned?.voice)}`}</div>
      ),
      pinTo: (node) => <div style={attributesToProps({ style: node.attribs?.style || '' }).style}>{`to ${pinned?.to || 'you'},`}</div>,
      // the letter on the wall is a fixed sheet: a long one shows its first lines
      pinText: (node) => (
        <div style={{ ...attributesToProps({ style: node.attribs?.style || '' }).style, display: '-webkit-box', WebkitBoxOrient: 'vertical', WebkitLineClamp: 4, overflow: 'hidden', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
          {pinned?.text ?? `a voice note · ${clock(pinned?.voice)}`}
        </div>
      )
    }),
    [pinned]
  );

  if (pinned) return letter ? <Screen key="up" desktop={DUP} phone={MUP} slots={pinnedSlots} /> : <Screen key="ep" desktop={DP} phone={MP} slots={pinnedSlots} />;
  const css = CSS + STILL + (busy ? BUSY : '');
  const cls = settled ? 'nt-still' : '';
  if (over && mode === 'write' && !letter) return <Screen desktop={DL} phone={ML} slots={longSlots} css={css} className={cls} />;
  return letter
    ? <Screen key="uw" desktop={DUW} phone={MUW} vals={vals} slots={slots} links={links} css={css} className={cls} />
    : <Screen key="ew" desktop={DW} phone={MW} vals={vals} slots={slots} links={links} css={css} className={cls} />;
}
