// Shrink every timer so the whole suite runs in seconds.
Object.assign(process.env, {
  MOD_PROMOTION_MS: '600',
  INVITE_EXPIRY_MS: '300',
  HAND_EXPIRY_MS: '300',
  HAND_COOLDOWN_MS: '300',
  VOICE_REQUEST_EXPIRY_MS: '300',
  RECONNECT_GRACE_MS: '400',
  CHAT_MIN_INTERVAL_MS: '50',
  PER_IP_OPEN: '10000',
  PER_IP_PER_MIN: '10000'
});

const { createWisp } = await import('../src/index.js');
const { io: ioc } = await import('socket.io-client');

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function startServer() {
  const wisp = createWisp();
  const port = await wisp.listen(0);
  const clients = [];
  let n = 0;

  async function connect({ token, name } = {}) {
    token ??= `test-token-${Date.now()}-${n++}-abcdef`;
    const socket = ioc(`http://localhost:${port}`, { auth: { token, name }, transports: ['websocket'], forceNew: true, reconnection: false });
    const log = [];
    const waiters = [];
    socket.onAny((event, payload) => {
      log.push([event, payload]);
      for (const w of [...waiters]) if (w.event === event && w.pred(payload)) {
        waiters.splice(waiters.indexOf(w), 1);
        w.resolve(payload);
      }
    });
    const c = {
      socket,
      token,
      log,
      session: null,
      emit: (event, payload = {}) => new Promise((resolve) => socket.emit(event, payload, resolve)),
      waitFor(event, pred = () => true, ms = 2000) {
        const seen = log.find(([e, p]) => e === event && pred(p) && !c.consumed.has(p));
        if (seen) {
          c.consumed.add(seen[1]);
          return Promise.resolve(seen[1]);
        }
        return new Promise((resolve, reject) => {
          const w = { event, pred, resolve: (p) => (c.consumed.add(p), resolve(p)) };
          waiters.push(w);
          setTimeout(() => {
            if (waiters.includes(w)) {
              waiters.splice(waiters.indexOf(w), 1);
              reject(new Error(`timeout waiting for ${event}`));
            }
          }, ms);
        });
      },
      saw: (event) => log.some(([e]) => e === event),
      consumed: new WeakSet(),
      close: () => socket.disconnect()
    };
    clients.push(c);
    c.session = await c.waitFor('session:ready');
    return c;
  }

  return {
    wisp,
    port,
    connect,
    async stop() {
      for (const c of clients) c.socket.disconnect();
      await wisp.close();
    }
  };
}

export const member = (snap, id) => snap.members.find((m) => m.id === id);
