from gen5 import *
import urllib.parse

W, H = 600, 320          # the sheet (fits the note + ~40px)
T = 4.4                  # burn duration (s)
E = H + 90               # where the edge sits inside the mask image
IH = 2 * H + 120         # mask image height
TRAVEL = E + 40

# ---------- the burn edge, generated once ----------
r = random.Random(42)
xs = list(range(0, W + 8, 8))
edge = []
phase = r.uniform(0, 6)
for x in xs:
    y = (math.sin(x / 47 + phase) * 9 + math.sin(x / 19 + 1.3) * 5 + math.sin(x / 7.3) * 2.2
         + r.uniform(-3, 3))
    edge.append((x, y))
# a couple of tongues of fire that run ahead
for cx, depth, wd in [(130, -38, 60), (395, -30, 48), (520, -22, 40)]:
    edge = [(x, y + depth * math.exp(-((x - cx) / wd) ** 2)) for x, y in edge]

def epath(off=0, base=None):
    base = E if base is None else base
    return ' '.join(('M' if i == 0 else 'L') + f'{x} {base + y + off:.1f}' for i, (x, y) in enumerate(edge))

def svg_url(svg):
    svg = svg.replace('%23', '#')
    return 'url("data:image/svg+xml;utf8,' + urllib.parse.quote(svg, safe=" =:/;,'()-.") + '")'

HOLES = [(210, E - 70, 9), (300, E - 52, 6), (460, E - 84, 11), (80, E - 46, 5), (560, E - 58, 7)]
def blob(cx, cy, rr, seed, k=1.0, n=13):
    """An irregular charred hole: a lumpy, uneven outline (never a clean circle)."""
    q = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + q.uniform(-.18, .18)
        rad = rr * k * q.uniform(.62, 1.28) * (1.25 if i % 4 == 0 else 1)
        pts.append((cx + math.cos(a) * rad * 1.15, cy + math.sin(a) * rad * .9))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'
holes = ''.join(' ' + blob(cx, cy, rr, 900 + i) for i, (cx, cy, rr) in enumerate(HOLES))
pts_rev = ' '.join(f'L{x} {E + y:.1f}' for x, y in reversed(edge))
MASK = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}'>"
               f"<path fill-rule='evenodd' fill='white' d='M0 0 L{W} 0 {pts_rev} Z{holes}'/></svg>")
# scorched rims: dark brown at the hole, fading to nothing; no bright ring
rim_defs = ''.join(f"<radialGradient id='h{i}' gradientUnits='userSpaceOnUse' cx='{cx}' cy='{cy}' r='{rr * 2.3:.1f}'>"
                   f"<stop offset='0' stop-color='%23140904'/><stop offset='.42' stop-color='%23241005' stop-opacity='.92'/>"
                   f"<stop offset='.68' stop-color='%235e3312' stop-opacity='.4'/><stop offset='1' stop-color='%237a4a1e' stop-opacity='0'/></radialGradient>"
                   for i, (cx, cy, rr) in enumerate(HOLES))
hole_rims = ''.join(f"<path d='{blob(cx, cy, rr, 900 + i, k=2.1)}' fill='url(%23h{i})' filter='url(%23rb)'/>" for i, (cx, cy, rr) in enumerate(HOLES))
band_top = ' '.join(f'L{x} {E + y - 46:.1f}' for x, y in edge)
CHAR = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}'>"
               f"<defs><linearGradient id='g' x1='0' y1='{E - 60}' x2='0' y2='{E + 10}' gradientUnits='userSpaceOnUse'>"
               f"<stop offset='0' stop-color='%237a4a1e' stop-opacity='0'/><stop offset='.55' stop-color='%236b3a14' stop-opacity='.45'/>"
               f"<stop offset='.85' stop-color='%232a1306' stop-opacity='.95'/><stop offset='1' stop-color='%23120804'/></linearGradient>"
               f"<filter id='b'><feGaussianBlur stdDeviation='2'/></filter><filter id='rb' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='1.4'/></filter>{rim_defs}</defs>"
               f"<path d='M{edge[0][0]} {E + edge[0][1] - 46:.1f} {band_top} {pts_rev} Z' fill='url(%23g)'/>"
               f"{hole_rims}"
               f"<path d='{epath(-2)}' fill='none' stroke='%23FF7A2E' stroke-width='6' filter='url(%23b)'/>"
               f"<path d='{epath(-1.5)}' fill='none' stroke='%23FFD27A' stroke-width='1.6'/></svg>")
