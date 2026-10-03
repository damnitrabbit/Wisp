"""N0TRACE V5 — voice + open pod rooms (phone). Boards: V5MVoiceWait, V5MVoiceAsk, V5MCall, V5MRooms, V5MRoom, V5MRoomHand."""
from gen5 import *
# shared pieces from the desktop module of the same group (importing it also regenerates the desktop boards: harmless)
from v5x_voice import (ic, MIC, MICOFF, DOOR, FLAG, TEXTI, HANDI, ink_wave, dots10, star, POD_CSS, status_dot, ROOMS, mini_wave,
                       write_manifest)
from v5m_talk import tchip, ctape, apaper, grow, mnote, bleed, LDOTS

W = MW - 2 * MPAD  # 346

def mlink(label, href='#', color=INK, size=10.5, icon=None, bold=True, hit=True):
    """Text action. hit=True keeps a 44px-tall tap row around the words."""
    i = ic(icon, 14) if icon else ''
    hh = 'min-height:44px;' if hit else ''
    return (f'<a href="{href}" class="ul" style="display:inline-flex;align-items:center;gap:7px;{hh}background-position:0 70%;white-space:nowrap;{TYPE};{"font-weight:700;" if bold else ""}'
            f'font-size:{size}px;letter-spacing:.14em;text-transform:uppercase;color:{color}">{i}<span>{label}</span></a>')

def mchip(label, href, kind='ink', w=150, seed=0, icon=None, h=48):
    """Torn-paper chip sized for thumbs: 48 primary, 44 minimum."""
    return tchip(label, href, kind, w, h, seed, icon, fs=12, pad=12)

# ---------- 1:1 pod pieces (phone) ----------
def mmsg(text, mine=False, who='moss_byte', t='11:52', i=0):
    if mine:
        return (f'<div class="msg" style="--i:{i};align-self:flex-end;max-width:84%">'
                f'<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px;text-align:right">YOU · {t}</div>'
                f'<span class="hl" style="{SERIF};font-size:16.5px;line-height:26px;color:{INK}">{text}</span></div>')
    return (f'<div class="msg" style="--i:{i};align-self:flex-start;max-width:86%;padding-left:11px;border-left:2px solid rgba(184,53,42,.35)">'
            f'<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px">{who.upper()} · {t}</div>'
            f'<span style="{SERIF};font-size:16.5px;line-height:26px;color:{INK}">{text}</span></div>')

def msys(text, i=0):
    return (f'<div class="msg" style="--i:{i};align-self:center;display:flex;align-items:center;gap:8px;{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">'
            f'<span style="width:22px;border-top:1px dashed {RULE}"></span>{ic(MIC, 12)}<span>{text}</span><span style="width:22px;border-top:1px dashed {RULE}"></span></div>')

def mtyping(who='moss_byte'):
    return (f'<div style="align-self:flex-start;display:flex;align-items:center;gap:8px;{HAND};font-size:17px;color:{PENCIL};padding-left:13px">'
            f'<span class="dots"><i></i><i></i><i></i></span>{who} is writing</div>')

MCONVO = [
    ("hey. I'm here. take your time, there's no rush.", False, '11:52'),
    ("I don't even know where to start honestly", True, '11:53'),
    ("that's okay. start anywhere. the middle is fine too.", False, '11:53'),
    ("my best friend moved away last month. tuesdays were chai after work. now tuesdays are just… tuesdays.", True, '11:55'),
    ("that sounds really lonely. like the shape of your week changed overnight.", False, '11:56'),
]

