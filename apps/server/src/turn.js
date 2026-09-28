import { config } from './config.js';

const STUN_ONLY = [{ urls: ['stun:stun.cloudflare.com:3478', 'stun:stun.l.google.com:19302'] }];
const TTL_S = 24 * 60 * 60;

let cache = null; // { iceServers, expiresAt }
let inflight = null;

// Relay usage as reported by clients (bytes that went through TURN), per calendar month.
// In memory only: a redeploy resets it, so the budget is deliberately set well below the free tier.
const usage = { month: monthKey(), bytes: 0 };

function monthKey(d = new Date()) {
  return `${d.getUTCFullYear()}-${d.getUTCMonth() + 1}`;
}

function rollMonth() {
  const m = monthKey();
  if (usage.month !== m) {
    usage.month = m;
    usage.bytes = 0;
  }
}

export function reportRelayBytes(bytes) {
  rollMonth();
  usage.bytes += bytes;
}

export function relayBudgetLeft() {
  rollMonth();
  return usage.bytes < config.turnMonthlyBudgetGb * 1e9;
}

export function turnStatus() {
  rollMonth();
  return {
    configured: Boolean(config.turnKeyId && config.turnApiToken),
    month: usage.month,
    reportedGb: +(usage.bytes / 1e9).toFixed(3),
    budgetGb: config.turnMonthlyBudgetGb,
    relayEnabled: relayBudgetLeft()
  };
}

async function fetchCloudflare() {
  const res = await fetch(
    `https://rtc.live.cloudflare.com/v1/turn/keys/${config.turnKeyId}/credentials/generate-ice-servers`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${config.turnApiToken}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ ttl: TTL_S })
    }
  );
  if (!res.ok) throw new Error(`cloudflare turn ${res.status}`);
  const body = await res.json();
  const list = Array.isArray(body.iceServers) ? body.iceServers : [body.iceServers];
  // Port 53 is blocked by most browsers; drop those URLs to avoid slow ICE timeouts.
  return list
    .map((s) => ({ ...s, urls: [].concat(s.urls).filter((u) => !/:53(\?|$)/.test(u)) }))
    .filter((s) => s.urls.length);
}

// Credentials are shared by everyone and refreshed twice a day. They only allow relaying
// media, and Cloudflare bills against our free allowance, which the budget check protects.
export async function getIceServers() {
  if (!config.turnKeyId || !config.turnApiToken || !relayBudgetLeft()) return STUN_ONLY;
  const now = Date.now();
  if (cache && cache.expiresAt > now) return cache.iceServers;
  if (!inflight) {
    inflight = fetchCloudflare()
      .then((iceServers) => {
        cache = { iceServers, expiresAt: now + (TTL_S / 2) * 1000 };
        return iceServers;
      })
      .catch((err) => {
        console.error('[turn] could not fetch credentials:', err.message);
        return STUN_ONLY;
      })
      .finally(() => {
        inflight = null;
      });
  }
  return inflight;
}
