"""N0TRACE V5 — system moments (desktop). Boards: V5MicAsk, V5MicBlocked, V5Offline, V5Reconnect, V5NotFound."""
from gen5 import *
import json, os

# ---------- local atoms ----------
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
LOCK = '<path d="M4 8h8v6.5H4zM5.8 8V5.6a2.2 2.2 0 0 1 4.4 0V8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
RELOAD = '<path d="M13 8.5a5 5 0 1 1-1.5-3.6M13 2.5v3h-3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'

def ic(icon, size=16, extra=''):
    return f'<svg width="{size}" height="{size + 1}" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0;{extra}">{icon}</svg>'

def fact_grid(rows, cols='150px 1fr', size=12):
    out = ''.join(f'<span style="color:{PENCIL}">{k}</span><span style="color:{vc}">{v}</span>' for k, v, vc in rows)
    return f'<div style="display:grid;grid-template-columns:{cols};row-gap:10px;{TYPE};font-size:{size}px;letter-spacing:.1em;color:{INK}">{out}</div>'

def long_arrow(d, head, color='#F0A08F', wait='1.6s', length=520, sw=2.2):
    """A hand-drawn pointer: a loose stroke plus an arrowhead, drawn on after the note lands."""
    return (f'<path class="draw" style="--len:{length};--d:1.1s;--w:{wait}" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path class="draw" style="--len:60;--d:.4s;--w:calc({wait} + 1s)" d="{head}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')

SYS_CSS = f"""
.write{{text-wrap:balance}}
.sway{{transform-origin:50% 0;animation:sway 7s ease-in-out infinite}}
@keyframes sway{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(1deg)}}}}
.dots i{{display:inline-block;width:5px;height:5px;margin-right:4px;border-radius:50%;background:currentColor;animation:dot 1.8s ease-in-out infinite}}
.dots i:nth-child(2){{animation-delay:.25s}}.dots i:nth-child(3){{animation-delay:.5s}}
@keyframes dot{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.step{{opacity:0;animation:rise 1s cubic-bezier(.2,.7,.2,1) var(--w) forwards;transform:translateY(8px)}}
.veil{{position:absolute;inset:0;background:rgba(6,6,7,.78);z-index:60;animation:fadein .8s ease both}}
.holdnote{{position:absolute;left:50%;top:50%;z-index:61;transform:translate(-50%,-50%);animation:hold .9s cubic-bezier(.3,1.25,.5,1) .4s both}}
@keyframes hold{{from{{opacity:0;transform:translate(-50%,-44%) rotate(-4deg)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
.loop{{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:loopdraw 4.8s cubic-bezier(.45,.05,.4,1) infinite}}
@keyframes loopdraw{{0%{{stroke-dashoffset:var(--len);opacity:1}}55%{{stroke-dashoffset:0;opacity:1}}80%{{stroke-dashoffset:0;opacity:0}}100%{{stroke-dashoffset:var(--len);opacity:0}}}}
.scrapfall{{animation:scrapfall 1.2s cubic-bezier(.3,1.1,.5,1) .2s both}}
@keyframes scrapfall{{from{{opacity:0;transform:translateY(-14px) rotate(-8deg)}}to{{opacity:1}}}}
.flutter{{transform-origin:50% 0;animation:flutter 5s ease-in-out infinite}}
@keyframes flutter{{0%,100%{{transform:rotate(-1.5deg)}}50%{{transform:rotate(2deg)}}}}
"""

def sys_page(main, crumb='', right='', overlay='', svg=''):
    return f'''
{atmos()}
{topbar(right=right, crumb=crumb)}
{svg}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:80px;padding-bottom:56px">
{main}
</main>{overlay}'''

# ================= X01 — before the browser asks for your mic =================
ask_note = paper(f'''
{t_type('before your browser asks', 11, PENCIL)}
{h_hand('Your browser will ask for your mic.', 46, color=INK, wait='.4s', extra='margin-top:10px')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:21px;line-height:1.6;color:{INK};margin-top:16px">It's only so moss_byte can hear you, now that you both said yes. Your voice goes straight between you, and it's never recorded.</div>
<div class="rise" style="--w:1.7s;display:flex;align-items:center;gap:34px;margin-top:34px">
{chip('allow mic', '#', kind='ink', seed=1101, w=190)}
<a href="V5Pod.dc.html" class="ul" style="{TYPE};font-size:12px;letter-spacing:.16em;color:{INK}">STAY ON TEXT</a></div>''',
    620, 430, rot=-1, seed=1102, pad='46px 52px', tapes=tape(250, -14, 120, 30, rot=-3, seed=111))

