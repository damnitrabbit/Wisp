"""N0TRACE V5 desktop: S04 The rules (V5Terms) + S05 Notices and toasts (V5Notices).
Importing this module only defines the shared copy + helpers; boards are generated under __main__."""
from gen5 import *
import json, os

MANIFEST = 'manifest_capcare.json'
ORDER = ['V5MCapsule', 'V5MCapsuleSealed', 'V5MCapsuleOpen', 'V5MHelp', 'V5MReported', 'V5MPrivacy', 'V5MTerms', 'V5Terms', 'V5Notices']


def write_manifest(boards):
    cur = []
    if os.path.exists(MANIFEST):
        try: cur = json.load(open(MANIFEST))
        except Exception: cur = []
    mine = {b['file'] for b in boards}
    allb = [b for b in cur if b['file'] not in mine] + boards
    allb.sort(key=lambda b: ORDER.index(b['file'][:-8]) if b['file'][:-8] in ORDER else 99)
    json.dump(allb, open(MANIFEST, 'w'), indent=1)


# ---------- auto-height paper (deckle in px on x, % on y) ----------
def deckle_auto(w, amp=2.4, step=16, seed=1, rows=14):
    r = random.Random(seed)
    j = lambda a: r.uniform(-a, a)
    pts = []
    n = max(2, int(w / step))
    for i in range(n): pts.append(f'{w * i / n:.1f}px {abs(j(amp)):.1f}px')
    for i in range(rows): pts.append(f'calc({w:.0f}px + {j(amp):.1f}px) {100 * i / rows:.1f}%')
    for i in range(n): pts.append(f'{w - w * i / n:.1f}px calc(100% - {abs(j(amp)):.1f}px)')
    for i in range(rows): pts.append(f'{abs(j(amp)):.1f}px {100 - 100 * i / rows:.1f}%')
    return 'polygon(' + ','.join(pts) + ')'


def apaper(inner, w, rot=0, kind='', seed=1, pad='30px 34px', tapes='', extra=''):
    """A sheet whose height follows its content."""
    return (f'<div class="lift" style="position:relative;width:{w}px;transform:rotate({rot}deg);flex-shrink:0;{extra}">'
            f'<div class="paper {kind}" style="position:relative;padding:{pad};clip-path:{deckle_auto(w, seed=seed)}">{inner}</div>{tapes}</div>')


# ---------- the rules: one source of copy for desktop + phone ----------
CONTACT = 'damnitrabbit.build@gmail.com'
RULES = [
    dict(k='who', tag="WHO IT'S FOR", title='Grown-ups only.', big='18+',
         body=["N0TRACE is for adults, 18 and over.", "If you're younger, this isn't the place yet. Please don't pretend otherwise."],
         kind='kraft'),
    dict(k='kind', tag='BE KIND', title="Be the stranger you'd want to meet.",
         items=['Listen more than you fix.', "Don't ask for names, numbers or socials.", 'In open pods, let people finish.', 'Let people leave. Leaving is always okay.'],
         kind='hi'),
    dict(k='removed', tag='WHAT GETS YOU REMOVED', title='These close your door.',
         items=['Threats, hate or harassment.', 'Anything sexual.', "Asking for or sharing anyone's personal details.", 'Selling, spamming or recruiting.', 'Pretending to be a counsellor or doctor.'],
         note='not sure? if you wouldn\'t say it to their face, don\'t.', kind=''),
    dict(k='reports', tag='REPORTS', title='One tap. No questions.',
         body=['Report ends the pod instantly. They only see that it closed, never who or why.',
               "2–3 reports close someone's door for the night. A report is a count, gone by morning."],
         kind='kraft'),
    dict(k='keep', tag='WHAT WE KEEP', title='Nothing.', circle=True,
         body=['No account. A new name every visit. Pod messages are never stored. Echoes fade in 24 hours. Your capsule stays in your browser.',
               "Email only if you ask, and only for Tonight's Question or your capsule."],
         link=('the full receipt →', 'Privacy'), kind='hi'),
    dict(k='voice', tag='VOICE', title='Voice is just you two.',
         body=['A 1:1 starts as text. Voice only happens if you both say yes.',
               "It goes peer to peer, straight between you. We never record it. We can't stop the other person from doing so, so share what feels okay."],
         kind=''),
    dict(k='heavy', tag="WHEN IT'S HEAVY", title="We're strangers, not a crisis line.",
         body=['If you might hurt yourself or someone else, please talk to someone trained. They pick up at any hour.'],
         link=('need help now →', 'Help'), red=True, kind=''),
    dict(k='who_made', tag='WHO MADE THIS', title='Damn_It_Rabbit.',
         body=['One person, building this at night. Questions, bugs, or something we got wrong? Write in. A human reads it.'],
         contact=True, kind='kraft'),
]


