"""N0TRACE V5 phone: talk flow. Boards MT01-MT09 (V5MMatching ... V5MPaused).
Helpers at the top are shared with v5x_talk.py (generation only runs under __main__)."""
from gen5 import *
import v5_live as LV
import json, os

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest_talk.json')
ORDER = ['V5Lean', 'V5LeanListen', 'V5Listener', 'V5Requeue', 'V5Paused',
         'V5MLean', 'V5MLeanListen', 'V5MMatching', 'V5MPod', 'V5MPodNudge', 'V5MPodEnd', 'V5MPodEndNotes', 'V5MQuestion', 'V5MAsleep', 'V5MListener', 'V5MRequeue', 'V5MPaused']
BOARDS = []
def board(name, title, h, row, w=MW):
    BOARDS.append({"file": name + '.dc.html', "title": title, "w": w, "h": h, "row": row})

def write_manifest():
    cur = []
    if os.path.exists(MANIFEST):
        try: cur = json.load(open(MANIFEST))
        except Exception: cur = []
    mine = {b['file'] for b in BOARDS}
    allb = [b for b in cur if b['file'] not in mine] + BOARDS
    allb.sort(key=lambda b: ORDER.index(b['file'][:-8]) if b['file'][:-8] in ORDER else 99)
    json.dump(allb, open(MANIFEST, 'w'), indent=1)

W = MW - 2 * MPAD   # 346
LRED = '#E07A6E'    # red ink that still reads on the dark board
SOFTRED = '#F0A08F'

# ---------- icons (same strokes as the desktop pod) ----------
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
DOOR = '<path d="M3 15h10M5 15V2.5h6V15M9 9h.01M11 2.5l2 1.5V15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
FLAG = '<path d="M4 15V2.5M4 3h8l-2 3 2 3H4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
def ic(icon, size=16):
    return f'<svg width="{size}" height="{size + 1}" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0">{icon}</svg>'

INKFLAT = '#2a2522'
def tchip(label, href='#', kind='ink', w=None, h=54, seed=11, icon=None, fs=13, rot=0, justify='center', pad=18):
    """One chip for every talk/voice action. ink = flat fill + torn edge + flat shadow (gen5 .chip.inkc);
    kraft/paper = torn paper with the usual lift. Heights: 54 desktop, 48 phone primary, 44 phone minimum."""
    import re as _re
    plain = _re.sub('<[^>]+>', '', label)
    ww = w or int(len(plain) * fs * .78 + 2 * pad + (24 if icon else 0))
    if kind == 'ink':
        bg, cls, col = f'background-color:{INKFLAT}', 'chip inkc', PAPERHI
        span_cls = ''
    else:
        bg, cls, col = (f'background-color:{KRAFT}' if kind == 'kraft' else f'background-color:{PAPERHI}'), 'chip lift', INK
        span_cls = ' class="paper"'
    i = (f'<svg width="15" height="16" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0">{icon}</svg>' if icon else '')
    rt = f'transform:rotate({rot}deg);' if rot else ''
    return (f'<a href="{href}" class="{cls}" style="position:relative;display:inline-flex;align-items:center;justify-content:{justify};gap:10px;width:{ww}px;height:{h}px;padding:0 {pad}px;flex-shrink:0;color:{col};{rt}">'
            f'<span{span_cls} style="position:absolute;inset:0;{bg};clip-path:{deckle(ww, h, amp=1.5, step=12, seed=seed)}"></span>{i}'
            f'<span style="position:relative;{TYPE};font-weight:700;font-size:{fs}px;letter-spacing:.16em;text-transform:uppercase;white-space:nowrap;color:{col}">{label}</span></a>')

def small_chip(label, href, icon, kind, w, seed, h=44, fs=12):
    return tchip(label, href, kind, w, h, seed, icon, fs, rot={'ink': -.8, 'kraft': .7, 'paper': .4}[kind], pad=12)

# ---------- the red-thread loader, parameterised ----------
def pin_svg(x, y, col, r=8):
    return (f"<ellipse cx='{x + r * .5:.1f}' cy='{y + r * .85:.1f}' rx='{r + 1}' ry='{r * .62:.1f}' fill='#000' opacity='.45'/>"
            f"<circle cx='{x}' cy='{y}' r='{r}' fill='{col}'/><circle cx='{x}' cy='{y}' r='{r}' fill='none' stroke='#000' stroke-opacity='.35'/>"
            f"<circle cx='{x - r * .32:.1f}' cy='{y - r * .32:.1f}' r='{r * .29:.1f}' fill='#fff' opacity='.28'/>")

def sag(x0, y0, x1, y1, k=60):
    mx = (x0 + x1) / 2
    ke = max(6, k - abs(y1 - y0) * .5)  # long drops hang almost straight; level spans sag
    return f'M {x0} {y0} Q {mx:.0f} {max(y0, y1) + ke + abs(x1 - x0) * .06:.0f} {x1} {y1}'

def scr(w, mt=10):
    return f"<div style='height:2px;width:{w}px;background:{RULE};margin-top:{mt}px;border-radius:2px'></div>"

