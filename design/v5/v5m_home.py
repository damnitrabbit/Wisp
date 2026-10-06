from gen5 import *
from v5_home import envelope

# ---------- fluid paper for the phone frame (shared by v5m_arrival / v5m_capcare) ----------
def fcard(inner, kind='', seed=1, pad='20px', rot=0, tapes='', grow=0, extra='', iextra='', torn=None):
    """A sheet as wide as its column whose height follows its content. grow>0 lets it take a share
    of the free height (flex-grow), so the screen fills on tall phones without a fixed height."""
    g = f'flex:{grow} 1 auto;min-height:0;' if grow else 'flex:0 0 auto;'
    return (f'<div class="lift" style="position:relative;{g}width:100%;display:flex;flex-direction:column;transform:rotate({rot}deg);{extra}">'
            f'<div class="paper {kind}" style="position:relative;flex:1 1 auto;padding:{pad};clip-path:{deckle(346, 300, seed=seed, torn=torn)};display:flex;flex-direction:column;{iextra}">{inner}</div>{tapes}</div>')

def ctape(w=100, y=-12, h=26, rot=-3, seed=3, dx=0, red=False):
    """Tape centred on a fluid sheet (dx nudges it right of centre)."""
    return tape(0, y, w, h, rot=rot, red=red, seed=seed).replace('left:0px', f'left:calc(50% - {w / 2 - dx:.0f}px)', 1)

def etape(w, h, rot, seed, right=None, bottom=None, left=None, top=None):
    """Tape pinned to a corner of a fluid sheet."""
    pos = ';'.join(f'{k}:{v}px' for k, v in (('right', right), ('bottom', bottom), ('left', left), ('top', top)) if v is not None)
    return tape(0, 0, w, h, rot=rot, seed=seed).replace('left:0px;top:0px', pos, 1)

def mrow(activity, feature, href, last=False):
    bb = '' if last else f'border-bottom:1px dashed {RULE};'
    return (f'<a href="{href}" class="row mrow" style="flex:0 0 auto;min-height:42px;{bb}">'
            f'<span style="{HAND};font-size:clamp(17px, 4.7vw, 19px);color:{INK};white-space:nowrap">{activity}</span>'
            f'<span class="go" style="display:flex;align-items:center;gap:8px;{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.1em;color:{PENCIL};white-space:nowrap;padding-right:2px;text-align:right;line-height:1.35"><span>{feature}</span><span style="color:{INK};font-size:13px">→</span></span></a>')

def qstrip(open_):
    """Tonight's question as a small polaroid strip: moon photo on the left, the question on the right."""
    href, label = ('V5MQuestion.dc.html', 'JOIN THE GROUP →') if open_ else ('V5MAsleep.dc.html', 'REMIND ME AT 10 →')
    inner = (f'<div style="display:flex;align-items:center;gap:12px">'
             f'<div style="flex-shrink:0;padding:4px 4px 12px;background:#fbf8f1;box-shadow:0 1px 2px rgba(0,0,0,.25);transform:rotate(-2.5deg)">{scene("moon", 42, 38, u="mqs")}</div>'
             f'<div style="display:flex;flex-direction:column;gap:3px;min-width:0">'
             f'<div style="{MARK};font-size:17px;line-height:1;color:{RED}">tonight\'s question</div>'
             f'<div style="{HAND};font-size:clamp(15px, 4.1vw, 16px);line-height:1.22;color:{INK}">What\'s something you pretend doesn\'t bother you?</div>'
             f'<div style="{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;color:{INK};margin-top:3px">{label}</div></div></div>')
    return f'<a href="{href}" class="chip" style="display:block;flex:1 1 auto;min-width:0">{fcard(inner, "hi", 803, "9px 16px 9px 14px", rot=-.8)}</a>'

HEAD = f'font-size:clamp(29px, 4.1vh, 34px)'
def mhome(open_, capsule=False, sub=None, strip=True):
    """Phone home. sub: replaces the line under the headline (e.g. a welcome-back slip).
    Frame: header · body (the two menu sheets share the free height) · dock (tonight's question) · footer."""
    cpad = '14px 22px 14px 20px'
    TTL = f'{HAND};font-size:clamp(23px, 6.3vw, 26px);line-height:1.1;margin-top:2px'
    left = fcard(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('on your own', 19)}<span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">ANY TIME</span></div>
