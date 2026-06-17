# Brand Style — AutoLecture brand-consistent visuals (light cream + navy + tan gradient)

> **When to use this vs [`palette.md`](palette.md):**
> - **brand-style.md (this file)** = content that should "fly the AutoLecture banner" — official demos / teasers / tutorials / homepage showcases / feature videos for beta users. Visuals match the [autolecture.ai](https://autolecture.ai) site, Studio, and watermark in the same tone — **brand-consistent**.
> - [`palette.md`](palette.md) (editorial dark) = content where **the content itself is the star** — vlogs / paper walkthroughs / personal narratives. Dark base + ocean blue, a generic editor look, not brand-bound.
>
> **Within one project use only one set, don't mix.** The two base colors are opposites (cream vs #0d1117), text colors are inverted; mixing them is jarring.
>
> ⚠️ **Strong hint: when unsure, don't grab both — ask the user, or default to editorial dark.** brand-style is the unified look **for going public under the AutoLecture name**; misusing it is worse than not using it (it looks like you're knocking off your own brand).

---

## Source of truth

Color values and tokens are copied from **`Auto_Lecture/frontend/src/styles.css`** (the `:root` block, as of 2026-05); if the site re-themes later, change that file first, then sync this doc. Logo is taken from `backend/static/watermark/autolecture-logo.png` (840×216).

---

## Palette (mirrors styles.css's `--brand-*` / `--bg-*` / `--fg-*` verbatim)

### Brand primary colors (from the duckling/chick logo)
```
brand-cream:     #f4e5bd   /* chick body — large-area brand color */
brand-tan:       #d9b47b   /* outline / "ginger" — stroke and warm tones */
brand-navy:      #234976   /* wordmark / primary CTA — also default body text */
brand-navy-deep: #1a3554   /* hover / pressed navy */
brand-cheek:     #7a1f1f   /* use sparingly, strong emphasis only, a single dot's worth */
```

### Surfaces (cream layered from outside in, **no black background**)
```
bg-0: #fefcf6   /* page outer layer — lightest cream */
bg-1: #ffffff   /* main panel / card */
bg-2: #f6efde   /* secondary panel / hover */
bg-3: #ece4d0   /* popover / pressed */
```

### Text (navy ladder, **no white text**)
```
fg-0: #234976   /* primary text = brand navy, same as the wordmark */
fg-1: #4a6585   /* secondary text */
fg-muted: #82929f
fg-dim:   #aab3bf
```

### Borders / links / semantic colors
```
border:        rgba(35,73,118,0.14)   /* navy with transparency, not harsh on cream */
border-soft:   rgba(35,73,118,0.07)
border-strong: rgba(35,73,118,0.30)

link:    #234976           /* same as accent, inline links don't steal from the CTA */
accent:  #234976           /* solid navy CTA */
accent-bg: rgba(35,73,118,0.10)

good: #2d8a3e   warn: #b58a1a   err: #c72d24
purple: #5e3aa0
```

### Brand gradient (hero / AI engine pill / emphasis points)
```
accent-grad:      linear-gradient(135deg, #234976 0%, #d9b47b 100%);
accent-grad-soft: linear-gradient(135deg, #23497615 0%, #d9b47b22 100%);
```
The navy → tan warm gradient is the **only gradient style**; don't invent others (no `linear-gradient(orange→red)` and the like).

---

## Font stack

```
sans: "Inter", "Noto Sans SC", -apple-system, BlinkMacSystemFont,
      "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
      sans-serif;
mono: ui-monospace, "SF Mono", Consolas, "Roboto Mono", monospace;
```

Consistent with [`palette.md`](palette.md) (Inter primary, Noto Sans SC for Chinese); the **only difference** is Noto Sans SC added in the fallback order — the site uses it as a fallback, so we follow suit.

---

## Type hierarchy (brand-mode overrides)

