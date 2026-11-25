from gen5 import *
from v5x_echo import wave, play_btn, kind_pick, toggle, THREAD_SCRIPT, THREAD_PROPS, write_board, KIND_CSS, letter_note, ico_note, ico_letter

STAMP_CSS = f"""
.stamp{{position:absolute;{MARK};color:{RED};border:3px solid {RED};border-radius:6px;padding:2px 12px 0;font-size:30px;letter-spacing:.06em;transform:rotate(-12deg);
mix-blend-mode:multiply;opacity:.85;-webkit-mask-image:{NOISE_LIGHT};mask-image:{NOISE_LIGHT};animation:stamp .55s cubic-bezier(.2,1.6,.4,1) 1.2s both;pointer-events:none}}
@keyframes stamp{{0%{{opacity:0;transform:rotate(-12deg) scale(1.9)}}60%{{opacity:.9;transform:rotate(-12deg) scale(.94)}}100%{{opacity:.85;transform:rotate(-12deg) scale(1)}}}}
.heard{{display:inline-flex;align-items:center;gap:7px;{MARK};font-size:21px;color:{RED};transition:transform .2s;white-space:nowrap}}
.played{{position:absolute;left:0;top:0;bottom:0;overflow:hidden}}
.heard:hover{{transform:scale(1.06) rotate(-2deg)}}
.note{{transition:transform .5s cubic-bezier(.2,.7,.2,1)}}
.note:hover{{transform:translateY(-4px) rotate(0deg) !important;z-index:20}}
.drop{{animation:drop .9s cubic-bezier(.3,1.4,.5,1) both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-70px) rotate(-10deg) scale(1.08)}}to{{opacity:1}}}}
.slap{{display:block;animation:slap .35s cubic-bezier(.2,1.6,.4,1) both}}
@keyframes slap{{from{{opacity:0;transform:scale(1.6) translateY(-12px)}}to{{opacity:1;transform:none}}}}
"""

def heart(color=RED, size=18, fill='none'):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 20 20" aria-hidden="true"><path d="M10 17 C3 12 1 8 3 5 C5 2 9 3 10 6 C11 3 15 2 17 5 C19 8 17 12 10 17 Z" '
            f'fill="{fill}" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/></svg>')

def echo_note(text, left, top, w, h, rot, seed, kind='', fades='fades in 14h', heard=4, to=None, faded=False, stamped=False, size=19, tapeat=None, voice=None, replies=0):
    # the stamp sits clear of the heard link, up and in from the corner
    stamp = f'<span class="stamp" style="right:42px;bottom:76px">HEARD</span>' if stamped else ''
    tx = tapeat if tapeat is not None else w / 2 - 50
    tp = tape(tx, -13, 100, 26, rot=random.Random(seed).uniform(-8, 8), seed=seed)
    op = 'opacity:.55;filter:saturate(.6);' if faded else ''
    heard_el = f'<span class="heard">{heart(fill=RED if stamped else "none")}heard · {heard + (1 if stamped else 0)}</span>'
    if to:  # an unsent letter: addressed, lined, corner folded, no replies
        foot = (f'<div style="position:absolute;left:28px;right:26px;bottom:20px;display:flex;justify-content:space-between;align-items:center">'
                f'<span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">{fades}</span>{heard_el}</div>{stamp}')
        return (f'<a href="V5UnsentOpen.dc.html" class="note" aria-label="An unsent letter to {to}" style="position:absolute;left:{left}px;top:{top}px;{op}transform:rotate({rot}deg)">'
                f'{letter_note(to, text, w, h, seed=seed, size=size, foot=foot, tapes=tp, lh=28)}</a>')
    if voice:
        body = (f'<div style="{HAND};font-size:25px;line-height:1.2;color:{INK}">{voice[0]}</div>'
                f'<div style="display:flex;align-items:center;gap:12px;margin-top:12px">{play_btn(42, f"vw{seed}")}'
                f'{wave(w - 56 - 54, 34, seed, f"vww{seed}", 0, head=False, sw=1.7)}</div>'
                f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{INK};margin-top:10px">VOICE · {voice[1]}</div>')
    else:
        body = f'<div style="{SERIF};font-size:{size}px;line-height:1.5;color:{INK}">{text}</div>'
    rep = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};white-space:nowrap">{replies} {"REPLY" if replies == 1 else "REPLIES"}</span>' if replies else ''
    inner = (f'{body}'
             f'<div style="position:absolute;left:28px;right:26px;bottom:20px;display:flex;justify-content:space-between;align-items:center">'
             f'<span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">{fades}</span>'
             f'<span style="display:flex;align-items:center;gap:14px">{rep}{heard_el}</span></div>{stamp}')
    return (f'<a href="V5EchoThread.dc.html" class="note" style="position:absolute;left:{left}px;top:{top}px;{op}transform:rotate({rot}deg)">'
            f'{paper(inner, w, h, kind=kind, seed=seed, pad="26px 28px", tapes=tp)}</a>')

