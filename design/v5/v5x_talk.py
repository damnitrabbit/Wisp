"""N0TRACE V5 desktop: new talk boards. T07 V5Listener, T08 V5Requeue, T09 V5Paused."""
from gen5 import *
import v5_live as LV
from v5m_talk import (board, write_manifest, thread_loader, you_note, closed_sign, SIGN_CSS, LRED, SOFTRED, tchip)
import gen5 as _g
_pg = _g.page; _g.page = lambda *a, **k: None   # borrow the scrap atom without rewriting v5_talk's boards
from v5_talk import mini_scrap
_g.page = _pg

# =====================================================================
# T07 — Before you listen
# =====================================================================
def promise(n, title, line, last=False):
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    return (f'<div style="display:flex;gap:20px;padding:16px 0;{bb}">'
            f'<span style="{MARK};font-size:32px;line-height:1;color:{RED};width:20px;flex-shrink:0">{n}</span>'
            f'<div><div style="{HAND};font-size:31px;line-height:1.15;color:{INK}">{title}</div>'
            f'<div style="{SERIF};font-size:18px;line-height:1.5;color:{PENCIL};margin-top:4px">{line}</div></div></div>')
promises = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('three small promises', 25)}<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">LISTEN POD</span></div>
<div style="margin-top:6px">
{promise('1', 'No fixing.', "They don't need a plan. They need someone there.")}
{promise('2', 'No judging.', 'Whatever they say, it stays small and safe here.')}
{promise('3', 'Let them lead.', 'Ask, follow, leave room for quiet.', True)}</div>''',
    490, 384, rot=-1.2, kind='hi', seed=1701, pad='32px 38px 22px', tapes=tape(190, -14, 110, 28, rot=2, seed=170))
heavy = paper(f'''
<div style="{HAND};font-size:30px;line-height:1.2;color:{INK}">If it gets heavy</div>
<div style="{SERIF};font-size:17.5px;line-height:1.55;color:{INK};margin-top:10px">You're a kind stranger, not a professional. If they might be in danger, share the helpline with them. You can leave gently any time.</div>
<a href="V5Help.dc.html" class="ul" style="display:inline-block;margin-top:16px;{TYPE};font-weight:700;font-size:12px;letter-spacing:.14em;color:{RED}">HELPLINES, ONE CLICK AWAY →</a>''',
    360, 270, rot=1.6, kind='kraft', seed=1702, pad='30px 32px', tapes=tape(130, -13, 100, 26, rot=-4, seed=171))
listener = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='listen pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:56px;padding:0 56px 50px">
<div style="width:340px;display:flex;flex-direction:column;gap:20px">
{h_hand('Before you listen.', 56, d='1.8s')}
<div class="rise" style="--w:1.1s;{SERIF};font-size:20px;line-height:1.6;color:{BOARDTXT}">Someone out there needs to be heard tonight. You don't need the right words. Just stay.</div>
<div class="rise" style="--w:1.8s;display:flex;align-items:center;gap:30px;margin-top:22px">{tchip("I'm ready", 'V5Matching.dc.html', 'ink', 180, 54, 1703)}{link('not tonight', 'V5Home.dc.html')}</div>
<div class="rise" style="--w:2.1s;{TYPE};font-size:11px;letter-spacing:.14em;line-height:1.7;color:{BOARDTXT};margin-top:8px;text-wrap:balance">STARTS AS TEXT · VOICE ONLY IF YOU BOTH SAY YES</div></div>
<div class="rise" style="--w:.5s">{promises}</div>
<div class="rise" style="--w:1.2s;margin-top:170px">{heavy}</div>
</main>
{footer()}'''
page('V5Listener', 'Before you listen', listener)
board('V5Listener', 'T07 — Before you listen', 900, 'talk', 1440)

# =====================================================================
# T08 — They left. Finding someone new.
# =====================================================================
rq_listeners = [(300, 40, -4, 741), (432, 130, 3, 742), (296, 186, -2, 743)]
rq_html, rq_css = thread_loader('d', 520, 290, (176, 150), (20, 46, 176, 128, -3), you_note(size=34, pad='28px 22px'), rq_listeners, slip=(112, 90), cycle=8.4, k=50)
left_note = paper(f'''
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">11:58 PM</div>
<div style="position:relative;display:inline-block;margin-top:8px;{HAND};font-size:30px;color:{INK}">moss_byte left the pod
<svg width="100%" height="12" viewBox="0 0 300 12" preserveAspectRatio="none" aria-hidden="true" style="position:absolute;left:0;top:34%;overflow:visible"><path class="draw" style="--len:330;--w:.9s;--d:.8s" d="M2 7 Q80 2 150 6 T298 5" fill="none" stroke="{PENCIL}" stroke-width="2.4" stroke-linecap="round"/></svg></div>
<div style="{SERIF};font-size:19px;line-height:1.6;color:{INK};margin-top:14px">It wasn't you. People leave for all kinds of reasons: a bad signal, a long day, a knock on the door.</div>
<div style="{TYPE};font-size:10.5px;letter-spacing:.14em;color:{PENCIL};margin-top:16px">THE CHAT IS WIPED · NOTHING KEPT</div>''',
    480, 252, rot=-1.4, kind='hi', seed=1711, pad='34px 40px', torn='bottom', tapes=tape(185, -14, 110, 28, rot=-2, seed=172))
