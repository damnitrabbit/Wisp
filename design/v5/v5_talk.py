from gen5 import *
import v5_live as LV
from v5m_talk import tchip

# ---------------- MATCHING ----------------
# A red thread leaves your note and quietly asks each listener on the board, one by one.
YOU_PIN = (330, 120)
LISTENERS = [  # (pin x, pin y, rot, seed)
    (720, 84, -4, 611), (880, 214, 3, 612), (1040, 70, -2, 613), (1190, 196, 5, 614)]
CYCLE = 11.2
SLOT = CYCLE / len(LISTENERS)
def _sag(x0, y0, x1, y1):
    mx = (x0 + x1) / 2
    return f'M {x0} {y0} Q {mx:.0f} {max(y0, y1) + 120 + (x1 - x0) * .06:.0f} {x1} {y1}'
def _pin(x, y, col):
    return (f"<ellipse cx='{x + 4}' cy='{y + 7}' rx='9' ry='5' fill='#000' opacity='.45'/>"
            f"<circle cx='{x}' cy='{y}' r='8' fill='{col}'/><circle cx='{x}' cy='{y}' r='8' fill='none' stroke='#000' stroke-opacity='.35'/>"
            f"<circle cx='{x - 2.6:.1f}' cy='{y - 2.6:.1f}' r='2.3' fill='#fff' opacity='.28'/>")
match_css = f"""
.thread{{stroke-dasharray:100 100;stroke-dashoffset:100;animation:ask {CYCLE}s cubic-bezier(.5,.05,.35,1) infinite;filter:drop-shadow(0 3px 2px rgba(0,0,0,.55))}}
@keyframes ask{{0%{{stroke-dashoffset:100}}9%{{stroke-dashoffset:0}}17%{{stroke-dashoffset:0}}24.5%,100%{{stroke-dashoffset:100}}}}
.slipw{{position:absolute;transform-origin:50% 8px;animation:tug {CYCLE}s ease-in-out infinite}}
@keyframes tug{{0%,8%{{transform:rotate(0) translateY(0)}}10%{{transform:rotate(-2.4deg) translateY(-3px)}}12.5%{{transform:rotate(1.6deg) translateY(-1px)}}15%,100%{{transform:rotate(0) translateY(0)}}}}
.slipw .lift{{transition:filter .4s}}
.knot{{opacity:0;animation:knot {CYCLE}s ease-in-out infinite}}
@keyframes knot{{0%,8.5%{{opacity:0;transform:scale(.4)}}10%{{opacity:1;transform:scale(1.15)}}12%,16%{{opacity:1;transform:scale(1)}}19%,100%{{opacity:0;transform:scale(.6)}}}}
.youw{{position:absolute;animation:breathe 4.4s ease-in-out infinite;transform-origin:50% 0}}
@keyframes breathe{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(.8deg)}}}}
"""
_scr = lambda w: f"<div style='height:2px;width:{w}px;background:{RULE};margin-top:12px;border-radius:2px'></div>"
def _listener(i, x, y, rot, seed):
    inner = f"<div style='padding-top:22px'>{_scr(70)}{_scr(92)}{_scr(54)}</div>"
    return (f'<div class="slipw" style="left:{x - 64}px;top:{y - 14}px;animation-delay:{i * SLOT:.2f}s">'
            f'{paper(inner, 128, 104, rot=rot, kind="hi" if i % 2 else "", seed=seed, pad="10px 18px")}</div>')
_threads = ''.join(
    f"<path class='thread' pathLength='100' style='animation-delay:{i * SLOT:.2f}s' d='{_sag(*YOU_PIN, x, y)}' fill='none' stroke='{RED}' stroke-width='2.2' stroke-linecap='round'/>"
    for i, (x, y, _, _) in enumerate(LISTENERS))
_knots = ''.join(
    f"<circle class='knot' style='animation-delay:{i * SLOT:.2f}s;transform-box:fill-box;transform-origin:center' cx='{x}' cy='{y}' r='13' fill='none' stroke='{RED}' stroke-width='1.6' stroke-dasharray='3 3'/>"
    for i, (x, y, _, _) in enumerate(LISTENERS))
_pins = _pin(*YOU_PIN, RED) + ''.join(_pin(x, y, '#3a3a3d') for x, y, _, _ in LISTENERS)
_you = paper(f'<div style="{HAND};font-size:36px;color:{INK};line-height:1">you</div>'
             f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-top:12px">QUIET_OTTER</div>',
             176, 128, rot=-3, kind='hi', seed=621, pad='30px 22px')
board = f'''
<div style="position:relative;width:1400px;height:330px;margin-top:10px">
<div class="youw" style="left:{YOU_PIN[0] - 88}px;top:{YOU_PIN[1] - 16}px">{_you}</div>
{''.join(_listener(i, *L) for i, L in enumerate(LISTENERS))}
<svg width="1400" height="330" viewBox="0 0 1400 330" aria-hidden="true" style="position:absolute;inset:0;overflow:visible;z-index:5">
{_threads}{_knots}{_pins}
</svg></div>'''
mcard = paper(f'''
<div style="display:grid;grid-template-columns:120px 1fr;row-gap:12px;{TYPE};font-size:13px;letter-spacing:.1em;color:{INK}">
<span style="color:{PENCIL}">THEY'LL</span><span>LISTEN FIRST</span>
<span style="color:{PENCIL}">STARTS AS</span><span>TEXT · VOICE ONLY IF YOU BOTH SAY YES</span>
<span style="color:{PENCIL}">KEPT</span><span>NOTHING</span></div>''', 470, 160, rot=-1.5, seed=501, pad='28px 32px', tapes=tape(180, -13, 100, 26, rot=3, seed=51))
def mini_scrap(text, feat, href, rot, seed, kind=''):
    inner = (f'<div style="{HAND};font-size:20px;color:{INK};white-space:nowrap">{text}</div>'
             f'<div style="{TYPE};font-size:9.5px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>')
    return f'<a href="{href}" class="chip" style="display:block">{paper(inner, 222, 74, rot=rot, seed=seed, kind=kind, pad="13px 18px")}</a>'
