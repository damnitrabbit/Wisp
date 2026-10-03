"""N0TRACE V5 phone: time capsule (MC01-03) + care/legal (MS01-04)."""
from gen5 import *
from v5m_home import fcard
import json, os

MANIFEST = 'manifest_capcare.json'
ORDER = ['V5MCapsule', 'V5MCapsuleSealed', 'V5MCapsuleOpen', 'V5MHelp', 'V5MReported', 'V5MPrivacy', 'V5MTerms', 'V5Terms', 'V5Notices']
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

W = MW - 2 * MPAD   # 346 paper width

def mhead(title, size=34, wait='.2s', d='1.6s'):
    return f'<div style="padding:2px {MPAD}px 0">{h_hand(title, size, wait=wait, d=d)}</div>'

# =====================================================================
# MC01 — Write to later you
# =====================================================================
def opt(label, sel=False):
    c = circle_scribble(len(label) * 9.5 + 30, 42, RED, wait='1.8s') if sel else ''
    return f'<span style="position:relative;display:inline-block;padding:4px 6px;{HAND};font-size:{"18px" if sel else "clamp(14px, 4vw, 18px)"};color:{INK if sel else PENCIL}">{c}{label}</span>'

def copt(label, key, sel=False, cw=None):
    """A clickable "open it" option; the chosen one gets the red circle."""
    c = circle_scribble(cw or (len(label) * 9.5 + 30), 42, RED, wait='1.8s')
    hint = 'true' if sel else 'false'
    return (f'<button type="button" class="capopt" onClick="{{{{pick{key}}}}}" aria-pressed="{{{{on{key}}}}}" '
            f'style="position:relative;display:inline-block;padding:4px 6px;{HAND};font-size:clamp(14px, 4vw, 18px);color:{{{{col{key}}}}}">'
            f'<sc-if value="{{{{on{key}}}}}" hint-placeholder-val="{{{{ {hint} }}}}">{c}</sc-if>{label}</button>')

def slot_field(html, name):
    """field() with its value line as a live slot."""
    k = 'padding:8px 0 6px'
    i = html.index(k); j = html.rindex('<div ', 0, i)
    return html[:j] + f'<div data-slot="{name}" ' + html[j + 5:]

CAP_VALS = ("onWeek: false, onMonth: false, onDate: true, colWeek: '#5F584E', colMonth: '#5F584E', colDate: '#221E1A', "
            "dateLabel: '15 october', storageNote: false")

def _ct(w, h, rot, seed, top=-13):
    return tape(0, top, w, h, rot=rot, seed=seed).replace('left:0px', f'left:calc(50% - {w / 2:.0f}px)', 1)

CAP_COPY = 'Sealed in this browser. If you add an email, we keep only that and the date, and delete both once it sends.'

def mcap_letter(email_value='', error='', date='15 october', h=380, chip_seed=1452):
    """Phone capsule letter: words, when it opens, the optional email, and the seal at the bottom right."""
    return fcard(f'''
<div style="{HAND};font-size:clamp(24px, 3.6vh, 28px);color:{INK}">Dear later me,</div>
<div data-slot="capText" style="{SERIF};font-size:clamp(16px, 2.2vh, 17px);line-height:1.5;color:{INK};margin-top:6px">Right now you're scared about the interview on Monday. Whatever happened, you went. That was the hard part. Be gentle with yourself either way.{'' if email_value else '<span class="blink" style="color:' + RED + '">|</span>'}</div>
<div style="margin-top:clamp(8px, 3vh - 8px, 30px);border-top:1px dashed {RULE};padding-top:12px">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">OPEN IT</div>
<div style="display:flex;flex-wrap:nowrap;align-items:center;justify-content:space-between;margin:0 -6px;white-space:nowrap">{copt('next week', 'Week')}{copt('in a month', 'Month')}{copt('{{dateLabel}}', 'Date', True, cw=125)}</div></div>
<div style="margin-top:clamp(8px, 2.4vh - 6px, 24px)">{slot_field(field('remind me by email · optional', email_value, 'you@somewhere.com', error=error, w=294).replace('width:294px', 'width:100%'), 'capEmail')}</div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:clamp(14px, 2.6vh, 24px);flex-shrink:0">{mtext('not now', 'V5MHome.dc.html', PENCIL)}{chip('seal it', 'V5MCapsuleSealed.dc.html', seed=chip_seed, w=150, kind='ink')}</div>''',
        kind='hi', seed=1451, pad='clamp(18px, 2.8vh, 24px) 26px clamp(16px, 2.4vh, 22px)', rot=.8, tapes=_ct(110, 28, 3, 145))

