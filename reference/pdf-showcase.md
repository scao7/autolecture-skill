# PDF to Video — Two Flows

The user hands you a PDF (usually a paper). There are **two** completely different asks. Decide which one first, then pick tools.

| Flow | User wants | How | Visual assets |
|---|---|---|---|
| **A · Explain the content** | "Make this paper clear to me" | LLM reads PDF → rewrites into a narration script → pull figures for visuals | figure crops from `extract_pdf_figures.py` + hand-written scenes |
| **B · Show the PDF** | "Show this PDF in the video — flip pages / zoom / highlight a sentence" | Render the real PDF pages on screen directly: zoom / scroll / highlight | `react-pdf` renders real pages (no pre-rasterization) |

Decision rules:
- "Turn this paper into an explainer / a popular-science piece" → **A** (default)
- "**Show** this PDF in the video" / "flip pages" / "zoom into a passage" / "highlight this sentence" / "like flipping through a magazine" → **B**
- Ambiguous → ask: "Do you want me to **explain the knowledge inside** (with animations), or **show the original PDF in the video** (page flips + zoom + highlight)?"

The two can be mixed: A as the spine, with one or two B "original-text highlight" views in the middle to stress a key sentence.

---

## Flow A · Explain the content (existing flow)

Unchanged. See [`figure-matching.md`](figure-matching.md): pull figures → match against audio anchor sentences → Ken Burns / annotate. The PDF is only a **source of assets**; the final visuals are freshly designed scenes, and the original PDF never appears.

---

## Flow B · Show the PDF (react-pdf, new)

The **real PDF pages appear** in the final visuals. This relies on `react-pdf` (pdfjs) in the AutoLecture Remotion bundle to render the original PDF directly — vector-sharp, stays crisp at any zoom, no need to pre-rasterize to PNG.

### Prerequisites
- Upload the PDF as a **project asset** (same as audio/images). In a scene, `staticFile('paper.pdf')` reaches it (AutoLecture mounts the project `assets/` as the bundle's `public/` at compile time).
- No need to run `extract_pdf_figures.py` — react-pdf reads the original PDF directly.

### Camera language (4 scene types, borrowed from pdf2video)
Pick a scene by "what the narration is doing this beat." One view = one scene = one narration beat:

| Template | Narration action | Effect | Key params |
|---|---|---|---|
| [`scene_pdf_overview.tsx.tpl`](../templates/scene_pdf_overview.tsx.tpl) | "Let's skim this paper quickly" | A few pages **fanned/stacked** as an establishing view | `PAGES=[1,2,3,4]`, `SPREAD` |
| [`scene_pdf_switch.tsx.tpl`](../templates/scene_pdf_switch.tsx.tpl) | "Method done, **flip to** the experiments page" | Page A **slides/fades** to page B | `PAGE_FROM/PAGE_TO`, `DIR`, `TURN_AT` |
| [`scene_pdf_focus.tsx.tpl`](../templates/scene_pdf_focus.tsx.tpl) | "Let's look at **this block**" | Show a page + focus/scroll to a region (no highlight box) | `FOCUS_PHRASE` or `FOCUS_FX/FY`, `SCROLL` |
| [`scene_pdf_highlight.tsx.tpl`](../templates/scene_pdf_highlight.tsx.tpl) | "The key is **this sentence**" | Show a page + zoom in + **highlight the exact sentence the narration is saying** | `TARGET` (the phrase the narration quotes), `ZOOM_END` |

Typical choreography: `overview` (establish) → `switch` (flip to target page) → `focus` (push to target region) → `highlight` (pin the key sentence). You don't need all of them — pick by what the narration needs.

### Fonts / CJK: cMap config
Papers often contain CJK / math / subset fonts; pdfjs needs cMaps to render them correctly, otherwise glyphs go blank. `scene_pdf_switch` / `scene_pdf_overview` already carry `PDF_OPTS = { cMapUrl, cMapPacked }`; when writing a new PDF scene, always pass `<Document options={PDF_OPTS}>`.

### How to align the highlight (core)
**Do NOT hardcode coordinates.** The templates auto-locate via pdfjs's text layer:
1. Find which sentence the narration is saying this beat in `\say{}` → put that sentence (or one distinctive phrase from it) into `TARGET`.
2. In the scene, `page.getTextContent()` finds the text item containing `TARGET`, takes its `transform` → `viewport.convertToViewportPoint()` to get a pixel bbox.
3. The highlight box is drawn on that bbox; set the zoom's `transform-origin` to the bbox center → the camera pushes onto that sentence automatically.

Phrase-selection tip: pick a few **distinctive, easy-to-match** words from the line (avoid "the"/"of" and other ubiquitous words). The highlight granularity is the **whole line / whole text span** (pdfjs hands you text per span) — visually "highlight this sentence" is already clean enough. Word-level precision requires estimating from character proportions, which is inaccurate in proportional fonts; don't do it by default.

### audio-first
Both templates' `DURATION_FRAMES` get rewritten by the compiler to the real duration of the matching `\say{}` — so the zoom always lands exactly when the narration finishes. So write animations using "natural duration ratios" (`interpolate(frame, [0, durationInFrames-1], ...)`), don't assume a fixed frame count.

### In main.tex
```latex
\begin{view}
  \say{This sentence in the paper is the most important — the base rate actually matters a lot.}
  \remotionFile{scenes/pdf_highlight_baserate.tsx}
\end{view}
```
(The scene file is just `scene_pdf_highlight.tsx.tpl` with placeholders filled in.)

### Cost
A react-pdf scene is a hand-written `\remotionFile{}` → hits cache → re-compile is nearly 0 cost (same as any other `\manimFile`/`\htmlFile`). Much cheaper than `\remotion{prompt}` LLM generation.

---

## Acknowledgement
Flow B's scene grammar (focus zoom / scroll / highlight) is borrowed from
[DangJin/pdf2video](https://github.com/DangJin/pdf2video) (MIT) — pdfjs
worker config, `delayRender`/`continueRender` async loading, and focus/scroll
motion all reference it. Our implementation is rewritten to AutoLecture's
`\remotionFile{}` + audio-first conventions, and extends pdf2video's "only show
the author's existing annotations" into **narration-driven highlighting of
arbitrary text**.