matching = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb=POD11)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center">
{board}
<div style="display:flex;flex-direction:column;align-items:center;gap:14px;margin-top:-6px">
{h_hand('Finding someone who\'ll listen…', 58)}
<div class="rise" style="--w:1.3s;{TYPE};font-size:12px;letter-spacing:.16em;color:{BOARDTXT}">USUALLY UNDER A MINUTE · 4 LISTENERS AWAKE</div>
</div>
<div style="display:flex;align-items:flex-start;gap:56px;margin-top:30px">
<div class="rise" style="--w:1.6s;margin-top:34px">{mcard}</div>
<div class="rise" style="--w:2s;display:flex;flex-direction:column;gap:12px;width:470px">
<div style="{MARK};font-size:23px;line-height:1.2;color:#F0A08F;transform:rotate(-1.5deg)">quiet night? it might take a little longer. that's okay.</div>
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT};margin-top:2px">OR LET IT GO ANOTHER WAY · ON YOUR OWN</div>
<div style="display:grid;grid-template-columns:repeat(2,222px);gap:12px 14px">{mini_scrap('get it out', 'BURN', 'V5Burn.dc.html', -1.5, 581)}{mini_scrap('leave it somewhere', 'ECHOES', 'V5Echoes.dc.html', 1.2, 582, 'kraft')}{mini_scrap('write it, don\'t send', 'UNSENT', 'V5UnsentWrite.dc.html', .8, 583, 'kraft')}{mini_scrap('hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', -1, 584)}</div>
<div style="margin-top:4px">{link('stop looking', 'V5Home.dc.html')}</div></div>
</div>
</main>'''
page('V5Matching', 'Finding someone', matching, css=match_css)
LV.mark('V5Matching', replace=[('4 LISTENERS AWAKE', '{{awake}}'), ("Finding someone who'll listen…", '{{matchTitle}}'), ("THEY'LL</span>", '{{whoFirst}}</span>')])

# ---------------- POD (1:1) ----------------
def slip(text, mine=False, who='moss_byte', seed=0, rot=0, w=None):
    kind = 'kraft' if mine else 'hi'
    ww = w or min(560, max(220, int(len(text) * 9.4 + 70)))
    lines = max(1, -(-int(len(text) * 9.4) // (ww - 60)))
    hh = 52 + lines * 29 + 18
    label = f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">{"YOU" if mine else who.upper()}</div>'
    inner = f'{label}<div style="{SERIF};font-size:19px;line-height:29px;color:{INK}">{text}</div>'
    al = 'flex-end' if mine else 'flex-start'
    return f'<div class="slipin" style="align-self:{al}">{paper(inner, ww, hh, rot=rot, kind=kind, seed=seed, pad="14px 22px", torn="bottom" if seed % 2 else "top")}</div>'

convo = ''.join([
    slip("hey. I'm here. take your time, there's no rush.", seed=511, rot=-.6),
    slip("I don't even know where to start honestly", True, seed=512, rot=.8),
    slip("that's okay. start anywhere. the middle is fine too.", seed=513, rot=-.4),
    slip("my best friend moved away last month and I didn't realise how much of my week was just… her", True, seed=514, rot=.5, w=520),
    slip("that sounds really lonely. like the shape of your days changed overnight.", seed=515, rot=-.8, w=480),
])
typing = (f'<div style="align-self:flex-start;display:flex;align-items:center;gap:10px;{HAND};font-size:20px;color:{BOARDTXT};padding-left:8px">'
          f'<span class="dots"><i></i><i></i><i></i></span>moss_byte is writing</div>')
pod_css = f"""
.slipin{{animation:slipin .7s cubic-bezier(.2,.9,.3,1) both}}
.slipin:nth-child(1){{animation-delay:.2s}}.slipin:nth-child(2){{animation-delay:.4s}}.slipin:nth-child(3){{animation-delay:.6s}}.slipin:nth-child(4){{animation-delay:.8s}}.slipin:nth-child(5){{animation-delay:1s}}
@keyframes slipin{{from{{opacity:0;transform:translateY(14px) rotate(-1deg)}}to{{opacity:1}}}}
.hl{{background-image:linear-gradient(transparent 38%,rgba(216,198,164,.75) 38%,rgba(216,198,164,.75) 90%,transparent 90%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 4px}}
.scroll{{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 70px);mask-image:linear-gradient(to bottom,transparent 0,#000 70px)}}
.msg{{opacity:0;animation:msgin .6s ease calc(.25s + var(--i) * .12s) both}}
@keyframes msgin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.pbtn{{transition:transform .2s ease,box-shadow .2s ease}}
.pbtn:hover{{transform:translateY(-1px);box-shadow:0 3px 0 rgba(0,0,0,.18)}}
.pbtn:active{{transform:translateY(1px);box-shadow:none}}
.dots i{{display:inline-block;width:6px;height:6px;margin-right:4px;border-radius:50%;background:{ASH};animation:dot 1.2s ease-in-out infinite}}
.dots i:nth-child(2){{animation-delay:.15s}}.dots i:nth-child(3){{animation-delay:.3s}}
@keyframes dot{{0%,100%{{transform:translateY(0);opacity:.4}}50%{{transform:translateY(-4px);opacity:1}}}}
.veil{{position:absolute;inset:0;background:rgba(8,8,9,.74);z-index:60;animation:fadein .6s ease both}}
.nudge{{position:absolute;left:50%;top:50%;z-index:61;transform:translate(-50%,-50%);animation:nudge .9s cubic-bezier(.3,1.3,.5,1) .3s both}}
@keyframes nudge{{from{{opacity:0;transform:translate(-50%,-30%) rotate(-6deg)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
"""
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
DOOR = '<path d="M3 15h10M5 15V2.5h6V15M9 9h.01M11 2.5l2 1.5V15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
FLAG = '<path d="M4 15V2.5M4 3h8l-2 3 2 3H4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
def pod_btn(label, href, icon, kind, seed=0):
    """DLS actions: torn paper chips (ink = primary, kraft = secondary); report is red-ink text with the hand underline."""
    ic = f'<svg width="16" height="17" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0">{icon}</svg>'
    if kind == 'red':
        return (f'<a href="{href}" class="ul" style="align-self:flex-start;display:inline-flex;align-items:center;gap:10px;margin:6px 0 0 4px;color:{RED};'
                f'{TYPE};font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase">{ic}<span>{label}</span></a>')
    rot = {'ink': -.8, 'kraft': .7}[kind]
    return tchip(label, href, kind, 240, 54, seed, icon, fs=13, rot=rot, justify='flex-start')

side = paper(f'''
<div style="{HAND};font-size:34px;line-height:1.2">you &amp; moss_byte</div>
<div style="display:flex;align-items:center;gap:8px;margin-top:8px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}"><span style="width:7px;height:7px;border-radius:50%;background:#E08A3C"></span>BOTH HERE</div>
<div style="{MARK};font-size:23px;color:{RED};line-height:1.25;margin-top:20px;transform:rotate(-1.5deg)">no fixing. no judging.<br>just two people.</div>
<div style="border-top:1px dashed {RULE};margin-top:22px;padding-top:18px;display:grid;grid-template-columns:1fr auto;row-gap:10px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">
<span>CHECK-IN IN</span><span style="color:{INK}">3:48</span><span>KEPT</span><span style="color:{INK}">NOTHING</span></div>
<div style="display:flex;flex-direction:column;gap:14px;margin-top:24px">
{pod_btn('ask for voice', '#', MIC, 'ink', seed=561)}
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};line-height:1.6;margin-top:2px;text-wrap:balance">VOICE STARTS ONLY IF YOU BOTH SAY YES.</div></div>
''', 300, 532, rot=-1.2, seed=521, pad='30px 30px', tapes=tape(100, -13, 100, 26, rot=-4, seed=52))
composer = paper(f'''<div style="display:flex;align-items:center;justify-content:space-between;gap:20px;height:100%">
<span style="{SERIF};font-style:italic;font-size:20px;color:{PENCIL}">say it however it comes out…</span>
<span style="{TYPE};font-weight:700;font-size:12px;letter-spacing:.18em;color:{INK}">SEND ↗</span></div>''', 760, 72, rot=.3, kind='hi', seed=531, pad='0 26px')

nudge_card = paper(f'''
<div style="{HAND};font-size:44px">It's been 10 minutes.</div>
<div style="{SERIF};font-size:20px;line-height:1.6;color:{INK};margin-top:12px">How are you doing? You can keep going, or end it gently. Either is okay.</div>
<div style="display:flex;align-items:center;gap:28px;margin-top:28px">{tchip('keep going', '#', 'ink', 190, 54, 541)}<a href="V5PodEnd.dc.html" class="ul" style="{TYPE};font-size:12px;letter-spacing:.16em;color:{INK}">END GENTLY</a></div>
<div style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL};margin-top:22px">THEY GET THE SAME QUESTION. NOBODY SEES WHAT THE OTHER PICKED.</div>''',
    560, 340, rot=-1, seed=542, pad='38px 44px', tapes=tape(220, -14, 110, 28, rot=3, seed=54))


