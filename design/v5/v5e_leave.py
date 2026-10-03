"""N0TRACE V5 edge cases, group edge_leave (L11-L19): burn empty / recording, echoes quiet wall / yours /
no replies / too long, capsule not yet / email off / lost. Desktop (V5*) + phone (V5M*)."""
from gen5 import *
from v5m_home import fcard
from v5x_echo import kind_pick, ECHO_CSS, wave, play_btn, toggle, THREAD_SCRIPT, THREAD_PROPS, heard_btn, stamp, REPLIES
import json

PINK = '#F0A08F'
MW_ = MW - 2 * MPAD  # 346
BOARDS = []
def board(name, title, w, h, row):
    BOARDS.append({"file": name + '.dc.html', "title": title, "w": w, "h": h, "row": row})

EDGE_SCRIPT = THREAD_SCRIPT.replace('heard ? 13 : 12', 'heard ? 4 : 3').replace("timeTitle: 'left here at 1:12 am'", "timeTitle: 'left here at 12:40 am'").replace("fadesShort: '14H'", "fadesShort: '22H'").replace('mcardH: 362', 'mcardH: 330')
EDGE_PROPS = THREAD_PROPS.replace('"heard":{"editor":"boolean","default":true}', '"heard":{"editor":"boolean","default":false}')

# ---------------------------------------------------------------- small local helpers
def stoggle(mode='write', size=12, gap=22, dark=False):
    """Static WRITE / SPEAK toggle (no script)."""
    on, off = (CHALK, BOARDTXT) if dark else (INK, PENCIL)
    def b(lbl, sel):
        return (f'<span style="color:{on if sel else off};position:relative;padding-bottom:6px">{lbl}'
                f'<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{1 if sel else 0}"></span></span>')
    return (f'<div style="display:flex;gap:{gap}px;align-items:center;{TYPE};font-size:{size}px;letter-spacing:.18em">'
            f'{b("WRITE", mode == "write")}<span style="color:{SOOT if dark else PENCIL};opacity:{1 if dark else .5}">/</span>{b("SPEAK", mode == "speak")}</div>')

def btoggle(size=12, gap=22):
    """WRITE / SPEAK on the live recording screen (speak is the chosen one here)."""
    def b(lbl, sel, fn):
        return (f'<button type="button" onClick="{{{{{fn}}}}}" style="color:{CHALK if sel else BOARDTXT};position:relative;padding-bottom:6px;letter-spacing:inherit">{lbl}'
                f'<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{1 if sel else 0}"></span></button>')
    return (f'<div style="display:flex;gap:{gap}px;align-items:center;{TYPE};font-size:{size}px;letter-spacing:.18em">'
            f'{b("WRITE", False, "toWrite")}<span style="color:{SOOT}">/</span>{b("SPEAK", True, "toSpeak")}</div>')

def heard_static(n, size=22):
    return (f'<span class="heard" style="font-size:{size}px"><svg width="{size - 4}" height="{size - 4}" viewBox="0 0 20 20" aria-hidden="true">'
            f'<path d="M10 17 C3 12 1 8 3 5 C5 2 9 3 10 6 C11 3 15 2 17 5 C19 8 17 12 10 17 Z" fill="none" stroke="{RED}" stroke-width="1.8" stroke-linejoin="round"/></svg>heard · {n}</span>')

def tally(n, h=24, color=RED, seed=3):
    """Hand-drawn tally marks in red ink: gates of five."""
    r = random.Random(seed)
    out, x = [], 2
    for g in range(0, n, 5):
        k = min(5, n - g)
        x0 = x
        for i in range(min(k, 4)):
            out.append(f'<path d="M{x + r.uniform(-1, 1):.1f} {2 + r.uniform(0, 2):.1f} L{x + r.uniform(-1.5, 1.5):.1f} {h - 2 - r.uniform(0, 2):.1f}"/>')
            x += 7
        if k == 5:
            out.append(f'<path d="M{x0 - 4:.1f} {h - 5:.1f} L{x - 2:.1f} {5:.1f}"/>')
        x += 8
    w = x
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<defs>{ROUGH.format(i="tl" + str(seed), s=4, sc=1.6)}</defs>'
            f'<g filter="url(#roughtl{seed})" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round">{"".join(out)}</g></svg>')

def ruled(top=60, gap=34, margin=None):
    m = (f'<div aria-hidden="true" style="position:absolute;top:0;bottom:0;left:{margin}px;width:1.5px;background:rgba(184,53,42,.45)"></div>' if margin else '')
    return (f'<div aria-hidden="true" style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 {gap - 1}px,rgba(96,120,150,.26) {gap - 1}px {gap}px);'
            f'background-position:0 {top}px;background-size:100% {gap}px;-webkit-mask:linear-gradient(transparent {top}px,#000 {top}px)"></div>{m}')

def pin(x, y, col='#5d5d61', s=7.5):
    return (f'<svg aria-hidden="true" width="{s * 4}" height="{s * 4}" viewBox="0 0 30 30" style="position:absolute;left:{x}px;top:{y}px;z-index:8;overflow:visible">'
            f'<ellipse cx="19" cy="21" rx="9" ry="5" fill="#000" opacity=".45"/><circle cx="15" cy="15" r="7.5" fill="{col}"/>'
            f'<circle cx="15" cy="15" r="7.5" fill="none" stroke="#000" stroke-opacity=".35"/><circle cx="12.5" cy="12.5" r="2.2" fill="#fff" opacity=".25"/></svg>')

def wall_ghosts(w, h, seed, n_tape=9, n_holes=14, spots=()):
    """Where notes used to be: faint tape ghosts, pin-hole pairs, a torn corner left under tape."""
    r = random.Random(seed)
    out = []
    for (x, y, ww, hh, rot) in spots:  # a note-shaped clean patch with tape ghosts on its top edge
        out.append(f"<g transform='rotate({rot} {x + ww / 2} {y + hh / 2})'>"
                   f"<rect x='{x}' y='{y}' width='{ww}' height='{hh}' fill='#cfc6ad' opacity='.022'/>"
                   f"<rect x='{x}' y='{y}' width='{ww}' height='{hh}' fill='none' stroke='#cfc6ad' stroke-width='.8' stroke-dasharray='2 5' opacity='.05'/>"
                   f"<rect x='{x + ww / 2 - 40}' y='{y - 10}' width='80' height='22' fill='#cfc6ad' opacity='.05'/>"
                   f"<circle cx='{x + 14}' cy='{y + 12}' r='1.7' fill='#000' opacity='.9'/><circle cx='{x + ww - 16}' cy='{y + 14}' r='1.7' fill='#000' opacity='.9'/></g>")
    for _ in range(n_tape):
        x, y = r.uniform(10, w - 90), r.uniform(10, h - 30); tw, th = r.uniform(50, 96), r.uniform(16, 24); rot = r.uniform(-30, 30)
        out.append(f"<rect x='{x:.0f}' y='{y:.0f}' width='{tw:.0f}' height='{th:.0f}' fill='#cfc6ad' opacity='.05' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>"
                   f"<rect x='{x:.0f}' y='{y:.0f}' width='{tw:.0f}' height='{th:.0f}' fill='none' stroke='#cfc6ad' stroke-width='.8' stroke-dasharray='3 2' opacity='.05' transform='rotate({rot:.0f} {x:.0f} {y:.0f})'/>")
    for _ in range(n_holes):
        x, y = r.uniform(8, w - 8), r.uniform(8, h - 8)
        out.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='1.6' fill='#000' opacity='.9'/><circle cx='{x - .6:.1f}' cy='{y - .6:.1f}' r='2.4' fill='none' stroke='#5a5753' stroke-width='.6' opacity='.35'/>")
    return f"<svg aria-hidden='true' width='{w}' height='{h}' viewBox='0 0 {w} {h}' style='position:absolute;left:0;top:0;overflow:visible'>{''.join(out)}</svg>"

def scrap(x, y, rot, s=1.0, seed=7):
    """A torn paper corner still stuck under a bit of tape."""
    return (f'<div aria-hidden="true" style="position:absolute;left:{x}px;top:{y}px;transform:rotate({rot}deg) scale({s});opacity:.5">'
            f'<div class="paper" style="width:46px;height:30px;clip-path:polygon(0 0,100% 0,82% 40%,96% 58%,60% 70%,40% 100%,22% 76%,0 88%)"></div>'
            f'{tape(-8, -8, 44, 16, rot=-12, seed=seed)}</div>')


# ================================================================ E05 — the wall, quiet night
def empty_note(w, h, size_h, size_m, seed, chip_href, chip_w):
    inner = (f'<div style="{HAND};font-size:{size_h}px;line-height:1.2;color:{INK}">Nobody\'s left anything yet tonight.</div>'
             f'<div style="{SERIF};font-size:{size_m}px;line-height:1.5;color:{INK};margin-top:12px">Be the first, or just sit here a minute.</div>'
             f'<div style="position:absolute;left:0;right:0;bottom:24px;display:flex;justify-content:center">{chip("leave the first one", chip_href, kind="ink", w=chip_w, seed=seed + 5)}</div>')
    return paper(inner, w, h, kind='hi', seed=seed, pad='30px 30px' if w > 300 else '26px 24px',
                 tapes=tape(w / 2 - 50, -13, 100, 26, rot=-4, seed=seed))

