"""N0TRACE V5 — voice + open pod rooms (desktop). Boards: V5VoiceWait, V5VoiceAsk, V5Call, V5Rooms, V5Room, V5RoomHand."""
from gen5 import *
import json, os
from v5m_talk import tchip

# ---------- local copies of the 1:1 pod pieces (v5_talk.py is not imported: it would regenerate its own boards) ----------
MIC = '<path d="M8 2.5a2.5 2.5 0 0 1 2.5 2.5v4a2.5 2.5 0 0 1-5 0V5A2.5 2.5 0 0 1 8 2.5zM4 8.5a4 4 0 0 0 8 0M8 12.5V15M5.5 15h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>'
MICOFF = MIC + '<path d="M2.5 2.5l11 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'
DOOR = '<path d="M3 15h10M5 15V2.5h6V15M9 9h.01M11 2.5l2 1.5V15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
FLAG = '<path d="M4 15V2.5M4 3h8l-2 3 2 3H4" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
TEXTI = '<path d="M2.5 3.5h11v7.5H7l-3 2.5v-2.5H2.5z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
HANDI = ('<path d="M5 9.5V4.2a1 1 0 0 1 2 0V8M7 8V2.8a1 1 0 0 1 2 0V8M9 8V3.4a1 1 0 0 1 2 0V8.6M11 8.6V5.2a1 1 0 0 1 2 0v4.6c0 3-1.8 5.2-4.6 5.2-2 0-3-1-4-2.6L2.9 9.6a1 1 0 0 1 1.7-1.1L5 9.5" '
         'fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>')

def ic(icon, size=16, extra=''):
    return f'<svg width="{size}" height="{size + 1}" viewBox="0 0 16 17" aria-hidden="true" style="position:relative;flex-shrink:0;{extra}">{icon}</svg>'

def pod_btn(label, href, icon, kind, seed=0, w=240):
    if kind == 'red':
        return (f'<a href="{href}" class="ul" style="align-self:flex-start;display:inline-flex;align-items:center;gap:10px;margin:6px 0 0 4px;color:{RED};'
                f'{TYPE};font-weight:700;font-size:12px;letter-spacing:.14em;text-transform:uppercase">{ic(icon)}<span>{label}</span></a>')
    rot = {'ink': -.8, 'kraft': .7, 'paper': .4}[kind]
    return tchip(label, href, kind, w, 54, seed, icon, fs=13, rot=rot, justify='flex-start')

def line_msg(text, mine=False, who='moss_byte', t='11:52', i=0, size=19, lh=30):
    if mine:
        head = f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px;text-align:right">YOU · {t}</div>'
        body = f'<span class="hl" style="{SERIF};font-size:{size}px;line-height:{lh}px;color:{INK}">{text}</span>'
        return f'<div class="msg" style="--i:{i};align-self:flex-end;max-width:76%;text-align:left">{head}{body}</div>'
    head = f'<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-bottom:4px">{who.upper()} · {t}</div>'
    body = f'<span style="{SERIF};font-size:{size}px;line-height:{lh}px;color:{INK}">{text}</span>'
    return f'<div class="msg" style="--i:{i};align-self:flex-start;max-width:76%;padding-left:14px;border-left:2px solid rgba(184,53,42,.35)">{head}{body}</div>'

def sys_line(text, i=0, color=PENCIL):
    """A quiet event written across the sheet, between two dashes."""
    return (f'<div class="msg" style="--i:{i};align-self:center;display:flex;align-items:center;gap:12px;{TYPE};font-size:10px;letter-spacing:.18em;color:{color};text-transform:uppercase">'
            f'<span style="width:40px;border-top:1px dashed {RULE}"></span>{ic(MIC, 13)}<span>{text}</span><span style="width:40px;border-top:1px dashed {RULE}"></span></div>')

def typing(who='moss_byte', size=20, pad=18):
    return (f'<div style="align-self:flex-start;display:flex;align-items:center;gap:10px;{HAND};font-size:{size}px;color:{PENCIL};padding-left:{pad}px">'
            f'<span class="dots"><i></i><i></i><i></i></span>{who} is writing</div>')