GLOW_IMG = svg_url(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{IH}'>"
                   f"<defs><filter id='b' x='-20%' y='-50%' width='140%' height='200%'><feGaussianBlur stdDeviation='12'/></filter></defs>"
                   f"<path d='{epath(4)}' fill='none' stroke='%23FF8A3D' stroke-width='16' opacity='.35' filter='url(%23b)'/>"
                   f"<path d='{epath(12)}' fill='none' stroke='%23FF5A2E' stroke-width='18' opacity='.09' filter='url(%23b)'/></svg>")

# ---------- particles ----------
pr = random.Random(7)
sparks = ''
for i in range(30):
    x = pr.uniform(2, 98); sz = pr.choice([2, 2, 3, 3, 4]); c = pr.choice(['#FFB347', '#FF7A2E', '#FFD27A'])
    sparks += (f'<i class="spark" style="left:{x:.1f}%;width:{sz}px;height:{sz}px;background:{c};box-shadow:0 0 8px {c};'
               f'--dx:{pr.uniform(-40, 40):.0f}px;--up:{pr.uniform(70, 190):.0f}px;animation-duration:{pr.uniform(.9, 1.7):.2f}s;'
               f'animation-delay:calc(var(--freeze,0s) + {pr.uniform(0, 1.6):.2f}s)"></i>')
ash = ''
for i in range(22):
    x = pr.uniform(0, 100); sz = pr.uniform(4, 11)
    poly = ','.join(f'{pr.uniform(0, 100):.0f}% {pr.uniform(0, 100):.0f}%' for _ in range(5))
    ash += (f'<i class="ash" style="left:{x:.1f}%;width:{sz:.0f}px;height:{sz * .8:.0f}px;clip-path:polygon({poly});'
            f'background:{pr.choice(["#3a332d", "#5a5149", "#26211d", "#7a6f63"])};--dx:{pr.uniform(-80, 80):.0f}px;--up:{pr.uniform(180, 380):.0f}px;'
            f'--rot:{pr.uniform(-260, 260):.0f}deg;animation-duration:{pr.uniform(2, 3.4):.2f}s;animation-delay:calc(var(--freeze,0s) + {pr.uniform(0, 2):.2f}s)"></i>')
settle = ''
for i in range(14):
    x = pr.uniform(30, 70); sz = pr.uniform(3, 8)
    settle += (f'<i class="settle" style="left:{x:.1f}%;width:{sz:.0f}px;height:{sz * .7:.0f}px;background:{pr.choice(["#4a423a", "#6d6358", "#2e2823"])};'
               f'--dx:{pr.uniform(-60, 60):.0f}px;--rot:{pr.uniform(-180, 180):.0f}deg;animation-delay:{pr.uniform(0, 1.8):.2f}s;animation-duration:{pr.uniform(3.5, 5.5):.2f}s"></i>')

