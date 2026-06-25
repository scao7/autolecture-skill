# Workflow · Simple instruction / text script → explainer video (audio-driven)

**Entry**: user gives only **one instruction / one topic / a text script** — no recording, no PDF, no live-action.
Narration is synthesized via TTS (`\say{}`); all visuals are hand-written source.

> **Audio-driven + finalize first**: this flow has no existing audio, so **the first thing to do is write the voiceover script and get the user to finalize it** — the voiceover script is the spine of the whole video's timeline; only after it's locked do all the visuals arrange around it.

> Supporting assets (GitHub repo screenshots / local images) are an opt-in increment, see [`../reference/figure-matching.md`](../reference/figure-matching.md). If the user actually gave a PDF / recording / live-action → route back to the corresponding workflow.

---

## Steps

### 0 · Use the run mode already confirmed at the SKILL.md entry + decide voice clone handling

> **The run mode was already set at SKILL.md entry ①** (mcp / zip); don't ask again here.

**Voice clone decision** (text-to-lecture defaults to TTS, must be done):
- **mcp**: check whether the user info from `whoami` has a voice sample; yes → "all `\say[voice=mine]`"; if you can't get it, ask the user as in zip.
- **zip**: `AskUserQuestion`, two choices: ① yes, use my cloned voice (whole video `voice=mine`) ② no / unsure (default speaker).

Write the decision into the plan notes in `<work>/script.md`. The whole video's `\say` uses one and the same handling. For the per-action correspondence of the mcp / zip modes, see [`../reference/runtime-modes.md`](../reference/runtime-modes.md).

### 1 · Prepare work directory
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
```

### 2 · Write the voiceover script → hand to user for edits / approval (**hard gate, stop here first**)
- Turn the user's instruction / topic / material into a **complete, segmented voiceover script** (each segment is the `\say{}` content of a later view).
- Write it to `<work>/script.md`, numbered by segment, with a **one-line visual intent** under each segment (what this beat should make the viewer see).
- **You MUST send the voiceover script to the user and wait for edits / approval before continuing.** Don't skip this step and go straight to the visuals — the script is the timeline; if the script isn't locked, the visuals are wasted work.
- User edits → update `script.md` and confirm once more; explicit approval → proceed to the next step.

### 3 · Estimate each segment's duration (TTS time) → cut views
- After the script is finalized, roughly estimate each segment's TTS duration by character count (Chinese ~4–5 chars/sec; English ~2.5 words/sec) and note it in beat_plan, for planning.
- **Real durations are auto-locked at compile time by TTS + audio-first** (the actual speech length of `\say{}` drives that view, visuals adapt via audio-first, see [`../reference/audio-first.md`](../reference/audio-first.md)) — so the estimate is only for layout and need not be precise.
- 5–12 segments, each 30–90 seconds; output `<work>/beat_plan.md`:

```markdown
| # | Est. | Voiceover point | Visual engine | Design note |
|---|------|----------|----------|----------|
| 1 | ~22s | Pose a counter-intuitive question | Remotion | Question text typewriter + large question-mark pulse |
| 2 | ~38s | Three core numbers   | HTML     | Three-column cards stagger-reverse |
```

### 4 · Root skeleton first (**before writing any visuals**, build it and immediately land it in the cloud)

> Hard-won lesson: leaving root assembly to the end = the project is long not in a "compilable state", and a mid-flow disconnect / resume leaves a pile of scraps. **The skeleton must be built and committed before you write the first scene's source.**

1. **Build the skeleton first**: turn every beat cut in step 3 into one `\begin{view}…\end{view}`, view count = beat count (not one fewer). In each view first put:
   - **Placeholder `\say{}`**: fill in **the corresponding segment of the finalized voiceover text** (narration is in the view from second one, not floating in a draft).
   - **Placeholder `\htmlFile{}`** (or the corresponding engine file): point at a **not-yet-written** filename `scenes/scene_NN_label.html`.
2. **`\say` and visual always co-located**: from the start, `\say{}` sits in the **same view** as its `\htmlFile{}` (or `\manimFile`/`\remotionFile`), narration and visual bound together, never decoupled. Later you only swap file contents, never re-cut narration.
3. **Commit / write to cloud immediately**:
   - **mcp mode (JSON-canonical)**: a "view" here = a SHOT. `set_project(title,
     aspect_ratio, style)` once, then author shot by shot per [`_delivery.md`](_delivery.md)
     path A's incremental loop: `upsert_shot(id, duration, description, engine, src,
     say_text)` — the `\say{}` becomes `say_text`, the `\htmlFile`/`\manimFile`/
     `\remotionFile` becomes the base-layer `engine` + the `src` code file — then
     `write_file(src, …)` the scene code, then `render_shot(id, storyboard=true)` on
     the spot. (No `storyboard.tex` skeleton, no `commit_files`/`.tex` writes.)
   - **zip mode**: write the skeleton into `<work>/main.tex` (VideoTeX), fill in scene files one by one under `<work>/scenes/`.

Skeleton example (placeholder narration + placeholder filenames, all views built):
```latex
\title{<title>}
\aspect{16:9}
\style{<style>}
\begin{videotex}
\begin{view}[title=Scene_01_Hook]
  \say{<finalized voiceover segment 1 text>}
  \htmlFile{scenes/scene_01_hook.html}   % file to be written
\end{view}
\begin{view}[title=Scene_02_...]
  \say{<finalized voiceover segment 2 text>}
  \htmlFile{scenes/scene_02_....html}    % file to be written
