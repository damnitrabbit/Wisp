'use client';
// The live parts of the write boards (echo + unsent letter share them): what you type, the counter, the voice note.
// They read a small store, so typing doesn't re-render the whole designed screen.
import { useEffect, useRef, useSyncExternalStore } from 'react';
import { attributesToProps, domToReact } from 'html-react-parser';
import { NOTE_MAX } from '@/lib/echoes';
import { clock } from '../ui';

export function createStore(init) {
  let s = init;
  const subs = new Set();
  return {
    get: () => s,
    set(patch) {
      s = { ...s, ...(typeof patch === 'function' ? patch(s) : patch) };
      subs.forEach((f) => f());
    },
    sub(f) {
      subs.add(f);
      return () => subs.delete(f);
    }
  };
}
export function useStore(store, pick) {
  return useSyncExternalStore(store.sub, () => pick(store.get()), () => pick(store.get()));
}

const styleOf = (node) => attributesToProps({ style: node.attribs?.style || '' }).style || {};
const BARE = { background: 'transparent', border: 0, outline: 'none', resize: 'none', padding: 0, margin: 0, width: '100%', font: 'inherit', color: 'inherit', lineHeight: 'inherit', letterSpacing: 'inherit' };

// The words. Over the limit, the part that won't fit is underlined in red ink under the text (a mirror behind
// a see-through textarea), like the design's "too long" note.
export function NoteText({ node, store, placeholder, minLines = 3, grow = false }) {
  const text = useStore(store, (s) => s.text);
  const ref = useRef(null);
  const mirror = useRef(null);
  const st = styleOf(node);
  const over = text.length > NOTE_MAX;
  useEffect(() => {
    const t = ref.current;
    if (!t) return;
    if (document.activeElement !== t && store.get().focus) {
      t.focus();
      t.setSelectionRange(t.value.length, t.value.length);
    }
  }, [store]);
  const lh = st.lineHeight && String(st.lineHeight).endsWith('px') ? parseFloat(st.lineHeight) : parseFloat(st.fontSize || 20) * (parseFloat(st.lineHeight) || 1.6);
  const box = { ...st, position: 'relative', display: 'flex', flexDirection: 'column', minHeight: Math.round(lh * minLines) };
  if (!grow) box.flex = '1 1 auto';
  const area = { ...BARE, flex: '1 1 auto', minHeight: Math.round(lh * minLines), overflowY: 'auto', scrollbarWidth: 'none', position: 'relative', zIndex: 1 };
  return (
    <div style={box}>
      {over && (
        <div ref={mirror} aria-hidden="true" style={{ position: 'absolute', inset: 0, whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', color: 'transparent', pointerEvents: 'none' }}>
          {text.slice(0, NOTE_MAX)}
          <span style={{ textDecoration: 'underline wavy #B8352A', textDecorationThickness: '1.5px', textUnderlineOffset: 4 }}>{text.slice(NOTE_MAX)}</span>
        </div>
      )}
      <textarea
        ref={ref}
        value={text}
        maxLength={NOTE_MAX + 200}
        placeholder={placeholder}
        aria-label={placeholder}
        className="nt-area"
        onChange={(e) => store.set({ text: e.target.value, focus: true })}
        onScroll={(e) => mirror.current && (mirror.current.scrollTop = e.target.scrollTop)}
        style={{ ...area, caretColor: '#B8352A' }}
      />
    </div>
  );
}

export function NoteCount({ node, store }) {
  const n = useStore(store, (s) => s.text.length);
  const st = styleOf(node);
  const over = n > NOTE_MAX;
  return <span style={{ ...st, ...(over ? { color: '#B8352A', fontWeight: 700 } : null) }} aria-live="polite">{n} / {NOTE_MAX}</span>;
}

// Hold to speak; let go to stop. Shows the designed recording row, with live time.
export function NoteVoice({ node, recStore, maxS = 30 }) {
  const rec = useStore(recStore, (s) => s.rec);
  const st = styleOf(node);
  const { state, elapsed, clip } = rec;
  const label =
    state === 'recording' ? `recording · ${clock(elapsed)}`
      : state === 'done' && clip ? `your voice · ${clock(clip.duration)}`
        : state === 'asking' ? 'asking for your mic…'
          : state === 'denied' ? 'your mic is blocked'
            : state === 'unsupported' ? 'this browser can’t record'
              : `hold to speak · up to ${maxS}s`;
  const hint = state === 'recording' ? 'LET GO TO STOP' : state === 'done' ? 'HOLD TO RECORD AGAIN' : 'PRESS AND HOLD';
  const replace = (n) => {
    if (n.type === 'text' && n.data.startsWith('recording')) return <>{label}</>;
    if (n.type === 'text' && n.data.includes('LET GO TO STOP')) return <>{hint}</>;
    if (n.type === 'tag' && n.name === 'span' && /border-radius:50%;background:#B8352A/.test(n.attribs?.style || '') && state !== 'recording') {
      return <span style={{ width: 12, height: 12, borderRadius: '50%', background: state === 'done' ? '#221E1A' : 'transparent', border: '2px solid #B8352A', flexShrink: 0 }} />;
    }
    if (n.type === 'tag' && n.attribs?.class?.includes('played')) {
      const frac = state === 'recording' ? Math.min(1, elapsed / maxS) : state === 'done' ? 1 : 0;
      return <div className={n.attribs.class} style={{ ...styleOf(n), width: `${frac * 100}%` }}>{domToReact(n.children, { replace })}</div>;
    }
    return undefined;
  };
  const down = (e) => {
    e.preventDefault();
    if (state === 'recording' || state === 'asking') return;
    if (state === 'done') rec.reset();
    rec.start();
  };
  const up = () => state === 'recording' && rec.stop();
  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={state === 'recording' ? 'Recording. Let go to stop.' : 'Press and hold to record a voice note'}
      onPointerDown={down}
      onPointerUp={up}
      onPointerLeave={up}
      onPointerCancel={up}
      onKeyDown={(e) => (e.key === ' ' || e.key === 'Enter') && !e.repeat && down(e)}
      onKeyUp={(e) => (e.key === ' ' || e.key === 'Enter') && up()}
      onContextMenu={(e) => e.preventDefault()}
      style={{ ...st, cursor: 'pointer', touchAction: 'none', userSelect: 'none', WebkitUserSelect: 'none' }}
    >
      {domToReact(node.children || [], { replace })}
    </div>
  );
}
