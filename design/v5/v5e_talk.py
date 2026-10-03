"""N0TRACE V5 edge cases: talk / pods (desktop + phone), group "edge_talk".
T11 NoOneFree, T12 PodsClosing, T13 PodsClosedMidChat, T14 SendFailed, T15 VoiceDeclined, T16 CallDropped,
T17 QuestionEmpty, T18 RoomsAllFull, T19 MovedOffStage, T20 RoomAlone. Each as V5<Name> (1440x900) + V5M<Name> (390x844)."""
from gen5 import *
import v5_live as LV
from v5m_home import fcard
import json, os
# desktop pod / voice / room pieces (importing re-runs that module's page() calls: harmless)
from v5x_voice import (ic, MIC, MICOFF, DOOR, FLAG, TEXTI, HANDI, pod_btn, line_msg, POD_CSS, status_dot, side_card, pod_layout,
                       ink_wave, lane, room_slip, ROOMS, dots10, star, MOD_BADGE, speaker_tag, CONVO, typing, CW, CH)
import v5x_voice as VX
# phone pieces
from v5m_voice import mlink, mchip, mmsg, msys, mtyping, MCONVO, mtag, mlane, mslip, SW as MSLW, SH as MSLH, TW as MTW, TH as MTH
import v5m_voice as MV
from v5m_talk import m_scrap, small_chip, pin_svg, LRED, SOFTRED, POD_CSS as MPOD_CSS, bleed, grow, scrap_grid, ctape, LDOTS

W = MW - 2 * MPAD   # 346
HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, 'manifest_edge_talk.json')
BOARDS = []
def board(name, title, w, h, row):
    BOARDS.append({"file": name + '.dc.html', "title": title, "w": w, "h": h, "row": row})

RETRY = '<path d="M13 8.5a5 5 0 1 1-1.6-3.7M13 2.5v3h-3" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
EXTRA_CSS = f"""
.write{{text-wrap:balance}}
.dead .hl{{background-image:linear-gradient(transparent 38%,rgba(150,145,138,.32) 38%,rgba(150,145,138,.32) 90%,transparent 90%)}}
.dead{{opacity:.55}}
.slipfall{{animation:slipfall 1.4s cubic-bezier(.3,.9,.4,1) var(--w,.3s) both}}
@keyframes slipfall{{from{{transform:translateY(-14px) rotate(var(--r0,0deg))}}to{{transform:none}}}}
.retry{{animation:retry 1s ease var(--w,1.2s) both}}
@keyframes retry{{from{{opacity:0;transform:translateY(-4px)}}to{{opacity:1;transform:none}}}}
.slot{{border:1.5px dashed rgba(34,30,26,.28)}}
.flat{{animation:flat 1.6s cubic-bezier(.4,0,.2,1) .4s both}}
@keyframes flat{{from{{opacity:1}}to{{opacity:1}}}}
"""
DCSS = POD_CSS + EXTRA_CSS
MCSS = POD_CSS + MPOD_CSS + EXTRA_CSS


def mini_scrap(text, feat, href, rot, seed, kind=''):
    inner = (f'<div style="{HAND};font-size:20px;color:{INK};white-space:nowrap">{text}</div>'
             f'<div style="{TYPE};font-size:9.5px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>')
    return f'<a href="{href}" class="chip" style="display:block">{paper(inner, 222, 74, rot=rot, seed=seed, kind=kind, pad="13px 18px")}</a>'

def fail_line(text, t='11:57', i=0, phone=False):
    """Your line that didn't make it: greyed, with a red-ink retry under it."""
    fs, lh, hs = (16, 26, 9) if phone else (19, 30, 10)
    return (f'<div class="msg" style="--i:{i};align-self:flex-end;max-width:{"84%" if phone else "74%"};text-align:left">'
            f'<div class="dead"><div style="{TYPE};font-size:{hs}px;letter-spacing:.16em;color:{PENCIL};margin-bottom:{3 if phone else 4}px;text-align:right">YOU · {t}</div>'
            f'<span class="hl" style="{SERIF};font-size:{fs}px;line-height:{lh}px;color:{INK}">{text}</span></div>'
            f'<a href="#" class="retry" style="--w:1.3s;display:flex;align-items:center;justify-content:flex-end;gap:7px;margin-top:{6 if phone else 8}px;color:{RED};{MARK};font-size:{18 if phone else 21}px;line-height:1">'
            f'{ic(RETRY, 14 if phone else 16)}<span>didn\'t send · try again</span></a></div>')

def pencil_line(text, i=0, phone=False):
    """A quiet event written across the sheet in pencil."""
    if phone:
        return (f'<div class="msg" style="--i:{i};align-self:center;max-width:86%;padding:6px 0;border-top:1.5px dashed {RULE};border-bottom:1.5px dashed {RULE};'
                f'{MARK};font-size:19px;line-height:1.2;color:{PENCIL};text-align:center">{text}</div>')
    dash = 60
    return (f'<div class="msg" style="--i:{i};align-self:center;display:flex;align-items:center;gap:{8 if phone else 14}px;{MARK};font-size:{18 if phone else 22}px;line-height:1;color:{PENCIL};white-space:nowrap">'
            f'<span style="width:{dash}px;border-top:1.5px dashed {RULE}"></span><span>{text}</span><span style="width:{dash}px;border-top:1.5px dashed {RULE}"></span></div>')

def write_manifest():
    json.dump(BOARDS, open(MANIFEST, 'w'), indent=1)


