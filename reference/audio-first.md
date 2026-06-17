# Audio-first timing — three-engine comparison

**Core principle**: audio length is ground truth. Visuals adapt to audio, never the other way around.
At compile time the compiler already knows the audio duration (target_dur); each of the three engines adapts differently.
This is the iron law shared by every workflow (HARD BAN #10) — read this page before writing any scene.

Consequences of violating it: scenes show either "animation ends early + frozen tail" or "animation runs faster than audio → too quick to read."

---

## `\manimFile[retime=true]{}` — compiler AST scale (must explicitly enable `retime=true`)

⚠️ **Since 2026-05-22, `\manimFile` no longer auto-scales duration by default**. Hand-written source renders at native speed by default (non-destructive
principle — it won't secretly alter your code); duration alignment is left to the compositor's hold/trim (audio longer than animation → freeze last frame; shorter →
truncate). To get audio-first auto-scaling, **the view MUST write `\manimFile[retime=true]{path.py}`.**
**Every `\manimFile` the skill generates always adds `retime=true`.**

With `retime=true` on, AutoLecture runs `fit_manim_to_target` over the source: it scans all `self.play(run_time=N)`
+ `self.wait(N)` in `construct()`, sums them to get natural_dur, then uniformly rewrites every
`run_time=` and `wait()` by the factor `target_dur / natural_dur` (clamped to [0.3×, 4.0×]).

**How to write**: write the scene at its "natural duration," write `\manimFile[retime=true]{...}` in the view, and let the scaler take over:
```python
self.play(FadeIn(circle), run_time=1.0)
self.wait(2.0)
self.play(circle.animate.scale(1.6), run_time=1.5)
```
**Don't**:
- Omit `retime=true` — the scene won't scale, and the moment the audio is longer the picture freezes (the most common pitfall).
- Estimate "audio is 15s so run_time=2.5" — when the TTS actually comes out at 14.3s the whole video is off.
- Use `time.sleep()` or any non-Manim timing — the scaler can't see it.

---

## `\remotionFile{}` — `useVideoConfig().durationInFrames` relative time

The compiler only overrides the top-level exported `DURATION_FRAMES` constant; **it does not change the component body**. So
hard-coding `interpolate(frame, [0, 30], ...)` in the component will end at 1s and freeze for the rest.

**How to write**: compute phase boundaries with `useVideoConfig().durationInFrames`:
```tsx
const { durationInFrames: dur } = useVideoConfig();
const kickerOp = interpolate(frame, [0, dur * 0.10], [0, 1], { extrapolateRight: 'clamp' });
const titleOp  = interpolate(frame, [dur * 0.10, dur * 0.20], [0, 1], { extrapolateRight: 'clamp' });
const accentOp = interpolate(frame, [dur * 0.85, dur], [0, 1], { extrapolateLeft: 'clamp' });
```
**Don't**: hard-code absolute frame numbers (`[0, 30]`, `[60, 90]`).

---

## `\htmlFile{}` — short entrance + continuous micro-motion

The compiler **does not change CSS keyframes**. Playwright records the full page for `target_duration` seconds;
once the CSS animation ends, you get a frozen frame.

**How to write**:
1. **All entrance animation finishes within 1.0–1.5s** (use staggered `animation-delay`: 0.2s / 0.4s / 0.6s).
2. **Keep at least one element in continuous micro-motion** (slow pulse / horizontal scan / drift) — so long audio
   keeps the picture "breathing" instead of becoming a still image.
3. **No long queues of sequential delays** (`delay: 0s; 4s; 8s; 12s`) — if the audio is actually
   5s, the later elements never appear.

`templates/scene_html.html.tpl`'s `.accent-pulse` + `.underline-scan` are the default
"breathe + sheen" skeleton.

---

## Hard timing budget: entrance ≤1.5s, then only looping micro-motion

The duration of an HTML/SVG scene is driven by the `\say` narration — the moment the narration starts, the picture must be **basically in place.**
So the entrance animation can't drag on, or you get "the narration is halfway through and the figure is still being drawn stroke by stroke."

**Budget**:

| Phase | Time window | What goes here |
|---|---|---|
| Entrance (draw / fade / rise) | **≤ ~1.5s** | stroke `@keyframes draw`, fill fade-in, title rise — draw it all once |
| Sustain (all remaining duration) | after 1.5s | **only** looping micro-motion like `bob` / `sway` / `spin` to fill; no more "new things appearing" |

**How to write**: stagger the entrance with `animation-delay` (0.2s / 0.4s / 0.6s) so even the last line finishes drawing by ~1.5s;
afterward all motion is a small-amplitude loop with `animation-iteration-count: infinite`:

```css
/* entrance: 1s draw line + 0.6s stagger, finishes within 1.6s at the latest */
.stroke { animation: draw 1s ease forwards; }
.stroke.s2 { animation-delay: 0.4s; }
.fill { animation: fade 0.8s ease 1s forwards; }   /* fill only after the lines */

/* sustain: only looping micro-motion, infinite loop */
.char { animation: bob 2.6s ease-in-out infinite; }
@keyframes bob { 50% { transform: translateY(-6px); } }
```

**Don't**: drag the entrance out to 3s+, or have elements appear slowly one after another (sequential delays) —
the narration finished that line long ago while the picture is still filling in frames.

**Self-check (recite after writing each HTML/SVG scene)**:
> **Entrance ≤1.5s, then only looping micro-motion.**

The full hand-drawn storybook toolkit (stroking / filling / pen jitter / bob-sway-spin) is in
[`hand-drawn-storybook.md`](hand-drawn-storybook.md) — that rhythm lands right inside this budget.
