import re
"""N0TRACE V5 — 'Notes after dark'. Shared design system + helpers."""
import random, math, html as _html

import os as _os
OUT = _os.environ.get('V5_OUT', _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'out')) + '/'
FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700'
         '&amp;family=Covered+By+Your+Grace&amp;family=Nothing+You+Could+Do'
         '&amp;family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;1,6..72,300;1,6..72,400&amp;display=swap" rel="stylesheet">')

# ---------- tokens ----------
NIGHT, NIGHT2, SOOT, ASH, CHALK = '#0D0D0E', '#161618', '#2B2B2E', '#8A8A8F', '#E9E9E7'
PAPER, PAPER2, PAPERHI, KRAFT = '#EFE7D6', '#E4D9C3', '#F7F2E7', '#D8C6A4'
INK, PENCIL, RULE = '#221E1A', '#5F584E', '#D3C7B0'
RED = '#B8352A'
SOFTRED, CRISIS = '#F0A08F', '#E07A6E'   # soft red ink on the board; crisis link
BOARDTXT = '#A39A8C'                       # small type sitting directly on the board
GLOW, ROSE, DAWN = '#FFB86B', '#FF8F6B', '#FFD9A8'

HAND = "font-family: 'Nothing You Could Do', 'Caveat', cursive"
MARK = "font-family: 'Covered By Your Grace', 'Caveat', cursive"
TYPE = "font-family: 'Courier Prime', 'Courier New', monospace"
SERIF = "font-family: 'Newsreader', Georgia, serif"

NOISE_DARK = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
              "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/>"
              "<feColorMatrix values='0 0 0 0 .2  0 0 0 0 .15  0 0 0 0 .1  0 0 0 .28 0'/></filter>"
              "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")
NOISE_LIGHT = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
               "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/>"
               "<feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0'/></filter>"
               "<rect width='100%' height='100%' filter='url(%23n)'/></svg>\")")
FIBRES = ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
          "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.012 .09' numOctaves='2' seed='4'/>"
          "<feColorMatrix values='0 0 0 0 .45  0 0 0 0 .36  0 0 0 0 .22  0 0 0 .22 -.04'/></filter>"
          "<rect width='100%' height='100%' filter='url(%23f)'/></svg>\")")


def _svg(inner, w=600, h=600):
    return ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='%d' height='%d'>%s</svg>\")" % (w, h, inner))
ROOM_BLOTCH = _svg("<filter id='b'><feTurbulence type='fractalNoise' baseFrequency='.005' numOctaves='4' seed='9' stitchTiles='stitch'/>"
                   "<feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .49  .3 0 0 0 -.14'/></filter><rect width='100%' height='100%' filter='url(%23b)'/>", 900, 900)
ROOM_FIBRE = _svg("<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.008 .16' numOctaves='2' seed='3' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 .6  0 0 0 0 .6  0 0 0 0 .6  0 0 0 .075 -.02'/></filter><rect width='100%' height='100%' filter='url(%23f)'/>", 500, 500)
ROOM_DUST = _svg("<filter id='d'><feTurbulence type='fractalNoise' baseFrequency='.7' numOctaves='1' seed='5' stitchTiles='stitch'/>"
                 "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -14 0 0 0 4.4'/></filter><rect width='100%' height='100%' filter='url(%23d)'/>", 400, 400)
ROOM_SPECK = _svg("<filter id='s'><feTurbulence type='fractalNoise' baseFrequency='.55' numOctaves='1' seed='12' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 .8  0 0 0 0 .8  0 0 0 0 .78  16 0 0 0 -13.2'/></filter><rect width='100%' height='100%' filter='url(%23s)'/>", 420, 420)

LEATHER = _svg("<filter id='l' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.19' numOctaves='2' seed='4' stitchTiles='stitch' result='n'/>"
               "<feDiffuseLighting in='n' lighting-color='%23111113' surfaceScale='1.3' result='d'><feDistantLight azimuth='225' elevation='42'/></feDiffuseLighting>"
               "<feComposite in='d' in2='SourceGraphic' operator='in'/></filter><rect width='100%' height='100%' fill='black' filter='url(%23l)'/>", 360, 360)
LEATHER_FOLD = _svg("<filter id='c'><feTurbulence type='fractalNoise' baseFrequency='.0035 .006' numOctaves='3' seed='21' stitchTiles='stitch' result='n'/>"
                    "<feDiffuseLighting in='n' lighting-color='white' surfaceScale='9' result='d'><feDistantLight azimuth='225' elevation='55'/></feDiffuseLighting>"
                    "<feColorMatrix in='d' values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  .25 0 0 0 -.19'/></filter><rect width='100%' height='100%' filter='url(%23c)'/>", 1100, 1100)

CORK_LIGHT = _svg("<filter id='a'><feTurbulence type='fractalNoise' baseFrequency='.3' numOctaves='2' seed='31' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 .135  0 0 0 0 .132  0 0 0 0 .128  1.1 0 0 0 -.6'/></filter><rect width='100%' height='100%' filter='url(%23a)'/>", 300, 300)
CORK_DARK = _svg("<filter id='k'><feTurbulence type='fractalNoise' baseFrequency='.26' numOctaves='2' seed='77' stitchTiles='stitch'/>"
                 "<feColorMatrix values='0 0 0 0 .03  0 0 0 0 .03  0 0 0 0 .03  -1.1 0 0 0 .48'/></filter><rect width='100%' height='100%' filter='url(%23k)'/>", 300, 300)
CORK_CHUNK = _svg("<filter id='c' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.07' numOctaves='2' seed='5' stitchTiles='stitch' result='n'/>"
                  "<feDiffuseLighting in='n' lighting-color='%23ffffff' surfaceScale='1.6' result='d'><feDistantLight azimuth='225' elevation='60'/></feDiffuseLighting>"
                  "<feColorMatrix in='d' values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  .12 0 0 0 -.09'/></filter><rect width='100%' height='100%' filter='url(%23c)'/>", 420, 420)