# ---------------- desktop chat sheet with an optional pinned slip at the top ----------------
def dsheet(msgs, tail='', top='', header='11:52 PM · YOU BOTH JOINED · NOTHING HERE IS SAVED'):
    inner = f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.16) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">{header}</div>
{top}
<div class="scroll" style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;padding:18px 6px 14px;overflow:hidden">{msgs}{tail}</div>
<div style="border-top:1.5px dashed {RULE};padding-top:16px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<span style="{SERIF};font-style:italic;font-size:19px;color:{PENCIL}">say it however it comes out…<span class="blink" style="color:{RED};font-style:normal">|</span></span>
<span style="display:flex;align-items:center;gap:22px;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}"><span>ENTER TO SEND</span>{chip('send ↗', '#', kind='ink', seed=533, w=120)}</span></div>
</div>"""
    return paper(inner, CW, CH, rot=0.3, kind='hi', seed=534, pad='22px 34px 22px', tapes=tape(CW / 2 - 60, -14, 120, 30, rot=-2, seed=53))

def convo_html(convo, start=0, line=line_msg):
    return ''.join(line(t, m, t=tt, i=start + i) for i, (t, m, tt) in enumerate(convo))

STD_BTNS = f'''<div style="display:flex;flex-direction:column;gap:14px;margin-top:24px">
{pod_btn('ask for voice', 'V5VoiceWait.dc.html', MIC, 'ink', seed=561)}
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};line-height:1.6;margin-top:2px">VOICE STARTS ONLY IF YOU BOTH SAY YES.</div></div>'''

LATE = [
    ("you said earlier you never told her you miss her. do you want to?", False, '1:41'),
    ("I think I'm scared it'll sound needy", True, '1:43'),
    ("missing someone isn't needy. it just means the tuesdays mattered.", False, '1:44'),
    ("okay. maybe I'll text her tomorrow. just 'I miss chai tuesdays'.", True, '1:47'),
    ("that's a perfect text. honestly.", False, '1:48'),
]
MLATE = [
    ("you said you never told her you miss her. do you want to?", False, '1:41'),
    ("I think I'm scared it'll sound needy", True, '1:43'),
    ("missing someone isn't needy. it means the tuesdays mattered.", False, '1:44'),
    ("okay. maybe I'll text her tomorrow. just 'I miss chai tuesdays'.", True, '1:47'),
    ("that's a perfect text. honestly.", False, '1:48'),
]

# =====================================================================
# T10 — Nobody's free right now
# =====================================================================
YOU_PIN = (330, 120)
LST = [(720, 84, -9, 611, -6, 26), (880, 214, 8, 612, 12, 12), (1040, 70, -13, 613, -4, 34), (1190, 196, 11, 614, 8, 16)]
def still_board():
    slips = ''
    holes = ''
    for i, (x, y, rot, seed, dx, dy) in enumerate(LST):
        inner = "<div style='padding-top:22px'></div>"
        slips += (f'<div class="slipfall" style="--w:{.3 + i * .15:.2f}s;--r0:{-rot * .6:.0f}deg;position:absolute;left:{x - 64 + dx}px;top:{y - 14 + dy}px">'
                  f'{paper(inner, 128, 104, rot=rot, kind="hi" if i % 2 else "", seed=seed, pad="10px 18px")}</div>')
        holes += f"<circle cx='{x}' cy='{y}' r='2' fill='#000'/><circle cx='{x - .6}' cy='{y - .6}' r='3' fill='none' stroke='#6a6763' stroke-width='.7' opacity='.5'/>"
    loose = pin_svg(905, 300, '#3a3a3d', 7) + pin_svg(1110, 168, '#3a3a3d', 7)
    taut = "M330 120 C 450 260 600 250 720 84"
    slack = "M330 120 C 318 280 420 318 486 268"
    thread = (f"<path d='{slack}' fill='none' stroke='{RED}' stroke-width='2.2' stroke-linecap='round' style='filter:drop-shadow(0 3px 2px rgba(0,0,0,.55))'>"
              f"<animate attributeName='d' from='{taut}' to='{slack}' dur='1.8s' begin='0.3s' fill='freeze' calcMode='spline' keyTimes='0;1' keySplines='.3 .7 .2 1'/></path>")
    you = paper(f'<div style="{HAND};font-size:36px;color:{INK};line-height:1">you</div>'
                f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-top:12px">QUIET_OTTER</div>',
                176, 128, rot=-3, kind='hi', seed=621, pad='30px 22px')
    return f'''<div style="position:relative;width:1400px;height:330px;margin-top:6px">
<div style="position:absolute;left:{YOU_PIN[0] - 88}px;top:{YOU_PIN[1] - 16}px">{you}</div>
{slips}
<svg width="1400" height="330" viewBox="0 0 1400 330" aria-hidden="true" style="position:absolute;inset:0;overflow:visible;z-index:5">{holes}{thread}{pin_svg(*YOU_PIN, RED)}{loose}</svg></div>'''

nofree = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='talk pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center">
{still_board()}
<div style="display:flex;flex-direction:column;align-items:center;gap:12px;margin-top:-8px">
{h_hand("Nobody's free right now.", 58)}
<div class="rise" style="--w:1.2s;{SERIF};font-size:21px;color:{ASH}">It's a quiet night. Keep waiting, or let it out on your own.</div>
<div class="rise" style="--w:1.4s;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">LOOKED FOR 3 MINUTES · NOTHING KEPT</div>
</div>
<div style="display:flex;align-items:flex-start;gap:70px;margin-top:28px">
<div class="rise" style="--w:1.7s;width:380px;display:flex;flex-direction:column;gap:20px;padding-top:30px">
<div style="display:flex;align-items:center;gap:30px;white-space:nowrap">{chip('keep waiting', 'V5Matching.dc.html', kind='ink', seed=1801, w=200)}{link('stop looking', 'V5Home.dc.html')}</div>
<div style="{MARK};font-size:21px;line-height:1.2;color:{SOFTRED};transform:rotate(-1.5deg)">it's not you. some nights<br>are just quieter.</div></div>
<div class="rise" style="--w:2s;display:flex;flex-direction:column;gap:12px;width:470px">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">OR LET IT OUT ON YOUR OWN · ANY TIME</div>
<div style="display:grid;grid-template-columns:repeat(2,222px);gap:12px 14px">{mini_scrap('get it out', 'BURN', 'V5Burn.dc.html', -1.5, 1881)}{mini_scrap('leave it somewhere', 'ECHOES', 'V5Echoes.dc.html', 1.2, 1882, 'kraft')}{mini_scrap("write it, don't send", 'UNSENT', 'V5UnsentWrite.dc.html', .8, 1883, 'kraft')}{mini_scrap('hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', -1, 1884)}</div></div>
</div>
</main>'''
page('V5NoOneFree', "Nobody's free right now", nofree, css=EXTRA_CSS)
LV.mark('V5NoOneFree', replace=[('LOOKED FOR 3 MINUTES', '{{looked}}')])
board('V5NoOneFree', "T11 — Nobody's free right now", 1440, 900, 'edge_talk')

# =====================================================================
# T11 — Pods close in 10 minutes
# =====================================================================
def close_slip(w=560, phone=False):
    fs = 18 if phone else 23
    inner = (f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">'
             f'<span style="{TYPE};font-weight:700;font-size:{9 if phone else 10}px;letter-spacing:.16em;color:{RED}">12:50 AM</span>'
             f'<span style="{TYPE};font-size:{9 if phone else 10}px;letter-spacing:.14em;color:{PENCIL}">KEEP TALKING</span></div>'
             f'<div style="{HAND};font-size:{fs}px;line-height:1.3;color:{INK};margin-top:6px">{"10 minutes left. pods close at 2am." if not phone else "10 minutes left."}<br>say what you need to.</div>')
    h = 118 if phone else 118
    return (f'<div class="pinned" style="--w:.9s;align-self:center;margin-top:{10 if phone else 14}px">'
            f'{paper(inner, w, h, rot=-1.2, kind="kraft", seed=1811, pad="14px 18px" if phone else "16px 24px", tapes=tape(w / 2 - 40, -11, 80, 22, rot=3, red=True, seed=181))}</div>')

closing_side = side_card(STD_BTNS.replace("CHECK-IN", "CHECK-IN"))
closing = pod_layout(side_card(STD_BTNS), dsheet(convo_html(LATE), typing(), close_slip(), header='1:31 AM · YOU BOTH JOINED · NOTHING HERE IS SAVED'))
closing = closing.replace("PODS OPEN · UNTIL 2AM", "PODS CLOSE AT 2AM · 10 MIN LEFT")
page('V5PodsClosing', 'Pods close in 10 minutes', closing, css=DCSS)
LV.pod('V5PodsClosing')
board('V5PodsClosing', 'T12 — Pods close soon', 1440, 900, 'edge_talk')

# =====================================================================
# T12 — It's 2am. The pod closed.
# =====================================================================
def clock(size=96, color=CHALK, uid='c'):
    """A hand-drawn clock at 2:00."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" aria-hidden="true" style="overflow:visible">'
            f'<defs><filter id="ck{uid}"><feTurbulence type="fractalNoise" baseFrequency=".06" numOctaves="2" seed="4"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter></defs>'
            f'<g filter="url(#ck{uid})" fill="none" stroke="{color}" stroke-linecap="round">'
            f'<path class="draw" style="--len:320;--d:1.4s;--w:.3s" d="M50 6 C76 5 95 24 94 50 C93 76 74 95 49 94 C24 93 6 74 7 49 C8 25 26 7 52 8" stroke-width="2.4"/>'
            f'<path class="draw" style="--len:40;--d:.5s;--w:1.6s" d="M50 50 L50 18" stroke-width="2.6"/>'
            f'<path class="draw" style="--len:30;--d:.5s;--w:2s" d="M50 50 L67 40" stroke-width="3.4"/>'
            + ''.join(f'<path d="M{50 + 38 * math.sin(a):.1f} {50 - 38 * math.cos(a):.1f} L{50 + 43 * math.sin(a):.1f} {50 - 43 * math.cos(a):.1f}" stroke-width="2" opacity=".7"/>' for a in [k * math.pi / 6 for k in range(12)]) +
            f'</g><circle cx="50" cy="50" r="3" fill="{color}"/></svg>')