d_spots = [(40, 40, 300, 200, -2.5), (420, 10, 260, 170, 2), (1010, 20, 290, 210, 3), (60, 300, 280, 180, 1.8), (1020, 290, 270, 180, -1.6), (690, 330, 280, 190, 2.4)]
d_wall = (f'<div aria-hidden="true" style="position:absolute;inset:0">{wall_ghosts(1328, 520, 51, 6, 18, d_spots)}'
          f'{scrap(1190, 30, 8, seed=71)}{scrap(170, 290, -14, .9, seed=72)}{pin(560, 380, "#7a2a22")}{pin(1250, 470, "#2b2b2e")}</div>')
d_note = (f'<div style="position:absolute;left:{(1328 - 420) // 2}px;top:120px;transform:rotate(-1.6deg)" class="drop">'
          f'{empty_note(420, 262, 33, 21, 5051, "V5EchoWrite.dc.html", 280)}</div>')
eempty = f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:4px 56px 0;display:flex;flex-direction:column;gap:26px">
<div>
{h_hand('The wall is quiet.', 54)}
<div class="rise" style="--w:1.2s;{TYPE};font-size:12px;letter-spacing:.16em;color:{BOARDTXT};margin-top:4px">ANONYMOUS · EACH ONE FADES AWAY IN 24 HOURS</div>
</div>
<div class="rise" style="--w:.4s;position:relative;height:520px">{d_wall}{d_note}
<div class="rise" style="--w:2s;position:absolute;left:{(1328 - 420) // 2 + 30}px;top:418px;{HAND};font-size:22px;color:{BOARDTXT};transform:rotate(-1deg)">everything from last night has already let go.</div></div>
</main>
{footer()}'''
page('V5EchoesEmpty', 'The wall is quiet', eempty, css=ECHO_CSS)
board('V5EchoesEmpty', 'L13 — The wall is quiet', 1440, 900, 'edge_leave')

m_spots = [(10, 30, 150, 150, -2), (190, 10, 150, 170, 2.4), (20, 430, 300, 140, 1.2), (180, 600, 150, 150, -2.2)]
m_wall = (f'<div aria-hidden="true" style="position:absolute;inset:0">{wall_ghosts(346, 640, 61, 4, 10, m_spots)}'
          f'{scrap(290, 200, 10, .8, seed=73)}{pin(30, 600, "#7a2a22", 6)}</div>')
m_note = (f'<div class="drop" style="position:absolute;left:{(346 - 306) / 2:.0f}px;top:170px;transform:rotate(-1.6deg)">'
          f'{empty_note(306, 290, 26, 17.5, 6051, "V5MEchoWrite.dc.html", 250)}</div>')
meempty = f'''
{matmos()}
{mtopbar(crumb='echoes', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 {MPAD}px;display:flex;flex-direction:column">
{h_hand('The wall is quiet.', 34)}
<div class="rise" style="--w:1s;{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.7;color:{BOARDTXT};margin-top:6px">ANONYMOUS · EACH ONE FADES IN 24 HOURS</div>
<div class="rise" style="--w:.4s;position:relative;flex-grow:1;margin-top:18px">{m_wall}{m_note}
<div class="rise" style="--w:2s;position:absolute;left:0;right:0;top:486px;text-align:center;{HAND};font-size:19px;line-height:1.35;color:{BOARDTXT}">everything from last night<br>has already let go.</div></div>
</main>
{mfooter()}'''
mpage('V5MEchoesEmpty', 'The wall is quiet', meempty, css=ECHO_CSS)
board('V5MEchoesEmpty', 'ML13 — The wall is quiet', 390, 844, 'm_edge_leave')


# ================================================================ E06 — an echo, no replies yet
def echo_card(w, h, phone=False):
    if not phone:
        inner = f'''
<div style="display:flex;justify-content:space-between;align-items:center;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">
<span>AN ECHO · {{{{modeLabel}}}}</span><span style="display:flex;align-items:center;gap:8px"><span style="width:7px;height:7px;border-radius:50%;border:1.5px solid {PENCIL}"></span>FADES IN {{{{fadesShort}}}}</span></div>
<sc-if value="{{{{isVoice}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="{HAND};font-size:32px;line-height:1.2;color:{INK};margin-top:16px">{{{{timeTitle}}}}</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:22px">
<button type="button" class="pbtn" onClick="{{{{togglePlay}}}}" aria-label="{{{{playLabel}}}}">{play_btn(64, 'epb', True)}</button>
{wave(340, 70, 91, 'ewe', 0, main=True)}
<span data-slot="playTime" style="{TYPE};font-size:12px;letter-spacing:.1em;color:{INK};white-space:nowrap">0:00 / 0:34</span></div>
<div style="{SERIF};font-style:italic;font-size:18px;line-height:1.5;color:{PENCIL};margin-top:22px">Just their voice. No transcript, and nothing left of it once it fades.</div></sc-if>
<sc-if value="{{{{isText}}}}" hint-placeholder-val="{{{{ false }}}}"><div style="{SERIF};font-size:21px;line-height:1.55;color:{INK};margin-top:18px;white-space:pre-wrap;overflow-wrap:anywhere">{{{{noteText}}}}</div></sc-if>
<div style="position:absolute;left:40px;right:40px;bottom:30px;border-top:1px dashed {RULE};padding-top:18px;display:flex;justify-content:space-between;align-items:center">
{heard_btn(26)}<span style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL};text-transform:uppercase">{{{{heardHint}}}}</span></div>
{stamp(40, 56, 36)}'''
        return paper(inner, w, h, rot=-1.2, kind='hi', seed=5501, pad='34px 40px', tapes=tape(w / 2 - 55, -14, 110, 28, rot=-3, seed=551), cls='thud').replace(f'height:{h}px', 'height:{{cardH}}px', 1)
    inner = f'''
<div style="display:flex;justify-content:space-between;align-items:center;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">
<span>AN ECHO · {{{{modeLabel}}}}</span><span style="display:flex;align-items:center;gap:6px"><span style="width:6px;height:6px;border-radius:50%;border:1.5px solid {PENCIL}"></span>FADES IN {{{{fadesShort}}}}</span></div>
<sc-if value="{{{{isVoice}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="{HAND};font-size:26px;line-height:1.2;color:{INK};margin-top:12px">{{{{timeTitle}}}}</div>
<div style="display:flex;align-items:center;gap:14px;margin-top:18px">
<button type="button" class="pbtn" onClick="{{{{togglePlay}}}}" aria-label="{{{{playLabel}}}}">{play_btn(54, 'mepb', True)}</button>
{wave(222, 58, 91, 'mewe', 0, main=True, sw=2)}</div>
<div data-slot="playTime" style="{TYPE};font-size:10.5px;letter-spacing:.1em;color:{INK};text-align:right;margin-top:8px">0:00 / 0:34</div>
<div style="{SERIF};font-style:italic;font-size:15.5px;line-height:1.5;color:{PENCIL};margin-top:10px">Just their voice. No transcript, and nothing left of it once it fades.</div></sc-if>
<sc-if value="{{{{isText}}}}" hint-placeholder-val="{{{{ false }}}}"><div style="{SERIF};font-size:18px;line-height:1.5;color:{INK};margin-top:14px;white-space:pre-wrap;overflow-wrap:anywhere">{{{{noteText}}}}</div></sc-if>
<div style="position:absolute;left:24px;right:24px;bottom:20px;border-top:1px dashed {RULE};padding-top:14px;display:flex;justify-content:space-between;align-items:center;gap:12px">
{heard_btn(23)}<span style="{TYPE};font-size:9px;letter-spacing:.12em;line-height:1.6;color:{PENCIL};text-transform:uppercase;text-align:right;max-width:150px">{{{{heardHint}}}}</span></div>
{stamp(26, 206, 26, '1.3s')}'''
    return paper(inner, w, h, rot=-1, kind='hi', seed=6501, pad='24px 24px', tapes=tape(w / 2 - 48, -13, 96, 26, rot=-3, seed=651), cls='thud').replace(f'height:{h}px', 'height:{{mcardH}}px', 1)

def blank_slip(w, h, phone=False):
    top = 58 if not phone else 50
    inner = (ruled(top, 34 if not phone else 30) +
             f'<div style="position:relative;{HAND};font-size:{28 if not phone else 23}px;color:{INK}">No replies yet.</div>'
             f'<div style="position:relative;{SERIF};font-style:italic;font-size:{20 if not phone else 17}px;line-height:{34 if not phone else 30}px;color:{PENCIL};margin-top:{14 if not phone else 10}px">'
             f'Heard is enough too.</div>'
             f'<div style="position:relative;{MARK};font-size:{21 if not phone else 18.5}px;line-height:{34 if not phone else 30}px;color:{PENCIL}">or say something kind back, below.</div>')
    return paper(inner, w, h, kind='', seed=5520 if not phone else 6520, pad='20px 28px' if not phone else '16px 22px',
                 tapes=tape(w / 2 - 45, -12, 90, 24, rot=2, seed=552))

def composer(w, h, phone=False):
    if not phone:
        return paper(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{toggle(11, 18)}<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">NO NAME ON IT</span></div>
<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:12px">
<div data-slot="replyText" style="{SERIF};font-size:20px;color:{PENCIL};font-style:italic">say something kind back<span class="blink" style="color:{RED};font-style:normal">|</span></div>
{chip('reply', kind='ink', w=120, seed=5521, onclick='sendReply')}</div></sc-if>
<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="replyVoice" style="display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:12px">
<div style="display:flex;align-items:center;gap:12px"><span style="width:12px;height:12px;border-radius:50%;background:{RED}"></span><span style="{HAND};font-size:24px;color:{INK}">hold to record a reply</span></div>
<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">UP TO 30 SECONDS</span></div></sc-if>''',
            w, h, rot=.4, seed=5522, pad='22px 28px', tapes=tape(w / 2 - 45, -12, 90, 24, rot=2, seed=553))
    return paper(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{toggle(10, 14)}<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};padding-bottom:6px">NO NAME ON IT</span></div>
