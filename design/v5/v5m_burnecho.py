"""N0TRACE V5 phone: Burn (MB01-04) + Echoes (ME01-04)."""
from gen5 import *
from v5x_echo import kind_pick, ECHO_CSS, wave, play_btn, heart, toggle, THREAD_SCRIPT, THREAD_PROPS, heard_btn, stamp, REPLIES, write_manifest, mwrite_board, KIND_CSS, letter_note, ico_note, ico_letter, step_label
import urllib.parse

# =====================================================================
# BURN (phone): a ~330px note, same physics as desktop, scaled down
# =====================================================================
W, H = 330, 330          # the sheet (fits the note + ~40px)
T = 4.0                  # burn duration (s)
E = H + 80               # edge position inside the mask image
IH = 2 * H + 120
TRAVEL = E + 30

r = random.Random(42)
edge = []
phase = r.uniform(0, 6)
for x in range(0, W + 6, 6):
    y = (math.sin(x / 33 + phase) * 6 + math.sin(x / 14 + 1.3) * 3.4 + math.sin(x / 5.5) * 1.5 + r.uniform(-2, 2))
    edge.append((x, y))
for cx, depth, wd in [(78, -26, 36), (218, -20, 30), (292, -15, 24)]:
    edge = [(x, y + depth * math.exp(-((x - cx) / wd) ** 2)) for x, y in edge]

def epath(off=0):
    return ' '.join(('M' if i == 0 else 'L') + f'{x} {E + y + off:.1f}' for i, (x, y) in enumerate(edge))

def svg_url(svg):
    svg = svg.replace('%23', '#')
    return 'url("data:image/svg+xml;utf8,' + urllib.parse.quote(svg, safe=" =:/;,'()-.") + '")'

HOLES = [(115, E - 50, 6), (172, E - 36, 4), (252, E - 58, 7), (44, E - 32, 3.5), (306, E - 42, 5)]
def blob(cx, cy, rr, seed, k=1.0, n=12):
    """An irregular charred hole (never a clean circle)."""
    q = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + q.uniform(-.18, .18)
        rad = rr * k * q.uniform(.62, 1.28) * (1.25 if i % 4 == 0 else 1)
        pts.append((cx + math.cos(a) * rad * 1.15, cy + math.sin(a) * rad * .9))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'
holes = ''.join(' ' + blob(cx, cy, rr, 950 + i) for i, (cx, cy, rr) in enumerate(HOLES))
pts_rev = ' '.join(f'L{x} {E + y:.1f}' for x, y in reversed(edge))
MASK = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}' viewBox='0 0 {W} {IH}' preserveAspectRatio='none'>"
               f"<path fill-rule='evenodd' fill='white' d='M0 0 L{W} 0 {pts_rev} Z{holes}'/></svg>")
rim_defs = ''.join(f"<radialGradient id='h{i}' gradientUnits='userSpaceOnUse' cx='{cx}' cy='{cy}' r='{rr * 2.3:.1f}'>"
                   f"<stop offset='0' stop-color='%23140904'/><stop offset='.42' stop-color='%23241005' stop-opacity='.92'/>"
                   f"<stop offset='.68' stop-color='%235e3312' stop-opacity='.4'/><stop offset='1' stop-color='%237a4a1e' stop-opacity='0'/></radialGradient>"
                   for i, (cx, cy, rr) in enumerate(HOLES))
hole_rims = ''.join(f"<path d='{blob(cx, cy, rr, 950 + i, k=2.1)}' fill='url(%23h{i})' filter='url(%23rb)'/>" for i, (cx, cy, rr) in enumerate(HOLES))
BAND = 34
band_top = ' '.join(f'L{x} {E + y - BAND:.1f}' for x, y in edge)
CHAR = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}' viewBox='0 0 {W} {IH}' preserveAspectRatio='none'>"
               f"<defs><linearGradient id='g' x1='0' y1='{E - 44}' x2='0' y2='{E + 8}' gradientUnits='userSpaceOnUse'>"
               f"<stop offset='0' stop-color='%237a4a1e' stop-opacity='0'/><stop offset='.55' stop-color='%236b3a14' stop-opacity='.45'/>"
               f"<stop offset='.85' stop-color='%232a1306' stop-opacity='.95'/><stop offset='1' stop-color='%23120804'/></linearGradient>"
               f"<filter id='b'><feGaussianBlur stdDeviation='1.6'/></filter><filter id='rb' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='1.1'/></filter>{rim_defs}</defs>"
               f"<path d='M{edge[0][0]} {E + edge[0][1] - BAND:.1f} {band_top} {pts_rev} Z' fill='url(%23g)'/>"
               f"{hole_rims}"
               f"<path d='{epath(-1.5)}' fill='none' stroke='%23FF7A2E' stroke-width='4.5' filter='url(%23b)'/>"
               f"<path d='{epath(-1)}' fill='none' stroke='%23FFD27A' stroke-width='1.3'/></svg>")
GLOW_IMG = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}' viewBox='0 0 {W} {IH}' preserveAspectRatio='none'>"
                   f"<defs><filter id='b' x='-20%' y='-50%' width='140%' height='200%'><feGaussianBlur stdDeviation='8'/></filter></defs>"
                   f"<path d='{epath(3)}' fill='none' stroke='%23FF8A3D' stroke-width='11' opacity='.35' filter='url(%23b)'/>"
                   f"<path d='{epath(9)}' fill='none' stroke='%23FF5A2E' stroke-width='13' opacity='.09' filter='url(%23b)'/></svg>")