STRIP_H = 100
SHEET_H = MH - 64 - 6 - STRIP_H - 20 - 24   # (legacy, fixed-frame sizes; the phone frame no longer uses them)
def pod_strip(status="THEY'RE LISTENING", right=None):
    """Legacy torn name strip (kept for anything still importing it; pod screens now use mwho + the dock)."""
    rt = right if right is not None else (f'<div style="display:flex;flex-direction:column;align-items:flex-end">'
                                         f'{mlink("leave gently", "V5MPodEnd.dc.html", INK, 10, DOOR)}{mlink("report", "V5MReported.dc.html", RED, 10, FLAG)}</div>')
    inner = (f'<div style="display:flex;align-items:center;justify-content:space-between;height:100%">'
             f'<div><div style="{HAND};font-size:23px;line-height:1.15;color:{INK}">you &amp; moss_byte</div>'
             f'<div style="margin-top:5px">{status_dot(status, PENCIL, size=9.5)}</div></div>{rt}</div>')
    return paper(inner, W, STRIP_H, rot=-.6, seed=601, pad='6px 16px 6px 18px', tapes=tape(W / 2 - 40, -11, 80, 22, rot=-3, seed=60))

# ---------- the pod shell (same as the call): name line · chat sheet (fills) · dock on the safe area ----------
def mwho(status="THEY'RE LISTENING", who='you &amp; moss_byte'):
    st = f'<div style="min-width:0;display:flex;justify-content:flex-end;text-align:right">{status_dot(status, BOARDTXT, size=9)}</div>' if status else ''
    return (f'<div class="rise" style="--w:.1s;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:0 2px 0 4px">'
            f'<span style="{HAND};font-size:24px;line-height:1.2;color:{CHALK};white-space:nowrap">{who}</span>{st}</div>')

def mcomposer():
    return (f'<div style="flex-shrink:0;border-top:1.5px dashed {RULE};padding-top:12px;display:flex;align-items:center;justify-content:space-between;gap:12px">'
            f'<span style="flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;{SERIF};font-style:italic;font-size:16px;color:{PENCIL};white-space:nowrap">say it however it comes out…<span class="blink" style="color:{INK};font-style:normal">|</span></span>'
            f'{mchip("send", "#", "ink", 84, seed=611)}</div>')

RULED = 'background-image:repeating-linear-gradient(to bottom,transparent 0 25px,rgba(96,120,150,.15) 25px 26px);background-position:0 10px'
def mchat_inner(msgs, tail='', top='', note='', header='11:52 PM · NOTHING HERE IS SAVED', composer=True, gap=15):
    return (f'<div aria-hidden="true" style="position:absolute;inset:0;{RULED};pointer-events:none"></div>'
            f'<div style="position:relative;flex:1 1 auto;min-height:0;display:flex;flex-direction:column">'
            f'<div style="flex-shrink:0;{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};text-align:center;padding-bottom:10px;border-bottom:1px dashed {RULE}">{header}</div>{top}'
            f'<div class="scroll" style="flex:1 1 auto;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:{gap}px;padding:14px 2px 12px;overflow:hidden">{msgs}{tail}</div>'
            f'{note}{mcomposer() if composer else ""}</div>')

def mchat(msgs, tail='', top='', note='', header='11:52 PM · NOTHING HERE IS SAVED', composer=True, rot=.3, seed=612, gap=15):
    """The chat paper of a live pod: an msheet, composer pinned to its bottom."""
    return msheet(mchat_inner(msgs, tail, top, note, header, composer, gap), kind='hi', seed=seed, pad='16px 18px 14px', rot=rot, minh=300,
                  tapes=ctape(100, 26, -2, 61))

def mchat_sheet(extra='', tail=None, h=None, note='', header='11:52 PM · NOTHING HERE IS SAVED'):
    msgs = ''.join(mmsg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(MCONVO)) + extra
    return mchat(msgs, mtyping() if tail is None else tail, note=note, header=header)

def pod_sub(leave='V5MPodEnd.dc.html', report='report · ends now'):
    return mlink('leave gently', leave, CHALK, 10.5, DOOR) + mlink(report, 'V5MReported.dc.html', CRISIS, 10.5, FLAG)

def voice_row(label='ask for voice', href='V5MVoiceWait.dc.html', right=f'CHECK-IN<br>IN 3:48'):
    return mcta(label, href, 'kraft', seed=1514, icon=ic(MIC, 14)) + (mnote(right) if right else '')

