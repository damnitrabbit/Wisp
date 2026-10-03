"""N0TRACE V5 — system moments (phone). Boards: V5MMicAsk, V5MMicBlocked, V5MOffline, V5MReconnect, V5MNotFound."""
from gen5 import *
import json, os, random

W = MW - 2 * MPAD  # 346
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
LOCK = '<path d="M4 8h8v6.5H4zM5.8 8V5.6a2.2 2.2 0 0 1 4.4 0V8" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>'
RELOAD = '<path d="M13 8.5a5 5 0 1 1-1.5-3.6M13 2.5v3h-3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'

def ic(icon, size=16):
    return f'<svg width="{size}" height="{size + 1}" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0">{icon}</svg>'

def long_arrow(d, head, color='#F0A08F', wait='1.6s', length=300, sw=2):
    return (f'<path class="draw" style="--len:{length};--d:1s;--w:{wait}" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>'
            f'<path class="draw" style="--len:50;--d:.4s;--w:calc({wait} + .9s)" d="{head}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>')

SYS_CSS = f"""
.write{{text-wrap:balance}}
.sway{{transform-origin:50% 0;animation:sway 7s ease-in-out infinite}}
@keyframes sway{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(1deg)}}}}
.dots i{{display:inline-block;width:5px;height:5px;margin-right:4px;border-radius:50%;background:currentColor;animation:dot 1.8s ease-in-out infinite}}
.dots i:nth-child(2){{animation-delay:.25s}}.dots i:nth-child(3){{animation-delay:.5s}}
@keyframes dot{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.step{{opacity:0;animation:rise 1s cubic-bezier(.2,.7,.2,1) var(--w) forwards;transform:translateY(8px)}}
.veil{{position:absolute;inset:0;background:rgba(6,6,7,.78);z-index:60;animation:fadein .8s ease both}}
.holdnote{{position:absolute;left:50%;top:46%;z-index:61;transform:translate(-50%,-50%);animation:hold .9s cubic-bezier(.3,1.25,.5,1) .4s both}}
@keyframes hold{{from{{opacity:0;transform:translate(-50%,-44%) rotate(-4deg)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
.loop{{stroke-dasharray:var(--len);stroke-dashoffset:var(--len);animation:loopdraw 4.8s cubic-bezier(.45,.05,.4,1) infinite}}
@keyframes loopdraw{{0%{{stroke-dashoffset:var(--len);opacity:1}}55%{{stroke-dashoffset:0;opacity:1}}80%{{stroke-dashoffset:0;opacity:0}}100%{{stroke-dashoffset:var(--len);opacity:0}}}}
.scrapfall{{animation:scrapfall 1.2s cubic-bezier(.3,1.1,.5,1) .2s both}}
@keyframes scrapfall{{from{{opacity:0;transform:translateY(-14px) rotate(-8deg)}}to{{opacity:1}}}}
.flutter{{transform-origin:50% 0;animation:flutter 5s ease-in-out infinite}}
@keyframes flutter{{0%,100%{{transform:rotate(-1.5deg)}}50%{{transform:rotate(2deg)}}}}
.hl{{background-image:linear-gradient(transparent 38%,rgba(216,198,164,.75) 38%,rgba(216,198,164,.75) 90%,transparent 90%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 3px}}
"""

def text_link(label, href, color=INK, size=11.5):
    return f'<a href="{href}" class="ul" style="{TYPE};font-size:{size}px;letter-spacing:.16em;text-transform:uppercase;color:{color}">{label}</a>'

SYS_CSS += """
.holdin{animation:holdin .9s cubic-bezier(.3,1.25,.5,1) .4s both}
@keyframes holdin{from{opacity:0;transform:translateY(5%) rotate(-4deg)}to{opacity:1;transform:none}}
"""

# ---------- phone frame helpers (see gen5: mbody / msheet / mdock) ----------
def ctape(w=110, h=28, rot=-3, seed=1, y=-13):
    """A tape centred on a sheet of any width."""
    return f'<span aria-hidden="true" style="position:absolute;left:50%;top:0;margin-left:{-w / 2:.0f}px;width:{w}px;height:0;z-index:6">{tape(0, y, w, h, rot=rot, seed=seed)}</span>'