mletter = mcap_letter()

mcwrite = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
{mbody(h_hand('Write to the you who comes later.', 28, wait='.2s', d='2s')
       + f'<div class="rise" style="--w:1.2s;margin-top:-6px;{SERIF};font-size:15px;line-height:1.5;color:{BOARDTXT}">{CAP_COPY}</div>'
       + f'<sc-if value="{{{{storageNote}}}}">{inline_note("this browser can\'t keep things right now (a private window?). an email reminder still works.", "soft", 17)}</sc-if>'
       + f'<div class="rise" style="--w:.5s;flex:0 0 auto;display:flex;flex-direction:column;margin:auto 0">{mletter}</div>', gap=12)}
<div style="height:{M_GAP + 6}px;flex-shrink:0"></div>
{mfooter()}'''
mpage('V5MCapsule', 'Time capsule', mcwrite, script="renderVals() { return { %s }; }" % CAP_VALS)
board('V5MCapsule', 'MC01 — Write to later you', MH, 'm_capsule')

# =====================================================================
# MC02 — Sealed (same physical envelope sequence, phone scale)
# =====================================================================
SEAL = (f'<svg width="62" height="62" viewBox="0 0 100 100" aria-hidden="true"><defs>{ROUGH.format(i="mseal", s=11, sc=6)}'
        f'<radialGradient id="msg" cx="40%" cy="35%"><stop offset="0" stop-color="#D4513F"/><stop offset=".7" stop-color="{RED}"/><stop offset="1" stop-color="#7d1f17"/></radialGradient></defs>'
        f'<g filter="url(#roughmseal)"><circle cx="50" cy="50" r="44" fill="url(#msg)"/><circle cx="50" cy="50" r="33" fill="none" stroke="#8e2a20" stroke-width="2.5"/></g>'
        f'<g transform="translate(26 33) scale(.4)" opacity=".85"><path d="M16 13 L45 11 L47 41 L15 42 Z M74 12 L104 13 L103 42 L73 41 Z" fill="#7a1d15"/>'
        f'<path d="M45 64 L52 71 L59 64 L66 71 L73 64" fill="none" stroke="#7a1d15" stroke-width="6" stroke-linecap="round"/></g></svg>')

EW, EH = 304, 192
VY = EH * .56
FY = EH * .64
LW, LH = EW - 48, 156
LTOP = EH * .13
def _poly(pts):
    return 'polygon(' + ','.join(f'{x:.0f}px {y:.0f}px' for x, y in pts) + ')'
_ml = paper(f'<div style="{HAND};font-size:19px">Dear later me,</div><div style="{SERIF};font-size:11.5px;line-height:1.55;margin-top:5px;color:{PENCIL};display:-webkit-box;-webkit-line-clamp:5;-webkit-box-orient:vertical;overflow:hidden">{{{{preview}}}}</div>',
            LW, LH, kind='hi', seed=1461, pad='16px 18px')
pocket = _poly([(0, 5), (EW / 2, VY), (EW, 5), (EW, EH), (0, EH)])
flap_poly = _poly([(0, 0), (EW, 0), (EW / 2, FY)])
menvelope = f"""<div class="env" style="position:relative;width:{EW}px;height:{EH}px">
<div style="position:absolute;inset:0;z-index:1;filter:drop-shadow(0 12px 18px rgba(0,0,0,.55))"><div class="paper kraft" style="position:absolute;inset:0;background-color:#B49D74;clip-path:{deckle(EW, EH, seed=1462)}"></div>
<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.28),rgba(0,0,0,0) 45%)"></div></div>
<div class="letter-in" style="position:absolute;left:{(EW - LW) / 2:.0f}px;top:{LTOP:.0f}px;width:{LW}px;height:{LH}px;z-index:3">{_ml}</div>
<div style="position:absolute;inset:0;z-index:4;filter:drop-shadow(0 -2px 3px rgba(0,0,0,.22))">
<div class="paper kraft" style="position:absolute;inset:0;clip-path:{pocket}"></div>
<svg width="{EW}" height="{EH}" style="position:absolute;inset:0" aria-hidden="true"><path d="M2 {EH - 2} L{EW / 2} {VY + 14:.0f} L{EW - 2} {EH - 2}" fill="none" stroke="rgba(80,55,25,.32)" stroke-width="1.3"/></svg>
<div style="position:absolute;right:18px;bottom:12px;{HAND};font-size:16px;color:{INK};transform:rotate(-3deg)">open on {{{{openShort}}}}.</div></div>
<div class="flap" style="position:absolute;left:0;top:0;width:{EW}px;height:{FY:.0f}px;transform-origin:50% 0">
<div class="paper kraft" style="position:absolute;inset:0;background-color:#CDB892;clip-path:{flap_poly}"></div></div>
<div class="seal" style="position:absolute;left:{EW / 2 - 31:.0f}px;top:{FY - 42:.0f}px;z-index:7">{SEAL}</div>
</div>"""
SEAL_CSS = """
.letter-in{opacity:0;animation:letterin 1.5s cubic-bezier(.55,.05,.35,1) .35s both}
@keyframes letterin{0%{opacity:0;transform:translateY(-170px) rotate(-3deg)}15%{opacity:1}100%{opacity:1;transform:translateY(0) rotate(0)}}
.flap{z-index:2;transform:perspective(600px) rotateX(180deg);animation:flap .9s cubic-bezier(.45,.05,.3,1) 2s both}
@keyframes flap{0%{z-index:2;transform:perspective(600px) rotateX(180deg);filter:brightness(.82)}49%{z-index:2}50%{z-index:6;filter:brightness(.7)}100%{z-index:6;transform:perspective(600px) rotateX(0deg);filter:brightness(1) drop-shadow(0 3px 3px rgba(0,0,0,.25))}}
.seal{opacity:0;animation:seal .6s cubic-bezier(.2,1.6,.4,1) 2.95s both}
@keyframes seal{0%{opacity:0;transform:scale(2.2) rotate(-20deg)}55%{opacity:1;transform:scale(.9) rotate(4deg)}100%{opacity:1;transform:scale(1) rotate(0)}}
.envwrap{animation:settle 1s ease 2.95s both}
@keyframes settle{0%,100%{transform:none}30%{transform:translateY(3px)}}
"""
msealed = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center">
<div class="envwrap" style="margin-top:190px">{menvelope}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:10px;margin-top:48px;padding:0 {MPAD}px;text-align:center">
{h_hand('Sealed.<br>See you on {{openLong}}.', 34, color=PAPERHI, wait='3.4s')}
<div class="rise" style="--w:4.2s;{SERIF};font-style:italic;font-size:16px;line-height:1.5;color:rgba(233,233,231,.8);5;max-width:300px">Until then it waits here, in this browser. Not even we can open it.</div>
<sc-if value="{{{{remindOk}}}}"><div class="rise" style="--w:4.4s">{inline_note('{{remindOkText}}', 'soft', 18)}</div></sc-if>
<sc-if value="{{{{remindFail}}}}"><div class="rise" style="--w:4.4s">{inline_note('{{remindFailA}}<br>{{remindFailB}}', 'soft', 18)}</div></sc-if>
</div>
<div class="rise" style="--w:4.6s;display:flex;align-items:center;justify-content:space-between;width:100%;padding:30px {MPAD + 4}px 0">{chip('back home', 'V5MHome.dc.html', seed=1463, w=170)}{link('write another', 'V5MCapsule.dc.html', size=12)}</div>
</main>
{mfooter()}'''
SEALED_VALS = "openLong: '15 October', openShort: '15 oct', preview: 'Right now you\\'re scared about the interview on Monday. Whatever happened, you went…', remindOk: false, remindFail: false, remindFailA: 'couldn\\'t set the reminder.', remindFailB: 'the letter is still sealed here.'"
mpage('V5MCapsuleSealed', 'Capsule sealed', msealed, css=SEAL_CSS, script="renderVals() { return { %s }; }" % SEALED_VALS)
board('V5MCapsuleSealed', 'MC02 — Sealed', MH, 'm_capsule')

