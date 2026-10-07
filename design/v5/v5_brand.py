from gen5 import *

def swatch(name, hexv, role, kind='paper', seed=1, dark_text=True):
    inner = (f'<div style="height:74px;background:{hexv};border-radius:2px"></div>'
             f'<div style="{HAND};font-size:22px;margin-top:10px;color:{INK}">{name}</div>'
             f'<div style="{TYPE};font-size:11px;letter-spacing:.12em;color:{PENCIL};margin-top:2px">{hexv} · {role}</div>')
    return paper(inner, 196, 168, rot=random.Random(seed).uniform(-2, 2), kind='hi', seed=seed, pad='14px 14px')

sw_dark = ''.join([swatch('night', NIGHT, 'the room', seed=1), swatch('soot', SOOT, 'lines in the dark', seed=2),
                   swatch('ash', ASH, 'quiet words', seed=3), swatch('chalk', CHALK, 'words in the dark', seed=4)])
sw_light = ''.join([swatch('paper', PAPER, 'notes', seed=5), swatch('kraft', KRAFT, 'your side', seed=6),
                    swatch('ink', INK, 'words on paper', seed=7), swatch('red ink', RED, 'care, marks, heard', seed=8),
                    swatch('black cork', '#141414', 'the board', seed=9)])

type_card = paper(f'''
<div style="display:grid;grid-template-columns:150px 1fr;row-gap:26px;align-items:baseline">
<div style="{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">THE APP'S VOICE<br>Nothing You Could Do</div>
<div style="{HAND};font-size:44px;line-height:1.2">Say it. Then let it go.</div>
<div style="{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">YOUR WORDS<br>Newsreader</div>
<div style="{SERIF};font-size:24px;line-height:1.5">I've been pretending I'm okay for so long that I forgot what okay felt like.</div>
<div style="{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">THE FACTS<br>Courier Prime</div>
<div style="{TYPE};font-size:14px;letter-spacing:.14em">NO ACCOUNT · NOTHING KEPT · FADES IN 24H</div>
<div style="{TYPE};font-size:11px;letter-spacing:.14em;color:{PENCIL}">RED INK<br>Covered By Your Grace</div>
<div style="{MARK};font-size:30px;color:{RED}">heard. you're not alone in this.</div>
</div>''', 760, 470, rot=-.6, seed=21, pad='40px 44px', tapes=tape(330, -14, 120, 30, rot=-3, seed=4))

logo_card = paper(f'''
<div style="display:flex;flex-direction:column;align-items:center;gap:18px;padding-top:14px">
{rabbit(180, INK, draw=True, uid='brand')}
<div class="write" style="--w:2.2s;{HAND};font-size:34px">Damn_It_Rabbit</div>
<div class="fadein" style="--w:3.4s">{wordmark(16, INK)}</div>
<div style="{TYPE};font-size:11px;letter-spacing:.12em;color:{PENCIL};text-align:center;margin-top:6px;line-height:1.7">SAME FACE, NOW DRAWN BY HAND.<br>THE 0 IS NEVER COLOURED.</div>
</div>''', 420, 470, rot=1.2, seed=22, pad='30px 30px', tapes=tape(150, -12, 120, 28, rot=4, seed=9))

comp = f'''
<div style="display:flex;gap:46px;align-items:flex-start">
<div style="display:flex;flex-direction:column;gap:22px;align-items:flex-start">
{t_type('actions', 11)}
{chip('let it go', seed=31)}
{chip('back home', kind='kraft', seed=32)}
<div style="display:flex;gap:26px;margin-top:4px">{link('write another')}{link('not now')}</div>
</div>
<div style="display:flex;flex-direction:column;gap:14px">
{t_type('paper · tape · polaroid', 11)}
<div style="display:flex;gap:30px;align-items:flex-start">
{polaroid('moon', 200, 150, 'the clouds were just so perfect', rot=-3, seed=41, u='b1', capsize=20)}
{polaroid('dawn', 200, 150, 'there is light after this', rot=2.5, seed=42, u='b2', capsize=20)}
{polaroid('window', 200, 150, 'someone is still awake', rot=-1.5, seed=43, u='b3', capsize=20)}
</div></div></div>'''

motion = paper(f'''
<div style="{HAND};font-size:34px;margin-bottom:14px">How things move</div>
<div style="display:grid;grid-template-columns:28px 1fr;row-gap:12px;{SERIF};font-size:19px;line-height:1.45">
<span style="{MARK};color:{RED};font-size:24px">1</span><span>Words write themselves on, left to right, like a pen.</span>
<span style="{MARK};color:{RED};font-size:24px">2</span><span>Everything is pinned to a black cork board in a thin frame, with pin holes, old staples and tape marks from notes that came before. Nothing glows unless it has to.</span>
<span style="{MARK};color:{RED};font-size:24px">3</span><span>Endings get a moment: paper burns to ash, a note gets taped up, a letter gets sealed.</span>
<span style="{MARK};color:{RED};font-size:24px">4</span><span>Everything else is slow and soft. Nothing snaps. Everything will be fine.</span>
</div>''', 640, 400, rot=.8, seed=23, pad='34px 40px', kind='kraft', tapes=tape(270, -13, 110, 28, rot=-5, seed=12))

body = f'''
{atmos(leak(-180, -200, 640) + leak(1100, 1300, 700, ROSE, 4) + '<div class="flare"></div>')}
<div style="position:relative;z-index:10;padding:64px 72px;display:flex;flex-direction:column;gap:56px">
<div style="display:flex;justify-content:space-between;align-items:flex-end">
<div>
{t_type('N0TRACE V5 · design language', 12)}
{h_hand('Notes after dark.', 96, wait='.3s', d='2s', extra='margin-top:10px')}
<div class="rise" style="--w:1.6s;{SERIF};font-size:22px;color:{ASH};max-width:680px;margin-top:8px;line-height:1.5">Raw, imperfect and handmade, like a note someone wrote for you with love. Paper notes pinned to a well-used black cork board.</div>
</div>
<div style="width:220px;margin-bottom:12px">{underline(220, RED, wait='2.2s')}<div style="{MARK};color:#E07A6E;font-size:26px;margin-top:6px;transform:rotate(-2deg)">less words,<br>more meaning.</div></div>
</div>
<div style="display:flex;gap:40px;align-items:flex-start">{type_card}{logo_card}</div>
<div style="display:flex;flex-direction:column;gap:18px">{t_type('the dark', 11)}<div style="display:flex;gap:22px">{sw_dark}</div></div>
<div style="display:flex;flex-direction:column;gap:18px">{t_type('the light', 11)}<div style="display:flex;gap:22px">{sw_light}</div></div>
<div style="display:flex;gap:56px;align-items:flex-start">{comp}</div>
<div style="display:flex;gap:56px;align-items:center">{motion}
<div style="position:relative;width:520px;height:340px">
<div style="position:absolute;inset:0;border:1px dashed {SOOT};border-radius:4px;overflow:hidden"><div class="room"></div></div>
<div style="position:absolute;left:28px;top:24px">{t_type('the board · black cork, framed, a little used', 11)}</div>
<div style="position:absolute;left:28px;bottom:26px;{HAND};font-size:30px;color:{CHALK}">pin anything here.</div>
</div></div>
</div>'''

page('V5Brand', 'V5 Brand', body, h=2100)
print('brand ok')
