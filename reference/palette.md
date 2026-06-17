# Visual palette + fonts · editorial dark (autolecture-skill default)

> This is the **default** editorial dark palette, suited for **content-is-the-star** vlogs / paper explainers / personal narratives — dark base, restrained, cool-toned.
>
> If the project is meant to **fly the AutoLecture banner** (official demo / teaser / tutorial / homepage showcase), use [`brand-style.md`](brand-style.md) instead — light cream + navy + tan gradient, matching the [autolecture.ai](https://autolecture.ai) site, Studio, and watermark. **Use one scheme per project, don't mix.**

## Palette

```
bg:        #0d1117   /* dark base, default background for all scenes */
fg:        #ffffff   /* primary text */
accent:    #6ec1e4   /* primary brand color - ocean blue */
highlight: #f4d35e   /* emphasis - warm yellow */
warn:      #ee6c4d   /* warning / red line - coral */
mint:      #4ec9b0   /* secondary emphasis - mint */
dim:       #5a6273   /* dimmed text */
sub:       #aab1c0   /* subtext / annotations */
border:    #2a2f3a   /* card border */
panel:     #1a2030   /* card base color */
```

## Font stack

```
font-family: 'Inter', system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

Math formulas:
```
font-family: 'Latin Modern Math', 'Cambria Math', 'STIX Two Math', serif;
```

Brush / calligraphy (for things like "大道至简"):
```
font-family: '楷体', 'KaiTi', 'STKaiti', 'Songti SC', serif;
```

## Text hierarchy

| Type | Size | Weight | Tracking |
|---|---|---|---|
| Headline (hook) | 96-124px | 800-900 | -2 |
| Subhead | 38-56px | 700 | -0.5 |
| Section title | 24-32px | 700 | 0 |
| Body | 16-22px | 400-500 | 0.3 |
| Meta (kicker) | 12-14px | 600 | 4-6 |

## Animation grammar (key to consistency)

| Action | CSS / Remotion |
|---|---|
| fade-up (appear) | `opacity: 0 → 1, transform: translateY(20px → 0)` |
| pop (pop out) | `opacity: 0 → 1, transform: scale(0.85 → 1)` |
| typewriter | reveal characters sliced by frame |
| strike-through | `::after` pseudo-element width: 0% → 100% |
| underline draw | same but horizontal |
| number roll | switch displayed digits by frame (Remotion) |

Timing: kicker out at 200ms, title at 400ms, content starts appearing staggered at 600ms.

## Remotion standard exports

```tsx
export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const DURATION_FRAMES = N * FPS;   // N seconds
```

The compiler overrides `DURATION_FRAMES` by audio duration at render time (via Comp.tsx's `n_replaced` path), so a reasonable default for this value is enough.

## HTML scene template style

- `body { background: #0d1117; }`
- Centered stage: `display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 50px;`
- Entrance animations consistently use `@keyframes` + staggered `animation-delay`
- Use inline `<style>`, **no external CSS / web fonts**
- viewBox 16:9 default (1280×720); for 9:16, change the stage width/height