def thread_loader(sfx, W_, H_, you_pin, you_box, you_inner, listeners, slip=(104, 84), cycle=11.2, k=60, pin_r=8, sw=2.2, you_kind='hi'):
    """you_box = (left, top, w, h, rot). listeners = [(pin x, pin y, rot, seed)]. Returns (html, css)."""
    n = len(listeners)
    slot = cycle / n
    sw_, sh_ = slip
    css = f"""
.th{sfx}{{stroke-dasharray:100 100;stroke-dashoffset:100;animation:ask{sfx} {cycle}s cubic-bezier(.5,.05,.35,1) infinite;filter:drop-shadow(0 3px 2px rgba(0,0,0,.55))}}
@keyframes ask{sfx}{{0%{{stroke-dashoffset:100}}{36 / n:.1f}%{{stroke-dashoffset:0}}{68 / n:.1f}%{{stroke-dashoffset:0}}{98 / n:.1f}%,100%{{stroke-dashoffset:100}}}}
.sl{sfx}{{position:absolute;transform-origin:50% 8px;animation:tug{sfx} {cycle}s ease-in-out infinite}}
@keyframes tug{sfx}{{0%,{32 / n:.1f}%{{transform:rotate(0) translateY(0)}}{40 / n:.1f}%{{transform:rotate(-2.4deg) translateY(-3px)}}{50 / n:.1f}%{{transform:rotate(1.6deg) translateY(-1px)}}{60 / n:.1f}%,100%{{transform:rotate(0) translateY(0)}}}}
.kn{sfx}{{opacity:0;animation:kn{sfx} {cycle}s ease-in-out infinite}}
@keyframes kn{sfx}{{0%,{34 / n:.1f}%{{opacity:0;transform:scale(.4)}}{40 / n:.1f}%{{opacity:1;transform:scale(1.15)}}{48 / n:.1f}%,{64 / n:.1f}%{{opacity:1;transform:scale(1)}}{76 / n:.1f}%,100%{{opacity:0;transform:scale(.6)}}}}
.yw{sfx}{{position:absolute;animation:yb{sfx} 4.4s ease-in-out infinite;transform-origin:50% 0}}
@keyframes yb{sfx}{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(.8deg)}}}}
"""
    def lst(i, x, y, rot, seed):
        inner = f"<div style='padding-top:{int(sh_ * .2)}px'>{scr(int(sw_ * .55), 9)}{scr(int(sw_ * .72), 9)}{scr(int(sw_ * .42), 9)}</div>"
        return (f'<div class="sl{sfx}" style="left:{x - sw_ / 2:.0f}px;top:{y - 12}px;animation-delay:{i * slot:.2f}s">'
                f'{paper(inner, sw_, sh_, rot=rot, kind="hi" if i % 2 else "", seed=seed, pad="8px 14px")}</div>')
    threads = ''.join(
        f"<path class='th{sfx}' pathLength='100' style='animation-delay:{i * slot:.2f}s' d='{sag(*you_pin, x, y, k)}' fill='none' stroke='{RED}' stroke-width='{sw}' stroke-linecap='round'/>"
        for i, (x, y, _, _) in enumerate(listeners))
    knots = ''.join(
        f"<circle class='kn{sfx}' data-snd='pluck' data-snd-i='{i}' data-snd-at='{0.37 / n:.3f}' style='animation-delay:{i * slot:.2f}s;transform-box:fill-box;transform-origin:center' cx='{x}' cy='{y}' r='{pin_r + 5}' fill='none' stroke='{BOARDTXT}' stroke-width='1.6' stroke-dasharray='3 3'/>"
        for i, (x, y, _, _) in enumerate(listeners))
    pins = pin_svg(*you_pin, RED, pin_r) + ''.join(pin_svg(x, y, '#3a3a3d', pin_r) for x, y, _, _ in listeners)
    l, t, w, h, rot = you_box
    you = paper(you_inner, w, h, rot=rot, kind=you_kind, seed=621 + len(sfx), pad='0')
    html = (f'<div style="position:relative;width:{W_}px;height:{H_}px;flex-shrink:0">'
            f'<div class="yw{sfx}" style="left:{l}px;top:{t}px">{you}</div>'
            f'{"".join(lst(i, *L) for i, L in enumerate(listeners))}'
            f'<svg width="{W_}" height="{H_}" viewBox="0 0 {W_} {H_}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible;z-index:5">{threads}{knots}{pins}</svg></div>')
    return html, css

def you_note(name='QUIET_OTTER', size=32, pad='24px 20px', sub=None):
    s = f'<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL};margin-top:10px">{name}</div>'
    if sub:
        s += f'<div style="{MARK};font-size:17px;color:{RED};margin-top:6px">{sub}</div>'
    return f'<div style="padding:{pad}"><div style="{HAND};font-size:{size}px;color:{INK};line-height:1">you</div>{s}</div>'

# ---------- chat atoms ----------
def line_msg(text, mine=False, who='moss_byte', t='11:52', i=0, size=16, lh=26, maxw='84%'):
    if mine:
        head = f'<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px;text-align:right">YOU · {t}</div>'
        body = f'<span class="hl" style="{SERIF};font-size:{size}px;line-height:{lh}px;color:{INK}">{text}</span>'
        return f'<div class="msg" style="--i:{i};align-self:flex-end;max-width:{maxw};text-align:left">{head}{body}</div>'
    head = f'<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px">{who.upper()} · {t}</div>'
    body = f'<span style="{SERIF};font-size:{size}px;line-height:{lh}px;color:{INK}">{text}</span>'
    return f'<div class="msg" style="--i:{i};align-self:flex-start;max-width:{maxw};padding-left:12px;border-left:2px solid rgba(184,53,42,.35)">{head}{body}</div>'

POD_CSS = f"""
.hl{{background-image:linear-gradient(transparent 38%,rgba(216,198,164,.75) 38%,rgba(216,198,164,.75) 90%,transparent 90%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 3px}}
.scroll{{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 56px);mask-image:linear-gradient(to bottom,transparent 0,#000 56px)}}
.msg{{opacity:0;animation:msgin .6s ease calc(.25s + var(--i) * .12s) both}}
@keyframes msgin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.dots i{{display:inline-block;width:5px;height:5px;margin-right:4px;border-radius:50%;background:{PENCIL};animation:dot 1.2s ease-in-out infinite}}
.dots i:nth-child(2){{animation-delay:.15s}}.dots i:nth-child(3){{animation-delay:.3s}}
@keyframes dot{{0%,100%{{transform:translateY(0);opacity:.4}}50%{{transform:translateY(-4px);opacity:1}}}}
.veil{{position:absolute;inset:0;background:rgba(8,8,9,.74);z-index:60;animation:fadein .6s ease both}}
.nudge{{position:absolute;left:50%;top:50%;z-index:61;transform:translate(-50%,-50%);animation:nudge .9s cubic-bezier(.3,1.3,.5,1) .3s both}}
@keyframes nudge{{from{{opacity:0;transform:translate(-50%,-30%) rotate(-6deg)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
.ldot{{width:6px;height:6px;border-radius:50%;background:#E08A3C;animation:ld 2.6s ease-out infinite}}
@keyframes ld{{0%{{box-shadow:0 0 0 0 rgba(224,138,60,.5)}}100%{{box-shadow:0 0 0 8px rgba(224,138,60,0)}}}}
"""

def mhead(title, size=34, wait='.2s', d='1.6s', pad=None):
    return f'<div style="padding:{pad or f"2px {MPAD}px 0"}">{h_hand(title, size, wait=wait, d=d)}</div>'

# ---------- fluid phone pieces (the phone frame: nothing wider than the column, heights follow content) ----------
def ctape(w=100, h=26, rot=-2, seed=61, red=False, y=-12):
    """A strip of tape centred on whatever it's stuck to (any width)."""
    return tape(0, y, w, h, rot=rot, red=red, seed=seed).replace('left:0px', f'left:calc(50% - {w / 2:g}px)', 1)

def apaper(inner, rot=0, kind='', seed=1, pad='22px 24px', tapes='', extra='', cls='', torn=None, fill=False):
    """A card that is as wide as its column and as tall as its words (no fixed height to overflow)."""
    h = 'height:100%;' if fill else ''
    return (f'<div class="lift {cls}" style="position:relative;width:100%;{h}transform:rotate({rot}deg);flex-shrink:0;{extra}">'
            f'<div class="paper {kind}" style="{h}padding:{pad};clip-path:{deckle(346, 200, seed=seed, torn=torn)}">{inner}</div>{tapes}</div>')

def bleed(html, cls=''):
    """A fixed-size drawing (the thread board) centred edge to edge; on narrow phones it trims evenly at the sides."""
    return f'<div class="{cls}" style="margin:0 -{MPAD}px;display:flex;justify-content:center;overflow-x:clip;flex-shrink:0">{html}</div>'

def grow(html, w='.3s'):
    """Wrapper that lets the main sheet (msheet) fill the body down to the dock."""
    return f'<div class="rise" style="--w:{w};flex:1 1 auto;min-height:0;display:flex;flex-direction:column">{html}</div>'