def rule_inner(rl, scale=1.0, pre='V5'):
    s = lambda v: f'{v * scale:.1f}'
    out = [f'<div style="{TYPE};font-size:{s(10.5)}px;letter-spacing:.18em;color:{RED if rl.get("red") else PENCIL}">{rl["tag"]}</div>']
    if rl.get('big'):
        out.append(f'<div style="display:flex;align-items:baseline;gap:{s(14)}px;margin-top:{s(4)}px"><span style="{HAND};font-size:{s(76)}px;line-height:1;color:{INK}">{rl["big"]}</span>'
                   f'<span style="{HAND};font-size:{s(28)}px;line-height:1.2;color:{INK}">{rl["title"]}</span></div>')
    elif rl.get('circle'):
        out.append(f'<div style="position:relative;display:inline-block;margin-top:{s(16)}px;margin-bottom:{s(4)}px;padding:0 {s(10)}px;{HAND};font-size:{s(44)}px;line-height:1.15;color:{INK}">'
                   f'{circle_scribble(int(215 * scale), int(80 * scale), RED, wait="1.6s")}{rl["title"]}</div>')
    else:
        out.append(f'<div style="{HAND};font-size:{s(30)}px;line-height:1.2;color:{INK};margin-top:{s(6)}px">{rl["title"]}</div>')
    for p in rl.get('body', []):
        out.append(f'<p style="{SERIF};font-size:{s(17)}px;line-height:1.55;color:{INK};margin:{s(10)}px 0 0">{p}</p>')
    if rl.get('items'):
        lis = ''.join(f'<li style="display:flex;gap:{s(12)}px;align-items:baseline;padding:{s(7)}px 0;border-bottom:1px dashed {RULE}">'
                      f'<span style="{HAND};font-size:{s(18)}px;color:{RED};flex-shrink:0">{"×" if rl["k"] == "removed" else "·"}</span>'
                      f'<span style="{SERIF};font-size:{s(17)}px;line-height:1.45;color:{INK}">{t}</span></li>' for t in rl['items'])
        out.append(f'<ul style="list-style:none;margin:{s(12)}px 0 0;padding:0;border-top:1px dashed {RULE}">{lis}</ul>')
    if rl.get('note'):
        out.append(f'<div style="{MARK};font-size:{s(21)}px;line-height:1.15;color:{RED};margin-top:{s(12)}px;transform:rotate(-1.5deg);transform-origin:left">{rl["note"]}</div>')
    if rl.get('link'):
        lab, tgt = rl['link']
        out.append(f'<div style="margin-top:{s(14)}px"><a href="{pre}{tgt}.dc.html" class="ul" style="{TYPE};font-weight:700;font-size:{s(11.5)}px;letter-spacing:.16em;text-transform:uppercase;color:{RED if rl.get("red") else INK}">{lab}</a></div>')
    if rl.get('contact'):
        out.append(f'<div style="margin-top:{s(14)}px;display:flex;align-items:center;gap:{s(14)}px;border-top:1px dashed rgba(34,30,26,.25);padding-top:{s(14)}px">'
                   f'{rabbit(int(44 * scale), INK, uid="rl" + pre, blink=False)}'
                   f'<a href="mailto:{CONTACT}" class="ul" style="{TYPE};font-weight:700;font-size:{s(13)}px;letter-spacing:.1em;color:{INK}">{CONTACT}</a></div>')
    return ''.join(out)