POD_CSS = f"""
.hl{{background-image:linear-gradient(transparent 38%,rgba(216,198,164,.75) 38%,rgba(216,198,164,.75) 90%,transparent 90%);-webkit-box-decoration-break:clone;box-decoration-break:clone;padding:0 4px}}
.scroll{{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 70px);mask-image:linear-gradient(to bottom,transparent 0,#000 70px)}}
.msg{{opacity:0;animation:msgin .6s ease calc(.25s + var(--i) * .12s) both}}
@keyframes msgin{{from{{opacity:0;transform:translateY(6px)}}to{{opacity:1;transform:none}}}}
.dots i{{display:inline-block;width:6px;height:6px;margin-right:4px;border-radius:50%;background:{PENCIL};animation:dot 1.2s ease-in-out infinite}}
.dots i:nth-child(2){{animation-delay:.15s}}.dots i:nth-child(3){{animation-delay:.3s}}
@keyframes dot{{0%,100%{{transform:translateY(0);opacity:.4}}50%{{transform:translateY(-4px);opacity:1}}}}
.veil{{position:absolute;inset:0;background:rgba(8,8,9,.7);z-index:60;animation:fadein .6s ease both}}
.nudge{{position:absolute;left:50%;top:50%;z-index:61;transform:translate(-50%,-50%);animation:nudge .9s cubic-bezier(.3,1.3,.5,1) .5s both}}
@keyframes nudge{{from{{opacity:0;transform:translate(-50%,-30%) rotate(-6deg)}}to{{opacity:1;transform:translate(-50%,-50%)}}}}
.waitdot{{width:7px;height:7px;border-radius:50%;background:#E08A3C;animation:wd 2.6s ease-out infinite}}
@keyframes wd{{0%{{box-shadow:0 0 0 0 rgba(224,138,60,.5)}}100%{{box-shadow:0 0 0 9px rgba(224,138,60,0)}}}}
.sway{{transform-origin:50% 0;animation:sway 6s ease-in-out infinite}}
@keyframes sway{{0%,100%{{transform:rotate(0)}}50%{{transform:rotate(1.2deg)}}}}
.pinned{{animation:pinned 1s cubic-bezier(.3,1.25,.5,1) var(--w,.6s) both}}
@keyframes pinned{{from{{opacity:0;transform:translateY(-22px) rotate(-5deg)}}to{{opacity:1;transform:none}}}}
.offst{{opacity:.75;transition:opacity .2s}}.offst:hover{{opacity:1}}
"""

def status_dot(text, color=PENCIL, dot='#E08A3C', size=11):
    return (f'<div style="display:flex;align-items:center;gap:8px;{TYPE};font-size:{size}px;letter-spacing:.14em;color:{color}">'
            f'<span class="waitdot" style="background:{dot}"></span>{text}</div>')

CONVO = [
    ("hey. I'm here. take your time, there's no rush.", False, '11:52'),
    ("I don't even know where to start honestly", True, '11:53'),
    ("that's okay. start anywhere. the middle is fine too.", False, '11:53'),
    ("my best friend moved away last month and I didn't realise how much of my week was just… her. tuesdays were chai after work, and on sundays she'd just show up at my door without texting first.", True, '11:55'),
    ("that sounds really lonely. like the shape of your days changed overnight, and nobody handed you a new one.", False, '11:56'),
]

CW, CH = 880, 724
def chat_sheet(extra_msgs='', tail=None, header='11:52 PM · YOU BOTH JOINED · NOTHING HERE IS SAVED', convo=CONVO):
    msgs = ''.join(line_msg(t, m, t=tt, i=i) for i, (t, m, tt) in enumerate(convo)) + extra_msgs
    tail = typing() if tail is None else tail
    inner = f"""<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.16) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">{header}</div>
<div class="scroll" style="flex-grow:1;min-height:0;display:flex;flex-direction:column;justify-content:flex-end;gap:20px;padding:18px 6px 14px;overflow:hidden">{msgs}{tail}</div>
<div style="border-top:1.5px dashed {RULE};padding-top:16px;display:flex;align-items:center;justify-content:space-between;gap:20px">
<span style="{SERIF};font-style:italic;font-size:19px;color:{PENCIL}">say it however it comes out…<span class="blink" style="color:{INK};font-style:normal">|</span></span>
<span style="display:flex;align-items:center;gap:22px;{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}"><span>ENTER TO SEND</span>{tchip('send ↗', '#', 'ink', 120, 54, 533)}</span></div>
</div>"""
    return paper(inner, CW, CH, rot=0.3, kind='hi', seed=534, pad='22px 34px 22px', tapes=tape(CW / 2 - 60, -14, 120, 30, rot=-2, seed=53))

def side_card(middle, status="THEY'RE LISTENING", h=532):
    return paper(f'''
<div style="{HAND};font-size:34px;line-height:1.2">you &amp; moss_byte</div>
<div style="margin-top:8px">{status_dot(status)}</div>
<div style="{MARK};font-size:23px;color:{RED};line-height:1.25;margin-top:18px;transform:rotate(-1.5deg)">no fixing. no judging.<br>you lead.</div>
<div style="border-top:1px dashed {RULE};margin-top:20px;padding-top:16px;display:grid;grid-template-columns:1fr auto;row-gap:10px;{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">
<span>CHECK-IN IN</span><span style="color:{INK}">3:48</span><span>KEPT</span><span style="color:{INK}">NOTHING</span></div>
{middle}''', 300, h, rot=-1.2, seed=521, pad='30px 30px', tapes=tape(100, -13, 100, 26, rot=-4, seed=52))

def pod_layout(side, sheet, crumb='talk pod', overlay='', under=''):
    return f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb=crumb)}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;gap:56px;padding:0 56px 24px">