def mpod(sheet, row=None, status="THEY'RE LISTENING", crumb='talk pod', overlay='', sub=None, head=None):
    """Live pod shell (talk pod, voice wait/ask, edge cases): exactly the call's frame."""
    row = voice_row() if row is None else row
    return f'''
{matmos()}
{mtopbar(back='V5MHomeOpen.dc.html', crumb=crumb)}
{mbody((head if head is not None else mwho(status)) + grow(sheet))}
<div class="rise" style="--w:1s;display:flex;flex-direction:column">
{mdock(row, sub=pod_sub() if sub is None else sub, footer=False)}</div>{overlay}'''

# overlays (nudge, voice ask) sit centred over the whole frame, as wide as the column
MOV_CSS = """.mov{position:absolute;inset:0;z-index:61;display:flex;align-items:center;justify-content:center;padding:0 22px;pointer-events:none}
.mov>.card{width:100%;max-width:360px;pointer-events:auto;animation:mnudge .9s cubic-bezier(.3,1.3,.5,1) .5s both}
@keyframes mnudge{from{opacity:0;transform:translateY(40px) rotate(-4deg)}to{opacity:1;transform:none}}"""
def moverlay(card):
    return f'<div class="veil"></div><div class="mov"><div class="card">{card}</div></div>'

# ================= MV01 — you asked for voice =================
wait_note = f'''<div class="pinned" style="--w:1s;position:relative;flex-shrink:0;margin:0 0 12px;padding:11px 13px 11px;border:1.5px dashed rgba(34,30,26,.35);background:rgba(216,198,164,.28);transform:rotate(-.5deg)">
<div style="display:flex;align-items:center;justify-content:space-between;gap:10px">
<span style="display:flex;align-items:center;gap:8px;color:{INK}">{ic(MIC, 16)}<span style="{HAND};font-size:20px;line-height:1">voice asked</span></span>
{status_dot('WAITING ON THEM', INK, size=9)}</div>
<div style="{SERIF};font-style:italic;font-size:14px;line-height:1.4;color:{PENCIL};margin-top:7px">Keep writing. Nothing starts unless you both say yes.</div></div>'''
mv01 = mpod(mchat_sheet(msys('11:57 · you asked for voice', 5) + mmsg('no rush on that. what was the best tuesday?', t='11:57', i=6), note=wait_note),
            row=mcta('take it back', 'V5MPod.dc.html', 'kraft', seed=1515, icon=ic(MIC, 14)))
mpage('V5MVoiceWait', 'Voice asked, waiting', mv01, css=POD_CSS)

# ================= MV02 — they'd like to talk by voice =================
def mfacts(rows):
    cells = ''.join(f'<span style="color:{PENCIL}">{k}</span><span style="color:{c}">{v}</span>' for k, v, c in rows)
    return f'<div style="display:grid;grid-template-columns:78px 1fr;row-gap:8px;{TYPE};font-size:10px;letter-spacing:.1em;line-height:1.45;color:{INK}">{cells}</div>'

ask_card = apaper(f'''
<div style="display:flex;align-items:center;justify-content:space-between">{t_mark('a small ask', 21)}<span style="color:{INK}">{ic(MIC, 20)}</span></div>
{h_hand('moss_byte would like to talk by voice.', 29, color=INK, wait='1s', d='1.7s', extra='margin-top:4px')}
<div class="rise" style="--w:1.8s;{SERIF};font-size:16.5px;line-height:1.5;color:{INK};margin-top:10px">Only if you want to. Text is just as good.</div>
<div class="rise" style="--w:2s;margin-top:16px;padding-top:14px;border-top:1px dashed {RULE}">{mfacts([('VOICE', 'PEER TO PEER · NEVER RECORDED', INK), ('YOUR MIC', 'ASKED ONLY AFTER YES', INK), ('KEPT', 'NOTHING', INK)])}</div>
<div class="rise" style="--w:2.3s;display:flex;align-items:center;gap:12px;margin-top:22px">{mcta('say yes', 'V5MCall.dc.html', 'ink', seed=621)}
{mtext('keep it to text', 'V5MPod.dc.html', INK)}</div>
<div class="rise" style="--w:2.6s;{TYPE};font-size:9px;letter-spacing:.13em;color:{PENCIL};margin-top:14px">NO REASON NEEDED. THEY WON'T BE TOLD WHY.</div>''',
    rot=-1, seed=622, pad='26px 24px 22px', tapes=ctape(100, 26, 3, 62, y=-13))