R = {rl['k']: rl for rl in RULES}

# ---------- notices: one source of copy ----------
# icons: 20x20 hand-drawn glyphs, stroke currentColor
IC = {
    'door': '<path d="M5 18V3h8v15M3 18h14M10.5 10.5h.01" /><path d="M13 5l3 1v12"/>',
    'ask': '<path d="M3 5h11v7H8l-3 3v-3H3z"/><path d="M16 8c1.4 1 1.4 3 0 4"/>',
    'no': '<path d="M3 5h11v7H8l-3 3v-3H3z"/><path d="M7 7l3 3M10 7l-3 3"/>',
    'mic': '<rect x="7.5" y="2.5" width="5" height="9" rx="2.5"/><path d="M4.5 9.5a5.5 5.5 0 0 0 11 0M10 15v3M7 18h6"/>',
    'mute': '<rect x="7.5" y="2.5" width="5" height="9" rx="2.5"/><path d="M4.5 9.5a5.5 5.5 0 0 0 11 0M10 15v3M7 18h6M3 3l14 14"/>',
    'loop': '<path d="M16 7a6.5 6.5 0 0 0-11.5 1M4 13a6.5 6.5 0 0 0 11.5-1"/><path d="M16 3v4h-4M4 17v-4h4"/>',
    'tick': '<path d="M3.5 10.5l4 4 9-10"/>',
    'full': '<circle cx="6" cy="6.5" r="2.3"/><circle cx="14" cy="6.5" r="2.3"/><path d="M2 16c0-3 2-4.5 4-4.5s4 1.5 4 4.5M10 16c0-3 2-4.5 4-4.5s4 1.5 4 4.5"/>',
    'down': '<path d="M3 4h14M10 7v10M6 13l4 4 4-4"/>',
    'hand': '<path d="M6.5 11V5a1.3 1.3 0 0 1 2.6 0v4.5M9.1 9V3.5a1.3 1.3 0 0 1 2.6 0V9M11.7 9V4.5a1.3 1.3 0 0 1 2.6 0V11c0 4-2 6.5-5 6.5-2.3 0-3.5-1.4-4.5-3.5l-1.4-3a1.2 1.2 0 0 1 2-1.2l1.5 2"/>',
    'flag': '<path d="M4.5 18V3M4.5 3.5h10l-2 3.5 2 3.5h-10"/>',
    'clock': '<circle cx="10" cy="10" r="7"/><path d="M10 6v4l3 2"/>',
    'seal': '<rect x="2.5" y="5" width="15" height="11" rx="1"/><path d="M2.5 5.5l7.5 6 7.5-6"/><circle cx="10" cy="11.5" r="2.2" fill="currentColor" stroke="none"/>',
    'pin': '<path d="M7 3h6l-1 5 3 3H5l3-3z M10 11v7"/>',
    'ear': '<path d="M6 8a4.5 4.5 0 0 1 9 0c0 3-3 3.5-3 6.5a2.5 2.5 0 0 1-4.5 1.5"/><path d="M9 8a1.5 1.5 0 0 1 3 0c0 1-1 1.5-1.5 2"/>',
    'flame': '<path d="M10 18c-3.3 0-5.5-2.3-5.5-5.3 0-3.2 2.7-4.6 3.3-8.2 2.2 1.4 3 3.4 2.7 5.3 1-.5 1.6-1.5 1.8-2.6 1.7 1.4 3.2 3.2 3.2 5.5 0 3-2.2 5.3-5.5 5.3z"/>',
}


