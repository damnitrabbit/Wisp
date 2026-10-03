"""N0TRACE V5 — E04 An echo (desktop): listen, Heard, reply. Also holds helpers reused by v5m_burnecho.py."""
from gen5 import *
import json, os

ECHO_CSS = f"""
.stamp{{position:absolute;{MARK};color:{RED};border:3px solid {RED};border-radius:6px;padding:2px 12px 0;font-size:30px;letter-spacing:.06em;transform:rotate(-12deg);
mix-blend-mode:multiply;opacity:.85;-webkit-mask-image:{NOISE_LIGHT};mask-image:{NOISE_LIGHT};animation:stamp .55s cubic-bezier(.2,1.6,.4,1) var(--sw,1.2s) both;pointer-events:none;z-index:6}}
@keyframes stamp{{0%{{opacity:0;transform:rotate(-12deg) scale(1.9)}}60%{{opacity:.9;transform:rotate(-12deg) scale(.94)}}100%{{opacity:.85;transform:rotate(-12deg) scale(1)}}}}
.thud{{animation:thud .5s ease var(--tw,1.5s) both}}
@keyframes thud{{0%,100%{{transform:none}}30%{{transform:translateY(2px) rotate(.2deg)}}}}
.heard{{display:inline-flex;align-items:center;gap:8px;{MARK};color:{RED};transition:transform .2s}}
.heard:hover{{transform:scale(1.06) rotate(-2deg)}}
.note{{transition:transform .5s cubic-bezier(.2,.7,.2,1)}}
.note:hover{{transform:translateY(-4px) rotate(0deg) !important;z-index:20}}
.drop{{animation:drop .9s cubic-bezier(.3,1.4,.5,1) both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-70px) rotate(-10deg) scale(1.08)}}to{{opacity:1}}}}
.slap{{display:block;animation:slap .35s cubic-bezier(.2,1.6,.4,1) both}}
@keyframes slap{{from{{opacity:0;transform:scale(1.6) translateY(-12px)}}to{{opacity:1;transform:none}}}}
.played{{position:absolute;left:0;top:0;bottom:0;overflow:hidden}}
.playing .played.main{{animation:prog 29s linear forwards}}
@keyframes prog{{to{{width:100%}}}}
.playing .phead{{animation:phead 29s linear forwards}}
@keyframes phead{{to{{left:100%}}}}
.ppau{{display:none}}.playing .ppau{{display:inline}}.playing .ptri{{display:none}}
.pbtn{{transition:transform .2s}}
.pbtn:hover{{transform:scale(1.06) rotate(-3deg)}}
.slip{{transition:transform .4s cubic-bezier(.2,.7,.2,1)}}
.slip:hover{{transform:translateY(-3px) rotate(0deg) !important}}
"""

# ---------- hand-drawn waveform ----------
def _bars(w, h, seed, step=5):
    r = random.Random(seed)
    out, mid = [], h / 2
    ph = r.uniform(0, 6)
    for x in range(3, w - 2, step):
        t = x / w
        env = (.35 + .65 * abs(math.sin(t * math.pi * 3.1 + ph))) * (.62 + .38 * math.sin(t * 19 + ph))
        if r.random() < .07:
            env *= .22
        a = max(.09, min(1, env * r.uniform(.55, 1.08))) * (mid - 3)
        out.append(f'M{x + r.uniform(-.6, .6):.1f} {mid - a + r.uniform(-1, 1):.1f}L{x + r.uniform(-.9, .9):.1f} {mid + a * r.uniform(.8, 1.1):.1f}')
    return ''.join(out)

def _wsvg(w, h, d, color, sw, uid, op=1):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<defs>{ROUGH.format(i=uid, s=5, sc=2.2)}</defs><g filter="url(#rough{uid})" opacity="{op}">'
            f'<path d="M0 {h / 2:.1f} L{w} {h / 2 + .8:.1f}" stroke="{color}" stroke-width=".9" opacity=".35"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/></g></svg>')

def wave(w, h, seed, uid, frac=.4, main=False, sw=2.2, head=True):
    """Waveform drawn by hand: pencil for what's left, ink for what's played, a red-ink playhead."""
    d = _bars(w, h, seed, step=5 if w > 200 else 4)
    ph = (f'<span class="phead" aria-hidden="true" style="position:absolute;left:{frac * 100:.0f}%;top:-6px;bottom:-6px;width:2px;margin-left:-1px;background:{RED};border-radius:2px;transform:rotate(2deg)"></span>') if head else ''
    return (f'<div style="position:relative;width:{w}px;height:{h}px">{_wsvg(w, h, d, PENCIL, sw, uid + "a", .45)}'
            f'<div class="played{" main" if main else ""}" style="width:{frac * 100:.0f}%">{_wsvg(w, h, d, INK, sw, uid + "b")}</div>{ph}</div>')

