"""N0TRACE V5 — edge-case system moments (desktop + phone).
Boards: V5SomethingBroke, V5Loading, V5NoVoice, V5StorageBlocked, V5WelcomeBack, V5SlowDown (+ V5M twins).
Does not import any other screen module: the home layout is copied here so no existing board is rewritten."""
from gen5 import *
import json, os, random, math

W = MW - 2 * MPAD          # 346, phone paper width
NAME = 'quiet_otter'
VEIL = '<div aria-hidden="true" style="position:absolute;inset:0;z-index:60;background:rgba(6,6,7,.78)"></div>'
BOARDS = []

def board(name, title, w, h, row):
    BOARDS.append({"file": name + '.dc.html', "title": title, "w": w, "h": h, "row": row})

EDGE_CSS = f"""
.write{{text-wrap:balance}}
.sway{{transform-origin:50% 0;animation:sway 7s ease-in-out infinite}}
@keyframes sway{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(1deg)}}}}
.peel{{transform-origin:0 50%;animation:peel 5.5s ease-in-out infinite}}
@keyframes peel{{0%,100%{{transform:rotate(-24deg)}}50%{{transform:rotate(-31deg)}}}}
.cornerfall{{animation:cornerfall 1.4s cubic-bezier(.3,1.1,.5,1) .5s both}}
@keyframes cornerfall{{from{{opacity:0;transform:translate(-30px,-60px) rotate(-30deg)}}to{{opacity:1}}}}
.pindrop{{animation:pindrop .9s cubic-bezier(.3,1.4,.5,1) var(--w,.5s) both}}
@keyframes pindrop{{0%{{opacity:0;transform:translateY(-26px) scale(1.5)}}60%{{opacity:1}}100%{{opacity:1;transform:none}}}}
.notein{{animation:notein 1.1s cubic-bezier(.25,.9,.3,1) .15s both}}
@keyframes notein{{from{{opacity:0;transform:translateY(-16px) rotate(-3deg)}}to{{opacity:1;transform:none}}}}
.tapeon{{animation:tapeon .55s cubic-bezier(.3,1.3,.5,1) var(--w,.9s) both}}
@keyframes tapeon{{from{{opacity:0;transform:translateY(-10px) scale(1.18)}}to{{opacity:1;transform:none}}}}
.loopwrite{{clip-path:inset(-30% 100% -30% -2%);animation:loopwrite 5.6s cubic-bezier(.5,.1,.3,1) 1.3s infinite}}
@keyframes loopwrite{{0%{{clip-path:inset(-30% 100% -30% -2%);opacity:1}}36%,78%{{clip-path:inset(-30% -3% -30% -2%);opacity:1}}92%{{clip-path:inset(-30% -3% -30% -2%);opacity:0}}100%{{clip-path:inset(-30% 100% -30% -2%);opacity:0}}}}
.blinkeyes{{transform-box:fill-box;transform-origin:center;animation:blinkeyes 3.2s ease-in-out 1.2s infinite}}
@keyframes blinkeyes{{0%,86%,100%{{transform:scaleY(1)}}91%{{transform:scaleY(.1)}}}}
.breath{{transform-box:fill-box;transform-origin:center;animation:breath 8s ease-in-out infinite}}
@keyframes breath{{0%,100%{{transform:scale(.6)}}45%,55%{{transform:scale(1)}}}}
.breathtxt{{animation:breathtxt 8s ease-in-out infinite}}
@keyframes breathtxt{{0%,100%{{opacity:.55}}50%{{opacity:1}}}}
.drain{{stroke-dasharray:var(--len);stroke-dashoffset:0;animation:drain 30s linear 1.4s forwards}}
@keyframes drain{{to{{stroke-dashoffset:var(--len)}}}}
.slipdown{{animation:slipdown 1s cubic-bezier(.3,1.25,.5,1) var(--w,.9s) both}}
@keyframes slipdown{{from{{opacity:0;transform:translateY(-22px) rotate(-5deg)}}to{{opacity:1}}}}
.drip{{animation:drip 4s ease-in 2.4s infinite}}
@keyframes drip{{0%,55%{{opacity:0;transform:translateY(-3px)}}65%{{opacity:1}}90%{{opacity:1;transform:translateY(5px)}}100%{{opacity:0;transform:translateY(7px)}}}}
.stdots i{{display:inline-block;width:5px;height:5px;margin-right:4px;border-radius:50%;background:currentColor;animation:stdot 1.8s ease-in-out infinite}}
.stdots i:nth-child(2){{animation-delay:.25s}}.stdots i:nth-child(3){{animation-delay:.5s}}
@keyframes stdot{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
"""

# ---------------------------------------------------------------- shared atoms
def jag(x0, y0, x1, y1, amp, step, r):
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / step))
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    return [(x0 + dx * i / n + nx * r.uniform(-amp, amp), y0 + dy * i / n + ny * r.uniform(-amp, amp)) for i in range(n)]

def poly(pts, ox=0, oy=0):
    return 'polygon(' + ','.join(f'{x - ox:.1f}px {y - oy:.1f}px' for x, y in pts) + ')'