def mnote(text, color=None):
    """Small type that sits in the dock row beside a button."""
    return f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.5;color:{color or BOARDTXT};text-align:right;flex-shrink:0">{text}</span>'

LDOTS = '<span class="ldots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span>'

def m_scrap(text, feat, href, rot, seed, kind=''):
    inner = (f'<div style="{HAND};font-size:16px;line-height:1.2;color:{INK}">{text}</div>'
             f'<div style="{TYPE};font-size:8.5px;font-weight:700;letter-spacing:.16em;color:{PENCIL};margin-top:3px">{feat} →</div>')
    return f'<a href="{href}" class="chip" style="display:block;min-width:0">{apaper(inner, rot, kind, seed, pad="12px 12px", fill=True)}</a>'

def scrap_grid(items, w='2.2s'):
    return f'<div class="rise" style="--w:{w};display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 14px;width:100%">{items}</div>'

def scrap_row(text, feat, href, rot, seed, kind='', w=W, h=62):
    inner = (f'<div style="display:flex;align-items:center;justify-content:space-between;height:100%">'
             f'<span style="{HAND};font-size:21px;color:{INK};white-space:nowrap">{text}</span>'
             f'<span style="{TYPE};font-size:9.5px;font-weight:700;letter-spacing:.16em;color:{PENCIL};white-space:nowrap">{feat} <span style="color:{INK};font-size:13px">→</span></span></div>')
    return f'<a href="{href}" class="chip" style="display:block">{paper(inner, w, h, rot=rot, seed=seed, kind=kind, pad="0 20px")}</a>'

# ---------- the closed-sign (shared with desktop paused) ----------
SIGN_CSS = """.sign{transform-origin:50% 0;animation:sign 7s ease-in-out infinite}
@keyframes sign{0%,100%{transform:rotate(-1.6deg)}50%{transform:rotate(1.6deg)}}"""
def closed_sign(w=230, h=150, title='closed for tonight', sub='OPENS AGAIN AT 10PM', tsize=34, seed=931, pin_r=8):
    """A kraft card hanging on red string from a single pin. Returns html with fixed width/height (string above)."""
    top = 54
    svg = (f'<svg width="{w}" height="{top + 6}" viewBox="0 0 {w} {top + 6}" aria-hidden="true" style="position:absolute;left:0;top:0;overflow:visible;z-index:6">'
           f'<path d="M{w * .22:.0f} {top + 4} L{w / 2:.0f} 10 L{w * .78:.0f} {top + 4}" fill="none" stroke="{RED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter:drop-shadow(0 2px 2px rgba(0,0,0,.5))"/>'
           f'{pin_svg(w / 2, 10, "#3a3a3d", pin_r)}</svg>')
    inner = (f'<div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:8px">'
             f'<div style="{HAND};font-size:{tsize}px;line-height:1.1;color:{INK}">{title}</div>' +
             (f'<div style="{TYPE};font-size:10px;font-weight:700;letter-spacing:.18em;color:{PENCIL}">{sub}</div>' if sub else '') + '</div>')
    holes = (f'<span style="position:absolute;left:{w * .22 - 4:.0f}px;top:8px;width:7px;height:7px;border-radius:50%;background:#1a1712;z-index:4"></span>'
             f'<span style="position:absolute;left:{w * .78 - 3:.0f}px;top:8px;width:7px;height:7px;border-radius:50%;background:#1a1712;z-index:4"></span>')
    card = paper(inner + '', w, h, kind='kraft', seed=seed, pad='22px 18px')
    return (f'<div class="sign" style="position:relative;width:{w}px;height:{top + h}px">{svg}'
            f'<div style="position:absolute;left:0;top:{top}px">{card}<div style="position:absolute;inset:0">{holes}</div></div></div>')