css = f"""
.sheet-in{{-webkit-mask-image:{MASK};mask-image:{MASK};-webkit-mask-size:{W}px {IH}px;mask-size:{W}px {IH}px;-webkit-mask-repeat:no-repeat;mask-repeat:no-repeat;-webkit-mask-position:0 0;mask-position:0 0}}
.char{{position:absolute;inset:0;pointer-events:none;background-image:{CHAR};background-size:{W}px {IH}px;background-repeat:no-repeat;background-position:0 0;opacity:0}}
.glow{{position:absolute;left:0;top:0;width:{W}px;height:{H + 26}px;pointer-events:none;background-image:{GLOW_IMG};background-size:{W}px {IH}px;background-repeat:no-repeat;background-position:0 0;opacity:0;mix-blend-mode:screen}}
.burning .sheet-in{{animation:burnmask {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
.burning .char{{opacity:1;animation:burnbg {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
.burning .glow{{opacity:1;animation:burnbg {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards,glowflick .18s steps(2) infinite}}
@keyframes burnmask{{to{{-webkit-mask-position:0 -{TRAVEL}px;mask-position:0 -{TRAVEL}px}}}}
@keyframes burnbg{{to{{background-position:0 -{TRAVEL}px}}}}
@keyframes glowflick{{50%{{filter:brightness(1.25)}}}}
.tapeburn{{position:absolute;inset:0;pointer-events:none}}
.burning .tapeburn{{animation:tapefall 1.1s ease-in calc(var(--freeze,0s) + 3.5s) forwards}}
@keyframes tapefall{{0%{{opacity:1;filter:none}}40%{{opacity:1;filter:brightness(.5) sepia(1)}}100%{{opacity:0;transform:translateY(60px) rotate(18deg);filter:brightness(.2)}}}}
.burning .curl{{animation:curl {T}s ease-in calc(var(--freeze,0s)) forwards}}
@keyframes curl{{0%{{transform:rotate(-.8deg)}}40%{{transform:rotate(-1.6deg) translateY(-4px) scale(.995)}}100%{{transform:rotate(-3deg) translateY(-14px) scale(.98)}}}}
.emit{{position:absolute;left:0;width:{W}px;top:{E}px;height:0;pointer-events:none;display:none}}
.burning .emit{{display:block;animation:emit {T}s cubic-bezier(.42,.02,.38,1) calc(var(--freeze,0s)) forwards}}
@keyframes emit{{to{{transform:translateY(-{TRAVEL}px)}}}}
.spark{{position:absolute;bottom:0;border-radius:50%;opacity:0;animation-name:spark;animation-iteration-count:infinite;animation-timing-function:ease-out}}
@keyframes spark{{0%{{opacity:0;transform:translate(0,0)}}10%{{opacity:1}}60%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),calc(var(--up) * -1)) scale(.4)}}}}
.ash{{position:absolute;bottom:0;opacity:0;animation-name:ashup;animation-iteration-count:infinite;animation-timing-function:cubic-bezier(.2,.6,.4,1)}}
@keyframes ashup{{0%{{opacity:0;transform:translate(0,0) rotate(0)}}12%{{opacity:.95}}100%{{opacity:0;transform:translate(var(--dx),calc(var(--up) * -1)) rotate(var(--rot))}}}}
.heat{{position:absolute;inset:-30%;pointer-events:none;background:radial-gradient(closest-side at 50% 60%,rgba(255,140,60,.15),rgba(255,90,40,.05) 45%,transparent 100%);mix-blend-mode:screen;opacity:0}}
.burning .heat{{animation:heat {T}s ease calc(var(--freeze,0s)) forwards}}
@keyframes heat{{0%{{opacity:0}}20%{{opacity:.8}}80%{{opacity:1}}100%{{opacity:.2}}}}
.burning .dimmable{{opacity:.28;transition:opacity 1s ease}}
.burning .words{{animation:scorch {T}s ease-in calc(var(--freeze,0s)) forwards}}
@keyframes scorch{{60%{{color:#3b2a1c}}100%{{color:#1a0f08}}}}
/* hold to burn */
.match{{position:relative;width:104px;height:104px;border-radius:50%;display:flex;align-items:center;justify-content:center;touch-action:none;user-select:none}}
.match .ring{{position:absolute;inset:0;transform:rotate(-90deg)}}
.match .ring circle.p{{stroke-dasharray:314;stroke-dashoffset:314;transition:stroke-dashoffset .25s ease}}
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
/* the ending */
.bloom{{position:absolute;left:50%;top:46%;width:1400px;height:1100px;margin:-550px 0 0 -700px;border-radius:50%;pointer-events:none;mix-blend-mode:screen;
background:radial-gradient(circle,rgba(255,214,160,.75),rgba(255,160,100,.28) 28%,rgba(255,120,80,.06) 55%,transparent 70%);animation:bloom 3.2s cubic-bezier(.2,.7,.2,1) both;z-index:2}}
@keyframes bloom{{0%{{opacity:0;transform:scale(.25)}}22%{{opacity:1}}100%{{opacity:.38;transform:scale(1)}}}}
.settle{{position:absolute;top:30%;opacity:0;animation-name:settle;animation-timing-function:ease-in-out;animation-fill-mode:both}}
@keyframes settle{{0%{{opacity:0;transform:translate(0,-40px)}}15%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),300px) rotate(var(--rot))}}}}
.wisp{{stroke-dasharray:420;stroke-dashoffset:420;animation:wisp 4s ease-out .2s forwards}}
@keyframes wisp{{40%{{opacity:.55}}100%{{stroke-dashoffset:0;opacity:0;transform:translateY(-60px)}}}}
"""