requeue = f'''
{atmos()}
{topbar(right='PODS OPEN · UNTIL 2AM', crumb='talk pod')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:90px;padding-bottom:40px">
<div style="display:flex;flex-direction:column;gap:30px">
{h_hand('They left.', 72)}
<div class="rise" style="--w:.6s">{left_note}</div></div>
<div style="display:flex;flex-direction:column;gap:6px;width:520px">
<div class="rise" style="--w:1.4s">{t_mark('finding someone new', 30, SOFTRED)}
<div style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT};margin-top:6px">ALREADY LOOKING · USUALLY UNDER A MINUTE</div></div>
<div class="fadein" style="--w:1.8s;margin-top:10px">{rq_html}</div>
<div class="rise" style="--w:2.2s;display:flex;flex-direction:column;gap:12px;margin-top:4px">
<div style="{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">NEED A MINUTE FIRST? LET IT GO ANOTHER WAY · ON YOUR OWN</div>
<div style="display:grid;grid-template-columns:repeat(2,222px);gap:12px 14px">{mini_scrap('get it out', 'BURN', 'V5Burn.dc.html', -1.5, 1781)}{mini_scrap('leave it somewhere', 'ECHOES', 'V5Echoes.dc.html', 1.2, 1782, 'kraft')}{mini_scrap("write it, don't send", 'UNSENT', 'V5UnsentWrite.dc.html', .8, 1783, 'kraft')}{mini_scrap('hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', -1, 1784)}</div>
<div style="margin-top:4px">{link('stop looking', 'V5Home.dc.html')}</div></div></div>
</main>
{footer()}'''
page('V5Requeue', 'They left, finding someone new', requeue, css=rq_css)
LV.mark('V5Requeue', replace=[('11:58 PM', '{{leftAt}}')])
board('V5Requeue', 'T08 — They left. Finding someone new', 900, 'talk', 1440)

# =====================================================================
# T09 — Pods closed for you tonight
# =====================================================================
def scrap_link(text, feat, href, rot, seed, kind=''):
    inner = f'<div style="{HAND};font-size:24px;color:{INK};white-space:nowrap">{text}</div><div style="{TYPE};font-size:10px;font-weight:700;letter-spacing:.18em;color:{PENCIL};margin-top:4px">{feat} →</div>'
    return f'<a href="{href}" class="chip" style="display:block">{paper(inner, 276, 108, rot=rot, seed=seed, kind=kind, pad="18px 24px")}</a>'
pnote = paper(f'''
<div style="{SERIF};font-size:20px;line-height:1.6;color:{INK}">A few people ended their pods with you tonight, so we're closing the door for a while. It's not a ban, and nothing follows you.</div>
<div style="border-top:1px dashed {RULE};margin-top:20px;padding-top:16px;display:grid;grid-template-columns:150px 1fr;row-gap:10px;{TYPE};font-size:12px;letter-spacing:.1em;color:{INK}">
<span style="color:{PENCIL}">OPENS AGAIN</span><span>TOMORROW · 10PM</span><span style="color:{PENCIL}">KEPT</span><span>A COUNT · GONE BY MORNING</span></div>''',
    520, 244, rot=-1, kind='hi', seed=1721, pad='36px 42px', tapes=tape(205, -14, 110, 28, rot=3, seed=173))
paused = f'''
{atmos()}
{topbar(right='BACK AT 10PM TOMORROW')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding-bottom:30px">
{h_hand('Pods are closed for you tonight.', 54, d='2s')}
<div style="display:flex;align-items:center;gap:90px;margin-top:14px">
<div class="rise" style="--w:.9s">{pnote}</div>
<div class="fadein" style="--w:.4s;margin-top:-40px">{closed_sign(270, 150, 'closed for tonight', '', 34, 1722)}</div></div>
<div class="rise" style="--w:1.6s;display:flex;flex-direction:column;align-items:center;gap:16px;margin-top:34px">
<div style="display:flex;align-items:baseline;gap:18px">{t_mark('still open for you', 26, SOFTRED)}<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{BOARDTXT}">ON YOUR OWN · ANY TIME</span></div>
<div style="display:flex;gap:26px">{scrap_link('get it out', 'BURN', 'V5Burn.dc.html', -2, 1723)}{scrap_link('leave it somewhere', 'ECHOES', 'V5Echoes.dc.html', 1.5, 1724, 'kraft')}{scrap_link('write it, don\'t send', 'UNSENT', 'V5UnsentWrite.dc.html', .8, 1726, 'kraft')}{scrap_link('hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', -1, 1725)}</div></div>
</main>
{footer()}'''
page('V5Paused', 'Pods closed for you tonight', paused, css=SIGN_CSS)
board('V5Paused', 'T09 — Pods closed for you tonight', 900, 'talk', 1440)

write_manifest()
print('talk desktop ok')