\end{view}
...
\end{videotex}
```

> Naming discipline: **one project uses one prefix only** (e.g. all `scene_NN_`); replace an old version by overwriting the same `src` via `write_file` (or `remove_shot` to drop the view), don't let two naming schemes coexist — on resume, "which is the official one" rests entirely on the order of `get_state().shots[]` (the shot list is the manifest; there's no active-root `.tex`).

### 5 · Assign visuals to each segment by "the voiceover's point and meaning" + pick an engine
Read [`../reference/engine-routing.md`](../reference/engine-routing.md). **The visual must hook this beat's voiceover point and meaning**, not generic illustration: mentions a number → large-type reversal; mentions a process → card cross-fade; mentions collapse → point cloud contracting. Quick reference: large type / numbers / typewriter → Remotion; titles / cards / tables / flows → HTML; 3D / formulas / geometry → Manim; faces / scenery → `\image[engine=gemini]`. **Default to HTML** (fastest, most stable).

> **Engine consistency > engine variety**: don't misread engine-routing as "must use ≥3 engines or it looks like PowerPoint". **Static stacking** is what looks like PowerPoint; **systematic motion-graphic hand-drawn SVG / HTML is not PowerPoint**. To do a unified style (e.g. whole-video hand-drawn storybook) you may use a single engine throughout; visual consistency outranks engine count. For hand-drawn style see [`../reference/hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md).

### 5b · Fable / analogy to explain tech → get the mapping table approved first (**only if this kind of topic**)

If the topic is "use a story / fable to explain tech by analogy" (e.g. use a town market to explain MCP), **before touching visuals** strictly follow this gating order; get "OK" at each gate before passing to the next:

| Gate | Output | Why approve it first |
|---|------|------|
| ① **Mapping table** | A table mapping each tech concept ↔ story element **one-to-one** | If the mapping is wrong, everything after is wasted; nail down "server=shop / tool=shelf / token=pass" first |
| ② **Story throughline** | One narrative line stringing all mappings together (the voiceover script cuts views off this) | View order is only set once the throughline is set |
| ③ **One visual sample** | Run through the sample gating in step 6 below | Style sign-off |
| ④ **Mass production** | Fill the remaining views | Only after the first three gates are all "OK" |

Mapping table example:
```markdown
| Tech concept | Story element |
|---|---|
| MCP server   | a shop in the Town of a Hundred Crafts |
| tool         | an implement on a shelf in the shop |
| OAuth token  | a pass to enter the town |
```
(Example values above kept in English; original used a Chinese town/MCP fable — translated to keep it readable.)

### 6 · Sample-first gating (**mandatory — any multi-view task**)

> The most valuable step: **make just 1 sample view end-to-end, get sign-off, then mass-produce the rest.** Doing the full set first only to find the style is wrong = a dozen-view redo + a wasted full compile.

1. **Pick a representative shot** (the beat with the most characters / elements), **hand-write just that one** scene file (`upsert_shot` + `write_file` the code).
2. **Render**: mcp mode `render_shot(id, storyboard=true)` renders just that shot's still; zip mode does a local sample compile.
3. **Frame-check**: read the still back from `get_state()` → `shots[].render.still` (the URL the render folded in) — no `fetch_frame` / base64 decode. See [`../reference/compile-and-preview.md`](../reference/compile-and-preview.md).
4. **Get sign-off**: send the sample frame to the user (or self-check) and get an explicit "OK". **No sign-off, no mass production.**
5. After sign-off → only then enter step 7 to batch hand-write the remaining views.

### 7 · Hand-write each scene's source (mass-produce only after sample sign-off)
Skeletons in [`../templates/`](../templates/). **Strictly hand-write, do not call the LLM to emit code** (HARD BAN #1). Unified palette [`../reference/palette.md`](../reference/palette.md) + font stack; the **audio-first iron rule** is in [`../reference/audio-first.md`](../reference/audio-first.md); each scene designed independently (HARD BAN #2), ≤60s, named `scene_NN_label.<ext>` (carry over the prefix from the step 4 skeleton, one scheme throughout).

- **Hand-drawn storybook style** (whole-video unified hand-drawn SVG/HTML): technique in [`../reference/hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md) (stroke `pathLength=1` + `draw` keyframe, `feTurbulence` pen jitter, bob/sway continuous micro-motion, cream/navy/tan brand colors).
- Narration (`say_text`) ≤400 chars; captions off by default (set `say_burn=true` to burn). zip mode keeps the VideoTeX `[retime=true]` / `\say[burn=on]` spellings.
- Each finished shot: in mcp mode immediately `upsert_shot` it + `write_file` its scene code + `render_shot(id, storyboard=true)` on the spot (incremental loop, see [`_delivery.md`](_delivery.md)). Don't pile work up to the end.

> **Single-view preview during dev, full compile only at the end**: full compile is expensive and slow (each view synthesizes TTS + real-time records on the fly; the first full compile of a dozen views can hit hundreds of credits). During dev only render the block you changed; **warn the user of the cost magnitude before a full compile**. For the specifics of single-view preview (the sub-tex must be a body fragment, temporarily overwrite the active root into a single-view document) see [`../reference/compile-and-preview.md`](../reference/compile-and-preview.md).

### 8 · Full compile + README + delivery
Sample signed off, remaining views all filled → compile the whole video (in mcp mode, if every block was rendered in step 7, this step basically all hits cache). Use [`../templates/README.md.tpl`](../templates/README.md.tpl) to write the "how to use". Then → **delivery: see [`_delivery.md`](_delivery.md)**.

> **resume / continuation**: after a conversation is interrupted and reconnected, **the first action must be `get_state`**, taking the cloud project's ProjectState shots + their scene code as the single source of truth; treat "everything already written" in the summary / memory only as a clue, and verify with `read_file` one by one. See [`../reference/resume-checklist.md`](../reference/resume-checklist.md).