def play_btn(size=56, uid='pb', interactive=False):
    c, rr = size / 2, size / 2 - 3
    circ = (f'M{c + rr * .15:.1f} {c - rr:.1f} C{c + rr * 1.08:.1f} {c - rr * 1.02:.1f} {c + rr * 1.06:.1f} {c + rr * .96:.1f} {c:.1f} {c + rr:.1f} '
            f'C{c - rr * 1.02:.1f} {c + rr * 1.04:.1f} {c - rr * 1.07:.1f} {c - rr * .88:.1f} {c - rr * .02:.1f} {c - rr * 1.05:.1f} L{c + rr * .3:.1f} {c - rr * .96:.1f}')
    tri = f'<path d="M{c - size * .1:.1f} {c - size * .16:.1f} L{c + size * .18:.1f} {c + 1:.1f} L{c - size * .1:.1f} {c + size * .17:.1f} Z" fill="{INK}" stroke="{INK}" stroke-width="1.5" stroke-linejoin="round"/>'
    pau = (f'<path d="M{c - size * .1:.1f} {c - size * .15:.1f} L{c - size * .1:.1f} {c + size * .15:.1f} M{c + size * .1:.1f} {c - size * .15:.1f} L{c + size * .1:.1f} {c + size * .15:.1f}" '
           f'stroke="{INK}" stroke-width="{max(3, size * .08):.1f}" stroke-linecap="round"/>')
    if interactive:
        glyph = f'<g class="ptri">{tri}</g><g class="ppau">{pau}</g>'
    else:
        glyph = tri
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<defs>{ROUGH.format(i=uid, s=3, sc=2.5)}</defs><g filter="url(#rough{uid})">'
            f'<path d="{circ}" fill="rgba(255,252,242,.35)" stroke="{INK}" stroke-width="2.2" stroke-linecap="round"/>{glyph}</g></svg>')

def heart(color=RED, size=18, fill='none'):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 20 20" aria-hidden="true"><path d="M10 17 C3 12 1 8 3 5 C5 2 9 3 10 6 C11 3 15 2 17 5 C19 8 17 12 10 17 Z" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/></svg>')

def mic(size=16, color=INK):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 20 20" aria-hidden="true"><rect x="7" y="2" width="6" height="11" rx="3" fill="none" stroke="{color}" stroke-width="1.8"/>'
            f'<path d="M4 10 C4 15 16 15 16 10 M10 15 V18" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/></svg>')

def toggle(size=12, gap=22):
    return f'''<div style="display:flex;gap:{gap}px;align-items:center;{TYPE};font-size:{size}px;letter-spacing:.18em">
<button type="button" onClick="{{{{toWrite}}}}" style="color:{{{{writeColor}}}};position:relative;padding-bottom:6px">WRITE<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{{{{writeLine}}}}"></span></button>
<span style="color:{PENCIL};opacity:.5">/</span>
<button type="button" onClick="{{{{toSpeak}}}}" style="color:{{{{speakColor}}}};position:relative;padding-bottom:6px">SPEAK<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{{{{speakLine}}}}"></span></button></div>'''


def kind_pick(sel='echo', fs=11, gap=18, cap=True):
    """What you're leaving: AN ECHO (open to replies) or AN UNSENT LETTER (to someone, replies off).
    Two small kraft labels on the board; the chosen one sits forward, the other waits faded."""
    def lab(key, text, sub, seed, rot):
        on = key == sel
        w = int(len(text) * fs * .78 + fs * 2.6)
        h = int(fs * 2.7)
        strip = (f'<span style="position:relative;display:inline-flex;align-items:center;justify-content:center;width:{w}px;height:{h}px;transform:rotate({rot}deg)" class="{"lift" if on else ""}">'
                 f'<span class="paper kraft" style="position:absolute;inset:0;clip-path:{deckle(w, h, amp=1.3, step=10, seed=seed)}"></span>'
                 f'<span style="position:relative;{TYPE};font-weight:700;font-size:{fs}px;letter-spacing:.16em;color:{INK}">{text}</span></span>')
        tick = (f'<svg width="{w}" height="8" viewBox="0 0 {w} 8" aria-hidden="true" style="display:block;margin-top:5px;overflow:visible"><path d="M3 4 Q{w * .3:.0f} 7 {w * .55:.0f} 3 T{w - 3} 4" fill="none" stroke="{RED}" stroke-width="2" stroke-linecap="round"/></svg>') if on else '<span style="display:block;height:13px"></span>'
        sb = f'<span style="display:block;{TYPE};font-size:{max(9, fs - 2)}px;letter-spacing:.12em;color:{BOARDTXT};margin-top:4px;white-space:nowrap">{sub}</span>' if cap else ''
        return (f'<button type="button" aria-pressed="{"true" if on else "false"}" style="display:flex;flex-direction:column;align-items:flex-start;text-align:left;opacity:{1 if on else .5}">'
                f'{strip}{tick}{sb}</button>')
    return (f'<div role="group" aria-label="What are you leaving?" style="display:flex;align-items:flex-start;gap:{gap}px">'
            f'{lab("echo", "AN ECHO", "OPEN TO REPLIES", 731, -1.5)}{lab("unsent", "AN UNSENT LETTER", "TO SOMEONE · NO REPLIES", 732, 1)}</div>')

