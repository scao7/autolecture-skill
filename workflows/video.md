# Workflow · User provides video → video (use the original video's audio, no TTS)

**Entry**: user gives a piece of **live-action video** (talking-head, screen-capture demo, product shots).
Most likely the user wants to **use the original video**, so **no TTS** — take the video's built-in audio as ground truth.

> Still **audio-driven**: the human voice in the video is the spine of the timeline; the visuals (keep live-action / cut to our assets / overlay motion graphics) all arrange around it.

> ⚠️ **Express all editing in .tex, NEVER pre-cut assets** (HARD BAN #11). The whole original video goes in as one asset;
> select a window with `\video[start=, end=]{original}` / `\audio[start=, end=]{original}` (the compiler takes the window from the original,
> the original is untouched), splice via view order, transition via `\fade`. **Do not** ffmpeg-slice/splice/retime outside and then drop it in —
> that bakes the edit into the file, bypassing .tex (P1 LaTeX is the single source of truth / preview equals export).

> 🎥 **Screen-capture + camera (Tella-style) assets are three files**: in-app `screen_cam` mode recording
> produces `{name}.webm` (rounded-corner avatar composite preview, for quick review only) + **`{name}.screen.webm` +
> `{name}.camera.webm`, two full raw tracks**. When composing a picture-in-picture layout **always use the two raw tracks**
> ([`templates/scene_screencast_pip.tsx.tpl`](../templates/scene_screencast_pip.tsx.tpl):
> SCREEN_FILE/WEBCAM_FILE point at the two files, PIP_SCALE/PIP_CORNER/PIP_MARGIN/
> MORPH_START/MORPH_END all tunable, includes the fullscreen-avatar→corner-shrink morph); don't put that composite preview file
> into the finished video. If you're unsure of the layout, extract the two tracks' frames LOCALLY (ffmpeg) and look first, then set parameters.

> 📝 **Captioning = writing an asset-level transcript**: `transcribe` to get word-level timestamps → `write_file` the corrected full transcript
> to `{media}.transcript.txt` → every view that references that asset auto-derives captions
> (window slicing + full-screen line breaking + punctuation stripped by default). Don't write captions into clip.tex / main.tex.

> 📚 **Reusing the same asset across multiple views → put it in a clip library** (a BibTeX for editing assets): collect the rough-cut results into
> `clips/*.tex` as `\begin{segment}{name}` (trim + optional `\caption`); in the main.tex preamble declare
> `\cliplibrary{clips/day1}` then reference with `\video{@name}`; for a single cut just inline
> `\video[start=, end=]`. This way, when a person later fine-tunes cut points / captions in Studio, they edit the same .tex.
> See the clip-library section of [`reference/dsl-cheatsheet.md`](../reference/dsl-cheatsheet.md) for syntax.

---

## Steps

### 0 · Use the run mode already confirmed at the SKILL.md entry

> **The run mode was already set at SKILL.md entry ①** (mcp / zip).

**This workflow does no TTS** (uses the original's built-in audio), so **no need to check voice clone status** — `voice=mine` is irrelevant to this workflow.

⚠️ **Asset-size note**: original ≥ 100MB (nearly every 1080p+ video) → must **transcode a proxy** (720p H.264 < 100MB) to pass zip / MCP upload. See [HARD BAN #11 exception clause](../SKILL.md) + memory `large-media-upload-constraint`.

### 1 · Prepare work directory + analyze audio
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
# put the video in as an asset under <work>/, e.g. clip.mp4
python3 scripts/transcribe.py --audio <clip.mp4> --out <work>/clip.mp4.whisper.json
```
Transcribe the **video's built-in audio** (for locating + captions + segmentation), fix transcription typos ([`../reference/typo-fixes.md`](../reference/typo-fixes.md)). **No rewrite, no re-synthesis** — audio stays as-is.

### 2 · Split into beats by audio
Use [`scripts/find_beats.py`](../scripts/find_beats.py) to search anchor sentences in the transcript, getting each segment's `[start, end]`. Between adjacent anchor sentences = one view. Output `<work>/beat_plan.md`.

### 3 · Ask the user: overlay effects or intercut edit?
This is the key fork of the video flow; ask via AskUserQuestion (or judge from clues):

| Mode | What the user wants | How to arrange |
|---|---|---|
| **A · Overlay** | "Add a caption bar / data card / arrow **on top of** my video" | Per view `\video{clip}` + `\remotionFile[over=true]{}`, **semi-transparent frosted-glass** motion layered over the live-action |
| **B · Intercut** | "**Cut together** my talking-head and the explanatory visuals" | Audio as spine: show talking-head when the face should be on screen, cut to our authored scene when a concept needs visualizing |
| **C · Tella screen-capture + PiP** | Has **two assets** (screen-capture + avatar), wants that smooth "avatar shrinks from fullscreen into the corner, screen-capture takes over" cut | One view, one `\remotionFile{}` scene loads both at once, `interpolate` does the fullscreen↔small-window morph |

---

## Mode A · Overlay effects (frosted-glass overlay)

Two visual layers in one view: **live-action base** (`\video`, carries the original audio = spine) + **transparent motion overlay** (`\remotionFile[over=true]`). Remotion renders the motion as a **transparent alpha asset**, and the **manifest layers** it over the live-action — the engine only produces the asset; all overlay composition lives in VideoTeX/manifest (preview equals export).

```latex
\begin{view}
  \video[start=0, end=8.5]{clip.mp4}                  % live-action base + original audio = spine
  \remotionFile[over=true]{scenes/overlay_01.tsx}      % transparent motion overlay
  % optional: extra voiceover / background music (audio overlay, does not replace original audio)
  % \say[volume=1.2]{supplementary note……}
\end{view}
```

- Template [`../templates/scene_overlay.tsx.tpl`](../templates/scene_overlay.tsx.tpl). **Semi-transparent frosted glass**: fill panels with low opacity (alpha 0.30–0.50) + light stroke + top sheen so the live-action shows through.
- **Mechanism**: `over=true` is just a **render hint** — it tells Remotion to render a transparent webm (alpha). **The engine never touches the live-action**; layering the alpha onto `\video` is the manifest's job. This view's duration is decided by `\video` (its built-in audio) (audio-first); to drop the original audio use `\video[mute=on]`.
- Two iron rules: ① the overlay's root `AbsoluteFill` must never set an opaque `backgroundColor` (it would cover the live-action); ② only give the graphic elements themselves a background.
- Audio overlay: original live-action audio + `\say` + `\bgm` mix together (use each one's `volume=` to set the ratio). `over=true` works for both `\remotion` and `\remotionFile`.

## Mode B · Intercut (audio-driven)

The user's talking-head audio is the **continuous spine**; the visuals cut between "face on screen" and "our assets". Which beat shows the face and which beat shows assets is decided by the audio content (hits a concept that needs visualizing → cut to assets; personal opinion / cinematically strong passage → show the face).

- **Face beat**: drop the live-action clip directly (with original audio):
  ```latex
  \begin{view}
    \video[start=0, end=8.5]{clip.mp4}     % talking-head, original audio follows
  \end{view}
  ```
- **Asset beat**: cut to a scene we authored, **with this segment's original audio underneath** (cut that segment from the same video audio):
  ```latex
  \begin{view}
    \audio[start=8.5, end=15.2]{clip.mp4}  % the user's voice for this segment
    \htmlFile{scenes/scene_concept.html}    % the explanatory visual we authored
  \end{view}
  ```
- When the two kinds of beats alternate to fill the whole audio timeline, `start/end` butt end-to-end (no gaps, no overlaps). Asset-beat visuals are audio-first (follow the `\audio` duration, see [`../reference/audio-first.md`](../reference/audio-first.md)).
- Picking engines / hand-writing scenes is the same as [`text-to-lecture.md`](text-to-lecture.md) steps 3–4, with the unified palette [`../reference/palette.md`](../reference/palette.md).

## Mode C · Tella screen-capture + avatar PiP (fullscreen↔small-window morph)

The user has **two assets** (one screen-capture + one talking-into-camera), and wants that smooth
Tella effect: opens with the avatar filling the screen for a self-intro, then **shrinks into the corner as a small window** while the screen-capture takes over.

Key insight: **this "shrink" is a morph within one beat and must live in the same `view`**. One
`\remotionFile{}` scene loads both videos at once, using `interpolate` to interpolate the avatar's scale /
position / corner-radius over time. This is **not** an `over=` overlay (an overlay layer is an independent transparent render the engine can't touch) —
in this beat the scene itself composites the two clips. The manifest only cuts / fades at **view boundaries**,
so a morph can't be done across two views.

```latex
\begin{view}
  \remotionFile{scenes/screencast_01.tsx}   % loads screen.mp4 + webcam.mp4 at the same time
  \audio{webcam.mp4}                          % voice = spine + decides this view's duration
\end{view}
```

- Template [`../templates/scene_screencast_pip.tsx.tpl`](../templates/scene_screencast_pip.tsx.tpl). Both loaded directly via `staticFile()`, both `muted` in the scene (the scene only shows visuals, carries no audio).
- **Audio**: the voice comes from `\audio{webcam.mp4}` (the same avatar file as the audio-track spine); it also sets this view's duration, and the compiler overrides `DURATION_FRAMES` from it, so morph timing points expressed as fractions of `dur` in the template auto-align. If you also want the screen-capture's system audio (click sounds / demo sounds), add another `\audio[...]{screen.mp4}` (overlay mix, does not replace).
- Template parameters: `PIP_SCALE` (small-window ratio 0.22–0.30), `PIP_CORNER` (br/bl/tr/tl), `MORPH_START/END` (0..1, which part of the clip the shrink happens in). To reverse it (zoom back to fullscreen face at the end) / add a title bar / punch-in zoom the screen-capture, search the `VARIANT` comments in the template.

---

## README + delivery
The video clip goes into the included items. Then → **delivery: see [`_delivery.md`](_delivery.md)**.