wall_notes = ''.join([
    echo_note("I got the job. There's no one I can tell who'd actually be happy for me, so I'm telling you.", 0, 30, 330, 230, -2.5, 401, 'hi', '21h left', 9, replies=2),
    echo_note("I miss who I was before all of this.", 360, 0, 280, 190, 2, 402, '', '19h left', 14, stamped=True),
    echo_note("I'm sorry I didn't pick up. I didn't know it was the last time you'd call.", 664, 34, 336, 262, -1.2, 403, '', '16h left', 6, to='grandpa'),
    echo_note('', 1014, 0, 316, 214, 3, 404, 'hi', '14h left', 12, voice=('left here at 1:12 am', '0:48'), replies=3),
    echo_note("Three years sober today. Nobody knows. I'm proud of me.", 40, 290, 300, 190, 1.8, 405, '', '9h left', 33),
    echo_note('', 380, 240, 290, 190, -2.8, 406, 'kraft', '17h left', 4, voice=('a long day', '0:12')),
    echo_note("You were right about me. I just wasn't ready to hear it.", 700, 326, 304, 226, 2.4, 407, '', '3h left', 2, to='you know who'),
    echo_note("first snow in my city tonight. hope it's quiet where you are.", 1030, 260, 280, 190, -1.6, 408, '', '41m left', 11, faded=True),
])

echoes = f'''
{atmos(leak(1120, -260, 600) + leak(-240, 620, 520, ROSE, 5) + '<div class="flare"></div>')}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px 0;display:flex;flex-direction:column;gap:22px">
<div style="display:flex;justify-content:space-between;align-items:flex-end">
<div>
{h_hand('Things people left here tonight.', 54)}
<div class="rise" style="--w:1.2s;{TYPE};font-size:12px;letter-spacing:.16em;color:{BOARDTXT};margin-top:4px">ANONYMOUS · EACH ONE FADES AWAY IN 24 HOURS · TAP <span style="color:{SOFTRED}">HEARD</span> IF IT REACHED YOU</div>
<div class="rise" style="--w:1.5s;display:flex;align-items:center;gap:34px;margin-top:14px;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">
<span style="display:flex;align-items:center;gap:9px">{ico_note(CHALK, 17)}<span><span style="color:{CHALK}">ECHOES</span> · ANYONE CAN REPLY</span></span>
<span style="display:flex;align-items:center;gap:9px">{ico_letter(CHALK, 17)}<span><span style="color:{CHALK}">UNSENT LETTERS</span> · HEARD ONLY</span></span></div>
</div>
<div class="rise" style="--w:.8s;display:flex;align-items:center;gap:14px;margin-bottom:4px">
<span style="{MARK};font-size:24px;color:#F0A08F;transform:rotate(-3deg)">your turn?</span>{chip('leave yours →', 'V5EchoWrite.dc.html', seed=411, w=210)}</div>
</div>
<div class="rise" data-slot="wall" style="--w:.4s;position:relative;height:540px">{wall_notes}</div>
</main>'''
page('V5Echoes', 'Echoes', echoes, css=STAMP_CSS)

