'use client';
// OPEN POD — pick a room. The board is the design's (V5Rooms / V5MRooms); the slips are the live rooms, busiest first.
import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { CHANNELS } from '@wisp/shared';
import Screen, { useView } from '@/v5/Screen';
import D from '@/v5/screens/V5Rooms';
import M from '@/v5/screens/V5MRooms';
import DFull from '@/v5/screens/V5RoomsAllFull';
import MFull from '@/v5/screens/V5MRoomsAllFull';
import Asleep from '@/app/asleep/page';
import { useWisp } from '@/lib/wisp';
import { podsOpen } from '@/lib/v5/hours';
import Tpl, { fill, CSS } from './_parts/Tpl';
import { roomTitle, roomTheme } from './_parts/names';

const CAP = 10;
const PAGE = 10;
const LIST_CSS = CSS + '\n.v5-phone{min-height:100dvh}';

function slipHtml(c, i, phone) {
  const full = c.n >= CAP;
  const k = i % 10;
  const base = { name: roomTitle(c), theme: roomTheme(c), href: `/rooms/${c.id}`, n: c.n, label: `${roomTitle(c)}, ${c.n} of ${CAP}${full ? ', full' : ''}` };
  if (phone) {
    const lead = c.stage[0] || 'nobody yet';
    const more = c.stageCount > 1 ? c.stageCount - 1 : 0;
    return fill(full ? `mSlipFull${k}` : `mSlip${k}`, { ...base, lead, more, live: c.stage.length > 0, dots: fill(full ? 'mDotsFull' : `mDots${Math.min(c.n, CAP)}`) });
  }
  let sp = '';
  if (!c.stage.length) sp = fill('dSpNone');
  else {
    sp = full ? fill('dSp', { name: c.stage[0] }) : fill(`dSpW${k}`, { name: c.stage[0] });
    if (c.stage[1]) sp += fill('dSp', { name: c.stage[1] });
    if (c.stageCount > 2) sp += fill('dMore', { more: c.stageCount - 2 });
  }
  return fill(full ? `dSlipFull${k}` : `dSlip${k}`, { ...base, sp, dots: fill(full ? 'dDotsFull' : `dDots${Math.min(c.n, CAP)}`) });
}

// One slot renders the grid: the screen's own grid element (its inline style), filled with live slips.
function Grid({ node, list }) {
  const phone = /repeat\(2,/.test(node.attribs?.style || '');
  const html = useMemo(() => list.map((c, i) => slipHtml(c, i, phone)).join(''), [list, phone]);
  return (
    <div style={styleOf(node)}>
      <Tpl html={html} />
    </div>
  );
}
function styleOf(node) {
  const o = {};
  for (const d of String(node.attribs?.style || '').split(';')) {
    const i = d.indexOf(':');
    if (i > 0) o[d.slice(0, i).trim().replace(/-([a-z])/g, (m, x) => x.toUpperCase())] = d.slice(i + 1).trim();
  }
  return o;
}

export function useRoomList() {
  const lobby = useWisp((s) => s.lobby);
  return useMemo(() => {
    const by = new Map((lobby.channels || []).map((c) => [c.id, c]));
    // busiest first; ties keep the catalog order so the board doesn't shuffle
    return CHANNELS.map((c, i) => {
      const l = by.get(c.id);
      return { ...c, i, n: l?.count ?? 0, stage: l?.stage ?? [], stageCount: l?.stageCount ?? 0 };
    }).sort((a, b) => b.n - a.n || a.i - b.i);
  }, [lobby.channels]);
}

function Rooms() {
  const router = useRouter();
  const list = useRoomList();
  const lobby = useWisp((s) => s.lobby);
  const [page, setPage] = useState(0); // desktop shows ten slips at a time
  const [all, setAll] = useState(false); // phone: ten, or all of them
  const [open, setOpen] = useState(true);
  const phoneView = useView()?.phone;
  useEffect(() => {
    const t = () => setOpen(podsOpen());
    t();
    const id = setInterval(t, 30_000);
    return () => clearInterval(id);
  }, []);

  const known = (lobby.channels || []).length > 0;
  const allFull = known && list.every((c) => c.n >= CAP);
  const pages = Math.ceil(list.length / PAGE);

  // every room full: wait on this page, walk in when a seat opens
  const waiting = useRef(false);
  useEffect(() => {
    if (allFull) waiting.current = true;
    else if (waiting.current && known) {
      const free = list.find((c) => c.n < CAP);
      if (free) router.push(`/rooms/${free.id}`);
    }
  }, [allFull, known, list, router]);

  const pageList = useMemo(() => list.slice(page * PAGE, page * PAGE + PAGE), [list, page]);
  const phoneList = useMemo(() => (all ? list : list.slice(0, PAGE)), [list, all]);
  const slots = useMemo(() => ({
    grid: (node) => {
      const phone = /repeat\(2,/.test(node.attribs?.style || '');
      if (allFull) return <Grid node={node} list={list.slice(0, phone ? 4 : 5)} />;
      return <Grid node={node} list={phone ? phoneList : pageList} />;
    }
  }), [allFull, list, pageList, phoneList]);

  const vals = useMemo(() => {
    const start = page * PAGE;
    return {
      // desktop words say which ten are pinned; the phone says how long the pods stay open
      ...(phoneView
        ? { roomsLine: `${list.length} ROOMS · UNTIL 2AM`, moreLabel: all ? 'just the busiest ↑' : `see all ${list.length} rooms →` }
        : {
            roomsLine: page === 0 ? `${list.length} ROOMS TONIGHT · ${PAGE} PINNED HERE` : `${list.length} ROOMS TONIGHT · ${start + 1}–${Math.min(list.length, start + PAGE)} HERE`,
            moreLabel: page === 0 ? `see all ${list.length} →` : page < pages - 1 ? 'the rest →' : '← busiest first'
          })
    };
  }, [page, pages, all, list.length, phoneView]);

  const links = useMemo(() => ({
    morelabel: () => {
      setPage((p) => (p + 1) % pages);
      setAll((a) => !a);
    },
    'waiting-for-a-seat': () => {}
  }), [pages]);

  if (!open || lobby.pods?.open === false) return <Asleep />;
  if (allFull) return <Screen desktop={DFull} phone={MFull} slots={slots} links={links} css={CSS} />;
  return <Screen desktop={D} phone={M} vals={vals} slots={slots} links={links} css={LIST_CSS} />;
}

// The list is public (and crawlable); walking into a room goes through the age gate.
export default function Page() {
  return <Rooms />;
}
