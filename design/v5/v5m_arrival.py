from gen5 import *
import json
from v5m_home import ctape, etape, fcard

# ---------------- MA01 BOOT ----------------
mboot_card = paper(f'''
<div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">
{rabbit(116, INK, draw=True, uid='mboot')}
<div class="write" style="--w:2.1s;--d:1.4s;{HAND};font-size:28px;color:{INK}">Damn_It_Rabbit</div>
<div class="fadein" style="--w:3.3s;{TYPE};font-size:10px;letter-spacing:.3em;color:{PENCIL}">PRESENTS</div>
</div>''', 290, 260, rot=-1.6, seed=61, pad='20px', tapes=tape(95, -13, 100, 28, rot=-4, seed=7))

mboot = f'''
{matmos()}
<div style="position:relative;z-index:10;flex:1 1 auto;min-height:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:clamp(28px, 5.4vh, 46px);padding:12px {MPAD}px">
<div class="rise" style="--w:.1s;max-width:100%">{mboot_card}</div>
<div class="fadein" style="--w:4s;display:flex;flex-direction:column;align-items:center;gap:10px">
<span style="{TYPE};font-weight:700;font-size:32px;letter-spacing:.34em;margin-right:-.34em;color:{PAPERHI}">N0TRACE</span>
<div style="opacity:.5">{underline(120, RED, 1.6, wait='4.6s', d='.8s')}</div>
<div class="fadein" style="--w:5s;{HAND};font-size:22px;color:{BOARDTXT};margin-top:2px">say it. let it go.</div>
<span style="{TYPE};font-size:11px;letter-spacing:.22em;color:{BOARDTXT};margin-top:clamp(14px, 3vh, 26px);white-space:nowrap">[ tap anywhere to begin<span class="blink">_</span> ]</span>
</div></div>
<div style="position:relative;z-index:10;flex-shrink:0;margin:0 {MPAD}px;padding:12px 0 calc(20px + {M_SAFE});display:flex;justify-content:space-between;gap:12px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT};white-space:nowrap">
<span>18+ ONLY</span><span>© 2026 · DUG UP BY <span style="letter-spacing:0">Damn_It_Rabbit</span></span></div>
<a href="V5MStory.dc.html" aria-label="Tap anywhere to begin" style="position:absolute;inset:0;z-index:70;cursor:pointer"></a>'''
mpage('V5MBoot', 'Boot', mboot)

# ---------------- MA02 STORY ----------------
SC = 4.8
def scene_wrap(i, inner, last=False):
    anim = f'animation:scLast 1.6s ease {i * SC:.1f}s both' if last else f'animation:sc {SC:.1f}s ease {i * SC:.1f}s both'
    return f'<section class="sc" style="{anim}">{inner}</section>'

def s1(t=0):
    return f'''<div class="write" style="--w:{t + .5:.1f}s;--d:1.8s;{HAND};font-size:46px;line-height:1.25;text-align:center;color:{CHALK}">Everyone<br>carries<br>something.</div>'''

def soft_window(html):
    """The window photo with its glow halved (the halo and the light on the floor)."""
    return html.replace('fill="#f4b46c" opacity=".6"', 'fill="#f4b46c" opacity=".3"').replace('fill="#f4b46c" opacity=".12"', 'fill="#f4b46c" opacity=".06"')

def s2(t=0):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:44px">
<div class="sink" style="animation-delay:{t + .6:.1f}s">{soft_window(polaroid('window', 230, 180, 'still awake at 2am', rot=-3, seed=71, u='ms2', capsize=22))}</div>
<div class="write" style="--w:{t + .9:.1f}s;--d:1.8s;{HAND};font-size:42px;line-height:1.25;text-align:center;color:{CHALK}">Some nights,<br>it gets heavy.</div></div>'''

def s3(t=0):
    note = paper(f'<div style="{SERIF};font-size:19px;line-height:1.6;color:{INK}">I don\'t know who to tell this to, so I\'m telling no one, here.</div>',
                 300, 170, rot=2, seed=72, pad='28px 28px', tapes=f'<span class="slap" style="animation-delay:{t + 1.3:.1f}s">{tape(100, -13, 100, 28, rot=-3, seed=8)}</span>')
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:46px">
<div class="drop" style="animation-delay:{t + .3:.1f}s">{note}</div>
<div class="write" style="--w:{t + 1.5:.1f}s;--d:1.6s;{HAND};font-size:42px;line-height:1.25;text-align:center;color:{CHALK}">You can put it<br>down here.</div></div>'''