# ---------- write an echo (step one: echo or unsent letter; then write / speak) ----------
page('V5EchoWrite', 'Leave an echo', write_board('echo'), css=STAMP_CSS + KIND_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)

# ---------- pinned (end state) ----------
pinned_note = paper(f'<div data-slot="pinnedText" style="{SERIF};font-size:22px;line-height:1.6;color:{INK};display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden">I keep rehearsing conversations that will never happen.</div>'
                    f'<div style="position:absolute;left:34px;bottom:22px;{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">FADES IN 24H</div>',
                    360, 210, rot=2.5, seed=431, pad='30px 34px',
                    tapes=f'<span class="slap" style="animation-delay:1s">{tape(130, -14, 100, 28, rot=-4, seed=43)}</span>')
ghosts = ''.join(f'<div style="position:absolute;left:{x}px;top:{y}px;opacity:.18;transform:rotate({rr}deg)">{paper("", ww, hh, seed=sd)}</div>'
                 for x, y, ww, hh, rr, sd in [(-330, -40, 260, 170, -3, 441), (420, -70, 240, 160, 2, 442), (-300, 230, 230, 150, 2, 443), (430, 210, 260, 170, -2, 444)])
pinned = f'''
{atmos(leak(520, 160, 720, GLOW, 0, dur=8) + leak(-200, 600, 480, ROSE, 3))}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:56px;padding-bottom:60px">
<div style="position:relative"><div class="drop" style="animation-delay:.2s">{pinned_note}</div></div>
<div style="display:flex;flex-direction:column;align-items:center;gap:14px">
{h_hand("It's up there now.", 64, color=PAPERHI, wait='1.4s')}
<div class="rise" style="--w:2.4s;{SERIF};font-style:italic;font-size:21px;color:rgba(233,233,231,.8);5">Someone out there might need exactly these words tonight.</div>
<div class="rise" style="--w:2.9s;display:flex;align-items:center;gap:34px;margin-top:22px">{chip('see the wall', 'V5Echoes.dc.html', seed=432, w=200)}{link('back home', 'V5Home.dc.html')}</div>
</div></main>'''
page('V5EchoPinned', 'Echo pinned', pinned, css=STAMP_CSS)

# ---------- capsule: write ----------
def opt(label, sel=False):
    c = circle_scribble(len(label) * 12 + 44, 54, RED, wait='1.8s') if sel else ''
    return f'<span style="position:relative;display:inline-block;padding:8px 14px;{HAND};font-size:23px;color:{INK if sel else PENCIL}">{c}{label}</span>'

def copt(label, key, sel=False, cw=None):
    """A clickable "open it" option; the chosen one gets the red circle."""
    c = circle_scribble(cw or (len(label) * 12 + 44), 54, RED, wait='1.8s')
    hint = 'true' if sel else 'false'
    return (f'<button type="button" class="capopt" onClick="{{{{pick{key}}}}}" aria-pressed="{{{{on{key}}}}}" '
            f'style="position:relative;display:inline-block;padding:8px 14px;{HAND};font-size:23px;color:{{{{col{key}}}}}">'
            f'<sc-if value="{{{{on{key}}}}}" hint-placeholder-val="{{{{ {hint} }}}}">{c}</sc-if>{label}</button>')

def slot_field(html, name):
    """field() with its value line as a live slot."""
    k = 'padding:8px 0 6px'
    i = html.index(k); j = html.rindex('<div ', 0, i)
    return html[:j] + f'<div data-slot="{name}" ' + html[j + 5:]

CAP_VALS = ("onWeek: false, onMonth: false, onDate: true, colWeek: '#5F584E', colMonth: '#5F584E', colDate: '#221E1A', "
            "dateLabel: 'on 15 october', storageNote: false")