<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px">
<div data-slot="replyText" style="{SERIF};font-size:17px;color:{PENCIL};font-style:italic">say something kind back<span class="blink" style="color:{RED};font-style:normal">|</span></div>
{chip('reply', kind='ink', w=96, seed=6521, onclick='sendReply')}</div></sc-if>
<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="replyVoice" style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:14px">
<div style="display:flex;align-items:center;gap:10px"><span style="width:11px;height:11px;border-radius:50%;background:{RED}"></span><span style="{HAND};font-size:21px;color:{INK}">hold to record a reply</span></div>
<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};text-align:right">UP TO<br>30 SEC</span></div></sc-if>''',
        w, h, rot=.4, seed=6522, pad='18px 20px', tapes=tape(w / 2 - 40, -11, 80, 22, rot=2, seed=653))

enorep = f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px;display:flex;gap:64px">
<div style="width:640px;display:flex;flex-direction:column;gap:18px;padding-top:2px">
<div class="rise" style="--w:.1s">{link('← the wall', 'V5Echoes.dc.html', BOARDTXT, 12)}</div>
{h_hand('Left for whoever is up.', 44, wait='.2s')}
<div class="rise" style="--w:.5s;margin:22px 0 0 14px">{echo_card(600, 336)}</div>
<div class="rise" style="--w:2.2s;margin:26px 0 0 30px">{t_mark("heard is the only reaction. no likes, no followers.", 22, PINK, 'transform:rotate(-1.5deg)')}</div>
</div>
<div style="flex-grow:1;display:flex;flex-direction:column;padding-top:40px">
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;padding-right:8px">
<span style="{HAND};font-size:34px;color:{CHALK}">replies · 0</span>
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">BY VOICE OR TEXT · THEY FADE WITH IT</span></div>
<div class="rise" style="--w:1s;margin-top:30px;transform:rotate(-.6deg)">{blank_slip(560, 176)}</div>
<div class="rise" style="--w:1.8s;margin-top:auto;margin-bottom:26px">{composer(600, 146)}</div>
</div>
</main>
{footer()}'''
page('V5EchoNoReplies', 'An echo, no replies yet', f'<div class="{{{{rootClass}}}}" style="position:absolute;inset:0;display:flex;flex-direction:column">{enorep}</div>',
     css=ECHO_CSS, script=EDGE_SCRIPT, props=EDGE_PROPS)
board('V5EchoNoReplies', 'L15 — An echo, no replies yet', 1440, 900, 'edge_leave')

NRH = 1010
menorep = f'''
{matmos(NRH)}
{mtopbar(crumb='the wall', back='V5MEchoes.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 {MPAD}px;display:flex;flex-direction:column">
{h_hand('Left for whoever is up.', 29, wait='.2s')}
<div class="rise" style="--w:.5s;margin:28px 0 0 2px">{echo_card(340, 330, True)}</div>
<div class="rise" style="--w:2.2s;margin:22px 0 0 8px">{t_mark("heard is the only reaction.<br>no likes, no followers.", 20, PINK, 'transform:rotate(-1.5deg)')}</div>
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;margin-top:34px">
<span style="{HAND};font-size:28px;color:{CHALK}">replies · 0</span>
<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">THEY FADE WITH IT</span></div>
<div class="rise" style="--w:1s;margin:22px 0 0 4px;transform:rotate(-.6deg)">{blank_slip(330, 150, True)}</div>
<div class="rise" style="--w:1.6s;margin-top:auto;margin-bottom:22px">{composer(346, 132, True)}</div>
</main>
{mfooter()}'''
mpage('V5MEchoNoReplies', 'An echo, no replies yet (scrolls)', f'<div class="{{{{rootClass}}}}" style="position:absolute;inset:0;display:flex;flex-direction:column">{menorep}</div>',
      h=NRH, css=ECHO_CSS, script=EDGE_SCRIPT, props=EDGE_PROPS)
board('V5MEchoNoReplies', 'ML15 — An echo, no replies yet (scrolls)', 390, NRH, 'm_edge_leave')


# ================================================================ E07 — your echo, a few hours later
YOURS = "I keep rehearsing conversations that will never happen."

def yours_note(w, h, phone=False):
    fs, pad = (24, '34px 40px') if not phone else (19.5, '24px 24px')
    lr = 40 if not phone else 24
    inner = (f'<div style="display:flex;justify-content:space-between;align-items:center;{TYPE};font-size:{11 if not phone else 9.5}px;letter-spacing:.16em;color:{PENCIL}">'
             f'<span>YOURS · FADES IN {{{{fadesShort}}}}</span><span>{{{{kindLabel}}}} · {{{{modeLabel}}}}</span></div>'
             f'<div data-slot="yoursBody" style="{SERIF};font-size:{fs}px;line-height:1.55;color:{INK};margin-top:{20 if not phone else 14}px">{YOURS}</div>'
             f'<div style="position:absolute;left:{lr}px;right:{lr}px;bottom:{28 if not phone else 20}px;border-top:1px dashed {RULE};padding-top:{16 if not phone else 14}px;display:flex;justify-content:space-between;align-items:center;gap:12px">'
             f'<span style="display:flex;align-items:center;gap:12px"><span data-slot="tally">{tally(6, 24 if not phone else 20, color=PENCIL, seed=7)}</span>'
             f'<span style="{MARK};font-size:{23 if not phone else 20}px;color:{PENCIL}">{{{{heardBy}}}}</span></span>'
             f'<a href="#" data-act="takeDown" class="ul" style="{MARK};font-size:{22 if not phone else 19}px;color:{RED}">{{{{takeDownLabel}}}}</a></div>')
    return paper(inner, w, h, rot=-1.2 if not phone else -1, kind='hi', seed=5701 if not phone else 6701, pad=pad,
                 tapes=tape(w / 2 - 55, -14, 110, 28, rot=-3, seed=571)).replace(f'height:{h}px', 'height:{{cardH}}px', 1)

def reply_slip(i, phone=False, wslip=560):
    name, when, kind, content, pk, seed = REPLIES[i]
    if not phone:
        if kind == 'text':
            body = f'<div style="{SERIF};font-size:19px;line-height:1.5;color:{INK};margin-top:8px">{content}</div>'; h = 132
        else:
            body = (f'<div style="display:flex;align-items:center;gap:16px;margin-top:10px">{play_btn(42, f"ypr{i}")}'
                    f'{wave(300, 40, seed, f"ywr{i}", 0, head=False, sw=1.8)}<span style="{TYPE};font-size:11px;letter-spacing:.1em;color:{INK}">{content}</span></div>'); h = 112
        hdr = (f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL}">'
               f'<span style="letter-spacing:.06em;font-size:12px">{name}</span><span>{"VOICE · " if kind == "voice" else ""}{when.upper()}</span></div>')
        rot, off = [-.8, .9][i], [0, 30][i]
        tp = tape([200, 330][i], -11, 80, 22, rot=[-4, 3][i], seed=seed)
        return f'<div class="slip rise" style="--w:{.9 + i * .25:.2f}s;margin-left:{off}px;transform:rotate({rot}deg)">{paper(hdr + body, wslip, h, kind=pk, seed=seed + 200, pad="20px 26px", tapes=tp)}</div>'
    if kind == 'text':
        body = f'<div style="{SERIF};font-size:16.5px;line-height:1.45;color:{INK};margin-top:6px">{content}</div>'; h = 112 if len(content) < 75 else 136
    else:
        body = (f'<div style="display:flex;align-items:center;gap:12px;margin-top:8px">{play_btn(36, f"mypr{i}")}'
                f'{wave(196, 32, seed, f"mywr{i}", 0, head=False, sw=1.6)}<span style="{TYPE};font-size:10px;letter-spacing:.1em;color:{INK}">{content}</span></div>'); h = 96
    hdr = (f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">'
           f'<span style="letter-spacing:.04em;font-size:11px">{name}</span><span>{"VOICE · " if kind == "voice" else ""}{when.upper()}</span></div>')
    rot, off = [-.8, .9][i], [0, 16][i]
    tp = tape([180, 40][i], -10, 70, 20, rot=[-4, 3][i], seed=seed)
    return f'<div class="slip rise" style="--w:{.9 + i * .25:.2f}s;margin-left:{off}px;transform:rotate({rot}deg)">{paper(hdr + body, 324, h, kind=pk, seed=seed + 230, pad="16px 20px", tapes=tp)}</div>'

eyours = f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px;display:flex;gap:64px">
<div style="width:640px;display:flex;flex-direction:column;gap:18px;padding-top:2px">
<div class="rise" style="--w:.1s">{link('← the wall', 'V5Echoes.dc.html', BOARDTXT, 12)}</div>
{h_hand('Yours. Still up there.', 48, wait='.2s')}
<div class="rise" style="--w:.5s;margin:26px 0 0 14px">{yours_note(600, 250)}</div>
<div class="rise" style="--w:2s;margin:30px 0 0 30px">{t_mark("there's no way to see who heard it. not for you, not for us.", 22, PINK, 'transform:rotate(-1.5deg)')}
<div style="{TYPE};font-size:11px;letter-spacing:.16em;line-height:1.9;color:{BOARDTXT};margin-top:18px">TAKING IT DOWN LETS IT GO EARLY. THE REPLIES GO WITH IT.</div></div>
</div>
<div style="flex-grow:1;display:flex;flex-direction:column;padding-top:40px">
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;padding-right:8px">
<span style="{HAND};font-size:34px;color:{CHALK}">{{{{repliesTitle}}}}</span>
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">THEY FADE WITH IT</span></div>
<div data-slot="replies" style="display:flex;flex-direction:column;gap:22px;margin-top:22px">{reply_slip(0)}{reply_slip(1)}</div>
</div>
</main>
{footer()}'''
YOURS_VALS = "fadesShort: '19H', kindLabel: 'AN ECHO', modeLabel: 'TEXT', heardBy: 'heard by 6', takeDownLabel: 'take it down now', repliesTitle: '2 replies'"
page('V5EchoYours', 'Your echo', eyours, css=ECHO_CSS, script="renderVals() { return { %s, cardH: 250 }; }" % YOURS_VALS)
board('V5EchoYours', 'L14 — Your echo (owner view)', 1440, 900, 'edge_leave')

meyours = f'''
{matmos()}
{mtopbar(crumb='the wall', back='V5MEchoes.dc.html')}
<main class="mbody" style="position:relative;z-index:10;flex:1 1 auto;min-height:0;padding:0 {MPAD}px 20px;display:flex;flex-direction:column;overflow-x:hidden;overflow-y:auto;scrollbar-width:none">
{h_hand('Yours. Still up there.', 32, wait='.2s')}
<div class="rise" style="--w:.5s;margin:26px 0 0 2px">{yours_note(340, 204, True)}</div>
<div class="rise" style="--w:2s;margin:18px 0 0 8px">{t_mark("there's no way to see who heard it.", 20, PINK, 'transform:rotate(-1.5deg)')}</div>
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;margin-top:26px">
<span style="{HAND};font-size:28px;color:{CHALK}">{{{{repliesTitle}}}}</span>
<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">THEY FADE WITH IT</span></div>
<div data-slot="replies" style="display:flex;flex-direction:column;gap:22px;margin-top:20px;flex-shrink:0">{reply_slip(0, True)}{reply_slip(1, True)}</div>
<div class="rise" style="--w:2.2s;{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.8;color:{BOARDTXT};margin-top:22px">TAKING IT DOWN LETS IT GO EARLY.<br>THE REPLIES GO WITH IT.</div>
</main>
{mfooter()}'''
mpage('V5MEchoYours', 'Your echo', meyours, css=ECHO_CSS, script="renderVals() { return { %s, cardH: 204 }; }" % YOURS_VALS)
board('V5MEchoYours', 'ML14 — Your echo (owner view)', 390, 844, 'm_edge_leave')


# ================================================================ E08 — leave yours, can't pin yet
LONG = ("I keep rehearsing conversations that will never happen. The one where I tell my brother I'm sorry about the wedding. "
        "The one where I tell my boss I'm not okay, and she just nods. The one where I call you back and you pick up, and we "
        "laugh about how long it's been, like nothing ever broke. I write them in the shower, on the bus, at 2 am. "
        "I think some part of me hopes saying them here counts for something.")
CUT = 400
LONG = LONG[:CUT]
assert len(LONG) == CUT, len(LONG)
TAIL = 26  # the last words, the part that ran past the edge of the note
long_html = (f'{LONG[:CUT - TAIL]}<span style="text-decoration:underline wavy {RED};text-decoration-thickness:1.5px;text-underline-offset:4px">{LONG[CUT - TAIL:]}</span>'
             f'<span class="blink" style="color:{RED}">|</span>')

def compose_long(w, h, phone=False):
    if not phone:
        return paper(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{stoggle('write', 12, 22)}<span data-slot="noteCount" style="{TYPE};font-size:12px;font-weight:700;letter-spacing:.14em;color:{INK};padding-bottom:6px">400 / 400</span></div>
<div data-slot="noteText" style="{SERIF};font-size:19px;line-height:1.6;color:{INK};margin-top:18px">{long_html}</div>
<div style="position:absolute;left:40px;right:40px;bottom:24px;border-top:1px dashed {RULE};padding-top:14px;display:flex;justify-content:space-between;align-items:center;gap:16px">
{inline_note('a little shorter, it has to fit on a note', 'red', 22)}<span style="{TYPE};font-size:10.5px;letter-spacing:.14em;color:{PENCIL};white-space:nowrap">NO NAME ON IT</span></div>''',
            w, h, rot=.9, kind='hi', seed=5802, pad='34px 40px', tapes=tape(w / 2 - 55, -14, 110, 28, rot=2, seed=582))
    return msheet(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{stoggle('write', 11, 16)}<span data-slot="noteCount" style="{TYPE};font-size:10.5px;font-weight:700;letter-spacing:.14em;color:{INK};padding-bottom:6px">400 / 400</span></div>
<div data-slot="noteText" style="{SERIF};font-size:15.5px;line-height:1.5;color:{INK};margin-top:14px">{long_html}</div>
<div style="margin-top:auto;flex-shrink:0;border-top:1px dashed {RULE};padding-top:10px">{inline_note('a little shorter, it has to fit on a note', 'red', 17.5)}</div>''',
        kind='hi', seed=6802, pad='20px 24px 16px', rot=-1.2, minh=h, tapes=tape(0, -13, 96, 26, rot=-3, seed=682).replace('left:0px', 'left:calc(50% - 48px)', 1))

ewerr = f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:90px;padding-bottom:40px">
<div style="width:420px;display:flex;flex-direction:column;gap:24px">
{h_hand('Leave it somewhere someone might find it.', 48, d='2s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:19px;line-height:1.55;color:{BOARDTXT}">It goes up on the wall for 24 hours. Strangers can listen, reply, or tap <span style="{MARK};color:{PINK};font-size:22px">heard</span>. No one can find you.</div>
<div class="rise" style="--w:1.7s;display:flex;align-items:center;gap:22px;margin-top:8px">{chip('pin it up', state='disabled', seed=5812, w=180)}{inline_note('trim it a little first', 'soft', 23)}</div>
<div class="rise" style="--w:1.9s">{link('not now', 'V5Echoes.dc.html')}</div>
</div>
<div style="display:flex;flex-direction:column;gap:28px"><div class="rise" style="--w:.9s;margin-left:6px">{kind_pick('echo', 12, 24)}</div>
<div class="rise" style="--w:.5s">{compose_long(620, 400)}</div></div>
</main>
{footer()}'''
page('V5EchoTooLong', "Leave yours, can't pin yet", ewerr, css=ECHO_CSS)
board('V5EchoTooLong', "L16 — Leave yours, can't pin yet (too long)", 1440, 900, 'edge_leave')

mewerr = f'''
{matmos()}
{mtopbar(crumb='echoes', back='V5MEchoes.dc.html')}
{mbody(h_hand('Leave it somewhere someone might find it.', 28, d='1.8s')
       + f'<div class="rise" style="--w:.9s;margin-top:4px">{kind_pick("echo", 10, 16)}</div>'
       + f'<div class="rise" style="--w:.5s;flex:1 0 auto;display:flex;flex-direction:column;margin-top:10px">{compose_long(338, 330, True)}</div>', gap=12)}
<div class="rise" style="--w:1.6s;display:flex;flex-direction:column">{mdock(mcta('pin it up', '#', 'paper', seed=6812, grow=False, state='disabled') + inline_note('trim it a little first', 'soft', 20))}</div>
{mfooter()}'''
mpage('V5MEchoTooLong', "Leave yours, can't pin yet", mewerr, css=ECHO_CSS)
board('V5MEchoTooLong', "ML16 — Leave yours, can't pin yet (too long)", 390, 844, 'm_edge_leave')


# ================================================================ L11 — burn, nothing to burn yet
def anchored(sheet, h, mhtml, label, left=-34, size=104, pad=34, gap=22):
    """The match sits on the note's bottom-left corner, overlapping its torn edge, like the live Burn board."""
    return (f'<div style="position:relative">{sheet}<div style="position:absolute;left:{left}px;top:{h - 22}px;z-index:12;display:flex;align-items:center;gap:{gap}px">'
            f'{mhtml}<div style="display:flex;flex-direction:column;gap:6px;padding-top:{pad}px">{label}</div></div></div>')

def dim_match(size=104):
    s = size / 104
    return (f'<div aria-disabled="true" style="position:relative;width:{size}px;height:{size}px;border-radius:50%;display:flex;align-items:center;justify-content:center;pointer-events:none;flex-shrink:0">'
            f'<svg width="{size}" height="{size}" viewBox="0 0 104 104" aria-hidden="true" style="position:absolute;inset:0"><circle cx="52" cy="52" r="51" fill="{NIGHT2}"/><circle cx="52" cy="52" r="50" fill="none" stroke="{BOARDTXT}" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="4 5"/></svg>'
            f'<svg width="{40 * s:.0f}" height="{66 * s:.0f}" viewBox="0 0 40 66" aria-hidden="true" style="position:relative;opacity:.38;filter:saturate(.3)"><rect x="17" y="16" width="6" height="48" rx="1.5" fill="{KRAFT}"/><ellipse cx="20" cy="14" rx="6.5" ry="8" fill="{RED}"/></svg></div>')

BW, BH = 600, 320
bsheet = paper(ruled(92, 38, 66) +
               f'<div style="position:relative;{HAND};font-size:24px;color:{PENCIL};padding-left:46px;margin-top:-4px">tonight, 11:48 pm</div>'
               f'<div style="position:relative;padding-left:46px;{SERIF};font-size:22px;line-height:38px;padding-top:16px"><span class="blink" style="color:{RED}">|</span></div>',
               BW, BH, rot=-.8, kind='hi', seed=301, pad='40px 44px 40px 30px', tapes=tape(240, -15, 120, 30, rot=-3, seed=31))

bempty = f'''
{atmos()}
{topbar(crumb='burn')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:100px;padding-bottom:40px">
<div style="width:440px;display:flex;flex-direction:column;gap:30px">
{h_hand("Say the thing you can't say out loud.", 52, wait='.2s', d='2s')}
<div class="rise" style="--w:1.2s;{TYPE};font-size:12px;letter-spacing:.16em;line-height:1.9;color:{BOARDTXT}">IT STAYS ON THIS DEVICE.<br>WHEN YOU BURN IT, IT'S GONE. FOR GOOD.</div>
<div class="rise" style="--w:1.5s">{stoggle('write', 12, 22, dark=True)}
<div style="{HAND};font-size:21px;color:{BOARDTXT};margin-top:14px">or tap speak, and just say it.</div></div>
</div>
<div class="rise" style="--w:.5s;margin-bottom:60px">{anchored(bsheet, BH, dim_match(104), f'<span style="{HAND};font-size:30px;color:{BOARDTXT};opacity:.7;white-space:nowrap">hold to burn it</span>' + inline_note('write something first. even one word.', 'soft', 23), pad=40)}</div>
</main>'''
page('V5BurnEmpty', 'Nothing to burn yet', bempty)
board('V5BurnEmpty', 'L11 — Burn, nothing to burn yet', 1440, 900, 'edge_leave')

MBW, MBH = 330, 330
mbsheet = paper(ruled(72, 30, 44) +
                f'<div style="position:relative;{HAND};font-size:19px;color:{PENCIL};padding-left:30px;margin-top:-2px">tonight, 11:48 pm</div>'
                f'<div style="position:relative;padding-left:30px;{SERIF};font-size:17px;line-height:30px;padding-top:13px"><span class="blink" style="color:{RED}">|</span></div>',
                MBW, MBH, rot=-.8, kind='hi', seed=301, pad='26px 24px 26px 20px', tapes=tape(115, -13, 100, 26, rot=-3, seed=31))
mbempty = f'''
{matmos()}
{mtopbar(crumb='burn', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:0 {MPAD}px 26px">
{h_hand("Say the thing you can't say out loud.", 31, wait='.2s', d='1.8s')}
<div class="rise" style="--w:1.1s;display:flex;justify-content:space-between;align-items:center;margin-top:12px">
{stoggle('write', 11, 16, dark=True)}<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT};padding-bottom:6px">STAYS ON THIS DEVICE</span></div>
<div class="rise" style="--w:1.3s;{HAND};font-size:18px;color:{BOARDTXT};margin-top:8px">or tap speak, and just say it.</div>
<div style="flex-grow:1;min-height:24px"></div>
<div class="rise" style="--w:.5s;margin:0 0 0 8px">{anchored(mbsheet, MBH, dim_match(84), f'<span style="{HAND};font-size:25px;color:{BOARDTXT};opacity:.7;white-space:nowrap">hold to burn it</span>' + inline_note('write something first.<br>even one word.', 'soft', 19), left=-12, size=84, pad=30, gap=16)}</div>
<div style="flex-grow:.45;flex-shrink:0;min-height:84px"></div>
</main>
{mfooter()}'''
mpage('V5MBurnEmpty', 'Nothing to burn yet', mbempty)
board('V5MBurnEmpty', 'ML11 — Burn, nothing to burn yet', 390, 844, 'm_edge_leave')


# ================================================================ L12 — burn, recording a voice note
REC_CSS = """
.lb{transform-box:fill-box;transform-origin:center;animation:lb var(--d,1.1s) ease-in-out var(--w,0s) infinite alternate}
@keyframes lb{from{transform:scaleY(var(--a,.35))}to{transform:scaleY(1)}}
.recdot{animation:recdot 2.4s ease-in-out infinite}
@keyframes recdot{0%,100%{opacity:1}50%{opacity:.35}}
.pressring{animation:pressring 2.6s ease-out infinite}
@keyframes pressring{0%{transform:scale(1);opacity:.55}100%{transform:scale(1.35);opacity:0}}
"""

def live_wave(w, h, frac, seed, uid, sw=2.2):
    """The note so far, drawn in ink from the left; the last few strokes still moving; the rest of the 2 minutes a pencil line."""
    r = random.Random(seed)
    mid, step = h / 2, (5 if w > 300 else 4)
    xe = int(w * frac)
    done, live = [], []
    xs = list(range(3, xe, step))
    for i, x in enumerate(xs):
        t = x / w
        env = (.35 + .65 * abs(math.sin(t * 17 + 1.1))) * (.6 + .4 * math.sin(t * 41))
        if r.random() < .08:
            env *= .25
        a = max(.1, min(1, env * r.uniform(.6, 1.1))) * (mid - 4)
        d = f'M{x + r.uniform(-.6, .6):.1f} {mid - a:.1f}L{x + r.uniform(-.9, .9):.1f} {mid + a * r.uniform(.8, 1.1):.1f}'
        if i >= len(xs) - 7:  # the edge that is still being spoken
            live.append(f'<path class="lb" d="{d}" style="--d:{r.uniform(.7, 1.3):.2f}s;--w:-{r.uniform(0, 1):.2f}s;--a:{r.uniform(.2, .5):.2f}"/>')
        else:
            done.append(d)
    rest = f'<path d="M{xe + 8} {mid} L{w - 2} {mid}" stroke="{PENCIL}" stroke-width="1.4" stroke-dasharray="2 6" opacity=".6"/>'
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<defs>{ROUGH.format(i=uid, s=5, sc=1.4)}</defs>'
            f'<g filter="url(#rough{uid})" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="round"><path d="{"".join(done)}"/>{"".join(live)}</g>'
            f'{rest}<line x1="{xe + 3}" y1="-4" x2="{xe + 4}" y2="{h + 4}" stroke="{RED}" stroke-width="2" stroke-linecap="round"/></svg>')

def idle_wave(w, h):
    """Before you speak: just the pencil line the note will be drawn along."""
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<path d="M3 {h / 2} L{w - 2} {h / 2}" stroke="{PENCIL}" stroke-width="1.4" stroke-dasharray="2 6" opacity=".6"/>'
            f'<line x1="3" y1="-4" x2="4" y2="{h + 4}" stroke="{RED}" stroke-width="2" stroke-linecap="round"/></svg>')

def rec_held(size=72):
    """The record button, pressed down: a calm ring breathes out from it while you hold."""
    return (f'<button type="button" class="recbtn" aria-label="{{{{recAria}}}}" onPointerDown="{{{{recStart}}}}" onPointerUp="{{{{recStop}}}}" onPointerCancel="{{{{recStop}}}}" onKeyDown="{{{{recKeyDown}}}}" onKeyUp="{{{{recKeyUp}}}}" onContextMenu="{{{{noMenu}}}}" '
            f'style="position:relative;display:inline-flex;align-items:center;justify-content:center;width:{size}px;height:{size}px;flex-shrink:0;border-radius:50%;touch-action:none;user-select:none;-webkit-user-select:none">'
            f'<sc-if value="{{{{recording}}}}" hint-placeholder-val="{{{{ true }}}}"><span class="pressring" aria-hidden="true" style="position:absolute;inset:0;border-radius:50%;border:2px solid {RED}"></span></sc-if>'
            f'<span style="position:absolute;inset:0;border-radius:50%;border:2px solid {INK};background:rgba(184,53,42,.08);transform:scale(.94)"></span>'
            f'<span style="position:relative;width:{size * .38:.0f}px;height:{size * .38:.0f}px;border-radius:50%;background:{RED}"></span></button>')

def rec_head(size, tsize):
    return (f'<div style="display:flex;align-items:center;justify-content:space-between">'
            f'<span style="display:flex;align-items:center;gap:12px"><sc-if value="{{{{recording}}}}" hint-placeholder-val="{{{{ true }}}}"><span class="recdot" style="display:block;width:{size * .45:.0f}px;height:{size * .45:.0f}px;border-radius:50%;background:{RED}"></span></sc-if>'
            f'<span style="{HAND};font-size:{size}px;color:{INK}">{{{{recLabel}}}}</span></span>'
            f'<span style="{TYPE};font-weight:700;font-size:{tsize}px;letter-spacing:.1em;color:{INK}">{{{{recTime}}}}</span></div>')

RBH = 470
rsheet = paper(f'''
<div style="{HAND};font-size:24px;color:{PENCIL};margin-top:-4px">tonight, 11:48 pm</div>
<div style="margin-top:18px">{rec_head(30, 18)}</div>
<div style="margin-top:18px"><sc-if value="{{{{recording}}}}" hint-placeholder-val="{{{{ true }}}}">{live_wave(512, 80, .78, 404, 'rlw')}</sc-if><sc-if value="{{{{notRecording}}}}">{idle_wave(512, 80)}</sc-if></div>
<div style="display:flex;justify-content:flex-end;margin-top:10px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}"><span>UP TO 2 MINUTES</span></div>
<div style="{SERIF};font-style:italic;font-size:18px;line-height:1.5;color:{PENCIL};margin-top:10px">Only you hear it. When it burns, the recording goes with it.</div>
<div style="position:absolute;left:44px;right:44px;bottom:40px;border-top:1px dashed {RULE};padding-top:18px;display:flex;align-items:center;gap:22px">
{rec_held(72)}<div><div style="{HAND};font-size:30px;color:{INK}">{{{{recHint}}}}</div>
<div style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL};margin-top:6px">KEEP HOLDING WHILE YOU TALK · OR HOLD SPACE</div></div></div>''',
               BW, RBH, rot=-.8, kind='hi', seed=301, pad='40px 44px', tapes=tape(240, -15, 120, 30, rot=-3, seed=31))

brec = f'''
{atmos()}
{topbar(crumb='burn')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:100px;padding-bottom:40px">
<div style="width:440px;display:flex;flex-direction:column;gap:30px">
{h_hand("Say the thing you can't say out loud.", 52, wait='.2s', d='2s')}
<div class="rise" style="--w:1.2s;{TYPE};font-size:12px;letter-spacing:.16em;line-height:1.9;color:{BOARDTXT}">IT STAYS ON THIS DEVICE.<br>WHEN YOU BURN IT, IT'S GONE. FOR GOOD.</div>
<div class="rise" style="--w:1.5s">{btoggle(12, 22)}</div>
</div>
<div class="rise" style="--w:.5s;margin-bottom:60px">{anchored(rsheet, RBH, dim_match(104), f'<span style="{HAND};font-size:30px;color:{BOARDTXT};opacity:.7;white-space:nowrap">hold to burn it</span>' + ('<sc-if value="{{recording}}" hint-placeholder-val="{{ true }}">' + inline_note('the match is yours once you let go.', 'soft', 23) + '</sc-if><sc-if value="{{recIdle}}">' + inline_note('say it first. then the match.', 'soft', 23) + '</sc-if><sc-if value="{{micBlocked}}">' + inline_note('your mic is blocked. allow it for this site<br>in the address bar, then hold again.', 'red', 21) + '</sc-if>'), pad=40)}</div>
</main>'''
REC_SCRIPT = "renderVals() { return { recording: true, notRecording: false, recIdle: false, micBlocked: false, notBlocked: true, recLabel: 'recording', recTime: '0:07', recHint: 'let go to stop', recAria: 'Hold to record' }; }"
page('V5BurnRecording', 'Burn, recording a voice note', brec, css=REC_CSS, script=REC_SCRIPT)
board('V5BurnRecording', 'L12 — Burn, recording a voice note', 1440, 900, 'edge_leave')

mrsheet = paper(f'''
<div style="{HAND};font-size:19px;color:{PENCIL};margin-top:-2px">tonight, 11:48 pm</div>
<div style="margin-top:22px">{rec_head(25, 15)}</div>
<div style="margin-top:22px"><sc-if value="{{{{recording}}}}" hint-placeholder-val="{{{{ true }}}}">{live_wave(282, 78, .78, 404, 'mrlw', 2)}</sc-if><sc-if value="{{{{notRecording}}}}">{idle_wave(282, 78)}</sc-if></div>
<div style="display:flex;justify-content:flex-end;margin-top:12px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}"><span>UP TO 2 MINUTES</span></div>
<div style="{SERIF};font-style:italic;font-size:15.5px;line-height:1.5;color:{PENCIL};margin-top:22px">Only you hear it. When it burns, the recording goes with it.</div>''',
                MBW, 340, rot=-.8, kind='hi', seed=301, pad='26px 24px', tapes=tape(115, -13, 100, 26, rot=-3, seed=31))
mbrec = f'''
{matmos()}
{mtopbar(crumb='burn', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:0 {MPAD}px 26px">
{h_hand("Say the thing you can't say out loud.", 31, wait='.2s', d='1.8s')}
<div class="rise" style="--w:1.1s;display:flex;justify-content:space-between;align-items:center;margin-top:12px">
{btoggle(11, 16)}<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT};padding-bottom:6px">STAYS ON THIS DEVICE</span></div>
<div style="flex-grow:1;min-height:24px"></div>
<div class="rise" style="--w:.5s;margin:0 0 0 8px">{mrsheet}</div>
<div class="rise" style="--w:1.4s;margin-top:18px;display:flex;align-items:center;gap:20px">
<span style="display:inline-flex;border-radius:50%;background:{PAPERHI};padding:6px" class="lift">{rec_held(76)}</span>
<div><div style="{HAND};font-size:27px;color:{CHALK}">{{{{recHint}}}}</div>
<sc-if value="{{{{notBlocked}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.7;color:{BOARDTXT};margin-top:4px">KEEP HOLDING WHILE YOU TALK.<br>THE MATCH COMES BACK AFTER.</div></sc-if>
<sc-if value="{{{{micBlocked}}}}">{inline_note("your mic is blocked. allow it for<br>this site, then hold again.", 'red', 18)}</sc-if></div></div>
<div style="flex-grow:.45;flex-shrink:0;min-height:40px"></div>
</main>
{mfooter()}'''
mpage('V5MBurnRecording', 'Burn, recording a voice note', mbrec, css=REC_CSS, script=REC_SCRIPT)
board('V5MBurnRecording', 'ML12 — Burn, recording a voice note', 390, 844, 'm_edge_leave')


# ================================================================ capsule: envelopes
def _poly(pts):
    return 'polygon(' + ','.join(f'{x:.0f}px {y:.0f}px' for x, y in pts) + ')'

def seal_svg(size, uid):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" aria-hidden="true"><defs>{ROUGH.format(i=uid, s=11, sc=6)}'
            f'<radialGradient id="g{uid}" cx="40%" cy="35%"><stop offset="0" stop-color="#D4513F"/><stop offset=".7" stop-color="{RED}"/><stop offset="1" stop-color="#7d1f17"/></radialGradient></defs>'
            f'<g filter="url(#rough{uid})"><circle cx="50" cy="50" r="44" fill="url(#g{uid})"/><circle cx="50" cy="50" r="33" fill="none" stroke="#8e2a20" stroke-width="2.5"/></g>'
            f'<g transform="translate(26 33) scale(.4)" opacity=".85"><path d="M16 13 L45 11 L47 41 L15 42 Z M74 12 L104 13 L103 42 L73 41 Z" fill="#7a1d15"/>'
            f'<path d="M45 64 L52 71 L59 64 L66 71 L73 64" fill="none" stroke="#7a1d15" stroke-width="6" stroke-linecap="round"/></g></svg>')

def sealed_env(ew, eh, seal, label_size, uid, seed):
    VY, FY = eh * .56, eh * .60
    pocket = _poly([(0, 6), (ew / 2, VY), (ew, 6), (ew, eh), (0, eh)])
    flap = _poly([(0, 0), (ew, 0), (ew / 2, FY)])
    return f"""<div style="position:relative;width:{ew}px;height:{eh}px">
<div style="position:absolute;inset:0;filter:drop-shadow(0 16px 24px rgba(0,0,0,.55))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#B49D74;clip-path:{deckle(ew, eh, seed=seed)}"></div></div>
<div style="position:absolute;inset:0;filter:drop-shadow(0 -2px 3px rgba(0,0,0,.22))"><div class="paper kraft" style="position:absolute;inset:0;clip-path:{pocket}"></div>
<svg width="{ew}" height="{eh}" style="position:absolute;inset:0" aria-hidden="true"><path d="M2 {eh - 2} L{ew / 2} {VY + 18:.0f} L{ew - 2} {eh - 2}" fill="none" stroke="rgba(80,55,25,.32)" stroke-width="1.5"/></svg>
<div style="position:absolute;right:{ew * .056:.0f}px;bottom:{eh * .07:.0f}px;{HAND};font-size:{label_size}px;color:{INK};transform:rotate(-3deg)">open on {{{{openShort}}}}.</div></div>
<div style="position:absolute;left:0;top:0;width:{ew}px;height:{FY:.0f}px;filter:brightness(1) drop-shadow(0 3px 3px rgba(0,0,0,.25))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#CDB892;clip-path:{flap}"></div></div>
<div style="position:absolute;left:{ew / 2 - seal / 2:.0f}px;top:{FY - seal * .65:.0f}px">{seal_svg(seal, uid)}</div>
</div>"""

def torn_env(ew, eh, uid, seed):
    """Opened, empty, the flap torn off at the tip. A scrap with half a seal lies beside it."""
    VY, FO = eh * .56, eh * .60
    r = random.Random(seed)
    pocket = _poly([(0, 6), (ew / 2, VY), (ew, 6), (ew, eh), (0, eh)])
    cut = .48  # fraction of the flap height that's left
    yc = FO * (1 - cut)
    xl, xr = ew / 2 - (ew / 2) * (1 - yc / FO), ew / 2 + (ew / 2) * (1 - yc / FO)
    jag = [(xr - (xr - xl) * i / 9, yc + r.uniform(-7, 7) * (eh / 290)) for i in range(1, 9)]
    flap = _poly([(0, FO), (ew, FO), (xr, yc)] + jag + [(xl, yc)])
    sw = ew * .3
    scr = _poly([(0, 0), (sw, 4), (sw * .5, sw * .62)])
    s = ew / 460
    return f"""<div style="position:relative;width:{ew}px;height:{eh}px;margin-top:{FO * cut:.0f}px">
<div style="position:absolute;left:0;top:{-FO:.0f}px;width:{ew}px;height:{FO:.0f}px;filter:drop-shadow(0 8px 12px rgba(0,0,0,.4))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#C2AC84;clip-path:{flap}"></div></div>
<div style="position:absolute;inset:0;filter:drop-shadow(0 16px 24px rgba(0,0,0,.55))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#9C8762;clip-path:{deckle(ew, eh, seed=seed)}"></div>
<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.42),rgba(0,0,0,.05) 60%)"></div></div>
<div style="position:absolute;inset:0;filter:drop-shadow(0 -2px 3px rgba(0,0,0,.22))"><div class="paper kraft" style="position:absolute;inset:0;clip-path:{pocket}"></div>
<svg width="{ew}" height="{eh}" style="position:absolute;inset:0" aria-hidden="true"><path d="M2 {eh - 2} L{ew / 2} {VY + 18:.0f} L{ew - 2} {eh - 2}" fill="none" stroke="rgba(80,55,25,.32)" stroke-width="1.5"/></svg></div>
<div aria-hidden="true" style="position:absolute;left:{ew + 26 * s:.0f}px;top:{eh * .62:.0f}px;width:{sw:.0f}px;height:{sw * .62:.0f}px;transform:rotate(142deg);filter:drop-shadow(0 6px 8px rgba(0,0,0,.5))">
<div class="paper kraft" style="position:absolute;inset:0;background-color:#CDB892;clip-path:{scr}"></div>
<div style="position:absolute;left:{sw * .5 - 22 * s:.0f}px;top:{sw * .62 - 40 * s:.0f}px;width:{44 * s:.0f}px;height:{24 * s:.0f}px;overflow:hidden">{seal_svg(int(44 * s), uid)}</div></div>
</div>"""

# ================================================================ C04 — not yet
cnot = f'''
{atmos()}
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:50px;padding-bottom:40px">
<div class="rise" style="--w:.2s;transform:rotate(-1.5deg)">{sealed_env(460, 290, 96, 22, 'cns', 462)}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
{h_hand('Not yet. {{daysLeft}}.', 58, color=PAPERHI, wait='.8s')}
<div class="rise" style="--w:1.6s;{TYPE};font-size:12px;letter-spacing:.18em;color:{BOARDTXT}">SEALED {{{{sealedUp}}}} · OPENS {{{{opensUp}}}}</div>
<div class="rise" style="--w:1.9s;{SERIF};font-style:italic;font-size:21px;color:rgba(233,233,231,.82);margin-top:4px">It's waiting right here. No peeking, not even for you.</div>
<div class="rise" style="--w:2.3s;margin-top:22px">{chip('back home', 'V5Home.dc.html', seed=7041, w=180)}</div>
</div></main>'''
NOTYET_VALS = "renderVals() { return { daysLeft: '9 more days', sealedUp: '14 SEPTEMBER', opensUp: 'SUNDAY, 11 OCTOBER', openShort: '11 oct' }; }"
page('V5CapsuleNotYet', 'Capsule, not yet', cnot, script=NOTYET_VALS)
board('V5CapsuleNotYet', 'L17 — Capsule, not yet', 1440, 900, 'edge_leave')

mcnot = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
{mbody(f'''<div style="display:flex;flex-direction:column;align-items:center">
<div class="rise" style="--w:.2s;transform:rotate(-1.5deg)">{sealed_env(304, 192, 62, 16, 'mcns', 1462)}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:48px;text-align:center">
{h_hand('Not yet.<br>{{daysLeft}}.', 38, color=PAPERHI, wait='.8s')}
<div class="rise" style="--w:1.6s;{TYPE};font-size:10px;letter-spacing:.16em;line-height:1.8;color:{BOARDTXT};margin-top:4px">OPENS {{{{opensUp}}}}</div>
<div class="rise" style="--w:1.9s;{SERIF};font-style:italic;font-size:17px;line-height:1.5;color:rgba(233,233,231,.82);max-width:300px">It's waiting right here.<br>No peeking, not even for you.</div>
</div></div>''', center=True)}
<div class="rise" style="--w:2.2s;display:flex;flex-direction:column">{mdock(mcta('back home', 'V5MHome.dc.html', 'paper', seed=7042))}</div>
{mfooter()}'''
mpage('V5MCapsuleNotYet', 'Capsule, not yet', mcnot, script=NOTYET_VALS)
board('V5MCapsuleNotYet', 'ML17 — Capsule, not yet', 390, 844, 'm_edge_leave')

# ================================================================ C05 — couldn't be kept
clost = f'''
{atmos()}
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:110px;padding-bottom:40px">
<div class="rise" style="--w:.2s;transform:rotate(2deg);margin-right:120px">{torn_env(440, 278, 'cls', 1501)}</div>
<div style="width:470px;display:flex;flex-direction:column;gap:22px">
{h_hand("This browser doesn't remember the letter anymore.", 48, wait='.6s', d='2s')}
<div class="rise" style="--w:1.8s;{SERIF};font-size:21px;line-height:1.6;color:rgba(233,233,231,.86)">We never had a copy, so neither do we.</div>
<div class="rise" style="--w:2.1s;{SERIF};font-size:17px;line-height:1.6;color:{BOARDTXT}">A capsule lives only in the browser you sealed it in. Clearing site data lets it go, and a private window forgets everything the moment it closes.</div>
<div class="rise" style="--w:2.4s;display:flex;align-items:center;gap:34px;margin-top:10px">{chip('write a new one', 'V5Capsule.dc.html', seed=7051, w=230)}{link('back home', 'V5Home.dc.html')}</div>
</div></main>'''
page('V5CapsuleLost', 'Capsule, the browser forgot', clost)
board('V5CapsuleLost', 'L19 — Capsule, the browser forgot', 1440, 900, 'edge_leave')

mclost = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
{mbody(f'''<div style="display:flex;flex-direction:column">
<div class="rise" style="--w:.2s;margin:0 0 0 6px;transform:rotate(2deg)">{torn_env(236, 150, 'mcls', 1502)}</div>
<div style="margin-top:40px">{h_hand("This browser doesn't remember the letter anymore.", 31, wait='.6s', d='2s')}</div>
<div class="rise" style="--w:1.8s;{SERIF};font-size:18px;line-height:1.5;color:rgba(233,233,231,.86);margin-top:12px">We never had a copy, so neither do we.</div>
<div class="rise" style="--w:2.1s;{SERIF};font-size:15px;line-height:1.55;color:{BOARDTXT};margin-top:10px">A capsule lives only in the browser you sealed it in. Private windows forget everything when they close.</div>
</div>''', center=True)}
<div class="rise" style="--w:2.4s;display:flex;flex-direction:column">{mdock(mcta('write a new one', 'V5MCapsule.dc.html', 'paper', seed=7052) + mtext('back home', 'V5MHome.dc.html'))}</div>
{mfooter()}'''
mpage('V5MCapsuleLost', 'Capsule, the browser forgot', mclost)
board('V5MCapsuleLost', 'ML19 — Capsule, the browser forgot', 390, 844, 'm_edge_leave')

# ================================================================ C06 — reminder email, check it
def opt(label, sel=False, phone=False, key=None, cw=None):
    if key:   # live: clickable, the chosen one circled
        hint = 'true' if sel else 'false'
        if phone:
            c = circle_scribble(cw or (len(label) * 9.5 + 30), 42, RED, wait='1.8s')
            st = f'padding:4px 6px;{HAND};font-size:clamp(14px, 4vw, 18px)'
        else:
            c = circle_scribble(cw or (len(label) * 12 + 44), 54, RED, wait='1.8s')
            st = f'padding:8px 14px;{HAND};font-size:23px'
        return (f'<button type="button" class="capopt" onClick="{{{{pick{key}}}}}" aria-pressed="{{{{on{key}}}}}" style="position:relative;display:inline-block;{st};color:{{{{col{key}}}}}">'
                f'<sc-if value="{{{{on{key}}}}}" hint-placeholder-val="{{{{ {hint} }}}}">{c}</sc-if>{label}</button>')
    if phone:
        c = circle_scribble(len(label) * 9.5 + 30, 42, RED, wait='1.8s') if sel else ''
        return f'<span style="position:relative;display:inline-block;padding:4px 6px;{HAND};font-size:{"18px" if sel else "clamp(14px, 4vw, 18px)"};color:{INK if sel else PENCIL}">{c}{label}</span>'
    c = circle_scribble(len(label) * 12 + 44, 54, RED, wait='1.8s') if sel else ''
    return f'<span style="position:relative;display:inline-block;padding:8px 14px;{HAND};font-size:23px;color:{INK if sel else PENCIL}">{c}{label}</span>'

ERR = "that address looks off. leave it empty if you'd rather not."
CAP_COPY = 'Sealed in this browser. If you add an email, we keep only that and the date, and delete both once it sends.'
EMAIL_BAD = 'sam@gmial<span class="blink" style="color:' + RED + '">|</span>'
def slot_field(html, name):
    """field() with its value line as a live slot."""
    k = 'padding:8px 0 6px'
    i = html.index(k); j = html.rindex('<div ', 0, i)
    return html[:j] + f'<div data-slot="{name}" ' + html[j + 5:]
EMAIL_VALS = ("renderVals() { return { onWeek: false, onMonth: false, onDate: true, colWeek: '#5F584E', colMonth: '#5F584E', colDate: '#221E1A', "
              "dateLabel: '%s', storageNote: false }; }")
# same composition as the fixed V5Capsule / V5MCapsule letters (kept local so this module never re-runs those boards)
letter = paper(f'''
<div style="{HAND};font-size:34px;color:{INK}">Dear later me,</div>
<div data-slot="capText" style="{SERIF};font-size:21px;line-height:1.65;color:{INK};margin-top:14px">Right now you're scared about the interview on Monday. Whatever happened, you went. That was the hard part. Be gentle with yourself either way.</div>
<div style="margin-top:40px;border-top:1px dashed {RULE};padding-top:16px;display:flex;align-items:center;gap:6px;flex-wrap:wrap">
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL};margin-right:10px">OPEN IT</span>{opt('next week', key='Week')}{opt('in a month', key='Month')}{opt('{{dateLabel}}', True, key='Date', cw=200)}</div>
<div style="margin-top:24px">{slot_field(field('remind me by email · optional', EMAIL_BAD, error=ERR, w=556), 'capEmail')}</div>
<div style="display:flex;justify-content:flex-end;margin-top:18px">{chip('seal it', 'V5CapsuleSealed.dc.html', seed=452, w=170, kind='ink')}</div>''',
    660, 530, rot=.8, kind='hi', seed=451, pad='46px 52px 40px', tapes=tape(270, -15, 120, 30, rot=3, seed=45))

cemail = f'''
<div class="room" aria-hidden="true"></div>{traces(1440, 900, seed=34)}<div class="vignette"></div><div class="grain"></div>
{topbar(crumb='time capsule')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:90px;padding-bottom:30px">
<div style="width:400px;display:flex;flex-direction:column;gap:24px">
{h_hand('Write to the you who comes later.', 50, d='2s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:19px;line-height:1.55;color:{BOARDTXT}">{CAP_COPY}</div>
<div class="rise" style="--w:2s">{inline_note('you can still seal it without one.', 'soft', 23)}</div>
<div class="rise" style="--w:1.7s;margin-top:4px">{link('not now', 'V5Home.dc.html')}</div>
</div>
<div class="rise" style="--w:.5s">{letter}</div>
</main>'''
page('V5CapsuleEmailError', 'Capsule, email looks off', cemail, script=EMAIL_VALS % '11 november')
board('V5CapsuleEmailError', "L18 — Capsule, email that doesn't look right", 1440, 900, 'edge_leave')

mletter = fcard(f'''
<div style="{HAND};font-size:clamp(24px, 3.6vh, 28px);color:{INK}">Dear later me,</div>
<div data-slot="capText" style="{SERIF};font-size:clamp(16px, 2.2vh, 17px);line-height:1.5;color:{INK};margin-top:6px">Right now you're scared about the interview on Monday. Whatever happened, you went. That was the hard part. Be gentle with yourself either way.</div>
<div style="margin-top:clamp(8px, 3vh - 8px, 30px);border-top:1px dashed {RULE};padding-top:12px">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">OPEN IT</div>
<div style="display:flex;flex-wrap:nowrap;align-items:center;justify-content:space-between;margin:0 -6px;white-space:nowrap">{opt('next week', phone=True, key='Week')}{opt('in a month', phone=True, key='Month')}{opt('{{dateLabel}}', True, phone=True, key='Date', cw=125)}</div></div>
<div style="margin-top:clamp(8px, 2.4vh - 6px, 24px)">{slot_field(field('remind me by email · optional', EMAIL_BAD, error=ERR, w=294).replace('width:294px', 'width:100%'), 'capEmail')}</div>
<div style="margin-top:8px;{HAND};font-size:18px;line-height:1.25;color:{PENCIL}">you can still seal it without one.</div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:clamp(12px, 2.2vh, 20px);flex-shrink:0">{mtext('not now', 'V5MHome.dc.html', PENCIL)}{chip('seal it', 'V5MCapsuleSealed.dc.html', seed=1452, w=150, kind='ink')}</div>''',
    kind='hi', seed=1451, pad='clamp(18px, 2.8vh, 24px) 26px clamp(16px, 2.4vh, 22px)', rot=.8, tapes=tape(0, -13, 110, 28, rot=3, seed=145).replace('left:0px', 'left:calc(50% - 55px)', 1))

mcemail = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
{mbody(h_hand('Write to the you who comes later.', 28, d='2s')
       + f'<div class="rise" style="--w:.5s;flex:0 0 auto;display:flex;flex-direction:column;margin:auto 0">{mletter}</div>', gap=12)}
<div style="height:{M_GAP + 6}px;flex-shrink:0"></div>
{mfooter()}'''
mpage('V5MCapsuleEmailError', 'Capsule, email looks off', mcemail, script=EMAIL_VALS % '11 nov')
board('V5MCapsuleEmailError', "ML18 — Capsule, email that doesn't look right", 390, 844, 'm_edge_leave')

# ---------------------------------------------------------------- manifest
key = lambda b: b['title'].split(' ')[0].lstrip('M')
desk = sorted([b for b in BOARDS if b['row'] == 'edge_leave'], key=key)
mob = sorted([b for b in BOARDS if b['row'] == 'm_edge_leave'], key=key)
json.dump(desk + mob, open('manifest_edge_leave.json', 'w'), indent=1)
print('edge leave ok', len(BOARDS))
