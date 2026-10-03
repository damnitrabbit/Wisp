from gen5 import *

# ---------------- BOOT ----------------
boot_card = paper(f'''
<div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">
{rabbit(150, INK, draw=True, uid='boot')}
<div class="write" style="--w:2.1s;--d:1.4s;{HAND};font-size:34px;color:{INK}">Damn_It_Rabbit</div>
<div class="fadein" style="--w:3.3s;{TYPE};font-size:11px;letter-spacing:.3em;color:{PENCIL}">PRESENTS</div>
</div>''', 380, 330, rot=-1.6, seed=61, pad='24px', tapes=tape(135, -14, 110, 30, rot=-4, seed=7))

boot = f'''
{atmos(leak(-260, 520, 760, GLOW, 0, dur=9) + leak(1180, -260, 520, ROSE, 3) + '<div class="flare"></div>')}
<div style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:44px">
<div class="rise" style="--w:.1s">{boot_card}</div>
<div class="fadein" style="--w:4s;display:flex;flex-direction:column;align-items:center;gap:14px">
<div style="position:relative;display:flex;flex-direction:column;align-items:center;gap:6px">
<div class="nglow" aria-hidden="true"></div>
<span style="position:relative;{TYPE};font-weight:700;font-size:46px;letter-spacing:.38em;margin-right:-.38em;color:{PAPERHI}">N0TRACE</span>
<div style="position:relative;opacity:.5">{underline(150, RED, 1.8, wait='4.6s', d='.8s')}</div>
<div class="fadein" style="--w:5s;{HAND};font-size:24px;color:{BOARDTXT};margin-top:2px">say it. let it go.</div></div>
<span style="{TYPE};font-size:12px;letter-spacing:.24em;color:{BOARDTXT};margin-top:14px">[ tap anywhere to begin<span class="blink">_</span> ]</span>
</div>
</div>
<div style="position:absolute;z-index:10;left:56px;right:56px;bottom:34px;display:flex;justify-content:space-between;{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT}">
<span>18+ ONLY</span><span>© 2026 · DUG UP BY <span style="letter-spacing:0">Damn_It_Rabbit</span></span></div>
<a href="V5Story.dc.html" aria-label="Tap anywhere to begin" style="position:absolute;inset:0;z-index:70;cursor:pointer"></a>'''
page('V5Boot', 'Boot', boot, css='.nglow{position:absolute;left:50%;top:-30px;width:520px;height:160px;margin-left:-260px;border-radius:50%;background:radial-gradient(closest-side,rgba(255,200,150,.16),transparent);filter:blur(10px);opacity:0;animation:fadein 2s ease 4.2s forwards}')

# ---------------- STORY ----------------
# 6 scenes, ~4.8s each, last one stays. Each scene is a centred composition.
SC = 4.8
def scene_wrap(i, inner, last=False):
    if last:
        anim = f'animation:scLast 1.6s ease {i * SC:.1f}s both'
    else:
        anim = f'animation:sc {SC:.1f}s ease {i * SC:.1f}s both'
    return f'<section class="sc" style="{anim}">{inner}</section>'

def s1():
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:18px">
<div class="write" style="--w:{0 * SC + .5:.1f}s;--d:1.8s;{HAND};font-size:72px;color:{CHALK}">Everyone carries something.</div></div>'''

def soft_window(html):
    """The window photo with its glow halved (the halo and the light on the floor)."""
    return html.replace('fill="#f4b46c" opacity=".6"', 'fill="#f4b46c" opacity=".3"').replace('fill="#f4b46c" opacity=".12"', 'fill="#f4b46c" opacity=".06"')

def s2(t=0):
    return f'''<div style="display:flex;align-items:center;gap:70px">
<div class="sink" style="animation-delay:{t + .6:.1f}s">{soft_window(polaroid('window', 300, 230, 'still awake at 2am', rot=-3, seed=71, u='s2', capsize=24))}</div>
<div class="write" style="--w:{t + .9:.1f}s;--d:1.8s;{HAND};font-size:64px;line-height:1.25;color:{CHALK}">Some nights,<br>it gets heavy.</div></div>'''

def s3(t=0):
    note = paper(f'<div style="{SERIF};font-size:21px;line-height:1.6;color:{INK}">I don\'t know who to tell this to, so I\'m telling no one, here.</div>',
                 360, 190, rot=2, seed=72, pad='30px 32px', tapes=f'<span class="slap" style="animation-delay:{t + 1.3:.1f}s">{tape(125, -14, 110, 30, rot=-3, seed=8)}</span>')
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:46px">
<div class="drop" style="animation-delay:{t + .3:.1f}s">{note}</div>
<div class="write" style="--w:{t + 1.5:.1f}s;--d:1.6s;{HAND};font-size:60px;color:{CHALK}">You can put it down here.</div></div>'''