| type | size | weight | color |
|---|---|---|---|
| Hero headline | 88–120px | 800–900 | `accent-grad` gradient text (`background-clip: text`) |
| Section heading | 24–32px | 700 | `fg-0` (#234976) |
| Body | 16–22px | 400–500 | `fg-1` (#4a6585) |
| Meta kicker | 12–14px | 600, letter-spacing 4–6 | `brand-tan` (#d9b47b) |
| Numbers / big data points | 64–96px | 800 | `brand-navy` primary, `brand-tan` secondary, **no coral red** |

---

## CSS starter (for HTML scenes, brand version)

```html
<style>
  html, body {
    margin: 0; background: #fefcf6;   /* cream base */
    color: #234976;                   /* navy text */
    font-family: 'Inter', 'Noto Sans SC', system-ui, 'PingFang SC', sans-serif;
  }
  .stage { display: flex; flex-direction: column; align-items: center;
           justify-content: center; height: 100vh; padding: 56px; }
  .kicker { color: #d9b47b; font-size: 14px; font-weight: 700;
            letter-spacing: 6px; text-transform: uppercase; }
  h1 { font-size: 80px; font-weight: 900; letter-spacing: -2px;
       background: linear-gradient(135deg, #234976 0%, #d9b47b 100%);
       -webkit-background-clip: text; background-clip: text; color: transparent; }
  .card { background: #ffffff;
          border: 1px solid rgba(35,73,118,0.14);
          border-radius: 14px; padding: 28px 24px;
          box-shadow: 0 8px 24px rgba(35,73,118,0.06); }
  .num.navy { color: #234976; }   .num.tan { color: #d9b47b; }
  .pill { display: inline-block; padding: 4px 12px; border-radius: 999px;
          background: rgba(35,73,118,0.10); color: #1a3554;
          font-size: 13px; font-weight: 700; }
</style>
```

## Remotion starter (brand lower-third)

Full template at [`../templates/scene_brand_lower_third.tsx.tpl`](../templates/scene_brand_lower_third.tsx.tpl). The core is:
```tsx
const C = {
  cream:  '#f4e5bd',
  tan:    '#d9b47b',
  navy:   '#234976',
  navyD:  '#1a3554',
  paper:  '#ffffff',
  ink1:   '#4a6585',
  border: 'rgba(35,73,118,0.14)',
  grad:   'linear-gradient(135deg, #234976 0%, #d9b47b 100%)',
};
```

---

## Transparent overlay (`over=true`) notes in brand mode

Same **iron rule** as dark: the overlay `AbsoluteFill` still **must not** have any opaque `backgroundColor` — only card elements may take a background. The only difference is the card itself: dark uses a semi-transparent black glass, **brand uses semi-transparent cream/paper**:
```tsx
background: 'rgba(255,255,255,0.86)',     // semi-transparent paper (warm when the original shows through)
border: '1px solid rgba(35,73,118,0.16)',
boxShadow: '0 10px 30px rgba(35,73,118,0.18)',
color: '#234976',                          // navy text
```
More "restrained" than dark glass — in a cream project the overlay shouldn't be too dark, or it looks dirty.

---

## Mascot: duckling/chick 🐥

Logo asset `Auto_Lecture/backend/static/watermark/autolecture-logo.png` (840×216), usable via `\imageFile{logos/autolecture-logo.png}` pulled into the project as a watermark / outro card.

emoji substitute: **🐥** (chick, yellow matches cream) beats 🦆 (duck, blue-gray and cold) — unless the content really is about ducks (like that duck-raising vlog, the topic decides everything).

See memory: `brand_mascot_duck.md` — AutoLecture-specific mascot rules, **don't apply them to other skills / personal projects**.

---

## Recommended `\style{}` string (copy straight into the main.tex preamble)

```latex
\style{AutoLecture brand-light; cream surfaces #fefcf6→#ffffff→#f6efde three layers, navy #234976 primary text and CTA, brand gradient navy→tan #d9b47b for hero/AI engine pill; Inter + Noto Sans SC + PingFang SC fallback; restrained motion, fade-up + small pop, gradient text via background-clip; live-action overlays use semi-transparent paper glass (rgba 0.86), no dark glass}
```

The editorial version is still in [`palette.md`](palette.md)'s `\style{}` examples, pick one.

---

## Do / Don't

| ✅ Do | ❌ Don't |
|---|---|
| cream base + navy text, gradient only goes navy→tan | don't mix the dark set (#0d1117 + ocean blue #6ec1e4) with the cream set |
| use the `accent-grad` gradient for hero big type | don't invent rainbow / three-color / yellow-to-red gradients outside the brand |
| warnings / errors use `warn #b58a1a` or `err #c72d24` (both warm, harmonize with cream) | don't use the dark set's coral red `#ee6c4d` — harsh and not a brand color |
| `\imageFile{logos/autolecture-logo.png}` as outro / corner mark | don't casually invent a new logo / recolor the logo |
| text hierarchy lands on the navy ladder `fg-0/fg-1/muted/dim` | don't use pure black `#000` text — clashes with navy, looks undesigned |

---

## Whole-video tone comparison (for at-a-glance decisions)

| | brand-style (this file) | [`palette.md`](palette.md) editorial |
|---|---|---|
| base color | cream `#fefcf6` / paper `#ffffff` | dark base `#0d1117` |
| text | navy `#234976` ladder | white ladder |
| primary / CTA | brand navy `#234976` | ocean blue `#6ec1e4` |
| warm / emphasis | brand tan `#d9b47b` / cream | warm yellow `#f4d35e` |
| warning | warn `#b58a1a` / err `#c72d24` | coral red `#ee6c4d` |
| gradient | navy → tan (brand-only) | gradient not required |
| use for | official promo / tutorials / homepage / SaaS built-in demos | personal vlog / paper walkthrough / editorial narrative |
| psychological tone | warm, trust, product feel | cool, focused, content feel |
