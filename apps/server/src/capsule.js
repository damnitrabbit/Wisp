// TIME CAPSULE reminder: one scheduled email, nothing else.
// The letter itself never reaches the server: it stays sealed in the writer's browser (localStorage).
// If they ask for a reminder, we hand Resend an email address and a send time, and keep nothing:
// no database, no log line with the address, no copy of the letter. Resend holds the scheduled email
// until it sends. Resend schedules at most 30 days ahead, so capsules with a reminder open within 30 days.
import { ERRORS } from '@wisp/shared';

export const MAX_AHEAD_MS = 30 * 24 * 3600_000; // Resend's scheduling window (scheduled_at, "up to 30 days")
export const MIN_AHEAD_MS = 60_000;
const EMAIL_RE = /^[^\s@<>()[\]\\,;:"]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;
const OPEN_URL = 'https://notrace.chat/capsule/open';

export const isEmail = (e) => typeof e === 'string' && e.length <= 254 && EMAIL_RE.test(e);

export function reminderEmail() {
  const subject = 'a letter from you arrived';
  const text = [
    'You wrote yourself a letter a while back and sealed it. Today is the day it opens.',
    '',
    `Open it here, in the same browser you sealed it in: ${OPEN_URL}`,
    '',
    "We never had a copy, and this email doesn't carry one. The letter only lives in that browser. If its data got cleared, it went with it, and that's okay too.",
    '',
    'N0TRACE',
    'We kept your address only to send this. Nothing else.'
  ].join('\n');
  const html = `<!doctype html><html><body style="margin:0;background:#0D0D0E;color:#E9E9E7;font-family:Georgia,serif">
<div style="max-width:480px;margin:0 auto;padding:40px 24px">
<p style="font-size:20px;line-height:1.5;margin:0 0 18px">You wrote yourself a letter a while back and sealed it. Today is the day it opens.</p>
<p style="margin:0 0 26px"><a href="${OPEN_URL}" style="display:inline-block;background:#F4EFE3;color:#2A2622;text-decoration:none;font-family:'Courier New',monospace;font-weight:bold;letter-spacing:.16em;font-size:13px;padding:14px 22px">OPEN IT</a></p>
<p style="font-size:15px;line-height:1.6;color:#A39A8C;margin:0 0 12px">Open it in the same browser you sealed it in. We never had a copy, and this email doesn't carry one. If that browser's data got cleared, the letter went with it, and that's okay too.</p>
<p style="font-family:'Courier New',monospace;font-size:11px;letter-spacing:.14em;color:#8A8A8F;margin:28px 0 0">N0TRACE · WE KEPT YOUR ADDRESS ONLY TO SEND THIS</p>
</div></body></html>`;
  return { subject, text, html };
}

// "Pods asleep" → EMAIL ME AT 10PM: the same one-off scheduled email, for tonight's pods opening.
export function podsEmail() {
  const url = 'https://notrace.chat/home';
  const subject = 'the pods are open';
  const text = [
    "It's 10pm. The pods are open until 2am: talk to someone, listen, or just sit in a room.",
    '',
    `Come in here: ${url}`,
    '',
    'N0TRACE',
    'We kept your address only to send this. Nothing else.'
  ].join('\n');
  const html = `<!doctype html><html><body style="margin:0;background:#0D0D0E;color:#E9E9E7;font-family:Georgia,serif">
<div style="max-width:480px;margin:0 auto;padding:40px 24px">
<p style="font-size:20px;line-height:1.5;margin:0 0 18px">It's 10pm. The pods are open until 2am: talk to someone, listen, or just sit in a room.</p>
<p style="margin:0 0 26px"><a href="${url}" style="display:inline-block;background:#F4EFE3;color:#2A2622;text-decoration:none;font-family:'Courier New',monospace;font-weight:bold;letter-spacing:.16em;font-size:13px;padding:14px 22px">COME IN</a></p>
<p style="font-family:'Courier New',monospace;font-size:11px;letter-spacing:.14em;color:#8A8A8F;margin:28px 0 0">N0TRACE · WE KEPT YOUR ADDRESS ONLY TO SEND THIS</p>
</div></body></html>`;
  return { subject, text, html };
}
const PODS_AHEAD_MS = 24 * 3600_000; // tonight's opening is never more than a day away

// fetchImpl / env / now are injectable for tests.
export function makeCapsuleRemind({ fetchImpl = (...a) => fetch(...a), env = process.env, now = () => Date.now(), perHour = 3 } = {}) {
  const recent = new Map(); // session token -> request times (memory only; no addresses)
  let swept = 0;
  const sweep = (t) => {
    if (t - swept < 60_000) return;
    swept = t;
    for (const [k, ts] of recent) {
      const keep = ts.filter((x) => x > t - 3600_000);
      if (keep.length) recent.set(k, keep);
      else recent.delete(k);
    }
  };

  return async function remind(user, { email, openAt, kind } = {}) {
    const t = now();
    sweep(t);
    const pods = kind === 'pods';
    if (!isEmail(email)) return { error: ERRORS.BAD_REQUEST, field: 'email' };
    const at = typeof openAt === 'string' || typeof openAt === 'number' ? new Date(openAt).getTime() : NaN;
    if (!Number.isFinite(at) || at < t + MIN_AHEAD_MS) return { error: ERRORS.BAD_REQUEST, field: 'openAt' };
    const max = pods ? PODS_AHEAD_MS : MAX_AHEAD_MS;
    if (at > t + max) return { error: ERRORS.TOO_LONG, maxAheadMs: max };

    const key = user?.token || user?.id || 'anon';
    const mine = (recent.get(key) || []).filter((x) => x > t - 3600_000);
    if (mine.length >= perHour) return { error: ERRORS.SLOW };
    mine.push(t);
    recent.set(key, mine);

    const apiKey = env.RESEND_API_KEY;
    if (!apiKey) return { error: 'unavailable' };
    const { subject, text, html } = pods ? podsEmail() : reminderEmail();
    try {
      const res = await fetchImpl('https://api.resend.com/emails', {
        method: 'POST',
        headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
        body: JSON.stringify({
          from: env.RESEND_FROM || 'N0TRACE <letters@notrace.chat>',
          to: [email],
          subject,
          text,
          html,
          scheduled_at: new Date(at).toISOString()
        })
      });
      if (!res.ok) {
        console.warn(`[capsule] reminder not scheduled (resend ${res.status})`); // never the address
        return { error: 'unavailable' };
      }
      return { ok: true, openAt: new Date(at).toISOString() };
    } catch {
      console.warn('[capsule] reminder not scheduled (network)');
      return { error: 'unavailable' };
    }
  };
}

// The one the socket server uses.
export const capsuleRemind = makeCapsuleRemind();