def scrap(text, rot, seed, delay, kind=''):
    # double-quoted style: the font stack itself has single quotes
    inner = f'<div style="{HAND};font-size:36px;color:{INK};white-space:nowrap">{text}</div>'
    return f'<div class="toss" style="animation-delay:{delay:.1f}s">{paper(inner, int(len(text) * 17 + 64), 84, rot=rot, seed=seed, pad="14px 30px", kind=kind)}</div>'

def s4(t=0):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:50px">
<div style="display:flex;gap:28px;align-items:center">
{scrap('burn it', -4, 81, t + .3)}{scrap('leave it somewhere', 2, 82, t + .6, 'kraft')}{scrap('keep it for later', -1, 83, t + .9)}{scrap('or talk to someone', 3, 84, t + 1.2, 'kraft')}
</div>
<div class="write" style="--w:{t + 1.6:.1f}s;--d:1.4s;{HAND};font-size:44px;color:{BOARDTXT}">however you need to.</div></div>'''

def s5(t=0):
    lines = ['no names.', 'no history.', 'nothing kept.']
    out = ''.join(f'<div class="type-on" style="--n:{len(l)};animation-delay:{t + .3 + i * .9:.1f}s;{TYPE};font-size:30px;letter-spacing:.2em;color:{CHALK};text-transform:uppercase">{l}</div>' for i, l in enumerate(lines))
    return f'<div style="display:flex;flex-direction:column;align-items:flex-start;gap:20px">{out}</div>'

def s6(t=0):
    return f'''<div style="display:flex;flex-direction:column;align-items:center;gap:34px">
{rabbit(90, CHALK, uid='st6')}
<div class="write" style="--w:{t + .8:.1f}s;--d:1.8s;{HAND};font-size:76px;color:{PAPERHI}">There's light after this.</div>
<div class="fadein" style="--w:{t + 2.4:.1f}s">{chip('come in  →', 'V5Age.dc.html', seed=91, w=220)}</div></div>'''

story_css = f"""
.sc{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;opacity:0;z-index:10}}
@keyframes sc{{0%{{opacity:0;filter:blur(4px)}}14%{{opacity:1;filter:none}}82%{{opacity:1;filter:none}}100%{{opacity:0;filter:blur(3px)}}}}
@keyframes scLast{{from{{opacity:0}}to{{opacity:1}}}}
.sink{{animation:sink 3s ease-in both}}
@keyframes sink{{from{{transform:translateY(-10px)}}to{{transform:translateY(22px) rotate(-2deg)}}}}
.drop{{animation:drop .9s cubic-bezier(.3,1.4,.5,1) both}}
@keyframes drop{{from{{opacity:0;transform:translateY(-60px) rotate(-8deg)}}to{{opacity:1;transform:none}}}}
.slap{{display:block;animation:slap .35s cubic-bezier(.2,1.6,.4,1) both}}
@keyframes slap{{from{{opacity:0;transform:scale(1.5) translateY(-10px)}}to{{opacity:1;transform:none}}}}
.toss{{animation:toss .9s cubic-bezier(.2,1.2,.4,1) both}}
@keyframes toss{{from{{opacity:0;transform:translateY(40px) rotate(12deg) scale(.9)}}to{{opacity:1;transform:none}}}}
.type-on{{overflow:hidden;white-space:nowrap;width:0;animation:typeon calc(var(--n) * 70ms) steps(var(--n)) both}}
@keyframes typeon{{to{{width:calc(var(--n) * 1.2em)}}}}
.dawn{{position:absolute;left:-10%;right:-10%;bottom:-60%;height:120%;border-radius:50%;background:radial-gradient(ellipse at 50% 30%,rgba(255,206,150,.55),rgba(255,143,107,.22) 35%,transparent 65%);mix-blend-mode:screen;filter:blur(30px);opacity:0;animation:dawn 4s ease {5 * SC:.1f}s both;z-index:3}}
@keyframes dawn{{from{{opacity:0;transform:translateY(25%)}}to{{opacity:1;transform:none}}}}
.prog span{{display:block;height:2px;background:{SOOT};position:relative;overflow:hidden}}
.prog span i{{position:absolute;inset:0;background:{CHALK};transform-origin:left;transform:scaleX(0);animation:pr {SC:.1f}s linear both}}
@keyframes pr{{to{{transform:scaleX(1)}}}}
"""
progress = '<div class="prog" style="position:absolute;z-index:30;top:40px;left:50%;transform:translateX(-50%);display:grid;grid-template-columns:repeat(6,70px);gap:8px">' + \
    ''.join(f'<span><i style="animation-delay:{i * SC:.1f}s"></i></span>' for i in range(6)) + '</div>'

story = f'''
{atmos(leak(-300, 560, 700, GLOW, 0) + leak(1100, -300, 560, ROSE, 5))}
<div class="dawn"></div>
{progress}
<a href="V5Age.dc.html" class="ul" style="position:absolute;z-index:30;top:32px;right:56px;{TYPE};font-size:12px;letter-spacing:.16em;color:{BOARDTXT}">SKIP</a>
{scene_wrap(0, s1())}{scene_wrap(1, s2(1 * SC))}{scene_wrap(2, s3(2 * SC))}{scene_wrap(3, s4(3 * SC))}{scene_wrap(4, s5(4 * SC))}{scene_wrap(5, s6(5 * SC), last=True)}
'''
page('V5Story', 'A short story', story, css=story_css)

# storyboard: the same six scenes, frozen, side by side
def frame(i, inner, cap):
    return f'''<div style="display:flex;flex-direction:column;gap:14px">