<div class="rise" style="--w:.1s;padding-top:10px">{side}</div>
<div class="rise" style="--w:.3s;padding-top:8px">{sheet}{under}</div>
</main>{overlay}'''

# ================= V01 — you asked for voice =================
wait_note = f'''<div class="pinned" style="--w:.9s;position:relative;margin-top:22px;padding:16px 16px 14px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(.6deg)">
<div style="display:flex;align-items:center;gap:10px;color:{INK}">{ic(MIC, 18)}<span style="{HAND};font-size:24px;line-height:1">voice asked</span></div>
<div style="margin-top:10px">{status_dot('WAITING ON MOSS_BYTE', INK, size=10.5)}</div>
<div style="{SERIF};font-style:italic;font-size:15.5px;line-height:1.45;color:{PENCIL};margin-top:10px">Keep writing. Nothing starts unless you both say yes.</div>
<a href="V5Pod.dc.html" class="ul" style="display:inline-block;margin-top:10px;{TYPE};font-weight:700;font-size:11px;letter-spacing:.16em;color:{INK}">TAKE IT BACK</a></div>
<div style="display:flex;flex-direction:column;gap:14px;margin-top:22px">
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}</div>'''
v01_sheet = chat_sheet(sys_line('11:57 · you asked to talk by voice', 5) +
                       line_msg("no rush on that. what was your favourite tuesday with her?", False, t='11:57', i=6))
v01 = pod_layout(side_card(wait_note, h=600), v01_sheet)
page('V5VoiceWait', 'Voice asked, waiting', v01, css=POD_CSS)

# ================= V02 — they'd like to talk by voice =================
def fact_grid(rows, cols='150px 1fr', size=12):
    cells = ''.join(f'<span style="color:{PENCIL}">{k}</span><span style="color:{c}">{v}</span>' for k, v, c in rows)
    return f'<div style="display:grid;grid-template-columns:{cols};row-gap:10px;{TYPE};font-size:{size}px;letter-spacing:.1em;color:{INK}">{cells}</div>'

ask_card = paper(f'''
<div style="display:flex;align-items:center;justify-content:space-between">{t_mark('a small ask', 24)}<span style="color:{INK}">{ic(MIC, 22)}</span></div>
{h_hand('moss_byte would like<br>to talk by voice.', 46, color=INK, wait='1s', d='1.8s', extra='margin-top:6px')}
<div class="rise" style="--w:1.9s;{SERIF};font-size:20px;line-height:1.55;color:{INK};margin-top:14px">Only if you want to. Text is just as good, and you can come back to it any time.</div>
<div class="rise" style="--w:2.1s;margin-top:22px;padding-top:18px;border-top:1px dashed {RULE}">{fact_grid([('VOICE', 'PEER TO PEER · NEVER RECORDED', INK), ('YOUR MIC', 'ASKED ONLY AFTER YOU SAY YES', INK), ('KEPT', 'NOTHING', INK)])}</div>
<div class="rise" style="--w:2.4s;display:flex;align-items:center;gap:30px;margin-top:30px">{tchip('say yes', 'V5Call.dc.html', 'ink', 170, 54, 701)}
<a href="V5Pod.dc.html" class="ul" style="{TYPE};font-size:12px;letter-spacing:.16em;color:{INK}">KEEP IT TO TEXT</a></div>
<div class="rise" style="--w:2.7s;{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL};margin-top:20px">NO REASON NEEDED. THEY WON'T BE TOLD WHY.</div>''',
    600, 520, rot=-1, seed=702, pad='38px 46px', tapes=tape(245, -14, 110, 28, rot=3, seed=70))
v02_side = side_card(f'''<div style="display:flex;flex-direction:column;gap:14px;margin-top:24px">
{pod_btn('ask for voice', '#', MIC, 'ink', seed=561)}
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'kraft', seed=562)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}</div>''')
v02 = pod_layout(v02_side, chat_sheet(sys_line('11:57 · moss_byte asked to talk by voice', 5), tail=''),
                 overlay=f'<div class="veil"></div><div class="nudge">{ask_card}</div>')
page('V5VoiceAsk', 'They would like to talk by voice', v02, css=POD_CSS)

