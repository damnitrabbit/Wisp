"""N0TRACE V5 — DLS board: components, states, rules. One tall desktop reference board (V5DLS).
Documents what exists in gen5.py, v5_talk.py (pod_btn, line_msg), v5_home.py (hrow), v5x_legal.py (toast),
v5x_echo.py (heard, stamp) and project/sound.js. Local copies of helpers are used so no other board is regenerated."""
from gen5 import *
from v5x_legal import apaper, toast, NOTICE_CSS
import json

SOFT, CRISIS, LIVE, FOCUS = '#F0A08F', '#E07A6E', '#E08A3C', GLOW
BOARD_BG, FRAME = '#0B0B0B', '#080808'
CW = 1328          # content width inside the 56px side margins
H = 6580


# ---------------------------------------------------------------- small atoms
def lab(t, c=PENCIL, size=10, ls='.16em', extra=''):
    return f'<div style="{TYPE};font-size:{size}px;letter-spacing:{ls};text-transform:uppercase;color:{c};line-height:1.55;{extra}">{t}</div>'

def spec(t, c=PENCIL, size=9.5):
    return f'<div style="{TYPE};font-size:{size}px;letter-spacing:.12em;text-transform:uppercase;color:{c};line-height:1.6;margin-top:6px">{t}</div>'

def serif(t, size=15, c=INK, extra=''):
    return f'<div style="{SERIF};font-size:{size}px;line-height:1.5;color:{c};{extra}">{t}</div>'

def hhead(t, size=26, c=INK, extra=''):
    return f'<div style="{HAND};font-size:{size}px;line-height:1.2;color:{c};{extra}">{t}</div>'

def sheet(inner, w, kind='hi', rot=0, seed=1, pad='28px 30px 30px', tx=None, red=False, tseed=None):
    tp = tape((tx if tx is not None else w / 2 - 48), -13, 96, 26, rot=random.Random(seed).choice([-4, -2, 3, 4]), seed=tseed or seed + 7, red=red)
    return apaper(inner, w, rot=rot, kind=kind, seed=seed, pad=pad, tapes=tp)

def sec(n, title, sub):
    return (f'<div style="display:flex;align-items:flex-end;gap:22px;margin-bottom:26px">'
            f'<span style="{HAND};font-size:50px;line-height:1;color:{SOFT};transform:rotate(-4deg);display:inline-block;padding-bottom:14px">{n}</span>'
            f'<div>{h_hand(title, 46, d="1.2s")}<div style="{TYPE};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{ASH};margin-top:4px">{sub}</div></div></div>')

def board_lab(t):
    return f'<div style="{TYPE};font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:{ASH};margin-bottom:12px">{t}</div>'

def hnote(t, c=CHALK, size=18, extra=''):
    return f'<div style="{HAND};font-size:{size}px;line-height:1.25;color:{c};{extra}">{t}</div>'

def bullets(items, c=INK, num_c=RED, size=15):
    return ''.join(f'<div style="display:grid;grid-template-columns:22px 1fr;gap:4px;padding:6px 0;border-bottom:1px dashed {RULE}">'
                   f'<span style="{MARK};font-size:19px;line-height:1.1;color:{num_c}">{i}</span>'
                   f'<span style="{SERIF};font-size:{size}px;line-height:1.45;color:{c}">{t}</span></div>' for i, t in enumerate(items, 1))


# ---------------------------------------------------------------- local copies of existing helpers
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
DOOR = '<path d="M3 15h10M5 15V2.5h6V15M9 9h.01M11 2.5l2 1.5V15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
FLAG = '<path d="M4 15V2.5M4 3h8l-2 3 2 3H4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'

def pod_btn(label, icon_, kind, seed=0, extra=''):
    """copy of v5_talk.pod_btn (240 x 50)."""
    ic = f'<svg width="16" height="17" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0">{icon_}</svg>'
    if kind == 'red':
        return (f'<a href="#" class="ul" style="align-self:flex-start;display:inline-flex;align-items:center;gap:10px;margin:6px 0 0 4px;color:{RED};'
                f'{TYPE};font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase;{extra}">{ic}<span>{label}</span></a>')
    ww, hh = 240, 50
    bg = {'ink': f'background-color:{INK};color:{PAPERHI}', 'kraft': f'background-color:{KRAFT};color:{INK}'}[kind]
    rot = {'ink': -.8, 'kraft': .7}[kind]
    return (f'<a href="#" class="chip lift" style="position:relative;display:flex;align-items:center;gap:12px;width:{ww}px;height:{hh}px;padding:0 18px;'
            f'color:{PAPERHI if kind == "ink" else INK};transform:rotate({rot}deg);{extra}">'
            f'<span class="paper" style="position:absolute;inset:0;{bg};clip-path:{deckle(ww, hh, amp=1.6, step=12, seed=seed)}"></span>'
            f'{ic}<span style="position:relative;flex-grow:1;{TYPE};font-weight:700;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase">{label}</span></a>')

def hrow(activity, feature, sw=260, hover=False, last=False):
    """copy of v5_home.hrow; hover=True shows the hover state statically."""
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    scr = f'width:{sw}px' if hover else ''
    go = 'transform:translateX(4px)' if hover else ''
    return (f'<a href="#" class="row" style="height:64px;{bb}--sw:{sw}px">'
            f'<span style="position:relative"><span style="{HAND};font-size:30px;color:{INK}">{activity}</span>'
            f'<span class="scribble" style="{scr}">{underline(sw, RED, 2.5, cls="", seed=len(activity))}</span></span>'
            f'<span class="go" style="display:flex;align-items:center;gap:12px;{TYPE};font-weight:700;font-size:12px;letter-spacing:.18em;color:{PENCIL};{go}">{feature}<span style="color:{INK};font-size:15px">→</span></span></a>')

def mini_scrap(text, feat, rot, seed, kind=''):
    inner = (f'<div style="{HAND};font-size:20px;color:{INK};white-space:nowrap">{text}</div>'
             f'<div style="{TYPE};font-size:9.5px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>')
    return f'<a href="#" class="chip" style="display:block">{paper(inner, 222, 74, rot=rot, seed=seed, kind=kind, pad="13px 18px")}</a>'

def scrap_link(text, feat, rot, seed, kind=''):
    inner = (f'<div style="{HAND};font-size:24px;color:{INK};white-space:nowrap">{text}</div>'
             f'<div style="{TYPE};font-size:10px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>')
    return f'<a href="#" class="chip" style="display:block">{paper(inner, 270, 112, rot=rot, seed=seed, kind=kind, pad="18px 24px")}</a>'

def pin_svg(col, r=8):
    s = r * 2 + 12
    x = y = r + 3
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 {s} {s}" aria-hidden="true" style="overflow:visible">'
            f"<ellipse cx='{x + 4}' cy='{y + 7}' rx='{r + 1}' ry='{r * .62:.1f}' fill='#000' opacity='.45'/>"
            f"<circle cx='{x}' cy='{y}' r='{r}' fill='{col}'/><circle cx='{x}' cy='{y}' r='{r}' fill='none' stroke='#000' stroke-opacity='.35'/>"
            f"<circle cx='{x - r * .32:.1f}' cy='{y - r * .32:.1f}' r='{r * .29:.1f}' fill='#fff' opacity='.28'/></svg>")

HEART = '<path d="M10 17 C3 12 1 8 3 5 C5 2 9 3 10 6 C11 3 15 2 17 5 C19 8 17 12 10 17 Z" fill="{f}" stroke="' + RED + '" stroke-width="1.8" stroke-linejoin="round"/>'
def heard_btn(on, size=24):
    f = RED if on else 'none'
    n = 13 if on else 12
    return (f'<button type="button" class="heard" aria-pressed="{"true" if on else "false"}" style="font-size:{size}px">'
            f'<svg width="{size - 2}" height="{size - 2}" viewBox="0 0 20 20" aria-hidden="true">{HEART.format(f=f)}</svg>heard · {n}</button>')