ask_svg = f'''<svg aria-hidden="true" width="1440" height="900" viewBox="0 0 1440 900" style="position:absolute;inset:0;z-index:20;pointer-events:none;overflow:visible">
{long_arrow('M372 238 C300 214 250 190 214 160 C180 132 160 118 138 100', 'M136 116 L136 98 L154 96', wait='1.9s', length=320)}
</svg>
<div class="fadein" style="--w:2.8s;position:absolute;z-index:20;left:214px;top:96px;{MARK};font-size:25px;line-height:1.1;color:#F0A08F;transform:rotate(-4deg)">it'll pop up<br>about here</div>'''
ask_side = (f'<div class="rise" style="--w:2.2s;display:flex;flex-direction:column;align-items:center;gap:16px;margin-top:40px">'
            f'{rabbit(120, CHALK, uid="xa")}<div style="{HAND};font-size:24px;line-height:1.3;color:{BOARDTXT};text-align:center">just the two of you.<br>nobody else listening.</div></div>')
x01 = sys_page(f'<div class="rise" style="--w:.1s;margin-left:60px">{ask_note}</div>{ask_side}', crumb='talk pod', right='PODS OPEN · UNTIL 2AM', svg=ask_svg)
page('V5MicAsk', 'Before the browser asks for your mic', x01, css=SYS_CSS)

# ================= X02 — mic is blocked =================
def step(n, text, icon, wait):
    return (f'<div class="step" style="--w:{wait};display:flex;align-items:center;gap:16px;padding:12px 0;border-bottom:1px dashed {RULE}">'
            f'<span style="{MARK};font-size:30px;line-height:1;color:{RED};width:22px">{n}</span>'
            f'<span style="display:inline-flex;width:34px;height:34px;align-items:center;justify-content:center;border:1.5px solid {INK};border-radius:50%;color:{INK}">{ic(icon, 17)}</span>'
            f'<span style="{HAND};font-size:27px;line-height:1.2;color:{INK}">{text}</span></div>')
blocked_note = paper(f'''
{t_type('mic is blocked', 11, PENCIL)}
{h_hand("We can't hear you yet.", 46, color=INK, wait='.4s', extra='margin-top:10px')}
<div class="rise" style="--w:1.1s;{SERIF};font-size:20px;line-height:1.55;color:{INK};margin-top:10px">Your browser said no to the mic. Three tiny steps fix it:</div>
<div style="margin-top:12px;border-top:1px dashed {RULE}">
{step(1, 'tap the lock in the address bar', LOCK, '1.5s')}
{step(2, 'find microphone, set it to allow', MIC, '1.9s')}
{step(3, 'reload this page', RELOAD, '2.3s')}</div>
<div class="rise" style="--w:2.8s;display:flex;align-items:center;gap:34px;margin-top:28px">
{chip('reload', '#', kind='ink', seed=1201, w=160)}
<a href="V5Pod.dc.html" class="ul" style="{TYPE};font-size:12px;letter-spacing:.16em;color:{INK}">STAY ON TEXT</a></div>''',
    640, 492, rot=.8, seed=1202, pad='44px 52px', tapes=tape(260, -14, 120, 30, rot=3, seed=121))
blocked_svg = f'''<svg aria-hidden="true" width="1440" height="900" viewBox="0 0 1440 900" style="position:absolute;inset:0;z-index:20;pointer-events:none;overflow:visible">
{long_arrow('M262 236 C220 214 190 180 170 150 C156 128 146 114 134 100', 'M128 116 L132 98 L150 100', wait='3s', length=240)}
</svg>
<div class="fadein" style="--w:3.9s;position:absolute;z-index:20;left:180px;top:104px;{MARK};font-size:25px;line-height:1.1;color:#F0A08F;transform:rotate(-4deg)">the lock {ic(LOCK, 18, 'top:2px;color:#F0A08F')} lives<br>up here</div>'''
blocked_side = (f'<div class="rise" style="--w:2s;display:flex;flex-direction:column;align-items:center;gap:16px;margin-top:40px">'
                f'{rabbit(110, CHALK, uid="xb")}<div style="{HAND};font-size:24px;line-height:1.3;color:{BOARDTXT};text-align:center">no rush.<br>text works just as well.</div></div>')