BASE_CSS = f"""*{{box-sizing:border-box}}
body{{margin:0;background:{NIGHT};color:{CHALK};{TYPE}}}
a{{color:inherit;text-decoration:none}}
button{{font:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer}}
::selection{{background:rgba(255,184,107,.35)}}
a:focus-visible,button:focus-visible,textarea:focus-visible,input:focus-visible,[role=button]:focus-visible{{outline:2px dashed {CHALK};outline-offset:5px;box-shadow:0 0 0 7px rgba(13,13,14,.55)}}
.paper a:focus-visible,.paper button:focus-visible{{outline-color:{INK};box-shadow:none}}
.grain{{position:absolute;inset:0;pointer-events:none;background-image:{NOISE_LIGHT};opacity:.06;z-index:50}}
.room{{position:absolute;inset:0;z-index:0;pointer-events:none;background-color:#0b0b0b;background-image:{CORK_LIGHT},{CORK_DARK},{CORK_CHUNK},linear-gradient(165deg,#111111,#0a0a0a 55%,#050505)}}
.room::after{{content:'';position:absolute;inset:0;border:14px solid #080808;box-shadow:inset 0 0 0 1px rgba(255,255,255,.05),inset 0 10px 22px rgba(0,0,0,.75),inset 0 -4px 14px rgba(0,0,0,.5)}}
.traces{{position:absolute;inset:0;z-index:1;pointer-events:none}}
.room.m::after{{border-width:7px;box-shadow:inset 0 0 0 1px rgba(255,255,255,.05),inset 0 6px 14px rgba(0,0,0,.75),inset 0 -3px 10px rgba(0,0,0,.5)}}
.vignette{{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse 75% 70% at 50% 45%,transparent 55%,rgba(0,0,0,.55));z-index:49}}
.paper{{position:relative;background-color:{PAPER};background-image:{NOISE_DARK},{FIBRES},radial-gradient(ellipse 80% 75% at 45% 40%,rgba(255,252,242,.45),transparent 62%),radial-gradient(ellipse at 50% 50%,transparent 64%,rgba(140,100,50,.16));color:{INK}}}
.paper.kraft{{background-color:{KRAFT}}}
.paper.hi{{background-color:{PAPERHI}}}
.paper.dusk{{background-color:#232325;color:{CHALK}}}
.lift{{filter:drop-shadow(0 18px 26px rgba(0,0,0,.5)) drop-shadow(0 2px 3px rgba(0,0,0,.35))}}
.tape{{position:absolute;background-color:rgba(226,212,176,.62);background-image:{NOISE_DARK};box-shadow:0 1px 2px rgba(0,0,0,.18);z-index:5}}
.tape.red{{background-color:rgba(184,53,42,.55)}}
.hand{{{HAND}}}.mark{{{MARK}}}.type{{{TYPE}}}.serif{{{SERIF}}}
/* light leaks */
.leak{{position:absolute;border-radius:50%;pointer-events:none;mix-blend-mode:screen;filter:blur(40px);animation:leak 11s ease-in-out infinite;z-index:40}}
@keyframes leak{{0%,100%{{opacity:.22;transform:translate(0,0) scale(.92)}}45%{{opacity:.4;transform:translate(14px,-10px) scale(1.06)}}62%{{opacity:.55;transform:translate(10px,-6px) scale(1.12)}}70%{{opacity:.34}}}}
.flare{{position:absolute;inset:-20%;pointer-events:none;mix-blend-mode:screen;background:linear-gradient(105deg,transparent 35%,rgba(255,200,140,.0) 42%,rgba(255,196,130,.13) 50%,rgba(255,150,100,.0) 58%,transparent 65%);animation:flare 14s ease-in-out infinite;z-index:41}}
@keyframes flare{{0%,72%{{transform:translateX(-60%);opacity:0}}78%{{opacity:1}}92%{{transform:translateX(60%);opacity:0}}100%{{transform:translateX(60%);opacity:0}}}}
/* writing on */
.write{{clip-path:inset(-30% 100% -30% -2%);animation:write var(--d,1.6s) cubic-bezier(.5,.1,.3,1) var(--w,.2s) forwards}}
@keyframes write{{to{{clip-path:inset(-30% -3% -30% -2%)}}}}
.draw{{stroke-dasharray:var(--len,600);stroke-dashoffset:var(--len,600);animation:draw var(--d,1.2s) ease-out var(--w,.4s) forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.rise{{opacity:0;transform:translateY(10px);animation:rise 1.1s cubic-bezier(.2,.7,.2,1) var(--w,.3s) forwards}}
@keyframes rise{{to{{opacity:1;transform:none}}}}
.fadein{{opacity:0;animation:fadein 1.4s ease var(--w,.3s) forwards}}
@keyframes fadein{{to{{opacity:1}}}}
.breathe{{animation:breathe 7s ease-in-out infinite}}
@keyframes breathe{{0%,100%{{transform:scale(.97)}}50%{{transform:scale(1.02)}}}}
.blink{{animation:blink 1.1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.eyes{{transform-box:fill-box;transform-origin:center;animation:eyes 5s infinite}}
@keyframes eyes{{0%,92%,100%{{transform:scaleY(1)}}95%{{transform:scaleY(.12)}}}}
/* interactive rows */
.row{{position:relative;display:flex;align-items:center;justify-content:space-between;gap:20px}}
.row .go{{transition:transform .25s ease}}
.row:hover .go{{transform:translateX(4px)}}
.row .scribble{{position:absolute;left:-6px;bottom:6px;width:0;height:16px;overflow:hidden;transition:width .45s cubic-bezier(.5,.1,.2,1)}}
.row:hover .scribble{{width:var(--sw,240px)}}
.chip{{transition:transform .2s ease}}
.chip.inkc{{filter:drop-shadow(0 2px 0 rgba(0,0,0,.35)) drop-shadow(0 6px 10px rgba(0,0,0,.25))}}
.chip:hover{{transform:rotate(-1deg) translateY(-2px)}}
.chip:active{{transform:rotate(0) translateY(1px) scale(.98)}}
.ldots i{{font-style:normal;animation:ldot 1.4s infinite}}.ldots i:nth-child(2){{animation-delay:.2s}}.ldots i:nth-child(3){{animation-delay:.4s}}
@keyframes ldot{{0%,60%,100%{{opacity:.2}}30%{{opacity:1}}}}
.ul{{background-image:linear-gradient({RED},{RED});background-size:0 2px;background-repeat:no-repeat;background-position:0 100%;transition:background-size .35s ease;padding-bottom:3px}}
.ul:hover{{background-size:100% 2px}}
@media (prefers-reduced-motion: reduce){{*{{animation-duration:.01s !important;animation-iteration-count:1 !important;transition:none !important}}.write{{clip-path:none}}}}
"""

# ---------- shape helpers ----------
def deckle(w, h, amp=2.4, step=16, seed=1, torn=None):
    """Return a clip-path polygon with rough, hand-torn edges.
    Points are relative (percent of the box + a px wobble), so the same sheet can stretch to any
    phone width or fill any height without the torn edge breaking. w/h only set how many teeth.
    torn: one of 'top','bottom' to make that edge strongly torn."""
    r = random.Random(seed)
    def j(a):
        return r.uniform(-a, a)
    def P(fx, dx, fy, dy):
        def c(f, d):
            if abs(d) < .05:
                return f'{f * 100:.2f}%'
            if f == 0:
                return f'{d:.1f}px'
            return f'calc({f * 100:.2f}% {"+" if d >= 0 else "-"} {abs(d):.1f}px)'
        return f'{c(fx, dx)} {c(fy, dy)}'
    pts = []
    def edge(side, length, a):
        n = max(2, int(length / step))
        for i in range(n):
            t = i / n
            d = j(a)
            if side == 't': pts.append(P(t, 0, 0, d))
            elif side == 'r': pts.append(P(1, d, t, 0))
            elif side == 'b': pts.append(P(1 - t, 0, 1, d))
            else: pts.append(P(0, d, 1 - t, 0))
    edge('t', w, amp * (4 if torn == 'top' else 1))
    edge('r', h, amp)
    edge('b', w, amp * (4 if torn == 'bottom' else 1))
    edge('l', h, amp)
    return 'polygon(' + ','.join(pts) + ')'

