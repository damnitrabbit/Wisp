# wisp

Talk to strangers. Leave no trace.

Anonymous, ephemeral voice rooms and 1:1 chat. No accounts, no logs, nothing stored. Built for $0.

## Layout

```
apps/server      Node + Socket.io signaling server (Northflank)
apps/web         Next.js site (Vercel)            ← coming next
packages/shared  limits, channels, error codes used by both
```

## How it works

- **Voice rooms.** 25 fixed rooms, 10 people max. The first two people in are mods. Everyone else listens and can
  raise a hand; mods bring people on stage, or move a speaker back down. Stay on stage for 2.5 minutes and you
  become a mod yourself. Mods can only be removed by reports from the room.
- **1:1.** Text first. Whoever has waited longest gets matched next. Either side can ask to switch to voice; both
  must agree.
- **Audio is peer to peer** (WebRTC). The server only passes connection messages between browsers. Calls fall back
  to a Cloudflare TURN relay when a direct connection is impossible.
- **Nothing is stored.** All state lives in memory and disappears when a room empties, a chat ends, or the server
  restarts.

## Run locally

```bash
npm install
npm run dev:server     # http://localhost:8080
npm test               # server tests
```

## Deploy

**Server → Northflank** (free Developer Sandbox)
- New service → combined (build + deploy) → this repo, branch `main`
- Build: Dockerfile, path `/apps/server/Dockerfile`, context `/`
- Port `8080`, HTTP, public
- Instances: **1** (state is in memory; more than one would split the rooms)
- Env: see `apps/server/.env.example`

---

© 2026 wisp · dug up by Damn_It_Rabbit
