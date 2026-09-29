// Crawlable pages for the searches people actually make. Each one answers its own question with
// real content (search engines penalise thin copies of the same page), and all link into the app.
// Written in sentence case; the site's CSS shows it in capitals.

export const LANDING = [
  {
    slug: 'omegle-alternative',
    title: 'Omegle alternative with voice rooms, no sign-up',
    description:
      'Looking for an Omegle alternative? NoTrace pairs you with a random stranger for 1:1 chat or drops you into anonymous voice rooms. No account, nothing stored.',
    h1: 'An Omegle alternative that keeps nothing.',
    lead:
      'Omegle closed in 2023. NoTrace keeps what people liked about it, talking to someone you will never meet, and fixes what went wrong: rooms moderate themselves, voice needs consent, and nothing about you is stored.',
    sections: [
      {
        h: 'What is the same',
        body: 'One click and you are talking to a random stranger. No profile, no login, no friends list. Skip whenever it is not clicking and you are matched with someone new.'
      },
      {
        h: 'What is different',
        body: 'Chats start as text. Voice only begins when both of you say yes. Beyond 1:1, there are 25 themed voice rooms for up to 10 people, like Late Night Confessions, Rant Room and Deep Questions. There is no video.'
      },
      {
        h: 'Why it is safer',
        body: 'Everyone joins a room as a listener. Mods are the first two people in, plus anyone who stays on stage for two and a half minutes. Enough reports from different people remove someone automatically, mods included. It is for adults only (18+).'
      }
    ],
    faq: [
      { q: 'Is NoTrace free?', a: 'Yes. There is nothing to buy and no account to create.' },
      { q: 'Does NoTrace have video chat?', a: 'No. It is text and voice only, by design. Voice starts only when both people agree.' },
      { q: 'Is anything saved?', a: 'No. There is no database. Rooms, chats and reports live in memory and disappear when the room empties or the chat ends.' }
    ]
  },
  {
    slug: 'talk-to-strangers',
    title: 'Talk to strangers online, anonymously',
    description:
      'Talk to strangers online without an account. Random 1:1 text chat that can turn into voice, or anonymous voice rooms with up to 10 people. Nothing is kept.',
    h1: 'Talk to strangers. Leave no trace.',
    lead:
      'Sometimes the easiest person to talk to is someone who will never know who you are. NoTrace gives you a new name every visit, like quiet_otter_42, and forgets you the moment you leave.',
    sections: [
      {
        h: 'Two ways to talk',
        body: 'Random 1:1 chat matches you with whoever has been waiting longest. It starts as text, and either of you can ask to switch to voice. Voice rooms are for groups: pick a theme, join as a listener, and raise your hand when you want to speak.'
      },
      {
        h: 'Nothing follows you',
        body: 'There are no accounts, no message history and no cookies. Messages go to the other person and nowhere else. If you want to keep the same name on your device, you can opt in; it is saved in your browser, not on our side.'
      },
      {
        h: 'Strangers, but not a free-for-all',
        body: 'A report button is always one click away, and reports from several different people remove someone automatically. In voice rooms, only mods decide who gets the mic.'
      }
    ],
    faq: [
      { q: 'Do I need to sign up to talk to strangers?', a: 'No. Open the site, confirm you are 18 or older, and pick 1:1 chat or a voice room.' },
      { q: 'Can the other person see who I am?', a: 'They see a random name like quiet_otter_42. In a voice call, audio goes directly between devices, so their browser can see your IP address, as with any peer-to-peer call.' },
      { q: 'What if someone is rude?', a: 'Skip them, or report them. Reports are anonymous.' }
    ]
  },
  {
    slug: 'anonymous-voice-chat',
    title: 'Anonymous voice chat rooms with strangers',
    description:
      'Anonymous voice chat rooms for up to 10 people: late night confessions, rants, debates, music and more. Join as a listener, raise your hand to speak. No sign-up.',
    h1: 'Anonymous voice chat rooms. Up to 10 strangers each.',
    lead:
      'Like a late-night radio show where anyone can call in. There are 25 themed rooms, from Late Night Confessions and Heartbreak Hotel to Debate Arena, Study Hall and Language Exchange.',
    sections: [
      {
        h: 'How a room works',
        body: 'You walk in as a listener with your mic off. Raise your hand and a mod can bring you on stage, or a mod can invite you up. Stay on stage for two and a half minutes and you become a mod yourself.'
      },
      {
        h: 'Who is in charge',
        body: 'The room is. The first two people in an empty room become its mods. Mods can bring people up and move speakers back down, but cannot touch other mods; only reports from the room can remove a mod.'
      },
      {
        h: 'Your voice stays yours',
        body: 'Audio travels directly between the people in the room, never through our server, and is never recorded. The room chat is cleared as soon as the room empties.'
      }
    ],
    faq: [
      { q: 'How many people fit in a voice room?', a: 'Up to 10. When a room is full, pick another one; the list shows the busiest rooms first.' },
      { q: 'Can I just listen?', a: 'Yes. Everyone starts as a listener, and you can stay one the whole time and still type in the room chat.' },
      { q: 'Does it work on phones?', a: 'Yes. It runs in the browser on desktop and mobile. Nothing to install.' }
    ]
  },
  {
    slug: 'random-chat',
    title: 'Random chat with strangers, no registration',
    description:
      'Free random chat with strangers, no registration. Get matched 1:1 in seconds, skip anytime, switch to voice only if you both agree. Anonymous and nothing stored.',
    h1: 'Random chat. One stranger at a time.',
    lead:
      'Press start and you are matched with whoever has been waiting longest. Not clicking? Skip and meet someone new. No registration, no history, nothing saved.',
    sections: [
      {
        h: 'Fast and fair matching',
        body: 'The queue is first come, first served, and you are never rematched straight back with the person you just skipped. If it is quiet, you are first in line for the next person.'
      },
      {
        h: 'Text first, voice by consent',
        body: 'Every chat starts as text. Either person can ask to switch to voice, and it only starts if the other says yes. Text keeps working during the call, and either of you can end it anytime.'
      },
      {
        h: 'Built to forget',
        body: 'There is no database behind NoTrace. Messages are passed to your match and never stored. When the chat ends, it is gone for both of you.'
      }
    ],
    faq: [
      { q: 'Is the random chat really anonymous?', a: 'You get a random name and there is no account, so nothing ties the chat to you. Be careful what you share: the other person is a stranger.' },
      { q: 'How do I skip?', a: 'Press S or hit Escape twice, or tap Skip on your phone.' },
      { q: 'Who can use it?', a: 'Adults only. NoTrace is for people 18 and older.' }
    ]
  }
];

export const LANDING_BY_SLUG = new Map(LANDING.map((p) => [p.slug, p]));
