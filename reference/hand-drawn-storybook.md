# Hand-drawn storybook — hand-drawn storybook visual technique recipe

A **copy-and-go** `\htmlFile{}` technique using inline SVG to get a "hand-drawn storybook" feel:
pen strokes draw in one by one, paint floods in afterward, the whole image carries a slight jitter + continuous micro-motion.
Validated 17 times across the 17 scenes of "Baiqiao City / MCP fable" on 2026-05-30, frozen into a reference —
**don't reinvent it next time**.

> Use for: explaining tech as fable / personifying concepts / any "warm, handmade, non-PPT" finished-video style.
> Using one hand-drawn HTML/SVG system for the whole video is not PPT — **a systematic animated hand-drawn style is an engine**;
> only static stacking looks like PPT. Visual consistency > number of engines (see [`engine-routing.md`](engine-routing.md)).

---

## Five parts (only the first three are mandatory)

| Part | Role | Key properties |
|---|---|---|
| 1. Inline SVG | Main subject, no external dependencies | `<svg viewBox>` written directly into HTML |
| 2. stroke draw | Lines "get drawn in" | `pathLength=1` + `stroke-dasharray/offset` + `@keyframes draw` |
| 3. flood fill | Paint floods in after the lines | `.f { opacity: 0→1 }`, `animation-delay` ≥ stroke duration |
| 4. Pen jitter | Handmade feel (lines aren't ruler-straight) | `feTurbulence` + `feDisplacementMap` on an outer `<g>` |
| 5. Continuous micro-motion | Don't freeze under long audio | `bob` / `sway` / `spin` loop |

The first three are the skeleton, #4 adds the "hand-drawn flavor", #5 is an audio-first hard requirement (see "Entrance budget" below).

---

## 1. stroke draw — lines get drawn in

Core: set `pathLength="1"` on every `<path>`, so no matter how long the real path is,
`stroke-dasharray` / `stroke-dashoffset` compute against a normalized `1`, and one `@keyframes` handles all lines.

```css
.s {
  fill: none;
  stroke: #234976;
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-dasharray: 1;        /* pairs with pathLength=1 */
  stroke-dashoffset: 1;       /* initially all "undrawn" */
  animation: draw 1s ease forwards;
}
@keyframes draw {
  to { stroke-dashoffset: 0; }  /* fully drawn */
}
```

```html
<path class="s" pathLength="1" d="M40 80 C 80 20, 160 20, 200 80" />
```

**Stagger multiple lines** (like a person drawing stroke by stroke, not all appearing at once):

```css
.s:nth-child(1) { animation-delay: 0s;   }
.s:nth-child(2) { animation-delay: 0.15s; }
.s:nth-child(3) { animation-delay: 0.30s; }
```

Constraints:

- A single `draw` of ~1s is enough; don't exceed 1.5s (see entrance budget).
- Stagger step 0.1–0.2s; too tight and you can't see the strokes, too loose and it overruns the budget.
- `pathLength="1"` goes on the SVG element (attribute), not CSS.

---

## 2. flood fill — paint floods in after the lines

The fill layer is independent of the stroke layer, transparent by default, and only floods in with `opacity: 0→1` after the strokes finish.

```css
.f {
  opacity: 0;
  animation: flood 0.5s ease forwards;
  animation-delay: 1s;        /* ≥ total stroke duration, ensures "draw lines first, color after" */
}
@keyframes flood {
  to { opacity: 1; }
}
```

```html
<!-- fill layer first (bottom), stroke layer after (on top) -->
<path class="f" d="M40 80 C 80 20, 160 20, 200 80 Z" fill="#d9b47b" />
<path class="s" pathLength="1" d="M40 80 C 80 20, 160 20, 200 80" />
```

Key points:

- `animation-delay` must be at least the moment "the last stroke finishes drawing", or the paint appears before the lines and breaks the illusion.
- For a "watercolor spreading" feel: a slightly longer `flood` duration (0.5–0.8s) + a slight `transform: scale(0.96→1)`.
- One `.f` per region; different regions can each add their own small delay for layering.

---

## 3. Pen jitter — feTurbulence + feDisplacementMap

Use fractal noise as a displacement map on the outermost `<g>`, and the whole image's edges get a "shaky hand, ink bleed" irregularity,
losing the ruler-straight stiffness.

```html
<svg viewBox="0 0 400 300">
  <defs>
    <filter id="rough">
      <feTurbulence type="fractalNoise" baseFrequency="0.02"
                    numOctaves="2" seed="7" result="noise" />
      <feDisplacementMap in="SourceGraphic" in2="noise"
                         scale="5" />   <!-- scale 4–6 is the sweet spot -->
    </filter>
  </defs>
  <g filter="url(#rough)">
    <!-- all .s / .f paths go here -->
  </g>
</svg>
```

Tuning:

| Param | Value | Notes |
|---|---|---|
| `scale` | **4–6** | Jitter amplitude; >8 and lines break up and smear |
| `baseFrequency` | 0.01–0.03 | Higher is "fuzzier"; too high looks like noise |
| `numOctaves` | 1–2 | 2 is plenty; more just slows it down |
| `seed` | any integer | Change seed = change the jitter pattern; give each scene a different seed to avoid looking identical |

Note: put the filter on the **outer `<g>`** (the whole group jitters together), don't put it on each path (each jittering separately will misalign).

---

## 4. Continuous micro-motion — bob / sway / spin

After the entrance finishes drawing, leave at least one **looping** micro-motion so the frame breathes under long audio (audio-first hard requirement).

```css
/* bob up and down — characters, floating objects */
@keyframes bob  { 0%,100% { transform: translateY(0);    } 50% { transform: translateY(-6px); } }
/* gentle side sway — flags, trees, signs */
@keyframes sway { 0%,100% { transform: rotate(-2deg);     } 50% { transform: rotate(2deg);     } }
/* slow rotation — gears, stars, halos */
@keyframes spin { to      { transform: rotate(360deg);    } }

.bob  { animation: bob  3s ease-in-out infinite; }
.sway { animation: sway 4s ease-in-out infinite; transform-origin: top center; }
.spin { animation: spin 12s linear infinite;     transform-origin: center;     }
```

- Period 3–12s; slower is classier; `infinite` guarantees no freeze.
- For `sway` / `spin`, remember to set `transform-origin` (sway pivot / rotation center).
- Apply micro-motion on the SVG element or a wrapping `<g>`; it doesn't conflict with draw/flood (different property axes).

---

## 5. Brand colors + title/captions

Hand-drawn storybook uses the light cream palette from [`brand-style.md`](brand-style.md):

```
cream  #fefcf6   /* background / paper */
navy   #234976   /* stroke / body text */
tan    #d9b47b   /* fill / warm color block */
```

**Use an HTML overlay for title / captions**, don't draw them into the SVG (SVG is reserved for illustration):
an absolutely positioned `<div>` layer, with text using a `rise` entrance.

```css
body { background: #fefcf6; }
.title {
  position: absolute; left: 0; right: 0; bottom: 8%;
  text-align: center; color: #234976;
  font-family: 'KaiTi','STKaiti','Songti SC',serif;  /* handmade-feel serif / kai script */
  font-size: 44px; font-weight: 700;
  opacity: 0; animation: rise 0.6s ease forwards; animation-delay: 1.1s;
}
@keyframes rise { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
```

Captions follow the audio-first rule: narration goes through `\say` (no burned captions by default, `burn=on` to burn them);
only "on-screen text" like titles uses an overlay.

---

## Entrance budget (audio-first iron law)

Duration is driven by `\say`, and **an HTML scene doesn't know how long the audio is** — the compiler doesn't touch your CSS keyframes,
Playwright records the full `target_duration` seconds, and after the entrance animation finishes it's a frozen frame.
So (see [`audio-first.md`](audio-first.md)):

1. **The entrance animation (line draw + color flood) finishes drawing in ≤ ~1.5s.**
   - Stroke ~1s (including stagger), fill `delay 1s` + ~0.5s, wrapping up within 1.5s.
2. After 1.5s, **leave only** a **looping** micro-motion like `bob` / `sway` / `spin`.
3. **No** long queues of sequential delays (`delay: 0s; 3s; 6s; 9s`) — if the audio is only 5s,
   the later elements never appear.

**One-line self-check**: open the scene and ask yourself "is anything still moving after second 2? Is the only motion the
`infinite` bob/sway/spin? Did the entrance finish drawing within 1.5s?" Compliant only if all three are "yes".

---

## Minimal runnable skeleton (copy and use)

A complete hand-drawn scene: cream paper + one tan sun (stroke → fill → spin) + navy title overlay.

```html
<!doctype html>
<html><head><meta charset="utf-8"><style>
  html,body { margin:0; height:100%; }
  body {
    background:#fefcf6;
    display:flex; align-items:center; justify-content:center;
    font-family:'KaiTi','STKaiti','Songti SC',serif;
  }
  .stage { position:relative; width:1280px; height:720px;
           display:flex; align-items:center; justify-content:center; }

  /* stroke */
  .s { fill:none; stroke:#234976; stroke-width:4;
       stroke-linecap:round; stroke-linejoin:round;
       stroke-dasharray:1; stroke-dashoffset:1;
       animation:draw 1s ease forwards; }
  .s:nth-of-type(2){ animation-delay:.15s; }
  @keyframes draw { to { stroke-dashoffset:0; } }

  /* fill (after lines are drawn) */
  .f { opacity:0; animation:flood .5s ease forwards; animation-delay:1s; }
  @keyframes flood { to { opacity:1; } }

  /* continuous micro-motion */
  .spin { transform-origin:center; animation:spin 14s linear infinite; }
  @keyframes spin { to { transform:rotate(360deg); } }

  /* title overlay + rise */
  .title { position:absolute; bottom:8%; width:100%; text-align:center;
           color:#234976; font-size:44px; font-weight:700;
           opacity:0; animation:rise .6s ease forwards; animation-delay:1.1s; }
  @keyframes rise { from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:translateY(0);} }
</style></head>
<body>
  <div class="stage">
    <svg viewBox="0 0 400 400" width="320" height="320">
      <defs>
        <filter id="rough">
          <feTurbulence type="fractalNoise" baseFrequency="0.02"
                        numOctaves="2" seed="7" result="n"/>
          <feDisplacementMap in="SourceGraphic" in2="n" scale="5"/>
        </filter>
      </defs>
      <!-- jitter on outer g + continuous rotation -->
      <g filter="url(#rough)" class="spin">
        <!-- fill layer at the bottom -->
        <circle class="f" cx="200" cy="200" r="70" fill="#d9b47b"/>
        <!-- stroke layer on top: circle + rays -->
        <circle class="s" pathLength="1" cx="200" cy="200" r="70"/>
        <path   class="s" pathLength="1" d="M200 90 V40 M200 360 V310
                 M90 200 H40 M360 200 H310"/>
      </g>
    </svg>
    <div class="title">百巧城的太阳</div>
  </div>
</body></html>
```

Running this scene: stroke finishes ~1.15s → fill floods in starting at 1s → title rises at 1.1s →
then the sun keeps `spin`-ning. Conforms to "entrance ≤1.5s, then only looping micro-motion".

---

## Production checklist (validated over 17 views)

1. **Do 1 sample shot first** → `render_shot(id, storyboard=true)` → read `get_state()` → `shots[].render.still` → sign off "good" → only then mass-produce the rest
   (the most valuable step; see the sample discipline in the main workflow).
2. **One naming prefix** for the whole video (e.g. `hd_01..hd_17`), so re-versioning is an easy `delete_file` to archive the old ones.
3. Give each scene a different `seed` so the jitter isn't identical.
4. Don't drift from the three brand colors: cream / navy / tan.
5. Run every scene through the "entrance budget self-check" above.