mv02 = mpod(mchat_sheet(msys('11:57 · moss_byte asked for voice', 5), tail=''), overlay=moverlay(ask_card))
mpage('V5MVoiceAsk', 'They would like to talk by voice', mv02, css=POD_CSS + MOV_CSS)

# ================= MV03 — on voice =================
def mlane(name, state, wave):
    st_col = '#B0561F' if state.startswith('SPEAK') else PENCIL
    return (f'<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:27px;color:{INK}">{name}</span>'
            f'<span style="{TYPE};font-size:9.5px;letter-spacing:.18em;color:{st_col}">{state}</span></div>{wave}')

call_inner = f'''<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 25px,rgba(96,120,150,.12) 25px 26px);background-position:0 10px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};text-align:center;padding-bottom:10px;border-bottom:1px dashed {RULE}">PEER TO PEER · NOT RECORDED</div>
<div style="display:flex;align-items:flex-end;justify-content:space-between;margin-top:14px">
<div><div style="{HAND};font-size:52px;line-height:1;color:{INK}">03:41</div>
<div style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL};margin-top:4px">14 MIN TOGETHER</div></div>
{status_dot('ON VOICE', INK, size=9.5)}</div>
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:22px">
<div class="rise" style="--w:.5s">{mlane('moss_byte', 'SPEAKING', ink_wave(306, 130, 50, 4301, 'ma', n=30, sw=2.4))}</div>
<div style="border-top:1.5px dashed {RULE}"></div>
<div class="rise" style="--w:.8s">{mlane('you', 'LISTENING', ink_wave(306, 90, 5, 4302, 'mb', color=PENCIL, n=30, step=1.4, sw=2))}</div>
</div>
</div>'''
def fluid(svg):
    """Let a fixed-size ink drawing stretch to its column (phones 320 to 430 wide)."""
    return svg.replace('<svg ', '<svg preserveAspectRatio="none" ', 1).replace('style="display:block;', 'style="display:block;width:100%;', 1)

call_inner = call_inner.replace(ink_wave(306, 130, 50, 4301, 'ma', n=30, sw=2.4), fluid(ink_wave(306, 130, 50, 4301, 'ma', n=30, sw=2.4))) \
                       .replace(ink_wave(306, 90, 5, 4302, 'mb', color=PENCIL, n=30, step=1.4, sw=2), fluid(ink_wave(306, 90, 5, 4302, 'mb', color=PENCIL, n=30, step=1.4, sw=2)))
call_sheet = msheet(call_inner, kind='hi', seed=631, pad='16px 20px 14px', rot=.3, minh=380, tapes=tape(W / 2 - 50, -12, 100, 26, rot=-2, seed=63))
mv03 = f'''
{matmos()}
{mtopbar(back='V5MHomeOpen.dc.html', crumb='talk pod')}
{mbody(f'<div class="rise" style="--w:.1s;padding-left:4px;{HAND};font-size:24px;color:{CHALK}">you &amp; moss_byte</div>'
       f'<div class="rise" style="--w:.3s;flex:1 1 auto;min-height:0;display:flex;flex-direction:column">{call_sheet}</div>')}
<div class="rise" style="--w:1s;display:flex;flex-direction:column">
{mdock(mcta('mute', '#', 'ink', seed=641, icon=ic(MIC, 14)) + mcta('back to text', 'V5MPod.dc.html', 'kraft', seed=642, icon=ic(TEXTI, 14)),
       sub=mlink('leave gently', 'V5MPodEnd.dc.html', CHALK, 10.5, DOOR) + mlink('report · ends now', 'V5MReported.dc.html', CRISIS, 10.5, FLAG), footer=False)}</div>'''