SPK = ('<svg width="15" height="13" viewBox="0 0 15 13" aria-hidden="true" style="flex-shrink:0"><path d="M1.5 4.5h2.6L7.6 1.6v9.8L4.1 8.5H1.5z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>'
       '<path class="w1" d="M9.8 4.3c.9.9.9 3.5 0 4.4" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><path class="w2" d="M11.6 2.6c1.9 1.9 1.9 5.9 0 7.8" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>'
       '<path class="x" d="M10 4.4l3.6 4.2M13.6 4.4L10 8.6" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>')
def pill(label, cls=''):
    return f'<span class="ntp {cls}">{SPK}<span>{label}</span></span>'


# ---------------------------------------------------------------- contrast
def _lum(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
def ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


# ================================================================= 0. header
intro = f'''
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:60px">
<div>
{t_type('N0TRACE V5 · design language system · for whoever builds it', 11)}
{h_hand('DLS. Components, states, rules.', 66, wait='.2s', d='1.8s', extra='margin-top:8px;white-space:nowrap;padding-right:20px')}
<div class="rise" style="--w:1s;max-width:780px;{SERIF};font-size:20px;line-height:1.55;color:{ASH};margin-top:10px">Everything N0TRACE is made of, measured. Values come straight from <span style="{TYPE};font-size:15px;color:{CHALK}">gen5.py</span>, the screen modules and <span style="{TYPE};font-size:15px;color:{CHALK}">sound.js</span>. If the code and this board disagree, the board is wrong: fix it here.</div>
</div>
<div class="rise" style="--w:1.4s;width:360px">{sheet(f"""
{lab('how to read this board')}
<div style="display:grid;grid-template-columns:auto 1fr;gap:8px 14px;margin-top:10px;align-items:baseline">
<span style="{HAND};font-size:20px;color:{INK}">hand</span>{serif('the rule, said plainly', 14)}
<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">TYPE</span>{serif('the exact value in code', 14)}
<span style="{MARK};font-size:20px;color:{RED}">red ink</span>{serif('a gap between code and rule', 14)}
</div>""", 360, rot=1, seed=9001, pad='24px 28px 26px')}</div>
</div>'''


# ================================================================= 1. colour
def swatch(name, hexv, token, where, seed, border=False):
    b = 'box-shadow:inset 0 0 0 1px rgba(34,30,26,.18);' if border else ''
    inner = (f'<div style="height:38px;background:{hexv};{b}"></div>'
             f'<div style="{HAND};font-size:19px;line-height:1.15;color:{INK};margin-top:8px">{name}</div>'
             f'<div style="{TYPE};font-size:9.5px;letter-spacing:.1em;color:{INK};margin-top:2px">{hexv.upper()} · {token}</div>'
             f'<div style="{SERIF};font-size:13px;line-height:1.35;color:{PENCIL};margin-top:5px">{where}</div>')
    return apaper(inner, 136, rot=random.Random(seed).uniform(-1.2, 1.2), kind='hi', seed=seed, pad='10px 10px 12px')

SW_BOARD = [
    ('night', NIGHT, 'NIGHT', 'page behind the board, body bg'),
    ('board', BOARD_BG, '.room', 'black cork + noise, the room itself'),
    ('frame', FRAME, '.room::after', '14px frame desktop, 7px phone'),
    ('soot', SOOT, 'SOOT', 'dashed rules on the board, footer line'),
    ('ash', ASH, 'ASH', 'quiet words + labels on the board'),
    ('chalk', CHALK, 'CHALK', 'words on the board, hand headlines'),
    ('soft red', SOFT, 'inline_note soft', 'care notes on the board'),
    ('crisis red', CRISIS, 'footer()', 'crisis link only. merge with soft red'),
    ('live', LIVE, 'livedot', 'live + listening dot, speaking'),
]
SW_PAPER = [
    ('paper', PAPER, 'PAPER', 'default sheet'),
    ('paper hi', PAPERHI, 'PAPERHI', 'chips, polaroids, sheets you write on'),
    ('kraft', KRAFT, 'KRAFT', 'your side, secondary chips, waiting'),
    ('ink', INK, 'INK', 'words on paper, primary chip'),
    ('pencil', PENCIL, 'PENCIL', 'labels + placeholders on paper'),
    ('rule', RULE, 'RULE', 'dashed lines + field lines on paper'),
    ('red ink', RED, 'RED', 'care, marks, heard, report, errors'),
    ('focus', FOCUS, 'GLOW', 'focus ring only (2px dashed)'),
    ('unused', '#161618', 'NIGHT2 · PAPER2', 'NIGHT2, PAPER2, ROSE, DAWN: not used. retire'),
]
sw_rows = ''.join(f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:{m}px">{"".join(swatch(*s, seed=9100 + o + i, border=s[1] in (PAPER, PAPERHI, KRAFT)) for i, s in enumerate(lst))}</div>'
                  for lst, o, m in [(SW_BOARD, 0, 0), (SW_PAPER, 20, 22)])

PAIRS = [  # fg, bg, name, where
    (INK, PAPER, 'ink on paper', 'all body copy on sheets'),
    (PENCIL, PAPER, 'pencil on paper', 'labels, placeholders'),
    (ASH, NIGHT, 'ash on night', 'labels on the board'),
    (CHALK, NIGHT, 'chalk on night', 'headlines on the board'),
    (RED, PAPER, 'red on paper', 'red ink notes, report'),
    (SOFT, NIGHT, 'soft red on night', 'care notes on the board'),
    (PAPERHI, INK, 'paper hi on ink', 'ink chip label'),
    (INK, KRAFT, 'ink on kraft', 'kraft chip, kraft sheet'),
    (PENCIL, KRAFT, 'pencil on kraft', 'labels on kraft sheets'),
    (RED, NIGHT, 'red on night', 'red text on the board'),
    ('#6A6A70', NIGHT, '#6A6A70 on night', 'v5x_legal dim labels'),
    (FOCUS, PAPER, 'focus on paper', 'focus ring on a sheet'),
]
def pair_row(fg, bg, name, where):
    r = ratio(fg, bg)
    verdict, vc = ('AA', INK) if r >= 4.5 else (('LARGE / UI ONLY', PENCIL) if r >= 3 else ('FAILS', RED))
    if name.startswith('focus'):
        verdict, vc = ('FAILS 3:1 (UI)', RED)
    return (f'<div style="display:grid;grid-template-columns:78px 1fr 56px;gap:10px;align-items:center;padding:7px 0;border-bottom:1px dashed {RULE}">'
            f'<div style="height:34px;background:{bg};display:flex;align-items:center;justify-content:center;{TYPE};font-weight:700;font-size:12px;letter-spacing:.1em;color:{fg};box-shadow:inset 0 0 0 1px rgba(34,30,26,.15)">Aa 11px</div>'
            f'<div><div style="{HAND};font-size:17px;line-height:1.1;color:{INK}">{name}</div><div style="{TYPE};font-size:9.5px;letter-spacing:.1em;color:{PENCIL};margin-top:2px">{where.upper()}</div></div>'
            f'<div style="text-align:right"><div style="{TYPE};font-weight:700;font-size:14px;color:{INK}">{r:.2f}</div><div style="{TYPE};font-size:9px;letter-spacing:.08em;color:{vc}">{verdict}</div></div></div>')
pcols = ''.join(f'<div style="border-top:1px dashed {RULE}">{"".join(pair_row(*p) for p in PAIRS[i * 3:(i + 1) * 3])}</div>' for i in range(4))
contrast = sheet(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{hhead('Contrast, measured (WCAG 2.x)', 28)}
<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">BODY ≥ 4.5 · LARGE TEXT (≥ 24PX HAND) + UI MARKS ≥ 3</span></div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:26px;margin-top:14px">{pcols}</div>
<div style="display:flex;gap:40px;margin-top:16px;align-items:flex-start">
{inline_note('pencil on kraft is 3.32. on kraft, labels go ink, not pencil.', 'red', 19)}
{inline_note('red on the board is 3.31: big hand only. small red on the board uses soft red.', 'red', 19)}
{inline_note('the focus ring vanishes on paper (1.39). see 8.', 'red', 19)}
</div>''', CW, rot=-.3, seed=9150, pad='28px 36px 30px')

s1 = f'''
<section>{sec('1', 'Colour', 'two worlds: the dark board, the light paper. tokens live in gen5.py')}
{board_lab('the board (dark)  ·  then  ·  the paper (light)')}
{sw_rows}
<div style="margin-top:40px">{contrast}</div>
</section>'''


# ================================================================= 2. type
TROWS = [
    # role, voice, desktop (size, lh, ls, sample), phone (size, lh, ls, sample), note
    ('H1 screen', 'HAND', (56, 1.22, 0, 'Say the thing.'), (34, 1.2, 0, 'Say the thing.'), 'one per screen · endings 86–96 / 44'),
    ('H2 card', 'HAND', (34, 1.2, 0, 'Let something out'), (26, 1.15, 0, 'Let something out'), 'sheet titles · 30–46'),
    ('row / item', 'HAND', (30, 1.2, 0, 'I need to talk'), (21, 1.2, 0, 'I need to talk'), 'home rows, names'),
    ('body', 'SERIF', (20, 1.55, 0, 'Just you. Nobody else needs to be online.'), (16.5, 1.5, 0, 'Just you. Nobody else needs to be'), 'Newsreader 300–400 · 18–22'),
    ('your words', 'SERIF', (19, 30 / 19, 0, "I don't even know where to start"), (16.5, 26 / 16.5, 0, "I don't even know where"), 'chat 19/30 · burn sheet 22/38'),
    ('label · fact', 'TYPE', (11, 1.5, .16, 'NO ACCOUNT · NOTHING KEPT'), (9.5, 1.5, .14, 'NO ACCOUNT · NOTHING KEPT'), 'caps · meta 10 / 9'),
    ('action', 'TYPE 700', (13, 1, .16, 'LET IT GO'), (12, 1, .15, 'LET IT GO'), 'chip · link 13 / 11, 400'),
    ('note', 'MARK', (23, 1.15, 0, 'you did good.'), (20, 1.15, 0, 'you did good.'), 'red ink / soft red · rot −1.5°'),
]
FONT = {'HAND': HAND, 'SERIF': SERIF, 'TYPE': TYPE, 'TYPE 700': TYPE + ';font-weight:700', 'MARK': MARK}
def tsample(voice, s, w):
    size, lh, ls, txt = s
    col = RED if voice == 'MARK' else INK
    st = f'{FONT[voice]};font-size:{size}px;line-height:{lh:.2f};letter-spacing:{ls}em;color:{col};white-space:nowrap;overflow:hidden;text-overflow:clip'
    lhs = f'{lh:.2f}'.rstrip('0').rstrip('.')
    return (f'<div style="width:{w}px;min-width:0"><div style="{st}">{txt}</div>'
            f'<div style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};margin-top:3px">{size:g}PX · LH {lhs} · LS {ls:g}EM</div></div>')
trows = ''.join(f'<div style="display:grid;grid-template-columns:118px 360px 220px;gap:18px;align-items:end;padding:7px 0;border-bottom:1px dashed {RULE}">'
                f'<div><div style="{HAND};font-size:19px;line-height:1.1;color:{INK}">{r}</div><div style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};margin-top:3px">{v} · {n.upper()}</div></div>'
                f'{tsample(v, d, 360)}{tsample(v, p, 220)}</div>' for r, v, d, p, n in TROWS)
voices = ''.join(f'<div style="flex:1;border-left:2px solid {RULE};padding-left:12px"><div style="{st};font-size:{sz}px;line-height:1.1;color:{c}">{smp}</div>'
                 f'<div style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};margin-top:4px">{nm}</div></div>'
                 for st, sz, c, smp, nm in [(HAND, 30, INK, 'Hand', "HAND · NOTHING YOU COULD DO · THE APP'S VOICE"),
                                            (SERIF, 26, INK, 'Serif', 'SERIF · NEWSREADER · YOUR WORDS, BODY'),
                                            (TYPE, 20, INK, 'TYPE', 'TYPE · COURIER PRIME CAPS · FACTS'),
                                            (MARK, 28, RED, 'mark', 'MARK · COVERED BY YOUR GRACE · CARE')])
type_sheet = sheet(f'''
{hhead('Four voices, one scale', 28)}
<div style="display:flex;gap:16px;margin-top:12px">{voices}</div>
<div style="display:grid;grid-template-columns:118px 360px 220px;gap:18px;margin-top:16px;padding-bottom:6px;border-bottom:1.5px solid {RULE}">
{lab('role')}{lab('desktop 1440')}{lab('phone 390')}</div>
{trows}
<div style="{SERIF};font-size:14px;line-height:1.5;color:{PENCIL};margin-top:14px">Hand never goes below 18px. Type never goes below 9px, and never below 9.5px for anything you must read to act. Lowercase hand notes are fine; type is always caps.</div>''',
    812, rot=.25, seed=9200, pad='28px 34px 30px')


# ================================================================= 3. layout
def desk_diagram():
    s = .22
    W_, H_ = 1440 * s, 900 * s
    m, hd, ft = 56 * s, 88 * s, 64 * s
    return f'''
<div style="position:relative;width:{W_:.0f}px;height:{H_:.0f}px;background:{BOARD_BG};box-shadow:inset 0 0 0 4px {FRAME},0 0 0 1px {SOOT}">
<div style="position:absolute;left:0;right:0;top:0;height:{hd:.0f}px;border-bottom:1px dashed {ASH};display:flex;align-items:center;padding-left:{m:.0f}px"></div>
<div style="position:absolute;left:0;top:{hd:.0f}px;bottom:{ft:.0f}px;width:{m:.0f}px;background:repeating-linear-gradient(45deg,rgba(240,160,143,.28) 0 2px,transparent 2px 6px)"></div>
<div style="position:absolute;right:0;top:{hd:.0f}px;bottom:{ft:.0f}px;width:{m:.0f}px;background:repeating-linear-gradient(45deg,rgba(240,160,143,.28) 0 2px,transparent 2px 6px)"></div>
<div style="position:absolute;left:{m:.0f}px;right:{m:.0f}px;top:{hd + 10:.0f}px;bottom:{ft + 10:.0f}px;border:1px dashed {SOOT};display:flex;align-items:center;justify-content:center;{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">CONTENT 1328</div>
<div style="position:absolute;left:{m:.0f}px;right:{m:.0f}px;bottom:0;height:{ft:.0f}px;border-top:1px dashed {ASH};display:flex;align-items:center"></div>
</div>'''

def phone_diagram():
    s = .24
    W_, H_ = 390 * s, 844 * s
    g, hd, ft = 22 * s, 64 * s, 44 * s
    hatch = 'background:repeating-linear-gradient(45deg,rgba(240,160,143,.3) 0 2px,transparent 2px 5px)'
    return f'''
<div style="position:relative;width:{W_:.0f}px;height:{H_:.0f}px;background:{BOARD_BG};box-shadow:inset 0 0 0 2.5px {FRAME},0 0 0 1px {SOOT}">
<div style="position:absolute;left:0;right:0;top:0;height:{hd:.0f}px;border-bottom:1px dashed {ASH}"></div>
<div style="position:absolute;left:0;top:{hd:.0f}px;bottom:{ft:.0f}px;width:{g:.0f}px;{hatch}"></div>
<div style="position:absolute;right:0;top:{hd:.0f}px;bottom:{ft:.0f}px;width:{g:.0f}px;{hatch}"></div>
<div style="position:absolute;left:{g:.0f}px;right:{g:.0f}px;top:{hd + 6:.0f}px;bottom:{ft + 6:.0f}px;border:1px dashed {SOOT};display:flex;align-items:center;justify-content:center;text-align:center;{TYPE};font-size:9px;letter-spacing:.1em;color:{ASH}">≤ 346</div>
<div style="position:absolute;left:{g:.0f}px;right:{g:.0f}px;bottom:0;height:{ft:.0f}px;border-top:1px dashed {ASH}"></div>
</div>'''

pad_demo = paper(f'''<div style="position:absolute;inset:28px;border:1px dashed {RED};opacity:.7"></div>
<div style="position:relative">{hhead('text lives in here', 22)}{serif('28px from every torn edge on desktop, 22px on phone. A torn top or bottom (torn=) tears ~4× deeper: add 10px on that side.', 13.5, PENCIL, 'margin-top:4px')}</div>''',
                 300, 178, rot=-.6, kind='hi', seed=9310, pad='28px 30px', torn='bottom')

SPACE = [(6, 'hairline gaps'), (10, 'label → value'), (14, 'inside a group'), (22, 'phone gutter, card stack'), (30, 'between groups'), (56, 'desktop margin, big breaks')]
space = ''.join(f'<div style="display:flex;align-items:center;gap:12px;height:22px"><span style="{TYPE};font-size:11px;font-weight:700;color:{CHALK};width:24px;text-align:right">{v}</span>'
                f'<span style="display:block;width:{v * 2.4:.0f}px;height:8px;background:{SOFT};opacity:.8"></span><span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};text-transform:uppercase">{t}</span></div>' for v, t in SPACE)
MAXW = [('reading note', '470–640'), ('chat sheet (pod)', '880'), ('side panel', '300'), ('toast / slip', '280–300'), ('phone paper', '346'), ('chip', 'len×10+84')]
maxw = ''.join(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px dashed {SOOT};{TYPE};font-size:10.5px;letter-spacing:.12em;text-transform:uppercase"><span style="color:{ASH}">{a}</span><span style="color:{CHALK}">{b}</span></div>' for a, b in MAXW)

layout_col = f'''
<div style="width:476px;display:flex;flex-direction:column;gap:26px">
<div style="display:flex;gap:22px;align-items:flex-start">
<div>{board_lab('desktop 1440 × 900')}{desk_diagram()}</div>
<div>{board_lab('phone 390 × 844')}{phone_diagram()}</div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:-6px">
<div style="{TYPE};font-size:10px;letter-spacing:.12em;color:{CHALK};line-height:1.8">SIDE MARGIN 56<br>HEADER 88 · TOPBAR()<br>FOOTER 64 · DASHED SOOT RULE<br>FRAME 14 · CONTENT 1328</div>
<div style="{TYPE};font-size:10px;letter-spacing:.12em;color:{CHALK};line-height:1.8">GUTTER 22 · MPAD<br>HEADER 64 · MTOPBAR()<br>FOOTER ~44 · MFOOTER()<br>FRAME 7 · PAPER ≤ 346</div></div>
<div style="display:flex;gap:18px;align-items:flex-start">{pad_demo}
<div style="padding-top:6px">{hnote('in a pod the footer gives way to a sticky composer.', ASH, 17)}{hnote('taller boards say (scrolls).', SOFT, 17, 'margin-top:12px')}</div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px">
<div>{board_lab('spacing steps')}{space}</div>
<div>{board_lab('max widths')}{maxw}</div></div>
</div>'''

s23 = f'''
<section>{sec('2 + 3', 'Type, then space', 'four voices · one scale per device · the 1440 / 390 grids')}
<div style="display:flex;justify-content:space-between;align-items:flex-start">{type_sheet}{layout_col}</div>
</section>'''


# ================================================================= 4. components
COLS = [('default', ''), ('hover', 'transform:rotate(-1deg) translateY(-2px)'), ('pressed', 'transform:rotate(0) translateY(1px) scale(.98)'),
        ('focus', f'outline:2px dashed {FOCUS};outline-offset:5px'), ('disabled', None), ('loading', None)]
def chip_cell(kind, col, extra, i):
    lbl = {'paper': 'let it go', 'ink': 'keep going', 'kraft': 'back home'}[kind]
    seed = 9400 + i
    if col == 'disabled':
        return chip(lbl, kind=kind, w=168, seed=seed, state='disabled')
    if col == 'loading':
        return chip({'paper': 'sealing', 'ink': 'sending', 'kraft': 'finding'}[kind], kind=kind, w=168, seed=seed, state='loading')
    return chip(lbl, kind=kind, w=168, seed=seed, extra=extra)
chip_head = ''.join(f'<div style="{TYPE};font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;color:{CHALK};text-align:center">{c}</div>' for c, _ in COLS)
chip_rows = ''
for ri, (kind, use) in enumerate([('paper', 'primary on the board'), ('ink', 'primary on paper'), ('kraft', 'secondary')]):
    cells = ''.join(f'<div style="display:flex;justify-content:center">{chip_cell(kind, c, e, ri * 10 + ci)}</div>' for ci, (c, e) in enumerate(COLS))
    chip_rows += (f'<div style="{HAND};font-size:22px;line-height:1.1;color:{CHALK}">{kind}<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};margin-top:4px">{use.upper()}</div></div>{cells}')
chips = f'''
<div style="display:grid;grid-template-columns:150px repeat(6,1fr);gap:26px 10px;align-items:center">
<div></div>{chip_head}{chip_rows}</div>
<div style="display:flex;gap:30px;align-items:flex-start;margin-top:26px">
<div style="flex:1;{TYPE};font-size:10px;letter-spacing:.12em;color:{ASH};line-height:1.9;text-transform:uppercase;border-top:1px dashed {SOOT};padding-top:10px">
chip(label, kind, w, state) · height 54 (phone 46) · type 700 13px .16em caps · torn edge deckle amp 1.6 step 12 · drop shadow .lift<br>
hover rotate(−1°) translateY(−2px) .2s ease · pressed rotate(0) translateY(1px) scale(.98) · focus 2px dashed, offset 5<br>
disabled opacity .38 + saturate(.4) + aria-disabled, always with a note saying why · loading label + 3 dots, 1.4s, stays tappable-looking but ignores taps</div>
<div style="width:300px;padding-top:6px">{inline_note("disabled? say why, right next to it: <br>“write something first”", 'soft', 20)}</div></div>'''

# links
links_sheet = sheet(f'''
{lab('text link · .ul')}
<div style="display:grid;grid-template-columns:auto 1fr;gap:14px 14px;align-items:center;margin-top:12px;white-space:nowrap">
{link('write another', color=INK)}{lab('default', size=9)}
<a href="#" class="ul" style="{TYPE};font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:{INK};background-size:100% 2px">write another</a>{lab('hover · .35s', size=9)}
<a href="#" class="ul" style="{TYPE};font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:{RED}">report · ends now</a>{lab('destructive', size=9)}
</div>
<div style="background:{NIGHT};margin:16px -6px 0;padding:14px 14px 12px;white-space:nowrap;display:grid;grid-template-columns:auto 1fr;gap:12px 10px;align-items:center">
{link('not now')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">ON THE BOARD</span>
<a href="#" class="ul" style="{TYPE};font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:{CRISIS};background-size:100% 2px">in crisis? →</a><span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">CRISIS · HOVER</span></div>
{spec('link(label, href, color, size) · type 13 .14em caps · line 2px red, grows 0 → 100% · secondary only: never the main action')}''',
    300, rot=-.8, seed=9500, pad='26px 28px 26px')

rows_sheet = sheet(f'''
{lab('row link · home · .row')}
<div style="margin-top:8px;border-top:1px dashed {RULE}">
{hrow('Leave it somewhere', 'ECHO · LETTER', 240)}
{hrow('I need to get this out', 'BURN', 300, hover=True, last=True)}</div>
<div style="display:flex;justify-content:space-between;margin-top:6px">{lab('default', size=9)}{lab('↑ hover: red scribble draws .45s, arrow nudges 4px', size=9)}</div>
{spec('hand 30 · feature in type 700 12 .18em pencil · row 64 tall · dashed rule between · the whole row is the target')}''',
    480, rot=.5, seed=9510, pad='26px 32px 26px')

fields_sheet = sheet(f'''
{lab('field(label, value, placeholder, error, helper)')}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:22px 30px;margin-top:14px">
<div>{field('email · optional', '', 'you@somewhere.com', w=210)}{spec('empty', size=9)}</div>
<div>{field('email · optional', 'otter@mail.com', '', w=210)}{spec('filled', size=9)}</div>
<div>{field('email · optional', 'otter@mail', '', error='add the part after the dot', w=210)}{spec('error · replaces helper', size=9)}</div>
<div>{field('email · optional', '', 'you@somewhere.com', helper='deleted once it sends', w=210)}{spec('helper', size=9)}</div>
</div>
{spec('label type 10 .16em · value serif 18 · line 1.5px rule → red on error · error in red ink, says how to fix it, never what you did wrong')}''',
    500, rot=-.4, seed=9520, pad='26px 32px 26px')

toggle_sheet = sheet(f'''
{lab('write / speak toggle')}
<div style="display:flex;flex-direction:column;gap:18px;margin-top:14px">
{''.join(f"""<div style="display:flex;gap:22px;align-items:center;{TYPE};font-size:12px;letter-spacing:.18em">
<span style="color:{INK if a else PENCIL};position:relative;padding-bottom:6px">WRITE<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{1 if a else 0}"></span></span>
<span style="color:{RULE}">/</span>
<span style="color:{PENCIL if a else INK};position:relative;padding-bottom:6px">SPEAK<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{0 if a else 1}"></span></span></div>""" for a in (True, False))}
</div>
{spec('type 12 .18em · on = ink + 2px red line · off = pencil · on the board on = chalk, off = ash, slash soot')}''',
    230, rot=.8, seed=9530, pad='26px 26px 24px')

comp_desk = f'''<div style="border-top:1.5px dashed {RULE};padding-top:14px;display:flex;align-items:center;justify-content:space-between;gap:16px">
<span style="{SERIF};font-style:italic;font-size:18px;color:{PENCIL};white-space:nowrap">say it however it comes out…<span class="blink" style="color:{RED};font-style:normal">|</span></span>
{chip('send ↗', kind='ink', seed=9541, w=110)}</div>'''
comp_typing = f'''<div style="border-top:1.5px dashed {RULE};padding-top:14px;display:flex;align-items:center;justify-content:space-between;gap:16px">
<span style="{SERIF};font-size:18px;color:{INK};white-space:nowrap">yeah. exactly that.<span class="blink" style="color:{RED}">|</span></span>
{chip('send ↗', kind='ink', seed=9542, w=110)}</div>'''
composer_sheet = sheet(f'''
{lab('composer · bottom of the chat sheet')}
<div style="margin-top:12px">{comp_desk}</div>{spec('empty: italic pencil placeholder, red caret blinks 1.1s', size=9)}
<div style="margin-top:12px">{comp_typing}</div>{spec('typing: serif 18–19 ink · enter sends · send is an ink chip', size=9)}
{spec('phone: its own paper strip, 60 tall, sticky above the keyboard, send chip 86 × 40 (raise to 44)', RED)}''',
    450, rot=-.3, seed=9540, pad='26px 30px 24px')

pod_sheet = sheet(f'''
{lab('pod actions · pod_btn')}
<div style="display:flex;flex-direction:column;gap:14px;margin-top:14px">
{pod_btn('ask for voice', MIC, 'ink', seed=561)}
{pod_btn('leave gently', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', FLAG, 'red')}</div>
{spec('240 × 50 · icon 16 · type 700 12.5 · ink = ask, kraft = leave, red text = report. report is one tap, no confirm')}''',
    300, rot=.6, seed=9550, pad='26px 30px 24px')

pill_col = f'''
<div style="width:250px">{board_lab('sound pill · sound.js')}
<div style="display:flex;flex-direction:column;gap:12px;align-items:flex-start">
<div style="display:flex;align-items:center;gap:12px">{pill('sound on')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">PLAYING</span></div>
<div style="display:flex;align-items:center;gap:12px">{pill('sound off', 'off')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">MUTED · M</span></div>
<div style="display:flex;align-items:center;gap:12px">{pill('music on', 'kw')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">WAITING SCREENS</span></div>
<div style="display:flex;align-items:center;gap:12px">{pill('replay with sound', 'wait')}</div>
<div style="display:flex;align-items:center;gap:12px">{pill('hear it', 'wait ph')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">PHONE</span></div>
<div style="display:flex;align-items:center;gap:12px">{pill('sound on', 'hov')}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">HOVER / FOCUS</span></div></div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.7;margin-top:12px;text-transform:uppercase">desk: right 48, bottom 76 · phone: footer, left 170 · only on boards that make sound</div>
{inline_note('the one rounded thing in the system. make it a torn slip?', 'soft', 18)}</div>'''

scraps_col = f'''
<div style="width:270px">{board_lab('let-it-go scraps · two sizes')}
<div style="display:flex;flex-direction:column;gap:12px">{mini_scrap('get it out', 'BURN', -1.5, 581)}{mini_scrap('leave it somewhere', 'ECHOES', 1.2, 582, 'kraft')}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.6">MINI 222 × 74 · HAND 20 · SIDE COLUMNS</div>
{scrap_link('hear it again later', 'TIME CAPSULE', -1, 573)}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.6">FULL 270 × 112 · HAND 24 · EMPTY + ASLEEP</div></div></div>'''

TOASTS = [dict(ev='', ic='door', msg='moss_byte left the pod.', sub="that's okay. stay, or go.", tone='paper', life=''),
          dict(ev='', ic='loop', msg='reconnecting…', sub='hold on, nothing is lost', tone='kraft', life='', spin=True),
          dict(ev='', ic='mic', msg="you're on voice.", sub='peer to peer · never recorded', tone='ink', life=''),
          dict(ev='', ic='flag', msg='reported. pod closed.', sub='you did the right thing.', tone='red', life='')]
TLAB = ['paper · it happened · 3–6s', 'kraft · in progress · until done', 'ink · live state · stays while true', 'red · care + safety · stays']
toasts_col = f'''
<div>{board_lab('toast / slip · toast(n) · 4 tones')}
<div style="display:grid;grid-template-columns:repeat(2,280px);gap:22px 26px">
{''.join(f'<div><div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{CHALK};margin-bottom:7px;text-transform:uppercase">{TLAB[i]}</div>{toast(n, 280, seed=9600 + i, rot=[-.6, .5, -.3, .6][i])}</div>' for i, n in enumerate(TOASTS))}
</div>
<div style="width:586px;{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.7;margin-top:14px;text-transform:uppercase">hand 19 + type 9.5 · 54 / 66 tall · icon always drawn · desktop bottom centre, phone under header · two at most · silent</div></div>'''

heard_sheet = sheet(f'''
{lab('heard · the only reaction')}
<div style="display:flex;flex-direction:column;gap:14px;margin-top:14px">
<div style="display:flex;align-items:center;justify-content:space-between">{heard_btn(False)}{lab('off', size=9)}</div>
<div style="display:flex;align-items:center;justify-content:space-between">{heard_btn(True)}{lab('on · aria-pressed', size=9)}</div></div>
<div style="position:relative;height:96px;margin-top:16px;border-top:1px dashed {RULE}">
<div style="{SERIF};font-style:italic;font-size:15px;color:{PENCIL};padding-top:12px;max-width:170px">an echo you listened to all the way through</div>
<span class="stamp" style="right:4px;top:30px;font-size:30px">HEARD</span></div>
{spec('mark 24–26 red · heart outline → filled · stamp: mark 30 red, 3px border, rot −12°, multiply, slams in .55s with a thud')}''',
    290, rot=-.6, seed=9650, pad='26px 28px 24px')

objects = f'''
<div>{board_lab('things on the board')}
<div style="display:flex;gap:38px;align-items:flex-start">
<div>{polaroid('moon', 150, 108, 'someone is still awake', rot=-2.5, seed=9701, u='dls1', capsize=19)}
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.6;margin-top:16px">POLAROID · PAPER HI · 14 PAD<br>HAND CAPTION 19–30 · TAPED TOP</div></div>
<div style="display:flex;flex-direction:column;gap:20px;padding-top:10px">
<div style="position:relative;width:130px;height:34px">{tape(0, 0, 120, 30, rot=-4, seed=9711)}</div>
<div style="position:relative;width:130px;height:34px">{tape(0, 0, 110, 28, rot=3, seed=9712, red=True)}</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.6">TAPE 96–120 × 26–30<br>±2–5° · ZIG-ZAG ENDS<br>RED TAPE = SAFETY SHEETS</div></div>
<div style="display:flex;flex-direction:column;gap:14px;padding-top:6px">
<div style="display:flex;gap:16px;align-items:center">{pin_svg(RED)}{pin_svg('#3A3A3D')}{pin_svg('#5D5D61', 6)}</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{ASH};line-height:1.6">PUSH PIN R 6–8<br>RED = YOU · GREY = OTHERS<br>SHADOW OFFSET 4, 7</div></div>
</div></div>'''

notes_sheet = sheet(f'''
{lab('margin notes · inline_note(text, tone)')}
<div style="display:flex;flex-direction:column;gap:12px;margin-top:14px">
{inline_note('add the part after the dot', 'red')}{spec('red · the one thing to fix', size=9)}
{inline_note('this stays on your device', 'pencil')}{spec('pencil · a quiet aside', size=9)}</div>
<div style="background:{NIGHT};margin:14px -6px 0;padding:12px 14px">{inline_note("quiet night? that's okay.", 'soft')}<div style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH};margin-top:6px">SOFT · ON THE BOARD ONLY</div></div>
{spec('mark 19 · rot −1.2° · one note per screen')}''',
    280, rot=.7, seed=9750, pad='26px 28px 24px')

rabbit_sheet = sheet(f'''
{lab('the rabbit · rabbit(w, color, mood)')}
<div style="display:flex;gap:22px;align-items:flex-end;margin-top:16px">
<div>{rabbit(84, INK, uid='dlsr1')}{spec('idle · blinks 5s', size=9)}</div>
<div>{rabbit(84, INK, mood='sleep', uid='dlsr2')}{spec('sleep · pods closed', size=9)}</div></div>
<div style="background:{NIGHT};margin:16px -6px 0;padding:12px 14px;display:flex;align-items:center;gap:14px">{rabbit(46, CHALK, uid='dlsr3', blink=False)}<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH};line-height:1.6">CHALK ON THE BOARD<br>34 IN HEADER · 26 PHONE</span></div>
{spec('optional in empty / error states · never in report or help screens')}''',
    290, rot=-.4, seed=9760, pad='26px 28px 24px')

s4 = f'''
<section>{sec('4', 'Components, every state', 'rendered live from the helpers · hover + pressed shown still, with their transforms applied')}
{board_lab('chip · the primary action · gen5.chip()')}
{chips}
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:44px">{links_sheet}{rows_sheet}{fields_sheet}</div>
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:44px">{toggle_sheet}{composer_sheet}{pod_sheet}{pill_col}</div>
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:44px">{scraps_col}{toasts_col}{heard_sheet}</div>
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:44px">{objects}{notes_sheet}{rabbit_sheet}</div>
</section>'''


# ================================================================= 5. patterns
def mini_board(inner, h=150):
    return f'<div style="position:relative;height:{h}px;background:{BOARD_BG};margin:12px -4px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:10px;box-shadow:inset 0 0 0 3px {FRAME}">{inner}</div>'
def mchip(t, kind='paper'):
    bg, fg = {'paper': (PAPERHI, INK), 'ink': (INK, PAPERHI), 'kraft': (KRAFT, INK)}[kind]
    return f'<span style="display:inline-block;background:{bg};color:{fg};{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;padding:7px 12px;text-transform:uppercase">{t}</span>'
def mlinkb(t, c=CHALK):
    return f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{c};border-bottom:1.5px solid {RED};padding-bottom:2px;text-transform:uppercase">{t}</span>'
def anat(items):
    return ''.join(f'<div style="display:grid;grid-template-columns:18px 1fr;gap:6px;padding:4px 0"><span style="{MARK};font-size:17px;line-height:1.1;color:{RED}">{i}</span>'
                   f'<span style="{SERIF};font-size:13.5px;line-height:1.4;color:{INK}">{t}</span></div>' for i, t in enumerate(items, 1))
PATTERNS = [
    ('empty state', mini_board(f'{rabbit(40, CHALK, mood="sleep", uid="dlsp1")}<div style="{HAND};font-size:19px;color:{CHALK}">The wall is quiet tonight.</div>{mchip("leave yours →")}'),
     ['what is true, in hand', 'one line on why it is fine', 'one next step (chip)', 'rabbit optional, asleep'], 'quiet is not broken. invite, don\'t apologise.'),
    ('error state', mini_board(f'<div style="background:{PAPERHI};padding:10px 14px;transform:rotate(-1deg);text-align:left"><div style="{HAND};font-size:18px;color:{INK}">Lost the signal.</div><div style="{SERIF};font-size:11.5px;color:{PENCIL}">nothing you wrote is lost.</div><div style="{MARK};font-size:14px;color:{RED};margin-top:2px">check your wifi, then</div></div>{mchip("try again", "ink")}'),
     ['what happened, plainly', 'what is safe (nothing lost)', 'red ink: the one thing to fix', 'one retry + help reachable'], 'never blame. no codes, no "!", no red screen.'),
    ('loading state', mini_board(f'<div style="{HAND};font-size:18px;color:{CHALK}">finding someone who\'ll listen…</div><div style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{ASH}">USUALLY UNDER A MINUTE</div>{mlinkb("stop looking")}'),
     ['what is happening, with …', 'how long, as a fact', 'a calm loop (thread, dots)', 'a way out, always'], 'loops ≥ 1.1s, soft. no spinners on paper.'),
    ('ending moment', mini_board(f'<div style="{HAND};font-size:26px;color:{PAPERHI}">It\'s gone.</div><div style="{MARK};font-size:15px;color:{SOFT};transform:rotate(-2deg)">you did good.</div><div style="display:flex;gap:12px;align-items:center">{mchip("write another")}{mlinkb("back home")}</div>'),
     ['the moment (burn, seal, pin)', 'hand headline, writes on', 'one kind note', 'two ways on: chip + link'], 'endings get time + a sound cue. then get out of the way.'),
    ('destructive · report', mini_board(f'<div style="display:flex;align-items:center;gap:6px;{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;color:{SOFT}">⚑ REPORT · ENDS NOW</div><div style="background:{PAPERHI};border-left:3px solid {RED};padding:7px 12px"><div style="{HAND};font-size:15px;color:{INK}">reported. pod closed.</div><div style="{TYPE};font-size:8px;letter-spacing:.12em;color:{PENCIL}">YOU DID THE RIGHT THING.</div></div>{mlinkb("need help now?")}'),
     ['red-ink text link, not a chip', 'one tap, no questions', 'red slip confirms, stays', 'help one tap away'], 'the other person only sees it closed.'),
]
pcards = ''.join(sheet(f'''{lab(t)}{mb}<div style="margin-top:10px">{anat(a)}</div>
<div style="{MARK};font-size:18px;line-height:1.15;color:{RED};margin-top:8px;transform:rotate(-1deg)">{r}</div>''', 252, rot=[-.8, .6, -.4, .9, -.6][i], seed=9800 + i, pad='22px 22px 22px', red=(i == 4))
                 for i, (t, mb, a, r) in enumerate(PATTERNS))
s5 = f'''
<section>{sec('5', 'Patterns', 'one note · one next step · rabbit optional · never blame')}
<div style="display:flex;justify-content:space-between;align-items:flex-start">{pcards}</div>
</section>'''


# ================================================================= 6. motion
MOTION = [
    ('write', '.write · clip-path wipe', '--d 1.6s', 'cubic-bezier(.5,.1,.3,1)', '--w .2s', 'every hand headline'),
    ('rise', '.rise · y 10 → 0 + fade', '1.1s', 'cubic-bezier(.2,.7,.2,1)', '--w .3s', 'copy + chips after it'),
    ('fadein', '.fadein', '1.4s', 'ease', '--w .3s', 'rabbit, quiet extras'),
    ('draw', '.draw · dashoffset', '--d 1.2s', 'ease-out', '--w .4s', 'underline, circle, arrow'),
    ('drop', '.drop · y −70, −10°, 1.08', '.9s', 'cubic-bezier(.3,1.4,.5,1)', '—', 'note pinned to wall'),
    ('slap', '.slap · scale 1.6 → 1', '.35s', 'cubic-bezier(.2,1.6,.4,1)', '—', 'tape pressed down'),
    ('stamp', '.stamp · 1.9 → 1, −12°', '.55s', 'cubic-bezier(.2,1.6,.4,1)', '--sw 1.2s', 'HEARD'),
    ('burn', 'mask + char travel up', '4.4s', 'cubic-bezier(.42,.02,.38,1)', 'tape +3.5s', 'burn, then bloom 3.2s'),
    ('envelope', 'letterin → flap → seal', '1.5 / .9 / .6s', '(.55,.05,.35,1) (.45,.05,.3,1) (.2,1.6,.4,1)', '.35 / 2 / 2.95s', 'capsule sealed'),
    ('unfold', '.unfold · rotateX −70°', '1.6s', 'cubic-bezier(.2,.8,.2,1)', '.3s', 'capsule opens'),
    ('slidein', 'toast · y 14 → 0', '.7s', 'cubic-bezier(.2,.8,.2,1)', '--w', 'toasts; chat lines .6s, +.12s each'),
    ('hover', 'chip · .ul · row', '.2 / .35 / .45s', 'ease · ease · (.5,.1,.2,1)', '—', 'all hovers'),
    ('loops', 'breathe · eyes · dots · live', '7 / 5 / 1.4 / 2.4s', 'ease-in-out', '—', 'calm, never under 1.1s'),
]
mrows = ''.join(f'<div style="display:grid;grid-template-columns:74px 150px 84px 1fr 70px;gap:10px;padding:6px 0;border-bottom:1px dashed {RULE};align-items:baseline">'
                f'<span style="{HAND};font-size:18px;line-height:1.1;color:{INK}">{a}</span>'
                f'<span style="{TYPE};font-size:9.5px;letter-spacing:.06em;color:{INK}">{b}</span>'
                f'<span style="{TYPE};font-weight:700;font-size:10px;color:{INK}">{c}</span>'
                f'<span style="{TYPE};font-size:9.5px;color:{PENCIL}">{d}<br><span style="color:{PENCIL};opacity:.9">{f}</span></span>'
                f'<span style="{TYPE};font-size:9.5px;color:{PENCIL};text-align:right">{e}</span></div>' for a, b, c, d, e, f in MOTION)
motion_sheet = sheet(f'''
{hhead('Motion tokens', 28)}
<div style="display:grid;grid-template-columns:74px 150px 84px 1fr 70px;gap:10px;margin-top:10px;padding-bottom:4px;border-bottom:1.5px solid {RULE}">{lab('token', size=9)}{lab('class · what moves', size=9)}{lab('duration', size=9)}{lab('easing · used for', size=9)}<div style="text-align:right">{lab('delay', size=9)}</div></div>
{mrows}
<div style="margin-top:14px;padding:12px 14px;background:rgba(184,53,42,.07);border-left:3px solid {RED}">
<div style="{HAND};font-size:20px;color:{INK}">reduced motion</div>
<div style="{SERIF};font-size:14px;line-height:1.5;color:{INK}">@media (prefers-reduced-motion: reduce): every animation .01s, one iteration, no transitions, .write shows whole. Endings still land on their final frame, and their sound still plays once.</div></div>''',
    644, rot=-.3, seed=9900, pad='28px 30px 28px')


# ================================================================= 7. sound
SOUNDS = [
    ('chalk', 'hand headlines: story (all), "It\'s gone", "Sealed", "it arrived", "up there now"', 'chalk on a board', '.19–.24'),
    ('burn', 'burn: the sheet catches (match, then fire)', 'strike, soft roar, crackle', '.42 · loudest'),
    ('flutter', 'burn: the tape falls away', 'a scrap drifting', '.05'),
    ('slide · fold · wax', 'capsule sealed: letter in, flap, seal', 'paper, crease, low thump + 2 notes', '.11 / .26 / .38'),
    ('unfold', 'capsule opens', 'a sheet unfolding', '.05–.26'),
    ('rip · tapepress', 'echo pinned: tape off the roll, pressed', 'sticky crackle, a press', '.2 / .32'),
    ('stamp', 'echo thread: HEARD lands', 'rubber-stamp thud', '.28'),
    ('heardchord', 'pod ended: "You were heard tonight."', 'soft strum + chalk', '.14'),
    ('pluck', 'matching + requeue: each knot on the thread', 'one string per listener', '.13 (.07 under music)'),
    ('music · story', 'story, age gate', 'fingerpicked guitar in D, pad, bells, 72 bpm', 'bed .5 · 5s in'),
    ('music · wait', 'matching, requeue', 'same, sparser, no bells', 'bed .4'),
]
srows = ''.join(f'<div style="display:grid;grid-template-columns:104px 1fr 150px 74px;gap:10px;padding:6px 0;border-bottom:1px dashed {RULE};align-items:baseline">'
                f'<span style="{HAND};font-size:17px;line-height:1.1;color:{INK}">{a}</span>'
                f'<span style="{SERIF};font-size:13.5px;line-height:1.35;color:{INK}">{b}</span>'
                f'<span style="{SERIF};font-style:italic;font-size:13px;line-height:1.35;color:{PENCIL}">{c}</span>'
                f'<span style="{TYPE};font-size:9.5px;color:{INK};text-align:right">{d}</span></div>' for a, b, c, d in SOUNDS)
sound_sheet = sheet(f'''
{hhead('Sound map', 28)}
<div style="display:grid;grid-template-columns:104px 1fr 150px 74px;gap:10px;margin-top:10px;padding-bottom:4px;border-bottom:1.5px solid {RULE}">{lab('cue', size=9)}{lab('where', size=9)}{lab('feel', size=9)}<div style="text-align:right">{lab('peak gain', size=9)}</div></div>
{srows}
<div style="{TYPE};font-size:9.5px;letter-spacing:.1em;color:{PENCIL};margin-top:8px;line-height:1.6">ALL SYNTHESISED, NOTHING FETCHED · SFX BUS .62 · ROOM REVERB · COMPRESSOR −20DB 3:1 · DEFINED BUT UNMAPPED: PIN, STRUM</div>
<div style="margin-top:12px;border-top:1px dashed {RULE}">{bullets([
    'Nothing plays before the first tap or key on the page.',
    'An ending missed before that tap offers <b>replay with sound</b> for 30s.',
    'One pill mutes everything; <b>M</b> does too (not while typing). Remembered on this device.',
    'Music only on story, age and waiting screens. Never where voice notes or calls play. Fades 1.5s when you leave.',
    'Sound is never the only signal: every cue rides an animation already on screen. Toasts stay silent.'], size=14)}</div>''',
    644, rot=.3, seed=9950, pad='28px 30px 28px')

s67 = f'''
<section>{sec('6 + 7', 'Motion, then sound', 'everything slow and soft · endings get a moment · durations as in code')}
<div style="display:flex;justify-content:space-between;align-items:flex-start">{motion_sheet}{sound_sheet}</div>
</section>'''


# ================================================================= 8. accessibility
focus_demo = (f'<div style="display:flex;gap:26px;align-items:center;margin-top:10px">'
              f'<a href="#" class="ul" style="{TYPE};font-size:12px;letter-spacing:.14em;color:{INK};outline:2px dashed {INK};outline-offset:5px">write another</a>'
              f'<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL}">ON PAPER: INK</span></div>'
              f'<div style="background:{NIGHT};margin-top:14px;padding:16px 16px;display:flex;gap:26px;align-items:center">'
              f'<a href="#" class="ul" style="{TYPE};font-size:12px;letter-spacing:.14em;color:{CHALK};outline:2px dashed {FOCUS};outline-offset:5px">not now</a>'
              f'<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{ASH}">BOARD: GLOW</span></div>')
tap_demo = (f'<div style="position:relative;display:inline-block;margin-top:14px;padding:13px 6px;outline:1.5px dashed {RED};outline-offset:0">'
            f'<a href="#" class="ul" style="{TYPE};font-size:11px;letter-spacing:.14em;color:{INK}">NOT NOW</a></div>'
            f'<div style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};margin-top:8px">TEXT 17 TALL · HIT AREA PADDED TO 44</div>')
A11Y = [
    ('focus ring', f'2px dashed, offset 5px, on :focus-visible only. Ink on paper, glow on the board. Never outline:none without a replacement.{focus_demo}'),
    ('tap size', f'Everything you tap is at least 44 × 44 on phone. Chips are 46–54. Text links and heard get padding, not bigger type.{tap_demo}'),
    ('contrast', 'Body ≥ 4.5:1, big hand (24px+) and UI marks ≥ 3:1. Pencil only on paper and paper hi, never on kraft. Small red only on paper; on the board use soft red.'),
    ('reduced motion', 'Honour prefers-reduced-motion everywhere, including JS-timed moments (burn, seal, pin): jump to the last frame. Loops stop.'),
    ('sound', 'Never the only signal. Every cue has a visible twin; captions are not needed because nothing spoken is synthesised. Mute is one tap or M.'),
    ('say it in words', 'Icons always with a word or aria-label. Disabled = aria-disabled + a note saying why. Toasts are role=status. Heard + the pill use aria-pressed.'),
]
a11y_cards = ''.join(f'<div style="padding:12px 0;border-bottom:1px dashed {RULE}"><div style="display:flex;gap:10px;align-items:baseline"><span style="{MARK};font-size:20px;color:{RED}">{i}</span>{hhead(t, 22)}</div>'
                     f'<div style="{SERIF};font-size:14px;line-height:1.45;color:{INK};margin-top:2px">{b}</div></div>' for i, (t, b) in enumerate(A11Y, 1))
a11y_sheet = sheet(f'''
{hhead('Accessibility, the non-negotiables', 28)}
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0 30px;margin-top:6px">{a11y_cards}</div>''', 880, rot=-.2, seed=9990, pad='28px 34px 26px')

GAPS = ['chips come in 54, 50, 46, 44 and 40 tall', 'four link helpers, four sizes (10.5–13)', 'type labels in 10 sizes, 8.5px on phone',
        'two soft reds: #F0A08F and #E07A6E', 'focus ring invisible on paper', 'pencil on kraft fails AA',
        '.dots, breathe, settle, drop mean different things in different files', 'the sound pill is the only rounded control']
gaps_sheet = sheet(f'''
{t_mark('known gaps, to fix', 26)}
<div style="margin-top:8px;border-top:1px dashed {RULE}">{bullets(GAPS, size=14.5)}</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.1em;color:{PENCIL};margin-top:10px;line-height:1.6">FILES + FUNCTIONS IN THE HANDOFF NOTE</div>''',
    410, kind='', rot=1, seed=9995, pad='26px 30px 24px', red=True)

s8 = f'''
<section>{sec('8', 'Accessibility', 'for everyone at 2am: tired eyes, one thumb, sound off')}
<div style="display:flex;justify-content:space-between;align-items:flex-start">{a11y_sheet}{gaps_sheet}</div>
</section>'''


# ================================================================= page
DLS_CSS = NOTICE_CSS + f"""
.ntp{{display:inline-flex;align-items:center;gap:8px;padding:7px 13px 7px 11px;border:1px solid rgba(233,233,231,.18);background:rgba(13,13,14,.72);color:#B9B9B6;
font-family:"Courier Prime",monospace;font-weight:700;font-size:10.5px;letter-spacing:.16em;text-transform:uppercase;border-radius:999px;white-space:nowrap}}
.ntp .x{{display:none}}.ntp.off{{color:#7E7E83}}.ntp.off .x{{display:block}}.ntp.off .w1,.ntp.off .w2{{display:none}}
.ntp.wait,.ntp.kw{{color:#C9C9C6}}.ntp.wait .w1,.ntp.wait .w2{{animation:ntw 2.4s ease-in-out infinite}}.ntp.wait .w2{{animation-delay:.3s}}
@keyframes ntw{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}
.ntp.hov{{border-color:rgba(233,233,231,.45);color:#E9E9E7}}
.ntp.ph{{font-size:8.5px;letter-spacing:.1em;padding:5px 10px 5px 8px;gap:6px}}
.stamp{{position:absolute;{MARK};color:{RED};border:3px solid {RED};border-radius:6px;padding:2px 12px 0;font-size:30px;letter-spacing:.06em;transform:rotate(-12deg);
mix-blend-mode:multiply;opacity:.85;-webkit-mask-image:{NOISE_LIGHT};mask-image:{NOISE_LIGHT};animation:stamp .55s cubic-bezier(.2,1.6,.4,1) 1.2s both;pointer-events:none;z-index:6}}
@keyframes stamp{{0%{{opacity:0;transform:rotate(-12deg) scale(1.9)}}60%{{opacity:.9;transform:rotate(-12deg) scale(.94)}}100%{{opacity:.85;transform:rotate(-12deg) scale(1)}}}}
.heard{{display:inline-flex;align-items:center;gap:8px;{MARK};color:{RED}}}
"""

body = f'''
{atmos(w=1440, h=H)}
{topbar(crumb='dls')}
<main style="position:relative;z-index:10;flex-grow:1;padding:18px 56px 56px;display:flex;flex-direction:column;gap:60px">
{intro}
{s1}
{s23}
{s4}
{s5}
{s67}
{s8}
</main>
{footer()}'''

page('V5DLS', 'DLS — components, states, rules', body, h=H, css=DLS_CSS)
json.dump([{"file": "V5DLS.dc.html", "title": "DLS — components, states, rules", "w": 1440, "h": H, "row": "dls"}],
          open('manifest_dls.json', 'w'), indent=1)
print('dls ok', H)
