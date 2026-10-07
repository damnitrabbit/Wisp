"""N0TRACE V5 — the live pieces of ECHOES (wall cards, reply slips, tallies) as HTML templates for the site.

The wall and the reply list hold real notes, so the site can't use the screen's fixed sample cards. This writes the
same markup the generators draw (echo_note / mnote in v5_leave.py + v5m_burnecho.py, the slips in v5x_echo.py /
v5e_leave.py) with {{tokens}} where live values go and <sc-if value="{{x}}"> for optional bits. The site fills them in
(apps/web/app/echoes/ui.js).

  cd design/v5 && python3.13 v5x_echo_parts.py      # writes apps/web/app/echoes/parts.gen.js
"""
import io, os, json, contextlib
from gen5 import *
from v5x_echo import wave, play_btn, heart, letter_note, dogear, unsent_tag, ruled
with contextlib.redirect_stdout(io.StringIO()):
    from v5e_leave import tally

OUTJS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'apps', 'web', 'app', 'echoes', 'parts.gen.js')
H = '{{h}}'
CLAMP = 'display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:{{lines}};overflow:hidden;white-space:pre-wrap;overflow-wrap:anywhere'

def sized(html, h):
    """paper(): height -> {{h}} (the deckle is relative, so any height keeps the torn edge)."""
    return html.replace(f'height:{h}px', 'height:{{h}}px', 1)

# ---------------------------------------------------------------- desktop wall (V5Echoes): 8 spots per block
D_SPOTS = [  # left, top, w, h, rot, seed, paper kind   (the eight spots of the designed wall)
    (0, 30, 330, 230, -2.5, 401, 'hi'), (360, 0, 280, 190, 2, 402, ''), (664, 34, 336, 262, -1.2, 403, ''),
    (1014, 0, 316, 214, 3, 404, 'hi'), (40, 290, 300, 190, 1.8, 405, ''), (380, 240, 290, 190, -2.8, 406, 'kraft'),
    (700, 326, 304, 226, 2.4, 407, ''), (1030, 260, 280, 190, -1.6, 408, ''),
]
D_BLOCK = 590  # one block of eight spots, then the pattern repeats further down the board

