# Borrowed Techniques — Motion Patterns Worth Stealing (Conceptually)

This file is a learning reference for Claude when writing
`\htmlFile{}` / `\remotionFile{}` scenes. It distills **techniques**
from public motion-graphics skill repos so future scenes can implement
the same effects from scratch, AutoLecture-themed.

> **Attribution & license:**
> The patterns below are summarized from
> <https://github.com/vibe-motion/skills> (the `vibe-motion` Claude
> skill collection, 500+⭐). That repo carries **no license file**, so
> default copyright applies — we read it for ideas, we DO NOT copy
> code into AutoLecture. Every scene that ships in this skill is
> hand-written from the technique description, not copy-pasted from
> someone else's source.

---

## When to reach for a borrowed technique

You're writing a scene and the script calls for something more
sophisticated than "fade in title, fade out title." Skim this file
first, pick the matching technique, then implement from scratch in
HTML / CSS / Remotion / Manim.

---

## 1. Infinite seamless scroll — credit rolls, tech stack, "by the numbers"

**When**: vertical or horizontal scrolling content that should feel
endless (a list of features, a long credit roll, a multi-column
photo wall).

**Technique** — domain duplication + modular arithmetic:

- Duplicate the content list inline: `[...items, ...items]`.
- Compute a `progress` from 0 → 1 across the loop duration.
- Translate the strip from `0%` to `-50%`. Because the second half is
  identical to the first, the frame at `-50%` is visually the same
  as `0%` and the seam is invisible when it resets.

**3D feel** (optional, gives gravitas to a credit roll):
- Parent wrapper: `perspective: 1000px; transform: rotateX(20deg) scale(1.2);`.
- The `scale(1.2)` is load-bearing — it pushes the tilted top/bottom
  edges off-screen so you don't see empty background bleed.

**Edge fade** so the strip doesn't have hard cut-offs:
- Absolute `linear-gradient` overlays at top + bottom with a high
  `zIndex`, blending to the background color.

**AutoLecture fit**: outro credit roll, a `\remotionFile{}` scene
listing "16 frameworks compared" or "by the numbers" cards.

---

## 2. Frame-driven continuous rotation

**When**: anything that spins forever — a logo, a vinyl record, a
loading wheel, an orbiting label.

**Technique**:

```
rotation_deg = (frame / (fps * seconds_per_revolution)) * 360
```

In Remotion, get `frame` from `useCurrentFrame()` and `fps` from
`useVideoConfig()`. Apply as `transform: rotate(${rotation_deg}deg)`.