# ================= V03 — on voice =================
def _smooth(pts):
    """Catmull-Rom through pts -> cubic bezier path string (fixed command count)."""
    d = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[0]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[i + 2] if i + 2 < len(pts) else pts[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return d

def wave_frame(w, h, amp, r, n):
    mid = h / 2
    bumps = [(r.uniform(.12, .88), r.uniform(.06, .16), r.uniform(.45, 1)) for _ in range(r.randint(2, 4))]
    pts = []
    for i in range(n + 1):
        t = i / n
        env = sum(a * math.exp(-((t - c) / s) ** 2) for c, s, a in bumps)
        env = min(1, env) * math.sin(math.pi * t) ** .5
        y = mid + (-1) ** i * env * amp * r.uniform(.35, 1) + r.uniform(-1.2, 1.2)
        pts.append((t * w, y))
    return _smooth(pts)

def ink_wave(w, h, amp, seed, uid, color=INK, n=46, frames=8, step=.95, sw=2.6, muted=False):
    """A hand-drawn ink line that moves with speech. amp ~0 = quiet; muted = still dashed line."""
    if muted:
        return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
                f'<path d="M0 {h / 2} Q{w / 4} {h / 2 - 2} {w / 2} {h / 2} T{w} {h / 2}" fill="none" stroke="{color}" stroke-width="2" stroke-dasharray="2 7" stroke-linecap="round" opacity=".5"/></svg>')
    r = random.Random(seed)
    fr = [wave_frame(w, h, amp, r, n) for _ in range(frames)]
    vals = ';'.join(fr + [fr[0]])
    kt = ';'.join(f'{i / frames:.4f}' for i in range(frames + 1))
    ks = ';'.join(['.45 0 .55 1'] * frames)
    dur = frames * step
    anim = lambda begin: f'<animate attributeName="d" dur="{dur:.2f}s" begin="{begin}" repeatCount="indefinite" calcMode="spline" keyTimes="{kt}" keySplines="{ks}" values="{vals}"/>'
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="display:block;overflow:visible">'
            f'<defs><filter id="ink{uid}" x="-5%" y="-30%" width="110%" height="160%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="{seed % 97}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="2.6"/></filter></defs>'
            f'<g filter="url(#ink{uid})" fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="{fr[-2]}" stroke-width="{sw * .55:.1f}" opacity=".16">{anim(f"-{step * 2.5:.2f}s")}</path>'
            f'<path d="{fr[-1]}" stroke-width="{sw * .7:.1f}" opacity=".28">{anim(f"-{step * 1.2:.2f}s")}</path>'
            f'<path class="draw" style="--len:{w * 3};--d:1.6s;--w:.6s" d="{fr[0]}" stroke-width="{sw}">{anim("0s")}</path></g></svg>')

def lane(name, state, wave, color=INK, note=''):
    st_col = '#B0561F' if state.startswith('SPEAK') else PENCIL
    return (f'<div style="display:flex;flex-direction:column;gap:6px">'
            f'<div style="display:flex;align-items:baseline;justify-content:space-between"><span style="{HAND};font-size:34px;color:{color}">{name}</span>'
            f'<span style="{TYPE};font-size:10.5px;letter-spacing:.18em;color:{st_col}">{state}</span></div>{wave}{note}</div>')

call_sheet_inner = f'''
<div style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 29px,rgba(96,120,150,.12) 29px 30px);background-position:0 14px"></div>
<div style="position:relative;height:100%;display:flex;flex-direction:column">
<div style="{TYPE};font-size:10px;letter-spacing:.18em;color:{PENCIL};text-align:center;padding-bottom:12px;border-bottom:1px dashed {RULE}">11:58 PM · PEER TO PEER · NOT RECORDED</div>
<div style="flex-grow:1;display:flex;flex-direction:column;justify-content:center;gap:54px;padding:0 24px">
<div class="rise" style="--w:.5s">{lane('moss_byte', 'SPEAKING', ink_wave(760, 150, 58, 4101, 'a'))}</div>
<div style="border-top:1.5px dashed {RULE}"></div>
<div class="rise" style="--w:.8s">{lane('you', 'LISTENING', ink_wave(760, 110, 7, 4102, 'b', color=PENCIL, step=1.4, sw=2.2))}</div>
</div>
<div style="border-top:1.5px dashed {RULE};padding-top:16px;display:flex;align-items:center;justify-content:space-between">
<span style="{SERIF};font-style:italic;font-size:18px;color:{PENCIL}">Pauses are fine. So is talking over each other.</span></div></div>'''
call_sheet = paper(call_sheet_inner, CW, CH, rot=0.3, kind='hi', seed=534, pad='22px 34px 22px', tapes=tape(CW / 2 - 60, -14, 120, 30, rot=-2, seed=53))
call_side = paper(f'''
<div style="{HAND};font-size:34px;line-height:1.2">you &amp; moss_byte</div>
<div style="margin-top:8px">{status_dot('ON VOICE', INK)}</div>
<div style="{HAND};font-size:64px;line-height:1;color:{INK};margin-top:18px">03:41</div>
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL};margin-top:4px">14 MIN TOGETHER</div>
<div style="display:flex;flex-direction:column;gap:14px;margin-top:26px;padding-top:22px;border-top:1px dashed {RULE}">
{pod_btn('mute', '#', MIC, 'ink', seed=711)}
{pod_btn('back to text', 'V5Pod.dc.html', TEXTI, 'kraft', seed=712)}
{pod_btn('leave gently', 'V5PodEnd.dc.html', DOOR, 'paper', seed=713)}
{pod_btn('report · ends now', 'V5Reported.dc.html', FLAG, 'red')}</div>''',
    300, 530, rot=-1.2, seed=521, pad='30px 30px', tapes=tape(100, -13, 100, 26, rot=-4, seed=52))