# ---------- pieces ----------
TEXT = ("I'm tired of being the one who always says it's fine. I said yes to the trip again even though I didn't want to go, "
        "and I'll smile the whole time, and nobody will ever know how heavy it felt to say yes.")

lines_bg = (f'<div aria-hidden="true" style="position:absolute;inset:0;background-image:repeating-linear-gradient(to bottom,transparent 0 37px,rgba(96,120,150,.28) 37px 38px);'
            f'background-position:0 92px;background-size:100% 38px;background-repeat:repeat-y;-webkit-mask:linear-gradient(transparent 92px,#000 92px)"></div>'
            f'<div aria-hidden="true" style="position:absolute;top:0;bottom:0;left:66px;width:1.5px;background:rgba(184,53,42,.45)"></div>')

write_body = (f'<sc-if value="{{{{writeMode}}}}" hint-placeholder-val="{{{{ true }}}}">'
              f'<div class="words" data-slot="burnText" style="position:relative;{SERIF};font-size:22px;line-height:38px;color:{INK};padding-top:16px">{TEXT}<span class="blink" style="color:{RED}">|</span></div></sc-if>')
wave_pts = ' '.join(f'{x},{40 + math.sin(x / 9) * (8 + 22 * abs(math.sin(x / 41))) * (1 if (x // 3) % 2 else -1) * random.Random(x).uniform(.4, 1):.1f}' for x in range(0, 420, 3))
voice_body = (f'<sc-if value="{{{{speakMode}}}}" hint-placeholder-val="{{{{ false }}}}"><div class="words" style="position:relative;padding-top:12px;color:{INK}">'
              f'<div style="{HAND};font-size:28px;line-height:1.2">a voice note, {{{{voiceLen}}}}</div>'
              f'<svg width="420" height="80" viewBox="0 0 420 80" style="margin-top:2px;display:block;height:58px" preserveAspectRatio="none" aria-hidden="true"><polyline points="{wave_pts}" fill="none" stroke="{INK}" stroke-width="2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>'
              f'<div style="display:flex;gap:26px;margin-top:10px;{TYPE};font-size:12px;letter-spacing:.16em"><button type="button" onClick="{{{{togglePlay}}}}" style="color:inherit;letter-spacing:inherit">{{{{playLabel}}}}</button><button type="button" onClick="{{{{reRecord}}}}" style="color:{PENCIL};letter-spacing:inherit">RE-RECORD</button></div>'
              f'<div style="{SERIF};font-style:italic;font-size:18px;color:{PENCIL};margin-top:12px">Only you hear it. When it burns, the recording goes with it.</div></div></sc-if>')

sheet_inner = f'''<div style="position:relative;{HAND};font-size:24px;color:{PENCIL};padding-left:46px;margin-top:-4px" data-slot="stamp">tonight, 11:48 pm</div>
<div style="position:relative;padding-left:46px">{write_body}{voice_body}</div>'''