def icon(k, size=20, color=INK):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 20 20" aria-hidden="true" style="flex-shrink:0;color:{color}">'
            f'<g fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{IC[k]}</g></svg>')


# tone: paper (it happened), kraft (in progress / waiting), ink (live state that stays), red (care + safety)
NOTICES = [
    ('In a 1:1 pod', [
        dict(ev='They left the pod', ic='door', msg='moss_byte left the pod.', sub='that\'s okay. stay, or go.', tone='paper', life='STAYS'),
        dict(ev='Voice request sent', ic='ask', msg='asked to switch to voice.', sub='waiting on them…', tone='kraft', life='UNTIL THEY ANSWER'),
        dict(ev='Voice request declined', ic='no', msg='they\'d rather type.', sub='no hard feelings.', tone='paper', life='4S'),
        dict(ev="You're on voice", ic='mic', msg='you\'re on voice.', sub='peer to peer · never recorded', tone='ink', life='STAYS WHILE LIVE'),
    ]),
    ('In an open pod', [
        dict(ev='Room is full', ic='full', msg='this room is full.', sub='10 of 10 · try another', tone='kraft', life='4S'),
        dict(ev='Your hand is up', ic='hand', msg='your hand is up.', sub='a mod will see it', tone='kraft', life='STAYS'),
        dict(ev='Moved off stage', ic='down', msg='you\'re listening now.', sub='a mod moved you off stage', tone='paper', life='5S'),
        dict(ev='Mic muted', ic='mute', msg='mic muted.', sub='no one can hear you', tone='ink', life='STAYS WHILE MUTED'),
    ]),
    ('Connection + care', [
        dict(ev='Reconnecting', ic='loop', msg='reconnecting…', sub='hold on, nothing is lost', tone='kraft', life='UNTIL BACK', spin=True),
        dict(ev='Back online', ic='tick', msg='you\'re back.', sub='right where you left off', tone='paper', life='3S'),
        dict(ev='Report sent', ic='flag', msg='reported. pod closed.', sub='you did the right thing.', tone='red', life='STAYS'),
        dict(ev='Pods closing', ic='clock', msg='pods close in 10 min.', sub='say what you need to say', tone='kraft', life='6S'),
    ]),
    ('On your own', [
        dict(ev='Capsule sealed', ic='seal', msg='sealed.', sub='it opens on 15 oct', tone='paper', life='4S', seal=True),
        dict(ev='Echo pinned', ic='pin', msg='pinned to the wall.', sub='it fades in 24 hours', tone='paper', life='4S'),
        dict(ev='Echo heard', ic='ear', msg='someone heard your echo.', sub='', tone='hi', life='4S'),
        dict(ev='Burnt', ic='flame', msg='burnt. it\'s gone.', sub='nothing kept', tone='paper', life='3S', burnt=True),
    ]),
]


