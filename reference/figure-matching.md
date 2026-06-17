# Matching assets to audio beats

How a grabbed figure (PDF page / figure / repo screenshot) maps to a segment of the transcript — anchor-sentence rules + design recommendations.

## General principle

**Every figure used must have anchor-sentence evidence.** Write it into `beat_plan.md`:

```markdown
| figure | matched beat | anchor evidence (verbatim transcript sentence) |
|---|---|---|
| `figures/fig-3.png` | beat 7 (collapse) | "As shown in Figure 3, all vectors collapse to the same point" |
```

No anchor sentence found → **don't use it**. Better to leave a passage with no figure than to shove one in because "this part is roughly about that."

---

## Anchor rules for PDF papers

**Default to figure crops only** — `extract_pdf_figures.py` is figures-only by default. Full-page rasters only appear when you explicitly do a "text highlight" (`--with-pages` flag).

### Strong match (use the figure directly)

| transcript mentions | matches |
|---|---|
| "Figure 1 / Figure 2 / Figure 3" | `fig-1.png` / `fig-2.png` / ... (numbered by detection order in the manifest) |
| "Figure 1 / Fig. 2" | same as above (mixed-language recording case) |
| "as shown / the figure above / the figure below" | nearest figure in context (look-back/forward in beats) |
| a fragment of the paper caption text appears | "the loss landscape figure" matches the figure whose caption contains "loss landscape" |

### Text-highlight cases (need `--with-pages`)

The cases below are the **only** ones that need a full-page raster — a single figure isn't enough. Explicitly tag `[needs-page]` when planning, and re-run `extract_pdf_figures.py --with-pages`:

| transcript case | full-page usage |
|---|---|
| "let's look at equation (3) here" | full page + zoom to the equation region + red-box annotate |
| "the original text says..." quoting a passage | full page + highlight that passage's bounding box |
| reading the paper's abstract / introduction aloud | full page slow scroll |
| section title page as a divider card | full page as a static chapter divider |

### No match (don't force a figure)

- A passage that's all macro narrative / philosophy / acknowledgements → use a pure Remotion/HTML scene
- No figure-relevant anchor sentence at all → don't force a figure

---

## Anchor rules for GitHub repos

### Strong match

| transcript mentions | matches |
|---|---|
| a heading / paragraph that appears in the README | the figure that README section references (check `manifest.json::readme_refs`) |
| screenshot title / alt text | "let's open the settings page" → matches the figure with alt="Settings page" |
| module name / filename | "look at the dashboard component" → matches `dashboard.png` or a figure under `docs/dashboard/*` |
| command / terminal output | matches a terminal screenshot (if any) |

### Weak match

| transcript mentions | hint |
|---|---|
| logo / brand name | only use the logo in the intro / closing-thanks segment |
| "demo" | use the README's top hero screenshot |

---

## Visual-effect decisions

Pick the effect by figure content and beat rhythm (avoid bare figure dumps; never use the same one for everything):

| case | recommended effect | implementation location |
|---|---|---|
| paper figure, single image, focus on one region | **Crop + Ken Burns zoom-in** (slow push toward focal point) | `scene_image_zoom.tsx.tpl` |
| paper figure, whole image matters (architecture/flow diagram) | **Ken Burns slow pan** (sweep left to right) | same, tune params |
| two figures compared (before / after) | **Side-by-side**, staggered entrance | HTML grid |
| repo screenshot, need to point at a UI element | **Annotate overlay** (red box + arrow + text label) | Remotion, `<svg>` above the image |
| repo multiple screenshots, continuous walkthrough | **Card transition**, fade in the next one | HTML keyframe |
| logo entrance | **Pop + scale up** (spring) | Remotion `spring` |
| paper equation page (`--with-pages`) | **Page scroll** (translateY), stop at the equation + red-box highlight it | hand-written Remotion |
| paper text quote (`--with-pages`) | **Highlight rect**: dim the whole page to 50%, keep the text bbox at 100% brightness | Remotion `<svg mask>` |

### Ken Burns parameter recommendations

For a 10s scene + 1280×720 canvas use:
- start: `scale(1.0) translate(0,0)`
- end:   `scale(1.15) translate(-40px, -20px)` (subtle drift toward focal point)
- easing: `easeOutQuart` (70% of the animation is done by 50% progress — gives viewers a buffer to see clearly)

For equation zoom use:
- start: full page visible
- mid (t=2s): zoom 4× to formula region
- hold mid 6s (let the user read)
- end (t=10s): zoom slightly to 5× for emphasis

### Annotate mode

For red box + arrow + label, draw an absolutely-positioned `<svg>` layer above the figure. Three-color palette:
- `#ee6c4d` (warn) — primary annotation
- `#6ec1e4` (accent) — secondary annotation
- `#f4d35e` (highlight) — guide lines

---

## Cases with no audio anchor but you still want a figure

A few cases: the user gave a figure but the audio never explicitly mentions it — e.g. a logo entrance, a chapter cover page. These are allowed, but you **must** tag `[no anchor — decorative]` in `beat_plan.md`, and only use them for:

- Opening title card (logo / paper title page)
- Chapter divider card (paper section-header page)
- Closing acknowledgements (collaborator photos, etc.)

In body narration passages, "shoving in a figure by feel" is strictly disallowed.