call_under = f'<div class="rise" style="--w:2.4s;margin:14px 0 0 30px;{MARK};font-size:19px;color:{BOARDTXT};transform:rotate(-1deg)">the line only moves while someone speaks.</div>'
page('V5Call', 'On voice', pod_layout(call_side, call_sheet, under=call_under), css=POD_CSS)

# ================= R01 — open pod: pick a room =================
ROOMS = [  # name, theme, people, speakers, full?
    ("can't sleep club", 'for the 1am ceiling starers', 7, ['neon_moth', 'paper_kite']),
    ('first jobs', 'bosses, payslips, being new', 5, ['static_heron']),
    ('long distance', 'love, friends, family, far away', 10, ['dusk_signal', 'low_tide', 'amber_fox']),
    ('songs that hit', 'the one you replayed today', 8, ['velvet_crow', 'moss_byte']),
    ('overthinkers anonymous', 'loops, and how to step out', 6, ['lowkey_comet', 'fog_lamp']),
    ('night shift', 'awake for work, not by choice', 4, ['quiet_ember']),
    ('new in the city', 'finding your people again', 9, ['tin_sparrow', 'kite_runner']),
    ('small wins', 'say the tiny good thing out loud', 3, ['soft_static']),
    ('home, far away', 'missing a place you left behind', 10, ['salt_moon', 'grey_finch']),
    ('3am cricket talk', 'scores, rants, old matches', 7, ['bat_and_moth', 'deep_cover']),
]
def dots10(n, size=9, gap=5, full=False):
    out = ''
    for i in range(10):
        f = i < n
        col = PENCIL if full else INK
        out += (f'<svg width="{size}" height="{size}" viewBox="0 0 10 10" aria-hidden="true"><path d="M5 1.2 C7.6 1 9 2.8 8.8 5.1 C8.6 7.6 6.9 9 4.8 8.8 C2.4 8.6 1 6.9 1.2 4.8 C1.4 2.6 3 1.3 5 1.2Z" '
                f'fill="{col if f else "none"}" stroke="{col if f else PENCIL}" stroke-width="1.1" opacity="{1 if f else .6}"/></svg>')
    return f'<span role="img" aria-label="{n} of 10 people" style="display:inline-flex;gap:{gap}px">{out}</span>'

def mini_wave(seed, w=34, h=14, color='#B0561F'):
    return ink_wave(w, h, 5, seed, f'm{seed}', color=color, n=8, frames=5, step=.6, sw=1.6)

def stamp(text='full', size=30, rot=-12):
    return (f'<span aria-hidden="true" style="position:absolute;right:16px;top:44px;transform:rotate({rot}deg);padding:2px 12px;border:2.5px solid {PENCIL};border-radius:4px;'
            f'{TYPE};font-weight:700;font-size:{size * .55:.0f}px;letter-spacing:.26em;color:{PENCIL};opacity:.85;text-transform:uppercase;mix-blend-mode:multiply">{text}</span>')

def room_slip(i, name, theme, n, speakers, w=236, h=262, href='V5Room.dc.html'):
    full = n >= 10
    r = random.Random(900 + i)
    rot = r.uniform(-2.2, 2.2)
    kind = ['hi', '', 'kraft', 'hi', '', 'hi', 'kraft', '', 'hi', ''][i % 10]
    sp = ''.join(f'<div style="display:flex;align-items:center;gap:8px;{HAND};font-size:18px;line-height:1.35;color:{INK};white-space:nowrap">{name_}'
                 f'{mini_wave(950 + i * 7 + j) if j == 0 and not full else ""}</div>' for j, name_ in enumerate(speakers[:2]))
    more = f'<div style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">+{len(speakers) - 2} MORE</div>' if len(speakers) > 2 else ''
    inner = f'''<div style="display:flex;flex-direction:column;height:100%">
<div style="{HAND};font-size:26px;line-height:1.12;color:{INK};min-height:58px;padding-right:{70 if full else 0}px">{name}</div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.35;color:{PENCIL};margin-top:4px;min-height:40px">{theme}</div>
<div style="border-top:1px dashed {RULE};margin-top:10px;padding-top:9px;flex-grow:1">
<div style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL};margin-bottom:3px">ON STAGE</div>{sp}{more}</div>
<div style="display:flex;align-items:center;justify-content:space-between;gap:8px">{dots10(n, 8, 4, full)}
<span style="{TYPE};font-weight:700;font-size:11px;letter-spacing:.1em;color:{PENCIL if full else INK}">{n}/10</span></div></div>'''
    pin = (f'<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true" style="position:absolute;left:{w / 2 - 10:.0f}px;top:-6px;z-index:6;overflow:visible">'
           f'<ellipse cx="13" cy="15" rx="8" ry="4.5" fill="#000" opacity=".4"/><circle cx="10" cy="10" r="7.5" fill="{RED if i % 3 == 0 else "#3a3a3d"}"/>'
           f'<circle cx="10" cy="10" r="7.5" fill="none" stroke="#000" stroke-opacity=".35"/><circle cx="7.6" cy="7.6" r="2.2" fill="#fff" opacity=".28"/></svg>')
    decor = pin if i % 2 == 0 else tape(w / 2 - 44, -12, 88, 24, rot=r.uniform(-6, 6), seed=930 + i)
    slip = paper(inner + (stamp() if full else ''), w, h, rot=rot, kind=kind, seed=910 + i, pad='22px 22px 18px', tapes=decor,
                 extra='opacity:.62;filter:grayscale(.3) drop-shadow(0 14px 20px rgba(0,0,0,.5))' if full else '')
    label = f'{name}, {n} of 10{", full" if full else ""}'
    if full:
        return f'<div class="rise" style="--w:{.25 + i * .08:.2f}s" aria-label="{label}">{slip}</div>'
    return f'<a href="{href}" class="chip rise" style="--w:{.25 + i * .08:.2f}s;display:block" aria-label="{label}">{slip}</a>'

