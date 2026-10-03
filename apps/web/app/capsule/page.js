'use client';
// TIME CAPSULE: write to later-you, pick when it opens, seal it in this browser. Optional email reminder.
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Capsule';
import M from '@/v5/screens/V5MCapsule';
import DErr from '@/v5/screens/V5CapsuleEmailError';
import MErr from '@/v5/screens/V5MCapsuleEmailError';
import DSealed from '@/v5/screens/V5CapsuleSealed';
import MSealed from '@/v5/screens/V5MCapsuleSealed';
import { storageOk, sealCapsule, openTime, dateBounds, longDate, shortDate, lowerDate, isEmail, remindByEmail, remindable } from '@/lib/v5/capsule';

const INK = '#221E1A';
const PENCIL = '#5F584E';
const RED = '#B8352A';
const CSS = `.captext textarea,.capmail input{scrollbar-width:none}.captext textarea:focus-visible,.capmail input:focus-visible{outline:none;box-shadow:none}
.captext textarea::placeholder{color:transparent}.capmail input::placeholder{color:${PENCIL};font-style:italic;opacity:1}
.cap-picked .capopt .draw{animation-delay:0s !important;animation-duration:.55s !important}
.capopt{cursor:pointer;background:none;border:0}.capopt:focus-visible{outline:2px dashed ${INK};outline-offset:2px}`;

function strip(node) {
  const p = attributesToProps(node.attribs || {});
  delete p['data-slot'];
  return p;
}

// The letter, written in the letter's own type.
function CapText({ node, store, lines = 4 }) {
  const [value, setValue] = useState(store.current);
  const [focus, setFocus] = useState(false);
  const p = strip(node);
  return (
    <div {...p} className="captext" style={{ ...p.style, position: 'relative' }}>
      <textarea
        aria-label="Your letter to later you"
        value={value}
        maxLength={4000}
        placeholder="write it here"
        onFocus={() => setFocus(true)}
        onBlur={() => setFocus(false)}
        onChange={(e) => {
          setValue(e.target.value);
          store.current = e.target.value;
        }}
        style={{ display: 'block', width: '100%', height: `${lines * 1.6}em`, margin: 0, padding: 0, border: 0, outline: 'none', resize: 'none', background: 'transparent', font: 'inherit', lineHeight: 'inherit', color: 'inherit', caretColor: RED, overflowY: 'auto' }}
      />
      {!value && !focus && (
        <span className="blink" aria-hidden="true" style={{ position: 'absolute', left: 0, top: 0, color: RED, pointerEvents: 'none' }}>|</span>
      )}
    </div>
  );
}

// "remind me by email · optional": the field's ruled line, as a real input.
function CapEmail({ node, store }) {
  const [value, setValue] = useState(store.current);
  const p = strip(node);
  return (
    <div {...p} className="capmail">
      <input
        type="email"
        inputMode="email"
        autoComplete="email"
        aria-label="Remind me by email (optional)"
        placeholder="you@somewhere.com"
        value={value}
        maxLength={254}
        onChange={(e) => {
          setValue(e.target.value);
          store.current = e.target.value;
        }}
        style={{ display: 'block', width: '100%', margin: 0, padding: 0, border: 0, outline: 'none', background: 'transparent', font: 'inherit', color: INK }}
      />
    </div>
  );
}

