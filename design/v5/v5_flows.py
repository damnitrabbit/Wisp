"""Run every V5 generator, then rebuild the boards where a tap leads straight into a moment with sound,
so that moment plays on the same page (and the browser lets its sound play)."""
import runpy, sys, os, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen5
MODS = ['v5_brand', 'v5_arrival', 'v5_home', 'v5_burn', 'v5_leave', 'v5_talk', 'v5x_echo', 'v5x_talk', 'v5x_voice', 'v5x_system', 'v5x_legal',
        'v5m_home', 'v5m_arrival', 'v5m_burnecho', 'v5m_capcare', 'v5m_talk', 'v5m_voice', 'v5m_system',
        'v5e_leave', 'v5e_talk', 'v5e_system', 'v5_dls', 'v5u_unsent']
for m in MODS:
    with contextlib.redirect_stdout(io.StringIO()):
        runpy.run_path(m + '.py', run_name='__main__')
F = gen5.flow
# desktop
F('V5Boot', [('V5Boot', {'V5Story.dc.html': 1}), ('V5Story', {'V5Age.dc.html': 2}), ('V5Age', {})])
F('V5HomeOpen', [('V5HomeOpen', {'V5CapsuleOpen.dc.html': 1, 'V5Lean.dc.html': 2}), ('V5CapsuleOpen', {}), ('V5Lean', {'V5Matching.dc.html': 3}), ('V5Matching', {})])
F('V5Capsule', [('V5Capsule', {'V5CapsuleSealed.dc.html': 1}), ('V5CapsuleSealed', {'V5Capsule.dc.html': 0})])
F('V5EchoWrite', [('V5EchoWrite', {'V5EchoPinned.dc.html': 1}), ('V5EchoPinned', {})])
F('V5Pod', [('V5Pod', {'V5PodEnd.dc.html': 1}), ('V5PodEnd', {})])
F('V5PodNudge', [('V5PodNudge', {'V5PodEnd.dc.html': 1}), ('V5PodEnd', {})])
# phone
F('V5MBoot', [('V5MBoot', {'V5MStory.dc.html': 1}), ('V5MStory', {'V5MAge.dc.html': 2}), ('V5MAge', {})])
F('V5MHomeOpen', [('V5MHomeOpen', {'V5MCapsuleOpen.dc.html': 1, 'V5MLean.dc.html': 2}), ('V5MCapsuleOpen', {}), ('V5MLean', {'V5MMatching.dc.html': 3}), ('V5MMatching', {})])
F('V5MCapsule', [('V5MCapsule', {'V5MCapsuleSealed.dc.html': 1}), ('V5MCapsuleSealed', {'V5MCapsule.dc.html': 0})])
F('V5MEchoWrite', [('V5MEchoWrite', {'V5MEchoPinned.dc.html': 1}), ('V5MEchoPinned', {})])
F('V5MPod', [('V5MPod', {'V5MPodEnd.dc.html': 1}), ('V5MPodEnd', {})])
F('V5MPodNudge', [('V5MPodNudge', {'V5MPodEnd.dc.html': 1}), ('V5MPodEnd', {})])
F('V5UnsentWrite', [('V5UnsentWrite', {'V5UnsentPinned.dc.html': 1}), ('V5UnsentPinned', {})])
F('V5MUnsentWrite', [('V5MUnsentWrite', {'V5MUnsentPinned.dc.html': 1}), ('V5MUnsentPinned', {})])
print('flows ok')