if __name__ == '__main__':
    # =====================================================================
    # MT01 — Finding someone (portrait thread loader)
    # =====================================================================
    LBW, LBH = 390, 372
    you_pin = (150, 98)
    listeners = [(300, 52, -4, 711), (86, 214, 3, 712), (286, 200, -2, 713), (186, 300, 4, 714)]
    loader_html, loader_css = thread_loader('m', LBW, LBH, you_pin, (26, 18, 150, 104, -3), you_note(), listeners, slip=(104, 84), k=46)
    mfacts = paper(f'''
<div style="display:grid;grid-template-columns:92px 1fr;row-gap:9px;{TYPE};font-size:11px;letter-spacing:.1em;line-height:1.45;color:{INK}">
<span style="color:{PENCIL}">THEY'LL</span><span>LISTEN FIRST</span>
<span style="color:{PENCIL}">STARTS AS</span><span>TEXT · VOICE ONLY IF YOU BOTH SAY YES</span>
<span style="color:{PENCIL}">KEPT</span><span>NOTHING</span></div>''', W, 128, rot=-1.2, seed=1501, pad='22px 24px', tapes=tape(W / 2 - 50, -12, 100, 26, rot=3, seed=150))
    matching = f'''
{matmos()}
{mtopbar(crumb=POD11, back='V5MHomeOpen.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center">
{loader_html}
<div style="width:100%;padding:0 {MPAD}px;margin-top:-4px">
{h_hand("Finding someone who'll listen…", 32, d='1.8s')}
<div class="rise" style="--w:1.3s;{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT};margin-top:6px">USUALLY UNDER A MINUTE · 4 LISTENERS AWAKE</div>
<div class="rise" style="--w:1.4s;{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT};margin-top:4px">PODS OPEN UNTIL 2AM</div></div>
<div class="rise" style="--w:1.6s;margin-top:28px">{mfacts}</div>
<div class="rise" style="--w:2s;width:100%;padding:22px {MPAD + 4}px 0">
<div style="{MARK};font-size:20px;line-height:1.15;color:{SOFTRED};transform:rotate(-1.5deg)">quiet night? it might take a little longer. that's okay.</div>
<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{BOARDTXT};margin-top:14px">OR LET IT GO ANOTHER WAY · ON YOUR OWN</div></div>
<div class="rise" style="--w:2.2s;display:grid;grid-template-columns:repeat(2,164px);gap:12px 14px;margin-top:12px">{m_scrap('get it out', 'BURN', 'V5MBurn.dc.html', -1.5, 1581)}{m_scrap('leave it somewhere', 'ECHOES', 'V5MEchoes.dc.html', 1.2, 1582, 'kraft')}{m_scrap("write, don't send", 'UNSENT', 'V5MUnsentWrite.dc.html', .8, 1583, 'kraft')}{m_scrap('hear it later', 'TIME CAPSULE', 'V5MCapsule.dc.html', -1, 1584)}</div>
<div class="rise" style="--w:2.4s;width:100%;padding:26px {MPAD + 4}px 0">{link('stop looking', 'V5MHomeOpen.dc.html', size=11)}</div>
</main>
{mfooter()}'''
    mpage('V5MMatching', 'Finding someone', matching, h=1050, css=loader_css)
    LV.mark('V5MMatching', replace=[('4 LISTENERS AWAKE', '{{awake}}'), ("Finding someone who'll listen…", '{{matchTitle}}'), ("THEY'LL</span>", '{{whoFirst}}</span>')])
    board('V5MMatching', 'MT01 — Finding someone (scrolls)', 1050, 'm_talk')

    # =====================================================================
    # MT02 — Talk pod: same layout as the voice boards (back + "talk pod", name strip, composer in the paper)
    # =====================================================================
    from v5m_voice import pod_strip, mchat_sheet, mpod as vpod, mmsg, mtyping, mchip, mlink as vlink, POD_CSS as VPOD_CSS, mchat, MCONVO
    pod_note = (f'<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 12px">'
                f'{mchip("ask for voice", "V5MVoiceWait.dc.html", "kraft", 176, seed=1514, icon=MIC, h=44)}'
                f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.5;color:{PENCIL};text-align:right">CHECK-IN<br>IN 3:48</span></div>')
    def m_sys_line(text):
        """The pod's one opening line (who came to do what): pencil, centred, like the other system lines."""
        return (f'<div class="msg" data-slot="podOpening" style="--i:0;align-self:center;display:flex;align-items:center;gap:8px;{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">'
                f'<span style="width:22px;border-top:1px dashed {RULE}"></span><span>{text}</span><span style="width:22px;border-top:1px dashed {RULE}"></span></div>')
    # the opening line is the first thing in the message list (it scrolls away like any message)
    # (one exchange fewer than the voice boards, so the opening line is on screen at 390x844)
    pod_msgs = m_sys_line('moss_byte came to talk.') + ''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MCONVO) if i != 2)
    pod_sheet = mchat(pod_msgs, mtyping())

    def mpod(nudge=False):
        ov = ''
        if nudge:
            card = paper(f'''
<div style="{HAND};font-size:32px;line-height:1.15">It's been 10 minutes.</div>
<div style="{SERIF};font-size:16.5px;line-height:1.55;color:{INK};margin-top:10px">How are you doing? You can keep going, or end it gently. Either is okay.</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:22px">{tchip('keep going', '#', 'ink', 164, 48, 1521, fs=12)}{vlink('end gently', 'V5MPodEnd.dc.html', INK, 11, bold=False)}</div>
<div style="{TYPE};font-size:9px;letter-spacing:.14em;line-height:1.6;color:{PENCIL};margin-top:16px">THEY GET THE SAME QUESTION. NOBODY SEES WHAT THE OTHER PICKED.</div>''',
                         W - 8, 296, rot=-1, seed=1522, pad='30px 26px', tapes=tape((W - 8) / 2 - 50, -13, 100, 26, rot=3, seed=152))
            ov = f'<div class="veil"></div><div class="nudge">{card}</div>'
        return vpod(pod_sheet, overlay=ov, status='BOTH HERE', crumb=POD11)
    OPEN_CSS = '.scroll{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 18px);mask-image:linear-gradient(to bottom,transparent 0,#000 18px)}'
    mpage('V5MPod', 'Talk pod', mpod(), css=VPOD_CSS + OPEN_CSS)
    LV.pod('V5MPod')
    board('V5MPod', 'MT02 — Talk pod', MH, 'm_talk')
    mpage('V5MPodNudge', 'Talk pod, 10 minute check-in', mpod(True), css=VPOD_CSS + OPEN_CSS)
    LV.pod('V5MPodNudge')
    board('V5MPodNudge', 'MT03 — 10 minute check-in', MH, 'm_talk')

    # =====================================================================
    # MT04 — Pod ended: you were heard · two slips (yours to write, theirs to land) · stay and listen?
    # Both people see this at the same moment; each sends or skips on their own, and the notes cross.
    # =====================================================================
    pr = random.Random(19)
    motes = ''.join(f'<i class="mote" style="left:{pr.uniform(5, 95):.0f}%;width:{(s := pr.uniform(2, 4)):.1f}px;height:{s:.1f}px;animation-delay:{pr.uniform(0, 8):.1f}s;animation-duration:{pr.uniform(8, 13):.1f}s;--dx:{pr.uniform(-30, 30):.0f}px"></i>' for _ in range(18))
    end_css = f""".mote{{position:absolute;bottom:-10px;border-radius:50%;background:#CFCFCC;opacity:0;animation-name:mote;animation-iteration-count:infinite;animation-timing-function:linear;z-index:3}}
@keyframes mote{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:.4}}100%{{opacity:0;transform:translate(var(--dx),-760px)}}}}
.stampx{{position:absolute;{MARK};color:{RED};border:2.5px solid {RED};border-radius:5px;padding:1px 9px 0;letter-spacing:.06em;transform:rotate(-12deg);opacity:0;animation:stampin .5s cubic-bezier(.3,1.6,.5,1) var(--sw,1.6s) forwards;mix-blend-mode:multiply}}
@keyframes stampin{{from{{opacity:0;transform:rotate(-12deg) scale(1.7)}}to{{opacity:.88;transform:rotate(-12deg) scale(1)}}}}
.landed{{animation:landed .8s cubic-bezier(.2,.9,.3,1.2) var(--w,2.6s) both}}
@keyframes landed{{from{{opacity:0;transform:translateY(-14px) rotate(-3deg)}}to{{opacity:1;transform:none}}}}"""
    MRULED = 'background-image:repeating-linear-gradient(to bottom,transparent 0 27px,rgba(96,120,150,.18) 27px 28px)'
    def mlbl(t, c=PENCIL):
        return f'<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{c}">{t}</div>'
    def m_your_slip(sent=False):
        if sent:
            inner = (f'{mlbl("YOUR NOTE · PINNED FOR THEM")}'
                     f'<div style="position:relative;margin-top:10px;{MRULED};{HAND};font-size:21px;line-height:28px;color:{INK};padding-right:56px">thank you for not rushing me. i needed that tonight.</div>'
                     f'<div style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};margin-top:10px">SENT · GONE WHEN THEY LEAVE</div>'
                     f'<span class="stampx" style="right:16px;bottom:30px;font-size:22px">SENT</span>')
            tp = ctape(100, 26, -3, 1534, red=True)
        else:
            inner = (f'{mlbl("LEAVE THEM A NOTE · OPTIONAL")}'
                     f'<div data-slot="noteWrite" style="margin-top:10px">'
                     f'<div style="{MRULED};height:84px;{HAND};font-size:20px;line-height:28px;color:{PENCIL}">say thanks, or anything…<span class="blink" style="color:{INK}">|</span></div>'
                     f'<div style="display:flex;align-items:center;justify-content:space-between;margin-top:12px">'
                     f'<span style="display:flex;align-items:center;gap:16px">{tchip("pin it", "#", "ink", 104, 44, 1536, fs=12)}'
                     f'<a href="#" class="ul" style="display:inline-flex;align-items:center;min-height:44px;{TYPE};font-size:10.5px;letter-spacing:.16em;color:{INK}">SKIP</a></span>'
                     f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">0 / 140</span></div></div>')
            tp = ctape(100, 26, 3, 1535)
        return apaper(inner, -1.2, 'hi', 1533, '20px 22px 16px', tapes=tp)
    MPIN = ('<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true" style="position:absolute;left:50%;top:-12px;margin-left:-11px;overflow:visible">'
            '<ellipse cx="15" cy="18" rx="9" ry="5" fill="#000" opacity=".45"/><circle cx="12" cy="12" r="8" fill="#3a3a3d"/>'
            '<circle cx="12" cy="12" r="8" fill="none" stroke="#000" stroke-opacity=".35"/><circle cx="9.4" cy="9.4" r="2.3" fill="#fff" opacity=".28"/></svg>')
    def m_their_spot(landed=False):
        if landed:
            inner = (f'{mlbl("MOSS_BYTE&#39;S NOTE")}'
                     f'<div data-slot="theirNote" style="margin-top:10px;{MRULED};{HAND};font-size:21px;line-height:28px;color:{INK}">thanks for staying with me tonight. i feel lighter.</div>'
                     f'<div style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};margin-top:10px">ONLY YOU SEE THIS · GONE WHEN YOU LEAVE</div>')
            return f'<div class="landed" style="--w:2.8s">{apaper(inner, 1.4, "", 1537, "20px 22px 16px", tapes=ctape(96, 26, -4, 1538))}</div>'
        return (f'<div style="position:relative;transform:rotate(1deg);border:2px dashed rgba(163,154,140,.45);border-radius:3px;background:rgba(0,0,0,.2);padding:18px 20px 14px;display:flex;flex-direction:column;gap:10px">{MPIN}'
                f'{mlbl("MOSS_BYTE&#39;S NOTE", BOARDTXT)}'
                f'<div data-slot="theirNote" style="text-align:center;{HAND};font-size:20px;line-height:1.35;color:{BOARDTXT};padding:6px 0">if they leave you one,<br>it lands here.</div>'
                f'<div style="{TYPE};font-size:9px;letter-spacing:.14em;color:{BOARDTXT};text-align:center">THEY CAN WRITE OR SKIP, SAME AS YOU</div></div>')
    m_ask = apaper(f'''<div style="{HAND};font-size:22px;line-height:1.25;color:{INK}">someone's waiting to be heard. stay and listen?</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px">{tchip('stay and listen', 'V5MMatching.dc.html', 'ink', 180, 48, 1541, fs=11.5, pad=12)}<a href="#" class="ul" style="display:inline-flex;align-items:center;min-height:44px;white-space:nowrap;{TYPE};font-size:10.5px;letter-spacing:.16em;color:{INK}">NOT TONIGHT</a></div>''',
        -.8, 'kraft', 1539, '18px 22px 14px', tapes=ctape(90, 24, -5, 1540))

    def mpodend(notes=False):
        wait = '' if notes else (f'<sc-if value="{{{{someoneWaiting}}}}" hint-placeholder-val="{{{{ true }}}}">'
                                 f'<div class="rise" style="--w:3.4s;flex-shrink:0;margin-top:6px">{m_ask}</div></sc-if>')
        return f'''
<div aria-hidden="true" style="position:absolute;inset:0;pointer-events:none">{motes}</div>
{matmos(MPODEND_H if not notes else MPODEND_NOTES_H)}
{mtopbar(crumb=POD11)}
{mbody(f"""<div style="margin:auto 0;display:flex;flex-direction:column;gap:14px;flex-shrink:0">
<div style="display:flex;flex-direction:column;align-items:center;gap:8px;flex-shrink:0;padding-top:6px">
{h_hand('You were heard<br>tonight.', 40, color=PAPERHI, wait='1s', d='2s', extra='text-align:center')}
<div class="rise" style="--w:2.2s;{TYPE};font-size:10.5px;letter-spacing:.18em;color:rgba(233,233,231,.8);">18 MIN · 42 MESSAGES · 0 KEPT</div></div>
<div class="rise" style="--w:2.6s;flex-shrink:0;margin-top:14px">{m_your_slip(notes)}</div>
<div class="rise" style="--w:2.9s;flex-shrink:0;margin-top:{16 if notes else 10}px">{m_their_spot(notes)}</div>
{wait}
<div class="rise" style="--w:3.8s;flex-shrink:0;{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.6;color:{BOARDTXT};text-align:center;margin-top:4px">YOU'VE HEARD 4 PEOPLE<br>THIS BROWSER REMEMBERS, WE DON'T</div></div>""", gap=14)}
<div class="rise" style="--w:3.6s;display:flex;flex-direction:column">{mdock(mcta('back home', 'V5MHomeOpen.dc.html', 'paper', seed=1532) + mtext('talk to someone new', 'V5MMatching.dc.html'))}</div>
{mfooter()}'''
    MPODEND_H, MPODEND_NOTES_H = 950, MH
    mpage('V5MPodEnd', 'Pod ended', mpodend(), h=MPODEND_H, css=end_css, script='renderVals() { return { someoneWaiting: true }; }')
    LV.mark('V5MPodEnd', replace=[('18 MIN · 42 MESSAGES · 0 KEPT', '{{stats}}')])
    board('V5MPodEnd', 'MT04 — You were heard tonight · leave a note (scrolls)', MPODEND_H, 'm_talk')
    mpage('V5MPodEndNotes', 'Pod ended, notes crossed', mpodend(True), h=MPODEND_NOTES_H, css=end_css)
    LV.mark('V5MPodEndNotes', replace=[('18 MIN · 42 MESSAGES · 0 KEPT', '{{stats}}')])
    board('V5MPodEndNotes', 'MT04b — Notes crossed', MPODEND_NOTES_H, 'm_talk')

    # =====================================================================
    # MT05 — Tonight's question (group pod)
    # =====================================================================
    def person(name, state, me=False):
        wave = ('<svg width="34" height="14" viewBox="0 0 44 18" aria-hidden="true"><path class="talkwave" d="M0 9 Q4 1 8 9 T16 9 T24 9 T32 9 T40 9" fill="none" stroke="#C0662A" stroke-width="2.2" stroke-linecap="round"/></svg>'
                if state == 'speaking' else '')
        col = INK if state != 'muted' else PENCIL
        return (f'<div style="display:flex;align-items:center;justify-content:space-between;height:37px;border-bottom:1px dashed {RULE}">'
                f'<span style="{HAND};font-size:20px;color:{col};white-space:nowrap">{name}{" (you)" if me else ""}</span>'
                f'<span style="display:flex;align-items:center;gap:8px;{TYPE};font-size:9px;letter-spacing:.14em;color:{"#A8521E" if state == "speaking" else PENCIL}">{wave}{state.upper()}</span></div>')
    room = msheet(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 20)}<span style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL}">6 OF 8 · 2 SEATS OPEN</span></div>