def scrap(text, rot, seed, delay, kind='', dx=0):
    w = int(len(text) * 14 + 56)
    # the sideways scatter is drawn for a 390 phone; it narrows on smaller phones so no scrap leaves the column
    return (f'<div class="toss" style="animation-delay:{delay:.1f}s;max-width:100%;margin-left:calc({dx / 50:.2f} * (min(100vw, 390px) - 340px))">' +
            paper(f'<div style="{HAND};font-size:28px;color:{INK};white-space:nowrap">{text}</div>', w, 68, rot=rot, seed=seed, pad="12px 26px", kind=kind) + '</div>')

def s4(t=0):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:40px">
<div style="display:flex;flex-direction:column;align-items:center;gap:14px">
{scrap('burn it', -4, 81, t + .3, dx=-90)}{scrap('leave it somewhere', 2, 82, t + .6, 'kraft', dx=30)}{scrap('keep it for later', -1, 83, t + .9, dx=-30)}{scrap('or talk to someone', 3, 84, t + 1.2, 'kraft', dx=24)}
</div>
<div class="write" style="--w:{t + 1.6:.1f}s;--d:1.4s;{HAND};font-size:32px;color:{BOARDTXT}">however you need to.</div></div>'''

def s5(t=0):
    lines = ['no names.', 'no history.', 'nothing kept.']
    out = ''.join(f'<div class="type-on" style="--n:{len(l)};animation-delay:{t + .3 + i * .9:.1f}s;{TYPE};font-size:22px;letter-spacing:.2em;color:{CHALK};text-transform:uppercase">{l}</div>' for i, l in enumerate(lines))
    return f'<div style="display:flex;flex-direction:column;align-items:flex-start;gap:18px;width:270px">{out}</div>'

def s6(t=0):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:30px">
{rabbit(76, CHALK, uid='mst6')}
<div class="write" style="--w:{t + .8:.1f}s;--d:1.8s;{HAND};font-size:46px;line-height:1.25;text-align:center;color:{PAPERHI}">There's light<br>after this.</div>
<div class="fadein" style="--w:{t + 2.4:.1f}s;margin-top:10px">{chip('come in  →', 'V5MAge.dc.html', seed=91, w=210)}</div></div>'''

story_css = f"""
.sc{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:0;z-index:10;padding:0 {MPAD}px}}
@keyframes sc{{0%{{opacity:0;filter:blur(4px)}}14%{{opacity:1;filter:none}}82%{{opacity:1;filter:none}}100%{{opacity:0;filter:blur(3px)}}}}
@keyframes scLast{{from{{opacity:0}}to{{opacity:1}}}}
.sink{{animation:sink 3s ease-in both}}
@keyframes sink{{from{{transform:translateY(-10px)}}to{{transform:translateY(18px) rotate(-2deg)}}}}
.drop{{animation:drop .9s cubic-bezier(.3,1.4,.5,1) both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-60px) rotate(-8deg)}}to{{opacity:1;transform:none}}}}
.slap{{display:block;animation:slap .35s cubic-bezier(.2,1.6,.4,1) both}}
@keyframes slap{{from{{opacity:0;transform:scale(1.5) translateY(-10px)}}to{{opacity:1;transform:none}}}}
.toss{{animation:toss .9s cubic-bezier(.2,1.2,.4,1) both}}
@keyframes toss{{from{{opacity:0;transform:translateY(40px) rotate(12deg) scale(.9)}}to{{opacity:1;transform:none}}}}
.type-on{{overflow:hidden;white-space:nowrap;width:0;animation:typeon calc(var(--n) * 70ms) steps(var(--n)) both}}
@keyframes typeon{{to{{width:calc(var(--n) * 1.2em)}}}}
.prog span{{display:block;height:2px;background:{SOOT};position:relative;overflow:hidden}}
.prog span i{{position:absolute;inset:0;background:{CHALK};transform-origin:left;transform:scaleX(0);animation:pr {SC:.1f}s linear both}}
@keyframes pr{{to{{transform:scaleX(1)}}}}
"""
progress = (f'<div class="prog" style="position:absolute;z-index:30;top:30px;left:{MPAD}px;width:min(234px, calc(100% - {2 * MPAD + 70}px));display:grid;grid-template-columns:repeat(6,1fr);gap:6px">' +
            ''.join(f'<span><i style="animation-delay:{i * SC:.1f}s"></i></span>' for i in range(6)) + '</div>')
