// Pod hours and tonight's question. Shared so the web app and the signaling server always agree.
// Pods (talk, listen, open rooms, tonight's question) are open 22:00–02:00 India time (Asia/Kolkata,
// UTC+5:30, no DST) every night.

export const POD_OPEN_MIN = 22 * 60; // 22:00
export const POD_CLOSE_MIN = 2 * 60; // 02:00
export const IST_OFFSET_MIN = 330;
export const POD_CLOSING_WARN_MIN = 10; // the "10 minutes left" slip
export const POD_CLOSED = 'closed'; // error code when a join is refused outside hours

// minutes since midnight, India time (fractional)
export function istMinutes(now = new Date()) {
  const t = now.getTime() / 60000 + IST_OFFSET_MIN;
  return ((t % 1440) + 1440) % 1440;
}

// Inside the nightly window? (ignores any always-open override; callers add their own)
export function podWindowOpen(now = new Date()) {
  const m = istMinutes(now);
  return m >= POD_OPEN_MIN || m < POD_CLOSE_MIN;
}

// Minutes until the window closes (0 when closed).
export function podMinsToClose(now = new Date()) {
  if (!podWindowOpen(now)) return 0;
  return (POD_CLOSE_MIN - istMinutes(now) + 1440) % 1440;
}

// The night a moment belongs to, as an India-time date string (YYYY-MM-DD). 00:00–02:00 belongs to the
// night before, so the question doesn't change at midnight.
export function podNight(now = new Date()) {
  const ist = new Date(now.getTime() + IST_OFFSET_MIN * 60000 - (istMinutes(now) < POD_CLOSE_MIN ? 86400000 : 0));
  return ist.toISOString().slice(0, 10);
}

export const QUESTIONS = Object.freeze([
  "What's something you pretend doesn't bother you?",
  'What did you need to hear this week that nobody said?',
  "What's a small thing that made today a little better?",
  'Who do you miss, and what would you tell them?',
  "What's something you're proud of that nobody noticed?",
  'What would you do tomorrow if you weren’t afraid?',
  "What's keeping you up tonight?",
  'What do you wish people asked you more often?',
  "What's a habit you're trying to let go of?",
  'Where do you feel most like yourself?',
  "What's something you changed your mind about?",
  'What are you carrying that isn’t yours to carry?',
  'What would you tell yourself from a year ago?',
  "What's a sound or smell that takes you home?"
]);

// Tonight's question: the same for everyone, picked by date.
export function questionFor(now = new Date()) {
  const [y, m, d] = podNight(now).split('-').map(Number);
  const day = Math.floor(Date.UTC(y, m - 1, d) / 86400000);
  return QUESTIONS[day % QUESTIONS.length];
}

export const QUESTION_ROOM = Object.freeze({ id: 'question', name: "tonight's question", blurb: 'one room, one question, everyone welcome', cap: 8 });
