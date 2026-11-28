// The one address search engines and link previews should use.
export const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL || (process.env.VERCEL ? 'https://notrace.chat' : 'http://localhost:3000');

export const SITE_NAME = 'NoTrace';
export const TAGLINE = 'Leave no trace.';
// Shown in every search result title. Anonymous + late-night + the two ways in (1:1 and voice pods).
export const TITLE = 'NoTrace · Anonymous late-night chat & voice pods';
// The zero spelling is the logo's; search engines should treat it as the same brand.
export const ALT_NAMES = ['N0TRACE', 'notrace.chat', 'NoTrace voice chat'];
export const DESCRIPTION =
  'An anonymous place for late nights: talk 1:1 or drop into voice pods with kind strangers (10pm–2am), vent and burn it, or leave an echo that fades in 24 hours. No sign-up, nothing about you stored.';
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