mstory = f'''
{matmos()}
{progress}
<a href="V5MAge.dc.html" class="ul" style="position:absolute;z-index:30;top:22px;right:{MPAD}px;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">SKIP</a>
{scene_wrap(0, s1())}{scene_wrap(1, s2(1 * SC))}{scene_wrap(2, s3(2 * SC))}{scene_wrap(3, s4(3 * SC))}{scene_wrap(4, s5(4 * SC))}{scene_wrap(5, s6(5 * SC), last=True)}
'''
mpage('V5MStory', 'A short story', mstory, css=story_css)

# ---------------- MA03 AGE ----------------
# the circled answer is the signature mark: it lives on the note itself, under the red line
age_yes = (f'<a href="V5MHome.dc.html" class="row" style="position:relative;flex:0 0 auto;height:64px;width:208px;justify-content:center">'
           f'{circle_scribble(208, 60, RED, wait="2.6s")}<span style="position:relative;{HAND};font-size:23px;color:{INK};white-space:nowrap">I\'m 18 or older →</span></a>')
mage_note = fcard(f'''<div style="display:flex;flex-direction:column">
<div class="write" style="--w:.4s;{HAND};font-size:clamp(32px, 9vw, 36px);line-height:1.2;color:{INK};padding-right:clamp(0px, 20vw - 50px, 40px)">Before you go in.</div>
<div class="rise" style="--w:1.4s;{SERIF};font-size:clamp(16.5px, 4.6vw, 18px);line-height:1.6;color:{INK};margin-top:clamp(10px, 2vh, 16px)">This place is for grown-ups. You'll meet strangers here, and they'll meet you. Nobody gets a name, a face, or a history.</div>
<div class="rise" style="--w:1.9s;{MARK};font-size:24px;line-height:1.2;color:{RED};margin-top:clamp(12px, 2.2vh, 18px);transform:rotate(-1.5deg)">Be the kind of stranger you'd want to meet.</div>
<div class="rise" style="--w:2.3s;display:flex;align-items:center;flex-wrap:wrap;gap:4px 8px;margin:clamp(20px, 3.4vh, 32px) 0 0 -8px">{age_yes}{mtext('not yet', 'V5MNotYet.dc.html', PENCIL)}</div>
</div>''', seed=101, pad='38px 26px 26px', rot=-1,
    tapes=ctape(110, -14, 30, rot=-4, seed=13, dx=-20) + etape(80, 26, 38, 14, right=-24, bottom=-10))

mage = f'''
{matmos()}
{mtopbar(crumb='first visit')}
{mbody(f'<div class="rise" style="--w:1s;align-self:flex-end;margin:0 4px -40px 0;position:relative;z-index:2">{polaroid("lamp", 104, 92, "just words.", rot=6, seed=102, u="mag", capsize=18, tapes=False)}</div>'
       f'<div class="rise" style="--w:.1s;flex:0 0 auto;display:flex;flex-direction:column;position:relative;z-index:1">{mage_note}</div>', top=8, center=True, gap=0)}
<div style="height:{M_GAP + 6}px;flex-shrink:0"></div>
{mfooter()}'''
mpage('V5MAge', 'Before you go in', mage)