def tape(x, y, w=110, h=30, rot=-6, red=False, seed=3):
    r = random.Random(seed)
    # zig-zag torn ends
    left = [(r.uniform(0, 5), i * h / 6) for i in range(7)]
    right = [(w - r.uniform(0, 5), h - i * h / 6) for i in range(7)]
    poly = 'polygon(' + ','.join(f'{a:.1f}px {b:.1f}px' for a, b in left + right) + ')'
    return f'<span class="tape{" red" if red else ""}" aria-hidden="true" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg);clip-path:{poly}"></span>'

def paper(inner, w, h, rot=0, kind='', seed=1, pad='36px 40px', extra='', torn=None, tapes='', cls=''):
    """A sheet of paper. Outer handles shadow+rotation, inner is clipped to a deckled edge."""
    return (f'<div class="lift {cls}" style="position:relative;width:{w}px;max-width:100%;height:{h}px;transform:rotate({rot}deg);flex-shrink:0;{extra}">'
            f'<div class="paper {kind}" style="position:absolute;inset:0;padding:{pad};clip-path:{deckle(w, h, seed=seed, torn=torn)}">{inner}</div>{tapes}</div>')

def leak(x, y, size=520, color=GLOW, delay=0, op=None, dur=11):
    return ''  # light leaks retired in the paper-room update
    o = f'opacity:{op};' if op is not None else ''
    return (f'<div class="leak" aria-hidden="true" style="left:{x}px;top:{y}px;width:{size}px;height:{size}px;'
            f'background:radial-gradient(circle,{color} 0%,rgba(255,143,107,.35) 38%,transparent 68%);'
            f'animation-delay:{delay}s;animation-duration:{dur}s;{o}"></div>')

_ATM = [0]
def traces(w=1440, h=900, seed=None):
    """Signs of a board that's been used: pin holes, tape ghosts, staples, a scrap, a couple of pins."""
    _ATM[0] += 1
    import sys as _sys, zlib as _z
    r = random.Random(seed if seed is not None else _z.crc32(_sys.argv[0].encode()) + 97 * _ATM[0])
    if w < 600:  # phone: a smaller, quieter patch of board; marks hug the side edges only
        out = []
        for _ in range(12):
            x, y = (r.choice([r.uniform(12, 30), r.uniform(w - 30, w - 12)]), r.uniform(70, h - 40)) if r.random() < .6 else (r.uniform(20, w - 20), r.uniform(70, h - 40))
            out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='1.5' fill='#000' opacity='.9'/><circle cx='{x - .6:.1f}' cy='{y - .6:.1f}' r='2.2' fill='none' stroke='#5a5753' stroke-width='.6' opacity='.35'/>")
        for side in ('l', 'r'):
            x = r.uniform(4, 18) if side == 'l' else r.uniform(w - 70, w - 50); y = r.uniform(140, h - 160); rot = r.uniform(-30, 30)
            out.append(f"<rect x='{x:.0f}' y='{y:.0f}' width='60' height='18' fill='#cfc6ad' opacity='.045' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>")
        # (no push-pin on phone: on a stretched frame it can land on the paper edge or the dock)
        return f"<svg class='traces' aria-hidden='true' width='{w}' height='{h}' viewBox='0 0 {w} {h}' preserveAspectRatio='none'>{''.join(out)}</svg>"
    def edgept():
        side = r.choice(['l', 'r', 'b', 'b', 't'])
        if side == 'l': return r.uniform(24, 130), r.uniform(110, h - 88)
        if side == 'r': return r.uniform(w - 140, w - 24), r.uniform(110, h - 88)
        if side == 't': return r.uniform(160, w - 160), r.uniform(70, 96)
        return r.uniform(40, w - 40), r.uniform(h - 138, h - 88)
    out = []
    for _ in range(26):
        x, y = (r.uniform(20, w - 20), r.uniform(20, h - 20)) if r.random() < .55 else edgept()
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='1.6' fill='#000' opacity='.9'/><circle cx='{x - .6:.1f}' cy='{y - .6:.1f}' r='2.4' fill='none' stroke='#5a5753' stroke-width='.6' opacity='.35'/>")
    for _ in range(4):
        x, y = edgept(); tw, th = r.uniform(60, 110), r.uniform(18, 26); rot = r.uniform(-25, 25)
        out.append(f"<rect x='{x:.0f}' y='{y:.0f}' width='{tw:.0f}' height='{th:.0f}' fill='#cfc6ad' opacity='.045' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>"
                   f"<rect x='{x:.0f}' y='{y:.0f}' width='{tw:.0f}' height='{th:.0f}' fill='none' stroke='#cfc6ad' stroke-width='.8' stroke-dasharray='3 2' opacity='.06' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>")
    for _ in range(3):
        x, y = edgept(); rot = r.uniform(-40, 40)
        out.append(f"<g transform='rotate({rot:.0f} {x:.0f} {y:.0f})' opacity='.55'><rect x='{x:.0f}' y='{y:.0f}' width='14' height='2' rx='.8' fill='#8d8b88'/><rect x='{x:.0f}' y='{y + 2:.0f}' width='14' height='1' fill='#000' opacity='.6'/></g>")
    x, y = edgept()
    out.append(f"<g opacity='.42'><path d='M{x:.0f} {y:.0f} l34 -6 l-8 30 l-6 -9 l-9 6 z' fill='#d9d0bd'/></g>"
               f"<circle cx='{x + 12:.0f}' cy='{y + 4:.0f}' r='5' fill='#2a2a2c'/><circle cx='{x + 10.5:.1f}' cy='{y + 2.5:.1f}' r='1.6' fill='#77777a'/>")
    for col in [r.choice(['#7a2a22', '#2b2b2e', '#5d5d61']), r.choice(['#2b2b2e', '#8b8b8f'])]:
        x, y = edgept()
        out.append(f"<g opacity='.9'><ellipse cx='{x + 4:.0f}' cy='{y + 6:.0f}' rx='9' ry='5' fill='#000' opacity='.45'/>"
                   f"<circle cx='{x:.0f}' cy='{y:.0f}' r='7.5' fill='{col}'/><circle cx='{x:.0f}' cy='{y:.0f}' r='7.5' fill='none' stroke='#000' stroke-opacity='.35'/>"
                   f"<circle cx='{x - 2.5:.1f}' cy='{y - 2.5:.1f}' r='2.2' fill='#fff' opacity='.22'/></g>")
    return f"<svg class='traces' aria-hidden='true' width='{w}' height='{h}' viewBox='0 0 {w} {h}' preserveAspectRatio='none'>{''.join(out)}</svg>"

