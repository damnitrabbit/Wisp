'use client';
// TIME CAPSULE, opening day: the letter (if it's due), "not yet" (if it isn't), or "this browser forgot".
import { useEffect, useMemo, useState } from 'react';
import { attributesToProps } from 'html-react-parser';
import Screen from '@/v5/Screen';
import DOpen from '@/v5/screens/V5CapsuleOpen';
import MOpen from '@/v5/screens/V5MCapsuleOpen';
import DNot from '@/v5/screens/V5CapsuleNotYet';
import MNot from '@/v5/screens/V5MCapsuleNotYet';
import DLost from '@/v5/screens/V5CapsuleLost';
import DArr from '@/v5/screens/V5CapsuleArrived';
import MArr from '@/v5/screens/V5MCapsuleArrived';
import DLetGo from '@/v5/screens/V5CapsuleLetGo';
import MLetGo from '@/v5/screens/V5MCapsuleLetGo';
import MLost from '@/v5/screens/V5MCapsuleLost';
import { readCapsule, clearCapsule, longDate, shortDate, upperDate, upperDay, agoText, leftText } from '@/lib/v5/capsule';

const CSS = `.capopen{scrollbar-width:none}.capopen::-webkit-scrollbar{display:none}`;

function OpenText({ node, text }) {
  const p = attributesToProps(node.attribs || {});
  delete p['data-slot'];
  const paras = text.split(/\n{2,}/);
  return (
    <div {...p} className="capopen" style={{ ...p.style, maxHeight: 'min(258px, 46vh)', overflowY: 'auto', whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
      {paras.map((t, i) => (
        <div key={i} style={i ? { marginTop: '0.6em' } : undefined}>{t}</div>
      ))}
    </div>
  );
}

export default function CapsuleOpenPage() {
  const [cap, setCap] = useState(undefined); // undefined while reading, null when there's none
  // arrived (still sealed: they open it themselves) → open (the letter) → gone (let it go: the capsule's own ending)
  const [stage, setStage] = useState('arrived');

  useEffect(() => {
    setCap(readCapsule());
  }, []);

  const due = cap && Date.parse(cap.openAt) <= Date.now();
  const vals = useMemo(() => {
    if (!cap) return {};
    return {
      sealedOn: longDate(cap.sealedAt),
      agoText: agoText(cap.sealedAt),
      daysLeft: leftText(cap.openAt),
      sealedUp: upperDate(cap.sealedAt),
      opensUp: upperDay(cap.openAt),
      openShort: shortDate(cap.openAt)
    };
  }, [cap]);
  const slots = useMemo(() => (cap ? { openText: (node) => <OpenText node={node} text={cap.text} /> } : {}), [cap]);
  const links = useMemo(
    () => ({
      CapsuleOpen: () => { setStage('open'); window.scrollTo(0, 0); },
      CapsuleLetGo: () => {
        clearCapsule(); // the letter leaves this browser for good
        setStage('gone');
        window.scrollTo(0, 0);
      }
    }),
    []
  );

  if (cap === undefined) return <div style={{ minHeight: '100dvh', background: '#0D0D0E' }} />;
  if (stage === 'gone') return <Screen key="gone" desktop={DLetGo} phone={MLetGo} css={CSS} />;
  if (!cap) return <Screen desktop={DLost} phone={MLost} css={CSS} />;
  if (!due) return <Screen desktop={DNot} phone={MNot} vals={vals} css={CSS} />;
  if (stage === 'arrived') return <Screen key="arrived" desktop={DArr} phone={MArr} vals={vals} links={links} css={CSS} />;
  return <Screen key="open" desktop={DOpen} phone={MOpen} vals={vals} slots={slots} links={links} css={CSS} />;
}