FADE_CSS = """
.fadeaway{display:flex;flex-direction:column;animation:fadeaway 2.8s ease var(--w,1.6s) forwards}
@keyframes fadeaway{to{opacity:var(--o,.3)}}
"""
LAST = LATE[1:] + [("send her that text. and go easy on yourself tonight.", False, '1:59')]
def faded(items, phone=False):
    n = len(items)
    out = ''
    for k, (t, m, tt) in enumerate(items):
        o = .16 + .34 * k / max(1, n - 1)
        ln = mmsg(t, m, t=tt, i=k) if phone else line_msg(t, m, t=tt, i=k)
        out += f'<div class="fadeaway" style="--w:{1.4 + k * .25:.2f}s;--o:{o:.2f}">{ln}</div>'
    return out

def asleep_line(phone=False):
    return (f'<div class="fadein" style="--w:2.8s;align-self:center;display:flex;align-items:center;gap:{10 if phone else 14}px;{MARK};font-size:{19 if phone else 23}px;line-height:1;color:{PENCIL};white-space:nowrap">'
            f'<span style="width:{22 if phone else 56}px;border-top:1.5px dashed {RULE}"></span><span>2:00 · pods are asleep</span><span style="width:{22 if phone else 56}px;border-top:1.5px dashed {RULE}"></span></div>')

