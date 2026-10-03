from gen5 import *

def hrow(activity, feature, href, last=False, sw=260):
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    return (f'<a href="{href}" class="row" style="height:64px;{bb}--sw:{sw}px">'
            f'<span style="position:relative"><span style="{HAND};font-size:30px;color:{INK}">{activity}</span>'
            f'<span class="scribble">{underline(sw, RED, 2.5, cls="", seed=len(activity))}</span></span>'
            f'<span class="go" style="display:flex;align-items:center;gap:12px;{TYPE};font-weight:700;font-size:12px;letter-spacing:.18em;color:{PENCIL}">{feature}<span style="color:{INK};font-size:15px">→</span></span></a>')


# ---------- a small sealed letter (the capsule envelope, pocket-sized) ----------
def envelope(w=110, rot=6, seed=231, uid='env', tape_on=True):
    """Kraft envelope seen from the back: flap V, red wax seal where the flap meets."""
    h = round(w * .64)
    vy = h * .58
    r = w * .13
    seal = (f'<defs>{ROUGH.format(i=uid, s=11, sc=4)}'
            f'<radialGradient id="g{uid}" cx="40%" cy="35%"><stop offset="0" stop-color="#D4513F"/><stop offset=".7" stop-color="{RED}"/><stop offset="1" stop-color="#7d1f17"/></radialGradient></defs>'
            f'<g filter="url(#rough{uid})"><circle cx="{w / 2:.1f}" cy="{vy:.1f}" r="{r:.1f}" fill="url(#g{uid})"/>'
            f'<circle cx="{w / 2:.1f}" cy="{vy:.1f}" r="{r * .7:.1f}" fill="none" stroke="#8e2a20" stroke-width="1.3"/></g>')
    svg = (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true" style="position:absolute;inset:0;overflow:visible">'
           f'<path d="M3 3 L{w / 2:.1f} {vy:.1f} L{w - 3} 3 Z" fill="#CDB892" opacity=".85"/>'
           f'<path d="M3 3 L{w / 2:.1f} {vy:.1f} L{w - 3} 3" fill="none" stroke="rgba(80,55,25,.45)" stroke-width="1.2" stroke-linejoin="round"/>'
           f'<path d="M3 {h - 3} L{w * .42:.1f} {h * .62:.1f} M{w - 3} {h - 3} L{w * .58:.1f} {h * .62:.1f}" fill="none" stroke="rgba(80,55,25,.25)" stroke-width="1"/>'
           f'{seal}</svg>')
    tp = tape(-14, -6, round(w * .42), 18, rot=-32, seed=seed + 1) if tape_on else ''
    return (f'<div class="lift" style="position:relative;width:{w}px;height:{h}px;transform:rotate({rot}deg);flex-shrink:0">'
            f'<div class="paper kraft" style="position:absolute;inset:0;background-color:{KRAFT};clip-path:{deckle(w, h, amp=1.3, step=11, seed=seed)}"></div>'
            f'{svg}{tp}</div>')

def letter_arrived():
    """Desktop: 'a letter from you arrived', with a hand-drawn arrow down to the envelope pinned under it. One link."""
    arrow = (f'<svg width="120" height="90" viewBox="0 0 120 90" aria-hidden="true" style="position:absolute;left:232px;top:30px;overflow:visible">'
             f'<path class="draw" style="--len:120;--d:.9s;--w:1.4s" d="M40 4 C66 10 74 34 62 54 C56 63 48 68 36 71" fill="none" stroke="{SOFTRED}" stroke-width="2" stroke-linecap="round"/>'
             f'<path class="draw" style="--len:36;--d:.4s;--w:2.2s" d="M47 63 L35 71 L46 79" fill="none" stroke="{SOFTRED}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    return (f'<a href="V5CapsuleOpen.dc.html" class="chip" aria-label="A letter from you arrived. Open it." '
            f'style="position:absolute;right:64px;top:98px;z-index:20;display:block;width:330px;height:150px">'
            f'<span style="position:absolute;left:0;top:0;{MARK};font-size:24px;color:{SOFTRED};white-space:nowrap">a letter from you arrived</span>'
            f'{arrow}<span class="rise" style="--w:.9s;position:absolute;left:150px;top:62px">{envelope(112, 6, uid="denv")}</span></a>')