MS = 104   # the match disc
match = f'''<div class="matchpin" style="position:absolute;left:-34px;top:{H - 22}px;z-index:12;display:flex;align-items:center;gap:22px">
<button type="button" class="match" aria-label="Hold to burn" onMouseDown="{{{{startHold}}}}" onMouseUp="{{{{cancelHold}}}}" onMouseLeave="{{{{cancelHold}}}}" onTouchStart="{{{{startHold}}}}" onTouchEnd="{{{{cancelHold}}}}" onKeyDown="{{{{keyDown}}}}" onKeyUp="{{{{cancelHold}}}}">
<svg class="ring" width="104" height="104" viewBox="0 0 104 104" aria-hidden="true"><circle cx="52" cy="52" r="51" fill="{NIGHT2}"/><circle cx="52" cy="52" r="50" fill="none" stroke="{BOARDTXT}" stroke-opacity=".55" stroke-width="1.5" stroke-dasharray="4 5"/><circle class="p" cx="52" cy="52" r="50" fill="none" stroke="{GLOW}" stroke-width="3" stroke-linecap="round"/></svg>
<svg width="40" height="66" viewBox="0 0 40 66" aria-hidden="true" style="overflow:visible;position:relative">
<g class="flame"><path d="M20 -14 C30 0 30 8 20 14 C10 8 10 0 20 -14 Z" fill="#FF8A3D"/><path d="M20 -4 C25 4 24 8 20 11 C16 8 15 4 20 -4 Z" fill="#FFE1A0"/></g>
<rect x="17" y="16" width="6" height="48" rx="1.5" fill="{KRAFT}"/><ellipse cx="20" cy="14" rx="6.5" ry="8" fill="{RED}"/></svg>
</button>
<div style="display:flex;flex-direction:column;gap:6px;padding-top:34px">
<span class="holdlabel" style="{HAND};font-size:30px;color:{CHALK};white-space:nowrap">{{{{holdLabel}}}}</span>
<div style="display:grid;align-items:start"><div style="grid-area:1/1;transition:opacity .35s ease;opacity:{{{{wordsOp}}}}" aria-hidden="{{{{wordsHidden}}}}"><span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{BOARDTXT};white-space:nowrap">PRESS AND HOLD · OR HOLD SPACE</span></div><div style="grid-area:1/1;transition:opacity .35s ease;opacity:{{{{emptyOp}}}}" aria-hidden="{{{{emptyHidden}}}}">{inline_note('write something first. even one word.', 'soft', 23)}</div></div></div></div>'''

sheet = (f'<div style="position:relative;width:{W}px;height:{H}px"><div class="heat"></div><div class="lift curl" style="position:relative;width:{W}px;height:{H}px;transform:rotate(-.8deg)">'
         f'<div class="sheet-in paper hi" style="position:absolute;inset:0;padding:40px 44px 40px 30px;clip-path:{deckle(W, H, seed=301)}">{lines_bg}{sheet_inner}<div class="char"></div></div>'
         f'<div class="glow"></div>'
         f'<div class="emit">{sparks}{ash}</div>'
         f'<span class="tapeburn">{tape(240, -15, 120, 30, rot=-3, seed=31)}</span>'
         f'</div>{match}</div>')

toggle = f'''<div style="display:flex;gap:22px;align-items:center;{TYPE};font-size:12px;letter-spacing:.18em">
<button type="button" onClick="{{{{toWrite}}}}" style="color:{{{{writeColor}}}};position:relative;padding-bottom:6px">WRITE<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{{{{writeLine}}}}"></span></button>
<span style="color:{BOARDTXT};opacity:.5">/</span>
<button type="button" onClick="{{{{toSpeak}}}}" style="color:{{{{speakColor}}}};position:relative;padding-bottom:6px">SPEAK<span style="position:absolute;left:0;right:0;bottom:0;height:2px;background:{RED};opacity:{{{{speakLine}}}}"></span></button></div>'''

writing = f'''<sc-if value="{{{{notGone}}}}" hint-placeholder-val="{{{{ true }}}}">
<main style="position:relative;z-index:10;flex-grow:1;display:flex;align-items:center;justify-content:center;gap:100px;padding-bottom:40px">
<div class="dimmable" style="width:440px;display:flex;flex-direction:column;gap:30px">
{h_hand("Say the thing you can't say out loud.", 52, wait='.2s', d='2s')}
<div class="rise" style="--w:1.2s;{TYPE};font-size:12px;letter-spacing:.16em;line-height:1.9;color:{BOARDTXT}">IT STAYS ON THIS DEVICE.<br>WHEN YOU BURN IT, IT'S GONE. FOR GOOD.</div>
<div class="rise" style="--w:1.5s">{toggle}<div style="{HAND};font-size:21px;color:{BOARDTXT};margin-top:14px;transition:opacity .35s ease;opacity:{{{{emptyOp}}}}" aria-hidden="{{{{emptyHidden}}}}">or tap speak, and just say it.</div></div>
</div>
<div class="rise" style="--w:.5s;margin-bottom:60px">{sheet}</div>
</main></sc-if>'''