# ---- one shared sheet: the conversation is written on a single notebook page ----
def line_msg(text, mine=False, who='moss_byte', t='11:52', i=0):
    head = f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">{"YOU" if mine else who.upper()} · {t}</div>'
    if mine:
        head = f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px;text-align:right">YOU · {t}</div>'
        body = f'<span class="hl" style="{SERIF};font-size:19px;line-height:30px;color:{INK}">{text}</span>'
        return f'<div class="msg" style="--i:{i};align-self:flex-end;max-width:74%;text-align:left">{head}{body}</div>'
    body = f'<span style="{SERIF};font-size:19px;line-height:30px;color:{INK}">{text}</span>'
    return f'<div class="msg" style="--i:{i};align-self:flex-start;max-width:74%;padding-left:16px;border-left:2px solid rgba(184,53,42,.35)">{head}{body}</div>'

def sys_line(text, size=10):
    """The pod's one opening line (who came to do what), in pencil, centred like the other system lines."""
    return (f'<div class="msg" data-slot="podOpening" style="--i:0;align-self:center;display:flex;align-items:center;gap:10px;{TYPE};font-size:{size}px;letter-spacing:.16em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">'
            f'<span style="width:28px;border-top:1px dashed {RULE}"></span><span>{text}</span><span style="width:28px;border-top:1px dashed {RULE}"></span></div>')

chat_msgs = sys_line('moss_byte came to talk.') + ''.join([
    line_msg("hey. I'm here. take your time, there's no rush.", t='11:52', i=0),
    line_msg("I don't even know where to start honestly", True, t='11:53', i=1),
    line_msg("that's okay. start anywhere. the middle is fine too.", t='11:53', i=2),
    line_msg("my best friend moved away last month and I didn't realise how much of my week was just… her. tuesdays were chai after work, and on sundays she'd just show up at my door. now the week has all these empty holes in it.", True, t='11:55', i=3),
    line_msg("that sounds really lonely. like the shape of your days changed overnight, and nobody handed you a new one.", t='11:56', i=4),
    line_msg("yeah. exactly that.", True, t='11:56', i=5),
])
chat_typing = (f'<div style="align-self:flex-start;display:flex;align-items:center;gap:10px;{HAND};font-size:20px;color:{PENCIL};padding-left:18px">'
               f'<span class="dots"><i></i><i></i><i></i></span>moss_byte is writing</div>')