def d_card(spot, typ, size=19):
    left, top, w, h, rot, seed, kind = spot
    stamp = '<sc-if value="{{isHeard}}"><span class="stamp" style="right:42px;bottom:76px">HEARD</span></sc-if>'
    tp = tape(w / 2 - 50, -13, 100, 26, rot=random.Random(seed).uniform(-8, 8), seed=seed)
    heard_el = f'<span class="heard">{heart(fill="{{heartFill}}")}heard · {{{{heardCount}}}}</span>'
    fades = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">{{{{fades}}}}</span>'
    pos = f'position:absolute;left:{left}px;top:{{{{top}}}}px;{{{{fadeStyle}}}}transform:rotate({rot}deg)'
    if typ == 'letter':
        foot = (f'<div style="position:absolute;left:28px;right:26px;bottom:20px;display:flex;justify-content:space-between;align-items:center">'
                f'{fades}{heard_el}</div>{stamp}')
        body = letter_note('{{to}}', '<span style="' + CLAMP + '">{{text}}</span>', w, h, seed=seed, size=size, foot=foot, tapes=tp, lh=28)
        return f'<a href="{{{{href}}}}" class="note" aria-label="An unsent letter to {{{{to}}}}" style="{pos}">{body}</a>'
    if typ == 'voice':
        inner = (f'<div style="{HAND};font-size:{25 if w >= 310 else 22}px;line-height:1.2;color:{INK};white-space:nowrap">{{{{title}}}}</div>'
                 f'<div style="display:flex;align-items:center;gap:12px;margin-top:12px">{play_btn(42, f"vw{seed}")}'
                 f'{wave(w - 56 - 54, 34, seed, f"vww{seed}", 0, head=False, sw=1.7)}</div>'
                 f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{INK};margin-top:10px">VOICE · {{{{dur}}}}</div>')
    else:
        inner = f'<div style="{SERIF};font-size:{size}px;line-height:1.5;color:{INK};{CLAMP}">{{{{text}}}}</div>'
    rep = (f'<sc-if value="{{{{replies}}}}"><span style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};white-space:nowrap">{{{{replies}}}}</span></sc-if>')
    inner += (f'<div style="position:absolute;left:28px;right:26px;bottom:20px;display:flex;justify-content:space-between;align-items:center">'
              f'{fades}<span style="display:flex;align-items:center;gap:14px">{rep}{heard_el}</span></div>{stamp}')
    return f'<a href="{{{{href}}}}" class="note" style="{pos}">{paper(inner, w, h, kind=kind, seed=seed, pad="26px 28px", tapes=tp)}</a>'

def d_lines(spot, typ, size=19):
    """How many lines of words fit in a spot above its footer."""
    h = spot[3]
    if typ == 'letter':
        return max(1, int((h - 26 - 30 - 34 - 56) / 28))
    return max(1, int((h - 26 - 56) / (size * 1.5)))

# ---------------------------------------------------------------- phone wall (V5MEchoes): rows of one or two
PINK = '#F0A08F'
M_FULL = [dict(w=318, rot=1.2, seed=604, kind='hi'), dict(w=330, rot=-1.4, seed=601, kind='hi'), dict(w=324, rot=-.9, seed=607, kind=''),
          dict(w=316, rot=1.3, seed=609, kind='')]
M_HALF = [dict(w=158, rot=2.2, seed=602, kind=''), dict(w=162, rot=-1.8, seed=603, kind='kraft'),
          dict(w=160, rot=-2.4, seed=605, kind=''), dict(w=160, rot=1.6, seed=606, kind='hi'),
          dict(w=162, rot=1.9, seed=608, kind='kraft'), dict(w=158, rot=-2.2, seed=610, kind='')]

def m_card(v, typ):
    w, rot, seed, kind = v['w'], v['rot'], v['seed'], v['kind']
    h = 180  # sized later
    half = w < 200
    size = 15 if half else 16.5
    if typ == 'voice':
        ww = w - (92 if not half else 40)
        body = (f'<div style="{HAND};font-size:{16 if half else 22}px;color:{INK};white-space:nowrap">{{{{title}}}}</div>'
                f'<div style="display:flex;align-items:center;gap:10px;margin-top:10px">{"" if half else play_btn(38, f"pw{seed}")}'
                f'{wave(ww, 32, seed, f"ww{seed}", 0, head=False, sw=1.6)}</div>'
                f'<div style="display:flex;align-items:center;gap:8px;margin-top:8px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{INK}">{"▶ " if half else ""}VOICE · {{{{dur}}}}</div>')
    else:
        body = f'<div style="{SERIF};font-size:{size}px;line-height:1.45;color:{INK};{CLAMP}">{{{{text}}}}</div>'
    rep = '' if half else f'<sc-if value="{{{{replies}}}}"><span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">{{{{replies}}}}</span></sc-if>'
    foot = (f'<div style="position:absolute;left:{16 if half else 20}px;right:{14 if half else 18}px;bottom:13px;display:flex;justify-content:space-between;align-items:center;gap:8px">'
            f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">{{{{fades}}}}</span>'
            f'<span style="display:flex;align-items:center;gap:12px">{rep}<span class="heard" style="font-size:18px;gap:5px">{heart(size=15, fill="{{heartFill}}")}{"" if half else "heard · "}{{{{heardCount}}}}</span></span></div>')
    st = '<sc-if value="{{isHeard}}"><span class="stamp" style="right:12px;top:{{stampTop}}px;font-size:19px;border-width:2px;padding:1px 8px 0;--sw:1.4s">HEARD</span></sc-if>'
    tp = tape(w / 2 - 38 + random.Random(seed).uniform(-14, 14), -11, 76, 22, rot=random.Random(seed).uniform(-8, 8), seed=seed)
    pos = f'position:relative;display:block;{{{{fadeStyle}}}}transform:rotate({rot}deg);margin-left:{{{{dx}}}}px;margin-top:{{{{dy}}}}px'
    if typ == 'letter':
        out = letter_note('{{to}}', '<span style="' + CLAMP + '">{{text}}</span>', w, h, seed=seed, size=size, pad=(18, 20), hdr=21, foot=foot + st, tapes=tp, lh=24, ear=22)
        return f'<a href="{{{{href}}}}" class="note" aria-label="An unsent letter to {{{{to}}}}" style="{pos}">{sized(out, h)}</a>'
    pad = '18px 16px' if half else '20px 20px'
    return f'<a href="{{{{href}}}}" class="note" style="{pos}">{sized(paper(body + foot + st, w, h, kind=kind, seed=seed, pad=pad, tapes=tp), h)}</a>'

# ---------------------------------------------------------------- reply slips (thread, yours)
D_SLIP = [dict(rot=-.8, off=0, tx=200, trot=-4), dict(rot=.9, off=34, tx=330, trot=3), dict(rot=-.5, off=10, tx=120, trot=-2)]
M_SLIP = [dict(rot=-.8, off=0, tx=180, trot=-4), dict(rot=.9, off=16, tx=40, trot=3), dict(rot=-.5, off=6, tx=120, trot=-2)]
SLIP_PAPER = [('hi', 511), ('', 512), ('kraft', 513)]

def slip(i, typ, phone=False):
    v = (M_SLIP if phone else D_SLIP)[i]
    pk, seed = SLIP_PAPER[i]
    w, h = (324, 112) if phone else (560, 132)
    if typ == 'text':
        body = (f'<div style="{SERIF};font-size:{16.5 if phone else 19}px;line-height:{1.45 if phone else 1.5};color:{INK};margin-top:{6 if phone else 8}px;'
                f'white-space:pre-wrap;overflow-wrap:anywhere">{{{{text}}}}</div>')
    else:
        pw = 196 if phone else 300
        body = (f'<div style="display:flex;align-items:center;gap:{12 if phone else 16}px;margin-top:{8 if phone else 10}px">'
                f'<button type="button" class="pbtn" data-act="play" aria-label="{{{{playLabel}}}}">{play_btn(36 if phone else 42, f"{"m" if phone else ""}rs{i}", True)}</button>'
                f'{wave(pw, 32 if phone else 40, seed, f"{"m" if phone else ""}rw{i}", 0, main=True, head=False, sw=1.6 if phone else 1.8)}'
                f'<span style="{TYPE};font-size:{10 if phone else 11}px;letter-spacing:.1em;color:{INK}">{{{{dur}}}}</span></div>')
    fs, nfs, ls = (9.5, 11, '.04em') if phone else (10.5, 12, '.06em')
    own = (f'<sc-if value="{{{{canRemove}}}}"><button type="button" data-act="remove" class="ul" style="{TYPE};font-size:{fs}px;letter-spacing:.14em;color:{RED};margin-left:12px">REMOVE</button></sc-if>'
           f'<sc-if value="{{{{canReport}}}}"><button type="button" data-act="report" class="ul" style="{TYPE};font-size:{fs}px;letter-spacing:.14em;color:{PENCIL};margin-left:12px">{{{{reportLabel}}}}</button></sc-if>')
    inner = (f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:{fs}px;letter-spacing:{".14em" if phone else ".16em"};color:{PENCIL}">'
             f'<span style="{"" if phone else "text-transform:lowercase;"}letter-spacing:{ls};font-size:{nfs}px">{{{{name}}}}</span><span>{{{{when}}}}{own}</span></div>{body}')
    tp = tape(v['tx'], -10 if phone else -11, 70 if phone else 80, 20 if phone else 22, rot=v['trot'], seed=seed)
    sheet = sized(paper(inner, w, h, kind=pk, seed=seed + (30 if phone else 0), pad='16px 20px' if phone else '20px 26px', tapes=tp), h)
    return (f'<div class="slip {{{{cls}}}}" style="--dur:{{{{secs}}}}s;margin-left:{v["off"]}px;transform:rotate({v["rot"]}deg);flex-shrink:0">{sheet}</div>')

T = {
    'dWall': {f'{i}{t}': d_card(s, t) for i, s in enumerate(D_SPOTS) for t in ('text', 'voice', 'letter')},
    'dLines': {f'{i}{t}': d_lines(s, t) for i, s in enumerate(D_SPOTS) for t in ('text', 'letter')},
    'dSpots': [{'top': s[1], 'h': s[3]} for s in D_SPOTS],
    'dBlock': D_BLOCK,
    'mFull': [{t: m_card(v, t) for t in ('text', 'voice', 'letter')} for v in M_FULL],
    'mHalf': [{t: m_card(v, t) for t in ('text', 'voice')} for v in M_HALF],
    'mFullW': [v['w'] for v in M_FULL], 'mHalfW': [v['w'] for v in M_HALF],
    'dSlip': [{t: slip(i, t) for t in ('text', 'voice')} for i in range(3)],
    'mSlip': [{t: slip(i, t, True) for t in ('text', 'voice')} for i in range(3)],
    'dTally': [tally(n, 24, color=PENCIL, seed=7) for n in range(0, 26)],
    'mTally': [tally(n, 20, color=PENCIL, seed=7) for n in range(0, 26)],
}
src = '// generated by design/v5/v5x_echo_parts.py — edit the generator, not this file\nexport default ' + json.dumps(T, ensure_ascii=False) + ';\n'
open(OUTJS, 'w').write(src)
print('echo parts ok', len(src))