pr = random.Random(7)
sparks = ''
for i in range(22):
    x = pr.uniform(2, 98); sz = pr.choice([2, 2, 2, 3, 3]); c = pr.choice(['#FFB347', '#FF7A2E', '#FFD27A'])
    sparks += (f'<i class="spark" style="left:{x:.1f}%;width:{sz}px;height:{sz}px;background:{c};box-shadow:0 0 6px {c};'
               f'--dx:{pr.uniform(-28, 28):.0f}px;--up:{pr.uniform(50, 130):.0f}px;animation-duration:{pr.uniform(.9, 1.6):.2f}s;'
               f'animation-delay:calc(var(--freeze,0s) + {pr.uniform(0, 1.6):.2f}s)"></i>')
ash = ''
for i in range(16):
    x = pr.uniform(0, 100); sz = pr.uniform(3, 8)
    poly = ','.join(f'{pr.uniform(0, 100):.0f}% {pr.uniform(0, 100):.0f}%' for _ in range(5))
    ash += (f'<i class="ash" style="left:{x:.1f}%;width:{sz:.0f}px;height:{sz * .8:.0f}px;clip-path:polygon({poly});'
            f'background:{pr.choice(["#3a332d", "#5a5149", "#26211d", "#7a6f63"])};--dx:{pr.uniform(-50, 50):.0f}px;--up:{pr.uniform(120, 260):.0f}px;'
            f'--rot:{pr.uniform(-260, 260):.0f}deg;animation-duration:{pr.uniform(2, 3.2):.2f}s;animation-delay:calc(var(--freeze,0s) + {pr.uniform(0, 2):.2f}s)"></i>')
settle = ''
for i in range(12):
    x = pr.uniform(25, 75); sz = pr.uniform(3, 7)
    settle += (f'<i class="settle" style="left:{x:.1f}%;width:{sz:.0f}px;height:{sz * .7:.0f}px;background:{pr.choice(["#4a423a", "#6d6358", "#2e2823"])};'
               f'--dx:{pr.uniform(-40, 40):.0f}px;--rot:{pr.uniform(-180, 180):.0f}deg;animation-delay:{pr.uniform(0, 1.8):.2f}s;animation-duration:{pr.uniform(3.5, 5.5):.2f}s"></i>')

# The sheet now grows with the phone, so the burn is drawn in proportions of the sheet, not px:
# the mask/char images are IH/H of the sheet tall and travel TRAVEL/H of it.
MS = IH / H * 100                                  # image height, % of the sheet
MP = (TRAVEL / H) / (IH / H - 1) * 100             # end position (bg/mask % semantics)
ETOP, EEND = E / H * 100, (E - TRAVEL) / H * 100   # spark/ash emitter, % of the sheet
BURN_CSS = f"""
.sheet-in{{-webkit-mask-image:{MASK};mask-image:{MASK};-webkit-mask-size:100% {MS:.2f}%;mask-size:100% {MS:.2f}%;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:0 0;mask-position:0 0}}
.char{{position:absolute;inset:0;pointer-events:none;background-image:{CHAR};background-size:100% {MS:.2f}%;background-repeat:no-repeat;background-position:0 0;opacity:0}}
.glow{{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none;background-image:{GLOW_IMG};background-size:100% {MS:.2f}%;background-repeat:no-repeat;background-position:0 0;opacity:0;mix-blend-mode:screen}}
.burning .sheet-in{{animation:burnmask {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
.burning .char{{opacity:1;animation:burnbg {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
.burning .glow{{opacity:1;animation:burnbg {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards,glowflick .18s steps(2) infinite}}
@keyframes burnmask{{to{{-webkit-mask-position:0 {MP:.2f}%;mask-position:0 {MP:.2f}%}}}}
@keyframes burnbg{{to{{background-position:0 {MP:.2f}%}}}}
@keyframes glowflick{{50%{{filter:brightness(1.25)}}}}
.tapeburn{{position:absolute;inset:0;pointer-events:none}}
.burning .tapeburn{{animation:tapefall 1s ease-in calc(var(--freeze,0s) + 3.1s) forwards}}
@keyframes tapefall{{0%{{opacity:1;filter:none}}40%{{opacity:1;filter:brightness(.5) sepia(1)}}100%{{opacity:0;transform:translateY(50px) rotate(18deg);filter:brightness(.2)}}}}
.burning .curl{{animation:curl {T}s ease-in calc(var(--freeze,0s)) forwards}}
@keyframes curl{{0%{{transform:rotate(-.4deg)}}40%{{transform:rotate(-1.2deg) translateY(-3px) scale(.995)}}100%{{transform:rotate(-2.6deg) translateY(-10px) scale(.98)}}}}
.emit{{position:absolute;left:0;width:100%;top:{ETOP:.2f}%;height:0;pointer-events:none;display:none}}
.burning .emit{{display:block;animation:emit {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
@keyframes emit{{from{{top:{ETOP:.2f}%}}to{{top:{EEND:.2f}%}}}}
.spark{{position:absolute;bottom:0;border-radius:50%;opacity:0;animation-name:spark;animation-iteration-count:infinite;animation-timing-function:ease-out}}
@keyframes spark{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}60%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),calc(var(--up) * -1)) scale(.4)}}}}
.ash{{position:absolute;bottom:0;opacity:0;animation-name:ashup;animation-iteration-count:infinite;animation-timing-function:cubic-bezier(.2,.6,.4,1)}}
@keyframes ashup{{0%{{opacity:0;transform:translate(0,0) rotate(0)}}12%{{opacity:.95}}100%{{opacity:0;transform:translate(var(--dx),calc(var(--up) * -1)) rotate(var(--rot))}}}}
.played{{position:absolute;left:0;top:0;bottom:0;overflow:hidden}}
.burning .dimmable{{opacity:.28;transition:opacity 1s ease}}
.burning .words{{animation:scorch {T}s ease-in calc(var(--freeze,0s)) forwards}}
@keyframes scorch{{60%{{color:#3b2a1c}}100%{{color:#1a0f08}}}}
.match{{position:relative;width:84px;height:84px;border-radius:50%;display:flex;align-items:center;justify-content:center;touch-action:none;user-select:none;flex-shrink:0}}
.match .ring{{position:absolute;inset:0;transform:rotate(-90deg)}}
.match .ring circle.p{{stroke-dasharray:252;stroke-dashoffset:252;transition:stroke-dashoffset .25s ease}}
.holding .match .ring circle.p{{stroke-dashoffset:0;transition:stroke-dashoffset 1.2s linear}}
.match .flame{{opacity:0;transform-origin:50% 100%;transform:scale(.3);transition:opacity .2s,transform .3s}}
.holding .match .flame,.burning .match .flame{{opacity:1;transform:scale(1);animation:flick .16s steps(2) infinite}}
@keyframes flick{{50%{{transform:scale(1.08,.94) skewX(3deg)}}}}
.holding .match{{animation:shake .12s linear infinite}}
@keyframes shake{{50%{{transform:translateX(1px) rotate(1deg)}}}}
/* nothing to burn yet (L11): the match waits, dim */
.isempty .match{{pointer-events:none}}
.isempty .match .ring circle:nth-child(2){{stroke-opacity:.35}}
.isempty .match .ring circle.p{{opacity:0}}
.isempty .match svg:not(.ring){{opacity:.38;filter:saturate(.3)}}
.isempty .match .flame{{display:none}}
.isempty .holdlabel{{color:{BOARDTXT} !important;opacity:.7}}
.settle{{position:absolute;top:24%;opacity:0;animation-name:settle;animation-timing-function:ease-in-out;animation-fill-mode:both}}
@keyframes settle{{0%{{opacity:0;transform:translate(0,-30px)}}15%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),240px) rotate(var(--rot))}}}}
.wisp{{stroke-dasharray:360;stroke-dashoffset:360;animation:wisp 4s ease-out .2s forwards}}
@keyframes wisp{{40%{{opacity:.55}}100%{{stroke-dashoffset:0;opacity:0;transform:translateY(-50px)}}}}
"""