THREAD_SCRIPT = """constructor(props) { super(props); this.state = { playing: null, heard: null, mode: null }; }
renderVals() {
const playing = this.state.playing ?? this.props.playing ?? false;
const heard = this.state.heard ?? this.props.heard ?? true;
const mode = this.state.mode ?? this.props.mode ?? 'write';
const on = '%s', off = '%s';
return {
rootClass: playing ? 'playing' : '',
isPlaying: playing, notPlaying: !playing, playLabel: playing ? 'Pause' : 'Play',
togglePlay: () => this.setState({ playing: !playing }),
isHeard: heard, notHeard: !heard, heardCount: heard ? 13 : 12, heartFill: heard ? '#B8352A' : 'none',
heardHint: heard ? 'they will know it reached someone' : 'tap once you have listened',
tapHeard: () => this.setState({ heard: !heard }),
writeMode: mode === 'write', speakMode: mode === 'speak',
writeColor: mode === 'write' ? on : off, speakColor: mode === 'speak' ? on : off,
writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,
toWrite: () => this.setState({ mode: 'write' }), toSpeak: () => this.setState({ mode: 'speak' }),
isVoice: true, isText: false, modeLabel: 'VOICE', fadesShort: '14H', timeTitle: 'left here at 1:12 am', cardH: 336, mcardH: 362,
noteText: '', repliesTitle: '3 replies', sendReply: () => {}
};
}""" % (INK, PENCIL)
THREAD_PROPS = '"heard":{"editor":"boolean","default":true},"playing":{"editor":"boolean","default":false},"mode":{"editor":"enum","options":["write","speak"],"default":"write"}'

REPLIES = [  # (name, when, kind, content, paper kind, seed)
    ('quiet_otter', '1h ago', 'text', "I heard every word. You're not as alone in this as it feels right now.", 'hi', 511),
    ('moss_byte', '52m ago', 'voice', '0:21', '', 512),
    ('paper_kite', '18m ago', 'text', "Same thing happened to me last spring. It does get quieter. Sending you something warm.", 'kraft', 513),
]

def heard_btn(size=24):
    return (f'<button type="button" class="heard" onClick="{{{{tapHeard}}}}" aria-pressed="{{{{isHeard}}}}" style="font-size:{size}px">'
            f'<svg width="{size - 2}" height="{size - 2}" viewBox="0 0 20 20" aria-hidden="true"><path d="M10 17 C3 12 1 8 3 5 C5 2 9 3 10 6 C11 3 15 2 17 5 C19 8 17 12 10 17 Z" '
            f'fill="{{{{heartFill}}}}" stroke="{RED}" stroke-width="1.8" stroke-linejoin="round"/></svg>heard · {{{{heardCount}}}}</button>')

def stamp(right, top, size=30, wait='1.2s'):
    return (f'<sc-if value="{{{{isHeard}}}}" hint-placeholder-val="{{{{ true }}}}">'
            f'<span class="stamp" style="right:{right}px;top:{top}px;font-size:{size}px;--sw:{wait}">HEARD</span></sc-if>')

def write_manifest(entries, group='leave1'):
    order = ['V5MBurn', 'V5MBurnVoice', 'V5MBurnMid', 'V5MBurnGone', 'V5MEchoes', 'V5MEchoWrite', 'V5MEchoPinned', 'V5MEchoThread', 'V5EchoThread']
    path = f'manifest_{group}.json'
    cur = json.load(open(path)) if os.path.exists(path) else []
    byf = {e['file']: e for e in cur}
    for e in entries:
        byf[e['file']] = e
    out = sorted(byf.values(), key=lambda e: order.index(e['file'].split('.')[0]) if e['file'].split('.')[0] in order else 99)
    json.dump(out, open(path, 'w'), indent=1)


# =====================================================================
# Echo vs unsent letter: the shared vocabulary (write boards, wall, letter paper)
# =====================================================================
LETTER_TXT = "I'm sorry I didn't pick up. I didn't know it was the last time you'd call."
ECHO_TXT = 'I keep rehearsing conversations that will never happen.'

