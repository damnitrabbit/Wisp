"""N0TRACE V5 — the live pieces of the open pod (room slips, stage cards, notes) and the group pod (tonight's question)
as HTML templates for the site.

Rooms and the question room hold real people, so the site can't use the boards' sample names. This writes the same
markup the generators draw (it calls their own functions), with {{tokens}} where live values go, {{{tokens}}} for
nested parts and <sc-if value="{{x}}"> for optional bits. data-act="x" data-id="{{id}}" marks an action.
The site fills them in (apps/web/app/rooms/_parts/Tpl.js).

  cd design/v5 && python3.13 v5_rooms_parts.py      # writes apps/web/app/rooms/_parts/parts.gen.js
"""
import io, os, json, contextlib, re
from gen5 import *
with contextlib.redirect_stdout(io.StringIO()):
    import v5x_voice as VX
    import v5m_voice as MV
    import v5e_talk as ET
    import v5_talk as T
from v5m_talk import tchip, ctape

OUTJS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'apps', 'web', 'app', 'rooms', '_parts', 'parts.gen.js')
P = {}


def act(h, name, idtok=False, href=None):
    """First placeholder link (or the one pointing at `href`) -> data-act (+ data-id)."""
    pat = re.escape(f'<a href="{href}"') if href else r'<a href="#"(?! data-act)'
    extra = f' data-act="{name}"' + (' data-id="{{id}}"' if idtok else '')
    assert re.search(pat, h), (name, pat)
    return re.sub(pat, lambda m: '<a href="#"' + extra, h, count=1)


def sub1(h, old, new):
    assert old in h, old[:80]
    return h.replace(old, new, 1)


def ifv(key, inner):
    return f'<sc-if value="{{{{{key}}}}}">{inner}</sc-if>'


CLAMP2 = 'display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;'

# =============================== rooms list ===============================
for i in range(10):
    for full in (False, True):
        n = 10 if full else 5
        h = VX.room_slip(i, '{{name}}', '{{theme}}', n, ['@A@', '@B@', '@C@'], href='{{href}}')
        a = h.index('>ON STAGE</div>') + len('>ON STAGE</div>')
        b = h.index('</div>\n<div style="display:flex;align-items:center;justify-content:space-between;gap:8px">', a)
        block = h[a:b]
        h = h[:a] + '{{{sp}}}' + h[b:]
        h = sub1(h, VX.dots10(n, 8, 4, full), '{{{dots}}}')
        h = sub1(h, f'>{n}/10<', '>{{n}}/10<')
        h = sub1(h, f'aria-label="{{{{name}}}}, {n} of 10', 'aria-label="{{label}}')
        h = h.replace(', full" ', '" ')
        h = sub1(h, f'font-style:italic;font-size:15px;line-height:1.35;color:{PENCIL};margin-top:4px;min-height:40px',
                 f'font-style:italic;font-size:15px;line-height:1.35;color:{PENCIL};margin-top:4px;min-height:40px;{CLAMP2}')
        P[f'dSlip{"Full" if full else ""}{i}'] = h
        if not full:
            la = block[:block.index('</div>') + 6]
            P[f'dSpW{i}'] = la.replace('@A@', '{{name}}')
    if i == 0:
        rest = block[block.index('</div>') + 6:]
        lb = rest[:rest.index('</div>') + 6]
        P['dSp'] = lb.replace('@B@', '{{name}}')
        P['dMore'] = rest[rest.index('</div>') + 6:].replace('+1 MORE', '+{{more}} MORE')
        P['dSpNone'] = P['dSp'].replace(f'color:{INK}', f'color:{PENCIL}').replace('{{name}}', 'nobody yet · walk in')
for n in range(11):
    P[f'dDots{n}'] = VX.dots10(n, 8, 4)
P['dDotsFull'] = VX.dots10(10, 8, 4, True)

