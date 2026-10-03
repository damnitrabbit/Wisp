"""N0TRACE V5 — Unsent letters (desktop + phone): write one (E05), it's out of you now (E06), one opened (E07)."""
from gen5 import *
import gen5, json
from v5x_echo import (ECHO_CSS, KIND_CSS, THREAD_SCRIPT, THREAD_PROPS, write_board, mwrite_board, letter_note, heard_btn, stamp,
                      ico_letter, step_label, LETTER_TXT, unsent_tag, dogear, ruled)

# sound: same cues as the echo pin (tape rip + press, chalk on the headline) and the HEARD stamp
_PIN_U = {'cls': {'drop': 'rip', 'slap': 'tapepress'}, 'chalk': ['out of you'], 'replay': 1}
for _n in ('V5UnsentPinned', 'V5MUnsentPinned'):
    gen5.SOUND.setdefault(_n, _PIN_U)
for _n in ('V5UnsentOpen', 'V5MUnsentOpen'):
    gen5.SOUND.setdefault(_n, {'cls': {'stamp': 'stamp'}})

LETTER_LONG = LETTER_TXT + " I still have your last voicemail. I play it when the house is too quiet."

# =====================================================================
# phone write board (shared by V5MEchoWrite + V5MUnsentWrite), on the phone frame:
# kind cards stay in the content, the compose paper is the main sheet, "pin it up / not now" is the dock
# =====================================================================
from v5x_echo import WRITE_COPY, kind_cards, toggle, _rec, ECHO_TXT, LETTER_TXT as _LT, ruled as _ruled

def ctape(w, h, rot, seed, top=-13, red=False):
    """A strip of tape centred on a sheet whatever its width."""
    return tape(0, top, w, h, rot=rot, red=red, seed=seed).replace('left:0px', f'left:calc(50% - {w / 2:.0f}px)', 1)

def fullw(html):
    """Fixed-width phone papers (346) stretch to the column instead."""
    return html.replace('width:346px;max-width:100%', 'width:100%')

def mcompose(sel='echo'):
    """Phone compose paper as the screen's main sheet: grows to the dock, foot pinned to its bottom edge."""
    P, fs, lh = 22, 18.5, 30
    count = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL};padding-bottom:6px">{58 if sel == "echo" else 74} / 400</span>'
    top = f'<div style="display:flex;justify-content:space-between;align-items:center">{toggle(11, 16)}{count}</div>'
    rec = _rec(250, 'mcw', 22, phone=True).replace('width:250px', 'width:100%;max-width:250px')
    if sel == 'echo':
        words = f'<div style="flex:1 1 auto;{SERIF};font-size:{fs}px;line-height:1.6;color:{INK};margin-top:16px">{ECHO_TXT}<span class="blink" style="color:{RED}">|</span></div>'
        foot, extra, ear, crease, rot = 'NO NAME ON IT. EVER. FADES IN 24H.', '', '', '', -.4
    else:
        extra = (f'<div style="display:flex;align-items:baseline;gap:10px;margin-top:10px;padding-bottom:2px;border-bottom:1.5px solid {RULE}">'
                 f'<span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">TO</span>'
                 f'<span style="{HAND};font-size:25px;line-height:1.2;color:{INK}">grandpa,</span>'
                 f'<span style="margin-left:auto;{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL};text-align:right">A NAME, OR JUST &ldquo;YOU&rdquo;</span></div>')
        words = f'<div style="flex:1 1 auto;min-height:{lh * 2}px;{SERIF};font-size:{fs}px;color:{INK};margin-top:8px;{_ruled(lh)}">{_LT}<span class="blink" style="color:{RED}">|</span></div>'
        foot, ear, rot = 'NOT SENT TO THEM. FADES IN 24H.', dogear(24), -.3
        crease = (f'<span aria-hidden="true" style="position:absolute;left:0;right:0;top:62%;height:2px;'
                  f'background:linear-gradient(to bottom,rgba(120,96,60,.13),rgba(255,252,242,.5))"></span>')
    body = (f'{ear}{crease}{top}{extra}'
            f'<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}">{words}</sc-if>'
            f'<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div style="margin-top:16px">{rec}</div></sc-if>'
            f'<div style="margin-top:auto;padding-top:12px;border-top:1px dashed {RULE};flex-shrink:0;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">{foot}</div>')
    return msheet(body, kind='hi', seed=621, pad=f'20px {P}px 16px', rot=rot, minh=200,
                  tapes=ctape(96, 26, -3, 62))