TEXT = ("I'm tired of being the one who always says it's fine. I said yes to the trip again even though I didn't want to go, "
        "and I'll smile the whole time, and nobody will ever know how heavy it felt to say yes.")
LH = 30
lines_bg = (f'<div aria-hidden="true" style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 {LH - 1}px,rgba(96,120,150,.28) {LH - 1}px {LH}px);'
            f'background-position:0 72px;background-size:100% {LH}px;background-repeat:repeat-y;-webkit-mask:linear-gradient(transparent 72px,#000 72px)"></div>'
            f'<div aria-hidden="true" style="position:absolute;top:0;bottom:0;left:44px;width:1.5px;background:rgba(184,53,42,.45)"></div>')
write_body = (f'<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}">'
              f'<div class="words" data-slot="burnText" style="position:relative;{SERIF};font-size:17px;line-height:{LH}px;color:{INK};padding-top:13px">{TEXT}<span class="blink" style="color:{RED}">|</span></div></sc-if>')
voice_body = (f'<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div class="words" style="position:relative;padding-top:12px;color:{INK}">'
              f'<div style="{HAND};font-size:24px;line-height:1.2">a voice note, {{{{voiceLen}}}}</div>'
              f'<div style="margin-top:10px">{wave(250, 48, 61, "mbv", .0, head=False, sw=2)}</div>'
              f'<div style="display:flex;gap:22px;margin-top:12px;{TYPE};font-size:10.5px;letter-spacing:.16em"><button type="button" onClick="{{{{togglePlay}}}}" style="color:inherit;letter-spacing:inherit">{{{{playLabel}}}}</button><button type="button" onClick="{{{{reRecord}}}}" style="color:{PENCIL};letter-spacing:inherit">RE-RECORD</button></div>'
              f'<div style="{SERIF};font-style:italic;font-size:15.5px;line-height:1.45;color:{PENCIL};margin-top:12px">Only you hear it. When it burns, the recording goes with it.</div></div></sc-if>')
sheet_inner = (f'<div style="position:relative;{HAND};font-size:19px;color:{PENCIL};padding-left:30px;margin-top:-2px" data-slot="stamp">tonight, 11:48 pm</div>'
               f'<div style="position:relative;padding-left:30px">{write_body}{voice_body}</div>')


