'use client';
import { useMemo } from 'react';
import Guard from '@/components/Guard';
import Screen from '@/v5/Screen';
import D from '@/v5/screens/V5Echoes';
import M from '@/v5/screens/V5MEchoes';
import DE from '@/v5/screens/V5EchoesEmpty';
import ME from '@/v5/screens/V5MEchoesEmpty';
import { useEchoList } from '@/lib/echoes';
import { DeskWall, PhoneWall } from './ui';

// The phone wall is drawn as one long board; the live one is as long as tonight's notes.
const PHONE_CSS = '.v5-phone{min-height:100dvh !important}';

function Wall() {
  const { notes, skew } = useEchoList();
  const now = Date.now() + skew;
  const slots = useMemo(
    () => ({
      wall: (node) =>
        // the phone board's wall sits 22px under the "your turn?" row; the desktop one doesn't
        /margin-top:22px/.test(node.attribs?.style || '') ? <PhoneWall notes={notes ?? []} now={now} /> : <DeskWall notes={notes ?? []} now={now} />
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [notes, Math.floor(now / 60_000)]
  );
  // Only the confirmed-empty wall (notes === []) gets the "the wall is quiet" board. While still loading
  // (notes === null) we show the wall frame with an empty board and the notes rise in, so there is no
  // "quiet" message flashing to a full wall on every visit. `tail` hides the "that's everything" end line
  // until there are actually notes above it.
  if (notes && notes.length === 0) return <Screen desktop={DE} phone={ME} />;
  return <Screen desktop={D} phone={M} slots={slots} css={PHONE_CSS} vals={{ tail: Boolean(notes && notes.length) }} />;
}

export default function Page() {
  return (
    <Guard>
      <Wall />
    </Guard>
  );
}