def mwrite_frame(sel='echo'):
    head, _ = WRITE_COPY[sel]
    nxt, label = ('V5MEchoPinned.dc.html', 'pin it up') if sel == 'echo' else ('V5MUnsentPinned.dc.html', 'put it up')
    return f'''<div style="position:absolute;inset:0;display:flex;flex-direction:column">
{matmos()}
{mtopbar(crumb='echoes', back='V5MEchoes.dc.html')}
{mbody(h_hand(head, 28, d='1.8s')
       + f'<div class="rise" style="--w:.6s;margin-top:2px">{step_label("WHAT ARE YOU LEAVING?", 9.5)}</div>'
       + f'<div class="rise" style="--w:.7s;margin-top:-4px">{fullw(kind_cards(sel, phone=True))}</div>'
       + f'<div class="rise" style="--w:.9s;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;margin-top:8px">{mcompose(sel)}</div>', gap=12)}
<div class="rise" style="--w:1.6s;display:flex;flex-direction:column">
{mdock(mcta(label, nxt, 'paper', seed=622) + mtext('not now', 'V5MEchoes.dc.html'))}</div>
{mfooter()}</div>'''

# =====================================================================
# E05 — write an unsent letter
# =====================================================================
page('V5UnsentWrite', 'Leave an unsent letter', write_board('unsent'), css=ECHO_CSS + KIND_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)
mpage('V5MUnsentWrite', 'Leave an unsent letter', mwrite_frame('unsent'), css=ECHO_CSS + KIND_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)

# =====================================================================
# E06 — it's out of you now (same physics as the echo pin: drop + tape slap)
# =====================================================================
def pinned_letter(phone=False):
    if phone:  # phone
        foot = f'<div style="position:absolute;left:22px;bottom:16px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">NOT SENT · FADES IN 24H</div>'
        tp = f'<span class="slap" style="animation-delay:1s">{tape(100, -13, 92, 26, rot=-4, seed=63)}</span>'
        return letter_note('grandpa', LETTER_TXT, 306, 222, rot=2.2, seed=631, size=17, pad=(22, 24), hdr=23, foot=foot, tapes=tp, lh=26, tag=False, ear=24)
    foot = f'<div style="position:absolute;left:34px;bottom:22px;{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">NOT SENT · FADES IN 24H</div>'
    tp = f'<span class="slap" style="animation-delay:1s">{tape(150, -14, 100, 28, rot=-4, seed=43)}</span>'
    return letter_note('grandpa', LETTER_TXT, 400, 262, rot=2.2, seed=431, size=20, pad=(30, 34), hdr=28, foot=foot, tapes=tp, lh=31, tag=False)

upinned = f'''
{atmos()}
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:52px;padding-bottom:60px">
<div style="position:relative"><div class="drop" style="animation-delay:.2s">{pinned_letter()}</div></div>
<div style="display:flex;flex-direction:column;align-items:center;gap:14px">
{h_hand("It's out of you now.", 64, color=PAPERHI, wait='1.4s')}
<div class="rise" style="--w:2.4s;{SERIF};font-style:italic;font-size:21px;color:rgba(233,233,231,.8)">No one will answer it. Some things just need to be said.</div>
<div class="rise" style="--w:2.9s;display:flex;align-items:center;gap:34px;margin-top:22px">{chip('see the wall', 'V5Echoes.dc.html', seed=432, w=200)}{link('back home', 'V5Home.dc.html')}</div>
</div></main>'''
page('V5UnsentPinned', "It's out of you now", upinned, css=ECHO_CSS)