def grow(sheet, wait='.1s', cls=''):
    """Wrap the main sheet so it can grow to meet the dock."""
    return f'<div class="rise {cls}" style="--w:{wait};flex:1 1 auto;min-height:0;display:flex;flex-direction:column">{sheet}</div>'

def dockwrap(dock, wait='1.6s'):
    return f'<div class="rise" style="--w:{wait};display:flex;flex-direction:column">{dock}</div>'

def mcard(inner, kind='', seed=1, pad='28px 24px', rot=0, tapes='', w='100%'):
    """A card that is as tall as its content (for overlays): deckled, fluid width."""
    return (f'<div class="lift" style="position:relative;width:{w};max-width:100%;transform:rotate({rot}deg)">'
            f'<div class="paper {kind}" style="padding:{pad};clip-path:{deckle(300, 340, seed=seed)}">{inner}</div>{tapes}</div>')

def board_note(rab, text, wait='2.3s'):
    """The rabbit + a pencil line, sitting at the foot of a sheet."""
    return (f'<div class="rise" style="--w:{wait};margin-top:auto;padding-top:14px;border-top:1px dashed {RULE};display:flex;align-items:center;gap:14px">'
            f'{rab}<div style="{HAND};font-size:19px;line-height:1.3;color:{PENCIL}">{text}</div></div>')

from v5m_home import fcard
def fitwrap(sheet, wait='.1s', cls=''):
    """Paper as tall as its words, centred in the free space (no empty paper under the message)."""
    return f'<div class="rise {cls}" style="--w:{wait};flex:0 0 auto;margin:auto 0;display:flex;flex-direction:column">{sheet}</div>'
def fsheet(inner, kind='', seed=1, pad='28px 24px', rot=0, tapes='', minh=0, **k):
    return fcard(inner, kind, seed, pad, rot, tapes)

def middle(inner):
    """The message block: centred in whatever height the sheet has."""
    return f'<div style="flex:1 0 auto;display:flex;flex-direction:column;justify-content:center;padding:6px 0 14px">{inner}</div>'

def phone(body, dock, crumb='', right=None, foot=True, overlay='', center=False, back=None):
    return f'''
{matmos()}
{mtopbar(crumb=crumb, right=right, back=back)}
{mbody(body, center=center)}
{dock}
{mfooter() if foot else ''}{overlay}'''

UNTIL = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">UNTIL 2AM</span>'

def up_note(text, side='right', wait='2s', h=58):
    """A salmon margin note with an arrow pointing up at the browser's own chrome."""
    arrow = (f'<svg width="26" height="{h - 6}" viewBox="0 0 26 {h - 6}" aria-hidden="true" style="flex-shrink:0;overflow:visible">'
             + long_arrow(f'M12 {h - 8} C10 {h * .6:.0f} 16 {h * .35:.0f} 13 4', 'M5 13 L13 3 L21 13', wait=wait, length=90) + '</svg>')
    txt = f'<div class="fadein" style="--w:calc({wait} + .8s);{MARK};font-size:20px;line-height:1.1;color:#F0A08F;transform:rotate(-4deg)">{text}</div>'
    row = arrow + txt if side == 'left' else txt + arrow
    jc = 'flex-start' if side == 'left' else 'flex-end'
    return f'<div style="flex-shrink:0;height:{h}px;display:flex;align-items:flex-end;justify-content:{jc};gap:10px;padding:0 10px">{row}</div>'

# ================= MX01 — before the browser asks =================
ask = fsheet(f'''{middle(f"""
{t_type('before your browser asks', 10, PENCIL)}
{h_hand('Your browser will ask for your mic.', 34, color=INK, wait='.4s', extra='margin-top:8px')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:17px;line-height:1.6;color:{INK};margin-top:12px">It's only so moss_byte can hear you, now that you both said yes. Your voice goes straight between you, and it's never recorded.</div>""")}
{board_note(rabbit(52, INK, uid="mxa"), 'just the two of you.<br>nobody else listening.')}''',
    rot=-.6, seed=2102, pad='30px 26px 20px', minh=300, tapes=ctape(110, 28, rot=-3, seed=211))
mx01 = phone(up_note("it'll pop up<br>up top") + fitwrap(ask),
             dockwrap(mdock(mcta('allow mic', '#', 'ink', seed=2101, icon=ic(MIC, 14)) + mtext('stay on text', 'V5MPod.dc.html'))),
             right=UNTIL)