<div style="margin-top:4px">{person('neon_moth', 'speaking')}{person('paper_kite', 'listening')}{person('static_heron', 'listening')}{person('dusk_signal', 'muted')}{person('lowkey_comet', 'listening')}{person('quiet_otter', 'listening', me=True)}</div>
<div style="{TYPE};font-size:9px;letter-spacing:.13em;color:{PENCIL};margin-top:12px;line-height:1.7">LET PEOPLE FINISH · LEAVING IS ALWAYS OKAY</div>''',
        kind='kraft', seed=1541, pad='22px 24px', rot=1, minh=318, tapes=ctape(100, 26, -3, 154))
    group_css = """.talkwave{stroke-dasharray:8 4;animation:tw .6s linear infinite}@keyframes tw{to{stroke-dashoffset:-24}}"""
    question = f'''
{matmos()}
{mtopbar(crumb="tonight's question", back='V5MHomeOpen.dc.html')}
{mbody(f'''
<div class="rise" style="--w:.1s;align-self:flex-start;padding:0 4px;{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">GROUP POD · OPEN UNTIL 2AM</div>
<div class="rise" style="--w:.2s;align-self:center;flex-shrink:0">{polaroid('moon', 286, 128, "What's something you pretend doesn't bother you?", rot=-2, seed=1542, u='mgq', capsize=23)}</div>
<div class="rise" style="--w:.6s;flex:1 0 auto;display:flex;flex-direction:column">{room}</div>''', gap=16)}
<div class="rise" style="--w:1.2s;display:flex;flex-direction:column">{mdock(mcta('join with voice', 'V5MPod.dc.html', 'paper', seed=1543) + mtext('just listen', 'V5MPod.dc.html'))}</div>
{mfooter()}'''
    mpage('V5MQuestion', "Tonight's question", question, css=group_css)
    LV.mark('V5MQuestion', slots=[('<div class="rise" style="--w:.6s;flex:1 0 auto;display:flex;flex-direction:column">', 'qroom'), ('<div class="rise" style="--w:1.2s;display:flex;flex-direction:column">', 'qdock')],
            replace=[("What's something you pretend doesn't bother you?", '{{question}}')])
    board('V5MQuestion', "MT05 — Tonight's question", MH, 'm_talk')

    # =====================================================================
    # MT06 — Pods asleep
    # =====================================================================
    sr = random.Random(13)
    stars = ''.join(f'<path class="tw" style="animation-delay:{sr.uniform(0, 4):.1f}s" d="M{x:.0f} {y - s:.1f} V{y + s:.1f} M{x - s:.1f} {y:.0f} H{x + s:.1f}" stroke="{CHALK}" stroke-width="1.2" stroke-linecap="round"/>'
                    for x, y, s in [(sr.uniform(30, 360), sr.uniform(10, 200), sr.uniform(2.5, 5)) for _ in range(14)])
    asleep_css = """.tw{animation:tw 3.6s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.2}50%{opacity:.9}}"""
    asleep = f'''