closed_sheet = paper(f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.14) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">1:31 AM · YOU &amp; MOSS_BYTE</div>
<div class="scroll" style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;padding:18px 6px 18px;overflow:hidden">{faded(LAST)}{asleep_line()}</div>
<div style="border-top:1.5px dashed {RULE};padding-top:14px;{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};text-align:center">IT ENDED FOR BOTH OF YOU · NOTHING KEPT</div>
</div>""", 600, 600, rot=-.8, kind='hi', seed=1821, pad='22px 32px 20px', tapes=tape(240, -14, 120, 30, rot=-2, seed=182))
closed = f'''
{atmos()}
{topbar(right='PODS OPEN AT 10PM', crumb='talk pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:96px;padding:0 56px 30px">
<div class="rise" style="--w:.2s">{closed_sheet}</div>
<div style="width:540px;display:flex;flex-direction:column;gap:16px">
<div class="fadein" style="--w:.6s">{clock(84, CHALK, 'd')}</div>
{h_hand("It's 2am.<br>Pods are asleep now.", 54, color=PAPERHI, wait='1.2s', d='2.2s', extra='white-space:nowrap')}
<div class="rise" style="--w:2.6s;{SERIF};font-size:21px;line-height:1.5;color:{ASH}">The conversation ended for both of you, gently, at the same time. Nothing was kept.</div>
<div class="rise" style="--w:2.8s;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">PODS OPEN AGAIN AT 10PM</div>
<div class="rise" style="--w:3.3s;display:flex;align-items:center;gap:34px;margin-top:24px">{chip('back home', 'V5Home.dc.html', kind='ink', seed=1822, w=180)}{link('leave something on the wall', 'V5EchoWrite.dc.html')}</div>
</div>
</main>
{footer()}'''
page('V5PodsClosedMidChat', "Pods are asleep now", closed, css=DCSS + FADE_CSS)
LV.mark('V5PodsClosedMidChat', replace=[('1:31 AM', '{{joined}}')])
board('V5PodsClosedMidChat', "T13 — Pods closed mid-conversation", 1440, 900, 'edge_talk')

# =====================================================================
# T13 — A message didn't send
# =====================================================================
FAILED = "and the worst part is I haven't told anyone. it feels silly to miss someone who only moved."
SEND_NOTE = "the connection slipped for a second. your words are still here."
sendfail = pod_layout(side_card(STD_BTNS), dsheet(convo_html(CONVO) + fail_line(FAILED, '11:57', 5),
                      f'<div class="retry" style="--w:1.9s;align-self:center;margin-top:2px">{inline_note(SEND_NOTE, "pencil", 21)}</div>'))
page('V5SendFailed', "A message didn't send", sendfail, css=DCSS)
LV.pod('V5SendFailed')
board('V5SendFailed', "T14 — A message didn't send", 1440, 900, 'edge_talk')

# =====================================================================
# V04 — They'd rather keep to text
# =====================================================================
dec_msgs = (convo_html(CONVO) + VX.sys_line('11:57 · you asked for voice', 5) + pencil_line("they'd like to keep it to text. that's okay.", 6)
            + line_msg("still here. tell me more about the tuesdays?", False, t='11:58', i=7))
declined = pod_layout(side_card(STD_BTNS), dsheet(dec_msgs))
page('V5VoiceDeclined', "They'd rather keep to text", declined, css=DCSS)
LV.pod('V5VoiceDeclined')
board('V5VoiceDeclined', "T15 — They'd rather keep it to text", 1440, 900, 'edge_talk')

# =====================================================================
# V05 — Voice dropped
# =====================================================================
def drop_slip(w=440, phone=False):
    fs = 21 if phone else 26
    inner = (f'<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">'
             f'<span style="{TYPE};font-weight:700;font-size:{9 if phone else 10}px;letter-spacing:.16em;color:{RED}">12:03 AM</span>'
             f'<span style="{TYPE};font-size:{9 if phone else 10}px;letter-spacing:.14em;color:{PENCIL}">NOTHING WAS RECORDED</span></div>'
             f'<div style="{HAND};font-size:{fs}px;line-height:1.3;color:{INK};margin-top:6px">The line dropped.<br>You\'re back on text.</div>')
    h = 104 if phone else 118
    return (f'<div class="pinned" style="--w:.9s;align-self:center;margin-top:{10 if phone else 14}px">'
            f'{paper(inner, w, h, rot=-1.2, kind="kraft", seed=1852, pad="14px 18px" if phone else "16px 26px", tapes=tape(w / 2 - 40, -11, 80, 22, rot=3, red=True, seed=185))}</div>')

DROP_BTNS = f'''<div style="display:flex;flex-direction:column;gap:14px;margin-top:24px">
{pod_btn('ask again', 'V5VoiceWait.dc.html', MIC, 'ink', seed=561)}
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};line-height:1.6;margin-top:2px">ASK FOR VOICE AGAIN WHENEVER. IT STARTS ONLY IF YOU BOTH SAY YES.</div></div>'''
DROP_AFTER = ("lost you for a sec. still here, just typing now.", False, '1:03')
drop_msgs = convo_html(CONVO[2:]) + VX.sys_line('12:02 · the voice line dropped', 3) + line_msg(DROP_AFTER[0], False, t=DROP_AFTER[2], i=4)
page('V5CallDropped', 'Voice dropped', pod_layout(side_card(DROP_BTNS), dsheet(drop_msgs, '', drop_slip())), css=DCSS)
LV.pod('V5CallDropped')
board('V5CallDropped', 'T16 — Voice dropped', 1440, 900, 'edge_talk')

# =====================================================================
# T14 — Tonight's question, first one here
# =====================================================================
def seat(name=None, me=False, h=46, fs=26, phone=False):
    if name:
        return (f'<div style="display:flex;align-items:center;justify-content:space-between;height:{h}px;border-bottom:1px dashed {RULE}">'
                f'<span style="{HAND};font-size:{fs}px;color:{INK}">{name}{" (you)" if me else ""}</span>'
                f'<span style="{TYPE};font-size:{9 if phone else 10}px;letter-spacing:.16em;color:{PENCIL}">LISTENING</span></div>')
    return (f'<div style="display:flex;align-items:center;height:{h}px;border-bottom:1px dashed {RULE}">'
            f'<span class="slot" style="display:block;width:{120 if phone else 170}px;height:{h - 20}px;border-radius:3px;opacity:.8"></span>'
            f'<span style="margin-left:auto;{TYPE};font-size:{9 if phone else 10}px;letter-spacing:.16em;color:{PENCIL};opacity:.55">OPEN SEAT</span></div>')

eroom = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 24)}<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">JUST YOU, FOR NOW</span></div>
<div style="margin-top:10px">{seat('quiet_otter', True)}{seat()}{seat()}{seat()}{seat()}{seat()}</div>
<div style="{MARK};font-size:21px;color:{RED};margin-top:16px;transform:rotate(-1deg)">a seat for you, and room for more.</div>''',
    520, 410, rot=1.2, kind='kraft', seed=1861, pad='30px 36px', tapes=tape(200, -13, 110, 28, rot=-3, seed=186))
qempty = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb="tonight's question")}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:80px;padding-bottom:40px">
<div class="rise" style="--w:.2s">{polaroid('sky', 380, 260, "What's something you pretend doesn't bother you?", rot=-2.5, seed=562, u='egq', capsize=30)}</div>
<div style="display:flex;flex-direction:column;gap:12px;width:560px">
{h_hand("You're the first one here.", 48, wait='.5s', extra='white-space:nowrap')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:21px;color:{ASH}">Stay, someone might come.</div>
<div class="rise" style="--w:.8s;margin-top:22px">{eroom}</div>
<div class="rise" style="--w:1.8s;display:flex;align-items:center;gap:30px;margin-top:26px">{chip('stay a while', '#', kind='ink', seed=1862, w=200)}{link('not tonight', 'V5Home.dc.html')}</div>
</div>
</main>'''
page('V5QuestionEmpty', "Tonight's question, first one here", qempty, css=EXTRA_CSS)
LV.mark('V5QuestionEmpty', replace=[("What's something you pretend doesn't bother you?", '{{question}}')])
board('V5QuestionEmpty', "T17 — First one in the room", 1440, 900, 'edge_talk')

# =====================================================================
# R04 — Every room is full
# =====================================================================
FULL = [(n, t, 10, s) for n, t, _, s in [ROOMS[1], ROOMS[2], ROOMS[3], ROOMS[6], ROOMS[8]]]
full_grid = ''.join(room_slip(i, *R) for i, R in enumerate(FULL))
allfull = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='open pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:4px 56px 0">
<div style="display:flex;align-items:flex-end;justify-content:space-between;gap:40px">
<div>{h_hand('Every room is full right now.', 58)}
<div class="rise" style="--w:1s;{SERIF};font-size:20px;color:{ASH};margin-top:2px">A seat opens when someone leaves.</div></div>
<div class="rise" style="--w:1.2s;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT};padding-bottom:6px">EVERY ROOM 10 OF 10</div></div>
<div style="display:grid;grid-template-columns:repeat(5,236px);justify-content:space-between;margin-top:64px">{full_grid}</div>
<div class="rise" style="--w:1.6s;display:flex;align-items:center;justify-content:center;gap:40px;margin-top:84px">{chip('waiting for a seat', '#', kind='ink', seed=1871, w=290, state='loading')}{link('try a 1:1 instead', 'V5Matching.dc.html')}</div>
<div class="rise" style="--w:1.9s;text-align:center;margin-top:18px;{MARK};font-size:21px;color:{SOFTRED}">stay on this page. you'll go in when a seat opens.</div>
</main>
{footer()}'''
page('V5RoomsAllFull', 'Every room is full', allfull, css=VX.rooms_css)
LV.mark('V5RoomsAllFull', slots=[('<div style="display:grid;grid-template-columns:repeat(5,236px);justify-content:space-between;margin-top:64px">', 'grid')])
board('V5RoomsAllFull', 'T18 — Every room is full', 1440, 900, 'edge_talk')

# =====================================================================
# R05 / R06 — room variants
# =====================================================================
def room_card2(title, theme, n, you_block, btns='', h=560):
    return paper(f'''
{t_mark('open pod', 22)}
<div style="{HAND};font-size:34px;line-height:1.15;margin-top:4px">{title}</div>
<div style="{SERIF};font-style:italic;font-size:16px;color:{PENCIL};margin-top:2px">{theme}</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px">{dots10(n, 9, 4)}<span style="{TYPE};font-weight:700;font-size:11px;letter-spacing:.1em">{n}/10</span></div>
{you_block}
<div style="display:flex;flex-direction:column;gap:14px;margin-top:22px">{btns}
{pod_btn('leave gently', 'V5Rooms.dc.html', DOOR, 'kraft', seed=722, w=230)}
{pod_btn('report someone', 'V5Reported.dc.html', FLAG, 'red')}</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};line-height:1.6;margin-top:14px">ONLY MODS LET HANDS UP OR MOVE SPEAKERS OFF STAGE. NEVER RECORDED.</div>''',
        290, h, rot=-1.2, seed=981, pad='28px 28px', tapes=tape(95, -13, 100, 26, rot=-4, seed=98))

def lrow(names, you=None):
    out = []
    for nm in names:
        y = f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">YOU</span>' if nm == you else ''
        out.append(f'<span style="display:inline-flex;align-items:center;gap:6px;{HAND};font-size:21px;color:{INK}">{nm}{y}</span>')
    return f'<div style="display:flex;flex-wrap:wrap;column-gap:26px;row-gap:6px">{"".join(out)}</div>'

def empty_tag(w=282, h=136, i=0, label='OPEN SEAT ON STAGE'):
    rot = [.9, .6, -.8][i % 3]
    return (f'<div class="rise slot" style="--w:{.6 + i * .12:.2f}s;width:{w}px;height:{h}px;transform:rotate({rot}deg);border-radius:3px;border-color:rgba(34,30,26,.3);'
            f'display:flex;align-items:center;justify-content:center;{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};opacity:.7">{label}</div>')

def stage2(tags, count_label, listeners_html, lcount, w=660, h=560):
    inner = f'''<div style="display:flex;align-items:baseline;justify-content:space-between;padding-bottom:10px;border-bottom:1px dashed {RULE}">
<span style="{HAND};font-size:30px;color:{INK}">on stage</span><span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">{count_label}</span></div>
<div style="display:grid;grid-template-columns:repeat(2,282px);justify-content:space-between;row-gap:24px;margin-top:22px">{tags}</div>
<div style="margin-top:28px;padding-top:12px;border-top:1.5px dashed {RULE}">
<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:10px"><span style="{HAND};font-size:26px;color:{INK}">listening</span>
<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">{lcount}</span></div>
{listeners_html}</div>'''
    return paper(inner, w, h, rot=.4, kind='kraft', seed=971, pad='26px 30px', tapes=tape(w / 2 - 60, -14, 120, 30, rot=-2, seed=97))

def room_shell(card, stage, right):
    return f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='open pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;justify-content:space-between;align-items:center;padding:0 56px 30px">
<div class="rise" style="--w:.1s">{card}</div>
<div class="rise" style="--w:.3s">{stage}</div>
<div style="padding-top:14px">{right}</div>
</main>
{footer()}'''

# R05 — moved back to listening
OFF_STAGE = [('neon_moth', 'speaking', False, False), ('paper_kite', 'muted', False, False), ('dusk_signal', 'listening', True, False), ('velvet_crow', 'listening', False, False)]
off_you = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(.5deg)">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">YOU</div>
<div style="{HAND};font-size:23px;color:{INK};line-height:1.1;margin-top:4px">listening</div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:6px">Your mic is off. Raise a hand whenever you'd like to speak again.</div></div>'''
off_slip = paper(f'''
<div style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{RED}">OFF STAGE · MIC OFF</div>
<div style="{HAND};font-size:31px;line-height:1.25;color:{INK};margin-top:10px">You're listening again.</div>
<div style="{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:8px">A mod moved you off stage. It happens, no reason needed.</div>
<a href="V5RoomHand.dc.html" class="ul" style="display:inline-flex;align-items:center;gap:8px;margin-top:20px;{TYPE};font-weight:700;font-size:11.5px;letter-spacing:.16em;color:{INK}">{ic(HANDI, 16)}RAISE HAND AGAIN</a>
<div style="{TYPE};font-size:9.5px;letter-spacing:.13em;line-height:1.6;color:{PENCIL};margin-top:16px">A MOD LETS YOUR HAND UP WHEN THERE'S ROOM.</div>''',
    290, 330, rot=-1.8, kind='hi', seed=1891, pad='26px 26px', tapes=tape(92, -13, 104, 26, rot=-3, red=True, seed=189))
off_right = (f'<div><div class="pinned" style="--w:1.1s">{off_slip}</div>'
             f'<div class="rise" style="--w:2s;margin-top:26px;padding-left:10px;{MARK};font-size:21px;color:{SOFTRED};transform:rotate(-2deg);line-height:1.2">listening is enough too.</div></div>')
off_stage = stage2(''.join(speaker_tag(i, *s, mod_view=False) for i, s in enumerate(OFF_STAGE)), '4 ON STAGE · MODS CHOOSE WHO COMES UP',
                   lrow(['static_heron', 'quiet_otter', 'fog_lamp', 'amber_fox'], you='quiet_otter'), '4 HERE · 2 SEATS OPEN')
page('V5MovedOffStage', 'Moved back to listening', room_shell(room_card2("can't sleep club", 'for the 1am ceiling starers', 8, off_you, h=520), off_stage, off_right), css=DCSS)
board('V5MovedOffStage', 'T19 — Moved off stage', 1440, 900, 'edge_talk')

# R06 — you're the first in the room
alone_you = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(184,53,42,.45);transform:rotate(-.6deg)">
<div style="display:flex;align-items:center;gap:10px">{star(26, uid='a')}<span style="{MARK};font-size:22px;color:{RED};line-height:1;white-space:nowrap">you're the first mod</span></div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:8px">You started it, so you hold the door for now.</div></div>'''
alone_stage = stage2(speaker_tag(0, 'quiet_otter', 'listening', True, True, mod_view=False) + ''.join(empty_tag(i=i) for i in range(3)),
                     '1 ON STAGE · 3 SEATS OPEN',
                     f'<div style="{HAND};font-size:22px;color:{PENCIL};opacity:.8">nobody yet. the door is open.</div>', '0 HERE · 9 SEATS OPEN')
alone_note = paper(f'''
{t_mark('what a mod does', 23)}
<div style="{SERIF};font-size:16.5px;line-height:1.55;color:{INK};margin-top:10px">When people arrive, you let raised hands up to speak, and you can move a speaker back to listening.</div>
<div style="{SERIF};font-size:16.5px;line-height:1.55;color:{INK};margin-top:10px">Others earn it by being kind in rooms like this. You don't have to do anything until someone's here.</div>
''',
    300, 300, rot=1.6, kind='hi', seed=1892, pad='26px 26px', tapes=tape(98, -13, 104, 26, rot=4, seed=190))
alone_right = (f'<div style="display:flex;flex-direction:column;gap:18px;width:310px">'
               f'{h_hand("You started this room.", 38, wait=".6s")}'
               f'<div class="rise" style="--w:1.4s;{SERIF};font-size:20px;line-height:1.45;color:{ASH};margin-top:-4px">The door is open. Stay a while, someone might come.</div>'
               f'<div class="pinned" style="--w:1.6s;margin-top:10px">{alone_note}</div></div>')
alone_card = room_card2('small wins', 'say the tiny good thing out loud', 1, alone_you, btns=pod_btn('mute', '#', MIC, 'ink', seed=721, w=230), h=600)
page('V5RoomAlone', "You're the first in the room", room_shell(alone_card, alone_stage, alone_right), css=DCSS)
board('V5RoomAlone', "T20 — Alone in your room", 1440, 900, 'edge_talk')


# #####################################################################
#                                PHONE
# #####################################################################
# in-pod phone screens share the VoiceWait shell: back arrow + "talk pod", the name strip with LEAVE / REPORT,
# the composer inside the paper, HELP top right.
def mchat_ed(msgs, tail='', top='', h=None, header='NOTHING HERE IS SAVED', voice=('ask for voice', 'V5MVoiceWait.dc.html')):
    """Live pod chat paper (MV.mchat: grows to the dock, composer pinned). Returns (sheet, voice) for mpod_page."""
    return MV.mchat(msgs, tail, top, header=header), voice

def mpod_page(sv, status="THEY'RE LISTENING"):
    sheet, voice = sv
    if voice:
        return MV.mpod(sheet, row=MV.voice_row(voice[0], voice[1], right=None), status=status)
    # no voice action on this screen: leave / report take the dock row
    return MV.mpod(sheet, row=f'<div style="flex:1 1 auto;display:flex;justify-content:space-between;align-items:center;min-height:48px">{MV.pod_sub()}</div>', sub='', status=status)

# ---------- MT10 — Nobody's free right now ----------
def mstill_board():
    BW, BH = 390, 300
    you_pin = (150, 92)
    lst = [(300, 52, -10, 711, -4, 24), (86, 214, 9, 712, 6, 10), (286, 200, -12, 713, -2, 26), (196, 250, 8, 714, 4, -46)]
    slips, holes = '', ''
    for i, (x, y, rot, seed, dx, dy) in enumerate(lst):
        slips += (f'<div class="slipfall" style="--w:{.3 + i * .15:.2f}s;--r0:{-rot * .6:.0f}deg;position:absolute;left:{x - 52 + dx}px;top:{y - 12 + dy}px">'
                  f'{paper("", 104, 84, rot=rot, kind="hi" if i % 2 else "", seed=seed, pad="8px 14px")}</div>')
        holes += f"<circle cx='{x}' cy='{y}' r='1.8' fill='#000'/><circle cx='{x - .6}' cy='{y - .6}' r='2.8' fill='none' stroke='#6a6763' stroke-width='.7' opacity='.5'/>"
    taut = "M150 92 C 210 170 260 150 300 52"
    slack = "M150 92 C 138 200 196 228 236 196"
    thread = (f"<path d='{slack}' fill='none' stroke='{RED}' stroke-width='2' stroke-linecap='round' style='filter:drop-shadow(0 3px 2px rgba(0,0,0,.55))'>"
              f"<animate attributeName='d' from='{taut}' to='{slack}' dur='1.8s' begin='0.3s' fill='freeze' calcMode='spline' keyTimes='0;1' keySplines='.3 .7 .2 1'/></path>")
    you = paper(f'<div style="padding:24px 20px"><div style="{HAND};font-size:32px;color:{INK};line-height:1">you</div>'
                f'<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL};margin-top:10px">QUIET_OTTER</div></div>', 150, 104, rot=-3, kind='hi', seed=622, pad='0')
    # the 4th slip is pulled lower than the board; keep it inside
    return f'''<div style="position:relative;width:{BW}px;height:{BH}px;flex-shrink:0">
<div style="position:absolute;left:26px;top:12px">{you}</div>{slips}
<svg width="{BW}" height="{BH}" viewBox="0 0 {BW} {BH}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible;z-index:5">{holes}{thread}{pin_svg(*you_pin, RED)}{pin_svg(64, 286, '#3a3a3d', 6)}</svg></div>'''

mnofree = f'''
{matmos()}
{mtopbar(crumb='talk pod', back='V5MHomeOpen.dc.html', right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">UNTIL 2AM</span>')}
{mbody(f'''<div style="flex:1 0 auto;display:flex;flex-direction:column;justify-content:center">{bleed(mstill_board())}</div>
<div style="width:100%;margin-top:-16px;flex-shrink:0">
{h_hand("Nobody's free right now.", 29, d='1.8s', extra='white-space:nowrap')}
<div class="rise" style="--w:1.2s;{SERIF};font-size:16px;line-height:1.5;color:{ASH};margin-top:6px">It's a quiet night. Keep waiting, or let it out on your own.</div>
<div class="rise" style="--w:1.4s;{TYPE};font-size:9.5px;letter-spacing:.16em;color:{BOARDTXT};margin-top:8px">LOOKED FOR 3 MINUTES · NOTHING KEPT</div></div>
<div class="rise" style="--w:2s;width:100%;padding:6px 4px 0;flex-shrink:0;{TYPE};font-size:9px;letter-spacing:.16em;color:{BOARDTXT}">OR LET IT OUT ON YOUR OWN</div>
<div style="flex-shrink:0">{scrap_grid(m_scrap('get it out', 'BURN', 'V5MBurn.dc.html', -1.5, 1981) + m_scrap('leave it somewhere', 'ECHOES', 'V5MEchoes.dc.html', 1.2, 1982, 'kraft') + m_scrap("write, don't send", 'UNSENT', 'V5MUnsentWrite.dc.html', .8, 1983, 'kraft') + m_scrap('hear it later', 'TIME CAPSULE', 'V5MCapsule.dc.html', -1, 1984))}</div>''', gap=12)}
<div class="rise" style="--w:1.7s;display:flex;flex-direction:column">{mdock(mcta('keep waiting', 'V5MMatching.dc.html', 'ink', seed=1901) + mtext('stop looking', 'V5MHomeOpen.dc.html'))}</div>
{mfooter()}'''
mpage('V5MNoOneFree', "Nobody's free right now", mnofree, css=EXTRA_CSS)
LV.mark('V5MNoOneFree', replace=[('LOOKED FOR 3 MINUTES', '{{looked}}')])
board('V5MNoOneFree', "MT11 — Nobody's free right now", 390, 844, 'm_edge_talk')

# ---------- MT11 — Pods close in 10 minutes ----------
mclosing = mpod_page(mchat_ed(''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MLATE)), mtyping(), close_slip(W - 36, phone=True),
                            header='1:31 AM · NOTHING SAVED'), status='10 MIN LEFT · CLOSES 2AM')
mpage('V5MPodsClosing', 'Pods close in 10 minutes', mclosing, css=MCSS)
LV.pod('V5MPodsClosing')
board('V5MPodsClosing', 'MT12 — Pods close soon', 390, 844, 'm_edge_talk')

# ---------- MT12 — It's 2am. The pod closed. ----------
mclosed_sheet = msheet(f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 25px,rgba(96,120,150,.14) 25px 26px);background-position:0 10px"></div>
<div style="position:relative;flex:1 1 auto;min-height:0;display:flex;flex-direction:column">
<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};text-align:center;padding-bottom:9px;border-bottom:1px dashed {RULE}">1:31 AM · YOU &amp; MOSS_BYTE</div>
<div class="scroll" style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:14px;padding:12px 2px 12px;overflow:hidden">{faded(LAST[-3:], phone=True)}{asleep_line(True)}</div>
</div>""", kind='hi', seed=1921, pad='16px 18px 14px', rot=-.6, minh=240, tapes=ctape(100, 26, -2, 192))
mclosed = f'''
{matmos()}
{mtopbar(crumb='talk pod', right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">PODS AT 10PM</span>')}
{mbody(f'''<div style="position:relative;width:100%;flex-shrink:0">
{h_hand("It's 2am.<br>Pods are asleep now.", 31, color=PAPERHI, wait='1s', d='2s', extra='white-space:nowrap')}
<div class="fadein" style="--w:.4s;position:absolute;right:2px;top:-4px">{clock(38, CHALK, 'm')}</div></div>
<div class="rise" style="--w:2.4s;width:100%;flex-shrink:0;{SERIF};font-size:16px;line-height:1.5;color:{ASH};margin-top:-6px">The conversation ended for both of you, gently, at the same time. Nothing was kept.</div>
<div style="height:8px;flex-shrink:0"></div>{grow(mclosed_sheet, '.2s')}''')}
<div class="rise" style="--w:3.1s;display:flex;flex-direction:column">{mdock(mcta('back home', 'V5MHomeOpen.dc.html', 'ink', seed=1922) + mtext('leave something<br>on the wall', 'V5MEchoWrite.dc.html'))}</div>
{mfooter()}'''
mpage('V5MPodsClosedMidChat', "Pods are asleep now", mclosed, css=MCSS + FADE_CSS)
LV.mark('V5MPodsClosedMidChat', replace=[('1:31 AM', '{{joined}}')])
board('V5MPodsClosedMidChat', "MT13 — Pods closed mid-conversation", 390, 844, 'm_edge_talk')