CW, CH = 880, 724
chat_inner = f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.16) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">11:52 PM · YOU BOTH JOINED · NOTHING HERE IS SAVED</div>
<div class="scroll" style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;padding:18px 6px 14px;overflow:hidden">{chat_msgs}{chat_typing}</div>
<div style="border-top:1.5px dashed {RULE};padding-top:16px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<span style="{SERIF};font-style:italic;font-size:19px;color:{PENCIL}">say it however it comes out…<span class="blink" style="color:{INK};font-style:normal">|</span></span>
<span style="display:flex;align-items:center;gap:22px;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}"><span>ENTER TO SEND</span>{tchip('send ↗', '#', 'ink', 120, 54, 533)}</span></div>
</div>"""
chat_sheet = paper(chat_inner, CW, CH, rot=0.3, kind='hi', seed=534, pad='22px 34px 22px', tapes=tape(CW / 2 - 60, -14, 120, 30, rot=-2, seed=53))

def pod(nudge=False):
    ov = f'<div class="veil"></div><div class="nudge">{nudge_card}</div>' if nudge else ''
    return f'''
{atmos(leak(1150, -240, 520, GLOW, 0) + leak(-240, 640, 460, ROSE, 6))}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb=POD11)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;gap:56px;padding:0 56px 24px">
<div class="rise" style="--w:.1s;padding-top:10px">{side}</div>
<div class="rise" style="--w:.3s;padding-top:8px">{chat_sheet}</div>
</main>{ov}'''
OPEN_CSS = '.scroll{-webkit-mask-image:none;mask-image:none}'  # the whole talk fits on the board: no top fade, so the opening line reads
page('V5Pod', 'Talk pod', pod(), css=pod_css + OPEN_CSS)
LV.pod('V5Pod')
page('V5PodNudge', 'Talk pod, 10 minute check-in', pod(True), css=pod_css + OPEN_CSS)
LV.pod('V5PodNudge')

# ---------------- POD ENDED ----------------
pr = random.Random(9)
motes = ''.join(f'<i class="mote" style="left:{pr.uniform(5, 95):.0f}%;width:{(s := pr.uniform(2, 5)):.1f}px;height:{s:.1f}px;animation-delay:{pr.uniform(0, 8):.1f}s;animation-duration:{pr.uniform(7, 12):.1f}s;--dx:{pr.uniform(-60, 60):.0f}px"></i>' for _ in range(34))
end_css = f"""
.dawnrise{{position:absolute;left:-15%;right:-15%;bottom:-75%;height:130%;border-radius:50%;background:radial-gradient(ellipse at 50% 28%,rgba(255,214,160,.62),rgba(255,150,100,.24) 34%,rgba(120,70,90,.08) 55%,transparent 68%);mix-blend-mode:screen;filter:blur(20px);animation:dr 4.5s cubic-bezier(.2,.7,.2,1) both;z-index:2}}
@keyframes dr{{from{{opacity:0;transform:translateY(30%)}}to{{opacity:1;transform:none}}}}
.mote{{position:absolute;bottom:-10px;border-radius:50%;background:#CFCFCC;box-shadow:none;opacity:0;animation-name:mote;animation-iteration-count:infinite;animation-timing-function:linear;z-index:3}}
@keyframes mote{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:.45}}100%{{opacity:0;transform:translate(var(--dx),-760px)}}}}
"""
# the end: two slips side by side. Yours to write on (optional), theirs an empty pin spot until a note lands.
# Both people see this at the same moment; each sends or skips on their own, and the notes cross.
note_css = f"""
.stampx{{position:absolute;{MARK};color:{RED};border:3px solid {RED};border-radius:6px;padding:2px 12px 0;letter-spacing:.06em;transform:rotate(-12deg);opacity:0;animation:stampin .5s cubic-bezier(.3,1.6,.5,1) var(--sw,1.6s) forwards;mix-blend-mode:multiply}}
@keyframes stampin{{from{{opacity:0;transform:rotate(-12deg) scale(1.7)}}to{{opacity:.88;transform:rotate(-12deg) scale(1)}}}}
.landed{{animation:landed .8s cubic-bezier(.2,.9,.3,1.2) var(--w,2.6s) both}}
@keyframes landed{{from{{opacity:0;transform:translateY(-18px) rotate(-4deg)}}to{{opacity:1;transform:none}}}}
"""
RULED_NOTE = 'background-image:repeating-linear-gradient(to bottom,transparent 0 33px,rgba(96,120,150,.18) 33px 34px)'
def lbl(t, c=PENCIL, size=10):
    return f'<div style="{TYPE};font-size:{size}px;letter-spacing:.16em;color:{c}">{t}</div>'

def your_slip(sent=False, w=440, h=262):
    if sent:
        body = (f'{lbl("YOUR NOTE · PINNED FOR THEM")}'
                f'<div style="position:relative;margin-top:14px;flex-grow:1;{RULED_NOTE};padding-top:2px">'
                f'<div style="{HAND};font-size:27px;line-height:34px;color:{INK}">thank you for not rushing me. i needed that tonight.</div></div>'
                f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-top:10px">SENT · GONE WHEN THEY LEAVE</div>'
                f'<span class="stampx" style="right:26px;bottom:40px;font-size:30px">SENT</span>')
        tp = tape(w / 2 - 55, -14, 110, 28, rot=-3, red=True, seed=557)
    else:
        body = (f'{lbl("LEAVE THEM A NOTE · OPTIONAL")}'
                f'<div data-slot="noteWrite" style="position:relative;margin-top:14px;flex-grow:1;display:flex;flex-direction:column">'
                f'<div style="flex-grow:1;{RULED_NOTE};padding-top:2px;{HAND};font-size:26px;line-height:34px;color:{PENCIL}">say thanks, or anything…<span class="blink" style="color:{INK}">|</span></div>'
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-top:12px">'
                f'<span style="display:flex;align-items:center;gap:22px">{tchip("pin it", "#", "ink", 120, 44, 556, fs=12)}'
                f'<a href="#" class="ul" style="{TYPE};font-size:11px;letter-spacing:.16em;color:{INK}">SKIP</a></span>'
                f'<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">0 / 140</span></div></div>')
        tp = tape(w / 2 - 50, -13, 100, 26, rot=3, seed=555)
    return paper(f'<div style="height:100%;display:flex;flex-direction:column">{body}</div>', w, h, rot=-1.4, kind='hi', seed=553, pad='26px 32px 24px', tapes=tp)

PIN = ('<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" style="position:absolute;left:50%;top:-13px;margin-left:-12px;overflow:visible">'
       '<ellipse cx="15" cy="18" rx="9" ry="5" fill="#000" opacity=".45"/><circle cx="12" cy="12" r="8" fill="#3a3a3d"/>'
       '<circle cx="12" cy="12" r="8" fill="none" stroke="#000" stroke-opacity=".35"/><circle cx="9.4" cy="9.4" r="2.3" fill="#fff" opacity=".28"/></svg>')

def their_spot(landed=False, w=440, h=262):
    if landed:
        inner = (f'<div style="height:100%;display:flex;flex-direction:column">{lbl("MOSS_BYTE&#39;S NOTE")}'
                 f'<div data-slot="theirNote" style="margin-top:14px;flex-grow:1;{RULED_NOTE};padding-top:2px;{HAND};font-size:27px;line-height:34px;color:{INK}">thanks for staying with me tonight. i feel lighter.</div>'
                 f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-top:10px">ONLY YOU SEE THIS · GONE WHEN YOU LEAVE</div></div>')
        return (f'<div class="landed" style="--w:2.8s">'
                f'{paper(inner, w, h, rot=1.6, seed=558, pad="26px 32px 24px", tapes=tape(w / 2 - 50, -13, 100, 26, rot=-4, seed=559))}</div>')
    # an empty pin spot on the board: dashed outline, a pin waiting, pencil words
    return (f'<div style="position:relative;width:{w}px;height:{h}px;flex-shrink:0;border:2px dashed rgba(163,154,140,.45);border-radius:3px;transform:rotate(1.2deg);'
            f'padding:26px 32px 22px;display:flex;flex-direction:column;background:rgba(0,0,0,.2)">{PIN}'
            f'{lbl("MOSS_BYTE&#39;S NOTE", BOARDTXT)}'
            f'<div data-slot="theirNote" style="flex-grow:1;display:flex;align-items:center;justify-content:center;text-align:center;{HAND};font-size:26px;line-height:1.35;color:{BOARDTXT}">if they leave you one,<br>it lands here.</div>'
            f'<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{BOARDTXT};text-align:center">THEY CAN WRITE OR SKIP, SAME AS YOU</div></div>')

ask = paper(f'''<div style="height:100%;display:flex;align-items:center;justify-content:space-between;gap:28px">
<div style="{HAND};font-size:28px;line-height:1.25;color:{INK}">someone's waiting to be heard.<br>stay and listen?</div>
<div style="display:flex;align-items:center;gap:24px;flex-shrink:0">{tchip('stay and listen', 'V5Matching.dc.html', 'ink', 214, 50, 561, fs=12)}<a href="#" class="ul" style="{TYPE};font-size:11px;letter-spacing:.16em;color:{INK}">NOT TONIGHT</a></div></div>''',
    908, 112, rot=-.6, kind='kraft', seed=562, pad='0 34px 0 38px', tapes=tape(70, -12, 96, 24, rot=-5, seed=563))

def podend_body(notes=False):
    wait = '' if notes else (f'<sc-if value="{{{{someoneWaiting}}}}" hint-placeholder-val="{{{{ true }}}}">'
                             f'<div class="rise" style="--w:3.4s;margin-top:14px">{ask}</div></sc-if>')
    return f'''
<div class="dawnrise"></div><div aria-hidden="true" style="position:absolute;inset:0;pointer-events:none">{motes}</div>
{atmos(leak(-200, -220, 520, ROSE, 2))}
{topbar(crumb=POD11)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding-bottom:24px">
<div style="display:flex;flex-direction:column;align-items:center;gap:8px">
{h_hand('You were heard tonight.', 66, color=PAPERHI, wait='1s', d='2s')}
<div class="rise" style="--w:2.2s;{TYPE};font-size:12px;letter-spacing:.2em;color:rgba(233,233,231,.8);">18 MINUTES · 42 MESSAGES · 0 KEPT</div></div>
<div class="rise" style="--w:2.6s;display:flex;align-items:flex-start;gap:28px;margin-top:22px">{your_slip(notes)}{their_spot(notes)}</div>
{wait}
<div class="rise" style="--w:3.8s;display:flex;align-items:center;justify-content:space-between;width:908px;margin-top:{18 if notes else 8}px">
<div style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">YOU'VE HEARD 4 PEOPLE · THIS BROWSER REMEMBERS, WE DON'T</div>
<div style="display:flex;align-items:center;gap:30px">{link('talk to someone new', 'V5Matching.dc.html')}{chip('back home', 'V5Home.dc.html', seed=552, w=180)}</div></div>
</main>'''
page('V5PodEnd', 'Pod ended', podend_body(), css=end_css + note_css, script='renderVals() { return { someoneWaiting: true }; }')
LV.mark('V5PodEnd', replace=[('18 MINUTES · 42 MESSAGES · 0 KEPT', '{{stats}}')])
page('V5PodEndNotes', 'Pod ended, notes crossed', podend_body(True), css=end_css + note_css)
LV.mark('V5PodEndNotes', replace=[('18 MINUTES · 42 MESSAGES · 0 KEPT', '{{stats}}')])

# ---------------- GROUP ROOM (tonight's question) ----------------
def person(name, state, me=False):
    wave = ('<svg width="44" height="18" viewBox="0 0 44 18" aria-hidden="true"><path class="talkwave" d="M0 9 Q4 1 8 9 T16 9 T24 9 T32 9 T40 9" fill="none" stroke="#E08A3C" stroke-width="2" stroke-linecap="round"/></svg>'
            if state == 'speaking' else '')
    col = INK if state != 'muted' else PENCIL
    return (f'<div style="display:flex;align-items:center;justify-content:space-between;height:46px;border-bottom:1px dashed {RULE}">'
            f'<span style="{HAND};font-size:26px;color:{col}">{name}{" (you)" if me else ""}</span>'
            f'<span style="display:flex;align-items:center;gap:10px;{TYPE};font-size:10px;letter-spacing:.16em;color:{"#C0662A" if state == "speaking" else PENCIL}">{wave}{state.upper()}</span></div>')
room = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 24)}<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">6 OF 8 · 2 SEATS OPEN</span></div>
<div style="margin-top:10px">{person('neon_moth', 'speaking')}{person('paper_kite', 'listening')}{person('static_heron', 'listening')}{person('dusk_signal', 'muted')}{person('lowkey_comet', 'listening')}{person('quiet_otter', 'listening', me=True)}</div>
<div style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL};margin-top:16px;line-height:1.8">LET PEOPLE FINISH · LEAVING IS ALWAYS OKAY</div>''',
    520, 410, rot=1.2, kind='kraft', seed=561, pad='30px 36px', tapes=tape(200, -13, 110, 28, rot=-3, seed=56))
group_css = """.talkwave{stroke-dasharray:8 4;animation:tw .6s linear infinite}@keyframes tw{to{stroke-dashoffset:-24}}"""
group = f'''
{atmos(leak(-220, -200, 560) + leak(1100, 600, 520, ROSE, 4) + '<div class="flare"></div>')}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb="tonight's question")}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:80px;padding:40px 0 0">
<div style="display:flex;flex-direction:column;gap:30px;align-items:flex-start">
<div class="rise" style="--w:.2s">{polaroid('moon', 380, 260, "What's something you pretend doesn't bother you?", rot=-2.5, seed=562, u='gq', capsize=30)}</div>
<div class="rise" style="--w:1.2s;display:flex;align-items:center;gap:30px;margin-left:10px">{chip('join with voice', 'V5Pod.dc.html', seed=563, w=220)}{link('just listen', 'V5Pod.dc.html')}</div>
</div>
<div class="rise" style="--w:.6s">{room}</div>
</main>'''
page('V5Question', "Tonight's question", group, css=group_css)
LV.mark('V5Question', slots=[('<div class="rise" style="--w:.6s">', 'qroom'), ('<div class="rise" style="--w:1.2s;display:flex;align-items:center;gap:30px;margin-left:10px">', 'qbtns')],
        replace=[("What's something you pretend doesn't bother you?", '{{question}}')])

# ---------------- PODS ASLEEP ----------------
sr = random.Random(3)
stars = ''.join(f'<path class="tw" style="animation-delay:{sr.uniform(0, 4):.1f}s" d="M{x} {y - s} V{y + s} M{x - s} {y} H{x + s}" stroke="{CHALK}" stroke-width="1.4" stroke-linecap="round"/>'
                for x, y, s in [(sr.uniform(40, 1400), sr.uniform(20, 380), sr.uniform(3, 7)) for _ in range(26)])
asleep_css = """.tw{animation:tw 3.6s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:.9}}"""
def scrap_link(text, feat, href, rot, seed, kind=''):
    inner = f'<div style="{HAND};font-size:24px;color:{INK};white-space:nowrap">{text}</div><div style="{TYPE};font-size:10px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>'
    return f'<a href="{href}" class="chip" style="display:block">{paper(inner, 270, 112, rot=rot, seed=seed, kind=kind, pad="18px 24px")}</a>'
asleep = f'''
<svg aria-hidden="true" width="1440" height="420" style="position:absolute;left:0;top:60px;z-index:2">{stars}
<path class="draw" style="--len:400;--d:2s" d="M1110 70 A70 70 0 1 0 1180 190 A56 56 0 1 1 1110 70 Z" fill="rgba(237,230,216,.08)" stroke="{CHALK}" stroke-width="2"/></svg>
{atmos(leak(980, -200, 520, DAWN, 0, op=None) + leak(-220, 640, 460, ROSE, 5))}
{topbar(right='PODS OPEN AT 10PM')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding-bottom:40px">
<div class="fadein" style="--w:.2s">{rabbit(170, CHALK, mood='sleep', uid='asl')}</div>
{h_hand("Everyone's asleep.", 72, wait='.6s')}
<div class="rise" style="--w:1.6s;{SERIF};font-size:22px;color:{BOARDTXT}">Pods open every night at 10. That's in <span style="color:{CHALK}">1 hour 42 minutes</span>.</div>
<div class="rise" style="--w:2s;display:flex;align-items:center;gap:16px;margin-top:8px;{TYPE};font-size:11px;letter-spacing:.14em;color:{BOARDTXT}">
<span>EMAIL ME AT 10PM</span><span style="width:240px;border-bottom:1px solid {SOOT};height:16px"></span><a href="#" class="ul" style="color:{CHALK}">REMIND ME</a><span style="color:{BOARDTXT}">· OPTIONAL · DELETED ONCE IT SENDS</span></div>
<div class="rise" style="--w:2.4s;margin-top:34px;display:flex;flex-direction:column;align-items:center;gap:18px">
<div style="{MARK};font-size:24px;color:#F0A08F">until then</div>
<div style="display:flex;gap:26px">{scrap_link('get it out', 'BURN', 'V5Burn.dc.html', -2, 571)}{scrap_link('leave it somewhere', 'ECHOES', 'V5Echoes.dc.html', 1.5, 572, 'kraft')}{scrap_link('write it, don\'t send', 'UNSENT', 'V5UnsentWrite.dc.html', .8, 574, 'kraft')}{scrap_link('hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', -1, 573)}</div></div>
</main>'''
page('V5Asleep', 'Pods asleep', asleep, css=asleep_css)

# ---------------- HELP ----------------
help_css = """
.breath{transform-origin:center;animation:br 14s ease-in-out infinite}
@keyframes br{0%{transform:scale(.7);opacity:.6}28.6%{transform:scale(1);opacity:1}57.1%{transform:scale(1);opacity:1}100%{transform:scale(.7);opacity:.6}}
.ph{position:absolute;left:0;right:0;text-align:center;opacity:0;animation:14s linear infinite}
.p1{animation-name:p1}.p2{animation-name:p2}.p3{animation-name:p3}
@keyframes p1{0%,26%{opacity:1}28.6%,100%{opacity:0}}@keyframes p2{0%,28%{opacity:0}30%,55%{opacity:1}57.1%,100%{opacity:0}}@keyframes p3{0%,57%{opacity:0}59%,97%{opacity:1}100%{opacity:0}}
.glowring{position:absolute;inset:-60px;border-radius:50%;background:radial-gradient(circle,rgba(255,200,140,.28),transparent 65%);animation:br 14s ease-in-out infinite}
"""
PHONEI = '<path d="M5 2.5h2.2l1.2 3-1.6 1.1a8 8 0 0 0 3.6 3.6l1.1-1.6 3 1.2V12a1.6 1.6 0 0 1-1.6 1.6A10.6 10.6 0 0 1 3.4 4.1 1.6 1.6 0 0 1 5 2.5z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
GLOBEI = '<circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2.5 8.5h12M8.5 2.5c-2.2 2.4-2.2 9.6 0 12M8.5 2.5c2.2 2.4 2.2 9.6 0 12" fill="none" stroke="currentColor" stroke-width="1.3"/>'
def callrow(k, name, detail, href, icon=PHONEI, color=INK, last=False):
    """Same row as the phone help (v5m_capcare.mcall): hand name, type sub-line, icon + number."""
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    return (f'<a href="{href}"{ext} class="row" style="min-height:76px;padding:10px 2px;{bb}gap:16px">'
            f'<span style="display:flex;flex-direction:column;gap:3px;min-width:0"><span style="{HAND};font-size:28px;line-height:1.2;color:{color}">{name}</span>'
            f'<span style="{TYPE};font-size:10.5px;letter-spacing:.12em;line-height:1.4;color:{PENCIL}">{detail}</span></span>'
            f'<span class="go" style="flex-shrink:0;display:flex;align-items:center;gap:9px;{TYPE};font-weight:700;font-size:14px;letter-spacing:.12em;color:{color}">'
            f'<svg width="18" height="18" viewBox="0 0 17 17" aria-hidden="true">{icon}</svg>{k}</span></a>')
numbers = paper(f'''
{t_mark('people who pick up', 24)}
<div style="margin-top:8px;border-top:1px dashed {RULE}">
{callrow('14416', 'Tele-MANAS', 'FREE · 24/7 · MANY INDIAN LANGUAGES', 'tel:14416')}
{callrow('112', 'Emergency', 'POLICE · AMBULANCE · FIRE', 'tel:112', color=RED)}
{callrow('FIND', 'Outside India', 'FINDAHELPLINE.COM · CALL, TEXT, CHAT', 'https://findahelpline.com', icon=GLOBEI, last=True)}
</div>
<div style="{SERIF};font-style:italic;font-size:17px;color:{PENCIL};margin-top:4px;line-height:1.5;border-top:1px dashed {RULE};padding-top:14px">The people here are kind strangers, not professionals. The people on these lines are trained, and they won't judge you.</div>''',
    540, 414, rot=-.8, seed=581, pad='34px 40px 28px', tapes=tape(210, -14, 110, 28, rot=3, seed=58))
helpp = f'''
{atmos(leak(-220, -220, 600, GLOW, 0) + leak(1120, 560, 520, ROSE, 3))}
{topbar(crumb='help')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:110px;padding-bottom:40px">
<div style="display:flex;flex-direction:column;gap:30px;width:520px">
{h_hand("You don't have to carry this alone.", 58, d='2s')}
<div style="display:flex;align-items:center;gap:40px;margin-top:20px">
<div style="position:relative;width:200px;height:150px;display:flex;align-items:center;justify-content:center"><div class="glowring"></div><div class="breath">{rabbit(170, CHALK, uid='hl', blink=False)}</div></div>
<div style="display:flex;flex-direction:column;gap:8px">
<div style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">NEED A MINUTE FIRST?</div>
<div style="position:relative;height:40px;width:220px;{HAND};font-size:32px;color:{CHALK}"><span class="ph p1" style="text-align:left">breathe in…</span><span class="ph p2" style="text-align:left">hold…</span><span class="ph p3" style="text-align:left">and let it go.</span></div>
<div style="{SERIF};font-size:17px;color:{BOARDTXT};line-height:1.5">Breathe with the rabbit. In as it grows, out as it settles.</div></div>
</div>
<div class="rise" style="--w:1.4s;margin-top:6px">{link('← back to where I was', 'V5Home.dc.html', CHALK, 12)}</div></div>
<div class="rise" style="--w:.6s">{numbers}</div>
</main>'''
page('V5Help', 'Need help now', helpp, css=help_css)

# ---------------- REPORTED ----------------
rep = paper(f'''
{h_hand('Sorry about that.', 50, color=INK)}
<div class="rise" style="--w:1.1s;{HAND};font-size:34px;color:{INK};margin-top:2px">You did the right thing.</div>
<div class="rise" style="--w:1.5s;{SERIF};font-size:20px;line-height:1.6;color:{INK};margin-top:18px">The pod ended the moment you reported. They only see that it closed, never who left or why.</div>
<div class="rise" style="--w:1.8s;margin-top:22px;display:grid;grid-template-columns:150px 1fr;row-gap:10px;{TYPE};font-size:12px;letter-spacing:.1em;color:{INK}">
<span style="color:{PENCIL}">YOUR PLACE</span><span>FRONT OF THE LINE</span><span style="color:{PENCIL}">THEM</span><span>2–3 REPORTS CLOSE THEIR DOOR FOR THE NIGHT</span><span style="color:{PENCIL}">KEPT</span><span>NOTHING</span></div>
<div class="rise" style="--w:2.2s;display:flex;align-items:center;gap:30px;margin-top:30px">{tchip('find someone else', 'V5Matching.dc.html', 'ink', 260, 54, 591)}<a href="V5Home.dc.html" class="ul" style="{TYPE};font-size:12px;letter-spacing:.16em;color:{INK}">NOT RIGHT NOW</a></div>''',
    700, 470, rot=-.8, seed=592, pad='50px 56px', tapes=tape(290, -15, 120, 30, rot=-3, seed=59))
reported = f'''
{atmos(leak(1100, -200, 560) + leak(-200, 600, 480, ROSE, 4))}
{topbar(crumb='talk pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:70px;padding-bottom:40px">
<div class="rise" style="--w:.1s">{rep}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:16px">{rabbit(120, CHALK, uid='rp')}<div style="{HAND};font-size:24px;color:{BOARDTXT};text-align:center">the chat is wiped.<br>your words left with you.</div></div>
</main>'''
page('V5Reported', 'Reported', reported)

# ---------------- WHAT WE KEEP (receipt) ----------------
def item(k, v, vc=INK, bold=False):
    return (f'<div style="display:flex;align-items:baseline;gap:8px;{TYPE};font-size:13px;letter-spacing:.06em;line-height:1.5;margin:7px 0">'
            f'<span style="color:{PENCIL};white-space:nowrap">{k}</span>'
            f'<span aria-hidden="true" style="flex-grow:1;min-width:16px;border-bottom:1.5px dotted {RULE}"></span>'
            f'<span style="color:{vc};white-space:nowrap;{"font-weight:700;" if bold else ""}">{v}</span></div>')
receipt = paper(f'''
<div style="text-align:center;{TYPE};font-weight:700;font-size:14px;letter-spacing:.3em">N0TRACE</div>
<div style="text-align:center;{TYPE};font-size:10px;letter-spacing:.2em;color:{PENCIL};margin-top:4px">WHAT WE KEEP · RECEIPT</div>
<div style="border-top:1.5px dashed {RULE};margin:16px 0 8px"></div>
{item('BURN', 'YOUR DEVICE · GONE WHEN BURNT')}{item('ECHOES + UNSENT', 'OUR MEMORY · 24H')}{item('POD MESSAGES', 'NEVER STORED')}{item('VOICE', 'PEER TO PEER · NEVER RECORDED')}
{item('CAPSULE', 'YOUR BROWSER ONLY')}{item('CAPSULE EMAIL', 'DELETED ONCE SENT')}{item('QUESTION EMAIL', 'UNTIL YOU UNSUBSCRIBE')}{item('REPORTS', 'A COUNT · GONE BY MORNING')}
<div style="border-top:1.5px dashed {RULE};margin:12px 0 8px"></div>
{item('YOUR NAME', 'THIS DEVICE, IF YOU ASK')}{item('TOTAL KEPT', 'NOTHING', INK, True)}
<div style="text-align:center;{HAND};font-size:26px;margin-top:20px">thank you for trusting us.</div>''',
    470, 492, rot=1.4, kind='hi', seed=601, pad='34px 36px', torn='bottom')
privacy = f'''
{atmos(leak(-200, -200, 560) + leak(1150, 600, 460, ROSE, 4))}
{topbar(crumb='what we keep')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:110px;padding-bottom:20px">
<div style="width:440px;display:flex;flex-direction:column;gap:22px">
{h_hand('Almost nothing, and never for long.', 56, d='2s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:20px;line-height:1.6;color:{BOARDTXT}">No accounts. No trackers. No ads. If the server restarts, everything in memory is gone. Nothing was saved, so nothing is lost.</div>
<div class="rise" style="--w:1.6s">{link('← back home', 'V5Home.dc.html')}</div></div>
<div class="printout">{receipt}</div>
</main>'''
page('V5Privacy', 'What we keep', privacy, css=""".printout{animation:print 1.8s cubic-bezier(.3,.8,.3,1) .3s both;clip-path:inset(0 0 100% 0)}@keyframes print{to{clip-path:inset(-40px -40px -40px -40px)}}""")
print('talk ok')