rooms_css = POD_CSS + """.rise.chip{animation:rise 1.1s cubic-bezier(.2,.7,.2,1) var(--w,.3s) forwards}"""
rooms_grid = ''.join(room_slip(i, *R, href='V5RoomHand.dc.html' if i == 3 else 'V5Room.dc.html') for i, R in enumerate(ROOMS))
rooms = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='open pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:4px 56px 0">
<div style="display:flex;align-items:flex-end;justify-content:space-between;gap:40px">
<div>{h_hand('Pick a room.', 58)}
<div class="rise" style="--w:1s;{SERIF};font-size:20px;color:{BOARDTXT};margin-top:2px">Themed voice rooms, up to 10 people. Speak if you like, or just listen.</div></div>
<div class="rise" style="--w:1.2s;display:flex;flex-direction:column;align-items:flex-end;gap:10px;padding-bottom:4px">
<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">25 ROOMS TONIGHT · 10 PINNED HERE</span>
{link('see all 25 →', '#', CHALK, 12)}</div></div>
<div style="display:grid;grid-template-columns:repeat(5,236px);justify-content:space-between;row-gap:22px;margin-top:24px">{rooms_grid}</div>
<div class="rise" style="--w:2s;display:flex;align-items:center;justify-content:center;gap:12px;margin-top:16px;{MARK};font-size:21px;color:{SOFTRED}">a seat opens when someone leaves.</div>
</main>
{footer()}'''
page('V5Rooms', 'Open pod, pick a room', rooms, css=rooms_css)

# ================= R02 / R03 — inside a room =================
def star(size=20, color=RED, uid='s'):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" aria-hidden="true" style="flex-shrink:0;overflow:visible">'
            f'<path d="M12 2.5 L14.6 9 L21.5 9.4 L16.2 13.8 L18 20.8 L12 16.9 L6.1 21 L7.7 14 L2.4 9.7 L9.3 9.1 Z" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round" '
            f'transform="rotate(-6 12 12)"/><path d="M11.8 7.5 L13 10.6 L16.4 10.9 L13.8 13 L14.6 16.4 L11.9 14.6 L9.2 16.4 L10 13 L7.5 10.9 L10.8 10.6 Z" fill="{color}" opacity=".85"/></svg>')

MOD_BADGE = lambda size=13: f'<span style="display:inline-flex;align-items:center;gap:4px;{TYPE};font-weight:700;font-size:{size * .75:.1f}px;letter-spacing:.16em;color:{INK}">{star(size, INK)}MOD</span>'

STAGE = [  # name, state, is_mod, is_you
    ('neon_moth', 'speaking', False, False),
    ('quiet_otter', 'listening', True, True),
    ('paper_kite', 'muted', False, False),
    ('dusk_signal', 'listening', True, False),
]
LISTENERS = ['static_heron', 'lowkey_comet', 'fog_lamp', 'amber_fox']

def speaker_tag(i, name, state, is_mod, me, mod_view, w=282, h=136):
    st_col = '#B0561F' if state == 'speaking' else PENCIL
    if state == 'speaking':
        wv = ink_wave(w - 56, 34, 13, 4200 + i, f'sp{i}', n=22, frames=7, step=.85, sw=2)
    elif state == 'muted':
        wv = f'<div style="display:flex;align-items:center;gap:8px;color:{PENCIL}">{ic(MICOFF, 14)}{ink_wave(w - 80, 34, 0, 0, "", muted=True, color=PENCIL)}</div>'
    else:
        wv = ink_wave(w - 56, 34, 2.5, 4200 + i, f'sp{i}', color=PENCIL, n=22, frames=6, step=1.4, sw=1.6)
    badge = MOD_BADGE() if is_mod else ''
    act = ''
    if mod_view and not me:
        act = f'<a href="#" class="ul offst" style="{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;color:{INK}">MOVE OFF STAGE</a>'
    elif me:
        act = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">YOU</span>'
    inner = f'''<div style="display:flex;align-items:center;gap:10px;white-space:nowrap"><span style="{HAND};font-size:25px;line-height:1.1;color:{INK}">{name}</span>{badge}</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin:4px 0 8px"><span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{st_col}">{state.upper()}</span>{act}</div>{wv}'''
    rot = [-1.2, .9, .6, -.8][i % 4]
    return f'<div class="rise" style="--w:{.4 + i * .12:.2f}s">{paper(inner, w, h, rot=rot, kind="hi" if i % 3 else "", seed=960 + i, pad="16px 20px")}</div>'

def listener_row(names, you_hand=None, hand_up=None):
    out = []
    for n in names:
        hand = f'<span style="color:{INK}">{ic(HANDI, 15)}</span>' if n in (you_hand, hand_up) else ''
        you = f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">YOU</span>' if n == you_hand else ''
        out.append(f'<span style="display:inline-flex;align-items:center;gap:6px;{HAND};font-size:21px;color:{INK}">{n}{hand}{you}</span>')
    return f'<div style="display:flex;flex-wrap:wrap;column-gap:26px;row-gap:6px">{"".join(out)}</div>'

def stage_sheet(mod_view, listeners, you_hand=None, hand_up=None, w=660, h=560):
    stage = [s for s in STAGE] if mod_view else [('neon_moth', 'speaking', False, False), ('paper_kite', 'muted', False, False), ('dusk_signal', 'listening', True, False), ('velvet_crow', 'listening', False, False)]
    tags = ''.join(speaker_tag(i, *s, mod_view=mod_view) for i, s in enumerate(stage))
    inner = f'''<div style="display:flex;align-items:baseline;justify-content:space-between;padding-bottom:10px;border-bottom:1px dashed {RULE}">
