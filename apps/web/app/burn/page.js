'use client';
// BURN: write it (or say it), hold the match, watch it go. Nothing is sent or stored anywhere.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Screen, { pickPhone } from '@/v5/Screen';
import D from '@/v5/screens/V5Burn';
import M from '@/v5/screens/V5MBurn';
import DRec from '@/v5/screens/V5BurnRecording';
import MRec from '@/v5/screens/V5MBurnRecording';
import { useHold, useVoiceNote, clock, HOLD_MS, VOICE_MAX_S } from '@/lib/v5/burn';

const RED = '#B8352A';
const BURN_MS = { desk: 4700, phone: 4300 }; // the design's burn animation (T + .3s)

// the ring fills over the whole hold
const CSS = `.holding .match .ring circle.p{transition-duration:${HOLD_MS / 1000}s}
.burntext textarea::placeholder{color:transparent}
.burntext textarea:focus-visible{outline:none;box-shadow:none}
.burntext textarea{scrollbar-width:none}.burntext textarea::-webkit-scrollbar{display:none}
.recbtn:focus-visible,.match:focus-visible{outline:2px dashed #E9E9E7;outline-offset:6px}`;

// The words, written straight onto the ruled sheet: same font, size and line height as the design text.
function BurnText({ node, store, onEmpty, phone }) {
  const [value, setValue] = useState(store.current);
  const [focus, setFocus] = useState(false);
  const props = attributesToProps(node.attribs || {});
  delete props['data-slot'];
  const lh = phone ? 30 : 38;
  const lines = phone ? 7 : 5;
  return (
    <div {...props} className="words burntext">
      <textarea
        aria-label="Say the thing you can't say out loud"
        value={value}
        maxLength={1200}
        autoFocus={!phone}
        spellCheck={false}
        onFocus={() => setFocus(true)}
        onBlur={() => setFocus(false)}
        onChange={(e) => {
          const v = e.target.value;
          setValue(v);
          store.current = v;
          onEmpty(!v.trim());
        }}
        placeholder="write it here"
        style={{ display: 'block', width: '100%', height: lh * lines, margin: 0, padding: 0, border: 0, outline: 'none', resize: 'none', background: 'transparent', font: 'inherit', fontSize: 'inherit', lineHeight: 'inherit', color: 'inherit', caretColor: RED, overflowY: 'auto' }}
      />
      {!value && !focus && (
        <span className="blink" aria-hidden="true" style={{ position: 'absolute', left: 0, top: props.style?.paddingTop ?? 16, color: RED, pointerEvents: 'none' }}>|</span>
      )}
    </div>
  );
}