def torn_note(inner, w, h, cut=110, rot=0, kind='', seed=1, pad='40px', tapes='', corner_at=None, corner_rot=24):
    """A note whose top-right corner has torn away; the torn corner lies on the board at corner_at (x, y)."""
    r = random.Random(seed)
    diag = [(w - cut, 0)] + jag(w - cut, 0, w, cut, 4.5, 7, r)[1:] + [(w, cut)]
    pts = jag(0, 0, w - cut, 0, 2.2, 16, r) + diag + jag(w, cut, w, h, 2.2, 16, r) + jag(w, h, 0, h, 2.2, 16, r) + jag(0, h, 0, 0, 2.2, 16, r)
    note = (f'<div class="lift" style="position:relative;width:{w}px;height:{h}px;transform:rotate({rot}deg);flex-shrink:0">'
            f'<div class="paper {kind}" style="position:absolute;inset:0;padding:{pad};clip-path:{poly(pts)}">{inner}</div>{tapes}')
    if corner_at:
        cpts = [(w - cut, 0), (w, 0), (w, cut)] + list(reversed(diag[1:-1]))
        cx, cy = corner_at
        note += (f'<div class="cornerfall" style="position:absolute;left:{cx}px;top:{cy}px;width:{cut}px;height:{cut}px">'
                 f'<div class="lift" style="width:{cut}px;height:{cut}px;transform:rotate({corner_rot}deg)">'
                 f'<div class="paper {kind}" style="position:absolute;inset:0;clip-path:{poly(cpts, w - cut, 0)}">'
                 f'<div style="position:absolute;left:{cut * .3:.0f}px;top:{cut * .2:.0f}px;width:{cut * .5:.0f}px;height:2px;background:{RULE}"></div></div></div></div>')
    return note + '</div>'

def half_tape(x, y, w=60, h=28, rot=-4, seed=7):
    """Tape come half off: one half stuck, the other lifted and curling."""
    r = random.Random(seed)
    lft = [(r.uniform(0, 4), i * h / 6) for i in range(7)]
    stuck = 'polygon(' + ','.join(f'{a:.1f}px {b:.1f}px' for a, b in lft) + f',{w}px {h}px,{w}px 0px)'
    rgt = [(w - r.uniform(0, 4), h - i * h / 6) for i in range(7)]
    lifted = f'polygon(0px 0px,0px {h}px,' + ','.join(f'{a:.1f}px {b:.1f}px' for a, b in rgt) + ')'
    return (f'<span aria-hidden="true" style="position:absolute;left:{x}px;top:{y}px;width:{2 * w}px;height:{h}px;transform:rotate({rot}deg);z-index:6">'
            f'<span class="tape" style="left:0;top:0;width:{w}px;height:{h}px;clip-path:{stuck}"></span>'
            f'<span class="peel" style="position:absolute;left:{w - 1}px;top:0;width:{w}px;height:{h}px;filter:drop-shadow(0 10px 6px rgba(0,0,0,.4))">'
            f'<span class="tape" style="left:0;top:0;width:{w}px;height:{h}px;background-color:rgba(214,198,160,.82);clip-path:{lifted};box-shadow:none"></span></span></span>')

def pushpin(size=18, col=RED):
    r = size / 2
    return (f'<svg width="{size + 10}" height="{size + 10}" viewBox="0 0 {size + 10} {size + 10}" aria-hidden="true" style="overflow:visible;display:block">'
            f'<ellipse cx="{r + 6:.1f}" cy="{r + 8:.1f}" rx="{r + 1:.1f}" ry="{r * .6:.1f}" fill="#000" opacity=".45"/>'
            f'<circle cx="{r + 2:.1f}" cy="{r + 2:.1f}" r="{r:.1f}" fill="{col}"/><circle cx="{r + 2:.1f}" cy="{r + 2:.1f}" r="{r:.1f}" fill="none" stroke="#000" stroke-opacity=".35"/>'
            f'<circle cx="{r - .8:.1f}" cy="{r - .8:.1f}" r="{r * .3:.1f}" fill="#fff" opacity=".3"/></svg>')

def type_link(label, href, color=INK, size=12, bold=False):
    return (f'<a href="{href}" class="ul" style="{TYPE};{"font-weight:700;" if bold else ""}font-size:{size}px;letter-spacing:.16em;'
            f'text-transform:uppercase;color:{color};white-space:nowrap">{label}</a>')

def status_line(text, size=11, color=PENCIL):
    return (f'<div role="status" style="display:flex;align-items:center;gap:10px;{TYPE};font-size:{size}px;letter-spacing:.16em;color:{color}">'
            f'<span class="stdots" aria-hidden="true"><i></i><i></i><i></i></span>{text}</div>')