def ico_note(color=INK, s=18):
    """An echo: a little note with a strip of tape."""
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 20 20" aria-hidden="true" style="display:block;flex-shrink:0;overflow:visible">'
            f'<path d="M3 5.5 L17 4.8 L17.4 17.2 L3.3 17.6 Z" fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M7 3 L13.2 2.6 L13.4 6.2 L7.2 6.6 Z" fill="{color}" opacity=".45"/>'
            f'<path d="M6 10.5 H14 M6 13.6 H11.5" stroke="{color}" stroke-width="1.3" stroke-linecap="round"/></svg>')

def ico_letter(color=INK, s=18):
    """An unsent letter: a page with a folded corner and a few written lines."""
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 20 20" aria-hidden="true" style="display:block;flex-shrink:0;overflow:visible">'
            f'<path d="M3.5 2.6 L12.6 2.4 L16.6 6.4 L16.8 17.6 L3.6 17.8 Z" fill="none" stroke="{color}" stroke-width="1.6" stroke-linejoin="round"/>'
            f'<path d="M12.6 2.4 L12.5 6.5 L16.6 6.4" fill="none" stroke="{color}" stroke-width="1.3" stroke-linejoin="round"/>'
            f'<path d="M6 9.6 Q8 8.4 10 9.4 M6 12.4 H13.6 M6 15.1 H12" stroke="{color}" stroke-width="1.3" stroke-linecap="round" fill="none"/></svg>')

def dogear(s=30):
    """Folded top-right corner of a letter (sits inside the clipped paper, so the cut shows the board)."""
    return (f'<span aria-hidden="true" style="position:absolute;right:0;top:0;width:{s}px;height:{s}px;z-index:3;'
            f'background:linear-gradient(225deg,#0b0b0b 0 50%,#c9bb9c 50%,#e2d8c2 100%)"></span>')

def ruled(lh):
    """Faint writing lines under a letter's words (line-height lh px)."""
    return (f'background-image:repeating-linear-gradient(to bottom,transparent 0,transparent {lh - 1}px,rgba(150,128,96,.26) {lh - 1}px,rgba(150,128,96,.26) {lh}px);'
            f'line-height:{lh}px')

def unsent_tag(fs=9.5):
    return (f'<span style="display:inline-block;{TYPE};font-weight:700;font-size:{fs}px;letter-spacing:.14em;color:{RED};border:1.5px solid {RED};'
            f'border-radius:2px;padding:3px 7px 2px;transform:rotate(-1.5deg);white-space:nowrap">UNSENT · NO REPLIES</span>')

KIND_CSS = f"""
.kcard{{display:block;opacity:.7;transition:opacity .25s ease,transform .3s cubic-bezier(.2,.7,.2,1)}}
.kcard:hover{{opacity:.92;transform:translateY(-3px)}}
"""

KIND_COPY = {'echo': ('AN ECHO', "for whoever's up. they can reply."),
             'unsent': ('AN UNSENT LETTER', "to someone who'll never read it.<br>no replies, just heard.")}

def _radio(on, s=22):
    ring = f'<path d="M11 2.2 C17 2 20 6 19.7 11.2 C19.4 16.6 15.6 19.8 10.6 19.6 C5.2 19.4 2.2 15.8 2.4 10.6 C2.6 5.6 6 2.6 12.2 2.8" fill="none" stroke="{RED if on else PENCIL}" stroke-width="1.8" stroke-linecap="round"/>'
    tick = f'<path d="M6.6 11.2 L9.8 14.4 L16.2 6.8" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>' if on else ''
    return f'<svg width="{s}" height="{s}" viewBox="0 0 22 22" aria-hidden="true" style="display:block;flex-shrink:0;overflow:visible">{ring}{tick}</svg>'

def kind_cards(sel='echo', phone=False):
    """Step one of leaving something: two small paper cards, each says what it is in one line.
    The chosen one sits forward with a red tick; the other waits faded and takes you to its own page."""
    href = {'echo': 'V5MEchoWrite.dc.html' if phone else 'V5EchoWrite.dc.html',
            'unsent': 'V5MUnsentWrite.dc.html' if phone else 'V5UnsentWrite.dc.html'}
    out = []
    for i, key in enumerate(('echo', 'unsent')):
        on = key == sel
        lab, line = KIND_COPY[key]
        ico = ico_note if key == 'echo' else ico_letter
        if phone:
            w, h, pad, fl, fs, rad = 346, (74 if key == 'echo' else 92), '15px 18px', 11, 15.5, 20
        else:
            w, h, pad, fl, fs, rad = 292, 116, '18px 22px', 12, 17, 22
        inner = (f'<div style="display:flex;align-items:center;gap:10px">{ico(INK, 18 if phone else 19)}'
                 f'<span style="{TYPE};font-weight:700;font-size:{fl}px;letter-spacing:.16em;color:{INK}">{lab}</span>'
                 f'<span style="margin-left:auto">{_radio(on, rad)}</span></div>'
                 f'<div style="{SERIF};font-size:{fs}px;line-height:1.35;color:{INK};margin-top:{7 if phone else 10}px">{line}</div>')
        rot = ([-1.2, .9] if not phone else [-.7, .6])[i]
        card = paper(inner, w, h, rot=rot if on else 0, kind='hi' if on else '', seed=741 + i + (10 if phone else 0), pad=pad,
                     extra='' if on else 'filter:none')
        if on:
            out.append(f'<div role="radio" aria-checked="true" aria-label="{lab.lower()}: {line.replace('<br>', ' ')}">{card}</div>')
        else:
            out.append(f'<a href="{href[key]}" class="kcard" role="radio" aria-checked="false" aria-label="{lab.lower()}: {line.replace('<br>', ' ')}">{card}</a>')
    d = 'column' if phone else 'row'
    return (f'<div role="radiogroup" aria-label="What are you leaving?" style="display:flex;flex-direction:{d};gap:{12 if phone else 16}px">'
            f'{"".join(out)}</div>')