match = f'''<div class="matchpin" style="position:absolute;left:-12px;top:{H - 22}px;z-index:12;display:flex;align-items:center;gap:16px">
<button type="button" class="match" aria-label="Hold to burn" onMouseDown="{{{{startHold}}}}" onMouseUp="{{{{cancelHold}}}}" onMouseLeave="{{{{cancelHold}}}}" onTouchStart="{{{{startHold}}}}" onTouchEnd="{{{{cancelHold}}}}" onKeyDown="{{{{keyDown}}}}" onKeyUp="{{{{cancelHold}}}}">
<svg class="ring" width="84" height="84" viewBox="0 0 84 84" aria-hidden="true"><circle cx="42" cy="42" r="41" fill="{NIGHT2}"/><circle cx="42" cy="42" r="40" fill="none" stroke="{BOARDTXT}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="4 5"/><circle class="p" cx="42" cy="42" r="40" fill="none" stroke="{GLOW}" stroke-width="3" stroke-linecap="round"/></svg>
<svg width="32" height="54" viewBox="0 0 40 66" aria-hidden="true" style="overflow:visible;position:relative">
<g class="flame"><path d="M20 -14 C30 0 30 8 20 14 C10 8 10 0 20 -14 Z" fill="#FF8A3D"/><path d="M20 -4 C25 4 24 8 20 11 C16 8 15 4 20 -4 Z" fill="#FFE1A0"/></g>
<rect x="17" y="16" width="6" height="48" rx="1.5" fill="{KRAFT}"/><ellipse cx="20" cy="14" rx="6.5" ry="8" fill="{RED}"/></svg>
</button>
<div style="display:flex;flex-direction:column;gap:5px;padding-top:28px">
<span class="holdlabel" style="{HAND};font-size:25px;color:{CHALK};white-space:nowrap">{{{{holdLabel}}}}</span>
<sc-if value="{{{{hasWords}}}}"><span style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.6;color:{BOARDTXT};white-space:nowrap">PRESS AND HOLD.<br>ONCE IT BURNS, IT'S GONE.</span></sc-if>
<sc-if value="{{{{isEmpty}}}}">{inline_note('write something first.<br>even one word.', 'soft', 19)}</sc-if></div></div>'''
sheet = (f'<div style="position:relative;width:{W}px;height:{H}px"><div class="lift curl" style="position:relative;width:{W}px;height:{H}px;transform:rotate(-.8deg)">'
         f'<div class="sheet-in paper hi" style="position:absolute;inset:0;padding:26px 24px 26px 20px;clip-path:{deckle(W, H, seed=301)}">{lines_bg}{sheet_inner}<div class="char"></div></div>'
         f'<div class="glow"></div><div class="emit">{sparks}{ash}</div>'
         f'<span class="tapeburn">{tape(115, -13, 100, 26, rot=-3, seed=31)}</span></div>{match}</div>')

writing = f'''<sc-if value="{{{{notGone}}}}" hint-placeholder-val="{{{{ true }}}}">
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;padding:0 {MPAD}px 26px">
<div class="dimmable">
{h_hand("Say the thing you can't say out loud.", 31, wait='.2s', d='1.8s')}
<div class="rise" style="--w:1.1s;display:flex;justify-content:space-between;align-items:center;margin-top:12px">
{toggle(11, 16)}<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT};padding-bottom:6px">STAYS ON THIS DEVICE</span></div>
<sc-if value="{{{{isEmpty}}}}"><div style="{HAND};font-size:18px;color:{BOARDTXT};margin-top:8px">or tap speak, and just say it.</div></sc-if></div>
<div style="flex-grow:1;min-height:24px"></div>
<div class="rise" style="--w:.5s;margin:0 0 0 8px">{sheet}</div>
<div style="flex-grow:.45;flex-shrink:0;min-height:84px"></div>
</main>{mfooter()}</sc-if>'''

gone = f'''<sc-if value="{{{{gone}}}}" hint-placeholder-val="{{{{ false }}}}">
<div aria-hidden="true" style="position:absolute;left:0;top:0;width:{MW}px;height:100%;z-index:3;pointer-events:none">{settle}</div>
<svg aria-hidden="true" width="160" height="260" viewBox="0 0 200 320" style="position:absolute;left:50%;top:120px;margin-left:-80px;z-index:3;overflow:visible">
<path class="wisp" d="M100 300 C70 250 140 220 100 170 C60 120 130 90 100 30" fill="none" stroke="#9a9188" stroke-width="5" stroke-linecap="round" style="filter:blur(3px)"/></svg>
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;padding:0 {MPAD + 8}px 70px;text-align:center">
{h_hand("It's gone.", 66, color=PAPERHI, wait='.9s', d='1.5s')}
<div class="rise" style="--w:2.1s;{SERIF};font-style:italic;font-size:20px;line-height:1.45;color:rgba(233,233,231,.8);5;">You said it. You let it exist.<br>Now, let it go.</div>
<div class="rise" style="--w:2.5s;{MARK};font-size:25px;color:#F0A08F;transform:rotate(-2deg);margin-top:2px">you did good.</div>
<div class="rise" style="--w:3s;display:flex;flex-direction:column;align-items:center;gap:22px;margin-top:30px">
{chip('write another', onclick='again', seed=33, w=220)}{link('back home', 'V5MHome.dc.html')}</div>
</main>{mfooter()}</sc-if>'''

burn_body = f'''
{matmos()}
{mtopbar(crumb='burn', back='V5MHome.dc.html')}
{writing}
{gone}'''