def toast(n, w=300, seed=1, rot=0, scale=1.0, cls=''):
    tone = n['tone']
    bg = {'paper': PAPER, 'hi': PAPERHI, 'kraft': KRAFT, 'ink': INK, 'red': PAPERHI}[tone]
    fg = PAPERHI if tone == 'ink' else INK
    sub_c = '#A9A39A' if tone == 'ink' else PENCIL
    ic_c = RED if tone == 'red' or n.get('burnt') else ('#E9B07A' if tone == 'ink' else INK)
    s = lambda v: f'{v * scale:.1f}'
    h = 66 if n['sub'] else 54
    h = int(h * scale)
    spin = ' class="spin"' if n.get('spin') else ''
    live = (f'<span class="livedot" style="width:{s(6)}px;height:{s(6)}px;border-radius:50%;background:#E08A3C;flex-shrink:0;margin-left:auto"></span>'
            if tone == 'ink' else '')
    sub = f'<span style="{TYPE};font-size:{s(9.5)}px;letter-spacing:.12em;text-transform:uppercase;color:{sub_c};white-space:nowrap">{n["sub"]}</span>' if n['sub'] else ''
    redbar = f'<span style="position:absolute;left:0;top:0;bottom:0;width:{s(4)}px;background:{RED};opacity:.85"></span>' if tone == 'red' else ''
    char = (f'<svg width="{w}" height="12" viewBox="0 0 {w} 12" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;left:0;bottom:0">'
            f'<path d="M0 12 V6 ' + ' '.join(f'L{x} {random.Random(seed + x).uniform(2, 10):.1f}' for x in range(0, w + 1, 9)) + f' V12 Z" fill="#2a2016" opacity=".55"/></svg>') if n.get('burnt') else ''
    inner = (f'<span class="paper" style="position:absolute;inset:0;background-color:{bg};clip-path:{deckle(w, h, amp=1.6, step=12, seed=seed)}">{redbar}{char}</span>'
             f'<span style="position:relative;display:flex;align-items:center;gap:{s(12)}px;width:100%;padding:0 {s(14)}px 0 {s(14 + (4 if tone == "red" else 0))}px">'
             f'<span{spin} style="display:flex">{icon(n["ic"], int(20 * scale), ic_c)}</span>'
             f'<span style="display:flex;flex-direction:column;gap:{s(1)}px;min-width:0"><span style="{HAND};font-size:{s(19)}px;line-height:1.15;color:{fg};white-space:nowrap">{n["msg"]}</span>{sub}</span>{live}</span>')
    return (f'<div class="lift {cls}" role="status" style="position:relative;display:flex;align-items:center;width:{w}px;height:{h}px;transform:rotate({rot}deg);color:{fg}">{inner}</div>')


NOTICE_CSS = """
.spin svg{animation:spin 2.4s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}
.livedot{animation:ld 2.4s ease-out infinite}@keyframes ld{0%{box-shadow:0 0 0 0 rgba(224,138,60,.55)}100%{box-shadow:0 0 0 7px rgba(224,138,60,0)}}
.slidein{opacity:0;animation:slidein .7s cubic-bezier(.2,.8,.2,1) var(--w,.3s) forwards}
@keyframes slidein{from{opacity:0;transform:translateY(14px) rotate(var(--r,0deg))}to{opacity:1;transform:rotate(var(--r,0deg))}}
"""