<span style="{HAND};font-size:30px;color:{INK}">on stage</span><span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">4 ON STAGE · MODS CHOOSE WHO COMES UP</span></div>
<div style="display:grid;grid-template-columns:repeat(2,282px);justify-content:space-between;row-gap:24px;margin-top:22px">{tags}</div>
<div style="margin-top:28px;padding-top:12px;border-top:1.5px dashed {RULE}">
<div style="display:flex;align-items:baseline;justify-content:space-between;margin-bottom:10px"><span style="{HAND};font-size:26px;color:{INK}">listening</span>
<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">{len(listeners)} HERE · 2 SEATS OPEN</span></div>
{listener_row(listeners, you_hand, hand_up)}</div>'''
    return paper(inner, w, h, rot=.4, kind='kraft', seed=971, pad='26px 30px', tapes=tape(w / 2 - 60, -14, 120, 30, rot=-2, seed=97))

def room_card(mod_view, h=650):
    if mod_view:
        you = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(-.6deg)">
<div style="display:flex;align-items:center;gap:10px">{star(24, INK, uid='b')}<span style="{HAND};font-size:23px;color:{INK};line-height:1">you're a mod here</span></div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:8px">Earned by being kind in rooms like this. You let people up, and help them down.</div></div>'''
        btns = f'''{pod_btn('mute', '#', MIC, 'ink', seed=721, w=230)}'''
    else:
        you = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(.5deg)">
<div style="display:flex;align-items:center;gap:10px;color:{INK}">{ic(HANDI, 20)}<span style="{HAND};font-size:23px;color:{INK};line-height:1.1">dusk_signal asked you up</span></div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:8px">Their note is on the right. Take your time.</div></div>'''
        btns = ''
    return paper(f'''
{t_mark('open pod', 22)}
<div style="{HAND};font-size:34px;line-height:1.15;margin-top:4px">can't sleep club</div>
<div style="{SERIF};font-style:italic;font-size:16px;color:{PENCIL};margin-top:2px">for the 1am ceiling starers</div>
<div style="display:flex;align-items:center;justify-content:space-between;margin-top:14px">{dots10(8, 9, 4)}<span style="{TYPE};font-weight:700;font-size:11px;letter-spacing:.1em">8/10</span></div>
{you}
<div style="display:flex;flex-direction:column;gap:14px;margin-top:22px">{btns}
{pod_btn('leave gently', 'V5Rooms.dc.html', DOOR, 'kraft', seed=722, w=230)}
{pod_btn('report someone', 'V5Reported.dc.html', FLAG, 'red')}</div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.12em;color:{PENCIL};line-height:1.6;margin-top:14px;text-wrap:balance">ONLY MODS LET HANDS UP OR MOVE SPEAKERS OFF STAGE. NEVER RECORDED.</div>''',
        290, h, rot=-1.2, seed=981, pad='28px 28px', tapes=tape(95, -13, 100, 26, rot=-4, seed=98))