def sheepish_rabbit(w=120, color=CHALK, uid='sh', blush=SOFTRED):
    """The rabbit, a bit embarrassed: lids half down, eyes glancing aside, a wobbly mouth, a little sweat drop."""
    h = int(w * .75)
    f = f'<filter id="rough{uid}" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>'
    body = (f'<path d="M14 27 L45 25 L46 41 L15 42 Z" fill="{color}"/>'
            f'<path d="M73 25 L104 27 L103 42 L73 41 Z" fill="{color}"/>'
            f'<path d="M12 21 L47 18" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M72 18 L106 22" stroke="{color}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M48 68 Q53 63 58 68 T68 68 T76 67" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="M18 52 l5 -6 M26 53 l5 -6 M34 53 l5 -6 M80 53 l5 -6 M88 53 l5 -6 M96 52 l5 -6" stroke="{blush}" stroke-width="2" stroke-linecap="round" opacity=".85"/>')
    drop = (f'<g class="drip"><path d="M114 4 C111 10 109 13 109 16 a5 5 0 0 0 10 0 C119 13 117 10 114 4 Z" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/></g>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 120 90" aria-hidden="true" style="overflow:visible">'
            f'<defs>{f}</defs><g filter="url(#rough{uid})">{body}</g>{drop}</svg>')

def desk_page(main, crumb='', right='', extra=''):
    return f'''
{atmos()}
{topbar(right=right, crumb=crumb)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:80px;padding-bottom:40px">
{main}
</main>{extra}
{footer()}'''

def phone_page(main, crumb='', right=None, foot=True, center=False):
    jc = 'justify-content:center;padding-bottom:40px;' if center else ''
    return f'''
{matmos()}
{mtopbar(crumb=crumb, right=right)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;{jc}">
{main}
</main>
{mfooter() if foot else ''}'''

def m_right(t, col=BOARDTXT):
    return f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{col}">{t}</span>'

# ---------------------------------------------------------------- phone frame (gen5: mbody / msheet / mdock)
def ctape(w=110, h=28, rot=-3, seed=1, y=-13):
    """A tape centred on a sheet of any width."""
    return f'<span aria-hidden="true" style="position:absolute;left:50%;top:0;margin-left:{-w / 2:.0f}px;width:{w}px;height:0;z-index:6">{tape(0, y, w, h, rot=rot, seed=seed)}</span>'

def grow(sheet, wait='.1s'):
    """Wrap the main sheet so it can grow to meet the dock."""
    return f'<div class="rise" style="--w:{wait};flex:1 1 auto;min-height:0;display:flex;flex-direction:column">{sheet}</div>'

def dockwrap(dock, wait='2s'):
    return f'<div class="rise" style="--w:{wait};display:flex;flex-direction:column">{dock}</div>'

from v5m_home import fcard
def fitwrap(sheet, wait='.1s', cls=''):
    """Paper as tall as its words, centred in the free space (no empty paper under the message)."""
    return f'<div class="rise {cls}" style="--w:{wait};flex:0 0 auto;margin:auto 0;display:flex;flex-direction:column">{sheet}</div>'
def fsheet(inner, kind='', seed=1, pad='28px 24px', rot=0, tapes='', minh=0, **k):
    return fcard(inner, kind, seed, pad, rot, tapes)

def middle(inner, align=''):
    """The message block, centred in whatever height the sheet has."""
    return f'<div style="flex:1 0 auto;display:flex;flex-direction:column;justify-content:center;{align}padding:6px 0 14px">{inner}</div>'

def sheet_foot(inner, wait='2.6s', cls='rise'):
    return f'<div class="{cls}" style="--w:{wait};margin-top:auto;padding-top:12px;border-top:1px dashed {RULE}">{inner}</div>'

def mframe(body, dock, crumb='', right=None, foot=True, center=False):
    return f'''
{matmos()}
{mtopbar(crumb=crumb, right=right)}
{mbody(body, center=center)}
{dock}
{mfooter() if foot else ''}'''

def mcard(inner, kind='', seed=1, pad='28px 24px', rot=0, tapes=''):
    """A card as tall as its content (for overlays): deckled, fluid width."""
    return (f'<div class="lift" style="position:relative;width:100%;transform:rotate({rot}deg)">'
            f'<div class="paper {kind}" style="padding:{pad};clip-path:{deckle(320, 300, seed=seed)}">{inner}</div>{tapes}</div>')

