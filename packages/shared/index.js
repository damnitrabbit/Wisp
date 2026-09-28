// Shared between the web app and the signaling server.
// Anything that both sides must agree on lives here: limits, channels, event names.

export const LIMITS = Object.freeze({
  ROOM_CAP: 10,
  FIRST_N_MODS: 2, // first two people into an empty room are mods (the first is the founding mod)
  MIN_STAGE_MODS: 2, // when mods drop below this, the longest-tenured speaker is promoted
  MOD_PROMOTION_MS: 150_000, // a speaker who stays on stage this long becomes a mod
  INVITE_EXPIRY_MS: 30_000, // stage invite from a mod
  HAND_EXPIRY_MS: 30_000, // raised hand resets if no mod answers
  HAND_COOLDOWN_MS: 10_000, // after a declined hand
  ROOM_REPORT_MAX: 5, // distinct reporters needed to remove someone from a room (lower in small rooms)
  PAIR_REPORT_THRESHOLD: 3, // distinct reporters before someone is removed from 1:1 matchmaking
  PAIR_BLOCK_MS: 24 * 60 * 60 * 1000,
  VOICE_REQUEST_EXPIRY_MS: 30_000,
  CHAT_MIN_INTERVAL_MS: 400,
  MSG_MAX: 500,
  ROOM_HISTORY: 200,
  RECONNECT_GRACE_MS: 15_000, // how long a dropped socket keeps its seat
  STILL_LOOKING_MS: 30_000 // client shows the "still looking" state after this
});

// Everything is anonymous: pseudonyms look like quiet_otter_42.
export const PSEUDONYM_RE = /^[a-z]{3,10}_[a-z]{3,10}_\d{2}$/;

const CHANNEL_ROWS = [
  ['Late Night Confessions', "Say the thing you'd never say in daylight."],
  ['Heartbreak Hotel', 'Checked in, not checking out anytime soon.'],
  ['Night Owls', 'For people who are, against their will, awake.'],
  ['Debate Arena', 'Pick a side. Defend it. No mercy, mostly good faith.'],
  ['Music & Vibes', "Whatever's in your ears right now, bring it here."],
  ['Rant Room', "Get it out. Nobody's going to fix it, just listen."],
  ['Random Roulette', "No theme. Whoever's here decides what happens."],
  ['Deep Questions', 'Would you rather... but it gets existential fast.'],
  ['Startup Chatter', 'Pitch it, roast it, or just complain about your cofounder.'],
  ['Gaming Lounge', 'Patch notes, rage quits, and one more round.'],
  ['Comedy Open Mic', 'Bomb here first so the real crowd never has to.'],
  ['Just Vent', 'No advice unless asked. Just get it off your chest.'],
  ['Movie Buffs', "Hot takes on things you definitely haven't seen."],
  ['Career Talk', 'Resumes, burnout, and whether to take the offer.'],
  ['Blind Dates', 'Anonymous small talk with mild romantic tension.'],
  ['Philosophy Hour', 'Free will, simulation theory, 2am energy at any hour.'],
  ['Support Circle', "A soft place to land. Be kind, that's the whole rule."],
  ['Study Hall', "Quiet company for whatever you're grinding through."],
  ['True Crime', 'Mildly concerning how much everyone here knows.'],
  ['Conspiracy Corner', 'The moon landing is not on the agenda. Everything else is.'],
  ['Book Club', "Whatever you're reading, someone here has opinions."],
  ['Poetry & Prose', "Read something out loud. It's braver than it sounds."],
  ['Travel Tales', "Where you've been and where you're pretending to be."],
  ['Music Production', "Beats, DAWs, and gear you can't actually afford."],
  ['Language Exchange', "Butcher a new language. Everyone's patient here."]
];

export const slugify = (s) =>
  s.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

export const CHANNELS = Object.freeze(
  CHANNEL_ROWS.map(([name, blurb]) => Object.freeze({ id: slugify(name), name, blurb }))
);

export const CHANNEL_BY_ID = new Map(CHANNELS.map((c) => [c.id, c]));

export const ROLES = Object.freeze({ MOD: 'mod', SPEAKER: 'speaker', LISTENER: 'listener' });

// Error codes returned in acks / joinError. The web app maps these to the notices in the design.
export const ERRORS = Object.freeze({
  NOT_FOUND: 'not_found',
  FULL: 'full',
  REMOVED: 'removed',
  BLOCKED: 'blocked',
  SLOW: 'slow',
  TOO_LONG: 'too_long',
  EMPTY: 'empty',
  NOT_ALLOWED: 'not_allowed',
  BAD_REQUEST: 'bad_request',
  COOLDOWN: 'cooldown'
});