# =====================================================================
# MC03 — It arrived
# =====================================================================
mopened = fcard(f'''
<div style="{HAND};font-size:30px;color:{INK}">Dear later me,</div>
<div data-slot="openText" style="{SERIF};font-size:18px;line-height:1.65;color:{INK};margin-top:12px"><div>Right now you're scared about the interview on Monday.</div>
<div style="margin-top:12px">Whatever happened, you went. That was the hard part. Be gentle with yourself either way.</div></div>
<div style="{HAND};font-size:22px;color:{INK};margin-top:18px;text-align:right">you, on {{{{sealedOn}}}}</div>
''', kind='hi', seed=1471, pad='28px 28px', rot=-1, tapes=_ct(100, 26, -3, 147))
open_css = """.unfold{animation:unfold 1.6s cubic-bezier(.2,.8,.2,1) .3s both;transform-origin:50% 100%}
@keyframes unfold{from{opacity:0;transform:perspective(700px) rotateX(-70deg) translateY(50px)}to{opacity:1;transform:none}}"""
mcopen = f'''
{matmos()}
{mtopbar(crumb='time capsule', back='V5MHome.dc.html')}
{mbody(f'''<div>{t_mark('it arrived.', 24, '#F0A08F', 'transform:rotate(-3deg);transform-origin:left')}
{h_hand('A note from you, {{agoText}}.', 32, wait='.4s', d='2s', extra='margin-top:4px')}</div>
<div class="unfold" style="flex:0 0 auto;display:flex;flex-direction:column;margin-top:10px">{mopened}</div>
<div class="rise" style="--w:1.5s;margin-top:4px;{SERIF};font-size:15px;line-height:1.5;color:{BOARDTXT}">Read it as many times as you like. When you leave this page, it's gone.</div>''', gap=12, center=True)}
<div class="rise" style="--w:1.9s;display:flex;flex-direction:column">{mdock(mcta('let it go', 'V5MBurnGone.dc.html', 'paper', seed=1472) + mtext('write back', 'V5MCapsule.dc.html'))}</div>
{mfooter()}'''
mpage('V5MCapsuleOpen', 'Capsule opened', mcopen, css=open_css, script="renderVals() { return { sealedOn: '1 October', agoText: 'two weeks ago' }; }")
board('V5MCapsuleOpen', 'MC03 — It arrived', MH, 'm_capsule')

# =====================================================================
# MS01 — Need help now
# =====================================================================
help_css = """
.breath{transform-origin:center;animation:br 14s ease-in-out infinite}
@keyframes br{0%{transform:scale(.7);opacity:.6}28.6%{transform:scale(1);opacity:1}57.1%{transform:scale(1);opacity:1}100%{transform:scale(.7);opacity:.6}}
.ph{position:absolute;left:0;top:0;white-space:nowrap;opacity:0;animation:14s linear infinite}
.p1{animation-name:p1}.p2{animation-name:p2}.p3{animation-name:p3}
@keyframes p1{0%,26%{opacity:1}28.6%,100%{opacity:0}}@keyframes p2{0%,28%{opacity:0}30%,55%{opacity:1}57.1%,100%{opacity:0}}@keyframes p3{0%,57%{opacity:0}59%,97%{opacity:1}100%{opacity:0}}
.tap{transition:background-color .2s}
.tap:active{background-color:rgba(34,30,26,.06)}
"""
PHONE = '<path d="M5 2.5h2.2l1.2 3-1.6 1.1a8 8 0 0 0 3.6 3.6l1.1-1.6 3 1.2V12a1.6 1.6 0 0 1-1.6 1.6A10.6 10.6 0 0 1 3.4 4.1 1.6 1.6 0 0 1 5 2.5z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
GLOBE = '<circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2.5 8.5h12M8.5 2.5c-2.2 2.4-2.2 9.6 0 12M8.5 2.5c2.2 2.4 2.2 9.6 0 12" fill="none" stroke="currentColor" stroke-width="1.3"/>'
def mcall(k, name, detail, href, icon=PHONE, color=INK, last=False):
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    return (f'<a href="{href}"{ext} class="row tap" style="min-height:70px;padding:8px 2px;margin:0 -2px;{bb}gap:12px">'
            f'<span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span style="{HAND};font-size:24px;line-height:1.2;color:{color}">{name}</span>'
            f'<span style="{TYPE};font-size:9.5px;letter-spacing:.12em;line-height:1.4;color:{PENCIL}">{detail}</span></span>'
            f'<span class="go" style="flex-shrink:0;display:flex;align-items:center;gap:8px;{TYPE};font-weight:700;font-size:13px;letter-spacing:.12em;color:{color}">'
            f'<svg width="17" height="17" viewBox="0 0 17 17" aria-hidden="true">{icon}</svg>{k}</span></a>')
mnumbers = paper(f'''
{t_mark('people who pick up', 21)}
<div style="margin-top:6px;border-top:1px dashed {RULE}">
{mcall('14416', 'Tele-MANAS', 'FREE · 24/7 · MANY INDIAN LANGUAGES', 'tel:14416')}
{mcall('112', 'Emergency', 'POLICE · AMBULANCE · FIRE', 'tel:112', color=RED)}
{mcall('FIND', 'Outside India', 'FINDAHELPLINE.COM · CALL, TEXT, CHAT', 'https://findahelpline.com', icon=GLOBE, last=True)}
</div>
<div style="{SERIF};font-style:italic;font-size:15px;color:{PENCIL};margin-top:10px;line-height:1.5;border-top:1px dashed {RULE};padding-top:12px">The people here are kind strangers, not professionals. The people on these lines are trained, and they won't judge you.</div>''',
    W, 386, rot=-.8, seed=1581, pad='26px 24px', tapes=tape(W / 2 - 50, -13, 100, 26, rot=3, seed=158))