export default function CapsulePage() {
  const [stage, setStage] = useState('write'); // write | error | sealed
  const [pick, setPickRaw] = useState('Week');
  const [picked, setPicked] = useState(false); // once they choose, the circle draws at once (no entrance delay)
  const setPick = useCallback((k) => { setPicked(true); setPickRaw(k); }, []);
  const [date, setDate] = useState('');
  const [canStore, setCanStore] = useState(true);
  const [remind, setRemind] = useState(null); // null | 'ok' | 'unavailable' | 'far' | 'fail'
  const [sealed, setSealed] = useState(null); // { openAt, preview }
  const text = useRef('');
  const email = useRef('');
  const dateInput = useRef(null);
  const [bounds, setBounds] = useState({ min: '', max: '' });

  useEffect(() => {
    setCanStore(storageOk());
    setBounds(dateBounds(new Date(), false));
  }, []);

  const openPicker = useCallback(() => {
    const el = dateInput.current;
    if (!el) return;
    // with an email, the date can only be as far as the reminder can reach (30 days)
    const b = dateBounds(new Date(), Boolean(email.current.trim()));
    setBounds(b);
    el.min = b.min;
    el.max = b.max;
    try {
      if (el.showPicker) return el.showPicker();
    } catch {}
    el.focus();
    el.click();
  }, []);

  const seal = useCallback(() => {
    const words = text.current.trim();
    if (!words) {
      document.querySelector('.captext textarea')?.focus();
      return;
    }
    const mail = email.current.trim();
    if (mail && !isEmail(mail)) return setStage('error');
    const at = openTime(pick, date);
    if (!at) return openPicker();
    sealCapsule(words, at); // false in a private window: the inline note already said so
    setSealed({ openAt: at.toISOString(), preview: words });
    setRemind(null);
    setStage('sealed');
    text.current = '';
    if (mail) {
      email.current = '';
      if (!remindable(at)) setRemind('far');
      else remindByEmail(mail, at).then((r) => setRemind(r?.ok ? 'ok' : r?.error === 'unavailable' ? 'unavailable' : r?.error === 'too_long' ? 'far' : 'fail'));
    }
  }, [pick, date, openPicker]);

  const vals = useMemo(() => {
    const opt = (k) => pick === k;
    const at = sealed ? new Date(sealed.openAt) : null;
    return {
      onWeek: opt('Week'),
      onMonth: opt('Month'),
      onDate: opt('Date'),
      colWeek: opt('Week') ? INK : PENCIL,
      colMonth: opt('Month') ? INK : PENCIL,
      colDate: opt('Date') ? INK : PENCIL,
      pickWeek: () => setPick('Week'),
      pickMonth: () => setPick('Month'),
      pickDate: () => {
        setPick('Date');
        openPicker();
      },
      dateLabel: date ? lowerDate(openTime('Date', date)) : 'a date',
      storageNote: !canStore,
      openLong: at ? longDate(at) : '',
      openShort: at ? shortDate(at) : '',
      preview: sealed?.preview || '',
      remindOk: remind === 'ok',
      remindOkText: at ? `we'll email you on ${lowerDate(at)}. then we forget the address.` : '',
      remindFail: remind === 'fail' || remind === 'unavailable' || remind === 'far',
      remindFailA: remind === 'unavailable' ? "email reminders aren't switched on yet." : remind === 'far' ? 'reminders only reach 30 days out.' : "couldn't set the reminder.",
      remindFailB: 'the letter is still sealed here.'
    };
  }, [pick, date, canStore, sealed, remind, openPicker, setPick]);

  const slots = useMemo(
    () => ({
      capText: (node) => <CapText node={node} store={text} />,
      capEmail: (node) => <CapEmail node={node} store={email} />
    }),
    []
  );
  const links = useMemo(
    () => ({
      CapsuleSealed: seal,
      Capsule: () => {
        setSealed(null);
        setRemind(null);
        setStage('write');
      }
    }),
    [seal]
  );

  const [d, m] = stage === 'sealed' ? [DSealed, MSealed] : stage === 'error' ? [DErr, MErr] : [D, M];
  return (
    <>
      <Screen key={stage} desktop={d} phone={m} vals={vals} slots={slots} links={links} css={CSS} className={picked ? 'cap-picked' : ''} />
      <input
        ref={dateInput}
        type="date"
        aria-label="When it opens"
        min={bounds.min}
        max={bounds.max}
        value={date}
        onChange={(e) => {
          const v = e.target.value;
          if (!v || (e.target.min && v < e.target.min) || (e.target.max && v > e.target.max)) return;
          setDate(v);
          setPick('Date');
        }}
        tabIndex={-1}
        style={{ position: 'fixed', left: '50%', top: '50%', width: 1, height: 1, opacity: 0, pointerEvents: 'none', border: 0, padding: 0 }}
      />
    </>
  );
}