if __name__ == '__main__':
    BOARDS = []

    # =================================================================
    # S04 — The rules, in plain words (desktop, scrolls)
    # =================================================================
    TH = 1780
    def sheet(k, w, rot, seed, tseed, tx=None, tred=False, pad='30px 34px 32px'):
        rl = R[k]
        tp = tape((tx if tx is not None else w / 2 - 50), -13, 100, 26, rot=random.Random(tseed).choice([-4, -2, 3, 5]), seed=tseed, red=tred)
        return apaper(rule_inner(rl), w, rot=rot, kind=rl['kind'], seed=seed, pad=pad, tapes=tp)

    terms = f'''
{atmos(w=1440, h=TH)}
{topbar(crumb='the rules')}
<main style="position:relative;z-index:10;flex-grow:1;padding:20px 120px 0">
<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:60px">
<div style="width:640px;padding-top:30px">
{h_hand('The rules, in plain words.', 66, d='2s')}
<div class="rise" style="--w:1.2s;{SERIF};font-size:21px;line-height:1.6;color:{ASH};margin-top:18px;max-width:560px">Short on purpose. N0TRACE works because strangers are gentle with each other. If something here isn't clear, that's on us.</div>
<div class="rise" style="--w:1.5s;{TYPE};font-size:11px;letter-spacing:.16em;color:#6A6A70;margin-top:22px">8 NOTES · 2 MINUTES · LAST CHANGED OCTOBER 2026</div>
</div>
<div class="rise" style="--w:.5s;margin-top:34px;margin-right:30px">{sheet('who', 440, 2.2, 1701, 171)}</div>
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:56px;margin-top:70px;align-items:start">
<div style="display:flex;flex-direction:column;gap:56px;align-items:center">
<div class="rise" style="--w:.7s">{sheet('kind', 370, -1.6, 1702, 172)}</div>
<div class="rise" style="--w:1s">{sheet('reports', 360, 1.4, 1703, 173)}</div>
</div>
<div style="display:flex;flex-direction:column;gap:56px;align-items:center;padding-top:46px">
<div class="rise" style="--w:.8s">{sheet('removed', 370, 1, 1704, 174, tred=True)}</div>
<div class="rise" style="--w:1.1s">{sheet('voice', 360, -1.2, 1705, 175)}</div>
</div>
<div style="display:flex;flex-direction:column;gap:56px;align-items:center;padding-top:10px">
<div class="rise" style="--w:.9s">{sheet('keep', 370, -.8, 1706, 176)}</div>
<div class="rise" style="--w:1.2s">{sheet('heavy', 360, 1.6, 1707, 177)}</div>
</div>
</div>
<div style="display:flex;justify-content:center;align-items:center;gap:70px;margin-top:70px">
<div class="rise" style="--w:1.3s">{sheet('who_made', 520, -1, 1708, 178)}</div>
<div class="rise" style="--w:1.5s;display:flex;flex-direction:column;gap:14px;max-width:300px">
<div style="{HAND};font-size:28px;line-height:1.3;color:{CHALK}">That's all of it. Now go be kind to a stranger.</div>
<div style="display:flex;gap:28px;margin-top:6px">{link('← home', 'V5Home.dc.html', size=12)}{link('what we keep', 'V5Privacy.dc.html', size=12)}</div></div>
</div>
</main>
{footer()}'''
    page('V5Terms', 'The rules', terms, h=TH)
    BOARDS.append({"file": "V5Terms.dc.html", "title": "S04 — The rules, in plain words (scrolls)", "w": 1440, "h": TH, "row": "care"})

    # =================================================================
    # S05 — Notices and toasts (reference sheet)
    # =================================================================
    NH = 1400
    cols = []
    sd = 1800
    for ci, (grp, items) in enumerate(NOTICES):
        rows = []
        for i, n in enumerate(items):
            sd += 1
            rot = [-.8, .6, -.4, .9, -.6][(ci + i) % 5]
            rows.append(f'<div class="slidein" style="--w:{.4 + ci * .15 + i * .12:.2f}s;display:flex;flex-direction:column;gap:10px">'
                        f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:10px;letter-spacing:.16em;text-transform:uppercase"><span style="color:{CHALK}">{n["ev"]}</span><span style="color:#6A6A70">{n["life"]}</span></div>'
                        f'{toast(n, 280, seed=sd, rot=rot)}</div>')
        cols.append(f'<section style="display:flex;flex-direction:column;gap:30px">'
                    f'<div style="{MARK};font-size:26px;color:#F0A08F;border-bottom:1px dashed {SOOT};padding-bottom:10px">{grp.lower()}</div>{"".join(rows)}</section>')

    def tone_key(tone, label, note):
        n = dict(ev='', ic={'paper': 'tick', 'kraft': 'loop', 'ink': 'mic', 'red': 'flag'}[tone], msg=label, sub='', tone=tone, life='')
        return (f'<div style="display:flex;flex-direction:column;gap:10px">{toast(n, 230, seed={'paper': 1881, 'kraft': 1882, 'ink': 1883, 'red': 1884}[tone], scale=.95)}'
                f'<div style="{SERIF};font-size:15px;line-height:1.45;color:{ASH};max-width:230px">{note}</div></div>')

    # anatomy: one big slip, annotated
    big = dict(ev='', ic='door', msg='moss_byte left the pod.', sub="that's okay. stay, or go.", tone='paper', life='')
    anatomy = f'''
<div style="position:relative;width:100%;height:206px">
<div style="position:absolute;left:10px;top:6px;display:flex;align-items:flex-end;gap:6px"><span style="{HAND};font-size:18px;color:{CHALK}">what happened, in the app's voice</span>{arrow_doodle(46, 34, ASH, wait='1.6s')}</div>
<div style="position:absolute;right:0;top:6px;display:flex;align-items:flex-end;gap:6px"><span style="display:block;transform:scaleX(-1)">{arrow_doodle(46, 34, ASH, wait='1.8s')}</span><span style="{HAND};font-size:18px;color:{CHALK}">a fact, or what you can do</span></div>
<div class="slidein" style="--w:.3s;position:absolute;left:50%;top:58px;margin-left:-250px">{toast(big, 500, seed=1890, rot=-1, scale=1.45)}</div>
<div style="position:absolute;left:60px;top:172px;{HAND};font-size:18px;color:{CHALK}">↑ a drawn icon, never colour alone</div>
<div style="position:absolute;right:90px;top:172px;{HAND};font-size:18px;color:{CHALK}">torn paper, no tape ↑</div>
</div>'''
    rules_li = ''.join(f'<li style="display:flex;gap:12px;padding:9px 0;border-bottom:1px dashed {SOOT}"><span style="{TYPE};font-size:11px;letter-spacing:.14em;color:#6A6A70;width:22px">{i:02d}</span>'
                       f'<span style="{SERIF};font-size:16.5px;line-height:1.45;color:{CHALK}">{t}</span></li>'
                       for i, t in enumerate(['Lowercase, short, kind. One line, then a smaller fact.', 'Desktop: bottom centre. Phone: just under the header.',
                                              'Two at most on screen. The newest sits on top.', 'Live states stay until they change. Everything else fades in 3 to 6 seconds.',
                                              'Tap to dismiss. Nothing needs an OK.', 'No exclamation marks, no emoji, no sounds.'], 1))
    notices = f'''
{atmos(w=1440, h=NH)}
{topbar(crumb='notices')}
<main style="position:relative;z-index:10;flex-grow:1;padding:16px 96px 0">
<div style="display:flex;justify-content:space-between;align-items:flex-end;gap:60px">
<div style="width:560px;flex-shrink:0">{h_hand('Notices and toasts.', 62, d='1.8s', extra='white-space:nowrap')}
<div class="rise" style="--w:1s;{SERIF};font-size:20px;line-height:1.55;color:{ASH};margin-top:14px">Every little slip N0TRACE hands you. They say what happened, then get out of the way.</div></div>
<div class="rise" style="--w:1.2s;display:grid;grid-template-columns:repeat(2,230px);gap:22px 34px;padding-bottom:4px">
{tone_key('paper', 'it happened', 'Paper. Something finished.')}
{tone_key('kraft', 'in progress', 'Kraft. Waiting on someone or something.')}
{tone_key('ink', 'live right now', 'Ink. A state that stays while it is true.')}
{tone_key('red', 'care + safety', 'Red ink. Reports and help.')}
</div>
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:38px;margin-top:58px">{"".join(cols)}</div>
<div style="display:grid;grid-template-columns:1fr 440px;gap:60px;margin-top:66px;align-items:center;border-top:1px dashed {SOOT};padding-top:40px">
<div>{t_type('anatomy of a slip', 11, ASH, extra='margin-bottom:6px')}{anatomy}</div>
<div>{t_type('how they behave', 11, ASH, extra='margin-bottom:10px')}<ol style="list-style:none;margin:0;padding:0;border-top:1px dashed {SOOT}">{rules_li}</ol></div>
</div>
</main>
{footer()}'''
    page('V5Notices', 'Notices and toasts', notices, h=NH, css=NOTICE_CSS)
    BOARDS.append({"file": "V5Notices.dc.html", "title": "S05 — Notices and toasts", "w": 1440, "h": NH, "row": "care"})

    write_manifest(BOARDS)
    print('legal ok')