def torn_msheet(inner, cut=84, rot=0, kind='', seed=1, pad='30px 26px', tapes='', minh=300):
    """msheet whose top-right corner has torn away; edges are relative so it fills any phone.
    Returns (sheet, corner) -- the corner is the torn-off piece, to lay on the board somewhere."""
    r = random.Random(seed)
    def c(base, d):
        return f'calc({base} {"+" if d >= 0 else "-"} {abs(d):.1f}px)'
    pts = []
    n = 14
    for i in range(n):                       # top, up to the tear
        pts.append(f'{c(f"(100% - {cut}px) * {i / n:.3f}", 0)} {r.uniform(-2.2, 2.2):.1f}px')
    diag = jag(0, 0, cut, cut, 4.5, 7, r)    # the tear (px inside the corner box)
    for x, y in diag:
        pts.append(f'{c("100%", x - cut)} {y:.1f}px')
    for i in range(16):                      # right
        pts.append(f'{c("100%", r.uniform(-2.2, 2.2))} {c(f"{cut}px + (100% - {cut}px) * {i / 16:.3f}", 0)}')
    for i in range(16):                      # bottom
        pts.append(f'{c(f"{100 - 100 * i / 16:.2f}%", 0)} {c("100%", r.uniform(-2.2, 2.2))}')
    for i in range(16):                      # left
        pts.append(f'{r.uniform(-2.2, 2.2):.1f}px {100 - 100 * i / 16:.2f}%')
    clip = 'polygon(' + ','.join(pts) + ')'
    sheet = (f'<div class="lift msheet" style="position:relative;flex:1 1 auto;min-height:{minh}px;width:100%;transform:rotate({rot}deg)">'
             f'<div class="paper {kind}" style="position:absolute;inset:0;padding:{pad};clip-path:{clip};display:flex;flex-direction:column;overflow:hidden">{inner}</div>{tapes}</div>')
    cpts = [(0, 0), (cut, 0), (cut, cut)] + list(reversed(diag[1:]))
    corner = (f'<div class="lift" style="width:{cut}px;height:{cut}px">'
              f'<div class="paper {kind}" style="position:absolute;inset:0;clip-path:{poly(cpts)}">'
              f'<div style="position:absolute;left:{cut * .3:.0f}px;top:{cut * .2:.0f}px;width:{cut * .5:.0f}px;height:2px;background:{RULE}"></div></div></div>')
    return sheet, corner


# ---------------------------------------------------------------- home layout (the real home modules; importing them writes no boards)
from v5_home import home, home_css
from v5m_home import mhome, css as mhome_css
HOME_CSS = home_css + mhome_css


# ================================================================ X11 · SOMETHING BROKE ON OUR SIDE
def broke_inner(phone=False):
    hs, bs, gap = (34, 17.5, 26) if phone else (48, 21, 32)
    home = 'V5MHome.dc.html' if phone else 'V5Home.dc.html'
    head = "That's on us,<br>not you." if phone else "That's on us, not you."
    return f'''
{t_type('something broke on our side', 10 if phone else 11, PENCIL)}
{h_hand(head, hs, color=INK, wait='.5s', extra='margin-top:10px')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:{bs}px;line-height:1.6;color:{INK};margin-top:12px;max-width:470px">Nothing was saved anyway, so nothing is lost. Give it a breath and try again.</div>
<div class="rise" style="--w:1.9s;margin-top:{18 if phone else 20}px">{status_line('TRYING AGAIN ON ITS OWN', 9.5 if phone else 11)}</div>
<div class="rise" style="--w:2.2s;display:flex;align-items:center;{"justify-content:space-between;" if phone else "gap:34px;"}margin-top:{gap}px">
{chip('try again', '#', kind='ink', seed=6201 if phone else 6101, w=164 if phone else 190)}{type_link('back home', home, size=11 if phone else 12)}</div>'''

d_note = torn_note(broke_inner(), 620, 420, cut=120, rot=-.8, seed=6102, pad='48px 54px',
                   tapes=tape(56, -14, 110, 30, rot=-5, seed=611) + half_tape(410, -10, 56, 28, rot=-3, seed=612),
                   corner_at=(600, 446), corner_rot=-18)
d_side = (f'<div class="rise" style="--w:2.6s;display:flex;flex-direction:column;align-items:center;gap:20px;margin-top:70px">'
          f'{sheepish_rabbit(150, CHALK, uid="eb")}<div style="{HAND};font-size:24px;line-height:1.3;color:{BOARDTXT};text-align:center">sorry.<br>we tripped on something.</div></div>')
page('V5SomethingBroke', 'Something broke on our side', desk_page(f'<div class="rise" style="--w:.1s;margin-right:70px">{d_note}</div>{d_side}'), css=EDGE_CSS)
board('V5SomethingBroke', 'X11 — Something broke on our side', 1440, 900, 'edge_sys')

m_broke = f'''{middle(f"""
{t_type('something broke on our side', 10, PENCIL)}
{h_hand("That's on us,<br>not you.", 34, color=INK, wait='.5s', extra='margin-top:10px')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:17.5px;line-height:1.6;color:{INK};margin-top:12px">Nothing was saved anyway, so nothing is lost. Give it a breath and try again.</div>
<div class="rise" style="--w:1.9s;margin-top:18px">{status_line('TRYING AGAIN ON ITS OWN', 9.5)}</div>""")}'''
m_note, m_corner = torn_msheet(m_broke, cut=84, rot=-.5, seed=6202, pad='30px 26px 20px', minh=280,
                               tapes=tape(30, -13, 100, 28, rot=-5, seed=621)
                               + f'<span aria-hidden="true" style="position:absolute;right:{84 + 66}px;top:0;width:0;height:0">{half_tape(0, -9, 44, 26, rot=-3, seed=622)}</span>')
m1 = mframe(f'''<div class="rise" style="--w:2.6s;flex-shrink:0;display:flex;align-items:center;gap:14px;padding:6px 4px 4px">{sheepish_rabbit(64, CHALK, uid="meb")}
<div style="{HAND};font-size:19px;line-height:1.3;color:{BOARDTXT}">sorry.<br>we tripped on something.</div>
<div class="cornerfall" style="margin-left:auto;flex-shrink:0;transform:rotate(30deg)">{m_corner}</div></div>''' + grow(m_note),
            dockwrap(mdock(mcta('try again', '#', 'ink', seed=6201) + mtext('back home', 'V5MHome.dc.html')), '2.2s'))