x02 = sys_page(f'<div class="rise" style="--w:.1s;margin-left:60px">{blocked_note}</div>{blocked_side}', crumb='talk pod', right='PODS OPEN · UNTIL 2AM', svg=blocked_svg)
page('V5MicBlocked', 'Mic is blocked', x02, css=SYS_CSS)

# ================= X03 — lost the signal =================
off_note = paper(f'''
<div style="display:flex;justify-content:center;margin-top:4px">{rabbit(130, INK, mood='sleep', uid='xo')}</div>
{h_hand('Lost the signal.', 52, color=INK, wait='.6s', extra='text-align:center;margin-top:18px')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:21px;line-height:1.6;color:{INK};text-align:center;margin-top:10px">Nothing was saved anyway,<br>so nothing is lost.</div>
<div class="rise" style="--w:2s;display:flex;justify-content:center;align-items:center;gap:10px;margin-top:22px;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">
<span class="dots"><i></i><i></i><i></i></span>TRYING AGAIN ON ITS OWN</div>
<div class="rise" style="--w:2.4s;display:flex;justify-content:center;margin-top:24px"><a href="#" onclick="{{{{retry}}}}" class="ul" style="{TYPE};font-weight:700;font-size:12px;letter-spacing:.16em;color:{INK}">TRY NOW</a></div>''',
    520, 450, rot=-1.2, kind='hi', seed=1302, pad='44px 48px', tapes=tape(205, -14, 110, 30, rot=-3, seed=131))
x03 = f'''
{atmos()}
{topbar(right='<span style="color:#C9BFAE">OFFLINE</span>')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;padding-bottom:56px">
<div class="rise" style="--w:.1s"><div class="sway">{off_note}</div></div>
<div class="fadein" style="--w:3s;{MARK};font-size:25px;color:#F0A08F;transform:rotate(-2deg)">it'll find its way back. you don't have to do anything.</div>
</main>'''
page('V5Offline', 'Lost the signal', x03, css=SYS_CSS)

# ================= X04 — reconnecting, mid pod (dimmed pod underneath) =================
CONVO = [
    ("hey. I'm here. take your time, there's no rush.", False, '11:52'),
    ("I don't even know where to start honestly", True, '11:53'),
    ("that's okay. start anywhere. the middle is fine too.", False, '11:53'),
    ("my best friend moved away last month and I didn't realise how much of my week was just… her.", True, '11:55'),
    ("that sounds really lonely. like the shape of your days changed overnight.", False, '11:56'),
]
def line_msg(text, mine=False, who='moss_byte', t='11:52'):
    if mine:
        return (f'<div style="align-self:flex-end;max-width:74%"><div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px;text-align:right">YOU · {t}</div>'
                f'<span class="hl" style="{SERIF};font-size:19px;line-height:30px;color:{INK}">{text}</span></div>')
    return (f'<div style="align-self:flex-start;max-width:74%;padding-left:16px;border-left:2px solid rgba(184,53,42,.35)"><div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">{who.upper()} · {t}</div>'
            f'<span style="{SERIF};font-size:19px;line-height:30px;color:{INK}">{text}</span></div>')