def step_label(t, size=11):
    return f'<div style="{TYPE};font-size:{size}px;letter-spacing:.16em;color:{BOARDTXT}">{t}</div>'

def _rec(w, uid, fs=26, gap=12, phone=False):
    stop = f'<span style="{TYPE};font-size:{9.5 if phone else 10}px;letter-spacing:.14em;color:{PENCIL}">LET GO TO STOP</span>'
    return (f'<div style="display:flex;align-items:center;gap:{gap}px"><span style="width:12px;height:12px;border-radius:50%;background:{RED}"></span>'
            f'<span style="{HAND};font-size:{fs}px;color:{INK};white-space:nowrap">recording · 0:07</span>'
            f'{"" if phone else "<span style=margin-left:auto>" + stop + "</span>"}</div>'
            f'<div style="margin-top:{12 if phone else 14}px">{wave(w, 44 if phone else 48, 88, uid, 1, head=False, sw=2)}</div>'
            f'{"<div style=margin-top:10px>" + stop + "</div>" if phone else ""}')

def compose_paper(sel='echo', phone=False):
    """The paper you write on (or speak into). Echo = a plain note; unsent = a letter, addressed."""
    if not phone:
        W, P, fs, lh, tf, cnt = 600, 40, 22, 36, 12, 11
    else:
        W, P, fs, lh, tf, cnt = 338, 24, 18.5, 30, 11, 9.5
    count = f'<span data-slot="noteCount" style="{TYPE};font-size:{cnt}px;letter-spacing:.14em;color:{PENCIL};padding-bottom:6px">{58 if sel == "echo" else 74} / 400</span>'
    top = f'<div style="display:flex;justify-content:space-between;align-items:center">{toggle(tf, 22 if not phone else 16)}{count}</div>'
    rec = _rec(W - 2 * P, 'dcw' if not phone else 'mcw', 26 if not phone else 22, phone=phone)
    if sel == 'echo':
        words = f'<div data-slot="noteText" style="{SERIF};font-size:{fs}px;line-height:1.6;color:{INK};margin-top:20px">{ECHO_TXT}<span class="blink" style="color:{RED}">|</span></div>'
        foot = 'NO NAME ON IT. EVER. FADES IN 24H.'
        H = 262 if not phone else 234
        extra_top, ear, crease = '', '', ''
        kind = 'hi'
    else:
        to = (f'<div style="display:flex;align-items:baseline;gap:12px;margin-top:{16 if not phone else 12}px;padding-bottom:2px;border-bottom:1.5px solid {RULE}">'
              f'<span style="{TYPE};font-size:{10 if not phone else 9.5}px;letter-spacing:.16em;color:{PENCIL}">TO</span>'
              f'<span style="{HAND};font-size:{30 if not phone else 25}px;line-height:1.2;color:{INK}">grandpa,</span>'
              f'<span style="margin-left:auto;{TYPE};font-size:{9.5 if not phone else 8.5}px;letter-spacing:.12em;color:{PENCIL}">A NAME, OR JUST &ldquo;YOU&rdquo;</span></div>')
        extra_top = to
        words = f'<div data-slot="noteText" style="{SERIF};font-size:{fs}px;color:{INK};margin-top:10px;{ruled(lh)}">{LETTER_TXT}<span class="blink" style="color:{RED}">|</span></div>'
        foot = "NOT SENT TO THEM. NO NAME ON IT. FADES IN 24H." if not phone else "NOT SENT TO THEM. FADES IN 24H."
        H = 318 if not phone else 272
        ear = dogear(30 if not phone else 24)
        # a faint fold across the sheet: it reads as a letter, not a sticky note
        crease = (f'<span aria-hidden="true" style="position:absolute;left:0;right:0;top:{H * .62:.0f}px;height:2px;'
                  f'background:linear-gradient(to bottom,rgba(120,96,60,.13),rgba(255,252,242,.5))"></span>')
        kind = 'hi'
    body = (f'{ear}{crease}{top}{extra_top}'
            f'<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}">{words}</sc-if>'
            f'<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="noteVoice" style="margin-top:18px">{rec}</div></sc-if>'
            f'<div style="position:absolute;left:{P}px;right:{P}px;bottom:{22 if not phone else 18}px;border-top:1px dashed {RULE};padding-top:12px;'
            f'{TYPE};font-size:{11 if not phone else 9.5}px;letter-spacing:.14em;color:{PENCIL}">{foot}</div>')
    tx = W / 2 - 55
    return paper(body, W, H, rot=-1.2 if sel == 'echo' else -.8, kind=kind, seed=421 if not phone else 621,
                 pad=f'{30 if not phone else 22}px {P}px', tapes=tape(tx, -14, 110 if not phone else 96, 28 if not phone else 26, rot=-3, seed=42 if not phone else 62))