# ---------------- MA04 NOT YET ----------------
import gen5 as _g0
_pg0 = _g0.page; _g0.page = lambda *a, **k: None   # borrow the helpline row atoms without rewriting desktop boards
from v5_arrival import GLOBE_I, PHONE_I, TAP_CSS
_g0.page = _pg0
def mcall(k, name, detail, href, icon=None, color=INK, last=False):
    """Phone helpline row (as on the help screen)."""
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    return (f'<a href="{href}"{ext} class="row tap" style="min-height:62px;padding:7px 2px;margin:0 -2px;{bb}gap:12px">'
            f'<span style="display:flex;flex-direction:column;gap:2px;min-width:0"><span style="{HAND};font-size:22px;line-height:1.2;color:{color}">{name}</span>'
            f'<span style="{TYPE};font-size:9px;letter-spacing:.1em;line-height:1.4;color:{PENCIL}">{detail}</span></span>'
            f'<span class="go" style="flex-shrink:0;display:flex;align-items:center;gap:7px;{TYPE};font-weight:700;font-size:13px;letter-spacing:.12em;color:{color}">'
            f'<svg width="17" height="17" viewBox="0 0 17 17" aria-hidden="true">{icon or PHONE_I}</svg>{k}</span></a>')
mny_note = paper(f'''
<div class="write" style="--w:.3s;{HAND};font-size:34px;line-height:1.2;color:{INK}">Not yet.<br>That's okay.</div>
<div class="rise" style="--w:1.2s;{SERIF};font-size:17px;line-height:1.55;color:{INK};margin-top:12px;text-wrap:pretty">N0TRACE is for adults. But if something is heavy right now, you deserve someone kind to talk to. These are free, and they're for you.</div>
<div class="rise" style="--w:1.6s;margin-top:14px;border-top:1px dashed {RULE}">
{mcall('1098', 'Childline India', 'FREE · 24/7 · UNDER 18', 'tel:1098')}
{mcall('112', 'Emergency', 'IF YOU ARE IN DANGER', 'tel:112', color=RED)}
{mcall('FIND', 'Outside India', 'FINDAHELPLINE.COM', 'https://findahelpline.com', icon=GLOBE_I, last=True)}</div>
<div class="rise" style="--w:1.9s;{SERIF};font-style:italic;font-size:15px;color:{PENCIL};margin-top:8px;padding-top:10px;border-top:1px dashed {RULE}">And a trusted adult. Really.</div>''', 346, 522, rot=.8, seed=111, pad='32px 26px', tapes=tape(120, -13, 110, 28, rot=3, seed=15))
mny = f'''
{matmos()}
{mtopbar(crumb='first visit')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;gap:22px;padding-top:10px">
<div class="rise" style="--w:.1s">{mny_note}</div>
<div class="rise" style="--w:2s;display:flex;align-items:center;gap:18px;align-self:stretch;padding:0 {MPAD + 6}px">{rabbit(64, CHALK, uid='mny')}
<div style="display:flex;flex-direction:column;gap:8px"><div style="{HAND};font-size:22px;color:{BOARDTXT}">we'll be here.</div>{link('← back', 'V5MAge.dc.html', size=11)}</div></div>
</main>'''
mpage('V5MNotYet', 'Not yet', mny, css=TAP_CSS)

# ---------------- MH03 KEEP THIS NAME? (over dimmed home) ----------------
import gen5 as _g
_real_page = _g.page
_g.page = lambda *a, **k: None          # import home layouts without rewriting their boards
import v5m_home as _mh
import v5_home as _dh
_g.page = _real_page

NAME = 'quiet_otter'
VEIL = '<div aria-hidden="true" style="position:absolute;inset:0;z-index:60;background:rgba(6,6,7,.78)"></div>'

def name_tag(size):
    return f'<span style="{TYPE};font-weight:700;font-size:{size}px;letter-spacing:.06em;color:{INK};background:rgba(184,53,42,.12);padding:1px 6px">{NAME}</span>'

