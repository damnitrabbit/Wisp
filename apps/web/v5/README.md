# V5 "Notes after dark" on the site

The design lives in `design/v5/*.py` (the generators behind the design canvas). The site renders those exact
screens, so the design is the source of truth.

1. Edit a generator in `design/v5/` (copy, layout, add a `data-slot`), then
   `cd design/v5 && python3.13 export_web.py <module> [<module>…]` — writes `apps/web/v5/screens/V5*.js` for the
   screens those modules make. (No arguments = every screen + base.css; only the lead runs that.)
2. A page renders a screen with `<Screen desktop={D} phone={M} vals={…} slots={…} links={…} />` (`apps/web/v5/Screen.js`).
   - Desktop screens (1440×900 boards) are scaled to the window; phone screens (390 wide, `V5M…`) fill the phone.
   - `<a href="V5X.dc.html">` becomes the route in `routes.js`. `links={{ Matching: () => start() }}` overrides one
     (key = screen name without `V5`/`V5M` and `.dc.html`) with a function or another route.
   - `{{name}}` in text/attributes and `onClick="{{fn}}"` (any on* attribute) read from `vals`.
   - `<sc-if value="{{x}}">…</sc-if>` renders when `vals.x` is truthy.
   - Any element with `data-slot="name"` is replaced by `slots.name` (a React node, or `(node) => node`).
     Put live parts (text inputs, chat lists, timers, the wall) in slots, styled with the same inline styles the
     generator uses for that spot.
3. Keep `vals`/`slots`/`links` stable (`useMemo`/`useCallback`): when they change the whole screen re-parses.
   Fast-changing state (typing, timers, message lists) belongs *inside* slot components, not in `vals`.
4. Sound: `public/sound.js` (copy of `design/v5/sound.js`) reads the `.nt-cfg` marker each screen carries and plays
   cues on CSS animations. Nothing to wire.

Rules
- Never hand-edit `apps/web/v5/screens/*` or `base.css` (generated).
- Don't change `gen5.py` shared helpers without the lead: every screen depends on them.
- Phone check sizes: 360×740, 390×844, 430×932. Desktop: 1440×900 and 1280×720.