mpage('V5MSomethingBroke', 'Something broke on our side', m1, css=EDGE_CSS)


# ================================================================ X12 · LOADING (generic loader)
def loader(nw, nh, rw, ts, uid, seed, label='one sec…'):
    rab = rabbit(rw, INK, uid=uid).replace('class="eyes"', 'class="blinkeyes"')
    inner = (f'<div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{int(nh * .08)}px">'
             f'{rab}<div role="status" aria-live="polite" style="position:relative"><div class="loopwrite" style="{HAND};font-size:{ts}px;line-height:1.2;color:{PENCIL};white-space:nowrap;padding:0 4px">{label}</div></div></div>')
    tw = nw * .46
    tp = f'<span class="tapeon" style="position:absolute;left:{nw / 2 - tw / 2:.0f}px;top:-13px;width:{tw:.0f}px;height:28px;z-index:6;--w:.9s">{tape(0, 0, int(tw), 28, rot=-3, seed=seed + 1)}</span>'
    return f'<div class="notein"><div class="sway">{paper(inner, nw, nh, rot=-.6, kind="hi", seed=seed, pad="20px", tapes=tp)}</div></div>'

d2 = f'''
{atmos()}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:34px">
{loader(280, 230, 112, 30, 'ld', 6501)}
<div class="fadein" style="--w:2s">{wordmark(12, BOARDTXT)}</div>
</main>'''
page('V5Loading', 'One sec', d2, css=EDGE_CSS)
board('V5Loading', 'X12 — Loading, one sec', 1440, 900, 'edge_sys')

m2 = f'''
{matmos()}
{mbody(f'<div style="display:flex;flex-direction:column;align-items:center;gap:28px">{loader(232, 196, 92, 26, "mld", 6601)}<div class="fadein" style="--w:2s">{wordmark(11, BOARDTXT)}</div></div>', center=True)}'''
mpage('V5MLoading', 'One sec', m2, css=EDGE_CSS)


# ================================================================ X13 · THIS BROWSER CAN'T DO VOICE
def can_phone(w=300, h=150, color=CHALK, wait='.9s'):
    """Two tin cans; the string between them has come apart and hangs slack."""
    def can(x, y, flip=False):
        s = -1 if flip else 1
        return (f'<path class="draw" style="--len:200;--d:.8s;--w:{wait}" d="M{x} {y} l{s * 4} 46 l{s * 38} 0 l{s * 4} -46" fill="none" stroke="{color}" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>'
                f'<ellipse class="draw" style="--len:160;--d:.7s;--w:{wait}" cx="{x + s * 23}" cy="{y}" rx="23" ry="7" fill="none" stroke="{color}" stroke-width="2.2"/>'
                f'<path d="M{x + s * 8} {y + 18} l{s * 30} 0 M{x + s * 9} {y + 30} l{s * 28} 0" stroke="{color}" stroke-width="1.2" opacity=".45"/>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="overflow:visible">'
            f'{can(10, 40)}{can(w - 10, 40, True)}'
            f'<path class="draw" style="--len:200;--d:1s;--w:1.6s" d="M33 84 C60 120 100 128 128 118 C134 116 136 122 132 128" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<path class="draw" style="--len:200;--d:1s;--w:1.9s" d="M{w - 33} 84 C{w - 60} 124 {w - 100} 130 {w - 132} 122 C{w - 138} 121 {w - 140} 128 {w - 134} 134" fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>'
            f'<path class="draw" style="--len:30;--d:.4s;--w:2.6s" d="M130 128 l-4 6 M132 128 l1 7 M{w - 134} 134 l-3 6 M{w - 134} 134 l3 6" stroke="{color}" stroke-width="1.2" stroke-linecap="round"/></svg>')

def browsers(size=11):
    return (f'<div style="display:flex;gap:10px;flex-wrap:wrap">' +
            ''.join(f'<span style="{TYPE};font-weight:700;font-size:{size}px;letter-spacing:.14em;color:{INK};border:1.5px solid {INK};padding:5px 10px 4px;transform:rotate({rt}deg)">{b}</span>'
                    for b, rt in (('CHROME', -1.5), ('FIREFOX', 1), ('SAFARI', -.5))) + '</div>')

def nv_inner(phone=False):
    hs, bs = (34, 17.5) if phone else (36, 21)
    head = "This browser<br>can't do voice." if phone else "This browser can't do voice."
    href = 'V5MPod.dc.html' if phone else 'V5Pod.dc.html'
    return f'''
{t_type('voice · not here', 10 if phone else 11, PENCIL)}
{h_hand(head, hs, color=INK, wait='.5s', extra='margin-top:10px;white-space:nowrap')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:{bs}px;line-height:1.6;color:{INK};margin-top:12px">Text works just the same. For voice, open N0TRACE in a newer Chrome, Firefox or Safari.</div>
<div class="rise" style="--w:1.9s;margin-top:16px">{browsers(10 if phone else 11)}</div>
<div class="rise" style="--w:2.3s;margin-top:{26 if phone else 32}px;{"display:flex;justify-content:center" if phone else ""}">{chip('continue on text', href, kind='ink', seed=6401 if phone else 6301, w=250 if phone else 260)}</div>'''