for i in range(10):
    for full in (False, True):
        n = 10 if full else 5
        h = MV.mslip(i, '{{name}}', '{{theme}}', n, ['@A@', '@B@'], '{{href}}')
        others = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}"> +1</span>'
        if not full:
            h = sub1(h, VX.mini_wave(980 + i, 26, 12), ifv('live', VX.mini_wave(980 + i, 26, 12)))
        h = sub1(h, '@A@' + others, '{{lead}}' + ifv('more', others.replace(' +1', ' +{{more}}')))
        h = sub1(h, VX.dots10(n, 7, 3, full), '{{{dots}}}')
        h = sub1(h, f'>{n}/10<', '>{{n}}/10<')
        h = sub1(h, f'aria-label="{{{{name}}}}, {n} of 10', 'aria-label="{{label}}')
        h = h.replace(', full" ', '" ')
        h = sub1(h, f'font-style:italic;font-size:13px;line-height:1.3;color:{PENCIL};margin-top:4px;min-height:34px',
                 f'font-style:italic;font-size:13px;line-height:1.3;color:{PENCIL};margin-top:4px;min-height:34px;{CLAMP2}')
        P[f'mSlip{"Full" if full else ""}{i}'] = h
for n in range(11):
    P[f'mDots{n}'] = VX.dots10(n, 7, 3)
P['mDotsFull'] = VX.dots10(10, 7, 3, True)

# =============================== inside a room (desktop) ===============================
card = ET.room_card2('{{title}}', '{{theme}}', 5, '{{{you}}}', btns='{{{btns}}}', h=561)
card = sub1(card, VX.dots10(5, 9, 4), '{{{cdots}}}')
card = sub1(card, '>5/10<', '>{{n}}/10<')
card = sub1(card, 'height:561px', 'height:{{h}}px')
card = act(card, 'leave', href='V5Rooms.dc.html')
card = act(card, 'report', href='V5Reported.dc.html')
card = sub1(card, '<span>report someone</span>', '<span>{{reportLabel}}</span>')
P['dCard'] = card
for n in range(11):
    P[f'dCDots{n}'] = VX.dots10(n, 9, 4)
P['dBtnMute'] = act(VX.pod_btn('{{muteLabel}}', '#', VX.MIC, 'ink', seed=721, w=230), 'mute')

P['dYouMod'] = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(-.6deg)">
<div style="display:flex;align-items:center;gap:10px">{VX.star(24, INK, uid='b')}<span style="{HAND};font-size:23px;color:{INK};line-height:1">you're a mod here</span></div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:8px">{{{{body}}}}</div></div>'''
P['dYouFirst'] = ET.alone_you
P['dYouHand'] = f'''<div style="margin-top:18px;padding:14px 14px 12px;border:1.5px dashed rgba(34,30,26,.35);transform:rotate(.5deg)">
<div style="display:flex;align-items:center;gap:10px;color:{INK}">{VX.ic(VX.HANDI, 20)}<span style="{HAND};font-size:23px;color:{INK};line-height:1.1">{{{{from}}}} asked you up</span></div>
<div style="{SERIF};font-style:italic;font-size:15px;line-height:1.45;color:{PENCIL};margin-top:8px">Their note is on the right. Take your time.</div></div>'''
you = sub1(ET.off_you, f'color:{INK};line-height:1.1;margin-top:4px">listening<', f'color:{INK};line-height:1.1;margin-top:4px">{{{{title}}}}<')
you = sub1(you, "Your mic is off. Raise a hand whenever you'd like to speak again.", '{{body}}')
P['dYouPlain'] = you

P['dStage'] = ET.stage2('{{{tags}}}', '{{count}}', '{{{listeners}}}', '{{lcount}}')
MOVE = f'<a href="#" class="ul offst" style="{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;color:{INK}">MOVE OFF STAGE</a>'
YOU = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{PENCIL}">YOU</span>'
REPORT = f'<a href="#" data-act="report" data-id="{{{{id}}}}" class="ul" style="{TYPE};font-weight:700;font-size:9.5px;letter-spacing:.14em;color:{RED}">REPORT</a>'
for i in range(4):
    for st in ('speaking', 'listening', 'muted'):
        h = VX.speaker_tag(i, '{{name}}', st, True, False, mod_view=True)
        h = sub1(h, VX.MOD_BADGE(), ifv('mod', VX.MOD_BADGE()))
        h = sub1(h, MOVE, ifv('canMove', MOVE.replace('<a href="#"', '<a href="#" data-act="move" data-id="{{id}}"')) + ifv('me', YOU) + ifv('canReport', REPORT))
        h = sub1(h, f'{HAND};font-size:25px;line-height:1.1;color:{INK}">{{{{name}}}}', f'{HAND};font-size:{{{{fs}}}}px;line-height:1.1;color:{INK}">{{{{name}}}}')
        P[f'dTag_{st}_{i}'] = h
    P[f'dEmpty{i}'] = ET.empty_tag(i=i % 3)