<svg aria-hidden="true" width="390" height="240" style="position:absolute;left:0;top:56px;z-index:2">{stars}
<path class="draw" style="--len:300;--d:2s" d="M300 40 A44 44 0 1 0 344 116 A35 35 0 1 1 300 40 Z" fill="rgba(237,230,216,.08)" stroke="{CHALK}" stroke-width="1.8"/></svg>
{matmos()}
{mtopbar()}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 {MPAD}px 30px">
<div class="fadein" style="--w:.2s">{rabbit(118, CHALK, mood='sleep', uid='masl')}</div>
{h_hand("Everyone's asleep.", 37, wait='.6s', extra='margin-top:14px;text-align:center;white-space:nowrap')}
<div class="rise" style="--w:1.6s;{SERIF};font-size:17px;line-height:1.5;color:{BOARDTXT};text-align:center;margin-top:6px">Pods open every night at 10.<br>That's in <span style="color:{CHALK}">1 hour 42 minutes</span>.</div>
<div class="rise" style="--w:2s;width:100%;margin-top:22px;{TYPE};font-size:10px;letter-spacing:.14em;color:{BOARDTXT}">
<div style="display:flex;align-items:center;gap:12px"><span style="white-space:nowrap">EMAIL ME AT 10PM</span><span style="flex-grow:1;border-bottom:1px solid {SOOT};height:14px"></span><a href="#" class="ul" style="color:{CHALK};white-space:nowrap">REMIND ME</a></div>
<div style="color:{BOARDTXT};margin-top:8px;font-size:9px">OPTIONAL · DELETED ONCE IT SENDS</div></div>
<div class="rise" style="--w:2.4s;width:100%;margin-top:26px;display:flex;flex-direction:column;align-items:center;gap:12px">
<div style="{MARK};font-size:21px;color:{SOFTRED};align-self:flex-start;margin-left:4px">until then</div>
<div style="display:grid;grid-template-columns:repeat(2,164px);gap:12px 14px">{m_scrap('get it out', 'BURN', 'V5MBurn.dc.html', -1.2, 1561)}{m_scrap('leave it somewhere', 'ECHOES', 'V5MEchoes.dc.html', 1, 1562, 'kraft')}{m_scrap("write, don't send", 'UNSENT', 'V5MUnsentWrite.dc.html', .8, 1564, 'kraft')}{m_scrap('hear it later', 'TIME CAPSULE', 'V5MCapsule.dc.html', -.6, 1563)}</div></div>
</main>
{mfooter()}'''
    mpage('V5MAsleep', 'Pods asleep', asleep, css=asleep_css)
    board('V5MAsleep', 'MT06 — Pods asleep', MH, 'm_talk')

    # =====================================================================
    # MT07 — Before you listen
    # =====================================================================
    def promise(n, title, line, last=False):
        bb = '' if last else f'border-bottom:1px dashed {RULE};'
        return (f'<div style="display:flex;gap:14px;padding:12px 0;{bb}">'
                f'<span style="{MARK};font-size:24px;line-height:1;color:{RED};width:16px;flex-shrink:0">{n}</span>'
                f'<div><div style="{HAND};font-size:23px;line-height:1.15;color:{INK}">{title}</div>'
                f'<div style="{SERIF};font-size:15px;line-height:1.45;color:{PENCIL};margin-top:3px">{line}</div></div></div>')
    promises = apaper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('three small promises', 19)}<span style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL}">LISTEN POD</span></div>
<div style="margin-top:4px">
{promise('1', 'No fixing.', "They don't need a plan. They need someone there.")}
{promise('2', 'No judging.', 'Whatever they say, it stays small and safe here.')}
{promise('3', 'Let them lead.', 'Ask, follow, leave room for quiet.', True)}</div>''',
        -1, 'hi', 1571, '22px 24px 16px', tapes=ctape(100, 26, 2, 157))
    heavy = msheet(f'''
<div style="{HAND};font-size:22px;line-height:1.2;color:{INK}">If it gets heavy</div>
<div style="{SERIF};font-size:14.5px;line-height:1.5;color:{INK};margin-top:6px">You're a kind stranger, not a professional. If they might be in danger, share the helpline. You can leave gently any time.</div>
<a href="V5MHelp.dc.html" class="ul" style="display:inline-block;margin-top:10px;{TYPE};font-weight:700;font-size:10.5px;letter-spacing:.14em;color:{RED}">HELPLINES, ONE TAP AWAY →</a>''',
        kind='kraft', seed=1572, pad='20px 22px', rot=1.2, minh=170)
    listener = f'''
{matmos()}
{mtopbar(crumb='listen pod', back='V5MHomeOpen.dc.html')}
{mbody(f'''<div style="flex-shrink:0;margin:0 -{MPAD}px">{mhead('Before you listen.', 36)}
<div class="rise" style="--w:1s;padding:2px {MPAD}px 0;{SERIF};font-size:15.5px;color:{BOARDTXT}">Someone out there needs to be heard tonight.</div>
<div class="rise" style="--w:1.2s;padding:6px {MPAD}px 0;{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">PODS OPEN UNTIL 2AM</div></div>
<div class="rise" style="--w:.5s;margin-top:8px;flex-shrink:0">{promises}</div>
<div class="rise" style="--w:1.1s;flex:1 0 auto;display:flex;flex-direction:column">{heavy}</div>''', gap=16)}
<div class="rise" style="--w:1.6s;display:flex;flex-direction:column">{mdock(mcta("I'm ready", 'V5MMatching.dc.html', 'ink', seed=1573) + mtext('not tonight', 'V5MHomeOpen.dc.html'))}</div>
{mfooter()}'''
    mpage('V5MListener', 'Before you listen', listener)
    board('V5MListener', 'MT07 — Before you listen (retired → V5MLeanListen)', MH, 'm_talk')

    # =====================================================================
    # MT00 — Tonight, I mostly want to… (one door, three slips, stacked)
    # =====================================================================
    from v5m_home import fcard
    MLEAN_CSS = """.lslip{display:block;transition:transform .25s ease,opacity .4s ease,filter .4s ease}
.lslip:active{transform:translateY(1px) scale(.99)}
.lslip.dim{opacity:.42;filter:saturate(.5) brightness(.9)}
.unfold{animation:unfold .9s cubic-bezier(.2,.8,.25,1) .35s both;transform-origin:50% 0}
@keyframes unfold{from{opacity:0;transform:scaleY(.3) rotate(-2deg)}to{opacity:1;transform:none}}
.crease{position:absolute;inset:0;pointer-events:none;background:linear-gradient(to bottom,transparent calc(33% - 1px),rgba(90,70,40,.10) 33%,rgba(255,255,255,.22) calc(33% + 1px),transparent calc(33% + 3px),transparent calc(66% - 1px),rgba(90,70,40,.10) 66%,rgba(255,255,255,.22) calc(66% + 1px),transparent calc(66% + 3px))}"""
    MLEANS = [  # (word, hint, kind, rot, seed, align)
        ('talk', "I'VE GOT SOMETHING ON MY MIND", '', -1.6, 1761, 'flex-start'),
        ('listen', "I'VE GOT ROOM FOR SOMEONE", 'hi', 1.2, 1762, 'flex-end'),
        ("either's fine", 'I JUST WANT SOME COMPANY', 'kraft', -.8, 1763, 'flex-start'),
    ]
    def m_lean_slip(i, href, picked=False, dim=False, small=False):
        word, hint, kind, rot, seed, al = MLEANS[i]
        circ = f'<span style="position:absolute;inset:0">{circle_scribble(112 if i == 0 else 190, 54, sw=2.2, wait="1.4s")}</span>' if picked else ''
        last = f'<span style="{MARK};font-size:17px;color:{RED};transform:rotate(4deg);flex-shrink:0">last time</span>' if picked else ''
        size = 24 if small else (34 if i < 2 else 30)
        hint_ = '' if small else f'<div style="{TYPE};font-size:9px;font-weight:700;letter-spacing:.14em;color:{PENCIL};padding-left:8px;margin-top:12px">{hint}</div>'
        inner = (f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">'
                 f'<span style="position:relative;display:inline-block;padding:0 8px;{HAND};font-size:{size}px;line-height:1.15;color:{INK};white-space:nowrap">{word}{circ}</span>{last}</div>{hint_}')
        pad = '10px 18px 8px' if small else '16px 20px 14px'
        return (f'<a href="{href}" class="lslip{" dim" if dim else ""}" aria-label="{word}" style="width:{80 if small else 90}%;align-self:{al}">'
                f'{fcard(inner, kind, seed, pad, rot=rot, tapes="" if small else ctape(80, 22, -rot * 2, seed + 10))}</a>')

    mlean = f'''
{matmos()}
{mtopbar(crumb=POD11, back='V5MHomeOpen.dc.html')}
{mbody(f"""<div style="flex-shrink:0;margin:0 -{MPAD}px">{mhead('Tonight, I mostly<br>want to…', 34)}
<div class="rise" style="--w:1.1s;padding:6px {MPAD}px 0;{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">PODS OPEN UNTIL 2AM</div></div>
<div class="rise" style="--w:.6s;margin:auto 0;padding:10px 0;display:flex;flex-direction:column;gap:22px;flex-shrink:0">
{m_lean_slip(0, 'V5MMatching.dc.html', picked=True)}{m_lean_slip(1, 'V5MLeanListen.dc.html')}{m_lean_slip(2, 'V5MMatching.dc.html')}</div>
<div class="rise" style="--w:1.6s;flex-shrink:0;{SERIF};font-style:italic;font-size:16px;line-height:1.5;color:{BOARDTXT};padding:0 4px">it only decides who we look for first. once you're in, you're just two people.</div>""", gap=14)}
<div class="rise" style="--w:2s;display:flex;flex-direction:column">{mdock(mtext('not tonight', 'V5MHomeOpen.dc.html') + mnote('TAP ONE · WE START<br>LOOKING STRAIGHT AWAY'))}</div>
{mfooter()}'''
    mpage('V5MLean', 'Tonight, I mostly want to', mlean, css=MLEAN_CSS)
    board('V5MLean', 'MT00 — Tonight, I mostly want to… (tap a slip)', MH, 'm_talk')

    # =====================================================================
    # MT00b — first "listen": the slip unfolds into the three small promises (shown once)
    # =====================================================================
    m_unfolded = apaper(f'''<div class="crease"></div>
<div style="position:relative;display:flex;justify-content:space-between;align-items:baseline">
<span style="{HAND};font-size:32px;line-height:1.1;color:{INK}">listen</span>{t_mark('three small promises', 19)}</div>
<div style="position:relative;margin-top:2px">
{promise('1', 'No fixing.', "They don't need a plan. They need someone there.")}
{promise('2', 'No judging.', 'Whatever they say, it stays small and safe here.')}
{promise('3', 'Let them lead.', 'Ask, follow, leave room for quiet.', True)}</div>''',
        .8, 'hi', 1762, '18px 22px 10px', tapes=ctape(96, 26, -3, 1772), extra='position:relative')
    mlean_listen = f'''
{matmos()}
{mtopbar(crumb=POD11, back='V5MHomeOpen.dc.html')}
{mbody(f"""<div style="flex-shrink:0;margin:0 -{MPAD}px">{mhead('Tonight, I mostly<br>want to…', 30)}</div>
<div style="margin:auto 0;display:flex;flex-direction:column;gap:16px;flex-shrink:0;padding:4px 0">
<div class="rise" style="--w:.2s;display:flex;flex-direction:column">{m_lean_slip(0, 'V5MMatching.dc.html', dim=True, small=True)}</div>
<div class="unfold">{m_unfolded}</div>
<div class="rise" style="--w:.3s;display:flex;flex-direction:column">{m_lean_slip(2, 'V5MMatching.dc.html', dim=True, small=True)}</div></div>""", gap=12)}
<div class="rise" style="--w:1.4s;display:flex;flex-direction:column">{mdock(mcta('okay, find someone', 'V5MMatching.dc.html', 'ink', seed=1773) + mnote("YOU'LL ONLY<br>SEE THIS ONCE."))}</div>
{mfooter()}'''
    mpage('V5MLeanListen', 'Tonight, I mostly want to listen', mlean_listen, css=MLEAN_CSS)
    board('V5MLeanListen', 'MT00b — First "listen": the slip unfolds (shown once)', MH, 'm_talk')


    # =====================================================================
    # MT08 — They left. Finding someone new.
    # =====================================================================
    rq_listeners = [(212, 40, -3, 731), (296, 112, 4, 732), (206, 186, -2, 733)]
    rq_html, rq_css = thread_loader('mr', 346, 262, (122, 128), (8, 40, 136, 100, -3), you_note(size=28, pad='22px 18px'), rq_listeners, slip=(86, 68), cycle=8.4, k=34, pin_r=7, sw=2)
    left_scrap = apaper(f'''
<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">11:58 PM</div>
<div style="position:relative;display:inline-block;margin-top:6px;{HAND};font-size:22px;color:{INK}">moss_byte left the pod
<svg width="100%" height="10" viewBox="0 0 220 10" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;left:0;top:34%;overflow:visible"><path class="draw" style="--len:240;--w:.9s;--d:.8s" d="M2 6 Q60 2 110 5 T218 4" fill="none" stroke="{PENCIL}" stroke-width="2" stroke-linecap="round"/></svg></div>
<div style="{SERIF};font-size:15.5px;line-height:1.5;color:{INK};margin-top:10px">It wasn't you. People leave for all kinds of reasons: a bad signal, a long day, a knock on the door.</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL};margin-top:12px">THE CHAT IS WIPED · NOTHING KEPT</div>''',
        -1.2, 'hi', 1581, '22px 24px', torn='bottom', tapes=ctape(100, 26, -2, 158))
    requeue = f'''
{matmos()}
{mtopbar(crumb=POD11, back='V5MHomeOpen.dc.html')}
{mbody(f'''<div style="flex-shrink:0;margin:0 -{MPAD}px">{mhead('They left.', 40)}</div>
<div class="rise" style="--w:.6s;margin-top:8px;flex-shrink:0">{left_scrap}</div>
<div class="rise" style="--w:1.4s;width:100%;padding:12px 0 0;flex-shrink:0">
{t_mark('finding someone new', 21, SOFTRED)}
<div style="{TYPE};font-size:10px;letter-spacing:.16em;line-height:1.6;color:{BOARDTXT};margin-top:4px">ALREADY LOOKING · USUALLY UNDER A MINUTE<br>PODS OPEN UNTIL 2AM</div></div>
<div class="fadein" style="--w:1.8s;flex:0 0 auto;display:flex;justify-content:center">{rq_html}</div>
<div class="rise" style="--w:2.2s;flex-shrink:0">
<div style="{SERIF};font-style:italic;font-size:15px;color:{BOARDTXT}">Need a minute first? That's fine.</div>
<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{BOARDTXT};margin-top:6px">OR LET IT GO ANOTHER WAY · ON YOUR OWN</div>
<div style="display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 14px;margin-top:12px">{m_scrap('get it out', 'BURN', 'V5MBurn.dc.html', -1.5, 1591)}{m_scrap('leave it somewhere', 'ECHOES', 'V5MEchoes.dc.html', 1.2, 1592, 'kraft')}{m_scrap("write, don't send", 'UNSENT', 'V5MUnsentWrite.dc.html', .8, 1593, 'kraft')}{m_scrap('hear it later', 'TIME CAPSULE', 'V5MCapsule.dc.html', -1, 1594)}</div></div>''')}
<div class="rise" style="--w:2.4s;display:flex;flex-direction:column">{mdock(mtext('stop looking', 'V5MHomeOpen.dc.html'))}</div>
{mfooter()}'''
    mpage('V5MRequeue', 'They left, finding someone new', requeue, h=1000, css=rq_css)
    LV.mark('V5MRequeue', replace=[('11:58 PM', '{{leftAt}}')])
    board('V5MRequeue', 'MT08 — They left. Finding someone new (scrolls)', 1000, 'm_talk')

    # =====================================================================
    # MT09 — Pods closed for you tonight
    # =====================================================================
    pfacts = paper(f'''
<div style="{SERIF};font-size:16px;line-height:1.55;color:{INK}">A few people ended their pods with you tonight, so we're closing the door for a while. It's not a ban, and nothing follows you.</div>
<div style="border-top:1px dashed {RULE};margin-top:14px;padding-top:12px;display:grid;grid-template-columns:96px 1fr;row-gap:8px;{TYPE};font-size:10px;letter-spacing:.1em;color:{INK}">
<span style="color:{PENCIL}">OPENS AGAIN</span><span>TOMORROW · 10PM</span><span style="color:{PENCIL}">KEPT</span><span>A COUNT · GONE BY MORNING</span></div>''',
        W, 192, rot=-.8, kind='hi', seed=1591, pad='22px 24px')
    paused = f'''
{matmos()}
{mtopbar()}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center">
<div style="width:100%;display:flex;align-items:flex-start;justify-content:space-between;padding:0 {MPAD}px 0 {MPAD}px">
<div style="padding-top:6px">{h_hand('Pods are closed<br>for you tonight.', 27, d='2s')}</div>
<div class="fadein" style="--w:.4s;margin-top:-4px;margin-right:-6px">{closed_sign(150, 100, 'closed<br>for tonight', '', 21, 1592, 7)}</div></div>
<div class="rise" style="--w:1s;margin-top:12px">{pfacts}</div>
<div class="rise" style="--w:1.6s;width:100%;margin-top:22px;display:flex;flex-direction:column;align-items:center;gap:11px">
<div style="width:100%;padding:0 {MPAD + 4}px;display:flex;justify-content:space-between;align-items:baseline">{t_mark('still open for you', 21, SOFTRED)}<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{BOARDTXT}">ON YOUR OWN</span></div>
<div style="display:grid;grid-template-columns:repeat(2,164px);gap:12px 14px">{m_scrap('get it out', 'BURN', 'V5MBurn.dc.html', -1.2, 1593)}{m_scrap('leave it somewhere', 'ECHOES', 'V5MEchoes.dc.html', 1, 1594, 'kraft')}{m_scrap("write, don't send", 'UNSENT', 'V5MUnsentWrite.dc.html', .8, 1596, 'kraft')}{m_scrap('hear it later', 'TIME CAPSULE', 'V5MCapsule.dc.html', -.6, 1595)}</div></div>
</main>
{mfooter()}'''
    mpage('V5MPaused', 'Pods closed for you tonight', paused, css=SIGN_CSS)
    board('V5MPaused', 'MT09 — Pods closed for you tonight', MH, 'm_talk')

    write_manifest()
    print('m talk ok')