burn_script = """constructor(props) { super(props); this.state = { stage: null, holding: false, mode: null }; }
componentWillUnmount() { clearTimeout(this.h); clearTimeout(this.t); }
renderVals() {
const stage = this.state.stage ?? this.props.stage ?? 'writing';
const mode = this.state.mode ?? this.props.mode ?? 'write';
const freeze = this.props.freeze ?? 0;
const doBurn = () => { this.setState({ stage: 'burning', holding: false }); clearTimeout(this.t); this.t = setTimeout(() => this.setState({ stage: 'gone' }), %d); };
const startHold = () => { if (stage !== 'writing') return; this.setState({ holding: true }); clearTimeout(this.h); this.h = setTimeout(doBurn, 1200); };
const cancelHold = () => { clearTimeout(this.h); if (this.state.holding) this.setState({ holding: false }); };
const cls = [stage === 'burning' ? 'burning' : '', this.state.holding ? 'holding' : '', freeze ? 'frozen' : ''].join(' ');
return {
rootClass: cls, rootStyle: freeze ? ('--freeze: -' + freeze + 's') : '',
notGone: stage !== 'gone', gone: stage === 'gone',
writeMode: mode === 'write', speakMode: mode === 'speak',
writeColor: mode === 'write' ? '#E9E9E7' : '%s', speakColor: mode === 'speak' ? '#E9E9E7' : '%s',
writeLine: mode === 'write' ? 1 : 0, speakLine: mode === 'speak' ? 1 : 0,
holdLabel: stage === 'burning' ? 'letting it go…' : (this.state.holding ? 'keep holding…' : 'hold to burn it'),
startHold, cancelHold,
keyDown: (e) => { if ((e.key === ' ' || e.key === 'Enter') && !this.state.holding) { e.preventDefault(); startHold(); } },
toWrite: () => this.setState({ mode: 'write' }), toSpeak: () => this.setState({ mode: 'speak' }),
again: () => this.setState({ stage: 'writing', holding: false }),
hasWords: true, isEmpty: false, voiceLen: '0:42', playLabel: '▶ PLAY'
};
}""" % (int(T * 1000 + 300), BOARDTXT, BOARDTXT)
frozen_css = ''.join(f'.frozen {c}{{animation-play-state:paused !important}}' for c in ['.sheet-in', '.char', '.glow', '.curl', '.emit', '.spark', '.ash', '.words', '.tapeburn'])
burn_props = '"stage":{"editor":"enum","options":["writing","burning","gone"],"default":"writing"},"mode":{"editor":"enum","options":["write","speak"],"default":"write"},"freeze":{"editor":"number","default":0}'
mpage('V5MBurn', 'Burn it', f'<div class="{{{{rootClass}}}}" style="{{{{rootStyle}}}};position:absolute;inset:0;display:flex;flex-direction:column">{burn_body}</div>',
      css=BURN_CSS + frozen_css, script=burn_script, props=burn_props)