ghosts = ''.join(f'<span aria-hidden="true" style="position:absolute;left:{x}px;top:{y}px;width:{ww}px;height:{hh}px;background:#cfc6ad;opacity:.05;transform:rotate({rr}deg)"></span>'
                 for x, y, ww, hh, rr in [(14, 150, 96, 26, -8), (300, 120, 70, 22, 12), (8, 560, 110, 30, 6), (296, 600, 80, 24, -10)])
mupinned = f'''
{matmos()}
{mtopbar(crumb='echoes', back='V5MEchoes.dc.html')}
<div style="position:absolute;inset:0;z-index:2;pointer-events:none">{ghosts}</div>
{mbody(f'<div class="drop" style="animation-delay:.2s;align-self:center;text-align:left">{pinned_letter(True)}</div>'
       f'<div style="display:flex;flex-direction:column;align-items:center;gap:12px;text-align:center;margin-top:30px">'
       f'{h_hand("It's out of you now.", 38, color=PAPERHI, wait="1.4s")}'
       f'<div class="rise" style="--w:2.3s;{SERIF};font-style:italic;font-size:18px;line-height:1.45;color:rgba(233,233,231,.8);max-width:300px">No one will answer it. Some things just need to be said.</div></div>', center=True)}
<div class="rise" style="--w:2.8s;display:flex;flex-direction:column">
{mdock(mcta('see the wall', 'V5MEchoes.dc.html', 'paper', seed=632) + mtext('back home', 'V5MHome.dc.html'))}</div>
{mfooter()}'''
mpage('V5MUnsentPinned', "It's out of you now", mupinned, css=ECHO_CSS)

# =====================================================================
# E07 — an unsent letter, opened: heard only, replies are off
# =====================================================================
U_SCRIPT = """constructor(props) { super(props); this.state = { heard: null }; }
renderVals() {
const heard = this.state.heard ?? this.props.heard ?? true;
return {
isHeard: heard, notHeard: !heard, heardCount: heard ? 7 : 6, heartFill: heard ? '#B8352A' : 'none',
heardHint: heard ? 'whoever wrote it will know it reached someone' : 'tap once you have read it',
tapHeard: () => this.setState({ heard: !heard }),
letterTo: 'grandpa', letterText: "I'm sorry I didn't pick up. I didn't know it was the last time you'd call. I still have your last voicemail. I play it when the house is too quiet.", fadesShort: '16H', cardH: 384
};
}"""
U_PROPS = '"heard":{"editor":"boolean","default":true}'

def fades(fs, dot):
    return (f'<span style="display:flex;align-items:center;gap:8px"><span style="width:{dot}px;height:{dot}px;border-radius:50%;border:1.5px solid {PENCIL}"></span>FADES IN {{{{fadesShort}}}}</span>')

