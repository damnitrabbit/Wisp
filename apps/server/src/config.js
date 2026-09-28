import { LIMITS } from '@wisp/shared';

const num = (name, fallback) => {
  const v = process.env[name];
  return v === undefined || v === '' ? fallback : Number(v);
};

// Every limit can be overridden by env (used by tests to shrink timers).
export const config = {
  port: num('PORT', 8080),
  allowedOrigins: (process.env.ALLOWED_ORIGINS || 'http://localhost:3000')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  limits: Object.fromEntries(Object.entries(LIMITS).map(([k, v]) => [k, num(k, v)])),

  // TURN (Cloudflare Realtime). Without these, clients get STUN only.
  turnKeyId: process.env.CF_TURN_KEY_ID || '',
  turnApiToken: process.env.CF_TURN_API_TOKEN || '',
  // Stop handing out relay credentials once this much relay traffic has been reported this month.
  // Cloudflare's free allowance is 1,000 GB; we stop well short of it.
  turnMonthlyBudgetGb: num('TURN_MONTHLY_BUDGET_GB', 800)
};
