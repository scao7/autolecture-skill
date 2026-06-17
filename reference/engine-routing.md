# Engine selection decision tree

Every beat must pick one visual engine. Below is the routing table by content type.

## Quick decision

```
What is the beat's content?
├── Math formulas / geometry / 3D point cloud / function plots / physics simulation
│   → Manim (.py)
├── Big-number flip / timeline animation / multi-stage transitions / typewriter text
│   → Remotion (.tsx)
├── Paper title / cards / comparison layout / flowchart / table / concept diagram
│   → HTML (.html)
├── Real photo / uploaded illustration
│   → \imageFile{path}
└── AI-style illustration (watercolor / cartoon / concept art)
    → \image[engine=gemini]{prompt}
```

## Detailed rules

### Manim (math/geometry)

**Use for**:
- 3D point clouds, vector fields, matrix transforms
- Math formula morphs (`TransformMatchingTex`)
- Geometric proofs (splitting a square, drawing tangents)
- Function plots, parametric curves
- Gravity/physics simulation (a ball dropping)

**Avoid for**:
- Text-heavy scenes (Manim renders text slowly and ugly)
- Complex animation + many elements (easily hits the 300s timeout)
- Simple card layouts (HTML is 100x simpler to write)

**Render-time rough estimate**: 480p15 default → render time ≈ scene duration × 3-8x. **Manim scenes over 70 seconds must be split**, or switch to Remotion DOM.

**Standard header**:
```python
from manim import Scene, ThreeDScene, Circle, ... 
from manim import PI, ORIGIN, UP, DOWN, RIGHT, LEFT, WHITE, BLUE, RED, YELLOW, GREEN

class LectureScene(Scene):  # or ThreeDScene
    def construct(self):
        # ...
        self.play(FadeIn(...), run_time=1.0)
        self.wait(2.0)
```

### Remotion (fine-grained animation)

**Use for**:
- Big-number reveal (a "48×" flip)
- Typewriter text / blur → sharp
- Multi-stage transitions (multiple `interpolate` + `spring`)
- L2-distance line chart + marked peaks
- Counters (6 → 5 → 4 → 1)
- Abstract timeline animations like tape-tearing / jigsaw
- Heavy particle DOM simulation (a lightweight alternative to Manim 3D point clouds)

**Avoid for**:
- Static cards (HTML is shorter)
- Math-rigor requirements (use Manim)

**Must export**:
```tsx
export const FPS = 30;
export const WIDTH = 1280;
export const HEIGHT = 720;
export const DURATION_FRAMES = N * FPS;
export const Comp: React.FC = () => { ... };
```

### HTML (cards/layout/text)

**Use for**:
- Paper title card (title + authors + arxiv)
- Three-column comparison, four-card grid
- Flowcharts, timelines
- Formula card (with color annotations)
- Intro / summary / acknowledgments
- Simple SVG icons

**Avoid for**:
- Complex timelines (use Remotion when you need precise frame-level control)
- True 3D (use Manim)

**Standard header**:
```html
<!DOCTYPE html>
<html lang="zh"><head><meta charset="UTF-8"><title>...</title>
<style>
  html, body { margin: 0; padding: 0; width: 100%; height: 100%;
               background: #0d1117; overflow: hidden;
               font-family: 'Inter', system-ui, 'PingFang SC', sans-serif;
               color: #fff; }
  .stage { width: 100vw; height: 100vh; display: flex; flex-direction: column;
           align-items: center; justify-content: center; padding: 50px;
           box-sizing: border-box; }
  @keyframes in { to { opacity: 1; transform: translate(0); } }
</style></head>
<body>
<div class="stage">
  ...
</div>
</body></html>
```

### `\imageFile` (uploaded assets)

**Use for**:
- You have a specific real photo, document screenshot, or product image
- Illustration the user prepared in advance

**Note**:
- Put files under assets/figures/
- Use `[fit=contain]` to avoid cropping

### `\image` (AI image generation, Gemini)

**Use for**:
- You need original illustration but don't want to find a designer / draw it yourself
- Consistent style (paired with `\style{}`)
- One-off concept art ("a girl having an idea", "a cartoon duck by the water")

**Avoid for**:
- Containing specific text (AI often gets text wrong)
- Requiring data accuracy (charts)

**How to call**:
```latex
\image[engine=gemini, aspect=16:9]{a thoughtful person at a desk, soft watercolor}
```

## Consistency principle

**Visual consistency takes priority over engine count.** The real disease of "looks like PPT" is **static stacking** — hard cuts between motionless cards, not "only used one engine".

- **Only static stacking looks like PPT**: no entrance animation, no continuous micro-motion, hard cuts between views.
- **A systematic animated hand-drawn SVG/HTML is not PPT**: stroke `draw`, fill fade-in, `feTurbulence` pen jitter, and `bob/sway/spin` micro-motion form one coherent language, and the whole video becomes a moving storybook, not slides.

So: to unify style (e.g. hand-drawn storybook throughout), **deliberately converging on a single engine is reasonable and encouraged**. Don't sacrifice visual consistency just to hit "≥3 engines". For specific techniques see [`hand-drawn-storybook.md`](hand-drawn-storybook.md).

The distribution table below is only a default starting point for a **mixed explainer video**, not a hard target — style-unified projects (hand-drawn storybook, pure-Manim math lessons) can and should deviate from it:

| Engine | Share |
|---|---|
| HTML | 50-60% (workhorse, cheap and stable) |
| Remotion | 25-35% (big numbers, timelines, abstract animation) |
| Manim | 5-15% (only when math/3D is genuinely needed) |
| `\image` AI | 0-5% (people/illustration) |
| `\imageFile` | 0-10% (specific assets) |