def open_letter(phone=False):
    if phone:
        W, H, P, fs, lh, hdr, tf = 340, 424, 24, 18, 29, 27, 9.5
    else:
        W, H, P, fs, lh, hdr, tf = 600, 384, 42, 21, 34, 34, 11
    inner = (f'{dogear(32 if not phone else 26)}'
             f'<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;padding-right:{18 if not phone else 14}px;{TYPE};font-size:{tf}px;letter-spacing:.14em;color:{PENCIL}">'
             f'{unsent_tag(10 if not phone else 9)}{fades(tf, 7 if not phone else 6)}</div>'
             f'<div style="{HAND};font-size:{hdr}px;line-height:1.2;color:{PENCIL};margin-top:{18 if not phone else 14}px">to {{{{letterTo}}}},</div>'
             f'<div style="{SERIF};font-size:{fs}px;color:{INK};margin-top:6px;white-space:pre-wrap;overflow-wrap:anywhere;{ruled(lh)}">{{{{letterText}}}}</div>'
             f'<div style="position:absolute;left:{P}px;right:{P}px;bottom:{28 if not phone else 20}px;border-top:1px dashed {RULE};padding-top:{16 if not phone else 14}px;display:flex;justify-content:space-between;align-items:center;gap:12px">'
             f'{heard_btn(26 if not phone else 23)}<span style="{TYPE};font-size:{10.5 if not phone else 9}px;letter-spacing:.12em;line-height:1.6;color:{PENCIL};text-transform:uppercase;text-align:right;max-width:{260 if not phone else 150}px">{{{{heardHint}}}}</span></div>'
             f'{stamp(56, 228, 34) if not phone else stamp(22, 262, 26, "1.3s")}')
    tp = tape(W / 2 - 55, -14, 110, 28, rot=-3, seed=51) if not phone else tape(W / 2 - 48, -13, 96, 26, rot=-3, seed=65)
    return paper(inner, W, H, rot=-1 if not phone else -.8, kind='hi', seed=501 if not phone else 651, pad=f'{34 if not phone else 24}px {P}px', tapes=tp, cls='thud').replace(f'height:{H}px', 'height:{{cardH}}px', 1)

def replies_off(phone=False):
    """Where replies would be: an empty, dashed slot and one soft line."""
    if phone:
        return (f'<div style="border:1.5px dashed #4a4a4f;border-radius:4px;padding:20px 20px;text-align:center">'
                f'<div style="{HAND};font-size:22px;line-height:1.35;color:{CHALK}">Replies are off.</div>'
                f'<div style="{SERIF};font-style:italic;font-size:16.5px;line-height:1.5;color:{BOARDTXT};margin-top:6px">It was never meant to be answered. Heard is enough.</div></div>')
    return (f'<div style="border:1.5px dashed #4a4a4f;border-radius:4px;height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 60px">'
            f'<div style="{HAND};font-size:30px;line-height:1.3;color:{CHALK}">Replies are off.</div>'
            f'<div style="{SERIF};font-style:italic;font-size:20px;line-height:1.5;color:{BOARDTXT};margin-top:8px">It was never meant to be answered. Heard is enough.</div></div>')

FACTS = 'IT WAS NEVER SENT TO THEM · NO ONE CAN SEE WHO WROTE IT'

uopen = f'''
<div class="room" aria-hidden="true"></div>{traces(1440, 900, seed=34)}<div class="vignette"></div><div class="grain"></div>
{topbar(crumb='echoes')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px;display:flex;gap:64px">
<div style="width:640px;display:flex;flex-direction:column;gap:18px;padding-top:2px">
<div class="rise" style="--w:.1s">{link('← the wall', 'V5Echoes.dc.html', BOARDTXT, 12)}</div>
{h_hand("Left for someone who'll never read it.", 44, wait='.2s')}
<div class="rise" style="--w:.9s;display:flex;align-items:center;gap:10px;margin-top:-6px">{ico_letter(BOARDTXT, 16)}{step_label('AN UNSENT LETTER · ANONYMOUS · HEARD ONLY')}</div>
<div class="rise" style="--w:.5s;margin:18px 0 0 14px">{open_letter()}</div>
</div>
<div style="flex-grow:1;display:flex;flex-direction:column;padding-top:40px">
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;padding-right:8px">
<span style="{HAND};font-size:34px;color:{CHALK}">no replies</span>
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">ONLY HEARD</span></div>
<div class="rise" style="--w:1.4s;margin-top:22px">{replies_off()}</div>
<div class="rise" style="--w:1.8s;{TYPE};font-size:11px;letter-spacing:.16em;line-height:1.8;color:{BOARDTXT};margin-top:22px">{FACTS}</div>
<div class="rise" style="--w:2.1s;margin-top:64px;display:flex;align-items:center;gap:16px">
<span style="{MARK};font-size:24px;color:{SOFTRED};transform:rotate(-3deg)">something you never said?</span>{chip('write your own', 'V5UnsentWrite.dc.html', seed=533, w=210)}</div>
</div>
</main>
{footer()}'''
page('V5UnsentOpen', 'An unsent letter, opened', f'<div style="position:absolute;inset:0;display:flex;flex-direction:column">{uopen}</div>',
     css=ECHO_CSS, script=U_SCRIPT, props=U_PROPS)