nv_note = paper(nv_inner(), 620, 410, rot=.8, seed=6302, pad='46px 54px', tapes=tape(250, -14, 120, 30, rot=3, seed=631))
nv_side = (f'<div class="rise" style="--w:.6s;display:flex;flex-direction:column;align-items:center;gap:18px;margin-top:30px">'
           f'{can_phone()}<div class="fadein" style="--w:3s;{MARK};font-size:25px;line-height:1.2;color:{SOFTRED};text-align:center;transform:rotate(-2deg)">the line\'s a little old.<br>words still get through.</div></div>')
page('V5NoVoice', "This browser can't do voice", desk_page(f'<div class="rise" style="--w:.1s">{nv_note}</div>{nv_side}', crumb='talk pod', right='PODS OPEN · UNTIL 2AM'), css=EDGE_CSS)
board('V5NoVoice', "X13 — This browser can't do voice", 1440, 900, 'edge_sys')

mnv_note = fsheet(f'''{middle(f"""
{t_type('voice · not here', 10, PENCIL)}
{h_hand("This browser<br>can't do voice.", 34, color=INK, wait='.5s', extra='margin-top:10px;white-space:nowrap')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:17.5px;line-height:1.6;color:{INK};margin-top:12px">Text works just the same. For voice, open N0TRACE in a newer Chrome, Firefox or Safari.</div>
<div class="rise" style="--w:1.9s;margin-top:16px">{browsers(10)}</div>""")}
{sheet_foot(f'<div style="{MARK};font-size:21px;line-height:1.2;color:{RED};text-align:center;transform:rotate(-2deg)">words still get through.</div>', '3s', 'fadein')}''',
    rot=.6, seed=6402, pad='30px 26px 18px', minh=300, tapes=ctape(110, 28, rot=3, seed=641))
m3 = mframe(f'''<div class="rise" style="--w:.6s;flex-shrink:0;height:108px;display:flex;justify-content:center"><div style="width:216px;height:108px"><div style="transform:scale(.72);transform-origin:0 0">{can_phone()}</div></div></div>''' + fitwrap(mnv_note),
            dockwrap(mdock(mcta('continue on text', 'V5MPod.dc.html', 'ink', seed=6401)), '2.3s'),
            crumb='talk pod', right=m_right('UNTIL 2AM'))
mpage('V5MNoVoice', "This browser can't do voice", m3, css=EDGE_CSS)


# ================================================================ X14 · PRIVATE WINDOW / STORAGE BLOCKED
def sb_inner(phone=False):
    home = 'V5MHome.dc.html' if phone else 'V5Home.dc.html'
    if phone:
        return f'''
{t_mark('private window?', 21)}
<div class="write" style="--w:.5s;--d:1.4s;{HAND};font-size:27px;line-height:1.25;color:{INK};margin-top:6px">This window forgets<br>when you close it.</div>
<div class="rise" style="--w:1.4s;{SERIF};font-size:17px;line-height:1.55;color:{INK};margin-top:10px">So your remembered name and time capsules won't stick. Everything else works.</div>
<div class="rise" style="--w:2s;margin-top:22px">{chip('okay', home, kind='ink', seed=6803, w=140)}</div>'''
    return f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('private window?', 26)}<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">ON THIS DEVICE</span></div>
<div class="write" style="--w:.5s;--d:1.4s;{HAND};font-size:32px;line-height:1.25;color:{INK};margin-top:10px;white-space:nowrap">This window forgets when you close it.</div>
<div class="rise" style="--w:1.4s;{SERIF};font-size:20px;line-height:1.6;color:{INK};margin-top:12px;max-width:540px">So your remembered name and time capsules won't stick. Everything else works.</div>
<div class="rise" style="--w:2s;margin-top:28px">{chip('okay', home, kind='ink', seed=6703, w=150)}</div>'''

sb_note = paper(sb_inner(), 720, 320, rot=-1, seed=6704, pad='40px 52px', tapes=tape(300, -15, 120, 30, rot=-3, seed=671))
d4 = f'''
<div aria-hidden="true" inert style="position:absolute;inset:0;display:flex;flex-direction:column">{home(False)}</div>
{VEIL}
<div role="dialog" aria-label="Private window" style="position:absolute;z-index:65;inset:0;display:flex;align-items:center;justify-content:center;padding-top:30px">
<div class="rise" style="--w:.2s">{sb_note}</div></div>'''
page('V5StorageBlocked', 'Private window', d4, css=HOME_CSS + EDGE_CSS)
board('V5StorageBlocked', 'X14 — Private window, storage blocked', 1440, 900, 'edge_sys')

msb_note = mcard(f'''
{t_mark('private window?', 21)}
<div class="write" style="--w:.5s;--d:1.4s;{HAND};font-size:27px;line-height:1.25;color:{INK};margin-top:6px">This window forgets<br>when you close it.</div>
<div class="rise" style="--w:1.4s;{SERIF};font-size:17px;line-height:1.55;color:{INK};margin-top:10px">So your remembered name and time capsules won't stick. Everything else works.</div>''',
    rot=-.6, seed=6804, pad='30px 26px 26px', tapes=ctape(110, 28, rot=-3, seed=681))
