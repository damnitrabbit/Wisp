// The one address search engines and link previews should use.
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || (process.env.VERCEL ? 'https://notrace.chat' : 'http://localhost:3000');

export const SITE_NAME = 'NoTrace';
export const TAGLINE = 'Leave no trace.';
// Shown in every search result title. "Voice" and "strangers" are what set NoTrace apart from similarly named text-chat apps.
export const TITLE = 'NoTrace · Anonymous voice rooms with strangers';
// The zero spelling is the logo's; search engines should treat it as the same brand.
export const ALT_NAMES = ['N0TRACE', 'notrace.chat', 'NoTrace voice chat'];
export const DESCRIPTION =
  'N0TRACE: anonymous voice rooms and random 1:1 chat with strangers. No sign-up, no video, nothing stored. A free Omegle alternative with 25 themed voice rooms.';
export const KEYWORDS = [
  'n0trace',
  'notrace voice chat',
  'notrace.chat',
  'talk to strangers',
  'omegle alternative',
  'anonymous chat',
  'random chat',
  'chat with strangers',
  'anonymous voice chat',
  'voice chat rooms',
  'random voice chat',
  'stranger chat',
  'free chat rooms',
  'online chat no sign up',
  'anonymous chat rooms',
  'talk to strangers online',
  'late night chat',
  'vent to strangers'
];
