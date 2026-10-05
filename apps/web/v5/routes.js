// Which page each design screen lives on. Desktop (V5X) and phone (V5MX) screens share a route.
// A link in a generated screen points at "V5Something.dc.html"; <Screen> turns it into the route here.
const R = {
  Boot: '/', Story: '/', Age: '/', NotYet: '/not-yet', Remember: '/home', WelcomeBack: '/home',
  Home: '/home', HomeOpen: '/home',
  Burn: '/burn', BurnVoice: '/burn', BurnMid: '/burn', BurnGone: '/burn', BurnEmpty: '/burn', BurnRecording: '/burn',
  Echoes: '/echoes', EchoesEmpty: '/echoes', EchoWrite: '/echoes/write', EchoPinned: '/echoes/write', EchoTooLong: '/echoes/write',
  EchoThread: '/echoes', EchoNoReplies: '/echoes', EchoYours: '/echoes',
  UnsentWrite: '/echoes/unsent', UnsentPinned: '/echoes/unsent', UnsentOpen: '/echoes',
  Capsule: '/capsule', CapsuleSealed: '/capsule', CapsuleOpen: '/capsule/open', CapsuleNotYet: '/capsule/open', CapsuleArrived: '/capsule/open', CapsuleLetGo: '/capsule/open',
  CapsuleLost: '/capsule/open', CapsuleEmailError: '/capsule',
  Matching: '/talk', Pod: '/talk', PodNudge: '/talk', PodEnd: '/talk', Requeue: '/talk', Reported: '/talk',
  VoiceAsk: '/talk', VoiceWait: '/talk', Call: '/talk', VoiceDeclined: '/talk', CallDropped: '/talk', SendFailed: '/talk',
  PodsClosing: '/talk', PodsClosedMidChat: '/talk', NoOneFree: '/talk', Reconnect: '/talk',
  Listener: '/listen',
  Rooms: '/rooms', RoomsAllFull: '/rooms', Room: '/rooms', RoomHand: '/rooms', MovedOffStage: '/rooms', RoomAlone: '/rooms',
  Question: '/question', QuestionEmpty: '/question',
  Asleep: '/asleep', Paused: '/asleep',
  Help: '/help', Privacy: '/privacy', Terms: '/terms', Notices: '/terms',
  MicAsk: '/talk', MicBlocked: '/talk', NoVoice: '/talk', Offline: '/home', NotFound: '/home', SomethingBroke: '/home',
  Loading: '/home', StorageBlocked: '/home', SlowDown: '/home'
};

export function routeFor(href) {
  if (!href) return null;
  const m = /^V5(?:M(?=[A-Z]))?([A-Za-z]+)\.dc\.html(.*)$/.exec(href);
  if (!m) return null;
  return (R[m[1]] || '/home') + (m[2] || '');
}

export default R;