export default function BurnPage() {
  const [stage, setStage] = useState('writing'); // writing | burning | gone
  const [mode, setMode] = useState('write');
  const [empty, setEmpty] = useState(true);
  const store = useRef('');
  const timer = useRef(null);
  const voice = useVoiceNote(VOICE_MAX_S);
  const voiceRef = useRef(voice);
  voiceRef.current = voice;

  const hasClip = Boolean(voice.clip);
  const isEmpty = mode === 'write' ? empty : !hasClip;

  const burn = useCallback(() => {
    setStage('burning');
    voiceRef.current.togglePlay && voiceRef.current.playing && voiceRef.current.togglePlay();
    clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      // let it go: the words and the recording are dropped from memory here
      store.current = '';
      setEmpty(true);
      voiceRef.current.clear();
      setStage('gone');
    }, pickPhone() ? BURN_MS.phone : BURN_MS.desk);
  }, []);
  const hold = useHold(burn);
  useEffect(() => () => clearTimeout(timer.current), []);
  // arriving from a capsule's "let it go": straight to the ending
  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('gone') === '1') {
      setStage('gone');
      window.history.replaceState(null, '', '/burn');
    }
  }, []);

  const canBurn = stage === 'writing' && !isEmpty;
  const startHold = useCallback((e) => hold.start(e, canBurn), [hold, canBurn]);
  const onEmpty = useCallback((v) => setEmpty(v), []);

  // speak: hold the red button to record
  const recKey = useRef(false);
  const vals = useMemo(() => {
    const w = mode === 'write';
    return {
      rootClass: [stage === 'burning' ? 'burning' : '', hold.holding ? 'holding' : '', isEmpty && stage === 'writing' ? 'isempty' : ''].join(' '),
      rootStyle: '--freeze: 0s',
      notGone: stage !== 'gone',
      gone: stage === 'gone',
      writeMode: w,
      speakMode: !w,
      writeColor: w ? '#E9E9E7' : '#A39A8C',
      speakColor: !w ? '#E9E9E7' : '#A39A8C',
      writeLine: w ? 1 : 0,
      speakLine: w ? 0 : 1,
      hasWords: !isEmpty,
      isEmpty: isEmpty && stage === 'writing',
      holdLabel: stage === 'burning' ? 'letting it go…' : hold.holding ? 'keep holding…' : 'hold to burn it',
      startHold,
      cancelHold: hold.end,
      keyDown: (e) => {
        if ((e.key === ' ' || e.key === 'Enter') && !e.repeat) {
          e.preventDefault();
          startHold(e);
        } else if (e.key === ' ' || e.key === 'Enter') e.preventDefault();
      },
      toWrite: () => stage === 'writing' && setMode('write'),
      toSpeak: () => stage === 'writing' && setMode('speak'),
      again: () => {
        hold.cancel();
        setStage('writing');
      },
      voiceLen: clock(voice.clip?.duration),
      playLabel: voice.playing ? '❚❚ PAUSE' : '▶ PLAY',
      togglePlay: () => voiceRef.current.togglePlay(),
      reRecord: () => voiceRef.current.clear(),
      // the recording screen
      recording: voice.state === 'recording',
      notRecording: voice.state !== 'recording',
      recIdle: voice.state !== 'recording' && voice.state !== 'denied' && voice.state !== 'unsupported',
      micBlocked: voice.state === 'denied' || voice.state === 'unsupported',
      notBlocked: voice.state !== 'denied' && voice.state !== 'unsupported',
      recLabel: voice.state === 'recording' ? 'recording' : voice.state === 'asking' ? 'asking for the mic…' : 'hold to record',
      recTime: clock(voice.elapsed),
      recHint: voice.state === 'recording' ? 'let go to stop' : 'hold, and say it',
      recAria: voice.state === 'recording' ? 'Recording. Let go to stop' : 'Hold to record a voice note',
      recStart: (e) => {
        if (e.button != null && e.button !== 0) return;
        e.currentTarget.setPointerCapture?.(e.pointerId);
        voiceRef.current.start();
      },
      recStop: () => voiceRef.current.stop(),
      recKeyDown: (e) => {
        if (e.key !== ' ' && e.key !== 'Enter') return;
        e.preventDefault();
        if (e.repeat || recKey.current) return;
        recKey.current = true;
        voiceRef.current.start();
      },
      recKeyUp: (e) => {
        if (e.key !== ' ' && e.key !== 'Enter') return;
        recKey.current = false;
        voiceRef.current.stop();
      },
      noMenu: (e) => e.preventDefault()
    };
  }, [mode, stage, hold, isEmpty, startHold, voice.clip, voice.playing, voice.state, voice.elapsed]);

  const slots = useMemo(
    () => ({
      burnText: (node) => <BurnText node={node} store={store} onEmpty={onEmpty} phone={pickPhone()} />
    }),
    [onEmpty]
  );
  const links = useMemo(() => ({}), []);

  // speak mode with nothing recorded yet: the recording sheet (L12)
  const recordingScreen = mode === 'speak' && !hasClip && stage === 'writing';
  return recordingScreen ? (
    <Screen key="rec" desktop={DRec} phone={MRec} vals={vals} links={links} css={CSS} />
  ) : (
    <Screen key="burn" desktop={D} phone={M} vals={vals} slots={slots} links={links} css={CSS} />
  );
}