mpage('V5MCall', 'On voice', mv03, css=POD_CSS)

# ================= MR01 — open pod: pick a room (scrolls) =================
SW, SH = 164, 214
def mslip(i, name, theme, n, speakers, href):
    full = n >= 10
    r = random.Random(700 + i)
    rot = r.uniform(-2.4, 2.4)
    kind = ['hi', '', 'kraft', 'hi', '', 'hi', 'kraft', '', 'hi', ''][i % 10]
    lead = speakers[0]
    others = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}"> +{len(speakers) - 1}</span>' if len(speakers) > 1 else ''
    wv = mini_wave(980 + i, 26, 12) if not full else ''
    inner = f'''<div style="display:flex;flex-direction:column;height:100%">
<div style="{HAND};font-size:20px;line-height:1.12;color:{INK};min-height:46px;padding-right:{30 if full else 0}px">{name}</div>
<div style="{SERIF};font-style:italic;font-size:13px;line-height:1.3;color:{PENCIL};margin-top:4px;min-height:34px">{theme}</div>
<div style="border-top:1px dashed {RULE};margin-top:8px;padding-top:7px;flex-grow:1">
<div style="display:flex;align-items:center;justify-content:space-between;{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL};margin-bottom:2px;height:14px">ON STAGE{wv}</div>
<div style="display:flex;align-items:center;gap:6px;{HAND};font-size:15.5px;color:{INK};white-space:nowrap">{lead}{others}</div></div>
<div style="display:flex;align-items:center;justify-content:space-between">{dots10(n, 7, 3, full)}
<span style="{TYPE};font-weight:700;font-size:10px;letter-spacing:.06em;color:{PENCIL if full else INK}">{n}/10</span></div></div>'''
    st = (f'<span aria-hidden="true" style="position:absolute;right:10px;top:30px;transform:rotate(-12deg);padding:1px 8px;border:2px solid {PENCIL};border-radius:3px;'
          f'{TYPE};font-weight:700;font-size:12px;letter-spacing:.22em;color:{PENCIL};opacity:.85;mix-blend-mode:multiply">FULL</span>') if full else ''
    pin = (f'<svg width="18" height="18" viewBox="0 0 20 20" aria-hidden="true" style="position:absolute;left:{SW / 2 - 9:.0f}px;top:-6px;z-index:6;overflow:visible">'
           f'<ellipse cx="13" cy="15" rx="8" ry="4.5" fill="#000" opacity=".4"/><circle cx="10" cy="10" r="7.5" fill="{RED if i % 3 == 0 else "#3a3a3d"}"/>'
           f'<circle cx="7.6" cy="7.6" r="2.2" fill="#fff" opacity=".28"/></svg>')
    decor = pin if i % 2 == 0 else tape(SW / 2 - 34, -11, 68, 20, rot=r.uniform(-6, 6), seed=730 + i)
    slip = paper(inner + st, SW, SH, rot=rot, kind=kind, seed=710 + i, pad='16px 14px 13px', tapes=decor,
                 extra='opacity:.6;filter:grayscale(.3) drop-shadow(0 12px 18px rgba(0,0,0,.5))' if full else '')
    label = f'{name}, {n} of 10{", full" if full else ""}'
    w = f'--w:{.3 + i * .07:.2f}s'
    if full:
        return f'<div class="rise" style="{w}" aria-label="{label}">{slip}</div>'
    return f'<a href="{href}" class="chip rise" style="{w};display:block" aria-label="{label}">{slip}</a>'