mrem_note = paper(f'''
{t_mark('one small thing', 21)}
<div class="write" style="--w:.6s;--d:1.6s;{HAND};font-size:30px;line-height:1.3;color:{INK};margin-top:6px">you're {name_tag(20)}<br>tonight.</div>
<div class="rise" style="--w:1.6s;{SERIF};font-size:17.5px;line-height:1.55;color:{INK};margin-top:12px">Want this phone to remember that name next time? It stays on this device. We never keep it.</div>
<div class="rise" style="--w:2.1s;display:flex;flex-direction:column;align-items:center;gap:18px;margin-top:22px">
{chip('keep it on this device', 'V5MHome.dc.html', kind='ink', seed=131, w=270)}
{link('new name every time', 'V5MHome.dc.html', color=INK, size=11.5)}
</div>''', 334, 386, rot=-1.2, seed=132, pad='30px 30px', tapes=tape(112, -13, 110, 28, rot=-3, seed=33))

mrem = f'''
<div aria-hidden="true" inert style="position:absolute;inset:0;display:flex;flex-direction:column">{_mh.mhome(False)}</div>
{VEIL}
<div role="dialog" aria-label="Keep this name?" style="position:absolute;z-index:65;left:0;right:0;bottom:66px;display:flex;justify-content:center">
<div class="rise" style="--w:.2s">{mrem_note}</div></div>'''
mpage('V5MRemember', 'Keep this name?', mrem, css=_mh.css)

# ---------------- H03 desktop: First arrival, keep this name? ----------------
drem_note = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('one small thing', 26)}<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">FIRST TIME HERE</span></div>
<div class="write" style="--w:.6s;--d:1.6s;{HAND};font-size:44px;line-height:1.3;color:{INK};margin-top:8px;white-space:nowrap">you're {name_tag(30)} tonight.</div>
<div class="rise" style="--w:1.6s;{SERIF};font-size:20px;line-height:1.6;color:{INK};margin-top:14px;max-width:470px">Want this device to remember that name next time? It stays here, on this device. We never keep it.</div>
<div class="rise" style="--w:2.1s;display:flex;align-items:center;gap:34px;margin-top:30px">
{chip('keep it on this device', 'V5Home.dc.html', kind='ink', seed=131, w=300)}
{link('new name every time', 'V5Home.dc.html', color=INK, size=12)}
</div>''', 680, 340, rot=-1, seed=132, pad='40px 52px', tapes=tape(280, -15, 120, 30, rot=-3, seed=33) + tape(610, 296, 90, 26, rot=35, seed=34))

drem = f'''
<div aria-hidden="true" inert style="position:absolute;inset:0;display:flex;flex-direction:column">{_dh.home(False)}</div>
{VEIL}
<div role="dialog" aria-label="Keep this name?" style="position:absolute;z-index:65;inset:0;display:flex;align-items:center;justify-content:center;padding-top:30px">
<div class="rise" style="--w:.2s">{drem_note}</div></div>'''
page('V5Remember', 'First arrival, keep this name?', drem, css=_dh.home_css)

json.dump([
    {"file": "V5MBoot.dc.html", "title": "MA01 — Boot", "w": 390, "h": 844, "row": "m_arrival"},
    {"file": "V5MStory.dc.html", "title": "MA02 — The story", "w": 390, "h": 844, "row": "m_arrival"},
    {"file": "V5MAge.dc.html", "title": "MA03 — Before you go in", "w": 390, "h": 844, "row": "m_arrival"},
    {"file": "V5MNotYet.dc.html", "title": "MA04 — Not yet, under 18", "w": 390, "h": 844, "row": "m_arrival"},
    {"file": "V5Remember.dc.html", "title": "H03 — First arrival: keep this name?", "w": 1440, "h": 900, "row": "home"},
    {"file": "V5MHome.dc.html", "title": "MH01 — Home, pods asleep", "w": 390, "h": 844, "row": "m_home"},
    {"file": "V5MHomeOpen.dc.html", "title": "MH02 — Home, pods open + capsule arrived (scrolls)", "w": 390, "h": _mh.MHOME_OPEN_H, "row": "m_home"},
    {"file": "V5MRemember.dc.html", "title": "MH03 — Keep this name?", "w": 390, "h": 844, "row": "m_home"},
], open('manifest_arrival.json', 'w'), ensure_ascii=False, indent=1)
print('m arrival ok')