gone = f'''<sc-if value="{{{{gone}}}}" hint-placeholder-val="{{{{ false }}}}">
<div class="bloom"></div>
<div aria-hidden="true" style="position:absolute;left:50%;top:0;width:900px;margin-left:-450px;height:100%;z-index:3;pointer-events:none">{settle}</div>
<svg aria-hidden="true" width="200" height="320" viewBox="0 0 200 320" style="position:absolute;left:50%;top:180px;margin-left:-100px;z-index:3;overflow:visible">
<path class="wisp" d="M100 300 C70 250 140 220 100 170 C60 120 130 90 100 30" fill="none" stroke="#9a9188" stroke-width="5" stroke-linecap="round" style="filter:blur(3px)"/></svg>
<main style="position:relative;z-index:10;flex-grow:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;padding-bottom:50px">
{h_hand("It's gone.", 96, color=PAPERHI, wait='.9s', d='1.6s')}
<div class="rise" style="--w:2.1s;{SERIF};font-style:italic;font-size:24px;color:rgba(233,233,231,.8);5">You said it. You let it exist. Now, let it go.</div>
<div class="rise" style="--w:2.5s;{MARK};font-size:26px;color:#F0A08F;transform:rotate(-2deg);margin-top:4px">you did good.</div>
<div class="rise" style="--w:3s;display:flex;align-items:center;gap:34px;margin-top:30px">
{chip('write another', onclick='again', seed=33, w=220)}{link('back home', 'V5Home.dc.html')}</div>
</main></sc-if>'''

body = f'''
{atmos(leak(-240, 580, 640, GLOW, 0) + leak(1150, -240, 520, ROSE, 4) + '<div class="flare"></div>')}
{topbar(crumb='burn')}
{writing}
{gone}'''

script = """constructor(props) { super(props); this.state = { stage: null, holding: false, mode: null }; }
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
hasWords: true, isEmpty: false, wordsOp: 1, emptyOp: 0, wordsHidden: 'false', emptyHidden: 'true', voiceLen: '0:42', playLabel: '▶ PLAY'
};
}""" % (int(T * 1000 + 300), BOARDTXT, BOARDTXT)

frozen_css = ''.join(f'.frozen {c}{{animation-play-state:paused !important}}' for c in ['.sheet-in','.char','.glow','.curl','.emit','.spark','.ash','.heat','.words','.tapeburn'])
props = '"stage":{"editor":"enum","options":["writing","burning","gone"],"default":"writing"},"mode":{"editor":"enum","options":["write","speak"],"default":"write"},"freeze":{"editor":"number","default":0}'

def build(name, title):
    doc_body = f'<div class="{{{{rootClass}}}}" style="{{{{rootStyle}}}};position:absolute;inset:0;display:flex;flex-direction:column">{body}</div>'
    page(name, title, doc_body, css=css + frozen_css, script=script, props=props)

build('V5Burn', 'Burn it')

# static frames that import the live board
def frame(name, title, attrs):
    SNDF = '' if 'freeze' in attrs else SND_HEAD
    MUTE = snd_marker({'mute': True}) if 'freeze' in attrs else ''
    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>N0TRACE — {title}</title><script src="./support.js"></script>{SNDF}</head>
<body><x-dc><helmet>{FONTS}<style>body{{margin:0;background:{NIGHT}}}</style></helmet>
<div style="width:1440px;height:900px;background:{NIGHT}"><dc-import name="V5Burn" {attrs} hint-size="1440px,900px"></dc-import>{MUTE}</div>
</x-dc><script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1440,"height":900}}}}'>
class Component extends DCLogic {{ renderVals() {{ return {{}}; }} }}
</script></body></html>"""
    open(OUT + name + '.dc.html', 'w').write(doc)
frame('V5BurnMid', 'Burning, frozen mid-way', 'stage="burning" freeze="1.7"')
frame('V5BurnGone', 'Burnt, the ending', 'stage="gone"')
frame('V5BurnVoice', 'Burn, voice note', 'mode="speak"')
print('burn ok', len(MASK), len(CHAR))