MRH = 1610
grid = ''.join(mslip(i, *R, href='V5MRoomHand.dc.html' if i == 3 else 'V5MRoom.dc.html') for i, R in enumerate(ROOMS))
mr01 = f'''
{matmos(MRH)}
{mtopbar(back='V5MHomeOpen.dc.html', crumb='open pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:6px {MPAD}px 0">
{h_hand('Pick a room.', 40)}
<div class="rise" style="--w:.9s;{SERIF};font-size:16px;line-height:1.45;color:{BOARDTXT};margin-top:2px">Themed voice rooms, up to 10 people.<br>Speak if you like, or just listen.</div>
<div class="rise" style="--w:1.1s;display:flex;align-items:center;justify-content:space-between;margin-top:14px;padding-bottom:10px;border-bottom:1px dashed {SOOT}">
<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">25 ROOMS · UNTIL 2AM</span>{mlink('see all 25 →', '#', CHALK, 10)}</div>
<div style="display:grid;grid-template-columns:repeat(2,{SW}px);justify-content:space-between;row-gap:26px;margin-top:26px">{grid}</div>
<div class="rise" style="--w:1.4s;{MARK};font-size:19px;line-height:1.25;color:#F0A08F;text-align:center;margin:26px 0 0;transform:rotate(-1.5deg)">a seat opens when someone leaves.</div>
<div class="rise" style="--w:1.5s;align-self:center;margin:8px 0 18px">{mlink('see all 25 rooms →', '#', CHALK, 10.5)}</div>
</main>
{mfooter()}'''
mpage('V5MRooms', 'Open pod, pick a room', mr01, h=MRH, css=POD_CSS + """.rise.chip{animation:rise 1.1s cubic-bezier(.2,.7,.2,1) var(--w,.3s) forwards}""")

# ================= MR02 / MR03 — inside a room =================
TW, TH = 160, 112
def mtag(i, name, state, is_mod, me, can_move):
    st_col = '#B0561F' if state == 'speaking' else PENCIL
    if state == 'speaking':
        wv = ink_wave(TW - 28, 22, 8, 4400 + i, f'ms{i}', n=16, frames=7, step=.85, sw=1.8)
    elif state == 'muted':
        wv = f'<div style="display:flex;align-items:center;gap:6px;color:{PENCIL}">{ic(MICOFF, 12)}{ink_wave(TW - 48, 22, 0, 0, "", muted=True, color=PENCIL)}</div>'
    else:
        wv = ink_wave(TW - 28, 22, 1.8, 4400 + i, f'ms{i}', color=PENCIL, n=16, frames=6, step=1.4, sw=1.4)
    badge = f'<span style="display:inline-flex;align-items:center;gap:3px;{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.14em;color:{INK}">{star(11, INK)}MOD</span>' if is_mod else ''
    foot = ''
    if can_move:
        foot = f'<a href="#" class="ul" style="{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.12em;color:{INK}">MOVE OFF STAGE</a>'
    elif me:
        foot = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}">YOU</span>'
    inner = (f'<div style="{HAND};font-size:19px;line-height:1.1;color:{INK};white-space:nowrap">{name}</div>'
             f'<div style="display:flex;align-items:center;justify-content:space-between;margin:3px 0 4px"><span style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{st_col}">{state.upper()}</span>{badge}</div>'
             f'{wv}<div style="margin-top:4px;height:12px">{foot}</div>')
    rot = [-1.2, .9, .7, -.8][i % 4]
    return f'<div class="rise" style="--w:{.4 + i * .1:.2f}s">{paper(inner, TW, TH, rot=rot, kind="hi" if i % 3 else "", seed=760 + i, pad="11px 13px 9px")}</div>'

def mlisteners(names, you=None, hand=None):
    out = []
    for n in names:
        h = f'<span style="color:{INK}">{ic(HANDI, 13)}</span>' if n in (you, hand) else ''
        y = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}">YOU</span>' if n == you else ''
        out.append(f'<span style="display:inline-flex;align-items:center;gap:5px;{HAND};font-size:17.5px;color:{INK};white-space:nowrap">{n}{h}{y}</span>')
    return f'<div style="display:flex;flex-wrap:wrap;column-gap:18px;row-gap:2px">{"".join(out)}</div>'