def atmos(leaks='', w=1440, h=900):
    m = ' m' if w < 600 else ''
    return f'<div class="room{m}" aria-hidden="true"></div>' + traces(w, h) + '<div class="vignette"></div><div class="grain"></div>'

def matmos(h=844):
    return atmos(w=390, h=h)


# ---------- the hand-drawn rabbit (Damn_It_Rabbit) ----------
ROUGH = ('<filter id="rough{i}" x="-10%" y="-10%" width="120%" height="120%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="{s}"/>'
         '<feDisplacementMap in="SourceGraphic" scale="{sc}"/></filter>')
def rabbit(w=120, color=INK, mood='idle', draw=False, uid='r', blink=True):
    h = int(w * 0.75)
    f = ROUGH.format(i=uid, s=7, sc=3)
    if draw:
        eyes_l = f'<path class="draw" style="--len:140;--d:.9s;--w:.4s" d="M16 13 L45 11 L47 41 L15 42 Z" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'
        eyes_r = f'<path class="draw" style="--len:140;--d:.9s;--w:.9s" d="M74 12 L104 13 L103 42 L73 41 Z" fill="none" stroke="{color}" stroke-width="3" stroke-linejoin="round"/>'
        fills = (f'<g class="fadein" style="--w:1.6s"><g class="eyes"><path d="M16 13 L45 11 L47 41 L15 42 Z" fill="{color}"/>'
                 f'<path d="M74 12 L104 13 L103 42 L73 41 Z" fill="{color}"/></g></g>')
        mouth = f'<path class="draw" style="--len:60;--d:.7s;--w:1.5s" d="M45 64 L52 71 L59 64 L66 71 L73 64" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
        body = eyes_l + eyes_r + fills + mouth
    elif mood == 'sleep':
        body = (f'<path d="M15 30 Q31 36 47 29" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M73 29 Q89 36 104 30" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
                f'<path d="M48 64 L54 69 L60 64 L66 69 L72 64" fill="none" stroke="{color}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'
                f'<text x="104" y="10" fill="{color}" style="{HAND};font-size:16px">z<animate attributeName="opacity" values="0;1;0" dur="3s" repeatCount="indefinite"/></text>')
    else:
        cls = ' class="eyes"' if blink else ''
        body = (f'<g{cls}><path d="M16 13 L45 11 L47 41 L15 42 Z" fill="{color}"/>'
                f'<path d="M74 12 L104 13 L103 42 L73 41 Z" fill="{color}"/></g>'
                f'<path d="M45 64 L52 71 L59 64 L66 71 L73 64" fill="none" stroke="{color}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 120 90" aria-hidden="true" style="overflow:visible">'
            f'<defs>{f}</defs><g filter="url(#rough{uid})">{body}</g></svg>')

def wordmark(size=15, color=CHALK, gap='.32em'):
    return f'<span style="{TYPE};font-weight:700;font-size:{size}px;letter-spacing:{gap};color:{color}">N0TRACE</span>'

# ---------- scribbles ----------
def underline(w=220, color=RED, sw=3, seed=2, cls='draw', d='.9s', wait='.6s'):
    r = random.Random(seed)
    y = 8
    pts = [f'M2 {y + r.uniform(-1.5, 1.5):.1f}']
    for i in range(1, 7):
        pts.append(f'Q{w * (i - .5) / 6:.0f} {y + r.uniform(-3, 3):.1f} {w * i / 6:.0f} {y + r.uniform(-1.5, 1.5):.1f}')
    return (f'<svg width="{w}" height="16" viewBox="0 0 {w} 16" aria-hidden="true" style="display:block;overflow:visible">'
            f'<path class="{cls}" style="--len:{w * 1.3:.0f};--d:{d};--w:{wait}" d="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/></svg>')

def circle_scribble(w=260, h=70, color=RED, sw=2.5, cls='draw', wait='.4s'):
    rx, ry = w / 2 - 6, h / 2 - 6
    d = (f'M{w / 2 + rx * .2:.0f} {6:.0f} C{w - 4} {2} {w + 6} {h - 8} {w / 2 + 10} {h - 3} '
         f'C{14} {h + 2} {-4} {h / 2 + 4} {w * .2:.0f} {h * .2:.0f} C{w * .35:.0f} {2} {w * .6:.0f} {4} {w * .7:.0f} {12}')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);overflow:visible;pointer-events:none">'
            f'<path class="{cls}" style="--len:{(w + h) * 2.4:.0f};--w:{wait}" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/></svg>')

def arrow_doodle(w=60, h=40, color=CHALK, flip=False, wait='.8s'):
    t = ' transform="scale(-1,1) translate(-60,0)"' if flip else ''
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 60 40" aria-hidden="true" style="overflow:visible"><g{t}>'
            f'<path class="draw" style="--len:90;--w:{wait}" d="M4 6 C20 2 44 8 50 30" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round"/>'
            f'<path class="draw" style="--len:30;--w:calc({wait} + .5s)" d="M42 25 L50 32 L55 22" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g></svg>')

# ---------- generated film photos (no stock images) ----------
PHOTO_GRAIN = ('<filter id="pg{u}"><feTurbulence type="fractalNoise" baseFrequency=".95" numOctaves="2" seed="{s}"/>'
               '<feColorMatrix values="0 0 0 0 .5  0 0 0 0 .45  0 0 0 0 .4  0 0 0 .55 0"/>'
               '<feComposite in2="SourceGraphic" operator="in"/></filter>'
               '<filter id="soft{u}"><feGaussianBlur stdDeviation="{b}"/></filter>')