mpage('V5MMicAsk', 'Before the browser asks for your mic', mx01, css=SYS_CSS)

# ================= MX02 — mic is blocked =================
def step(n, text, icon, wait):
    return (f'<div class="step" style="--w:{wait};display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:1px dashed {RULE}">'
            f'<span style="{MARK};font-size:25px;line-height:1;color:{RED};width:16px">{n}</span>'
            f'<span style="display:inline-flex;flex-shrink:0;width:30px;height:30px;align-items:center;justify-content:center;border:1.5px solid {INK};border-radius:50%;color:{INK}">{ic(icon, 15)}</span>'
            f'<span style="{HAND};font-size:clamp(18px,5.4vw,21px);line-height:1.2;color:{INK}">{text}</span></div>')
blocked = fsheet(f'''{middle(f"""
{t_type('mic is blocked', 10, PENCIL)}
{h_hand("We can't hear you yet.", 32, color=INK, wait='.4s', extra='margin-top:8px')}
<div class="rise" style="--w:1.1s;{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:8px">Your browser said no to the mic. Three tiny steps fix it:</div>
<div style="margin-top:10px;border-top:1px dashed {RULE}">
{step(1, 'tap the lock up top', LOCK, '1.5s')}
{step(2, 'microphone → allow', MIC, '1.9s')}
{step(3, 'reload this page', RELOAD, '2.3s')}</div>""")}
{board_note(rabbit(44, INK, uid="mxb"), 'no rush. text works<br>just as well.', wait='3s')}''',
    rot=.6, seed=2202, pad='28px 26px 18px', minh=300, tapes=ctape(110, 28, rot=3, seed=221))
lock_txt = f'the lock <svg width="15" height="16" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;top:2px">{LOCK}</svg> lives<br>up in the address bar'
mx02 = phone(up_note(lock_txt, side='left', wait='3s') + fitwrap(blocked),
             dockwrap(mdock(mcta('reload', '#', 'ink', seed=2201, icon=ic(RELOAD, 14)) + mtext('stay on text', 'V5MPod.dc.html')), wait='2.8s'),
             right=UNTIL)
mpage('V5MMicBlocked', 'Mic is blocked', mx02, css=SYS_CSS)

# ================= MX03 — lost the signal =================
off = fsheet(f'''{middle(f"""
<div style="display:flex;justify-content:center">{rabbit(110, INK, mood='sleep', uid='mxo')}</div>
{h_hand('Lost the signal.', 40, color=INK, wait='.6s', extra='text-align:center;margin-top:16px')}
<div class="rise" style="--w:1.5s;{SERIF};font-size:18px;line-height:1.6;color:{INK};text-align:center;margin-top:8px">Nothing was saved anyway,<br>so nothing is lost.</div>
<div class="rise" style="--w:2s;display:flex;justify-content:center;align-items:center;gap:10px;margin-top:20px;{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">
<span class="dots"><i></i><i></i><i></i></span>TRYING AGAIN ON ITS OWN</div>""")}
<div class="fadein" style="--w:3s;margin-top:auto;padding-top:14px;border-top:1px dashed {RULE};{MARK};font-size:20px;line-height:1.2;color:{RED};transform:rotate(-1.5deg);text-align:center">it'll find its way back.<br>you don't have to do anything.</div>''',
    rot=-.6, kind='hi', seed=2302, pad='30px 24px 18px', minh=320, tapes=ctape(110, 28, rot=-3, seed=231))