def mstage(stage, mod_view, listeners, you=None, hand=None, h=408):
    tags = ''.join(mtag(i, n, s, m, me, mod_view and not me) for i, (n, s, m, me) in enumerate(stage))
    inner = f'''<div style="display:flex;align-items:baseline;justify-content:space-between;padding-bottom:7px;border-bottom:1px dashed {RULE}">
<span style="{HAND};font-size:23px;color:{INK}">on stage</span><span style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL}">4 ON STAGE</span></div>
<div style="display:grid;grid-template-columns:repeat(2,{TW}px);justify-content:space-between;row-gap:12px;margin-top:12px">{tags}</div>
<div style="margin-top:14px;padding-top:7px;border-top:1.5px dashed {RULE}">
<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:21px;color:{INK}">listening</span>
<span style="{TYPE};font-size:8.5px;letter-spacing:.14em;color:{PENCIL}">{len(listeners)} HERE · 2 SEATS OPEN</span></div>
{mlisteners(listeners, you, hand)}</div>'''
    return paper(inner, W + 6, h, rot=.3, kind='kraft', seed=771, pad='14px 10px 12px', tapes=tape(W / 2 - 46, -12, 92, 24, rot=-2, seed=77))

def mroom_head(mod_view):
    you = (f'<span style="display:inline-flex;align-items:center;gap:6px;{MARK};font-size:18px;color:{BOARDTXT};line-height:1">{star(17, BOARDTXT)}you\'re a mod here</span>'
           if mod_view else f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">YOU\'RE LISTENING</span>')
    return (f'<div class="rise" style="--w:.1s;padding:0 2px">'
            f'<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:27px;color:{CHALK};line-height:1.15">can\'t sleep club</span>'
            f'<span style="{TYPE};font-weight:700;font-size:10px;letter-spacing:.1em;color:{CHALK}">8/10</span></div>'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-top:5px">'
            f'<span style="{SERIF};font-style:italic;font-size:14px;color:{BOARDTXT}">for the 1am ceiling starers</span>{you}</div></div>')

def mroom_bar(mod_view):
    """Same footerless dock as the live pods: the room's one state on the left, leave/report on the right."""
    left = (mchip('mute', '#', 'ink', 118, seed=781, icon=MIC) if mod_view else
            f'<span style="display:inline-flex;align-items:center;gap:7px;min-height:44px;{HAND};font-size:17px;color:{CHALK};white-space:nowrap">{ic(HANDI, 15)}dusk_signal asked you up</span>')
    links = (f'<span style="display:flex;align-items:center;gap:16px">{mlink("leave gently", "V5MRooms.dc.html", CHALK, 10.5, DOOR)}'
             f'{mlink("report", "V5MReported.dc.html", CRISIS, 10.5, FLAG)}</span>')
    row = (f'<div style="flex:1 1 auto;display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:48px;flex-wrap:wrap;row-gap:4px">'
           f'{left}{links}</div>')
    return f'<div class="rise" style="--w:1s;display:flex;flex-direction:column">{mdock(row, footer=False)}</div>'

MSTAGE_MOD = [('neon_moth', 'speaking', False, False), ('quiet_otter', 'listening', True, True),
              ('paper_kite', 'muted', False, False), ('dusk_signal', 'listening', True, False)]
MSTAGE_LIS = [('neon_moth', 'speaking', False, False), ('paper_kite', 'muted', False, False),
              ('dusk_signal', 'listening', True, False), ('velvet_crow', 'listening', False, False)]

def note_slip(inner, h, seed, rot):
    return paper(inner, W - 14, h, rot=rot, kind='hi', seed=seed, pad='16px 20px 14px', tapes=tape((W - 14) / 2 - 46, -12, 92, 24, rot=3, red=True, seed=seed + 1))

hand_slip = note_slip(f'''<div style="display:flex;align-items:center;justify-content:space-between">{t_mark('a hand is up', 20)}<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">0:42 · NEXT: STATIC_HERON</span></div>
<div style="display:flex;align-items:center;gap:10px;margin-top:6px"><span class="sway" style="display:inline-block;color:{INK}">{ic(HANDI, 26)}</span>
<span style="{HAND};font-size:23px;line-height:1.1;color:{INK}">lowkey_comet</span></div>
<div style="{SERIF};font-size:14.5px;color:{PENCIL};margin-top:2px">would like to come up and speak.</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:12px">{mchip('invite up', '#', 'ink', 138, seed=791)}{mlink('not now', '#', INK, 10.5, bold=False)}</div>''', 170, 792, -.8)

invite_slip = note_slip(f'''<div style="display:flex;align-items:center;justify-content:space-between"><span style="display:flex;align-items:center;gap:6px">{star(15, INK)}<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">FROM DUSK_SIGNAL · MOD</span></span></div>
<div style="display:flex;align-items:baseline;gap:12px;margin-top:2px">{h_hand('come up?', 36, color=INK, wait='1.4s', d='1.1s', extra='white-space:nowrap')}
<span class="rise" style="--w:2s;{SERIF};font-size:14px;line-height:1.35;color:{PENCIL}">a seat on stage is yours</span></div>
<div class="rise" style="--w:2.2s;display:flex;align-items:center;gap:22px;margin-top:8px">{mchip('come up', '#', 'ink', 128, seed=795)}{mlink('not now', '#', INK, 10.5, bold=False)}</div>
<div class="rise" style="--w:2.4s;{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL};margin-top:9px">YOUR MIC IS ASKED ONLY WHEN YOU COME UP.</div>''', 170, 796, -1.2)

def mroom(mod_view):
    if mod_view:
        stage = mstage(MSTAGE_MOD, True, ['static_heron', 'lowkey_comet', 'fog_lamp', 'amber_fox'], hand='lowkey_comet')
        slip = hand_slip
    else:
        stage = mstage(MSTAGE_LIS, False, ['static_heron', 'quiet_otter', 'fog_lamp', 'amber_fox'], you='quiet_otter')
        slip = invite_slip
    return f'''
{matmos()}
{mtopbar(back='V5MRooms.dc.html', crumb='open pod')}
{mbody(f'''{mroom_head(mod_view)}
<div class="rise" style="--w:.3s;flex:1 0 auto;display:flex;flex-direction:column">{stage}</div>
<div class="pinned" style="--w:1.2s;align-self:center;flex-shrink:0;margin-top:{-4 if mod_view else -2}px">{slip}</div>''', top=0)}
{mroom_bar(mod_view)}'''

mpage('V5MRoom', 'Open pod room, mod view', mroom(True), css=POD_CSS)
mpage('V5MRoomHand', 'Open pod room, invited to stage', mroom(False), css=POD_CSS)

PHONE = [
    {"file": "V5MVoiceWait.dc.html", "title": "MV01 — You asked for voice", "w": 390, "h": 844, "row": "m_voice"},
    {"file": "V5MVoiceAsk.dc.html", "title": "MV02 — They'd like to talk by voice", "w": 390, "h": 844, "row": "m_voice"},
    {"file": "V5MCall.dc.html", "title": "MV03 — On voice", "w": 390, "h": 844, "row": "m_voice"},
    {"file": "V5MRooms.dc.html", "title": "MR01 — Open pod: pick a room (scrolls)", "w": 390, "h": MRH, "row": "m_rooms"},
    {"file": "V5MRoom.dc.html", "title": "MR02 — In a room, mod view", "w": 390, "h": 844, "row": "m_rooms"},
    {"file": "V5MRoomHand.dc.html", "title": "MR03 — Listener, invited to stage", "w": 390, "h": 844, "row": "m_rooms"},
]
if __name__ == '__main__':
    import v5x_voice
    write_manifest(v5x_voice.DESK + PHONE)
    print('voice phone ok')