WRITE_COPY = {
    'echo': ('Leave it somewhere someone might find it.',
             'No name on it, ever. Strangers can listen, tap <span style="{m}">heard</span> or reply. It fades in 24 hours.'),
    'unsent': ('Say what you never got to say.',
               'It never reaches them, and no one can tell it was you. People can only tap <span style="{m}">heard</span>. It fades in 24 hours.'),
}

def write_board(sel='echo'):
    """Desktop: leave an echo / an unsent letter. One primary chip: the pin moment."""
    head, sub = WRITE_COPY[sel]
    sub = sub.format(m=f'{MARK};color:{SOFTRED};font-size:22px')
    nxt, label = ('V5EchoPinned.dc.html', 'pin it up') if sel == 'echo' else ('V5UnsentPinned.dc.html', 'put it up')
    return f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:96px;padding-bottom:40px">
<div style="width:430px;display:flex;flex-direction:column;gap:22px">
{h_hand(head, 48, d='2s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:19px;line-height:1.55;color:{BOARDTXT}">{sub}</div>
</div>
<div style="width:600px;display:flex;flex-direction:column">
<div class="rise" style="--w:.6s">{step_label('WHAT ARE YOU LEAVING?')}</div>
<div class="rise" style="--w:.7s;margin-top:14px">{kind_cards(sel)}</div>
<div class="rise" style="--w:.9s;margin-top:34px">{compose_paper(sel)}</div>
<div class="rise" style="--w:1.6s;display:flex;align-items:center;gap:30px;margin-top:30px">{chip(label, nxt, seed=422, w=180)}{link('not now', 'V5Echoes.dc.html')}</div>
</div>
</main>'''

def _ctape(w, h, rot, seed, top=-13):
    return tape(0, top, w, h, rot=rot, seed=seed).replace('left:0px', f'left:calc(50% - {w / 2:.0f}px)', 1)

def _mcompose(sel='echo'):
    """Phone compose paper as the screen's main sheet: grows to the dock, foot pinned to its bottom edge."""
    P, fs, lh = 22, 18.5, 30
    count = f'<span data-slot="noteCount" style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL};padding-bottom:6px">{58 if sel == "echo" else 74} / 400</span>'
    top = f'<div style="display:flex;justify-content:space-between;align-items:center">{toggle(11, 16)}{count}</div>'
    rec = _rec(250, 'mcw', 22, phone=True).replace('width:250px', 'width:100%;max-width:250px')
    if sel == 'echo':
        words = f'<div data-slot="noteText" style="flex:1 1 auto;{SERIF};font-size:{fs}px;line-height:1.6;color:{INK};margin-top:16px">{ECHO_TXT}<span class="blink" style="color:{RED}">|</span></div>'
        foot, extra, ear, crease, rot = 'NO NAME ON IT. EVER. FADES IN 24H.', '', '', '', -.4
    else:
        extra = (f'<div style="display:flex;align-items:baseline;gap:10px;margin-top:10px;padding-bottom:2px;border-bottom:1.5px solid {RULE}">'
                 f'<span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">TO</span>'
                 f'<span style="{HAND};font-size:25px;line-height:1.2;color:{INK}">grandpa,</span>'
                 f'<span style="margin-left:auto;{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL};text-align:right">A NAME, OR JUST &ldquo;YOU&rdquo;</span></div>')
        words = f'<div data-slot="noteText" style="flex:1 1 auto;min-height:{lh * 2}px;{SERIF};font-size:{fs}px;color:{INK};margin-top:8px;{ruled(lh)}">{LETTER_TXT}<span class="blink" style="color:{RED}">|</span></div>'
        foot, ear, rot = 'NOT SENT TO THEM. FADES IN 24H.', dogear(24), -.3
        crease = (f'<span aria-hidden="true" style="position:absolute;left:0;right:0;top:62%;height:2px;'
                  f'background:linear-gradient(to bottom,rgba(120,96,60,.13),rgba(255,252,242,.5))"></span>')
    body = (f'{ear}{crease}{top}{extra}'
            f'<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}">{words}</sc-if>'
            f'<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="noteVoice" style="margin-top:16px">{rec}</div></sc-if>'
            f'<div style="margin-top:auto;padding-top:12px;border-top:1px dashed {RULE};flex-shrink:0;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">{foot}</div>')
    return msheet(body, kind='hi', seed=621, pad=f'20px {P}px 16px', rot=rot, minh=200, tapes=_ctape(96, 26, -3, 62))

def mwrite_board(sel='echo'):
    """Phone twin of write_board, on the phone frame: compose paper is the main sheet, pin it up / not now in the dock."""
    head, _ = WRITE_COPY[sel]
    nxt, label = ('V5MEchoPinned.dc.html', 'pin it up') if sel == 'echo' else ('V5MUnsentPinned.dc.html', 'put it up')
    cards = kind_cards(sel, phone=True).replace('width:346px;max-width:100%', 'width:100%')
    return f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column">
{matmos()}
{mtopbar(crumb='echoes', back='V5MEchoes.dc.html')}
{mbody(h_hand(head, 28, d='1.8s')
       + f'<div class="rise" style="--w:.6s;margin-top:2px">{step_label("WHAT ARE YOU LEAVING?", 9.5)}</div>'
       + f'<div class="rise" style="--w:.7s;margin-top:-4px">{cards}</div>'
       + f'<div class="rise" style="--w:.9s;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;margin-top:8px">{_mcompose(sel)}</div>', gap=12)}
<div class="rise" style="--w:1.6s;display:flex;flex-direction:column">
{mdock(mcta(label, nxt, 'paper', seed=622) + mtext('not now', 'V5MEchoes.dc.html'))}</div>
{mfooter()}</div>'''

def letter_note(to, text, w, h, rot=0, seed=1, size=19, pad=(26, 28), hdr=24, foot='', tapes='', cls='', lh=None, tag=True, ear=30):
    """An unsent letter as it sits on the wall: addressed, lined, corner folded, tagged."""
    lh = lh or round(size * 1.5)
    t = f'<div style="margin-bottom:8px">{unsent_tag(9 if w < 330 else 9.5)}</div>' if tag else ''
    inner = (f'{dogear(ear)}{t}<div style="{HAND};font-size:{hdr}px;line-height:1.25;color:{PENCIL};margin-bottom:4px">to {to},</div>'
             f'<div style="{SERIF};font-size:{size}px;color:{INK};{ruled(lh)}">{text}</div>{foot}')
    return paper(inner, w, h, rot=rot, kind='hi', seed=seed, pad=f'{pad[0]}px {pad[1]}px', tapes=tapes, cls=cls)


if __name__ == '__main__':
    # ---------- the echo ----------
    echo_inner = f'''
<div style="display:flex;justify-content:space-between;align-items:center;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">
<span>AN ECHO · {{{{modeLabel}}}}</span><span style="display:flex;align-items:center;gap:8px"><span style="width:7px;height:7px;border-radius:50%;border:1.5px solid {PENCIL}"></span>FADES IN {{{{fadesShort}}}}</span></div>
<sc-if value="{{{{isVoice}}}}" hint-placeholder-val="{{{{ true }}}}">
<div style="{HAND};font-size:32px;line-height:1.2;color:{INK};margin-top:16px">{{{{timeTitle}}}}</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:22px">
<button type="button" class="pbtn" onClick="{{{{togglePlay}}}}" aria-label="{{{{playLabel}}}}">{play_btn(64, 'pbe', True)}</button>
{wave(340, 70, 77, 'we', 0, main=True)}
<span data-slot="playTime" style="{TYPE};font-size:12px;letter-spacing:.1em;color:{INK};white-space:nowrap">0:19 / 0:48</span></div>
<div style="{SERIF};font-style:italic;font-size:18px;line-height:1.5;color:{PENCIL};margin-top:22px">Just their voice. No transcript, and nothing left of it once it fades.</div></sc-if>
<sc-if value="{{{{isText}}}}" hint-placeholder-val="{{{{ false }}}}"><div style="{SERIF};font-size:21px;line-height:1.55;color:{INK};margin-top:18px;white-space:pre-wrap;overflow-wrap:anywhere">{{{{noteText}}}}</div></sc-if>
<div style="position:absolute;left:40px;right:40px;bottom:30px;border-top:1px dashed {RULE};padding-top:18px;display:flex;justify-content:space-between;align-items:center">
{heard_btn(26)}<span style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL};text-transform:uppercase">{{{{heardHint}}}}</span></div>
{stamp(40, 56, 36)}'''
    echo = paper(echo_inner, 600, 336, rot=-1.2, kind='hi', seed=501, pad='34px 40px', tapes=tape(245, -14, 110, 28, rot=-3, seed=51), cls='thud').replace('height:336px', 'height:{{cardH}}px', 1)

    def slip(name, when, kind, content, pk, seed, i):
        if kind == 'text':
            body = f'<div style="{SERIF};font-size:19px;line-height:1.5;color:{INK};margin-top:8px">{content}</div>'
            h = 132
        else:
            body = (f'<div style="display:flex;align-items:center;gap:16px;margin-top:10px">{play_btn(42, f"pr{i}")}'
                    f'{wave(300, 40, seed, f"wr{i}", 0, head=False, sw=1.8)}<span style="{TYPE};font-size:11px;letter-spacing:.1em;color:{INK}">{content}</span></div>')
            h = 112
        inner = (f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL}">'
                 f'<span style="text-transform:lowercase;letter-spacing:.06em;font-size:12px">{name}</span><span>{"VOICE · " if kind == "voice" else ""}{when.upper()}</span></div>{body}')
        rot = [-.8, .9, -.5][i]
        off = [0, 34, 10][i]
        tp = tape([200, 330, 120][i], -11, 80, 22, rot=[-4, 3, -2][i], seed=seed)
        return f'<div class="slip rise" style="--w:{.9 + i * .25:.2f}s;margin-left:{off}px;transform:rotate({rot}deg)">{paper(inner, 560, h, kind=pk, seed=seed, pad="20px 26px", tapes=tp)}</div>'

    slips = ''.join(slip(*r, i) for i, r in enumerate(REPLIES))

    composer = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{toggle(11, 18)}<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">NO NAME ON IT</span></div>
<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:12px">
<div data-slot="replyText" style="{SERIF};font-size:20px;color:{PENCIL};font-style:italic">say something kind back<span class="blink" style="color:{RED};font-style:normal">|</span></div>
{chip('reply', kind='ink', w=120, seed=521, onclick='sendReply')}</div></sc-if>
<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="replyVoice" style="display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:12px">
<div style="display:flex;align-items:center;gap:12px"><span style="width:12px;height:12px;border-radius:50%;background:{RED}"></span><span style="{HAND};font-size:24px;color:{INK}">hold to record a reply</span></div>
<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">UP TO 30 SECONDS</span></div></sc-if>''',
        600, 146, rot=.4, kind='', seed=522, pad='22px 28px', tapes=tape(270, -12, 90, 24, rot=2, seed=52))

    # board marks drawn from a fixed seed so the pinned scrap sits in empty board, clear of the headline
    room = '<div class="room" aria-hidden="true"></div>' + traces(1440, 900, seed=34) + '<div class="vignette"></div><div class="grain"></div>'
    body = f'''
{room}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px;display:flex;gap:64px">
<div style="width:640px;display:flex;flex-direction:column;gap:18px;padding-top:2px">
<div class="rise" style="--w:.1s">{link('← the wall', 'V5Echoes.dc.html', BOARDTXT, 12)}</div>
{h_hand('Left for whoever is up.', 44, wait='.2s')}
<div class="rise" style="--w:.9s;display:flex;align-items:center;gap:10px;margin-top:-6px">{ico_note(BOARDTXT, 16)}{step_label('AN ECHO · ANONYMOUS · ANYONE CAN LISTEN AND REPLY · FADES IN {{fadesShort}}')}</div>
<div class="rise" style="--w:.5s;margin:18px 0 0 14px">{echo}</div>
<div class="rise" style="--w:2.2s;display:flex;align-items:center;gap:14px;margin:26px 0 0 30px">
{t_mark("heard is the only reaction. no likes, no followers.", 22, SOFTRED, 'transform:rotate(-1.5deg)')}</div>
</div>
<div style="flex-grow:1;display:flex;flex-direction:column;padding-top:40px">
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;padding-right:8px">
<span style="{HAND};font-size:34px;color:{CHALK}">{{{{repliesTitle}}}}</span>
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">BY VOICE OR TEXT · THEY FADE WITH IT</span></div>
<div data-slot="replies" style="display:flex;flex-direction:column;gap:20px;margin-top:22px">{slips}</div>
<div class="rise" style="--w:1.8s;margin-top:auto;margin-bottom:26px">{composer}</div>
</div>
</main>
{footer()}'''
    doc_body = f'<div class="{{{{rootClass}}}}" style="position:absolute;inset:0;display:flex;flex-direction:column">{body}</div>'
    page('V5EchoThread', 'An echo', doc_body, css=ECHO_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)
    write_manifest([{"file": "V5EchoThread.dc.html", "title": "E04 — An echo: listen, Heard, reply", "w": 1440, "h": 900, "row": "echoes"}])
    print('echo thread ok')
