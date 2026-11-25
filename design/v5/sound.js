/* N0TRACE · sound.
   Everything here is synthesised with Web Audio: no audio files, nothing fetched.
   Sounds are tied to moments that already animate on screen:
     - an element with data-snd="<cue>" plays that cue when its CSS animation starts
     - <meta name="nt-music" content="story"> plays the soft intro music
     - <meta name="nt-chalk" content="all"> makes every .write headline sound like chalk
     - an element with data-snd-click="<cue>" plays the cue when tapped
   Nothing plays until the person has tapped or pressed a key on this page, and a small
   "sound" toggle (remembered on this device) can switch it all off. */
(function () {
  'use strict';
  if (window.NT_SND) return;
  var AC = window.AudioContext || window.webkitAudioContext;

  // ------------------------------------------------------------ engine (works on any context)
  function Engine(ctx) {
    var E = this, sr = ctx.sampleRate;
    E.ctx = ctx;
    E.master = ctx.createGain(); E.master.gain.value = 1;
    var comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -20; comp.knee.value = 18; comp.ratio.value = 3; comp.attack.value = 0.01; comp.release.value = 0.3;
    E.master.connect(comp); comp.connect(ctx.destination);
    // small warm room
    E.verb = ctx.createConvolver();
    var irLen = Math.floor(sr * 2.6), ir = ctx.createBuffer(2, irLen, sr);
    for (var c = 0; c < 2; c++) { var d = ir.getChannelData(c); for (var i = 0; i < irLen; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / irLen, 3.2); }
    E.verb.buffer = ir;
    var verbOut = ctx.createGain(); verbOut.gain.value = 0.32;
    var verbLP = ctx.createBiquadFilter(); verbLP.type = 'lowpass'; verbLP.frequency.value = 3800;
    E.verb.connect(verbLP); verbLP.connect(verbOut); verbOut.connect(E.master);
    E.sfx = ctx.createGain(); E.sfx.gain.value = 0.62; E.sfx.connect(E.master);
    E.sfxSend = ctx.createGain(); E.sfxSend.gain.value = 0.18; E.sfx.connect(E.sfxSend); E.sfxSend.connect(E.verb);
    E.music = ctx.createGain(); E.music.gain.value = 0; E.music.connect(E.master);
    E.musicSend = ctx.createGain(); E.musicSend.gain.value = 0.55; E.music.connect(E.musicSend); E.musicSend.connect(E.verb);
    // one long noise buffer, reused by every noisy sound
    var nLen = sr * 3; E.noise = ctx.createBuffer(1, nLen, sr);
    var nd = E.noise.getChannelData(0); for (var j = 0; j < nLen; j++) nd[j] = Math.random() * 2 - 1;
    // brown-ish noise for fire roar
    E.brown = ctx.createBuffer(1, nLen, sr);
    var bd = E.brown.getChannelData(0), last = 0; for (var k = 0; k < nLen; k++) { last = (last + 0.02 * (Math.random() * 2 - 1)) / 1.02; bd[k] = last * 3.5; }
    E.ksCache = {};
  }
  var P = Engine.prototype;

  P.noiseSrc = function (t, dur, buf) {
    var s = this.ctx.createBufferSource(); s.buffer = buf || this.noise; s.loop = true;
    s.start(t, Math.random() * 2.5); s.stop(t + dur + 0.05); return s;
  };
  P.filt = function (type, f, q) { var b = this.ctx.createBiquadFilter(); b.type = type; b.frequency.value = f; if (q != null) b.Q.value = q; return b; };
  P.env = function (g, t, a, peak, hold, rel) {
    g.gain.setValueAtTime(0.0001, t);
    g.gain.linearRampToValueAtTime(peak, t + a);
    g.gain.setValueAtTime(peak, t + a + hold);
    g.gain.exponentialRampToValueAtTime(0.0001, t + a + hold + rel);
  };
  P.chain = function (nodes, out) { for (var i = 0; i < nodes.length - 1; i++) nodes[i].connect(nodes[i + 1]); nodes[nodes.length - 1].connect(out || this.sfx); };

  // a short noisy grain (used by chalk, paper, crackle)
  P.grain = function (t, dur, f, q, vol, type) {
    var g = this.ctx.createGain(), s = this.noiseSrc(t, dur), b = this.filt(type || 'bandpass', f, q);
    this.env(g, t, Math.min(0.006, dur / 3), vol, dur * 0.3, dur * 0.7); this.chain([s, b, g]);
  };

  // ------------------------------------------------------------ cues
  // chalk on a board while a line writes itself on: short strokes, grainy, a little squeak now and then
  P.chalk = function (t, dur, vol) {
    vol = vol || 0.24; var end = t + Math.max(0.35, dur), x = t + 0.02;
    while (x < end - 0.05) {
      var len = 0.05 + Math.random() * 0.14, f = 2300 + Math.random() * 1700;
      var s = this.noiseSrc(x, len), b = this.filt('bandpass', f, 2.2), hp = this.filt('highpass', 900), g = this.ctx.createGain();
      // grainy amplitude: chalk catching the board
      g.gain.setValueAtTime(0.0001, x);
      var steps = Math.max(3, Math.floor(len / 0.012));
      for (var i = 1; i <= steps; i++) g.gain.linearRampToValueAtTime(vol * (0.45 + Math.random() * 0.55) * Math.sin(Math.PI * i / steps), x + len * i / steps);
      g.gain.linearRampToValueAtTime(0.0001, x + len + 0.01);
      this.chain([s, b, hp, g]);
      if (Math.random() < 0.08) { // a tiny squeak
        var o = this.ctx.createOscillator(), og = this.ctx.createGain(); o.type = 'sine';
        o.frequency.setValueAtTime(2600 + Math.random() * 900, x); o.frequency.linearRampToValueAtTime(2900 + Math.random() * 900, x + 0.05);
        this.env(og, x, 0.01, vol * 0.08, 0.02, 0.03); o.connect(og); og.connect(this.sfx); o.start(x); o.stop(x + 0.1);
      }
      x += len + 0.02 + Math.random() * 0.07;
    }
  };

  // a match struck on the box: scratch, then the flare catching
  P.match = function (t) {
    for (var i = 0; i < 9; i++) this.grain(t + i * 0.011 + Math.random() * 0.004, 0.014, 3200 + Math.random() * 2600, 1.4, 0.32);
    var s = this.noiseSrc(t + 0.09, 0.9), lp = this.filt('lowpass', 500), g = this.ctx.createGain();
    lp.frequency.setValueAtTime(400, t + 0.09); lp.frequency.exponentialRampToValueAtTime(2600, t + 0.2); lp.frequency.exponentialRampToValueAtTime(700, t + 0.9);
    this.env(g, t + 0.09, 0.06, 0.42, 0.08, 0.7); this.chain([s, lp, g]);
    var s2 = this.noiseSrc(t + 0.1, 0.5), hp = this.filt('highpass', 4500), g2 = this.ctx.createGain();
    this.env(g2, t + 0.1, 0.01, 0.1, 0.05, 0.4); this.chain([s2, hp, g2]);
  };

  // paper burning: a soft roar that rises and dies, with crackles and small pops
  P.fire = function (t, dur) {
    var s = this.noiseSrc(t, dur + 1.2, this.brown), lp = this.filt('lowpass', 700), g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.36, t + 0.8);
    g.gain.linearRampToValueAtTime(0.3, t + dur * 0.7); g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 1.1);
    this.chain([s, lp, g]);
    var hiss = this.noiseSrc(t, dur + 0.6), hb = this.filt('bandpass', 5200, 0.7), hg = this.ctx.createGain();
    hg.gain.setValueAtTime(0.0001, t); hg.gain.linearRampToValueAtTime(0.05, t + 0.6); hg.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.5);
    this.chain([hiss, hb, hg]);
    var x = t + 0.1;
    while (x < t + dur + 0.6) {
      var into = (x - t) / dur, rate = into < 0.15 ? 10 : into < 0.85 ? 26 : 9;
      this.grain(x, 0.004 + Math.random() * 0.01, 1500 + Math.random() * 4500, 1.2, 0.08 + Math.random() * 0.22);
      if (Math.random() < 0.05) this.grain(x, 0.03, 600 + Math.random() * 500, 1.5, 0.3); // a pop
      x += -Math.log(1 - Math.random()) / rate;
    }
  };

  // paper sliding into an envelope
  P.slide = function (t, dur) {
    dur = dur || 0.9; var s = this.noiseSrc(t, dur), b = this.filt('bandpass', 1800, 0.9), g = this.ctx.createGain();
    b.frequency.setValueAtTime(1200, t); b.frequency.linearRampToValueAtTime(3200, t + dur);
    g.gain.setValueAtTime(0.0001, t); g.gain.linearRampToValueAtTime(0.11, t + dur * 0.35); g.gain.linearRampToValueAtTime(0.07, t + dur * 0.8); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    this.chain([s, b, g]);
    this.grain(t + dur - 0.02, 0.05, 500, 1, 0.16, 'lowpass'); // settles at the bottom
  };

  // a sheet folding over: crinkles, then a soft crease
  P.fold = function (t, dur) {
    dur = dur || 0.8; var n = 22;
    for (var i = 0; i < n; i++) { var x = t + Math.pow(Math.random(), 1.4) * dur * 0.85; this.grain(x, 0.008 + Math.random() * 0.025, 2500 + Math.random() * 5500, 0.9, 0.05 + Math.random() * 0.1, 'highpass'); }
    var s = this.noiseSrc(t, dur), b = this.filt('bandpass', 2400, 0.6), g = this.ctx.createGain();
    this.env(g, t, dur * 0.4, 0.05, 0.05, dur * 0.5); this.chain([s, b, g]);
    this.grain(t + dur - 0.04, 0.07, 420, 0.9, 0.26, 'lowpass');
  };

  // wax seal pressed: a low soft thump and a small squish
  P.wax = function (t) {
    var o = this.ctx.createOscillator(), g = this.ctx.createGain(); o.type = 'sine';
    o.frequency.setValueAtTime(120, t); o.frequency.exponentialRampToValueAtTime(48, t + 0.22);
    this.env(g, t, 0.006, 0.38, 0.02, 0.3); o.connect(g); g.connect(this.sfx); o.start(t); o.stop(t + 0.4);
    this.grain(t + 0.01, 0.12, 700, 0.8, 0.14, 'lowpass');
    this.grain(t + 0.02, 0.05, 2600, 1, 0.04);
    this.pluck(t + 0.32, 74, 0.09, this.sfx, 0.55); this.pluck(t + 0.5, 81, 0.06, this.sfx, 0.65); // a small closing note
  };

  // a push pin into cork, with a short tape tear
  P.pin = function (t) {
    this.grain(t, 0.12, 2600, 0.7, 0.07, 'bandpass'); // tape
    var o = this.ctx.createOscillator(), g = this.ctx.createGain(); o.type = 'triangle';
    o.frequency.setValueAtTime(420, t + 0.13); o.frequency.exponentialRampToValueAtTime(160, t + 0.18);
    this.env(g, t + 0.13, 0.002, 0.3, 0.005, 0.08); o.connect(g); g.connect(this.sfx); o.start(t + 0.13); o.stop(t + 0.3);
    this.grain(t + 0.13, 0.02, 1800, 1.2, 0.22);
  };

  // tape pulled off the roll: the sticky crackle speeds up, then the strip tears free
  P.rip = function (t, dur) {
    dur = dur || 0.5; var x = t;
    while (x < t + dur) {
      var k = (x - t) / dur, rate = 70 + k * 260;
      this.grain(x, 0.003 + Math.random() * 0.006, 1400 + Math.random() * 4600, 1.1, (0.07 + Math.random() * 0.13) * (0.5 + k * 0.7));
      x += -Math.log(1 - Math.random()) / rate;
    }
    var s = this.noiseSrc(t, dur), b = this.filt('bandpass', 1500, 1.2), g = this.ctx.createGain();
    b.frequency.setValueAtTime(1300, t); b.frequency.exponentialRampToValueAtTime(3800, t + dur);
    g.gain.setValueAtTime(0.0001, t);
    for (var i = 1; i <= 16; i++) g.gain.linearRampToValueAtTime((0.025 + 0.06 * i / 16) * (0.6 + Math.random() * 0.4), t + dur * i / 16);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.03); this.chain([s, b, g]);
    this.grain(t + dur, 0.025, 3200, 0.9, 0.22); // the tear
  };
  // tape pressed down onto paper
  P.tapepress = function (t) {
    this.grain(t, 0.05, 320, 0.8, 0.32, 'lowpass');
    for (var i = 0; i < 5; i++) this.grain(t + 0.02 + i * 0.018, 0.012, 2500 + Math.random() * 2500, 1, 0.04, 'highpass');
  };

  // the red "heard" stamp
  P.stamp = function (t) {
    var o = this.ctx.createOscillator(), g = this.ctx.createGain(); o.type = 'sine';
    o.frequency.setValueAtTime(160, t); o.frequency.exponentialRampToValueAtTime(60, t + 0.12);
    this.env(g, t, 0.003, 0.28, 0.01, 0.16); o.connect(g); g.connect(this.sfx); o.start(t); o.stop(t + 0.3);
    this.grain(t, 0.04, 1400, 0.8, 0.18);
  };

  // tape falling away / a scrap drifting
  P.flutter = function (t, dur) {
    dur = dur || 0.7; var s = this.noiseSrc(t, dur), b = this.filt('bandpass', 2000, 0.8), g = this.ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    for (var i = 0; i < 9; i++) g.gain.linearRampToValueAtTime((i % 2 ? 0.015 : 0.05) * (1 - i / 10), t + dur * (i + 1) / 10);
    g.gain.linearRampToValueAtTime(0.0001, t + dur); this.chain([s, b, g]);
  };

  // ------------------------------------------------------------ plucked strings (Karplus-Strong)
  P.ks = function (midi, bright) {
    var key = midi + ':' + (bright || 0); if (this.ksCache[key]) return this.ksCache[key];
    var sr = this.ctx.sampleRate, f = 440 * Math.pow(2, (midi - 69) / 12), N = Math.max(2, Math.round(sr / f));
    var len = Math.floor(sr * (midi < 52 ? 3.4 : 2.6)), buf = this.ctx.createBuffer(1, len, sr), out = buf.getChannelData(0);
    var dl = new Float32Array(N), prev = 0, b = bright || 0.5;
    for (var i = 0; i < N; i++) { var r = Math.random() * 2 - 1; prev = prev + b * (r - prev); dl[i] = prev; } // softened pick
    var damp = midi < 52 ? 0.9985 : 0.9972, idx = 0;
    for (var n = 0; n < len; n++) { var y = dl[idx], nx = dl[(idx + 1) % N]; out[n] = y; dl[idx] = (y + nx) * 0.5 * damp; idx = (idx + 1) % N; }
    for (var m = 0; m < 400; m++) out[len - 1 - m] *= m / 400;
    this.ksCache[key] = buf; return buf;
  };
  P.pluck = function (t, midi, vol, out, bright) {
    var s = this.ctx.createBufferSource(); s.buffer = this.ks(midi, bright);
    var lp = this.filt('lowpass', 2600 + (midi - 50) * 20, 0.5), body = this.filt('peaking', 210, 1.1); body.gain.value = 3;
    var g = this.ctx.createGain(); g.gain.value = vol;
    s.connect(body); body.connect(lp); lp.connect(g); g.connect(out || this.sfx); s.start(t);
  };
  // a soft strum, for "you were heard tonight"
  P.strum = function (t) {
    var notes = [50, 57, 62, 64, 66, 69];
    for (var i = 0; i < notes.length; i++) this.pluck(t + i * 0.045, notes[i], 0.14 - i * 0.012, this.sfx, 0.45);
    this.pluck(t + 1.6, 74, 0.06, this.sfx, 0.6);
  };

  // ------------------------------------------------------------ the intro music
  // Slow fingerpicked guitar in D, a quiet pad underneath, a few bell notes on top.
  // Room-mic warmth, nothing loud. Think 2am, a window, someone still awake.
  var CH = [
    { b: 50, t: [57, 64, 66], pad: [62, 66, 69] },   // Dadd9
    { b: 49, t: [57, 64, 69], pad: [61, 64, 69] },   // A/C#
    { b: 47, t: [54, 62, 69], pad: [59, 62, 66] },   // Bm7
    { b: 43, t: [55, 62, 66], pad: [59, 62, 67] }    // Gmaj7
  ];
  var PAT = [[0, 'b'], [2, 1], [3, 2], [4, 1], [5, 0], [6, 1], [7, 2], [7.5, 1]];
  var MEL = [null, [0, 81], [3, 78], [5, 76], null, [1, 74], [4, 76], [6, 73], null, [0, 78], [4, 81], null, null, [2, 76], [5, 74], null];
  P.startMusic = function (t0, mode) {
    if (this.playing) return; this.playing = true; this.mode = mode || 'story'; var wait = this.mode === 'wait';
    var E = this, ctx = this.ctx, eighth = 60 / 72 / 2, bar = eighth * 8;
    E.music.gain.cancelScheduledValues(t0); E.music.gain.setValueAtTime(0.0001, t0); E.music.gain.linearRampToValueAtTime(wait ? 0.4 : 0.5, t0 + 5);
    var hiss = ctx.createBufferSource(); hiss.buffer = E.noise; hiss.loop = true;
    var hl = E.filt('lowpass', 2400), hg = ctx.createGain(); hg.gain.value = 0.006; hiss.connect(hl); hl.connect(hg); hg.connect(E.music); hiss.start(t0);
    E.hiss = hiss;
    var barN = 0, next = t0 + 0.3;
    function scheduleBar(bt, n) {
      var c = CH[Math.floor(n / 2) % CH.length], second = n % 2 === 1;
      for (var i = 0; i < PAT.length; i++) {
        if (wait && (i === 1 || i === 3 || i === 7)) continue; // sparser while waiting
        var p = PAT[i], note = p[1] === 'b' ? c.b : c.t[p[1]];
        if (second && i === 0) note = c.b + 12;
        if (second && i === 7) continue;
        var hum = (Math.random() - 0.5) * 0.02, vel = (p[1] === 'b' ? 0.17 : 0.1) * (0.8 + Math.random() * 0.35);
        E.pluck(bt + p[0] * eighth + hum, note, vel, E.music, p[1] === 'b' ? 0.35 : 0.5);
      }
      if (!second) { // pad swells under each chord
        for (var k = 0; k < c.pad.length; k++) {
          var o = ctx.createOscillator(), o2 = ctx.createOscillator(), g = ctx.createGain(), lp = E.filt('lowpass', 750, 0.3);
          var fz = 440 * Math.pow(2, (c.pad[k] - 69) / 12); o.type = 'triangle'; o2.type = 'sine';
          o.frequency.value = fz; o2.frequency.value = fz * 1.004;
          g.gain.setValueAtTime(0.0001, bt); g.gain.linearRampToValueAtTime(0.016, bt + bar * 0.9); g.gain.linearRampToValueAtTime(0.012, bt + bar * 1.7); g.gain.exponentialRampToValueAtTime(0.0001, bt + bar * 2.4);
          o.connect(lp); o2.connect(lp); lp.connect(g); g.connect(E.music); o.start(bt); o2.start(bt); o.stop(bt + bar * 2.5); o2.stop(bt + bar * 2.5);
        }
      }
      var m = MEL[n % MEL.length]; if (m && n >= 4 && !wait) E.pluck(bt + m[0] * eighth, m[1], 0.05, E.music, 0.75);
    }
    E.musicTick = function (now) {
      while (next < now + 1.5) { scheduleBar(next, barN); barN++; next += bar; }
    };
    E.musicTick(t0);
  };
  P.stopMusic = function (t) {
    if (!this.playing) return; this.playing = false; this.musicTick = null;
    this.music.gain.cancelScheduledValues(t); this.music.gain.setValueAtTime(this.music.gain.value, t); this.music.gain.linearRampToValueAtTime(0.0001, t + 1.5);
    if (this.hiss) this.hiss.stop(t + 1.6);
  };

  // ------------------------------------------------------------ live page wiring
  // Each board that has sound carries a hidden <i class="nt-cfg"> in its own content:
  //   data-music="story|wait"  music for the story and the waiting screens, nowhere else
  //   data-chalk="all"         every handwritten headline writes on with chalk
  //   data-pos / data-kind     where the sound switch sits and how it's worded
  //   data-replay="1"          an ending moment: if it played before the first tap, replay it with sound
  // The marker travels with the board, so when you move to a screen without music, the music fades out.
  var S = window.NT_SND = { Engine: Engine, debug: false, log: [] };
  function storeGet() { try { return localStorage.getItem('nt-sound'); } catch (e) { return null; } }
  function storeSet(v) { try { localStorage.setItem('nt-sound', v); } catch (e) {} }
  S.muted = storeGet() === 'off';
  S.armed = false; S.eng = null;
  function note(cue, extra) { S.log.push({ cue: cue, at: +(performance.now() / 1000).toFixed(2), extra: extra || '' }); if (S.debug) console.log('[nt-snd]', cue, extra || ''); }

  function ensure() {
    if (S.eng || !AC) return S.eng;
    try { S.eng = new Engine(new AC()); } catch (e) { S.eng = null; }
    return S.eng;
  }
  function live() { return S.armed && S.eng && S.eng.ctx.state === 'running'; }
  function ready() { return !S.muted && live(); }
  function now() { return S.eng.ctx.currentTime + 0.02; }
  function dur(el) {
    var cs = getComputedStyle(el), d = (cs.animationDuration || '1s').split(',')[0].trim();
    return d.indexOf('ms') > 0 ? parseFloat(d) / 1000 : parseFloat(d) || 1;
  }

  var CUES = {
    chalk: function (el) { var d = dur(el), len = (el.textContent || '').trim().length; S.eng.chalk(now(), Math.min(d * 0.92, 0.25 + len * 0.07), len > 30 ? 0.19 : 0.24); },
    burn: function (el) { var d = dur(el); S.eng.match(now()); S.eng.fire(now() + 0.25, Math.max(2, d - 0.6)); },
    slide: function (el) { S.eng.slide(now(), Math.min(1.2, dur(el) * 0.8)); },
    fold: function (el) { S.eng.fold(now(), dur(el)); },
    wax: function () { S.eng.wax(now()); },
    pin: function () { S.eng.pin(now()); },
    rip: function () { S.eng.rip(now() + 0.24, 0.5); },
    tapepress: function () { S.eng.tapepress(now()); },
    stamp: function () { S.eng.stamp(now()); },
    flutter: function (el) { S.eng.flutter(now(), Math.min(1, dur(el))); },
    unfold: function (el) { S.eng.fold(now(), Math.min(1, dur(el))); },
    strum: function () { S.eng.strum(now()); },
    heardchord: function (el) { S.eng.strum(now()); var d = dur(el); S.eng.chalk(now() + 0.15, Math.min(d * 0.9, 1.6), 0.17); },
    pluck: function (el) {
      var notes = [62, 66, 69, 74, 71], i = parseInt(el.getAttribute('data-snd-i') || '0', 10);
      var d = dur(el), at = parseFloat(el.getAttribute('data-snd-at') || '0.09');
      S.eng.pluck(now() + d * at, notes[i % notes.length], S.eng.playing ? 0.07 : 0.13, S.eng.sfx, 0.4);
    }
  };

  // ---- which board are we on
  var cur = null, cfgEl = null, pageStart = performance.now(), missed = 0, seen = new WeakMap(), chalkAll = false;
  function readCfg() {
    var els = document.querySelectorAll('.nt-cfg'), el = els.length ? els[els.length - 1] : null;
    if (el !== cfgEl) { // a new board came in
      cfgEl = el; pageStart = performance.now(); missed = 0; seen = new WeakMap();
      cur = el ? { music: el.getAttribute('data-music'), chalk: el.getAttribute('data-chalk'), pos: el.getAttribute('data-pos'),
                   kind: el.getAttribute('data-kind'), replay: el.getAttribute('data-replay') === '1' } : null;
      chalkAll = !!(cur && cur.chalk === 'all');
      placeToggle();
    }
    return cur;
  }

  function fire(el, cue, why) {
    if (!CUES[cue]) return;
    if (!ready()) { if (!S.muted) missed++; return; }
    note(cue, why);
    try { CUES[cue](el); } catch (e) { if (S.debug) console.log(e); }
  }
  function onAnim(e) {
    var el = e.target; if (!el || !el.getAttribute) return;
    readCfg();
    var cue = el.getAttribute('data-snd');
    if (!cue && chalkAll && el.classList && el.classList.contains('write')) cue = 'chalk';
    if (!cue) return;
    var only = el.getAttribute('data-snd-anim'); if (only && only !== e.animationName) return;
    if (!only && (cue === 'chalk' || cue === 'heardchord') && e.animationName !== 'write') return;
    if (e.type === 'animationstart') { var k = seen.get(el) || {}; if (k[e.animationName]) return; k[e.animationName] = 1; seen.set(el, k); }
    if (e.type === 'animationiteration' && cue !== 'pluck') return;
    fire(el, cue, e.animationName);
  }
  document.addEventListener('animationstart', onAnim, true);
  document.addEventListener('animationiteration', onAnim, true);
  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('[data-snd-click]') : null;
    if (el) { arm(); setTimeout(function () { fire(el, el.getAttribute('data-snd-click'), 'click'); }, 30); }
  }, true);

  // ---- music follows the board: on for the story and the waiting screens, off everywhere else
  function syncMusic() {
    if (!S.eng) return;
    var want = cur && cur.music && !S.muted && live() ? cur.music : null;
    if (want && (!S.eng.playing || S.eng.mode !== want)) {
      if (S.eng.playing) S.eng.stopMusic(S.eng.ctx.currentTime);
      var t = S.eng.ctx.currentTime + (S.eng.playing ? 1.6 : 0.05);
      setTimeout(function () { if (S.eng && !S.eng.playing && cur && cur.music === want && ready()) { S.eng.startMusic(S.eng.ctx.currentTime + 0.05, want); note('music', want); } }, S.eng.playing ? 1700 : 0);
    } else if (!want && S.eng.playing) {
      S.eng.stopMusic(S.eng.ctx.currentTime); note('music-off');
    }
  }

  // ---- an ending that happened before the first tap gets replayed, with its sound
  function replay() {
    seen = new WeakMap(); missed = 0;
    var root = cfgEl && cfgEl.parentElement; if (!root) return;
    // restart every CSS animation on this board: switch them off, let the browser notice, put them back
    var all = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*'))), saved = [];
    all.forEach(function (el) { if (el === tog || !el.style) return; saved.push([el, el.getAttribute('style')]); el.style.setProperty('animation', 'none', 'important'); });
    void root.offsetWidth;
    saved.forEach(function (x) { if (x[1] === null) x[0].removeAttribute('style'); else x[0].setAttribute('style', x[1]); });
    note('replay');
  }

  function arm() {
    if (S.muted) return;
    if (!ensure()) return;
    var first = !S.armed; S.armed = true;
    var p = S.eng.ctx.state === 'running' ? null : S.eng.ctx.resume();
    var go = function () {
      paint(); syncMusic();
      if (first && cur && cur.replay && missed > 0 && performance.now() - pageStart < 30000) replay();
    };
    if (p && p.then) p.then(go); else go();
  }
  ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) { window.addEventListener(ev, function (e) { if (tog && tog.contains(e.target)) return; arm(); }, { capture: true, passive: true }); });
  setInterval(function () {
    readCfg(); paint(); syncMusic();
    if (S.eng && S.eng.musicTick && S.eng.ctx.state === 'running') S.eng.musicTick(S.eng.ctx.currentTime);
  }, 250);
  document.addEventListener('visibilitychange', function () {
    if (!S.eng) return;
    if (document.hidden) S.eng.ctx.suspend(); else if (S.armed && !S.muted) S.eng.ctx.resume();
  });

  // ---- the sound switch
  var tog = null;
  var SPK = '<svg width="15" height="13" viewBox="0 0 15 13" aria-hidden="true" style="flex-shrink:0"><path d="M1.5 4.5h2.6L7.6 1.6v9.8L4.1 8.5H1.5z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>' +
            '<path class="w1" d="M9.8 4.3c.9.9.9 3.5 0 4.4" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path class="w2" d="M11.6 2.6c1.9 1.9 1.9 5.9 0 7.8" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>' +
            '<path class="x" d="M10 4.4l3.6 4.2M13.6 4.4L10 8.6" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>';
  function isPhone() {
    var r = cfgEl && cfgEl.parentElement, w = r ? r.offsetWidth : 0;
    if (!w) { var x = document.querySelector('x-dc > div'); w = x ? x.offsetWidth : 0; }
    if (!w) w = window.innerWidth;
    return w < 600;
  }
  var lastCls = '';
  function placeToggle() {
    if (!document.body) return;
    if (!tog) build();
    if (!tog) return;
    tog.style.display = cur ? 'flex' : 'none';
    paint();
  }
  function paint() {
    if (!tog || !cur) return;
    // where the switch sits depends on the board's real width, which is only known once it has rendered
    S.phone = isPhone();
    var pos = cur.pos || (S.phone ? 'foot' : 'desk');
    var cls = 'nt-snd p-' + pos + (cur.kind === 'wait' ? ' k-wait' : '');
    if (cls !== lastCls) { lastCls = cls; tog.className = cls; }
    var on = live() && !S.muted, wait = cur.kind === 'wait', ph = S.phone, label;
    // one switch, two words: it says what you'll hear, and one tap flips it
    if (!S.muted && !on && cur.replay && missed > 0) label = ph ? 'hear it' : 'replay with sound';
    else label = (wait ? 'music ' : 'sound ') + (S.muted ? 'off' : 'on');
    tog.setAttribute('aria-label', S.muted ? 'Turn sound on' : 'Mute sound');
    tog.title = S.muted ? 'Turn sound on (M)' : 'Mute (M)';
    var sp = tog.querySelector('span'); if (sp.textContent !== label) sp.textContent = label;
    tog.setAttribute('aria-pressed', on ? 'true' : 'false');
    tog.classList.toggle('off', S.muted); tog.classList.toggle('wait', !S.muted && !on);
    lastCls = tog.className;
  }
  function build() {
    if (tog || !document.body) return;
    var st = document.createElement('style');
    st.textContent = '.nt-snd{position:fixed;z-index:90;display:flex;align-items:center;gap:8px;padding:7px 13px 7px 11px;border:1px solid rgba(233,233,231,.18);background:rgba(13,13,14,.72);color:#B9B9B6;' +
      'font-family:"Courier Prime",monospace;font-weight:700;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;cursor:pointer;border-radius:999px;transition:color .25s,border-color .25s}' +
      '.nt-snd:hover,.nt-snd:focus-visible{border-color:rgba(233,233,231,.45)}.nt-snd.off{color:#7E7E83}' +
      '.nt-snd:hover,.nt-snd:focus-visible{color:#E9E9E7;outline:none}.nt-snd .x{display:none}.nt-snd.off .x{display:block}.nt-snd.off .w1,.nt-snd.off .w2{display:none}' +
      '.nt-snd.wait{color:#C9C9C6}.nt-snd.wait .w1,.nt-snd.wait .w2{animation:ntw 2.4s ease-in-out infinite}.nt-snd.wait .w2{animation-delay:.3s}' +
      '@keyframes ntw{0%,100%{opacity:.25}50%{opacity:1}}' +
      '.nt-snd.p-desk{right:48px;bottom:76px}' +
      '.nt-snd.p-dtop{right:48px;top:96px}' +
      '.nt-snd.p-foot{left:170px;bottom:11px;font-size:8.5px;letter-spacing:.1em;padding:5px 10px 5px 8px;gap:6px}' +
      '.nt-snd.p-br{right:12px;bottom:96px;font-size:8.5px;letter-spacing:.12em;padding:6px 11px 6px 9px;gap:6px}' +
      '.nt-snd.k-wait{color:#C9C9C6}';
    document.head.appendChild(st);
    tog = document.createElement('button'); tog.type = 'button'; tog.className = 'nt-snd'; tog.style.display = 'none';
    tog.setAttribute('aria-label', 'Sound'); tog.innerHTML = SPK + '<span></span>';
    tog.addEventListener('click', function (e) {
      e.stopPropagation();
      if (S.muted || (cur && cur.replay && missed > 0 && !live())) unmute(); else mute();
    });
    document.body.appendChild(tog);
  }
  function unmute() {
    S.muted = false; storeSet('on');
    if (S.eng) { var g = S.eng.master.gain; g.cancelScheduledValues(S.eng.ctx.currentTime); g.setValueAtTime(1, S.eng.ctx.currentTime); }
    arm(); paint();
  }
  function mute() {
    S.muted = true; storeSet('off');
    if (S.eng) { S.eng.stopMusic(S.eng.ctx.currentTime); S.eng.master.gain.setTargetAtTime(0, S.eng.ctx.currentTime, 0.15); }
    paint();
  }
  // M mutes and unmutes, unless you're typing
  window.addEventListener('keydown', function (e) {
    if (!cur || e.metaKey || e.ctrlKey || e.altKey || (e.key !== 'm' && e.key !== 'M')) return;
    var t = e.target; if (t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName))) return;
    if (S.muted) unmute(); else mute();
  }, true);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { readCfg(); placeToggle(); });
  else { readCfg(); placeToggle(); }
})();