CAP_COPY = 'Sealed in this browser. If you add an email, we keep only that and the date, and delete both once it sends.'

def cap_letter(email_value='', error='', date='on 15 october', h=506, chip_seed=452):
    """The capsule letter: words, then when it opens, then the optional email, and the seal at the bottom right."""
    return paper(f'''
<div style="{HAND};font-size:34px;color:{INK}">Dear later me,</div>
<div data-slot="capText" style="{SERIF};font-size:21px;line-height:1.65;color:{INK};margin-top:14px">Right now you're scared about the interview on Monday. Whatever happened, you went. That was the hard part. Be gentle with yourself either way.{'' if email_value else '<span class="blink" style="color:' + RED + '">|</span>'}</div>
<div style="margin-top:40px;border-top:1px dashed {RULE};padding-top:16px;display:flex;align-items:center;gap:6px;flex-wrap:wrap">
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL};margin-right:10px">OPEN IT</span>{copt('next week', 'Week')}{copt('in a month', 'Month')}{copt('{{dateLabel}}', 'Date', True, cw=200)}</div>
<div style="margin-top:24px">{slot_field(field('remind me by email · optional', email_value, 'you@somewhere.com', error=error, w=556), 'capEmail')}</div>
<div style="display:flex;justify-content:flex-end;margin-top:22px">{chip('seal it', 'V5CapsuleSealed.dc.html', seed=chip_seed, w=170, kind='ink')}</div>''',
        660, h, rot=.8, kind='hi', seed=451, pad='46px 52px 40px', tapes=tape(270, -15, 120, 30, rot=3, seed=45))

letter = cap_letter()

cwrite = f'''
{atmos(leak(1080, -240, 620) + leak(-260, 560, 560, ROSE, 4))}
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:90px;padding-bottom:30px">
<div style="width:400px;display:flex;flex-direction:column;gap:24px">
{h_hand('Write to the you who comes later.', 50, d='2s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:19px;line-height:1.55;color:{BOARDTXT}">{CAP_COPY}</div>
<sc-if value="{{{{storageNote}}}}">{inline_note("this browser can't keep things right now (a private window?).<br>the letter won't wait here. an email reminder still works.", 'soft', 21)}</sc-if>
<div class="rise" style="--w:1.7s;margin-top:8px">{link('not now', 'V5Home.dc.html')}</div>
</div>
<div class="rise" style="--w:.5s">{letter}</div>
</main>'''
page('V5Capsule', 'Time capsule', cwrite, script="renderVals() { return { %s }; }" % CAP_VALS)

# ---------- capsule: sealed (end state) ----------
SEAL = (f'<svg width="96" height="96" viewBox="0 0 100 100" aria-hidden="true"><defs>{ROUGH.format(i="seal", s=11, sc=6)}'
        f'<radialGradient id="sg" cx="40%" cy="35%"><stop offset="0" stop-color="#D4513F"/><stop offset=".7" stop-color="{RED}"/><stop offset="1" stop-color="#7d1f17"/></radialGradient></defs>'
        f'<g filter="url(#roughseal)"><circle cx="50" cy="50" r="44" fill="url(#sg)"/><circle cx="50" cy="50" r="33" fill="none" stroke="#8e2a20" stroke-width="2.5"/></g>'
        f'<g transform="translate(26 33) scale(.4)" opacity=".85"><path d="M16 13 L45 11 L47 41 L15 42 Z M74 12 L104 13 L103 42 L73 41 Z" fill="#7a1d15"/>'
        f'<path d="M45 64 L52 71 L59 64 L66 71 L73 64" fill="none" stroke="#7a1d15" stroke-width="6" stroke-linecap="round"/></g></svg>')

env_w, env_h = 460, 290
VY = env_h * .56          # where the side flaps meet (the V of the pocket)
FY = env_h * .60          # how far the top flap reaches when closed
LW, LH = env_w - 64, 238  # letter
_letter = paper(f'<div style="{HAND};font-size:26px">Dear later me,</div><div style="{SERIF};font-size:15px;line-height:1.6;margin-top:8px;color:{PENCIL};display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden">{{{{preview}}}}</div>',
                LW, LH, kind="hi", seed=461, pad='24px 26px')
