// Pod hours: open 22:00–02:00 India time (Asia/Kolkata, UTC+5:30, no DST) every night.
// NEXT_PUBLIC_PODS_ALWAYS_OPEN=1 keeps them open (testing).
const OPEN_MIN = 22 * 60; // 22:00
const CLOSE_MIN = 2 * 60; // 02:00
const IST_OFFSET_MIN = 330;

const alwaysOpen = () => process.env.NEXT_PUBLIC_PODS_ALWAYS_OPEN === '1';

// minutes since midnight, India time (fractional)
function istMinutes(now) {
  const t = now.getTime() / 60000 + IST_OFFSET_MIN;
  return ((t % 1440) + 1440) % 1440;
}

export function podsOpen(now = new Date()) {
  if (alwaysOpen()) return true;
  const m = istMinutes(now);
  return m >= OPEN_MIN || m < CLOSE_MIN;
}

// { open, minsToOpen, minsToClose, opensAt: Date, closesAt: Date, label }
// minsToOpen is 0 while open; minsToClose is 0 while closed.
export function podsInfo(now = new Date()) {
  const m = istMinutes(now);
  const open = podsOpen(now);
  const toOpen = open ? 0 : Math.ceil(OPEN_MIN - m); // closed => between 02:00 and 22:00
  const toClose = open ? (alwaysOpen() && !(m >= OPEN_MIN || m < CLOSE_MIN) ? Infinity : Math.ceil((CLOSE_MIN - m + 1440) % 1440)) : 0;
  const at = (mins) => new Date(now.getTime() + mins * 60000);
  return {
    open,
    minsToOpen: toOpen,
    minsToClose: toClose,
    opensAt: open ? null : at(toOpen),
    closesAt: open && Number.isFinite(toClose) ? at(toClose) : null,
    label: open ? (Number.isFinite(toClose) ? fmtDur(toClose) : '') : fmtDur(toOpen),
  };
}

// 102 -> "1H 42M", 40 -> "40M", 120 -> "2H"
export function fmtDur(mins) {
  if (!Number.isFinite(mins)) return '';
  const h = Math.floor(mins / 60), mm = Math.max(0, Math.round(mins % 60));
  if (!h) return `${mm}M`;
  return mm ? `${h}H ${mm}M` : `${h}H`;
}
