'use client';
// WebRTC plumbing shared by voice rooms (mesh) and 1:1 calls (single peer).
// Audio only. Media goes browser to browser; the server just relays these messages.
import { send, bus } from './wisp';

// One peer connection with a single sendrecv audio transceiver. Only the initiator ever makes
// offers, so there's no glare to resolve; going on/off stage just swaps the outgoing track.
export class Peer {
  constructor({ iceServers, initiator, signal, onStream, onDead }) {
    this.initiator = initiator;
    this.signal = signal;
    this.onStream = onStream;
    this.onDead = onDead;
    this.track = null;
    this.pending = [];
    this.closed = false;
    this.pc = new RTCPeerConnection({ iceServers, bundlePolicy: 'max-bundle' });
    this.pc.onicecandidate = (e) => e.candidate && this.signal({ candidate: e.candidate.toJSON() });
    this.pc.ontrack = (e) => this.onStream(e.streams[0] ?? new MediaStream([e.track]));
    this.pc.onconnectionstatechange = () => {
      const st = this.pc.connectionState;
      if (st === 'failed') this.onDead?.('failed');
      if (st === 'disconnected') {
        clearTimeout(this.dcTimer);
        this.dcTimer = setTimeout(() => this.pc.connectionState === 'disconnected' && this.onDead?.('failed'), 6000);
      }
    };
  }

  async start(track) {
    this.track = track ?? null;
    if (!this.initiator) return;
    const t = this.pc.addTransceiver('audio', { direction: 'sendrecv' });
    await t.sender.replaceTrack(this.track);
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    this.signal({ sdp: this.pc.localDescription.toJSON() });
  }

  async handle(data) {
    if (this.closed || !data) return;
    try {
      if (data.sdp) {
        await this.pc.setRemoteDescription(data.sdp);
        if (data.sdp.type === 'offer') {
          const t = this.pc.getTransceivers()[0];
          if (t) {
            t.direction = 'sendrecv';
            await t.sender.replaceTrack(this.track);
          }
          const answer = await this.pc.createAnswer();
          await this.pc.setLocalDescription(answer);
          this.signal({ sdp: this.pc.localDescription.toJSON() });
        }
        for (const c of this.pending.splice(0)) await this.pc.addIceCandidate(c).catch(() => {});
      } else if (data.candidate) {
        if (this.pc.remoteDescription) await this.pc.addIceCandidate(data.candidate).catch(() => {});
        else this.pending.push(data.candidate);
      }
    } catch (err) {
      console.warn('[rtc]', err?.message);
    }
  }

  async setTrack(track) {
    this.track = track ?? null;
    const t = this.pc.getTransceivers()[0];
    if (t && !this.closed) await t.sender.replaceTrack(this.track).catch(() => {});
  }

  close() {
    this.closed = true;
    clearTimeout(this.dcTimer);
    try { this.pc.close(); } catch {}
  }
}

// ---------- audio out ----------

const players = new Map();
export function play(id, stream) {
  let el = players.get(id);
  if (!el) {
    el = document.createElement('audio');
    el.autoplay = true;
    el.setAttribute('playsinline', '');
    el.style.display = 'none';
    document.body.appendChild(el);
    players.set(id, el);
  }
  if (el.srcObject !== stream) el.srcObject = stream;
  el.play().catch(() => bus.emit('audioBlocked'));
}
export function stop(id) {
  const el = players.get(id);
  if (!el) return;
  el.srcObject = null;
  el.remove();
  players.delete(id);
}
export function resumeAudio() {
  for (const el of players.values()) el.play().catch(() => {});
  ctx?.resume?.();
}

// ---------- levels (who is speaking) ----------

let ctx = null;
const meters = new Map();
export function meter(id, stream) {
  if (typeof window === 'undefined' || !stream) return;
  if (meters.get(id)?.stream === stream) return;
  unmeter(id);
  try {
    ctx ??= new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === 'suspended') ctx.resume?.().catch?.(() => {});
    const src = ctx.createMediaStreamSource(stream);
    const an = ctx.createAnalyser();
    an.fftSize = 512;
    src.connect(an);
    meters.set(id, { stream, src, an, buf: new Uint8Array(an.fftSize) });
  } catch {}
}
export function unmeter(id) {
  const m = meters.get(id);
  if (!m) return;
  try { m.src.disconnect(); } catch {}
  meters.delete(id);
}
export function speakingIds(threshold = 0.035) {
  const out = new Set();
  for (const [id, m] of meters) {
    m.an.getByteTimeDomainData(m.buf);
    let sum = 0;
    for (const v of m.buf) sum += ((v - 128) / 128) ** 2;
    if (Math.sqrt(sum / m.buf.length) > threshold) out.add(id);
  }
  return out;
}

// ---------- relay usage (keeps the TURN free tier honest) ----------

const lastBytes = new WeakMap();
export async function reportRelay(pcs) {
  let total = 0;
  for (const pc of pcs) {
    try {
      const stats = await pc.getStats();
      let pair = null;
      stats.forEach((r) => {
        if (r.type === 'transport' && r.selectedCandidatePairId) pair = stats.get(r.selectedCandidatePairId);
      });
      if (!pair) stats.forEach((r) => { if (r.type === 'candidate-pair' && r.nominated && r.state === 'succeeded') pair = r; });
      if (!pair) continue;
      const local = stats.get(pair.localCandidateId);
      const remote = stats.get(pair.remoteCandidateId);
      if (local?.candidateType !== 'relay' && remote?.candidateType !== 'relay') continue;
      const bytes = (pair.bytesSent ?? 0) + (pair.bytesReceived ?? 0);
      total += Math.max(0, bytes - (lastBytes.get(pc) ?? 0));
      lastBytes.set(pc, bytes);
    } catch {}
  }
  if (total > 0) send('rtc:usage', { relayBytes: total });
}