<div style="{TTL}">Let something out</div>
<nav aria-label="Let something out" style="display:flex;flex-direction:column;margin-top:4px;border-top:1px dashed {RULE}">
{mrow('I need to get this out', 'BURN', 'V5MBurn.dc.html')}
{mrow('Leave it somewhere', 'ECHO ·<br>LETTER', 'V5MEchoes.dc.html')}
{mrow('Hear it again later', 'CAPSULE', 'V5MCapsule.dc.html', True)}
</nav>''', seed=801, pad=cpad, rot=-1.2, grow=0, tapes=ctape(100, -12, 26, rot=-3, seed=81, dx=-30))
    if open_:
        rinner = f'''<nav aria-label="Talk to someone" style="display:flex;flex-direction:column;margin-top:4px;border-top:1px dashed rgba(34,30,26,.25)">
{mrow('Someone, one on one', '1:1 POD', 'V5MLean.dc.html')}
{mrow('A room, just listening in', 'OPEN POD', 'V5MRooms.dc.html', True)}</nav>'''
        # the small group is tonight's question: it lives in the strip below, not as a fourth row
        status = f'<span style="display:flex;align-items:center;gap:6px;{TYPE};font-size:9.5px;letter-spacing:.16em;color:{INK}"><span class="pulse-dot"></span>OPEN<span data-slot="here"> · 37 HERE</span></span>'
        rg = 4
    else:
        rinner = f'''<div style="margin-top:6px;border-top:1px dashed rgba(34,30,26,.25);padding:10px 0 8px;display:flex;align-items:center;gap:14px">
{rabbit(44, INK, mood='sleep', uid='mhs')}
<div style="display:flex;flex-direction:column;gap:4px"><div style="{HAND};font-size:clamp(17px, 4.7vw, 19px);line-height:1.25">Everyone's asleep. Back at 10pm.</div>
<a href="V5MAsleep.dc.html" class="ul" style="{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.16em;color:{INK};align-self:flex-start;padding:4px 0">REMIND ME →</a></div></div>'''
        status = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.16em;color:{PENCIL}">10PM – 2AM</span>'
        rg = 2
    right = fcard(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('with real people', 19)}{status}</div>
<div style="{TTL}">Talk to someone</div>
{rinner}''', kind='kraft', seed=802, pad=cpad, rot=1, grow=0, tapes=ctape(96, -12, 26, rot=4, seed=82, dx=-20))
    cap = (f'<a href="V5MCapsuleOpen.dc.html" class="chip" aria-label="A letter from you arrived. Open it." style="display:flex;align-items:center;justify-content:flex-end;gap:6px;margin:6px 2px 0 0">'
           f'<span style="{MARK};font-size:19px;color:{SOFTRED};white-space:nowrap">a letter from you arrived</span>'
           f'<svg width="34" height="22" viewBox="0 0 34 22" aria-hidden="true" style="overflow:visible;flex-shrink:0">'
           f'<path class="draw" style="--len:50;--d:.6s;--w:1.2s" d="M2 6 C12 2 22 4 30 13" fill="none" stroke="{SOFTRED}" stroke-width="1.8" stroke-linecap="round"/>'
           f'<path class="draw" style="--len:24;--d:.3s;--w:1.7s" d="M22 13 L31 14 L30 5" fill="none" stroke="{SOFTRED}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
           f'<span class="rise" style="--w:.8s;margin:8px 0 0 2px">{envelope(70, 6, uid="menv", tape_on=False)}</span></a>')
    hint = str(capsule).lower()
    cap = f'<sc-if value="{{{{letter}}}}" hint-placeholder-val="{{{{ {hint} }}}}">{cap}</sc-if>'
    pick = f'<div class="rise msub" style="--w:1.2s;{TYPE};font-size:10px;letter-spacing:.14em;line-height:1.5;color:{BOARDTXT};margin-top:4px">PICK WHAT FITS. YOU CAN ALWAYS COME BACK.</div>'
    if sub is None:
        # the arrived letter takes the place of this line when it shows (site: vals.noLetter)
        sub = f'<sc-if value="{{{{noLetter}}}}" hint-placeholder-val="{{{{ {str(not capsule).lower()} }}}}">{pick}</sc-if>'
    hello = f'<div class="mhello">{h_hand("What do you need <br>tonight?", 34, d="1.8s", extra=HEAD)}{sub}{cap}</div>'
    body = f'''
{matmos()}
{mtopbar(right=f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">{"UNTIL 2AM" if open_ else "PODS AT 10PM"}</span>')}
{mbody(hello + f'<div class="mnotes" style="margin:auto 0;padding:clamp(4px, 1.4vh, 18px) 0;display:flex;flex-direction:column;gap:clamp(14px, 2.2vh, 24px)">'
       f'<div class="rise" style="--w:.5s;width:94%;align-self:flex-start;display:flex;flex-direction:column">{left}</div>'
       f'<div class="rise" style="--w:.8s;width:94%;align-self:flex-end;display:flex;flex-direction:column">{right}</div></div>', gap=0)}
{f'<div class="rise" style="--w:1.1s;display:flex;flex-direction:column">{mdock(qstrip(open_))}</div>' if strip else f'<div style="height:{M_GAP}px;flex-shrink:0"></div>'}
{mfooter()}'''
    return body

css = """.pulse-dot{width:7px;height:7px;border-radius:50%;background:#E08A3C;animation:pd 2.4s ease-out infinite}
@keyframes pd{0%{box-shadow:0 0 0 0 rgba(224,138,60,.55)}100%{box-shadow:0 0 0 9px rgba(224,138,60,0)}}
@media (max-height:780px){.msub{display:none}.mrow{min-height:38px!important}.mnotes{padding:0!important;gap:12px!important}.mhello br{display:none}.mhello > .write{font-size:clamp(24px, 7.2vw, 30px)!important;white-space:nowrap}}"""
MHOME_H = 844
MHOME_OPEN_H = 844
if __name__ == '__main__':
    mpage('V5MHome', 'Home', mhome(False), h=MHOME_H, css=css)
    mpage('V5MHomeOpen', 'Home, pods open', mhome(True, capsule=True), h=MHOME_OPEN_H, css=css)
    print('mhome ok')