li = VX.listener_row(['@N@'], you_hand='@N@')
li = li[li.index('<span'):li.rindex('</div>')]
hand = f'<span style="color:{INK}">{VX.ic(VX.HANDI, 15)}</span>'
you9 = f'<span style="{TYPE};font-size:9px;letter-spacing:.14em;color:{PENCIL}">YOU</span>'
li = sub1(li, '@N@' + hand + you9, '{{name}}' + ifv('hand', hand) + ifv('you', you9) + ifv('rep', you9.replace('YOU', 'REPORT').replace(f'color:{PENCIL}', f'color:{RED}')))
P['dLi'] = sub1(li, '<span style=', '<span data-act="{{act}}" data-id="{{id}}" style=')
P['dLiRow'] = '<div style="display:flex;flex-wrap:wrap;column-gap:26px;row-gap:6px">{{{items}}}</div>'
P['dLiNone'] = f'<div style="{HAND};font-size:22px;color:{PENCIL};opacity:.8">nobody yet. the door is open.</div>'

hn = VX.hand_note
hn = sub1(hn, '>a hand is up<', '>{{mark}}<')
hn = sub1(hn, '>0:42<', '>{{t}}<')
hn = sub1(hn, '>lowkey_comet<', '>{{name}}<')
hn = sub1(hn, '>would like to come up and speak.<', '>{{body}}<')
row_a = hn.index('<div style="display:flex;align-items:center;gap:22px;margin-top:22px">')
row_b = hn.index('</a></div>', row_a) + len('</a></div>')
row = hn[row_a:row_b]
row = sub1(row, tchip('invite up', '#', 'ink', 150, 54, 731), act(tchip('{{yes}}', '#', 'ink', 150, 54, 731), 'yes', True))
row = act(row.replace('>NOT NOW<', '>{{no}}<'), 'no', True)
hn = hn[:row_a] + ifv('chips', row) + hn[row_b:]
hn = sub1(hn, 'THEY CHOOSE WHETHER TO COME UP. THEIR MIC IS ASKED ONLY THEN.', '{{foot}}')
q = sub1(VX.queue_note, 'NEXT HAND · STATIC_HERON', 'NEXT HAND · {{NEXT}}')
P['dRightHand'] = f'<div><div class="pinned" style="--w:1.1s">{hn}</div>{ifv("next", q)}</div>'

invite = paper(f'''
<div style="display:flex;align-items:center;gap:8px">{VX.star(20, INK, uid='i')}<span style="{TYPE};font-size:10.5px;letter-spacing:.16em;color:{PENCIL}">FROM {{{{FROM}}}} · MOD</span></div>
{h_hand('come up?', 48, color=INK, wait='1.4s', d='1.2s', extra='margin-top:8px;white-space:nowrap')}
<div style="{SERIF};font-size:17px;line-height:1.5;color:{INK};margin-top:6px">There's a seat on stage for you. Say as much or as little as you like.</div>
<div style="display:flex;align-items:center;gap:22px;margin-top:22px">{act(tchip('come up', '#', 'ink', 140, 54, 741), 'accept')}
<a href="#" data-act="refuse" class="ul" style="{TYPE};font-size:11.5px;letter-spacing:.16em;color:{INK}">NOT NOW</a></div>
<div style="{TYPE};font-size:9.5px;letter-spacing:.13em;line-height:1.6;color:{PENCIL};margin-top:18px">YOUR MIC IS ASKED ONLY WHEN YOU SAY COME UP. STEP DOWN ANY TIME.</div>''',
    290, 370, rot=-1.8, kind='hi', seed=992, pad='26px 26px', tapes=tape(92, -13, 104, 26, rot=-3, red=True, seed=96))