mhelp = f'''
{matmos()}
{mtopbar(crumb='help', back='V5MHome.dc.html', right='')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column">
{mhead("You don't have to carry this alone.", 34, d='2s')}
<div class="rise" style="--w:.6s;display:flex;justify-content:center;margin-top:26px">{mnumbers}</div>
<div style="flex-grow:1;min-height:24px"></div>
<div class="rise" style="--w:1.2s;display:flex;align-items:center;gap:20px;padding:0 {MPAD + 4}px">
<div style="width:96px;height:76px;display:flex;align-items:center;justify-content:center;flex-shrink:0"><div class="breath">{rabbit(92, CHALK, uid='mhl', blink=False)}</div></div>
<div style="display:flex;flex-direction:column;gap:6px">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">NEED A MINUTE FIRST?</div>
<div style="position:relative;height:30px;{HAND};font-size:25px;color:{CHALK}"><span class="ph p1">breathe in…</span><span class="ph p2">hold…</span><span class="ph p3">and let it go.</span></div>
<div style="{SERIF};font-size:14px;color:{BOARDTXT};line-height:1.45">In as the rabbit grows, out as it settles.</div></div></div>
<div style="flex-grow:1.2;min-height:24px"></div>
</main>
<div style="position:relative;z-index:55;margin:0 {MPAD}px;padding:12px 0 18px;border-top:1px dashed {SOOT};display:flex;justify-content:space-between;{TYPE};font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;color:{BOARDTXT}"><span>you can come back any time</span><a href="V5MHome.dc.html" class="ul">home</a></div>'''
mpage('V5MHelp', 'Need help now', mhelp, css=help_css)
board('V5MHelp', 'MS01 — Need help now', MH, 'm_care')