m4 = f'''
<div aria-hidden="true" inert style="position:absolute;inset:0;display:flex;flex-direction:column">{mhome(False)}</div>
{VEIL}
<div role="dialog" aria-label="Private window" style="position:absolute;z-index:65;inset:0;display:flex;flex-direction:column;justify-content:flex-end;padding-top:64px">
<div class="rise" style="--w:.2s;padding:0 {MPAD}px">{msb_note}</div>
{dockwrap(mdock(mcta('okay', 'V5MHome.dc.html', 'paper', seed=6803), footer=False), '1.8s')}</div>'''
mpage('V5MStorageBlocked', 'Private window', m4, css=HOME_CSS + EDGE_CSS)


# ================================================================ X15 · WELCOME BACK (name remembered)
def welcome_slip(phone=False):
    home = 'V5MHome.dc.html' if phone else 'V5Home.dc.html'
    nm = f'<span style="{TYPE};font-weight:700;letter-spacing:.05em;background:rgba(184,53,42,.12);padding:1px 6px">{NAME}</span>'
    if phone:
        w, h = 300, 78
        inner = (f'<div style="height:100%;display:flex;flex-direction:column;justify-content:center">'
                 f'<div class="write" style="--w:1.4s;--d:1.6s;{HAND};font-size:20px;line-height:1.3;color:{INK};white-space:nowrap">welcome back, <span style="font-size:14px">{nm}</span>.</div>'
                 f'<div class="rise" style="--w:3s;margin-top:6px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL};white-space:nowrap">NOT YOU? '
                 f'<a href="{home}" class="ul" style="color:{INK};font-weight:700">NEW NAME</a></div></div>')
        note = paper(inner, w, h, rot=-1.5, kind='kraft', seed=6911, pad='12px 18px 10px')
    else:
        w, h = 300, 128
        inner = (f'<div style="height:100%;display:flex;flex-direction:column;justify-content:center">'
                 f'<div class="write" style="--w:1.4s;--d:1.4s;{HAND};font-size:28px;line-height:1.25;color:{INK};padding-right:6px">welcome back,</div>'
                 f'<div class="write" style="--w:2.3s;--d:.9s;{TYPE};font-size:19px;color:{INK};margin-top:4px">{nm}.</div>'
                 f'<div class="rise" style="--w:3s;margin-top:12px;{TYPE};font-size:10.5px;letter-spacing:.14em;color:{PENCIL};white-space:nowrap">NOT YOU? '
                 f'<a href="{home}" class="ul" style="color:{INK};font-weight:700">NEW NAME</a></div></div>')
        note = paper(inner, w, h, rot=3, kind='kraft', seed=6901, pad='20px 26px 16px')
    return (f'<div class="slipdown" role="status" style="--w:.9s;position:relative;width:{w}px">{note}'
            f'<div class="pindrop" style="--w:1.5s;position:absolute;left:{w / 2 - 10:.0f}px;top:-8px;z-index:8">{pushpin(16)}</div></div>')

d_greet = f'<div style="position:absolute;z-index:30;right:96px;top:104px">{welcome_slip()}</div>'
page('V5WelcomeBack', 'Welcome back', home(False, greeting=d_greet), css=HOME_CSS + EDGE_CSS)
board('V5WelcomeBack', 'X15 — Welcome back, name remembered', 1440, 900, 'edge_sys')

MWB_H = 890   # the welcome slip pushes tonight's question below the fold: this board scrolls
m_sub = f'<div style="margin:10px 0 2px 2px">{welcome_slip(True)}</div>'
mpage('V5MWelcomeBack', 'Welcome back', mhome(False, sub=m_sub), h=MWB_H, css=HOME_CSS + EDGE_CSS)


# ================================================================ X16 · SLOW DOWN (rate limit)
def breath_timer(size=120, label=15, uid='bt'):
    c = size / 2
    rr = c - 4
    L = 2 * math.pi * rr
    return (f'<div style="position:relative;width:{size}px;height:{size}px;flex-shrink:0">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible">'
            f'<circle cx="{c}" cy="{c}" r="{rr:.1f}" fill="none" stroke="{RULE}" stroke-width="1.4" stroke-dasharray="3 4"/>'
            f'<circle class="drain" style="--len:{L:.0f}" cx="{c}" cy="{c}" r="{rr:.1f}" fill="none" stroke="{INK}" stroke-width="2.2" stroke-linecap="round" transform="rotate(-90 {c} {c})"/>'
            f'<g class="breath"><path d="M{c + 2} 14 C{size - 12} 13 {size - 10} {c + 6} {c + 4} {size - 14} C18 {size - 12} 13 {c + 4} 19 {c - 16} C24 18 {c - 6} 14 {c + 8} 15" fill="rgba(184,53,42,.07)" stroke="{RED}" stroke-width="2" stroke-linecap="round"/></g></svg>'
            f'<div class="breathtxt" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;{HAND};font-size:{label}px;color:{RED}">breathe</div></div>')