<div class="frz" style="position:relative;width:420px;height:262px;border:1px dashed {SOOT};border-radius:3px;overflow:hidden;background:{NIGHT}">
<div style="position:absolute;left:0;top:0;width:1440px;height:900px;transform:scale(.2917);transform-origin:0 0;display:flex;align-items:center;justify-content:center">{inner}</div></div>
<div style="display:flex;gap:12px;align-items:baseline"><span style="{MARK};color:{RED};font-size:24px">{i}</span><span style="{SERIF};font-size:17px;color:{BOARDTXT};line-height:1.45">{cap}</span></div></div>'''
frz_css = '.frz *{animation:none !important}.frz .write{clip-path:none !important}.frz .write,.frz .rise,.frz .fadein,.frz .toss,.frz .drop,.frz .slap,.frz .type-on,.frz .sink{opacity:1 !important;transform:none}.frz .type-on{width:auto}.frz .draw{stroke-dashoffset:0}'
sb = f'''
{atmos()}
<div style="position:relative;z-index:10;padding:60px 64px;display:flex;flex-direction:column;gap:34px">
<div>{t_type('first visit · the story, frame by frame', 12)}{h_hand('Before home, a short story.', 52, extra='margin-top:6px')}</div>
<div style="display:grid;grid-template-columns:repeat(3,420px);gap:38px 44px">
{frame(1, s1(), 'Everyone carries something. One line, written on in the dark.')}
{frame(2, s2(), 'A photo slowly sinks, like it\'s heavy. Some nights, it gets heavy.')}
{frame(3, s3(), 'A note drops onto the desk and gets taped down. You can put it down here.')}
{frame(4, s4(), 'Four scraps get tossed in: everything N0TRACE lets you do.')}
{frame(5, s5(), 'The promise, typed out: no names, no history, nothing kept.')}
{frame(6, s6(), 'Dawn comes up from the bottom. There\'s light after this. Come in.')}
</div></div>'''
page('V5StoryBoard', 'Story, frame by frame', sb, css=story_css + frz_css, h=920)

# ---------------- AGE ----------------
age_note = paper(f'''
<div class="write" style="--w:.4s;{HAND};font-size:50px;color:{INK}">Before you go in.</div>
<div class="rise" style="--w:1.4s;{SERIF};font-size:22px;line-height:1.6;color:{INK};margin-top:22px;max-width:520px">This place is for grown-ups. You'll meet strangers here, and they'll meet you. Nobody gets a name, a face, or a history.</div>
<div class="rise" style="--w:1.9s;{MARK};font-size:30px;color:{RED};margin-top:20px;transform:rotate(-1.5deg)">Be the kind of stranger you'd want to meet.</div>
<div style="display:flex;align-items:center;gap:60px;margin-top:46px">
<a href="V5Home.dc.html" onclick="{{{{adult}}}}" class="row" style="position:relative;padding:14px 34px">{circle_scribble(370, 92, RED, wait='2.6s')}<span style="{HAND};font-size:36px;color:{INK}">I'm 18 or older →</span></a>
<a href="V5NotYet.dc.html" class="ul" style="{TYPE};font-size:13px;letter-spacing:.16em;color:{PENCIL}">NOT YET</a>
</div>''', 720, 560, rot=-1, seed=101, pad='58px 64px', tapes=tape(300, -16, 120, 32, rot=-4, seed=13) + tape(640, 510, 100, 28, rot=38, seed=14))

age = f'''
{atmos(leak(1050, -220, 640) + leak(-200, 600, 520, ROSE, 4) + '<div class="flare"></div>')}
{topbar(crumb='first visit')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:90px;padding-bottom:40px">
<div class="rise" style="--w:.1s">{age_note}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:20px;margin-top:-60px">
<div class="rise" style="--w:1s">{polaroid('lamp', 260, 320, 'no names. no faces.<br>just words.', rot=4, seed=102, u='ag', capsize=24)}</div>
</div>
</main>'''
page('V5Age', 'Before you go in', age)

# ---------------- NOT YET (under 18) ----------------
PHONE_I = '<path d="M5 2.5h2.2l1.2 3-1.6 1.1a8 8 0 0 0 3.6 3.6l1.1-1.6 3 1.2V12a1.6 1.6 0 0 1-1.6 1.6A10.6 10.6 0 0 1 3.4 4.1 1.6 1.6 0 0 1 5 2.5z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
GLOBE_I = '<circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2.5 8.5h12M8.5 2.5c-2.2 2.4-2.2 9.6 0 12M8.5 2.5c2.2 2.4 2.2 9.6 0 12" fill="none" stroke="currentColor" stroke-width="1.3"/>'
def hcall(k, name, detail, href, icon=PHONE_I, color=INK, last=False):
    """A helpline row, same as the help screen: hand name + type sub-line, icon + number on the right."""
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
    return (f'<a href="{href}"{ext} class="row tap" style="min-height:66px;padding:8px 2px;margin:0 -2px;{bb}gap:16px">'
            f'<span style="display:flex;flex-direction:column;gap:3px;min-width:0"><span style="{HAND};font-size:27px;line-height:1.2;color:{color}">{name}</span>'
            f'<span style="{TYPE};font-size:10.5px;letter-spacing:.12em;line-height:1.4;color:{PENCIL}">{detail}</span></span>'
            f'<span class="go" style="flex-shrink:0;display:flex;align-items:center;gap:9px;{TYPE};font-weight:700;font-size:15px;letter-spacing:.12em;color:{color}">'
            f'<svg width="18" height="18" viewBox="0 0 17 17" aria-hidden="true">{icon}</svg>{k}</span></a>')
TAP_CSS = '.tap{transition:background-color .2s}.tap:active{background-color:rgba(34,30,26,.06)}'

ny_note = paper(f'''
<div class="write" style="--w:.3s;{HAND};font-size:48px;color:{INK}">Not yet. That's okay.</div>
<div class="rise" style="--w:1.2s;{SERIF};font-size:21px;line-height:1.6;color:{INK};margin-top:16px;text-wrap:pretty">N0TRACE is for adults. But if something is heavy right now, you deserve someone kind to talk to. These are free, and they're for you.</div>
<div class="rise" style="--w:1.6s;margin-top:20px;border-top:1px dashed {RULE}">
{hcall('1098', 'Childline India', 'FREE · 24/7 · FOR ANYONE UNDER 18', 'tel:1098')}
{hcall('112', 'Emergency', 'IF YOU ARE IN DANGER RIGHT NOW', 'tel:112', color=RED)}
{hcall('FIND', 'Outside India', 'FINDAHELPLINE.COM · CALL, TEXT, CHAT', 'https://findahelpline.com', icon=GLOBE_I, last=True)}</div>
<div class="rise" style="--w:1.9s;{SERIF};font-style:italic;font-size:17px;color:{PENCIL};margin-top:12px;padding-top:12px;border-top:1px dashed {RULE}">And a trusted adult. Really.</div>''', 660, 548, rot=.8, seed=111, pad='48px 58px', tapes=tape(270, -14, 120, 30, rot=3, seed=15))
ny = f'''
{atmos()}
{topbar(crumb='first visit')}
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:70px;padding-bottom:40px">
<div class="rise" style="--w:.1s">{ny_note}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:22px">{rabbit(140, CHALK, uid='ny')}
<div style="{HAND};font-size:26px;color:{BOARDTXT}">we'll be here.</div>{link('← back', 'V5Age.dc.html')}</div>
</main>'''
page('V5NotYet', 'Not yet', ny, css=TAP_CSS)
print('arrival ok')
