# VideoTeX DSL cheatsheet (for autolecture-skill)

## Document structure

```latex
\title{<title>}
\aspect{16:9}                 % Aspect ratio. Default short edge 720p
% \aspect{16:9, 1080p}        % Or add resolution: 720p / 1080p / 1440p / 2k / 4k
\style{<visual style description: injected into the LLM visual engine system prompt>}
\voice{<TTS timbre/tone description, optional; if omitted falls back to the \style description>}

\begin{videotex}
  \begin{view}[opts]
    ...layer macros...
  \end{view}

  \fade[duration=0.5]{}   % transition (optional)

  \begin{view}...\end{view}
\end{videotex}
```

## Visual layer macros (one per view)

| Macro | Applies to | Notes |
|---|---|---|
| `\manimFile[retime=true]{path.py}` | Manim Python source | The render entry class is fixed to `LectureScene` (write the animation into this class; the `scene=` selector was removed on 2026-05-23). **`retime=true` is mandatory** (since 2026-05-22, `\manimFile` no longer auto-scales duration by default — only `retime=true` scales `self.play/wait` to the `\say` length; otherwise it renders at source native speed and freezes the last frame). |
| `\htmlFile{path.html}` | HTML source | Playwright live screen recording; self-contained inline CSS |
| `\remotionFile{path.tsx}` | Remotion React source | Must export `Comp` / `FPS` / `WIDTH` / `HEIGHT` / `DURATION_FRAMES` |
| `\imageFile{path.png}` | Uploaded image | opts: `fit / position / bg / lead` |
| `\image[engine=gemini]{prompt}` | AI image generation | Gemini, single generation, same prompt+style hits cache |
| `\video[start=,end=]{path.mp4}` | Uploaded video clip | `mute / loop / fit` |

**Banned**: `\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}` — LLM-generated code, unstable.

## Audio layer

| Macro | Applies to |
|---|---|
| `\say{text}` | TTS synthesis. opts: `voice=mine` / `speaker` / `speed` / `model` / `burn` / `as` |
| `\audio[start=N, end=N]{path.m4a}` | Clip original audio (no TTS, no auto captions) |

## Caption layer

| Macro | Applies to |
|---|---|
| `\caption{...}` | Burn captions only, **never drives TTS**. opts: `position=top|bottom|hidden` / `align=auto|on|off`. Use it to caption recordings/live footage (pair with `\audio`: original audio plays + captions burned in). Replaces the removed `\text` and the deprecated `\say[mute=true]`. |

Default behavior when omitted: `\say` present → captions use the `\say` text (needs `burn=on`); `\audio` used alone → no captions (add `\caption` for captions).

## view-level opts

Only 2: `duration` (seconds) + `title` (display name in the editor).

## preamble-only macros

`\title` / `\aspect` / `\style` (visual) / `\voice` (TTS timbre/tone, decoupled from `\style`) / `\subtitle[size=, color=, position=top|bottom, punct=keep]{on|off|auto}` (style only affects display/burn-in, **does not trigger re-render**) / `\bgm[volume=,loop=]{path}` / `\character[voice=,speed=]{name}` / `\cliplibrary{clips/day1}` (declares a clip asset library, repeatable, BibTeX style).

### clip library (BibTeX for clip assets)

Clip trims are written **non-destructively** and centrally in the clip document; main.tex references them with `@name`:

```latex
% main.tex preamble (if not declared, defaults to looking for clip.tex)
\cliplibrary{clips/day1}        % omit .tex and it's auto-completed, same as \bibliography

% clips/day1.tex —— only \begin{segment}{name} is allowed at top level
\begin{segment}{intro_hook}
\video[start=2, end=8]{takes/a.mp4}
\caption{opening caption}       % optional: a caption that travels with the segment
\end{segment}

% main.tex body —— segment ≈ @entry, \video{@name} ≈ \cite
\begin{view}\video{@intro_hook}\end{view}
```

Caption mechanism (live footage defaults to **asset-level transcripts**): give an asset `assets/{media}.transcript.txt` (a full corrected transcript) + the existing `{media}.whisper.json` (the `transcribe` output), and **every view referencing that asset auto-derives captions for its own [start,end] window** — zero caption content in the tex, captions follow as you drag trim points, edit the transcript and it re-aligns instantly (no re-render). `\caption{}` can still serve as a view-level explicit override: just write **one continuous block of text** — line-level splitting and timecodes are derived (after aligning to speech, auto-split by punctuation / roughly every 18 chars into full-screen sentences). **Do not** hand-write timing. The only split override: write `\\` in the body to force a sentence break there. The whole video can export SRT (`GET /projects/{id}/captions.srt`).

Rules: a declared library is **strict** (missing file / duplicate segment name across libraries → error); views / effects / `\say` are forbidden in the clip document; for a quick one-off trim, just write `\video[start=, end=]{src}` inline in the view (anonymous inline trim) — no need to enter it into the library. **Agent rough-cut = write the clip library; human fine-tune = drag trim points / edit captions in Studio** — both edit the same .tex.

### `\aspect{}` syntax (important)

- `\aspect{16:9}` — aspect only, default short edge **720p** (→ 1280×720).
- `\aspect{16:9, 1080p}` — aspect + resolution. Valid RES values: `720p` / `1080p` / `1440p` / `2k` (= 1440p) / `4k` (= 2160p).
- Resolution takes effect at **compile time**: each view block renders natively to the target size (manim/html/remotion all output frames at this canvas). The export button only decides whether to burn the watermark, no longer does resolution switching.
- Want 4K? Write `\aspect{16:9, 4k}` then re-compile all (the cache misses because the canvas changed → re-render).

## body elements

`\begin{view}...\end{view}` / `\begin{segment}[title=,continuous=]...\end{segment}` / `\fade[duration=,color=]{}` / `\input{path.tex}`.

## A minimal example (hand-written source mode)

```latex
\title{Hello AutoLecture}
\aspect{16:9}
\style{深色背景 #0d1117, Inter + PingFang SC, 简洁动画}

\begin{videotex}

\begin{view}[title=Hook]
  \say{今天我们来看看世界上最小的世界模型。}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \say{15M 参数,2 个损失函数,48 倍加速。}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```

## A polished-mode example (clip original audio)

```latex
\title{论文解读}
\aspect{16:9}
\style{学术深度解读, 深色背景, 高对比白字, Inter + PingFang SC}

\begin{videotex}

\begin{view}[title=Hook]
  \audio[start=0.00, end=32.34]{podcast.m4a}
  \remotionFile{scenes/scene_01_hook.tsx}
\end{view}

\begin{view}[title=Card]
  \audio[start=32.34, end=66.44]{podcast.m4a}
  \htmlFile{scenes/scene_02_card.html}
\end{view}

\end{videotex}
```