left_inner = f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('on your own', 24)}<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">ANY TIME</span></div>
<div style="{HAND};font-size:46px;line-height:1.15;margin-top:6px">Let something out</div>
<div style="{SERIF};font-size:18px;color:{PENCIL};margin-top:4px">Just you. Nobody else needs to be online.</div>
<nav aria-label="Let something out" style="margin-top:18px;border-top:1px dashed {RULE}">
{hrow('I need to get this out', 'BURN', 'V5Burn.dc.html', sw=300)}
{hrow('Leave it somewhere', 'ECHO · LETTER', 'V5Echoes.dc.html', sw=240)}
{hrow('Hear it again later', 'TIME CAPSULE', 'V5Capsule.dc.html', True, sw=240)}
</nav>'''

right_open = f'''<nav aria-label="Talk to someone" style="margin-top:18px;border-top:1px dashed rgba(34,30,26,.25)">
{hrow('I need to talk', 'TALK POD', 'V5Matching.dc.html', sw=190)}
{hrow('I can listen', 'LISTEN POD', 'V5Listener.dc.html', sw=170)}
{hrow('Just talk', 'OPEN POD', 'V5Rooms.dc.html', sw=120)}
{hrow('Join a small group', 'GROUP POD', 'V5Question.dc.html', True, sw=250)}
</nav>'''
right_closed = f'''<div style="margin-top:18px;border-top:1px dashed rgba(34,30,26,.25);padding-top:30px;display:flex;align-items:center;gap:26px">
{rabbit(96, INK, mood='sleep', uid='hs')}
<div style="display:flex;flex-direction:column;gap:10px">
<div style="{HAND};font-size:32px;line-height:1.2">Everyone's asleep.<br>Back at 10pm.</div>
<div style="{TYPE};font-size:11px;letter-spacing:.14em;color:{INK}">1:1 CHATS · LISTENING · SMALL GROUPS</div>
<a href="V5Asleep.dc.html" class="ul" style="{TYPE};font-weight:700;font-size:12px;letter-spacing:.16em;color:{INK};align-self:flex-start;margin-top:4px">REMIND ME →</a>
</div></div>'''

def right_inner(open_):
    status = (f'<span style="display:flex;align-items:center;gap:8px;{TYPE};font-size:11px;letter-spacing:.16em;color:{INK}"><span class="pulse-dot"></span>OPEN · 37 HERE</span>' if open_
              else f'<span style="{TYPE};font-size:11px;letter-spacing:.16em;color:{PENCIL}">10PM – 2AM</span>')
    return f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('with real people', 24)}{status}</div>
<div style="{HAND};font-size:46px;line-height:1.15;margin-top:6px">Talk to someone</div>
<div style="{SERIF};font-size:18px;color:{PENCIL};margin-top:4px">{"Text first. Voice only if you both agree." if open_ else "Strangers, kind ones. Every night."}</div>
{right_open if open_ else right_closed}'''

home_css = f""".pulse-dot{{width:8px;height:8px;border-radius:50%;background:#E08A3C;box-shadow:0 0 0 0 rgba(224,138,60,.6);animation:pd 2.4s ease-out infinite}}
@keyframes pd{{0%{{box-shadow:0 0 0 0 rgba(224,138,60,.55)}}100%{{box-shadow:0 0 0 10px rgba(224,138,60,0)}}}}
.lift.sheet{{transition:transform .5s cubic-bezier(.2,.7,.2,1)}}
.lift.sheet:hover{{transform:rotate(0deg) translateY(-4px) !important}}
"""

def home(open_, capsule=False, focus=False, greeting=''):
    """Desktop home. greeting: extra markup pinned over the board (e.g. a welcome-back slip)."""
    left = paper(left_inner, 520, 412, rot=-1.4, seed=201, pad='34px 40px', cls='sheet',
                 tapes=tape(200, -14, 120, 30, rot=-3, seed=21))
    right = paper(right_inner(open_), 520, 412, rot=1.1, kind='kraft', seed=202, pad='34px 40px', cls='sheet',
                  tapes=tape(220, -15, 110, 30, rot=4, seed=22))
    q = polaroid('moon', 220, 200, "What's something you pretend doesn't bother you?", rot=3.5, seed=203, u='hq', capsize=23)
    cap = letter_arrived() if capsule else ''
    status = 'PODS OPEN · UNTIL 2AM' if open_ else 'PODS OPEN AT 10PM · 1H 42M'
    qhref, qlabel = ('V5Question.dc.html', 'JOIN THE ROOM →') if open_ else ('V5Asleep.dc.html', 'REMIND ME AT 10 →')
    body = f'''
{atmos()}
{topbar(right=status)}
{cap}
<main style="position:relative;z-index:10;flex-grow:1;padding:0 56px 30px;display:flex;flex-direction:column;justify-content:center;gap:30px">
<div>
{h_hand('What do you need tonight?', 60, wait='.2s', d='1.8s')}
<div class="rise" style="--w:1.4s;{TYPE};font-size:12px;letter-spacing:.16em;color:{BOARDTXT};margin-top:4px">PICK WHAT FITS. YOU CAN ALWAYS COME BACK.</div>
</div>
<div class="{'notes' if focus else ''}" style="display:flex;align-items:flex-start;gap:34px">
<div class="rise" style="--w:.5s"><div class="nf">{left}</div></div>
<div class="rise" style="--w:.8s"><div class="nf rest-dim">{right}</div></div>
<div class="rise" style="--w:1.1s;margin-left:6px;margin-top:-22px"><a href="{qhref}" class="nf rest-dim" style="display:block;position:relative">
<div style="{MARK};font-size:24px;color:{SOFTRED};transform:rotate(-4deg);margin:0 0 14px 6px">tonight's question</div>
{q}
<div style="{TYPE};font-weight:700;font-size:12px;letter-spacing:.16em;color:{CHALK};margin:18px 0 0 18px">{qlabel}</div>
</a></div>
</div>
</main>{greeting}
{footer()}'''
    return body


focus_css = home_css + '''
.notes .nf{transition:opacity .55s ease,filter .55s ease,transform .7s cubic-bezier(.2,.7,.2,1)}
.notes .nf .lift.sheet:hover{transform:none !important}
.notes:not(:has(.nf:hover)) .nf.rest-dim,.notes:has(.nf:hover) .nf:not(:hover){opacity:.82;filter:saturate(.85) brightness(.94);transform:scale(.975)}
.notes:not(:has(.nf:hover)) .nf:not(.rest-dim),.notes .nf:hover{opacity:1;filter:none;transform:scale(1.02) translateY(-6px)}
.notes .nf:hover .lift{filter:drop-shadow(0 26px 34px rgba(0,0,0,.6)) drop-shadow(0 0 40px rgba(255,184,107,.10))}
'''
if __name__ == '__main__':
    page('V5Home', 'Home', home(False, focus=True), css=focus_css)
    page('V5HomeOpen', 'Home, pods open', home(True, capsule=True, focus=True), css=focus_css)
    print('home ok')