def frame(name, title, attrs):
    SNDF = '' if 'freeze' in attrs else SND_HEAD
    MUTE = snd_marker({'mute': True}) if 'freeze' in attrs else ''
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>N0TRACE — {title}</title><script src="./support.js"></script>{SNDF}</head>
<body><x-dc><helmet>{FONTS}<style>body{{margin:0;background:{NIGHT}}}</style></helmet>
<div style="position:relative;width:{MW}px;height:{MH}px;background:{NIGHT};overflow:hidden"><dc-import name="V5MBurn" {attrs} hint-size="{MW}px,{MH}px"></dc-import>{MUTE}</div>
</x-dc><script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{MW},"height":{MH}}}}}'>
class Component extends DCLogic {{ renderVals() {{ return {{}}; }} }}
</script></body></html>"""
    open(OUT + name + '.dc.html', 'w').write(doc)
frame('V5MBurnVoice', 'Burn, voice note', 'mode="speak"')
frame('V5MBurnMid', 'Burning, frozen mid-way', 'stage="burning" freeze="1.7"')
frame('V5MBurnGone', "It's gone", 'stage="gone"')

# =====================================================================
# ECHOES (phone)
# =====================================================================
PINK = '#F0A08F'

def mnote(x, y, w, h, rot, seed, kind='', text='', fades='', heard=4, replies=0, to=None, faded=False, stamped=False, voice=None, size=None):
    half = w < 200
    size = size or (15 if half else 16.5)
    tohdr = f'<div style="{HAND};font-size:{19 if half else 21}px;color:{PENCIL};margin-bottom:4px">to {to},</div>' if to else ''
    if voice:
        ww = w - (92 if not half else 40)
        body = (f'<div style="{HAND};font-size:{19 if half else 22}px;color:{INK}">{voice[0]}</div>'
                f'<div style="display:flex;align-items:center;gap:10px;margin-top:10px">{"" if half else play_btn(38, f"pw{seed}")}'
                f'{wave(ww, 32, seed, f"ww{seed}", 0, head=False, sw=1.6)}</div>'
                f'<div style="display:flex;align-items:center;gap:8px;margin-top:8px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{INK}">{"▶ " if half else ""}VOICE · {voice[1]}</div>')
    else:
        body = f'<div style="{SERIF};font-size:{size}px;line-height:1.45;color:{INK}">{text}</div>'
    rep = f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">{replies} {"REPLY" if replies == 1 else "REPLIES"}</span>' if replies and not half else ''
    foot = (f'<div style="position:absolute;left:{16 if half else 20}px;right:{14 if half else 18}px;bottom:13px;display:flex;justify-content:space-between;align-items:center;gap:8px">'
            f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};text-transform:uppercase;white-space:nowrap">{fades}</span>'
            f'<span style="display:flex;align-items:center;gap:12px">{rep}<span class="heard" style="font-size:18px;gap:5px">{heart(size=15, fill=RED if stamped else "none")}{"" if half else "heard · "}{heard + (1 if stamped else 0)}</span></span></div>')
    st = f'<span class="stamp" style="right:12px;top:{h - 84}px;font-size:19px;border-width:2px;padding:1px 8px 0;--sw:1.4s">HEARD</span>' if stamped else ''
    tp = tape(w / 2 - 38 + random.Random(seed).uniform(-14, 14), -11, 76, 22, rot=random.Random(seed).uniform(-8, 8), seed=seed)
    op = 'opacity:.55;filter:saturate(.6);' if faded else ''
    if to:  # an unsent letter: addressed, lined, corner folded, no replies
        return (f'<a href="V5MUnsentOpen.dc.html" class="note" aria-label="An unsent letter to {to}" style="position:absolute;left:{x}px;top:{y}px;{op}transform:rotate({rot}deg)">'
                f'{letter_note(to, text, w, h, seed=seed, size=size, pad=(18, 20), hdr=21, foot=foot + st, tapes=tp, lh=24, ear=22)}</a>')
    pad = '18px 16px' if half else '20px 20px'
    return (f'<a href="V5MEchoThread.dc.html" class="note" style="position:absolute;left:{x}px;top:{y}px;{op}transform:rotate({rot}deg)">'
            f'{paper(tohdr + body + foot + st, w, h, kind=kind, seed=seed, pad=pad, tapes=tp)}</a>')

ROWS = [
    [dict(w=330, h=164, rot=-1.4, seed=601, kind='hi', voice=('left here at 1:12 am', '0:48'), fades='14h left', heard=12, replies=3)],
    [dict(w=158, h=176, rot=2.2, seed=602, text='I miss who I was before all of this.', fades='19h left', heard=14, stamped=True),
     dict(w=162, h=196, rot=-1.8, seed=603, kind='kraft', text="Three years sober today. Nobody knows. I'm proud of me.", fades='9h left', heard=33)],
    [dict(w=324, h=196, rot=-.9, seed=607, to='grandpa', text="I'm sorry I didn't pick up. I didn't know it was the last time you'd call.", fades='16h left', heard=6)],
    [dict(w=160, h=150, rot=-2.4, seed=605, voice=('a long day', '0:12'), fades='17h left', heard=4),
     dict(w=160, h=178, rot=1.6, seed=606, kind='hi', text='I keep rehearsing conversations that will never happen.', fades='6h left', heard=5)],
    [dict(w=318, h=158, rot=1.2, seed=604, kind='hi', text="I got the job. There's no one I can tell who'd actually be happy for me, so I'm telling you.", fades='21h left', heard=9, replies=2)],
    [dict(w=316, h=184, rot=1.3, seed=609, to='you know who', text="You were right about me. I just wasn't ready to hear it.", fades='3h left', heard=2)],
    [dict(w=162, h=204, rot=1.9, seed=608, kind='kraft', text="Some days I'm fine. Today was not one of those days, and that's okay too.", fades='12h left', heard=21),
     dict(w=158, h=186, rot=-2.2, seed=610, text="first snow in my city tonight. hope it's quiet where you are.", fades='41m left', heard=11, faded=True)],
]
wall, y = '', 16
for row in ROWS:
    if len(row) == 1:
        n = row[0]; x = (346 - n['w']) / 2 + random.Random(n['seed']).uniform(-6, 6)
        wall += mnote(x, y, **n); y += n['h'] + 34
    else:
        a, b = row
        wall += mnote(0, y + 6, **a) + mnote(346 - b['w'], y, **b); y += max(a['h'] + 6, b['h']) + 34
WALL_H = y
EH = 64 + 200 + WALL_H + 260

echoes = f'''
{matmos(EH)}
{mtopbar(crumb='echoes', back='V5MHome.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 {MPAD}px;display:flex;flex-direction:column">
{h_hand('Things people left here tonight.', 31)}
<div class="rise" style="--w:1s;{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.7;color:{BOARDTXT};margin-top:6px">ANONYMOUS · EACH ONE FADES IN 24 HOURS<br>TAP <span style="color:{PINK}">HEARD</span> IF IT REACHED YOU</div>
<div class="rise" style="--w:1.3s;display:flex;flex-direction:column;gap:8px;margin-top:14px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">
<span style="display:flex;align-items:center;gap:9px">{ico_note(CHALK, 16)}<span><span style="color:{CHALK}">ECHOES</span> · ANYONE CAN REPLY</span></span>
<span style="display:flex;align-items:center;gap:9px">{ico_letter(CHALK, 16)}<span><span style="color:{CHALK}">UNSENT LETTERS</span> · HEARD ONLY</span></span></div>
<div class="rise" style="--w:.7s;display:flex;align-items:center;justify-content:space-between;margin-top:16px">
<span style="{MARK};font-size:22px;color:{PINK};transform:rotate(-3deg)">your turn?</span>{chip('leave yours →', 'V5MEchoWrite.dc.html', seed=611, w=180)}</div>
<div class="rise" data-slot="wall" style="--w:.4s;position:relative;height:{WALL_H}px;margin-top:22px">{wall}</div>
<div class="rise" style="--w:1.4s;display:flex;flex-direction:column;align-items:center;gap:16px;padding:10px 0 34px">
<span style="{HAND};font-size:22px;color:{BOARDTXT}">that's everything from tonight.</span>
{chip('leave yours →', 'V5MEchoWrite.dc.html', seed=612, w=180, kind='kraft')}</div>
</main>
{mfooter()}'''
mpage('V5MEchoes', 'Echoes (scrolls)', echoes, h=EH, css=ECHO_CSS)

# ---------- leave yours (step one: echo or unsent letter; then write / speak) ----------
mpage('V5MEchoWrite', 'Leave yours', mwrite_board('echo'), css=ECHO_CSS + KIND_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)

# ---------- pinned ----------
pinned_note = paper(f'<div data-slot="pinnedText" style="{SERIF};font-size:19px;line-height:1.55;color:{INK};display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden">I keep rehearsing conversations that will never happen.</div>'
                    f'<div style="position:absolute;left:26px;bottom:18px;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">FADES IN 24H</div>',
                    290, 170, rot=2.5, seed=631, pad='24px 26px',
                    tapes=f'<span class="slap" style="animation-delay:1s">{tape(100, -13, 92, 26, rot=-4, seed=63)}</span>')
ghosts = ''.join(f'<span aria-hidden="true" style="position:absolute;left:{x}px;top:{y}px;width:{ww}px;height:{hh}px;background:#cfc6ad;opacity:.05;transform:rotate({rr}deg)"></span>'
                 for x, y, ww, hh, rr in [(14, 150, 96, 26, -8), (300, 120, 70, 22, 12), (8, 560, 110, 30, 6), (296, 600, 80, 24, -10)])
pinned = f'''
{matmos()}
{mtopbar(crumb='echoes', back='V5MEchoes.dc.html')}
<div style="position:absolute;inset:0;z-index:2;pointer-events:none">{ghosts}</div>
{mbody(f'''<div style="display:flex;flex-direction:column;align-items:center;gap:40px;text-align:center">
<div class="drop" style="animation-delay:.2s">{pinned_note}</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:12px">
{h_hand("It's up there now.", 38, color=PAPERHI, wait='1.4s')}
<div class="rise" style="--w:2.3s;{SERIF};font-style:italic;font-size:18px;line-height:1.45;color:rgba(233,233,231,.8);max-width:300px">Someone out there might need exactly these words tonight.</div>
</div></div>''', center=True)}
<div class="rise" style="--w:2.8s;display:flex;flex-direction:column">{mdock(mcta('see the wall', 'V5MEchoes.dc.html', 'paper', seed=632) + mtext('back home', 'V5MHome.dc.html'))}</div>
{mfooter()}'''
mpage('V5MEchoPinned', "It's up there now", pinned, css=ECHO_CSS)

# ---------- an echo: listen, heard, reply ----------
echo_inner = f'''
<div style="display:flex;justify-content:space-between;align-items:center;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">
<span>AN ECHO · {{{{modeLabel}}}}</span><span style="display:flex;align-items:center;gap:6px"><span style="width:6px;height:6px;border-radius:50%;border:1.5px solid {PENCIL}"></span>FADES IN {{{{fadesShort}}}}</span></div>
<sc-if value="{{{{isVoice}}}}" hint-placeholder-val="{{{{ true }}}}">
<div style="{HAND};font-size:26px;line-height:1.2;color:{INK};margin-top:12px">{{{{timeTitle}}}}</div>
<div style="display:flex;align-items:center;gap:14px;margin-top:18px">
<button type="button" class="pbtn" onClick="{{{{togglePlay}}}}" aria-label="{{{{playLabel}}}}">{play_btn(54, 'mpbe', True)}</button>
{wave(222, 58, 77, 'mwe', 0, main=True, sw=2)}</div>
<div data-slot="playTime" style="{TYPE};font-size:10.5px;letter-spacing:.1em;color:{INK};text-align:right;margin-top:8px">0:19 / 0:48</div>
<div style="{SERIF};font-style:italic;font-size:15.5px;line-height:1.5;color:{PENCIL};margin-top:10px">Just their voice. No transcript, and nothing left of it once it fades.</div></sc-if>
<sc-if value="{{{{isText}}}}" hint-placeholder-val="{{{{ false }}}}"><div style="{SERIF};font-size:18px;line-height:1.5;color:{INK};margin-top:14px;white-space:pre-wrap;overflow-wrap:anywhere">{{{{noteText}}}}</div></sc-if>
<div style="position:absolute;left:24px;right:24px;bottom:20px;border-top:1px dashed {RULE};padding-top:14px;display:flex;justify-content:space-between;align-items:center;gap:12px">
{heard_btn(23)}<span style="{TYPE};font-size:9px;letter-spacing:.12em;line-height:1.6;color:{PENCIL};text-transform:uppercase;text-align:right;max-width:150px">{{{{heardHint}}}}</span></div>
{stamp(26, 236, 26, '1.3s')}'''
echo = paper(echo_inner, 340, 362, rot=-1, kind='hi', seed=651, pad='24px 24px', tapes=tape(122, -13, 96, 26, rot=-3, seed=65), cls='thud').replace('height:362px', 'height:{{mcardH}}px', 1)

def mslip(name, when, kind, content, pk, seed, i):
    if kind == 'text':
        body = f'<div style="{SERIF};font-size:16.5px;line-height:1.45;color:{INK};margin-top:6px">{content}</div>'
        h = 112 if len(content) < 75 else 136
    else:
        body = (f'<div style="display:flex;align-items:center;gap:12px;margin-top:8px">{play_btn(36, f"mpr{i}")}'
                f'{wave(196, 32, seed, f"mwr{i}", 0, head=False, sw=1.6)}<span style="{TYPE};font-size:10px;letter-spacing:.1em;color:{INK}">{content}</span></div>')
        h = 96
    inner = (f'<div style="display:flex;justify-content:space-between;{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">'
             f'<span style="letter-spacing:.04em;font-size:11px">{name}</span><span>{"VOICE · " if kind == "voice" else ""}{when.upper()}</span></div>{body}')
    rot = [-.8, .9, -.5][i]
    off = [0, 16, 6][i]
    w = 324
    tp = tape([180, 40, 120][i], -10, 70, 20, rot=[-4, 3, -2][i], seed=seed)
    return f'<div class="slip rise" style="--w:{.9 + i * .25:.2f}s;margin-left:{off}px;transform:rotate({rot}deg)">{paper(inner, w, h, kind=pk, seed=seed + 30, pad="16px 20px", tapes=tp)}</div>'
slips = ''.join(mslip(*rr, i) for i, rr in enumerate(REPLIES))

mcomposer = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:center">{toggle(10, 14)}<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL};padding-bottom:6px">NO NAME ON IT</span></div>
<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}"><div style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:10px">
<div data-slot="replyText" style="{SERIF};font-size:17px;color:{PENCIL};font-style:italic">say something kind back<span class="blink" style="color:{RED};font-style:normal">|</span></div>
{chip('reply', kind='ink', w=96, seed=661, onclick='sendReply')}</div></sc-if>
<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div data-slot="replyVoice" style="display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:14px">
<div style="display:flex;align-items:center;gap:10px"><span style="width:11px;height:11px;border-radius:50%;background:{RED}"></span><span style="{HAND};font-size:21px;color:{INK}">hold to record a reply</span></div>
<span style="{TYPE};font-size:9px;letter-spacing:.12em;color:{PENCIL};text-align:right">UP TO<br>30 SEC</span></div></sc-if>''',
    346, 132, rot=.4, seed=662, pad='18px 20px', tapes=tape(136, -11, 80, 22, rot=2, seed=66))

TH = 1310
thread = f'''
{matmos(TH)}
{mtopbar(crumb='the wall', back='V5MEchoes.dc.html')}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 {MPAD}px;display:flex;flex-direction:column">
{h_hand('Left for whoever is up.', 29, wait='.2s')}
<div class="rise" style="--w:.9s;display:flex;align-items:flex-start;gap:9px;margin-top:6px">{ico_note(BOARDTXT, 15)}<div style="{TYPE};font-size:9.5px;letter-spacing:.14em;line-height:1.7;color:{BOARDTXT}">AN ECHO · ANONYMOUS · FADES IN {{{{fadesShort}}}}<br>ANYONE CAN LISTEN AND REPLY</div></div>
<div class="rise" style="--w:.5s;margin:24px 0 0 2px">{echo}</div>
<div class="rise" style="--w:2.2s;margin:22px 0 0 8px">{t_mark("heard is the only reaction.<br>no likes, no followers.", 20, PINK, 'transform:rotate(-1.5deg)')}</div>
<div class="rise" style="--w:.7s;display:flex;align-items:baseline;justify-content:space-between;margin-top:34px">
<span style="{HAND};font-size:28px;color:{CHALK}">{{{{repliesTitle}}}}</span>
<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">THEY FADE WITH IT</span></div>
<div data-slot="replies" style="display:flex;flex-direction:column;gap:22px;margin-top:20px">{slips}</div>
<div class="rise" style="--w:1.6s;margin-top:auto;margin-bottom:22px">{mcomposer}</div>
</main>
{mfooter()}'''
mpage('V5MEchoThread', 'An echo (scrolls)', f'<div class="{{{{rootClass}}}}" style="position:absolute;inset:0;display:flex;flex-direction:column">{thread}</div>',
      h=TH, css=ECHO_CSS, script=THREAD_SCRIPT, props=THREAD_PROPS)

write_manifest([
    {"file": "V5MBurn.dc.html", "title": "MB01 — Burn: write, hold the match", "w": 390, "h": 844, "row": "m_burn"},
    {"file": "V5MBurnVoice.dc.html", "title": "MB02 — Burn, voice note", "w": 390, "h": 844, "row": "m_burn"},
    {"file": "V5MBurnMid.dc.html", "title": "MB03 — Burning, frozen mid-way", "w": 390, "h": 844, "row": "m_burn"},
    {"file": "V5MBurnGone.dc.html", "title": "MB04 — It's gone", "w": 390, "h": 844, "row": "m_burn"},
    {"file": "V5MEchoes.dc.html", "title": "ME01 — The wall (scrolls)", "w": 390, "h": EH, "row": "m_echoes"},
    {"file": "V5MEchoWrite.dc.html", "title": "ME02 — Leave yours", "w": 390, "h": 844, "row": "m_echoes"},
    {"file": "V5MEchoPinned.dc.html", "title": "ME03 — It's up there now", "w": 390, "h": 844, "row": "m_echoes"},
    {"file": "V5MEchoThread.dc.html", "title": "ME04 — An echo: listen, Heard, reply (scrolls)", "w": 390, "h": TH, "row": "m_echoes"},
])
print('m burn+echo ok', EH, TH)