P['dRightInvite'] = (f'<div><div class="pinned" style="--w:1.1s">{invite}</div>'
                     f'<div class="rise" style="--w:2s;margin-top:26px;padding-left:10px;{MARK};font-size:21px;color:{SOFTRED};transform:rotate(-2deg);line-height:1.2">no pressure.<br>listening is enough too.</div></div>')

off = ET.off_slip
off = sub1(off, '>OFF STAGE · MIC OFF<', '>{{kicker}}<')
off = sub1(off, ">You're listening again.<", '>{{title}}<')
off = sub1(off, '>A mod moved you off stage. It happens, no reason needed.<', '>{{body}}<')
a0 = off.index('<a href="V5RoomHand.dc.html"')
a1 = off.index('</a>', a0) + 4
lk = off[a0:a1].replace('<a href="V5RoomHand.dc.html"', '<a href="#" data-act="{{act}}"').replace('RAISE HAND AGAIN', '{{action}}')
lk = sub1(lk, VX.ic(VX.HANDI, 16), ifv('hand', VX.ic(VX.HANDI, 16)))
off = off[:a0] + ifv('action', lk) + off[a1:]
off = sub1(off, ">A MOD LETS YOUR HAND UP WHEN THERE'S ROOM.<", '>{{foot}}<')
P['dRightNote'] = (f'<div><div class="pinned" style="--w:1.1s">{off}</div>'
                   + ifv('under', f'<div class="rise" style="--w:2s;margin-top:26px;padding-left:10px;{MARK};font-size:21px;color:{SOFTRED};transform:rotate(-2deg);line-height:1.2">{{{{under}}}}</div>') + '</div>')
P['dRightAlone'] = ET.alone_right

# =============================== inside a room (phone) ===============================
mh = ET.mroom_head2('{{title}}', '{{theme}}', '{{n}}', '{{{right}}}')
mh = sub1(mh, f'<span style="{SERIF};font-style:italic;font-size:14px;color:{BOARDTXT}">{{{{theme}}}}</span>',
          f'<span style="{SERIF};font-style:italic;font-size:14px;color:{BOARDTXT};min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-right:10px">{{{{theme}}}}</span>')
mh = sub1(mh, 'justify-content:space-between;margin-top:5px">', 'justify-content:space-between;margin-top:5px;white-space:nowrap">')
P['mHead'] = mh
P['mRightMod'] = f'<span style="display:inline-flex;align-items:center;gap:6px;{MARK};font-size:18px;color:{BOARDTXT};line-height:1">{VX.star(17, BOARDTXT)}you\'re a mod here</span>'
P['mRightFirst'] = f'<span style="display:inline-flex;align-items:center;gap:6px;{MARK};font-size:18px;color:{SOFTRED};line-height:1">{VX.star(17, ET.LRED, uid="ma")}you\'re the first mod</span>'
P['mRightText'] = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">{{{{text}}}}</span>'
P['mStage'] = ET.mstage2('{{{tags}}}', '{{count}}', '{{{listeners}}}', '{{lcount}}', h=384)
MMOVE = f'<a href="#" class="ul" style="{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.12em;color:{INK}">MOVE OFF STAGE</a>'
MYOU = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}">YOU</span>'
MREPORT = f'<a href="#" data-act="report" data-id="{{{{id}}}}" class="ul" style="{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.12em;color:{RED}">REPORT</a>'
MBADGE = f'<span style="display:inline-flex;align-items:center;gap:3px;{TYPE};font-weight:700;font-size:8.5px;letter-spacing:.14em;color:{INK}">{VX.star(11, INK)}MOD</span>'
for i in range(4):
    for st in ('speaking', 'listening', 'muted'):
        h = MV.mtag(i, '{{name}}', st, True, False, True)
        h = sub1(h, MBADGE, ifv('mod', MBADGE))
        h = sub1(h, MMOVE, ifv('canMove', MMOVE.replace('<a href="#"', '<a href="#" data-act="move" data-id="{{id}}"')) + ifv('me', MYOU) + ifv('canReport', MREPORT))
        h = sub1(h, f'{HAND};font-size:19px;line-height:1.1;color:{INK};white-space:nowrap">{{{{name}}}}', f'{HAND};font-size:{{{{fs}}}}px;line-height:1.1;color:{INK};white-space:nowrap">{{{{name}}}}')
        P[f'mTag_{st}_{i}'] = h
    P[f'mEmpty{i}'] = ET.mempty_tag(i % 3)