def slow_inner(phone=False):
    home = 'V5MHome.dc.html' if phone else 'V5Home.dc.html'
    if phone:
        return f'''
<div style="display:flex;align-items:center;gap:16px">{breath_timer(92, 14)}
<div class="write" style="--w:.6s;--d:1.3s;{HAND};font-size:24px;line-height:1.2;color:{INK}">Let's slow<br>down a second.</div></div>
<div class="rise" style="--w:1.5s;{SERIF};font-size:17px;line-height:1.55;color:{INK};margin-top:14px">A lot of tries, very close together. Take a breath. You can go again in about 30 seconds.</div>
<div class="rise" style="--w:2s;display:flex;align-items:center;justify-content:space-between;margin-top:20px">
{chip('try again', '#', kind='ink', seed=6961, w=150, state='disabled')}{type_link('back home', home, size=11)}</div>
<div class="rise" style="--w:2.3s;margin-top:8px">{inline_note('opens again in a moment', 'pencil', 17)}</div>'''
    return f'''
{t_type('a short pause', 11, PENCIL)}
<div class="write" style="--w:.6s;--d:1.4s;{HAND};font-size:42px;line-height:1.2;color:{INK};margin-top:8px;white-space:nowrap">Let's slow down a second.</div>
<div style="display:flex;align-items:center;justify-content:space-between;gap:30px;margin-top:16px">
<div class="rise" style="--w:1.5s;{SERIF};font-size:20px;line-height:1.6;color:{INK};max-width:420px">A lot of tries, very close together. Take a breath. You can go again in about 30 seconds.</div>
<div class="rise" style="--w:1.2s">{breath_timer(118, 16)}</div></div>
<div class="rise" style="--w:2s;display:flex;align-items:center;gap:30px;margin-top:24px">
{chip('try again', '#', kind='ink', seed=6951, w=170, state='disabled')}{inline_note('opens again in a moment', 'pencil', 20)}
<span style="flex-grow:1"></span>{type_link('back home', home)}</div>'''

slow_note = paper(slow_inner(), 720, 420, rot=-.9, seed=6952, pad='44px 52px', tapes=tape(60, -13, 100, 28, rot=-7, seed=695) + tape(570, -13, 100, 28, rot=6, seed=696))
d6 = desk_page(f'<div class="rise" style="--w:.1s">{slow_note}</div>')
page('V5SlowDown', "Let's slow down a second", d6, css=EDGE_CSS)
board('V5SlowDown', "X16 — Slow down, too many tries", 1440, 900, 'edge_sys')

mslow_note = fsheet(f'''{middle(f"""
<div style="display:flex;align-items:center;gap:16px">{breath_timer(92, 14)}
<div class="write" style="--w:.6s;--d:1.3s;{HAND};font-size:24px;line-height:1.2;color:{INK}">Let's slow<br>down a second.</div></div>
<div class="rise" style="--w:1.5s;{SERIF};font-size:17px;line-height:1.55;color:{INK};margin-top:14px">A lot of tries, very close together. Take a breath. You can go again in about 30 seconds.</div>
<div class="rise" style="--w:2.3s;margin-top:10px">{inline_note('opens again in a moment', 'pencil', 17)}</div>""")}
{sheet_foot(f'<div style="{MARK};font-size:20px;line-height:1.2;color:{RED};text-align:center;transform:rotate(-2deg)">nobody\'s in trouble. just a breath.</div>', '3s', 'fadein')}''',
    rot=-.6, seed=6962, pad='30px 24px 18px', minh=300, tapes=tape(24, -12, 86, 26, rot=-7, seed=697)
    + f'<span aria-hidden="true" style="position:absolute;right:112px;top:0;width:0;height:0">{tape(0, -12, 86, 26, rot=6, seed=698)}</span>')
m6 = mframe(fitwrap(mslow_note),
            dockwrap(mdock(mcta('try again', '#', 'ink', seed=6961, state='disabled') + mtext('back home', 'V5MHome.dc.html')), '2s'))
mpage('V5MSlowDown', "Let's slow down a second", m6, css=EDGE_CSS)


# ---------------------------------------------------------------- manifest (desktop, then phone twins)
for n, t in [('SomethingBroke', 'MX11 — Something broke on our side'), ('Loading', 'MX12 — Loading, one sec'),
             ('NoVoice', "MX13 — This browser can't do voice"), ('StorageBlocked', 'MX14 — Private window, storage blocked'),
             ('WelcomeBack', 'MX15 — Welcome back, name remembered (scrolls)'), ('SlowDown', 'MX16 — Slow down, too many tries')]:
    board('V5M' + n, t, MW, MWB_H if n == 'WelcomeBack' else MH, 'm_edge_sys')
json.dump(BOARDS, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest_edge_sys.json'), 'w'), ensure_ascii=False, indent=1)
print('edge_sys ok')
