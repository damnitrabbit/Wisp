"""Marks the live parts of the pod screens (talk / listen / voice / rooms) for the site.

Called right after a pod screen's page()/mpage() in the generators. It only touches the copy in gen5.PAGES, so the
canvas boards look exactly as before, while the site gets:
  data-slot="msgs"      the conversation (a scrolling list the site fills)
  data-slot="composer"  the "say it however it comes out…" row (a real input + send)
  data-slot="checkin"   the check-in countdown
  {{partner}} / {{PARTNER}} / {{me}} / {{ME}} / {{joined}} / {{slipAt}} / {{status}} / {{lead}}  live values
  data-act="<label>"    on every href="#" action, so the site can wire it (<Screen links={{ mute: fn }}>)
"""
import re
import gen5

_A = re.compile(r'<a href="#"((?:(?!>).)*)>(.*?)</a>', re.S)


def _slug(html):
    t = re.sub(r'<[^>]+>', ' ', html)
    t = re.sub(r'&[a-z]+;|[^a-z0-9]+', ' ', t.lower()).strip()
    return '-'.join(t.split()[:4]) or 'act'


def acts(body):
    """Give every placeholder link a data-act named after its words ("invite up" -> data-act="invite-up")."""
    def sub(m):
        attrs, inner = m.group(1), m.group(2)
        if 'data-act=' in attrs:
            return m.group(0)
        return f'<a href="#" data-act="{_slug(inner)}"{attrs}>{inner}</a>'
    return _A.sub(sub, body)


_COMPOSER = re.compile(r'<div style="((?:flex-shrink:0;)?border-top:1\.5px dashed [^"]*?padding-top:1[26]px;display:flex[^"]*)">(?=\s*<span[^>]*>say it however)')


def pod(name, voice_href=None):
    """A live 1:1 pod screen (talk pod, voice wait/ask, edge states)."""
    p = gen5.PAGES.get(name)
    if not p or p.get('_live'):
        return
    p['_live'] = True
    b = p['body']
    b = b.replace('<div class="scroll" style=', '<div class="scroll" data-slot="msgs" style=')
    b = _COMPOSER.sub(lambda m: f'<div data-slot="composer" style="{m.group(1)}">', b)
    b = b.replace('3:48', '<span data-slot="checkin">3:48</span>')
    b = b.replace('11:52 PM', '{{joined}}').replace('1:31 AM', '{{joined}}')
    b = b.replace('12:50 AM', '{{slipAt}}').replace('12:03 AM', '{{slipAt}}')
    b = b.replace("THEY'RE LISTENING", '{{status}}').replace('you lead.', '{{lead}}')
    b = names(b)
    # the desktop side's "ask for voice" was a placeholder link: point it where the phone's goes
    vh = voice_href or ('V5MVoiceWait.dc.html' if p['w'] == gen5.MW else 'V5VoiceWait.dc.html')
    b = re.sub(r'<a href="#"((?:(?!>).)*>(?:(?!</a>).)*?ask for voice)', lambda m: f'<a href="{vh}"{m.group(1)}', b, flags=re.S)
    p['body'] = acts(b)


def names(b):
    # the crumb says "talk pod" or "listen pod" (the same boards serve both pods)
    b = re.sub(r'(">)talk pod(</span></a)', r'\1{{crumb}}\2', b)
    return (b.replace('moss_byte', '{{partner}}').replace('MOSS_BYTE', '{{PARTNER}}')
             .replace('quiet_otter', '{{me}}').replace('QUIET_OTTER', '{{ME}}'))


def mark(name, slots=(), replace=(), keep_names=False):
    """Any other live screen: wrap given snippets in slots / swap literal text for {{values}}.
    slots: [(exact html snippet, slot name)] -> the snippet's first tag gets data-slot.
    replace: [(literal, replacement)]."""
    p = gen5.PAGES.get(name)
    if not p or p.get('_live'):
        return
    p['_live'] = True
    b = p['body']
    for r in replace:
        b = b.replace(r[0], r[1], *(r[2:3]))
    for snippet, slot in slots:
        if snippet in b:
            b = b.replace(snippet, re.sub(r'^<(\w+)', lambda m: f'<{m.group(1)} data-slot="{slot}"', snippet, count=1), 1)
    if not keep_names:
        b = names(b)
    p['body'] = acts(b)
