# Workflow · User provides PDF paper → explainer video

**Entry**: user gives a PDF (usually a paper / arxiv link / .pdf file).
A PDF has **two completely different intents**; judge before acting (see [`../reference/pdf-showcase.md`](../reference/pdf-showcase.md)):

| Flow | What the user wants | How to do it | PDF on screen? |
|---|---|---|---|
| **A · Explain the knowledge** (default)| "Make this paper clear" | LLM reads PDF → voiceover script → extract figures for the visuals | ✗ Only a source asset; the visuals are freshly designed scenes |
| **B · Show the PDF** (focus of this flow)| "**Show** this PDF in the video — page-turn / zoom / highlight a sentence" | `react-pdf` renders the real pages directly + zoom / scroll / highlight | ✓ Real pages on screen |

Decision: "explain / popularize" → A; "show the original / page-turn / zoom the original text / highlight this sentence / like flipping a magazine" → B; if unclear, ask one question. **The two are often mixed** (A as the main line, with B's original-text highlight shots inserted to emphasize key sentences).

> Where does narration come from? A PDF has no built-in narration — either the LLM writes the voiceover from the PDF (`\say{}` TTS), or the user separately provides a recording (layer in [`audio-upload.md`](audio-upload.md)). Confirm the narration source first.

---

## Common steps

### 0 · Use the mode already confirmed at the SKILL.md entry

> **The run mode was already set at SKILL.md entry ①** (mcp / zip).

If narration goes via TTS (LLM writes the PDF explainer script), the **voice clone decision** is the same as audio-upload / text-to-lecture — by run mode (mcp checks `whoami` / zip uses `AskUserQuestion` to ask the user). If narration uses a recording the user separately provided (layer in the audio-upload workflow), handle it per that workflow's step 0.

See [`../reference/runtime-modes.md`](../reference/runtime-modes.md) for details.

### 1 · Prepare work directory
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
```
The PDF always goes in as a **project asset** under `<work>/` (Flow B's scene grabs it via `staticFile('paper.pdf')`).

---

## Flow A · Explain the knowledge (extract figures as assets)

1. LLM reads PDF → write the voiceover script (clear beginning/middle/end, 5–12 segments).
2. Extract figures:
   ```bash
   python3 scripts/extract_pdf_figures.py --pdf <paper.pdf> --out <work>/figures/
   # default figures-only: fig-1.png .. fig-N.png + manifest (with captions)
   # only add --with-pages if you need full pages (for text highlight / formula zoom / full-page scroll) (HARD BAN #9)
   ```
3. Match figures by audio anchor sentences ("Figure N / Fig N / caption keyword" → corresponding fig). **Each figure needs anchor-sentence evidence** written into `beat_plan.md` (HARD BAN #8).
4. Extracted figures **must not be laid out bare** (HARD BAN #6) — wrap each in at least one dynamic: Ken Burns ([`../templates/scene_image_zoom.tsx.tpl`](../templates/scene_image_zoom.tsx.tpl)) / crop-reveal / annotate / side-by-side. Rules in [`../reference/figure-matching.md`](../reference/figure-matching.md).

→ After this it's the ordinary "pick engine + hand-write scene + assemble tex", same as [`text-to-lecture.md`](text-to-lecture.md) steps 3–6.

---

## Flow B · Show the PDF (react-pdf real pages, pdf2video shot grammar)

**Real PDF pages appear in the final image**, via `react-pdf` (pdfjs) vector rendering built into the AutoLecture Remotion bundle — zoom in arbitrarily without blur, **no pre-rasterization, does not run** `extract_pdf_figures.py`.

### Shot grammar (4 scenes, each = one beat of narration)
Full description + key parameters in [`../reference/pdf-showcase.md`](../reference/pdf-showcase.md).

| scene template | What this beat of narration is doing |
|---|---|
| [`scene_pdf_overview`](../templates/scene_pdf_overview.tsx.tpl) | "Let's quickly skim this paper" — a few pages fan out to establish the shot |
| [`scene_pdf_switch`](../templates/scene_pdf_switch.tsx.tpl) | "Turn to the next page / the experiments page" — page A slides to page B |
| [`scene_pdf_focus`](../templates/scene_pdf_focus.tsx.tpl) | "Look at this part" — push in / scroll to a region |
| [`scene_pdf_highlight`](../templates/scene_pdf_highlight.tsx.tpl) | "The key is this sentence" — push in + highlight the sentence the narration is quoting |

Typical arrangement: `overview` (open) → `switch` (turn to the target page) → `focus` (push to the target region) → `highlight` (nail the key sentence). Pick as the narration needs; you don't have to use every kind.

### How "locating" lines up (core — this is the "render + locate" the user wants)
**Never hardcode coordinates.** Put the phrase this beat of narration quotes into the template's `TARGET` / `FOCUS_PHRASE`; the template uses pdfjs's text layer to auto-locate the bbox, then pushes the zoom's `transform-origin` onto that sentence:
1. The sentence this `\say{}` beat covers → pick a few **distinctive, easy-to-match** words from it (avoid "the"/"of") and put them into the placeholder.
2. In the scene `page.getTextContent()` finds the text item containing the phrase → `viewport.convertToViewportPoint()` converts to a pixel bbox.
3. The highlight box is drawn on the bbox, the zoom pushes to the bbox center — the camera arrives just as the narration finishes saying it.

### Must-have details
- **PDF uploaded as an asset**; scene uses `staticFile('paper.pdf')`.
- **audio-first**: `DURATION_FRAMES` gets rewritten by the compiler into `\say{}`'s real duration — animate with `durationInFrames` ratios, don't assume a fixed frame count (see [`../reference/audio-first.md`](../reference/audio-first.md)).
- **CJK / math / subset fonts**: always include `<Document options={{cMapUrl, cMapPacked}}>`, otherwise glyphs go blank (the switch/overview templates already bundle `PDF_OPTS`).

### In main.tex
```latex
\begin{view}
  \say{这篇论文我们快速过一遍。}
  \remotionFile{scenes/pdf_overview.tsx}
\end{view}
\begin{view}
  \say{论文里这句话最关键 —— 基率其实非常重要。}
  \remotionFile{scenes/pdf_highlight_baserate.tsx}   % TARGET set to「基率」
\end{view}
```
(The `\say{}` and TARGET example values above are kept in Chinese on purpose — they demonstrate narrating/locating a Chinese-topic PDF; the skill still produces videos in the user's topic language.)

### Acknowledgement
Flow B's shot grammar (overview/switch/focus/highlight, pdfjs text-layer locating, cMap) is borrowed from [DangJin/pdf2video](https://github.com/DangJin/pdf2video) (MIT), rewritten to AutoLecture's `\remotionFile{}` + audio-first conventions, and extends its "show only the author's existing annotations" into **narration-driven arbitrary text highlight / locating**.

---

## README + delivery
The PDF goes into the included items (Flow B needs it as an asset). Then → **delivery: see [`_delivery.md`](_delivery.md)**.