mx03 = phone(fitwrap(f'<div class="sway" style="display:flex;flex-direction:column">{off}</div>'),
             dockwrap(mdock(mcta('try now', '#', 'ink', seed=2301)), wait='2.4s'),
             right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:#C9BFAE">OFFLINE</span>')
mpage('V5MOffline', 'Lost the signal', mx03, css=SYS_CSS)

# ================= MX04 — reconnecting, mid pod (dimmed phone pod underneath) =================
CONVO = [
    ("hey. I'm here. take your time, there's no rush.", False, '11:52'),
    ("I don't even know where to start honestly", True, '11:53'),
    ("that's okay. start anywhere. the middle is fine too.", False, '11:53'),
    ("my best friend moved away last month and I didn't realise how much of my week was just… her.", True, '11:55'),
    ("that sounds really lonely. like the shape of your days changed overnight.", False, '11:56'),
]
def line_msg(text, mine=False, who='moss_byte', t='11:52'):
    if mine:
        return (f'<div style="align-self:flex-end;max-width:84%"><div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px;text-align:right">YOU · {t}</div>'
                f'<span class="hl" style="{SERIF};font-size:16px;line-height:25px;color:{INK}">{text}</span></div>')
    return (f'<div style="align-self:flex-start;max-width:84%;padding-left:12px;border-left:2px solid rgba(184,53,42,.35)"><div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px">{who.upper()} · {t}</div>'
            f'<span style="{SERIF};font-size:16px;line-height:25px;color:{INK}">{text}</span></div>')
sheet = msheet(f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 24px,rgba(96,120,150,.16) 24px 25px);background-position:0 12px"></div>
<div style="position:relative;flex:1 1 auto;min-height:0;display:flex;flex-direction:column">
<div style="display:flex;justify-content:space-between;align-items:baseline;padding-bottom:10px;border-bottom:1px dashed {RULE}">
<span style="{HAND};font-size:22px;color:{INK}">you &amp; moss_byte</span><span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">RECONNECTING…</span></div>
<div style="flex:1 1 auto;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:16px;padding:14px 2px 12px;overflow:hidden">{''.join(line_msg(a, b, t=c) for a, b, c in CONVO)}</div>
<div style="margin-top:auto;border-top:1.5px dashed {RULE};padding-top:12px;display:flex;align-items:center;justify-content:space-between;gap:12px">
<span style="{SERIF};font-style:italic;font-size:16px;color:{PENCIL};white-space:nowrap;overflow:hidden;text-overflow:ellipsis">say it however…</span>{chip('send ↗', '#', kind='ink', seed=2433, w=100)}</div>
</div>""", rot=.3, kind='hi', seed=2434, pad='18px 20px 16px', minh=380, tapes=ctape(100, 26, rot=-2, seed=243, y=-12))

def hold_loop(size=96, uid='hl', rabbit_w=56):
    L = 3.3 * size
    r = size / 2 - 5
    c = size / 2
    d = (f'M{c + 4:.0f} {c - r:.0f} C{c + r * 1.05:.0f} {c - r:.0f} {c + r + 2:.0f} {c + r * .6:.0f} {c + r * .3:.0f} {c + r:.0f} '
         f'C{c - r * .5:.0f} {c + r + 3:.0f} {c - r - 2:.0f} {c + r * .4:.0f} {c - r + 2:.0f} {c - r * .2:.0f} C{c - r * .8:.0f} {c - r * .9:.0f} {c - r * .2:.0f} {c - r - 3:.0f} {c + 10:.0f} {c - r + 1:.0f}')
    return (f'<div style="position:relative;width:{size}px;height:{size}px;display:flex;align-items:center;justify-content:center;flex-shrink:0">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible">'
            f'<path class="loop" style="--len:{L:.0f}" d="{d}" fill="none" stroke="{PENCIL}" stroke-width="2" stroke-linecap="round"/></svg>'
            f'<div class="breathe">{rabbit(rabbit_w, INK, uid=uid)}</div></div>')

hold_card = mcard(f'''
<div style="display:flex;flex-direction:column;align-items:center;text-align:center">
{hold_loop(104, 'mxr', 60)}
<div style="{HAND};font-size:32px;line-height:1.15;color:{INK};margin-top:12px">Reconnecting…</div>
<div style="{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:6px">We're holding your place<br>for 30 seconds.</div></div>
<div style="border-top:1px dashed {RULE};margin-top:18px;padding-top:14px;display:flex;flex-direction:column;align-items:center;gap:6px;text-align:center">
<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.6;color:{PENCIL}">IF IT DOESN'T COME BACK,<br>THE POD ENDS GENTLY.</span>
{mtext('leave gently', 'V5MPodEnd.dc.html', INK)}</div>''',
    rot=-1, seed=2402, pad='30px 26px 14px', w='300px', tapes=ctape(110, 28, rot=3, seed=241))
pod_dock = mdock(mtext('leave gently', 'V5MPodEnd.dc.html', CHALK) + '<span style="flex:1"></span>' + mtext('report · ends now', 'V5MReported.dc.html', CRISIS), footer=False)
mx04 = f'''
{matmos()}
{mtopbar(back='V5MHomeOpen.dc.html', crumb='talk pod')}
<div aria-hidden="true" inert style="position:relative;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;opacity:.15">
{mbody(grow(sheet, '0s'))}
{pod_dock}</div>
<div class="veil"></div>
<div role="dialog" aria-label="Reconnecting" style="position:absolute;inset:0;z-index:61;display:flex;align-items:center;justify-content:center;padding:64px {MPAD}px 40px">
<div class="holdin" style="width:300px;max-width:100%">{hold_card}</div></div>'''
mpage('V5MReconnect', 'Reconnecting, mid pod', mx04, css=SYS_CSS)

# ================= MX05 — this note isn't here =================
def torn_scrap(w=130, h=80, seed=2501):
    r = random.Random(seed)
    pts = [(0, 0), (w, 0), (w - r.uniform(0, 3), h * .45)]
    n = 12
    for i in range(n + 1):
        x = w - w * i / n
        y = h * (.42 + .5 * i / n) + r.uniform(-8, 8)
        pts.append((x, min(h, max(h * .3, y))))
    poly = 'polygon(' + ','.join(f'{x:.1f}px {y:.1f}px' for x, y in pts) + ')'
    sc = (f'<div class="lift" style="position:relative;width:{w}px;height:{h}px;transform:rotate(-3deg)">'
          f'<div class="paper hi" style="position:absolute;inset:0;clip-path:{poly}">'
          f'<div style="position:absolute;left:16px;top:26px;width:{w * .64:.0f}px;height:2px;background:{RULE}"></div>'
          f'<div style="position:absolute;left:16px;top:38px;width:{w * .4:.0f}px;height:2px;background:{RULE}"></div></div></div>')
    return (f'<div class="scrapfall" style="position:relative;flex-shrink:0;width:{w + 24}px;height:{h + 20}px">'
            f'<div class="flutter" style="position:absolute;left:12px;top:10px">{sc}</div>'
            f'{tape(24, 0, 110, 28, rot=-5, seed=251)}</div>')
nf = fsheet(f'''{middle(f"""
{t_type('nothing pinned here anymore', 10, PENCIL)}
{h_hand('It already let go.', 33, color=INK, wait='.5s', extra='margin-top:8px')}
<div class="rise" style="--w:1.4s;{SERIF};font-size:17px;line-height:1.6;color:{INK};margin-top:10px">Whatever was here has faded, like it was meant to. Rooms close when the night ends. Echoes fade in a day.</div>
<div class="rise" style="--w:1.9s;{MARK};font-size:22px;line-height:1.2;color:{RED};margin-top:12px;transform:rotate(-1.5deg)">that's the whole point.</div>""")}
<div class="rise" style="--w:2.6s;margin-top:auto;padding-top:12px;border-top:1px dashed {RULE};display:flex;justify-content:center">{rabbit(56, INK, uid="mxn")}</div>''',
    rot=.6, seed=2502, pad='30px 26px 16px', minh=300, tapes=ctape(110, 28, rot=3, seed=252))
mx05 = phone(f'''<div style="flex-shrink:0;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 4px 0">
{torn_scrap()}
<div class="fadein" style="--w:1.4s;{HAND};font-size:18px;line-height:1.3;color:{BOARDTXT};text-align:right">someone left<br>something here.<br>now it's just tape.</div></div>''' + fitwrap(nf, '.3s'),
             dockwrap(mdock(mcta('back home', 'V5MHome.dc.html', 'ink', seed=2503)), wait='2.3s'))
mpage('V5MNotFound', "This note isn't here", mx05, css=SYS_CSS)

PHONE = [
    {"file": "V5MMicAsk.dc.html", "title": "MX01 — Before the browser asks for your mic", "w": 390, "h": 844, "row": "m_system"},
    {"file": "V5MMicBlocked.dc.html", "title": "MX02 — Mic is blocked", "w": 390, "h": 844, "row": "m_system"},
    {"file": "V5MOffline.dc.html", "title": "MX03 — Lost the signal", "w": 390, "h": 844, "row": "m_system"},
    {"file": "V5MReconnect.dc.html", "title": "MX04 — Reconnecting, mid pod", "w": 390, "h": 844, "row": "m_system"},
    {"file": "V5MNotFound.dc.html", "title": "MX05 — This note isn't here", "w": 390, "h": 844, "row": "m_system"},
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
    write_manifest(PHONE)
    print('system phone ok')