# ---------- MT13 — A message didn't send ----------
MFAILED = "and the worst part is I haven't told anyone. it feels silly to miss someone who only moved."
msendfail = mpod_page(mchat_ed(''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MCONVO)) + fail_line(MFAILED, '11:57', 5, phone=True),
                      f'<div class="retry" style="--w:1.9s;align-self:center;text-align:center;max-width:90%">{inline_note(SEND_NOTE, "pencil", 18)}</div>'))
mpage('V5MSendFailed', "A message didn't send", msendfail, css=MCSS)
LV.pod('V5MSendFailed')
board('V5MSendFailed', "MT14 — A message didn't send", 390, 844, 'm_edge_talk')

# ---------- MV04 — They'd rather keep to text ----------
mdec_msgs = (''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MCONVO[1:])) + msys('11:57 · you asked for voice', 4)
             + pencil_line("they'd like to keep it to text. that's okay.", 5, phone=True) + mmsg('still here. tell me more about the tuesdays?', t='11:58', i=6))
mdeclined = mpod_page(mchat_ed(mdec_msgs, '', voice=None))
mpage('V5MVoiceDeclined', "They'd rather keep to text", mdeclined, css=MCSS)
LV.pod('V5MVoiceDeclined')
board('V5MVoiceDeclined', "MT15 — They'd rather keep it to text", 390, 844, 'm_edge_talk')