def _poly(pts):
    return 'polygon(' + ','.join(f'{x:.0f}px {y:.0f}px' for x, y in pts) + ')'
pocket = _poly([(0, 6), (env_w / 2, VY), (env_w, 6), (env_w, env_h), (0, env_h)])
flap_poly = _poly([(0, 0), (env_w, 0), (env_w / 2, FY)])
envelope = f"""<div class="env" style="position:relative;width:{env_w}px;height:{env_h}px">
<!-- 1. inside of the envelope (back panel) -->
<div style="position:absolute;inset:0;z-index:1;filter:drop-shadow(0 16px 24px rgba(0,0,0,.55))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#B49D74;clip-path:{deckle(env_w, env_h, seed=462)}"></div>
<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.28),rgba(0,0,0,0) 45%)"></div></div>
<!-- 2. the letter slides down into the pocket, in front of the back panel -->
<div class="letter-in" style="position:absolute;left:{(env_w - LW) / 2:.0f}px;top:{env_h * .12:.0f}px;width:{LW}px;height:{LH}px;z-index:3">{_letter}</div>
<!-- 3. the pocket (side + bottom flaps), in front of the letter -->
<div style="position:absolute;inset:0;z-index:4;filter:drop-shadow(0 -2px 3px rgba(0,0,0,.22))">
<div class="paper kraft" style="position:absolute;inset:0;clip-path:{pocket}"></div>
<svg width="{env_w}" height="{env_h}" style="position:absolute;inset:0" aria-hidden="true"><path d="M2 {env_h - 2} L{env_w / 2} {VY + 18:.0f} L{env_w - 2} {env_h - 2}" fill="none" stroke="rgba(80,55,25,.32)" stroke-width="1.5"/></svg>
<div style="position:absolute;right:26px;bottom:20px;{HAND};font-size:22px;color:{INK};transform:rotate(-3deg)">open on {{{{openShort}}}}.</div></div>
<!-- 4. the top flap: open and behind everything first, then folds down over the front -->
<div class="flap" style="position:absolute;left:0;top:0;width:{env_w}px;height:{FY:.0f}px;transform-origin:50% 0">
<div class="paper kraft" style="position:absolute;inset:0;background-color:#CDB892;clip-path:{flap_poly}"></div></div>
<!-- 5. the seal, pressed onto the flap's tip -->
<div class="seal" style="position:absolute;left:{env_w / 2 - 48:.0f}px;top:{FY - 62:.0f}px;z-index:7">{SEAL}</div>
</div>"""