# =====================================================================
# MS02 — Reported
# =====================================================================
def kv(k, v, vc=INK):
    return (f'<div style="display:flex;flex-direction:column;gap:3px;padding:9px 0;border-bottom:1px dashed {RULE}">'
            f'<span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">{k}</span>'
            f'<span style="{TYPE};font-size:12px;letter-spacing:.08em;line-height:1.45;color:{vc}">{v}</span></div>')
mrep = fcard(f'''
{h_hand('Sorry about that.', 36, color=INK)}
<div class="rise" style="--w:1.1s;{HAND};font-size:26px;color:{INK};margin-top:2px">You did the right thing.</div>
<div class="rise" style="--w:1.5s;{SERIF};font-size:16.5px;line-height:1.55;color:{INK};margin-top:12px">The pod ended the moment you reported. They only see that it closed, never who left or why.</div>
<div class="rise" style="--w:1.8s;margin-top:12px;border-top:1px dashed {RULE}">
{kv('YOUR PLACE', 'FRONT OF THE LINE')}{kv('THEM', '2–3 REPORTS CLOSE THEIR DOOR FOR THE NIGHT')}{kv('KEPT', 'NOTHING')}</div>''',
    seed=1592, pad='28px 26px', rot=-.8, tapes=_ct(110, 28, -3, 159))