def scene(kind, w, h, u='p'):
    defs = PHOTO_GRAIN.format(u=u, s=3, b=6)
    if kind == 'moon':
        g = (f'<linearGradient id="s{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2430"/><stop offset=".62" stop-color="#3a4250"/><stop offset=".63" stop-color="#20252c"/><stop offset="1" stop-color="#121418"/></linearGradient>')
        body = (f'<rect width="{w}" height="{h}" fill="url(#s{u})"/>'
                f'<circle cx="{w * .68:.0f}" cy="{h * .3:.0f}" r="{w * .18:.0f}" fill="#f6e7c4" opacity=".25" filter="url(#soft{u})"/>'
                f'<circle cx="{w * .68:.0f}" cy="{h * .3:.0f}" r="{w * .065:.0f}" fill="#f3e6c8"/>'
                f'<rect x="{w * .63:.0f}" y="{h * .64:.0f}" width="{w * .1:.0f}" height="{h * .3:.0f}" fill="#e9d9b5" opacity=".28" filter="url(#soft{u})"/>'
                f'<path d="M0 {h * .63:.0f} L{w} {h * .62:.0f}" stroke="#4a515c" stroke-width="1"/>')
    elif kind == 'dawn':
        g = (f'<linearGradient id="s{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2a36"/><stop offset=".45" stop-color="#7d5e5a"/><stop offset=".72" stop-color="#e3a46e"/><stop offset="1" stop-color="#f1cf9a"/></linearGradient>')
        body = (f'<rect width="{w}" height="{h}" fill="url(#s{u})"/>'
                f'<circle cx="{w * .5:.0f}" cy="{h * .8:.0f}" r="{w * .3:.0f}" fill="#ffd9a0" opacity=".45" filter="url(#soft{u})"/>'
                f'<circle cx="{w * .5:.0f}" cy="{h * .8:.0f}" r="{w * .09:.0f}" fill="#fff0cf"/>'
                f'<path d="M0 {h * .78:.0f} C{w * .2:.0f} {h * .7:.0f} {w * .35:.0f} {h * .74:.0f} {w * .5:.0f} {h * .79:.0f} C{w * .65:.0f} {h * .72:.0f} {w * .8:.0f} {h * .69:.0f} {w} {h * .76:.0f} L{w} {h} L0 {h} Z" fill="#2b221f"/>'
                f'<path d="M{w * .18:.0f} {h * .36:.0f} q6 -5 12 0 q6 -5 12 0" fill="none" stroke="#2b2422" stroke-width="2"/>')
    elif kind == 'window':
        g = f'<linearGradient id="s{u}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#191715"/><stop offset="1" stop-color="#0e0d0c"/></linearGradient>'
        body = (f'<rect width="{w}" height="{h}" fill="url(#s{u})"/>'
                f'<rect x="{w * .3:.0f}" y="{h * .18:.0f}" width="{w * .4:.0f}" height="{h * .5:.0f}" fill="#f4b46c" opacity=".6" filter="url(#soft{u})"/>'
                f'<rect x="{w * .33:.0f}" y="{h * .21:.0f}" width="{w * .34:.0f}" height="{h * .44:.0f}" fill="#f7c98c"/>'
                f'<path d="M{w * .5:.0f} {h * .21:.0f} V{h * .65:.0f} M{w * .33:.0f} {h * .43:.0f} H{w * .67:.0f}" stroke="#2a1d14" stroke-width="5"/>'
                f'<path d="M{w * .33:.0f} {h * .65:.0f} L{w * .15:.0f} {h} L{w * .85:.0f} {h} L{w * .67:.0f} {h * .65:.0f} Z" fill="#f4b46c" opacity=".12"/>')
    elif kind == 'lamp':
        g = f'<linearGradient id="s{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121417"/><stop offset="1" stop-color="#262522"/></linearGradient>'
        body = (f'<rect width="{w}" height="{h}" fill="url(#s{u})"/>'
                f'<path d="M{w * .42:.0f} {h * .22:.0f} L{w * .1:.0f} {h} L{w * .9:.0f} {h} Z" fill="#ffcf8a" opacity=".22" filter="url(#soft{u})"/>'
                f'<circle cx="{w * .42:.0f}" cy="{h * .22:.0f}" r="{w * .16:.0f}" fill="#ffc985" opacity=".45" filter="url(#soft{u})"/>'
                f'<circle cx="{w * .42:.0f}" cy="{h * .22:.0f}" r="{w * .03:.0f}" fill="#fff1d6"/>'
                f'<path d="M{w * .42:.0f} {h * .24:.0f} L{w * .42:.0f} {h * .2:.0f} Q{w * .42:.0f} {h * .12:.0f} {w * .52:.0f} {h * .12:.0f} L{w * .52:.0f} {h}" fill="none" stroke="#0b0b0b" stroke-width="5"/>')
    else:  # sky + bird
        g = f'<linearGradient id="s{u}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7f9aa3"/><stop offset="1" stop-color="#c9c4b4"/></linearGradient>'
        body = (f'<rect width="{w}" height="{h}" fill="url(#s{u})"/>'
                f'<ellipse cx="{w * .65:.0f}" cy="{h * .55:.0f}" rx="{w * .35:.0f}" ry="{h * .25:.0f}" fill="#efe9dc" filter="url(#soft{u})"/>'
                f'<ellipse cx="{w * .3:.0f}" cy="{h * .2:.0f}" rx="{w * .2:.0f}" ry="{h * .08:.0f}" fill="#e8e3d6" opacity=".8" filter="url(#soft{u})"/>'
                f'<path d="M{w * .35:.0f} {h * .45:.0f} q10 -9 20 -2 q10 -9 20 2 q-10 -3 -20 4 q-10 -7 -20 -4z" fill="#1b1a19"/>'
                f'<path d="M0 {h * .86:.0f} q40 -30 70 -10 q30 -25 60 -5 q40 -28 80 0 L{w} {h * .8:.0f} L{w} {h} L0 {h} Z" fill="#1d241e"/>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block">'
            f'<defs>{defs}{g}</defs>{body}<rect width="{w}" height="{h}" filter="url(#pg{u})" opacity=".55"/>'
            f'<rect width="{w}" height="{h}" fill="#c9a77a" opacity=".07"/></svg>')