mli = MV.mlisteners(['@N@'], you='@N@')
mli = mli[mli.index('<span'):mli.rindex('</div>')]
mhand = f'<span style="color:{INK}">{VX.ic(VX.HANDI, 13)}</span>'
myou = f'<span style="{TYPE};font-size:8.5px;letter-spacing:.12em;color:{PENCIL}">YOU</span>'
mli = sub1(mli, '@N@' + mhand + myou, '{{name}}' + ifv('hand', mhand) + ifv('you', myou) + ifv('rep', myou.replace('YOU', 'REPORT').replace(f'color:{PENCIL}', f'color:{RED}')))
P['mLi'] = sub1(mli, '<span style=', '<span data-act="{{act}}" data-id="{{id}}" style=')
P['mLiRow'] = '<div style="display:flex;flex-wrap:wrap;column-gap:18px;row-gap:2px">{{{items}}}</div>'
P['mLiNone'] = f'<div style="{HAND};font-size:18px;color:{PENCIL};opacity:.85">nobody yet. the door is open.</div>'

hs = MV.hand_slip
hs = sub1(hs, '>a hand is up<', '>{{mark}}<')
hs = sub1(hs, '>0:42 · NEXT: STATIC_HERON<', '>{{t}}<')
hs = sub1(hs, '>lowkey_comet<', '>{{name}}<')
hs = sub1(hs, '>would like to come up and speak.<', '>{{body}}<')
ra = hs.index('<div style="display:flex;align-items:center;gap:22px;margin-top:12px">')
rb = hs.index('</a></div>', ra) + len('</a></div>')
row = hs[ra:rb]
row = sub1(row, MV.mchip('invite up', '#', 'ink', 138, seed=791), act(MV.mchip('{{yes}}', '#', 'ink', 138, seed=791), 'yes', True))
row = act(row.replace('<span>not now</span>', '<span>{{no}}</span>'), 'no', True)
P['mSlipHand'] = hs[:ra] + ifv('chips', row) + hs[rb:]
iv = MV.invite_slip
iv = sub1(iv, '>FROM DUSK_SIGNAL · MOD<', '>FROM {{FROM}} · MOD<')
iv = act(iv, 'accept')
iv = act(iv, 'refuse')
P['mSlipInvite'] = iv
mo = ET.moff_slip
mo = sub1(mo, '>OFF STAGE · MIC OFF<', '>{{kicker}}<')
mo = sub1(mo, ">You're listening again.<", '>{{title}}<')
mo = sub1(mo, '>A mod moved you off stage. It happens, no reason needed.<', '>{{body}}<')
a0 = mo.index('<div style="margin-top:10px"><a href="V5MRoomHand.dc.html"')
a1 = mo.index('</a></div>', a0) + len('</a></div>')
lk = mo[a0:a1].replace('<a href="V5MRoomHand.dc.html"', '<a href="#" data-act="{{act}}"').replace('<span>raise hand again</span>', '<span>{{action}}</span>')
lk = sub1(lk, VX.ic(VX.HANDI, 14), ifv('hand', VX.ic(VX.HANDI, 14)))
P['mSlipNote'] = mo[:a0] + ifv('action', lk) + mo[a1:]
P['mSlipAlone'] = ET.malone_slip
bar = ET.mroom_bar2('{{{left}}}')
bar = act(bar, 'leave', href='V5MRooms.dc.html')
bar = act(bar, 'report', href='V5MReported.dc.html')
P['mBar'] = sub1(bar, '<span>report</span>', '<span>{{reportLabel}}</span>')
P['mBarMute'] = act(MV.mchip('{{muteLabel}}', '#', 'ink', 118, seed=1995, icon=VX.MIC, h=44), 'mute')
P['mBarText'] = f'<span style="{TYPE};font-size:9.5px;letter-spacing:.14em;color:{BOARDTXT}">{{{{text}}}}</span>'