SEAL_CSS = """
.letter-in{opacity:0;animation:letterin 1.5s cubic-bezier(.55,.05,.35,1) .35s both}
@keyframes letterin{0%{opacity:0;transform:translateY(-250px) rotate(-3deg)}15%{opacity:1}100%{opacity:1;transform:translateY(0) rotate(0)}}
.flap{z-index:2;transform:perspective(900px) rotateX(180deg);animation:flap .9s cubic-bezier(.45,.05,.3,1) 2s both}
@keyframes flap{0%{z-index:2;transform:perspective(900px) rotateX(180deg);filter:brightness(.82)}49%{z-index:2}50%{z-index:6;filter:brightness(.7)}100%{z-index:6;transform:perspective(900px) rotateX(0deg);filter:brightness(1) drop-shadow(0 3px 3px rgba(0,0,0,.25))}}
.seal{opacity:0;animation:seal .6s cubic-bezier(.2,1.6,.4,1) 2.95s both}
@keyframes seal{0%{opacity:0;transform:scale(2.2) rotate(-20deg)}55%{opacity:1;transform:scale(.9) rotate(4deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
.envwrap{animation:settle 1s ease 2.95s both}
@keyframes settle{0%,100%{transform:none}30%{transform:translateY(4px)}}
"""
sealed = f'''
{atmos(leak(470, 120, 760, GLOW, 1.2, dur=9) + leak(-260, 560, 520, ROSE, 3) + '<div class="flare"></div>')}
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:50px;padding-bottom:40px">
<div class="envwrap" style="margin-top:110px">{envelope}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
{h_hand('Sealed. See you on {{openLong}}.', 58, color=PAPERHI, wait='3.4s')}
<div class="rise" style="--w:4.2s;{SERIF};font-style:italic;font-size:21px;color:rgba(233,233,231,.8);5">Until then it waits here, in this browser. Not even we can open it.</div>
<sc-if value="{{{{remindOk}}}}"><div class="rise" style="--w:4.4s">{inline_note('{{remindOkText}}', 'soft', 22)}</div></sc-if>
<sc-if value="{{{{remindFail}}}}"><div class="rise" style="--w:4.4s">{inline_note('{{remindFailA}} {{remindFailB}}', 'soft', 22)}</div></sc-if>
<div class="rise" style="--w:4.6s;display:flex;align-items:center;gap:34px;margin-top:20px">{chip('back home', 'V5Home.dc.html', seed=463, w=180)}{link('write another', 'V5Capsule.dc.html')}</div>
</div></main>'''
SEALED_VALS = "openLong: '15 October', openShort: '15 oct', preview: 'Right now you\\'re scared about the interview on Monday. Whatever happened, you went…', remindOk: false, remindFail: false, remindFailA: 'couldn\\'t set the reminder.', remindFailB: 'the letter is still sealed here.'"
page('V5CapsuleSealed', 'Capsule sealed', sealed, css=SEAL_CSS, script="renderVals() { return { %s }; }" % SEALED_VALS)

# ---------- capsule: open ----------
opened_letter = paper(f'''
<div style="{HAND};font-size:36px;color:{INK}">Dear later me,</div>
<div data-slot="openText" style="{SERIF};font-size:22px;line-height:1.7;color:{INK};margin-top:16px"><div>Right now you're scared about the interview on Monday.</div>
<div style="margin-top:14px">Whatever happened, you went. That was the hard part. Be gentle with yourself either way.</div></div>
<div style="{HAND};font-size:28px;color:{INK};margin-top:22px;text-align:right">you, on {{{{sealedOn}}}}</div>
''', 640, 470, rot=-1, kind='hi', seed=471, pad='48px 54px')
open_css = """.unfold{animation:unfold 1.6s cubic-bezier(.2,.8,.2,1) .3s both;transform-origin:50% 100%}
@keyframes unfold{from{opacity:0;transform:perspective(900px) rotateX(-70deg) translateY(60px)}to{opacity:1;transform:none}}"""
copen = f'''
{atmos(leak(460, 60, 760, GLOW, 0, dur=9) + leak(1150, 600, 420, ROSE, 3))}
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:80px;padding-bottom:40px">
<div style="width:380px;display:flex;flex-direction:column;gap:22px">
{t_mark('it arrived.', 30, '#F0A08F', 'transform:rotate(-3deg)')}
{h_hand('A note from you, {{agoText}}.', 50, wait='.4s', d='2s')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:19px;line-height:1.55;color:{ASH}">Read it as many times as you like. When you leave this page, it's gone.</div>
<div class="rise" style="--w:1.9s;display:flex;flex-direction:column;align-items:flex-start;gap:20px;margin-top:10px">
{chip('let it go', 'V5CapsuleLetGo.dc.html', seed=472, w=170)}{link('write back to a later you', 'V5Capsule.dc.html')}</div>
</div>
<div class="unfold">{opened_letter}</div>
</main>'''
page('V5CapsuleOpen', 'Capsule opened', copen, css=open_css, script="renderVals() { return { sealedOn: '1 October', agoText: 'two weeks ago' }; }")
print('leave ok')