def mopen_letter():
    """Phone: the opened letter is the screen's main sheet. Heard row pinned to its bottom edge."""
    inner = (f'{dogear(26)}'
             f'<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;padding-right:14px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">'
             f'{unsent_tag(9)}{fades(9.5, 6)}</div>'
             f'<div style="{HAND};font-size:27px;line-height:1.2;color:{PENCIL};margin-top:14px">to {{{{letterTo}}}},</div>'
             f'<div style="flex:1 1 auto;{SERIF};font-size:18px;color:{INK};margin-top:6px;white-space:pre-wrap;overflow-wrap:anywhere;{ruled(29)}">{{{{letterText}}}}</div>'
             f'<div style="position:relative;flex-shrink:0;margin-top:8px;border-top:1px dashed {RULE};padding-top:14px;display:flex;justify-content:space-between;align-items:center;gap:12px">'
             f'<span style="flex-shrink:0;white-space:nowrap">{heard_btn(23)}</span><span style="{TYPE};font-size:9px;letter-spacing:.12em;line-height:1.6;color:{PENCIL};text-transform:uppercase;text-align:right;max-width:150px">{{{{heardHint}}}}</span>'
             f'{stamp(2, -54, 26, "1.3s")}</div>')
    return msheet(inner, kind='hi', seed=651, pad='22px 24px 18px', rot=-.4, minh=300, cls='thud',
                  tapes=ctape(96, 26, -3, 65))

MOH = 844
muopen = f'''
{matmos(MOH)}
{mtopbar(crumb='the wall', back='V5MEchoes.dc.html')}
{mbody(h_hand("Left for someone who'll never read it.", 28, wait='.2s')
       + f'<div class="rise" style="--w:.9s;display:flex;align-items:center;gap:9px;margin-top:-6px">{ico_letter(BOARDTXT, 15)}<div style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">AN UNSENT LETTER · HEARD ONLY</div></div>'
       + f'<div class="rise" style="--w:.5s;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;margin-top:10px">{mopen_letter()}</div>')}
<div class="rise" style="--w:1.4s;display:flex;flex-direction:column">
{mdock(f'<div style="flex:1 1 auto;min-width:0">{replies_off(True)}</div>')}</div>
{mfooter()}'''
mpage('V5MUnsentOpen', 'An unsent letter, opened', f'<div style="position:absolute;inset:0;display:flex;flex-direction:column">{muopen}</div>',
      h=MOH, css=ECHO_CSS, script=U_SCRIPT, props=U_PROPS)

json.dump([
    {"file": "V5UnsentWrite.dc.html", "title": "E05 — Leave an unsent letter", "w": 1440, "h": 900, "row": "echoes"},
    {"file": "V5UnsentPinned.dc.html", "title": "E06 — It's out of you now", "w": 1440, "h": 900, "row": "echoes"},
    {"file": "V5UnsentOpen.dc.html", "title": "E07 — An unsent letter, opened", "w": 1440, "h": 900, "row": "echoes"},
    {"file": "V5MUnsentWrite.dc.html", "title": "ME05 — Leave an unsent letter", "w": 390, "h": 844, "row": "m_echoes"},
    {"file": "V5MUnsentPinned.dc.html", "title": "ME06 — It's out of you now", "w": 390, "h": 844, "row": "m_echoes"},
    {"file": "V5MUnsentOpen.dc.html", "title": "ME07 — An unsent letter, opened", "w": 390, "h": MOH, "row": "m_echoes"},
], open('manifest_unsent.json', 'w'), indent=1)
print('unsent ok')