mreported = f'''
{matmos()}
{mtopbar(crumb='talk pod')}
{mbody(f'''<div class="rise" style="--w:.1s;flex:0 0 auto;display:flex;flex-direction:column;margin-top:8px">{mrep}</div>
<div class="rise mrp-row" style="--w:2.6s;display:flex;align-items:center;gap:16px;margin-top:6px">{rabbit(56, CHALK, uid='mrp')}<div style="{HAND};font-size:20px;line-height:1.3;color:{BOARDTXT}">the chat is wiped.<br>your words left with you.</div></div>''', gap=16, center=True)}
<div class="rise" style="--w:2.2s;display:flex;flex-direction:column">{mdock(mcta('find someone else', 'V5MMatching.dc.html', 'paper', seed=1591) + mtext('not now', 'V5MHome.dc.html'))}</div>
{mfooter()}'''
mpage('V5MReported', 'Reported', mreported, css='@media (max-height:780px){.mrp-row{display:none!important}}')
board('V5MReported', 'MS02 — Reported', MH, 'm_care')

# =====================================================================
# MS03 — What we keep (receipt)
# =====================================================================
def item(k, v, vc=INK, bold=False):
    """One receipt line: label, dotted leader, value. Long values wrap to a second line, right-aligned under the first."""
    return (f'<div style="display:flex;align-items:baseline;gap:6px;{TYPE};font-size:10.5px;letter-spacing:.05em;line-height:1.45;margin:7px 0">'
            f'<span style="color:{PENCIL};white-space:nowrap">{k}</span><span style="flex-grow:1;min-width:14px;border-bottom:1.5px dotted {RULE};transform:translateY(-3px)"></span>'
            f'<span style="color:{vc};text-align:right;{"font-weight:700;" if bold else ""}">{v}</span></div>')
ROWS = [('BURN', 'YOUR DEVICE ·<br>GONE WHEN BURNT'), ('ECHOES + UNSENT', 'OUR MEMORY · 24H'), ('POD MESSAGES', 'NEVER STORED'),
        ('VOICE', 'PEER TO PEER ·<br>NEVER RECORDED'), ('CAPSULE', 'YOUR BROWSER ONLY'), ('CAPSULE EMAIL', 'DELETED ONCE SENT'),
        ('QUESTION EMAIL', 'UNTIL YOU<br>UNSUBSCRIBE'), ('REPORTS', 'A COUNT ·<br>GONE BY MORNING'), ('YOUR NAME', 'THIS DEVICE,<br>IF YOU ASK')]