def polaroid(kind, w, h, caption='', rot=-2, seed=5, u='p', capsize=22, tapes=True):
    import re as _re
    _plain = _re.sub('<[^>]+>', ' ', caption)
    lines = (caption.count('<br>') + 1) if '<br>' in caption else max(1, -(-len(_plain) * capsize * .56 // (w - 8)))
    pw, ph = w + 28, h + (int(30 + lines * capsize * 1.3 + 12) if caption else 32)
    cap = f'<div style="{HAND};font-size:{capsize}px;line-height:1.25;color:{INK};padding:14px 4px 0">{caption}</div>' if caption else ''
    tp = tape(pw / 2 - 55, -14, 110, 28, rot=3, seed=seed) if tapes else ''
    return paper(f'{scene(kind, w, h, u)}{cap}', pw, ph, rot=rot, kind='hi', seed=seed, pad='14px 14px', tapes=tp)

# ---------- text atoms ----------
def h_hand(t, size=56, color=CHALK, wait='.2s', d='1.6s', extra=''):
    return f'<div class="write" style="--w:{wait};--d:{d};{HAND};font-size:{size}px;line-height:1.22;color:{color};{extra}">{t}</div>'

def t_type(t, size=13, color=ASH, ls='.14em', extra=''):
    return f'<div style="{TYPE};font-size:{size}px;letter-spacing:{ls};text-transform:uppercase;color:{color};{extra}">{t}</div>'

def t_mark(t, size=22, color=RED, extra=''):
    return f'<div style="{MARK};font-size:{size}px;line-height:1.1;color:{color};{extra}">{t}</div>'

def chip(label, href='#', kind='paper', w=None, seed=11, onclick=None, extra='', state=''):
    """Primary action: a torn paper chip with typewriter text. kind: paper | ink | kraft.
    state: '' | 'disabled' (faded, not clickable, says why nearby) | 'loading' (dots after the label)"""
    if state == 'disabled':
        extra += ';opacity:.38;filter:saturate(.4);pointer-events:none;cursor:default'
    if state == 'loading':
        label = label + '<span class="ldots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span>'
    ww = w or (len(re.sub('<[^>]+>', '', label)) * 10 + 84)
    bg = {'paper': f'background-color:{PAPERHI};color:{INK}', 'ink': f'background-color:{INK};color:{PAPERHI}',
          'kraft': f'background-color:{KRAFT};color:{INK}'}[kind]
    inner = (f'<span class="paper" style="position:absolute;inset:0;{bg};clip-path:{deckle(ww, 54, amp=1.6, step=12, seed=seed)}"></span>'
             f'<span style="position:relative;{TYPE};font-weight:700;font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:inherit">{label}</span>')
    st = f'position:relative;display:inline-flex;align-items:center;justify-content:center;width:{ww}px;height:54px;{"color:" + (INK if kind != "ink" else PAPERHI)};{extra}'
    if onclick:
        return f'<button type="button" class="{"chip inkc" if kind == "ink" else "chip lift"}" onClick="{{{{{onclick}}}}}" style="{st}">{inner}</button>'
    cls = 'chip inkc' if kind == 'ink' else 'chip lift'
    if state == 'disabled':
        return f'<span class="{cls}" role="button" aria-disabled="true" style="{st}">{inner}</span>'
    return f'<a href="{href}" class="{cls}" style="{st}">{inner}</a>'

def field(label, value='', placeholder='', error='', helper='', w=360, dark=False):
    """A single-line input written on a ruled line. error replaces helper, in red ink with a small mark."""
    c, lc = (CHALK, ASH) if dark else (INK, PENCIL)
    line = RED if error else (SOOT if dark else RULE)
    txt = f'<span style="color:{c}">{value}</span>' if value else f'<span style="color:{lc};font-style:italic">{placeholder}</span>'
    under = (f'<div style="{MARK};font-size:18px;color:{RED};margin-top:6px">✕ {error}</div>' if error else
             (f'<div style="{TYPE};font-size:10px;letter-spacing:.14em;color:{lc};margin-top:8px;text-transform:uppercase">{helper}</div>' if helper else ''))
    return (f'<div style="width:{w}px"><div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{lc};text-transform:uppercase">{label}</div>'
            f'<div style="{SERIF};font-size:18px;padding:8px 0 6px;border-bottom:1.5px solid {line}">{txt}</div>{under}</div>')

def inline_note(text, tone='red', size=19):
    """A small handwritten margin note: red = something to fix, soft = gentle info."""
    col = {'red': RED, 'soft': '#F0A08F', 'pencil': PENCIL}[tone]
    return f'<div style="{MARK};font-size:{size}px;line-height:1.2;color:{col};transform:rotate(-1.2deg)">{text}</div>'

def link(label, href='#', color=CHALK, size=13):
    return f'<a href="{href}" class="ul" style="{TYPE};font-size:{size}px;letter-spacing:.14em;text-transform:uppercase;color:{color}">{label}</a>'

# the 1:1 pod crumb: the hand font drops the colon, so the numbers are typed
POD11 = f'<span style="{TYPE};font-size:.74em;letter-spacing:.04em">1:1</span> pod'

def topbar(right='', crumb='', dark=True):
    c = CHALK if dark else INK
    cr = f'<span style="{HAND};font-size:20px;color:{ASH if dark else PENCIL};margin-left:18px">{crumb}</span>' if crumb else ''
    return (f'<header style="position:relative;z-index:55;height:88px;flex-shrink:0;padding:0 56px;display:flex;align-items:center;justify-content:space-between">'
            f'<a href="V5Home.dc.html" style="display:flex;align-items:center;gap:14px" aria-label="N0TRACE home">{rabbit(34, c, uid="tb", blink=False)}{wordmark(14, c)}{cr}</a>'
            f'<div style="display:flex;align-items:center;gap:28px;{TYPE};font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{ASH}">{right}'
            f'<a href="V5Help.dc.html" class="ul" style="color:{CHALK}">need help now?</a></div></header>')

def footer(dark=True):
    return (f'<footer style="position:relative;z-index:55;height:64px;flex-shrink:0;margin:0 56px;display:flex;align-items:center;justify-content:space-between;border-top:1px dashed {SOOT};{TYPE};font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:{ASH}">'
            f'<span>no account · a new name every visit · nothing kept · 18+</span>'
            f'<span style="display:flex;gap:26px"><a href="V5Privacy.dc.html" class="ul">what we keep</a><a href="V5Help.dc.html" class="ul" style="color:#E07A6E">in crisis? talk to someone trained →</a></span></footer>')

# ---------- phone (390 x 844) ----------
MW, MH, MPAD = 390, 844, 22   # phone frame, gutter
def mtopbar(crumb='', back=None, right=None, dark=True):
    """Phone header: rabbit + wordmark (or a back arrow + crumb), help on the right."""
    c = CHALK if dark else INK
    if back:
        left = (f'<a href="{back}" aria-label="Back" style="display:flex;align-items:center;gap:10px;color:{c}">'
                f'<svg width="20" height="16" viewBox="0 0 20 16" aria-hidden="true"><path d="M19 8H2M8 2L2 8l6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
                f'<span style="{HAND};font-size:21px;color:{ASH if dark else PENCIL}">{crumb}</span></a>')
    else:
        cr = f'<span style="{HAND};font-size:18px;color:{ASH if dark else PENCIL};margin-left:8px">{crumb}</span>' if crumb else ''
        left = f'<a href="V5MHome.dc.html" style="display:flex;align-items:center;gap:10px" aria-label="N0TRACE home">{rabbit(26, c, uid="mtb", blink=False)}{wordmark(11, c)}{cr}</a>'
    # help is always top right on phone; status (hours, offline) belongs in the screen, not here
    help_ = f'<a href="V5MHelp.dc.html" class="ul" style="{TYPE};font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:{CHALK};padding:12px 0 12px 12px">help</a>'
    rt = right if (right is not None and 'OFFLINE' in str(right)) else help_
    return (f'<header style="position:relative;z-index:55;height:64px;flex-shrink:0;padding:8px {MPAD}px 0;display:flex;align-items:center;justify-content:space-between">'
            f'{left}{rt}</header>')

# Phone frame, one rule for every screen (scales from 320x568 to 430x932):
#   header 64  ·  body (flex, the main sheet fills it)  ·  dock  ·  footer on the safe area
# The gaps around the dock are tokens, never per-screen numbers.
M_GAP = 14            # main sheet -> dock (+6 body bottom pad = 20 visible)
M_DOCK_FOOT = 14      # dock -> footer rule
M_SAFE = 'env(safe-area-inset-bottom, 0px)'
def mfooter():
    return (f'<footer style="position:relative;z-index:55;flex-shrink:0;margin:0 {MPAD}px;padding:12px 0 calc(16px + {M_SAFE});border-top:1px dashed {SOOT};display:flex;justify-content:space-between;{TYPE};font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:{ASH}">'
            f'<span>nothing kept · 18+</span><a href="V5MHelp.dc.html" class="ul" style="color:#E07A6E">in crisis? →</a></footer>')

def mbody(inner, center=False, gap=14, top=4, cls='', extra=''):
    """The flexible middle of a phone screen. center=True for scene screens (a note, an envelope)."""
    jc = 'justify-content:safe center;' if center else ''
    return (f'<main class="mbody {cls}" style="position:relative;z-index:10;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;{jc}gap:{gap}px;padding:{top + 16}px {MPAD}px 6px;margin-top:-16px;overflow-x:hidden;overflow-y:auto;scrollbar-width:none;{extra}">'
            f'{inner}</main>')

def msheet(inner, kind='', seed=1, pad='20px 20px 18px', rot=0, tapes='', minh=260, cls='', extra='', torn=None):
    """The main paper of a phone screen: as wide as the gutters allow, and it grows to meet the dock,
    so the space under it is always M_GAP whatever the phone. Put a flex column inside."""
    return (f'<div class="lift msheet {cls}" style="position:relative;flex:1 1 auto;min-height:{minh}px;width:100%;transform:rotate({rot}deg);{extra}">'
            f'<div class="paper {kind}" style="position:absolute;inset:0;padding:{pad};clip-path:{deckle(346, 600, seed=seed, torn=torn)};display:flex;flex-direction:column;overflow:hidden">{inner}</div>{tapes}</div>')

def mdock(row, sub='', footer=True):
    """Actions live here, in the thumb zone: M_GAP under the sheet, M_DOCK_FOOT over the footer
    (or the safe area when a screen has no footer, like a live pod)."""
    bot = f'{M_DOCK_FOOT}px' if footer else f'calc(18px + {M_SAFE})'
    sub = f'<div style="display:flex;justify-content:space-between;align-items:center;min-height:32px">{sub}</div>' if sub else ''
    return (f'<div class="mdock" style="position:relative;z-index:20;flex-shrink:0;padding:{M_GAP}px {MPAD}px {bot};display:flex;flex-direction:column;gap:10px">'
            f'<div style="display:flex;align-items:center;gap:12px">{row}</div>{sub}</div>')

def mcta(label, href='#', kind='ink', seed=11, onclick=None, icon='', grow=True, state=''):
    """Dock button: a torn chip that stretches with the phone (min 48 tall)."""
    bg = {'paper': f'background-color:{PAPERHI};color:{INK}', 'ink': f'background-color:{INK};color:{PAPERHI}',
          'kraft': f'background-color:{KRAFT};color:{INK}'}[kind]
    ex = ''
    if state == 'disabled':
        ex = ';opacity:.38;filter:saturate(.4);pointer-events:none;cursor:default'
    inner = (f'<span class="paper" style="position:absolute;inset:0;{bg};clip-path:{deckle(180, 50, amp=1.5, step=12, seed=seed)}"></span>'
             f'<span style="position:relative;display:inline-flex;align-items:center;gap:8px;{TYPE};font-weight:700;font-size:11.5px;letter-spacing:.16em;text-transform:uppercase;color:inherit;white-space:nowrap">{icon}{label}</span>')
    st = (f'position:relative;display:inline-flex;align-items:center;justify-content:center;{"flex:1 1 0;" if grow else "padding:0 22px;"}min-width:0;height:50px;'
          f'color:{INK if kind != "ink" else PAPERHI}{ex}')
    cls = 'chip inkc' if kind == 'ink' else 'chip lift'
    if onclick:
        return f'<button type="button" class="{cls}" onClick="{{{{{onclick}}}}}" style="{st}">{inner}</button>'
    return f'<a href="{href}" class="{cls}" style="{st}">{inner}</a>'

def mtext(label, href='#', color=None, onclick=None):
    """Quiet second action next to a dock button: typewriter caps, 48px tap height."""
    c = color or CHALK
    st = f'display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 6px;{TYPE};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{c};white-space:nowrap'
    if onclick:
        return f'<button type="button" class="ul" onClick="{{{{{onclick}}}}}" style="{st};background:none;border:0">{label}</button>'
    return f'<a href="{href}" class="ul" style="{st}">{label}</a>'

def mpage(name, title, body, h=MH, css='', script=None, props='', bg=NIGHT):
    page(name, title, body, w=MW, h=h, css=css, script=script, props=props, bg=bg)


# ---------- sound (see project/sound.js; everything is synthesised, nothing fetched) ----------
# per board: music (meta), chalk ('all' or headline substrings), cls {class: cue}
_BURN = {'cls': {'sheet-in': 'burn', 'tapeburn': 'flutter'}, 'chalk': ["It's gone"]}
_SEAL = {'cls': {'letter-in': 'slide', 'flap': 'fold', 'seal': 'wax'}, 'chalk': ['Sealed'], 'replay': 1}
_OPEN = {'cls': {'unfold': 'slide'}}   # one paper sound as the letter comes out; no chalk on top of it, no replay
_LETGO = {'cls': {'foldaway': 'fold'}}
_PIN = {'cls': {'drop': 'rip', 'slap': 'tapepress'}, 'chalk': ['up there now'], 'replay': 1}
_KNOT = {'cls': {'knot': 'pluck'}, 'music': 'wait', 'kind': 'wait'}
SOUND = {
    # music only where someone is being told the story, or waiting: never where voice notes or calls play
    'V5Story': {'music': 'story', 'chalk': 'all'}, 'V5MStory': {'music': 'story', 'chalk': 'all'},
    'V5Age': {'music': 'story'}, 'V5MAge': {'music': 'story'},
    'V5Matching': _KNOT, 'V5MMatching': _KNOT, 'V5Requeue': _KNOT, 'V5MRequeue': _KNOT,
    'V5Burn': _BURN, 'V5MBurn': dict(_BURN, pos='br'),
    'V5CapsuleSealed': _SEAL, 'V5MCapsuleSealed': _SEAL,
    'V5CapsuleOpen': _OPEN, 'V5MCapsuleOpen': _OPEN, 'V5CapsuleLetGo': _LETGO, 'V5MCapsuleLetGo': _LETGO,
    'V5EchoPinned': _PIN, 'V5MEchoPinned': _PIN,
    'V5EchoThread': {'cls': {'stamp': 'stamp'}, 'pos': 'dtop'},
    'V5EchoNoReplies': {'cls': {'stamp': 'stamp'}}, 'V5MEchoNoReplies': {'cls': {'stamp': 'stamp'}}, 'V5MEchoThread': {'cls': {'stamp': 'stamp'}},
    'V5PodEnd': {'chalkcue': 'heardchord', 'chalk': ['heard'], 'replay': True}, 'V5MPodEnd': {'chalkcue': 'heardchord', 'chalk': ['heard'], 'replay': True},
    'V5PodEndNotes': {'chalkcue': 'heardchord', 'chalk': ['heard'], 'replay': True}, 'V5MPodEndNotes': {'chalkcue': 'heardchord', 'chalk': ['heard'], 'replay': True},
    'V5NotFound': {'chalk': ['already let go'], 'replay': 1}, 'V5MNotFound': {'chalk': ['already let go'], 'replay': 1},
}
# every V5 board loads the engine (so sound survives screen changes); only boards with a marker show the switch
SND_HEAD = '<script src="./sound.js"></script>'

def _strip(h):
    return re.sub(r'<[^>]+>', '', h)

def snd_marker(cfg):
    attrs = ''
    for k in ('music', 'chalk', 'pos', 'kind'):
        if cfg.get(k) and not (k == 'chalk' and cfg[k] != 'all'):
            attrs += f' data-{k}="{cfg[k]}"'
    if cfg.get('replay'):
        attrs += ' data-replay="1"'
    return f'<i class="nt-cfg" hidden aria-hidden="true"{attrs}></i>'

def tag_sound(cfg, doc):
    if cfg.get('chalk') and cfg.get('chalk') != 'all':
        cue = cfg.get('chalkcue', 'chalk')
        out, i = [], 0
        for m in re.finditer(r'<div class="write"', doc):
            out.append(doc[i:m.end()]); i = m.end()
            txt = _strip(doc[m.end():m.end() + 700])[:160]
            if any(k in txt for k in cfg['chalk']):
                out.append(f' data-snd="{cue}"')
        out.append(doc[i:]); doc = ''.join(out)
    for c, cue in cfg.get('cls', {}).items():
        n = [0]
        def rep(m):
            n[0] += 1
            extra = f' data-snd-i="{n[0] - 1}"' if cue == 'pluck' else ''
            return f'{m.group(0)} data-snd="{cue}"{extra}'
        doc = re.sub(r'class=(["\'])%s(?:\s[^"\']*)?\1' % re.escape(c), rep, doc)
    return doc

def apply_sound(name, doc):
    cfg = SOUND.get(name)
    if not cfg:
        return doc, SND_HEAD  # the engine loads everywhere, so music can fade out when you leave a music screen
    doc = tag_sound(cfg, doc)
    # the marker rides inside the board's own content
    m = re.search(r'<x-dc>.*?</helmet>\s*<div[^>]*>', doc, re.S)
    if m:
        doc = doc[:m.end()] + snd_marker(cfg) + doc[m.end():]
    return doc, SND_HEAD

PAGES = {}
def _root_size(w, h):
    if w == MW:   # phone: fill whatever phone this is; long (scrolling) boards keep their length
        return f'width: 100vw; min-width: 320px; height: {"100vh" if h == MH else str(h) + "px"}; min-height: {min(h, 568)}px'
    return f'width: {w}px; height: {h}px'

def page(name, title, body, w=1440, h=900, css='', script=None, props='', bg=NIGHT):
    # canvas = the board as drawn; v5_live may rewrite body for the site ({{partner}}...), flow boards use canvas
    PAGES[name] = dict(title=title, body=body, canvas=body, w=w, h=h, css=css, script=script, props=props, bg=bg)
    if script is None:
        script = 'renderVals() { return {}; }'
    dp = '{%s"$preview":{"width":%d,"height":%d}}' % ((props + ',') if props else '', w, h)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>N0TRACE — {title}</title>
<script src="./support.js"></script>
{{SNDHEAD}}
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
{BASE_CSS}{css}
.flare,.leak,.nglow,.dawn,.dawnrise,.bloom,.glowring{{display:none !important}}
</style>
</helmet>
<div style="position: relative; {_root_size(w, h)}; background: {bg}; color: {CHALK}; display: flex; flex-direction: column; overflow: hidden">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{dp}'>
class Component extends DCLogic {{
{script}
}}
</script>
</body>
</html>
"""
    doc, sndhead = apply_sound(name, doc)
    doc = doc.replace('{SNDHEAD}', sndhead)
    open(OUT + name + '.dc.html', 'w').write(doc)


# ---------- one board, several moments ----------
# A tap that starts the next moment stays on the same page, so the browser counts that tap and the
# moment's sound plays with its animation (the real site is one page anyway). Each moment keeps its own
# sound settings, and music only plays while a music moment is on screen.
def flow(name, stages, title=None, phone=False):
    """stages: [(source_board, {href: index_of_moment_it_leads_to})]; the first moment is what the board shows."""
    import copy
    srcs = [copy.deepcopy(PAGES[s]) for s, _ in stages]
    first = srcs[0]
    parts, css_seen, css_all = [], set(), []
    for i, ((src, links), p) in enumerate(zip(stages, srcs)):
        frag = p.get('canvas', p['body'])
        cfg = SOUND.get(src, {})
        frag = tag_sound(cfg, frag) if cfg else frag
        marker = snd_marker(cfg) if cfg else ''
        for href, j in links.items():
            n = frag.count(f'href="{href}"')
            assert n >= 1, (name, src, href)
            frag = frag.replace(f'href="{href}"', f'onClick="{{{{go{j}}}}}" role="button" tabindex="0"')
        show = 'true' if i == 0 else 'false'
        parts.append(f'<sc-if value="{{{{s{i}}}}}" hint-placeholder-val="{{{{ {show} }}}}">'
                     f'<div style="position:absolute;inset:0;overflow-y:auto;overflow-x:hidden;background:{p["bg"]}">'
                     f'<div style="position:relative;{"height:100%;min-height:568px" if (p["w"] == MW and p["h"] == MH) else "min-height:" + str(p["h"]) + "px"};display:flex;flex-direction:column">{marker}{frag}</div></div></sc-if>')
        if p['css'] and p['css'] not in css_seen:
            css_seen.add(p['css']); css_all.append(p['css'])
    n = len(stages)
    vals = ', '.join([f's{i}: stage === {i}' for i in range(n)] + [f'go{i}: () => this.setState({{ stage: {i} }})' for i in range(n)])
    script = ("constructor(props) { super(props); this.state = { stage: null, mode: null }; }\n"
              "renderVals() {\n"
              "const stage = this.state.stage ?? (+this.props.stage || 0);\n"
              "const mode = this.state.mode ?? 'write';\n"
              f"const on = '{INK}', off = '{PENCIL}';\n"
              "return { " + vals + ",\n"
              "writeMode: mode === 'write', speakMode: mode === 'speak',\n"
              "writeColor: mode === 'write' ? on : off, speakColor: mode === 'speak' ? on : off,\n"
              "writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,\n"
              "toWrite: () => this.setState({ mode: 'write' }), toSpeak: () => this.setState({ mode: 'speak' }) };\n}")
    props = '"stage":{"editor":"enum","options":[%s],"default":"0"}' % ','.join(f'"{i}"' for i in range(n))
    css = '\n'.join(css_all) + '\n[role=button]{cursor:pointer}'
    page(name, title or first['title'], ''.join(parts), w=first['w'], h=first['h'], css=css, script=script, props=props, bg=first['bg'])