CW, CH = 880, 724
chat_inner = f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.16) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">11:52 PM · YOU BOTH JOINED · NOTHING HERE IS SAVED</div>
<div style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;padding:18px 6px 14px;overflow:hidden">{''.join(line_msg(a, b, t=c) for a, b, c in CONVO)}</div>
<div style="border-top:1.5px dashed {RULE};padding-top:16px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<span style="{SERIF};font-style:italic;font-size:19px;color:{PENCIL}">say it however it comes out…</span>
<span style="display:flex;align-items:center;gap:22px;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}"><span>ENTER TO SEND</span>{chip('send ↗', '#', kind='ink', seed=533, w=120)}</span></div>
</div>"""
chat_sheet = paper(chat_inner, CW, CH, rot=0.3, kind='hi', seed=534, pad='22px 34px 22px', tapes=tape(CW / 2 - 60, -14, 120, 30, rot=-2, seed=53))
side = paper(f'''
<div style="{HAND};font-size:34px;line-height:1.2">you &amp; moss_byte</div>
<div style="margin-top:8px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">RECONNECTING…</div>
<div style="{MARK};font-size:23px;color:{RED};line-height:1.25;margin-top:20px;transform:rotate(-1.5deg)">no fixing. no judging.<br>you lead.</div>
<div style="border-top:1px dashed {RULE};margin-top:22px;padding-top:18px;display:grid;grid-template-columns:1fr auto;row-gap:10px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">
<span>CHECK-IN AT 10 MIN</span><span style="color:{INK}">06:12</span><span>KEPT</span><span style="color:{RED}">NOTHING</span></div>''',
    300, 360, rot=-1.2, seed=521, pad='30px 30px', tapes=tape(100, -13, 100, 26, rot=-4, seed=52))

def hold_loop(size=120, uid='hl', rabbit_w=72):
    """A pencil circle that slowly draws itself round the rabbit, lets go, and draws again."""
    L = 3.3 * size
    r = size / 2 - 6
    c = size / 2
    d = (f'M{c + 4:.0f} {c - r:.0f} C{c + r * 1.05:.0f} {c - r:.0f} {c + r + 2:.0f} {c + r * .6:.0f} {c + r * .3:.0f} {c + r:.0f} '
         f'C{c - r * .5:.0f} {c + r + 3:.0f} {c - r - 2:.0f} {c + r * .4:.0f} {c - r + 2:.0f} {c - r * .2:.0f} C{c - r * .8:.0f} {c - r * .9:.0f} {c - r * .2:.0f} {c - r - 3:.0f} {c + 10:.0f} {c - r + 1:.0f}')
    return (f'<div style="position:relative;width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible">'
            f'<path class="loop" style="--len:{L:.0f}" d="{d}" fill="none" stroke="{PENCIL}" stroke-width="2.2" stroke-linecap="round"/></svg>'
            f'<div class="breathe">{rabbit(rabbit_w, INK, uid=uid)}</div></div>')

hold_card = paper(f'''
<div style="display:flex;align-items:center;gap:30px">
{hold_loop(128, 'xr', 74)}
<div style="display:flex;flex-direction:column">
<div style="{HAND};font-size:38px;line-height:1.15;color:{INK}">Reconnecting…</div>
<div style="{SERIF};font-size:19px;line-height:1.5;color:{INK};margin-top:8px">We're holding your place<br>for 30 seconds.</div></div></div>
<div style="border-top:1px dashed {RULE};margin-top:22px;padding-top:16px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<span style="{TYPE};font-size:10px;letter-spacing:.14em;line-height:1.6;color:{PENCIL}">IF IT DOESN'T COME BACK, THE POD ENDS GENTLY.</span>
<a href="V5PodEnd.dc.html" class="ul" style="{TYPE};font-weight:700;font-size:11px;letter-spacing:.16em;color:{INK};white-space:nowrap">LEAVE GENTLY</a></div>''',
    540, 262, rot=-1, seed=1402, pad='34px 40px', tapes=tape(215, -14, 110, 28, rot=3, seed=141))
x04 = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='talk pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;gap:56px;padding:0 56px 24px;opacity:.15">
<div style="padding-top:10px">{side}</div>
<div style="padding-top:8px">{chat_sheet}</div>
</main>
<div class="veil"></div><div class="holdnote">{hold_card}</div>'''
page('V5Reconnect', 'Reconnecting, mid pod', x04, css=SYS_CSS + f""".hl{{background-image:linear-gradient(transparent 38%,rgba(216,198,164,.75) 38%,rgba(216,198,164,.75) 90%,transparent 90%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 4px}}""")

# ================= X05 — this note isn't here (404) =================
def torn_scrap(w=170, h=96, seed=1501):
    """All that's left: a strip of tape and the torn top of a note that was pulled away."""
    r = random.Random(seed)
    pts = [(0, 0), (w, 0), (w - r.uniform(0, 3), h * .45)]
    n = 14
    for i in range(n + 1):  # a deep ragged tear running back across, lower on the left
        x = w - w * i / n
        y = h * (.42 + .5 * i / n) + r.uniform(-9, 9)
        pts.append((x, min(h, max(h * .3, y))))
    poly = 'polygon(' + ','.join(f'{x:.1f}px {y:.1f}px' for x, y in pts) + ')'
    sc = (f'<div class="lift" style="position:relative;width:{w}px;height:{h}px;transform:rotate(-3deg)">'
          f'<div class="paper hi" style="position:absolute;inset:0;clip-path:{poly}">'
          f'<div style="position:absolute;left:18px;top:30px;width:110px;height:2px;background:{RULE}"></div>'
          f'<div style="position:absolute;left:18px;top:44px;width:70px;height:2px;background:{RULE}"></div></div></div>')
    return (f'<div class="scrapfall" style="position:relative;width:{w + 40}px;height:{h + 30}px">'
            f'<div class="flutter" style="position:absolute;left:20px;top:12px">{sc}</div>'
            f'{tape(40, 0, 130, 32, rot=-5, seed=151)}</div>')
nf_note = paper(f'''
{t_type('nothing pinned here anymore', 11, PENCIL)}
{h_hand('It already let go.', 54, color=INK, wait='.5s', extra='margin-top:10px')}
<div class="rise" style="--w:1.4s;{SERIF};font-size:21px;line-height:1.6;color:{INK};margin-top:14px">Whatever was here has faded, like it was meant to. Rooms close when the night ends. Echoes fade in a day.</div>
<div class="rise" style="--w:1.9s;{MARK};font-size:26px;color:{RED};margin-top:16px;transform:rotate(-1.5deg)">that's the whole point of this place.</div>
<div class="rise" style="--w:2.3s;margin-top:30px">{chip('back home', 'V5Home.dc.html', kind='ink', seed=1503, w=180)}</div>''',
    620, 404, rot=.8, seed=1502, pad='46px 52px', tapes=tape(240, -14, 120, 30, rot=3, seed=152))
nf_side = f'''<div style="display:flex;flex-direction:column;align-items:center;gap:30px;margin-top:-40px">
{torn_scrap()}
<div class="fadein" style="--w:1.4s;{HAND};font-size:22px;color:{BOARDTXT};text-align:center">someone left something here.<br>now it's just tape.</div>
<div class="rise" style="--w:2.6s;margin-top:20px">{rabbit(100, CHALK, uid='xn')}</div></div>'''
x05 = sys_page(f'<div class="rise" style="--w:.1s">{nf_note}</div>{nf_side}', crumb='')
page('V5NotFound', "This note isn't here", x05, css=SYS_CSS)

DESK = [
    {"file": "V5MicAsk.dc.html", "title": "X01 — Before the browser asks for your mic", "w": 1440, "h": 900, "row": "system"},
    {"file": "V5MicBlocked.dc.html", "title": "X02 — Mic is blocked", "w": 1440, "h": 900, "row": "system"},
    {"file": "V5Offline.dc.html", "title": "X03 — Lost the signal", "w": 1440, "h": 900, "row": "system"},
    {"file": "V5Reconnect.dc.html", "title": "X04 — Reconnecting, mid pod", "w": 1440, "h": 900, "row": "system"},
    {"file": "V5NotFound.dc.html", "title": "X05 — This note isn't here", "w": 1440, "h": 900, "row": "system"},
]

def write_manifest(entries):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest_system.json')
    cur = json.load(open(p)) if os.path.exists(p) else []
    files = {e['file'] for e in entries}
    cur = [e for e in cur if e['file'] not in files] + entries
    order = {'system': 0, 'm_system': 1}
    cur.sort(key=lambda e: order.get(e['row'], 9))
    json.dump(cur, open(p, 'w'), indent=1)

if __name__ == '__main__':
    write_manifest(DESK)
    print('system desktop ok')