mreceipt = paper(f'''
<div style="text-align:center;{TYPE};font-weight:700;font-size:13px;letter-spacing:.3em">N0TRACE</div>
<div style="text-align:center;{TYPE};font-size:9.5px;letter-spacing:.2em;color:{PENCIL};margin-top:4px">WHAT WE KEEP · RECEIPT</div>
<div style="border-top:1.5px dashed {RULE};margin:12px 0 6px"></div>
{"".join(item(k, v) for k, v in ROWS)}
<div style="border-top:1.5px dashed {RULE};margin:10px 0 6px"></div>
{item('TOTAL KEPT', 'NOTHING', INK, True)}
<div style="text-align:center;{HAND};font-size:21px;margin-top:12px">thank you for trusting us.</div>''',
    322, 446, rot=1.2, kind='hi', seed=1601, pad='24px 22px', torn='bottom')
mprivacy = f'''
{matmos()}
{mtopbar(crumb='what we keep', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column">
{mhead('Almost nothing, and never for long.', 32, d='2s')}
<div class="rise" style="--w:1.2s;padding:6px {MPAD}px 0;{SERIF};font-size:15.5px;line-height:1.5;color:{BOARDTXT}">No accounts. No trackers. No ads. If the server restarts, what's in memory is gone.</div>
<div class="printout" style="display:flex;justify-content:center;margin-top:20px">{mreceipt}</div>
<div class="rise" style="--w:2s;display:flex;justify-content:space-between;padding:20px {MPAD}px 0">{link('the rules →', 'V5MTerms.dc.html', size=11)}{link('home', 'V5MHome.dc.html', size=11)}</div>
</main>
{mfooter()}'''
mpage('V5MPrivacy', 'What we keep', mprivacy, css=""".printout{animation:print 1.8s cubic-bezier(.3,.8,.3,1) .3s both;clip-path:inset(0 0 100% 0)}@keyframes print{to{clip-path:inset(-40px -40px -40px -40px)}}""")
board('V5MPrivacy', 'MS03 — What we keep', MH, 'm_care')

# =====================================================================
# MS04 — The rules (scrolls)
# =====================================================================
from v5x_legal import RULES, rule_inner, apaper   # shared rules copy (importing defines only)
MTH = 2830
msheets = []
for i, rl in enumerate(RULES):
    rot = [-1.2, 1, -.7, 1.3, -1, .8, -1.1, .9][i]
    tp = tape(W / 2 - 46 + (i % 3 - 1) * 40, -12, 92, 24, rot=[-4, 3, -2, 5][i % 4], seed=1610 + i, red=(rl['k'] == 'removed'))
    msheets.append(f'<div class="rise" style="--w:{.4 + min(i, 3) * .2:.1f}s">' + apaper(rule_inner(rl, .9, 'V5M'), W - 6, rot=rot, kind=rl['kind'], seed=1620 + i, pad='24px 24px 26px', tapes=tp) + '</div>')
mterms = f'''
{matmos(MTH)}
{mtopbar(crumb='the rules', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column">
{mhead('The rules, in plain words.', 34, d='2s')}
<div class="rise" style="--w:1.1s;padding:8px {MPAD}px 0;{SERIF};font-size:15.5px;line-height:1.5;color:{BOARDTXT}">Short on purpose. If something here isn't clear, that's on us.</div>
<div class="rise" style="--w:1.3s;padding:12px {MPAD}px 0;{TYPE};font-size:9.5px;letter-spacing:.16em;color:{BOARDTXT}">8 NOTES · 2 MINUTES · OCTOBER 2026</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:30px;margin-top:30px">{"".join(msheets)}</div>
<div style="padding:40px {MPAD}px 0;{HAND};font-size:24px;line-height:1.3;color:{CHALK}">That's all of it. Now go be kind to a stranger.</div>
<div style="display:flex;justify-content:space-between;padding:18px {MPAD}px 30px">{link('← home', 'V5MHome.dc.html', size=11)}{link('what we keep', 'V5MPrivacy.dc.html', size=11)}</div>
</main>
{mfooter()}'''
mpage('V5MTerms', 'The rules', mterms, h=MTH)
board('V5MTerms', 'MS04 — The rules, in plain words (scrolls)', MTH, 'm_care')

write_manifest()
print('capcare ok')