# =============================== tonight's question ===============================
for st in ('speaking', 'listening', 'muted'):
    P[f'dPerson_{st}'] = T.person('{{name}}', st)
P['dQRoom'] = paper(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 24)}<span style="{TYPE};font-size:10px;letter-spacing:.16em;color:{PENCIL}">{{{{count}}}}</span></div>
<div style="margin-top:10px">{{{{{{people}}}}}}</div>
<div style="{TYPE};font-size:10px;letter-spacing:.14em;color:{PENCIL};margin-top:16px;line-height:1.8">LET PEOPLE FINISH · LEAVING IS ALWAYS OKAY</div>''',
    520, 411, rot=1.2, kind='kraft', seed=561, pad='30px 36px', tapes=tape(200, -13, 110, 28, rot=-3, seed=56)).replace('height:411px', 'height:{{h}}px')
P['dQBtns'] = (f'<div class="rise" style="--w:1.2s;display:flex;align-items:center;gap:30px;margin-left:10px">'
               f'{act(chip("{{a}}", "#", seed=563, w=220), "a")}{act(link("{{b}}", "#"), "b")}</div>')


def mperson(name, state):  # same row as the phone board (v5m_talk MT05)
    wave = ('<svg width="34" height="14" viewBox="0 0 44 18" aria-hidden="true"><path class="talkwave" d="M0 9 Q4 1 8 9 T16 9 T24 9 T32 9 T40 9" fill="none" stroke="#C0662A" stroke-width="2.2" stroke-linecap="round"/></svg>'
            if state == 'speaking' else '')
    col = INK if state != 'muted' else PENCIL
    return (f'<div style="display:flex;align-items:center;justify-content:space-between;height:37px;border-bottom:1px dashed {RULE}">'
            f'<span style="{HAND};font-size:20px;color:{col};white-space:nowrap">{name}</span>'
            f'<span style="display:flex;align-items:center;gap:8px;{TYPE};font-size:9px;letter-spacing:.14em;color:{"#A8521E" if state == "speaking" else PENCIL}">{wave}{state.upper()}</span></div>')


for st in ('speaking', 'listening', 'muted'):
    P[f'mPerson_{st}'] = mperson('{{name}}', st)
P['mQRoom'] = msheet(f'''
<div style="display:flex;justify-content:space-between;align-items:baseline">{t_mark('in the room', 20)}<span style="{TYPE};font-size:9px;letter-spacing:.16em;color:{PENCIL}">{{{{count}}}}</span></div>
<div style="margin-top:4px">{{{{{{people}}}}}}</div>
<div style="{TYPE};font-size:9px;letter-spacing:.13em;color:{PENCIL};margin-top:12px;line-height:1.7">LET PEOPLE FINISH · LEAVING IS ALWAYS OKAY</div>''',
    kind='kraft', seed=1541, pad='22px 24px', rot=1, minh=318, tapes=ctape(100, 26, -3, 154))
P['mQDock'] = (f'<div class="rise" style="--w:1.2s;display:flex;flex-direction:column">'
               + mdock(act(mcta('{{a}}', '#', 'paper', seed=1543), 'a') + act(mtext('{{b}}', '#'), 'b')) + '</div>')

CSS = ET.EXTRA_CSS + T.group_css + """
[data-act]{cursor:pointer}
"""


def write():
    os.makedirs(os.path.dirname(OUTJS), exist_ok=True)
    src = ('// generated by design/v5/v5_rooms_parts.py — edit the generator, not this file\n'
           f'export const CSS = {json.dumps(CSS, ensure_ascii=False)};\n'
           f'export default {json.dumps(P, ensure_ascii=False)};\n')
    open(OUTJS, 'w').write(src)
    print(f'{len(P)} parts written, {len(src) // 1024} KB')


if __name__ == '__main__':
    write()