# ---------- MV05 — Voice dropped ----------
mdrop_msgs = (''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MCONVO[3:])) + msys('12:02 · voice line dropped', 2)
              + mmsg(DROP_AFTER[0], False, t=DROP_AFTER[2], i=3))
mdrop = mpod_page(mchat_ed(mdrop_msgs, '', drop_slip(W - 36, phone=True), voice=('ask again', 'V5MVoiceWait.dc.html')), status='BACK ON TEXT')
mpage('V5MCallDropped', 'Voice dropped', mdrop, css=MCSS)
LV.pod('V5MCallDropped')
board('V5MCallDropped', 'MT16 — Voice dropped', 390, 844, 'm_edge_talk')

# ---------- MT14 — Tonight's question, first one here ----------
meroom = fcard(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 20)}<span style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL}">JUST YOU, FOR NOW</span></div>
<div style="margin-top:4px">{seat('quiet_otter', True, 36, 20, True)}{''.join(seat(None, h=34, phone=True) for _ in range(5))}</div>''',
    kind='kraft', seed=1961, pad='20px 24px', rot=1, tapes=ctape(100, 26, -3, 196))
mqempty = f'''
{matmos()}
{mtopbar(crumb="tonight's question", back='V5MHomeOpen.dc.html', right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">UNTIL 2AM</span>')}
{mbody(f'''<div class="rise" style="--w:.2s;align-self:center;flex-shrink:0">{polaroid('sky', 270, 96, "What's something you pretend doesn't bother you?", rot=-2, seed=1542, u='meq', capsize=21)}</div>
<div style="width:100%;padding:4px 0 0;flex-shrink:0">{h_hand("You're the first one here.", 30, wait='.5s')}
<div class="rise" style="--w:1.3s;{SERIF};font-size:17px;color:{ASH};margin-top:2px">Stay, someone might come.</div></div>
<div class="rise" style="--w:.8s;margin-top:4px;flex:0 0 auto;display:flex;flex-direction:column">{meroom}</div>''', gap=14, center=True)}
<div class="rise" style="--w:1.8s;display:flex;flex-direction:column">{mdock(mcta('stay a while', '#', 'ink', seed=1962) + mtext('not tonight', 'V5MHomeOpen.dc.html'))}</div>
{mfooter()}'''
mpage('V5MQuestionEmpty', "Tonight's question, first one here", mqempty, css=EXTRA_CSS)
LV.mark('V5MQuestionEmpty', replace=[("What's something you pretend doesn't bother you?", '{{question}}')])
board('V5MQuestionEmpty', "MT17 — First one in the room", 390, 844, 'm_edge_talk')

# ---------- MR04 — Every room is full ----------
mfull_grid = ''.join(mslip(i, n, t, 10, s, '#') for i, (n, t, _, s) in enumerate([ROOMS[1], ROOMS[2], ROOMS[3], ROOMS[8]]))
mallfull = f'''
{matmos()}
{mtopbar(back='V5MHomeOpen.dc.html', crumb='open pod', right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">UNTIL 2AM</span>')}
{mbody(f'''<div style="flex-shrink:0">{h_hand('Every room is full<br>right now.', 34)}
</div><div class="rise" style="--w:.9s;flex-shrink:0;{SERIF};font-size:16px;line-height:1.45;color:{ASH};margin-top:-10px">A seat opens when someone leaves.</div>
<div class="rise" style="--w:1s;flex-shrink:0;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT};margin-top:-4px;padding-bottom:10px;border-bottom:1px dashed {SOOT}">EVERY ROOM 10 OF 10</div>
<div style="flex-shrink:0;display:grid;grid-template-columns:repeat(2,{MSLW}px);justify-content:space-between;row-gap:22px;margin-top:8px">{mfull_grid}</div>''')}
<div class="rise" style="--w:1.5s;display:flex;flex-direction:column">{mdock(mcta('waiting for a seat' + LDOTS, '#', 'ink', seed=1971) + mtext('try a 1:1', 'V5MMatching.dc.html'))}</div>
{mfooter()}'''
mpage('V5MRoomsAllFull', 'Every room is full', mallfull, css=POD_CSS + """.rise.chip{animation:rise 1.1s cubic-bezier(.2,.7,.2,1) var(--w,.3s) forwards}""")
LV.mark('V5MRoomsAllFull', slots=[(f'<div style="flex-shrink:0;display:grid;grid-template-columns:repeat(2,{MSLW}px);justify-content:space-between;row-gap:22px;margin-top:8px">', 'grid')])
board('V5MRoomsAllFull', 'MT18 — Every room is full', 390, 844, 'm_edge_talk')

# ---------- MR05 / MR06 — room variants ----------
def mroom_head2(title, theme, n, right):
    return (f'<div class="rise" style="--w:.1s;padding:0 2px;flex-shrink:0">'
            f'<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:27px;color:{CHALK};line-height:1.15">{title}</span>'
            f'<span style="{TYPE};font-weight:700;font-size:10px;letter-spacing:.1em;color:{CHALK}">{n}/10</span></div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-top:5px">'
            f'<span style="{SERIF};font-style:italic;font-size:14px;color:{BOARDTXT}">{theme}</span>{right}</div></div>')

def mempty_tag(i):
    rot = [.9, .7, -.8][i % 3]
    return (f'<div class="rise slot" style="--w:{.5 + i * .1:.2f}s;width:{MTW}px;height:{MTH}px;transform:rotate({rot}deg);border-radius:3px;border-color:rgba(34,30,26,.3);'
            f'display:flex;align-items:center;justify-content:center;{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL};opacity:.7">OPEN SEAT</div>')

def mstage2(tags, count_label, listeners_html, lcount, h=408):
    inner = f'''<div style="display:flex;align-items:baseline;justify-content:space-between;padding-bottom:7px;border-bottom:1px dashed {RULE}">
<span style="{HAND};font-size:23px;color:{INK}">on stage</span><span style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL}">{count_label}</span></div>
<div style="display:grid;grid-template-columns:repeat(2,{MTW}px);justify-content:space-between;row-gap:12px;margin-top:12px">{tags}</div>
<div style="margin-top:14px;padding-top:7px;border-top:1.5px dashed {RULE}">
<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:21px;color:{INK}">listening</span>
<span style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL}">{lcount}</span></div>
{listeners_html}</div>'''
    return msheet(inner, kind='kraft', seed=771, pad='14px 10px 12px', rot=.3, minh=h, tapes=ctape(92, 24, -2, 77))

def mlrow(names, you=None):
    out = []
    for nm in names:
        y = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}">YOU</span>' if nm == you else ''
        out.append(f'<span style="display:inline-flex;align-items:center;gap:5px;{HAND};font-size:17.5px;color:{INK};white-space:nowrap">{nm}{y}</span>')
    return f'<div style="display:flex;flex-wrap:wrap;column-gap:18px;row-gap:2px">{"".join(out)}</div>'

def mroom_bar2(left):
    return (f'<div class="rise" style="--w:1s;display:flex;flex-direction:column">'
            + mdock(f'<div style="flex:1 1 auto;display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:48px">'
                    f'{left}{mlink("leave gently", "V5MRooms.dc.html", CHALK, 10.5, DOOR)}{mlink("report", "V5MReported.dc.html", LRED, 10.5, FLAG)}</div>', footer=False) + '</div>')

def mroom_page(head, stage, slip, bar):
    return f'''
{matmos()}
{mtopbar(back='V5MRooms.dc.html', crumb='open pod')}
{mbody(f'''{head}
<div class="rise" style="--w:.3s;flex:1 0 auto;display:flex;flex-direction:column">{stage}</div>
<div class="pinned" style="--w:1.2s;align-self:center;margin-top:-4px;flex-shrink:0">{slip}</div>''')}
{bar}'''

moff_stage = mstage2(''.join(mtag(i, n, s, m, me, False) for i, (n, s, m, me) in enumerate(OFF_STAGE)), '4 ON STAGE',
                     mlrow(['static_heron', 'quiet_otter', 'fog_lamp', 'amber_fox'], you='quiet_otter'), '4 HERE · 2 SEATS OPEN', h=418)
moff_slip = MV.note_slip(f'''<div style="{TYPE};font-size:9px;letter-spacing:.14em;color:{RED}">OFF STAGE · MIC OFF</div>
<div style="{HAND};font-size:24px;line-height:1.2;color:{INK};margin-top:6px">You're listening again.</div>
<div style="{SERIF};font-size:14.5px;line-height:1.45;color:{INK};margin-top:4px">A mod moved you off stage. It happens, no reason needed.</div>
<div style="margin-top:10px">{mlink('raise hand again', 'V5MRoomHand.dc.html', INK, 10.5, HANDI)}</div>''', 188, 1991, -1)
page_moff = mroom_page(mroom_head2("can't sleep club", 'for the 1am ceiling starers', 8, f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">YOU\'RE LISTENING</span>'),
                       moff_stage, moff_slip, mroom_bar2(f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">MIC OFF</span>'))
mpage('V5MMovedOffStage', 'Moved back to listening', page_moff, css=MCSS)
board('V5MMovedOffStage', 'MT19 — Moved off stage', 390, 844, 'm_edge_talk')

malone_stage = mstage2(mtag(0, 'quiet_otter', 'listening', True, True, False) + ''.join(mempty_tag(i) for i in range(3)), '1 ON STAGE · 3 OPEN',
                       f'<div style="{HAND};font-size:18px;color:{PENCIL};opacity:.85">nobody yet. the door is open.</div>', '0 HERE', h=384)
malone_slip = MV.note_slip(f'''{h_hand('You started this room.', 25, color=INK, wait='1s', d='1.4s')}
<div class="rise" style="--w:1.8s;{SERIF};font-size:15px;color:{PENCIL};margin-top:0">Stay a while, someone might come.</div>
<div class="rise" style="--w:2s;{SERIF};font-size:14px;line-height:1.45;color:{INK};margin-top:8px">You're its mod for now: you let raised hands up, and can move a speaker back to listening. Others earn it by being kind.</div>''', 196, 1993, -.8)
page_malone = mroom_page(mroom_head2('small wins', 'say the tiny good thing out loud', 1,
                                     f'<span style="display:inline-flex;align-items:center;gap:6px;{MARK};font-size:18px;color:{SOFTRED};line-height:1">{star(17, LRED, uid="ma")}you\'re the first mod</span>'),
                         malone_stage, malone_slip, mroom_bar2(mchip('mute', '#', 'ink', 118, seed=1995, icon=MIC, h=44)))
mpage('V5MRoomAlone', "You're the first in the room", page_malone, css=MCSS)
board('V5MRoomAlone', "MT20 — Alone in your room", 390, 844, 'm_edge_talk')

write_manifest()
print('pods edge ok', len(BOARDS))