**Pair with marquee scrolling text** (long titles that don't fit
in one line): duplicate the text node and translate the flex container
from `0` to `-50%` (same trick as #1, applied to text width).

**Realistic disc texture** (vinyl-record vibe) — pure CSS, no images:
- `radial-gradient` rings simulate grooves
- `box-shadow: inset` simulates label depth + edge lighting

**AutoLecture fit**: any view that shows a spinning element while
the narrator talks (turntable, dial, planet).

---

## 3. "Explode then assemble" — dramatic reveal of a complex diagram

**When**: a complex SVG (system architecture, anatomy, exploded
mechanical view) needs an entrance that feels purposeful, not
slideshowy.

**Technique** — reverse logic + overshoot easing:

1. **Reverse start state**: pieces are NOT off-screen waiting to fly
   in — they start INSIDE the frame and get *thrown out* in step 1
   with extreme directional scaling (`scaleX: 0.05, scaleY: 4`)
   simulating motion blur / speed.
2. **Hero settle**: the main body/skeleton element returns first with
   `elastic.out` easing (~1.5s).
3. **Detail stagger**: remaining parts return in randomized order
   (`stagger: 0.02-0.05`) with `back.out(2.5)` — the overshoot is
   what makes it feel like the pieces *click* into place.
4. **Whole-scene rotation** during the settle (180° or 360°) adds
   the "force" feel without being gratuitous.

**Suggested easing intensities**:
- Standard assembly: `back.out(2.5)`, duration 1.2s
- "Forceful": `back.out(5)`, `rotation: -360`, duration 0.7s
- Elegant: `power4.out`, `stagger: 0.02`, duration 1.5s

In `\htmlFile{}` use GSAP from CDN; in `\remotionFile{}` write the
same curves via `interpolate(frame, [...], [...], { easing: ... })`.

**AutoLecture fit**: any view that introduces a non-trivial diagram
(model architecture, pipeline schematic, formula breakdown). Beats a
plain fade.

---

## 4. Swinging spotlight reveal

**When**: a title card that needs to feel dramatic / cinematic
(opening title, section header).

**Technique**:
- SVG (or CSS clip-path) spotlight cone that swings through an arc.
- Pivot at the **top vertex** of the cone (where the lamp would be),
  not the center — so the beam grows from the lamp tip naturally
  rather than rotating around its middle.
- Text underneath only becomes visible where the cone overlaps;
  outside the cone it's masked to background color.
- Configurable swing angle (typically 30-60°) and cycle period.

**Adds polish**: glow halo at the lamp tip via `filter: blur(...)`
or `radial-gradient`; soft cone edge via SVG gradient stops fading
from `mask_color` to transparent.

**AutoLecture fit**: opening title view for a longer demo, or the
final "thank you" card. Restraint: don't use more than once per
video or it stops being special.

---

## 5. Typewriter / prompt-reveal

**When**: showing code, a CLI command, or a prompt being entered.

**Technique**:
- Character-by-character reveal driven by `frame / typingSpeedFrames`.
- Optional blinking cursor: opacity alternates on a fixed cycle.
- For Claude-style prompts: a slight tilt at start (`rotateX(8deg)
  rotateY(-3deg)`) that levels off to flat by frame N — gives
  perspective entrance.
- For transparent compositing into a parent scene, render with
  `--codec=prores --pixel-format=yuva444p10le` (Remotion) so the
  alpha channel survives.

**AutoLecture fit**: code-walkthrough scenes (`\remotionFile{}` of
each code snippet appearing typewriter-style), or any view where
showing the typing itself is the point.

---

## 6. Procedural motion (sine-driven body / orbits / waves)

**When**: any "alive" decorative element that should keep moving
while the narrator speaks — fish swimming, hair, plants in wind,
particle drift.

**Technique**:
- Each segment of the body has a base position + a sine offset:
  `pos[i] = base[i] + amplitude * sin(t * freq + phase * i)`.
- Phase offset between segments creates the wave-propagation feel.
- Smaller amplitude on tail/extremities than on body to look
  natural.

**AutoLecture fit**: ambient backgrounds (`\htmlFile{}` with a few
SVG fish / particles) for views where the foreground is text — keeps
the eye engaged without distracting.

---

## Adjacent ideas worth considering (not techniques per se)

- **One-asset-per-skill granularity**: vibe-motion ships each pattern
  as its own skill (`remotion-3d-ticker`, `light-spotlight-render`,
  etc.) rather than one monolith. If AutoLecture wants discoverable
  building blocks via claude.ai's Personal Skills marketplace, the
  unbundling pattern is a good model.
- **"How it works" sections in SKILL.md**: each vibe-motion skill
  explains the technique before the "how to use" — useful for future
  Claudes adapting the pattern.
- **`npx skills add <repo>`**: their interactive installer pattern.
  Could be a v0.2 distribution thought for AutoLecture if individual
  scene-pattern skills get split out.

---

## What this file is NOT

- Not a license to copy vibe-motion source code.
- Not a license to copy any commercial template's source code either.
- Not a binding contract on scene aesthetics — these are *patterns*,
  pick the right one for each beat, ignore them all if the script
  calls for something else.

If you (the Claude running this skill) need an actual implementation
of any technique above, write it from scratch in the appropriate
engine and add it to `templates/` if it's broadly reusable.