hand_note = paper(f'''
<div style="display:flex;align-items:center;justify-content:space-between">{t_mark('a hand is up', 23)}<span style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL}">0:42</span></div>
<div style="display:flex;align-items:center;gap:12px;margin-top:12px"><span class="sway" style="display:inline-block;color:{INK}">{ic(HANDI, 34)}</span>
<span style="{HAND};font-size:29px;line-height:1.1;color:{INK}">lowkey_comet</span></div>
<div style="{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:12px">would like to come up and speak.</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:22px">{tchip('invite up', '#', 'ink', 150, 54, 731)}
<a href="#" class="ul" style="{TYPE};font-size:11.5px;letter-spacing:.16em;color:{INK}">NOT NOW</a></div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.13em;line-height:1.6;color:{PENCIL};margin-top:18px">THEY CHOOSE WHETHER TO COME UP. THEIR MIC IS ASKED ONLY THEN.</div>''',
    290, 380, rot=1.6, kind='hi', seed=991, pad='26px 26px', tapes=tape(90, -13, 104, 26, rot=4, red=True, seed=99))
queue_note = f'''<div class="rise" style="--w:1.6s;margin-top:26px;padding-left:10px">
<div style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{BOARDTXT}">NEXT HAND · STATIC_HERON</div>
<div style="{MARK};font-size:21px;color:#F0A08F;margin-top:10px;transform:rotate(-2deg);line-height:1.2">one at a time.<br>no one is rushed off.</div></div>'''

def room_page(mod_view):
    if mod_view:
        right = f'<div><div class="pinned" style="--w:1.1s">{hand_note}</div>{queue_note}</div>'
        stage = stage_sheet(True, LISTENERS, hand_up='lowkey_comet')
    else:
        invite = paper(f'''
<div style="display:flex;align-items:center;gap:8px">{star(20, INK, uid='i')}<span style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL}">FROM DUSK_SIGNAL · MOD</span></div>
{h_hand('come up?', 48, color=INK, wait='1.4s', d='1.2s', extra='margin-top:8px;white-space:nowrap')}
<div style="{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:6px">There's a seat on stage for you. Say as much or as little as you like.</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:22px">{tchip('come up', '#', 'ink', 140, 54, 741)}
<a href="#" class="ul" style="{TYPE};font-size:11.5px;letter-spacing:.16em;color:{INK}">NOT NOW</a></div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.13em;line-height:1.6;color:{PENCIL};margin-top:18px">YOUR MIC IS ASKED ONLY WHEN YOU SAY COME UP. STEP DOWN ANY TIME.</div>''',
            290, 370, rot=-1.8, kind='hi', seed=992, pad='26px 26px', tapes=tape(92, -13, 104, 26, rot=-3, red=True, seed=96))
        right = (f'<div><div class="pinned" style="--w:1.1s">{invite}</div>'
                 f'<div class="rise" style="--w:2s;margin-top:26px;padding-left:10px;{MARK};font-size:21px;color:{SOFTRED};transform:rotate(-2deg);line-height:1.2">no pressure.<br>listening is enough too.</div></div>')
        stage = stage_sheet(False, ['static_heron', 'quiet_otter', 'fog_lamp', 'amber_fox'], you_hand='quiet_otter')
    return f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='open pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;justify-content:space-between;align-items:center;padding:0 56px 30px">
<div class="rise" style="--w:.1s">{room_card(mod_view, h=624 if mod_view else 500)}</div>
<div class="rise" style="--w:.3s">{stage}</div>
<div style="padding-top:14px">{right}</div>
</main>
{footer()}'''

page('V5Room', 'Open pod room, mod view', room_page(True), css=POD_CSS)
page('V5RoomHand', 'Open pod room, invited to stage', room_page(False), css=POD_CSS)

# ---------- manifest (merged with the phone module's entries) ----------
DESK = [
    {"file": "V5VoiceWait.dc.html", "title": "V01 — You asked for voice", "w": 1440, "h": 900, "row": "voice"},
    {"file": "V5VoiceAsk.dc.html", "title": "V02 — They'd like to talk by voice", "w": 1440, "h": 900, "row": "voice"},
    {"file": "V5Call.dc.html", "title": "V03 — On voice", "w": 1440, "h": 900, "row": "voice"},
    {"file": "V5Rooms.dc.html", "title": "R01 — Open pod: pick a room", "w": 1440, "h": 900, "row": "rooms"},
    {"file": "V5Room.dc.html", "title": "R02 — In a room, mod view", "w": 1440, "h": 900, "row": "rooms"},
    {"file": "V5RoomHand.dc.html", "title": "R03 — Listener, invited to stage", "w": 1440, "h": 900, "row": "rooms"},
]
def write_manifest(entries):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'manifest_voice.json')
    cur = json.load(open(p)) if os.path.exists(p) else []
    files = {e['file'] for e in entries}
    cur = [e for e in cur if e['file'] not in files] + entries
    order = {'voice': 0, 'rooms': 1, 'm_voice': 2, 'm_rooms': 3}
    cur.sort(key=lambda e: order.get(e['row'], 9))  # stable: keeps V01..V03 order inside a row
    json.dump(cur, open(p, 'w'), indent=1)

if __name__ == '__main__':
    write_manifest(DESK)
    print('voice desktop ok')
