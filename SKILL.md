---
name: autolecture-skill
version: 0.11.0
description: Turn the user's material end-to-end into a project that compiles to a finished video in AutoLecture (https://autolecture.ai). At the entry, first set the runtime mode, then ask **freestyle or find a dedicated template in the marketplace** (each genre in the marketplace is a server-delivered authoring card any MCP-connected agent can use); freestyle then routes by primary input type to the matching workflow: plain text/script→generate an explainer; audio/podcast→transcribe + match visuals; PDF paper→explain (extract figures) or showcase the original (react-pdf real pages + zoom + located highlight, à la pdf2video); live-action video→overlay transparent effects (over=) or screencast+avatar Tella-style picture-in-picture (recording yields screen/camera raw tracks, PiP arranged by template, tunable later); reference video→visual replication (extract frames, read the motion, write scenes to match). All visuals are hand-written \manimFile/\htmlFile/\remotionFile source (no LLM prompts); AI is used only for \image[engine=gemini]{} image generation. On start, check whether the autolecture MCP tools are present (the mcp.autolecture.ai/mcp connector): if so, mcp mode builds the project + compiles + inspects frames directly in the cloud; if not, ask the user to use MCP or just produce a zip to upload (claude.ai web goes zip). Two delivery paths: with MCP tools, drive cloud compile directly via the connector; otherwise package a zip for the user to upload. Goal: user gives material → run → out.mp4 + Studio URL.
---

# autolecture-skill

Turn the user's material into a project package that compiles to a finished video
the moment they hit ▶ Recompile in AutoLecture. This SKILL.md is the **routing
entry** — first decide which kind of video the user wants, then open the matching
[`workflows/`](workflows/) playbook and execute it.

## Core: everything is audio-driven

Unlike other skills — **an AutoLecture project is ALWAYS audio-driven**: the
narration / voice is the timeline spine of the whole film, and visuals appear only
to follow the audio's pacing and meaning, never the reverse. Whatever the entry:
- **Simple instruction / text** → write a voiceover script and **get the user's
  sign-off** → TTS → match visuals to each segment's timing and meaning.
- **Audio recording** → transcribe + fix typos → decide "keep the original audio
  and just cut" vs "re-synthesize with voice clone" → split visuals by the audio.
- **Video** → **no TTS**: analyze and split by the video's own audio → overlay
  effects or edit-combine.

So step one of every workflow is "fix the audio timeline", and only step two is
"match a visual to each segment".

## When to trigger

The user says "make an autolecture video / demo", "I recorded a voiceover, turn it
into a video", "I have a script / paper / project I want explained", "cut my podcast
and match visuals", "add some motion over my live footage", or just drops in an
audio / text / PDF / video file.

---

## Entry: **set three things up front** (ask once; workflows never re-ask)

### Entry ① · Runtime mode? → check for MCP first (**always, before any workflow**)

**The first thing the skill does on start is check whether you currently have the
autolecture MCP tools** — once the `mcp.autolecture.ai/mcp` connector is attached,
the tool list shows `create_project` / `write_file` / `edit_file` / `add_asset` /
`compile` / `get_status` / `fetch_frame` (the prefix depends on the client, e.g.
`autolecture:compile`). This is a fact Claude can see directly — no script needed.

- **Have the MCP tools** → **mcp mode** (preferred). Claude uses these tools to
  build the project in the cloud, write `main.tex` + scene files, upload assets,
  compile, and pull rendered frames to inspect — end to end, nothing dropped to a
  local zip, and when a compile fails it can `fetch_frame` to debug.
  **On connect, call `server_info` once for version reconciliation**: ① if the
  returned `skill_version_current` is newer than this SKILL.md's header `version`,
  tell the user "the skill has a new version, run `npx skills add
  scao7/autolecture-skill` to update (on claude.ai re-upload the zip)" — then carry
  on, don't block this task; ② if the returned `dsl_spec_sha` doesn't match the local
  `harness/spec/dsl.json`, take the **live spec from `get_dsl_spec`** as truth (the
  bundled dsl.json is just an offline fallback).
  **You can start from a template**: `list_gallery_templates` → pick one →
  `get_template_card(slug)` to read how to fill it → `use_gallery_template(slug)` to
  clone it into a new project and replace placeholders on top — far faster than
  writing from scratch (the templates are all compile-verified real projects).
- **No MCP tools** → ask the user with `AskUserQuestion`, two choices:

  | Option | Which path |
  |---|---|
  | **① Use MCP (recommended)** — Claude builds the project + compiles + inspects in the cloud, hands you a Studio link when done | Guide the connector: in your client (Claude.ai / Cursor / Claude Code) Settings → Connectors → Add → paste `https://mcp.autolecture.ai/mcp` → approve in the browser (OAuth). Once connected, refresh tools / reopen the chat, then start the skill → enter **mcp mode** |
  | **② Give me a zip, I'll upload it myself** — connect nothing; for claude.ai web / users who don't want to authorize | **zip mode**: Claude produces a project zip, you drag it onto [autolecture.ai](https://autolecture.ai) (the web auto-detects main.tex + registers assets) |

With the mode set, **workflows never ask again** — each workflow's step 0 just
branches on `mcp / zip`. For how each action is done in either mode, see
[`reference/runtime-modes.md`](reference/runtime-modes.md).

### Entry ② · Which path? → freestyle / marketplace

With the mode set, ask the user how to start this video (use `AskUserQuestion`, two
choices):

| Option | Which path |
|---|---|
| **① Freestyle** — I'll design the approach from scratch | Go to **Entry ③** and route by primary input type into `workflows/`; **no marketplace dependency**, base features always work |
| **② Find a dedicated template in the marketplace** — pick a verified starting point by genre | Go to [`reference/marketplace.md`](reference/marketplace.md): list genres → pick a template → pull the authoring card → clone the starting project → take over per the card's recipe. **mcp mode only** (zip mode falls back to freestyle) |

- **Unsure / no explicit user ask** → default to **freestyle** (it works
  standalone, most robust).
- If they pick the marketplace, jump to `reference/marketplace.md` and **skip Entry
  ③'s input routing** — the genre card already contains the recipe.
- If they pick freestyle, continue below.

### Entry ③ · (freestyle) What's the primary input type? → pick a workflow

> Only the **freestyle** path runs this step; if they went to the marketplace, work
> from the card and skip this.

**Figure out what primary input the user has** (look at the files they gave + what
they said; if unclear, use AskUserQuestion). Then **read the matching workflow file**
and execute it:

| User's primary input / ask | workflow | one line |
|---|---|---|
| A **reference video** to "make it in this style" (YouTube link / file / project asset) | [`workflows/replicate-style.md`](workflows/replicate-style.md) | extract frames, read the motion → hand-write scenes to replicate the visual language (YouTube only on Claude Code local) |
| Only **text / a one-line instruction / a topic**, no recording | [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) | **write a voiceover script and get sign-off** → TTS → match visuals to the voiceover |
| An **audio recording / podcast** (mp3/wav/m4a) | [`workflows/audio-upload.md`](workflows/audio-upload.md) | transcribe + fix typos → keep original audio and cut, or re-synthesize with voice clone |
| A **PDF paper** | [`workflows/pdf-paper.md`](workflows/pdf-paper.md) | A: explain the content (extract figures), or B: showcase the original (real pages + zoom + located highlight) |
| A **live-action video** / **screencast + avatar** | [`workflows/video.md`](workflows/video.md) | no TTS; split by the original audio → overlay effects (frosted glass) / edit-combine / Tella screencast PiP |

To ask, use AskUserQuestion with these five categories: "① I'll give text / a topic
② I recorded audio / a podcast ③ I have a PDF paper ④ I have live-action video ⑤ I
have a reference video to follow".

**Stackable**: the primary input picks the main workflow, other material is
supporting —
- audio / text + PDF figure / GitHub repo / local image → match into visuals per
  [`reference/figure-matching.md`](reference/figure-matching.md) inside the main workflow.
- audio / text + you want to **showcase** a PDF original on screen → stack the Flow B
  shots from [`workflows/pdf-paper.md`](workflows/pdf-paper.md).
- anything + live-action clips → those views use the `over=` overlay / edit-combine
  from [`workflows/video.md`](workflows/video.md).

### Entry ④ · then proceed as usual

With mode + primary input set, it's the normal video flow — the workflow confirms
with the user in order: **what to make** (topic / scope), **the material on hand**
(primary input + supporting figures / repo / footage), **the visual style they want**
(pick one palette: editorial dark or AutoLecture brand). Then write the voiceover
script → match visuals → deliver.

---

All workflows converge on the same delivery step:
[`workflows/_delivery.md`](workflows/_delivery.md).

---

## HARD BANS (apply to every workflow — never break, ever)

1. **No LLM-prompt macros**: `\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}`
   / `\show{}` are all forbidden. Every visual must be `\manimFile[retime=true]{path.py}`
   / `\htmlFile{path.html}` / `\remotionFile{path.tsx}` / `\imageFile{path.png}` /
   `\image[engine=gemini]{prompt}` (AI image generation is allowed). Reason: LLM-
   generated code is unstable with a high compile-failure rate; hand-written source +
   cache hits = a render in seconds. **`\manimFile` MUST carry `[retime=true]`** (since
   2026-05-22 duration is no longer auto-scaled by default; without it the animation
   won't scale to the audio and the end frame freezes). Use `\caption{}` for subtitles
   (`\text` is retired, `\say[mute]` is deprecated).
2. **No template shortcuts**: each scene's visual **must** be custom-designed to that
   view's content — never fill different text into the same template.
3. **Never skip fixing transcription typos**: Chinese Whisper produces many homophone
   errors; build the [correction map](reference/typo-fixes.md) first before using text
   in a headline. **The audio is untouched** — typos only affect on-screen text.
4. **No silent fallback — quality first**: missing dependency / failed extraction /
   corrupt asset → **error to the user immediately**, never ship a degraded artifact.
   `autolecture_no_silent_fallback` is this skill's lifeline.
5. **Never commit AI-generated samples to `examples/`** (the
   `autolecture_few_shot_human_curated` rule).
6. **No bare image dumps**: a figure extracted from a PDF / repo must be wrapped in at
   least one motion (zoom / crop / annotate / side-by-side / scroll).
7. **Never pull more than 50MB of assets from a repo**: `clone_github_assets.py`
   sparse-checkout pulls images only, skips + warns above the threshold.
8. **Image matches need anchor-phrase evidence**: for every image-to-view mapping,
   write the triggering source sentence from the transcript in `beat_plan.md` (so
   images aren't placed by gut feel).
9. **Never rasterize whole PDF pages by default**: `extract_pdf_figures.py` is
   figures-only by default; use `--with-pages` only when explicitly doing "text
   highlight / formula zoom / full-page scroll".
10. **Audio duration drives the visual**: never reverse-assume the visual's duration
    sets the scene duration. For the three-engine audio-first patterns see
    [`reference/audio-first.md`](reference/audio-first.md) — read before writing any scene.
11. **No pre-cutting / pre-stitching assets — all editing is expressed in .tex**:
    **never** use ffmpeg / editing software outside the project to slice, stitch,
    reorder, time-stretch, or add transitions to raw material before dropping it in.
    The raw material goes in **whole** as an asset; all editing is declared in VideoTeX:
    - **clip selection / cut** → `\video[start=, end=]{raw.mp4}` / `\audio[start=, end=]{raw.mp4}`
      (the compiler takes that time window from the raw file; the raw is untouched).
    - **ordering / stitching** → the view sequence (the manifest concats in order).
    - **transitions** → `\fade` / view boundaries; don't burn transitions into the asset.

    Reason: P1 **LaTeX is the single source of truth**, P2 **no GUI drift** — editing
    is **editable, previewable, non-destructive** characters in the .tex (preview ===
    export). Pre-cut assets = editing decisions burned into the file, bypassing the
    .tex, breaking the whole architecture. (Sole exception: if the raw is truly huge
    you may rough-cut to a working range as the asset, but **the fine cut still lives in
    the .tex**.)
12. **resume = the cloud is the single source of truth**: the **first action** of any
    continue / resume task **must be `get_snapshot`**, taking the cloud's actual files +
    `main.tex`'s view order as truth. A summary / journal / remembered file list is only
    a **lead**; `read_file` each one to verify the real thing; **don't trust "it's all
    written"**. Reason: a compaction summary will name wrong files (abandoned drafts,
    missing views, naming clashes), and taking over on it would edit the wrong set. See
    [`reference/resume-checklist.md`](reference/resume-checklist.md).
13. **Sample first (mandatory)**: for any **multi-view task, do ONE sample end-to-end
    and get sign-off** (build project → write 1 view → compile → `fetch_frame` to check →
    user says "looks good") **before batching** the rest. Reason: a sample rework costs
    1 view, post-batch rework costs N views; the most valuable step.
14. **One naming prefix per project + clean up orphans on replace**: a project uses one
    scene naming prefix (e.g. `hd_*`); **when replacing an old version, `delete_file` /
    `move_file` to archive it** so no mixed-version orphan files linger. `main.tex`'s view
    order (or `MANIFEST.md`) is the **single list of the current official views**. Reason:
    multiple coexisting prefixes = on resume you'd have to guess "which set is official".
15. **`main.tex` skeleton first**: build a **compilable skeleton of ALL views** (each
    view first gets a placeholder `\say` + `\htmlFile`) and commit it immediately, **then
    fill view by view**; keep it compilable / ordered / recoverable throughout. **Put
    `\say` and its visual in the same view** (don't leave narration only in a draft, or
    resume has to re-cut from the original text).
16. **`\manimFile` must carry `[retime=true]`; `\say` ≤400 chars, subtitles off by
    default** (need `burn=on` to burn). Reason (retime): since 2026-05-22 duration is no
    longer auto-scaled; without it the animation won't scale to the audio and the end
    frame freezes. (This echoes ban 1, especially easy to miss on resume / batch.)
17. **No "write everything then compile" — compile each view as you write it**:
    `compile` is incremental (unchanged blocks all hit cache, only the new block renders),
    so write 1 view → `write_file` → `compile(wait_seconds=60)` on the spot → check
    `block_errors` → fix → next view. **Cost is identical to one final compile, but errors
    arrive one at a time.** Batch-writing then compiling = N blocks' errors dumped into the
    chat at once + context already spent on debugging ("conversation too long" kills the
    session outright, and everything written-but-not-compiled is unverified).
    **Context hygiene** alongside: once scene code is in `write_file`, don't restate it in
    the body; edit files with `edit_file`, don't rewrite whole files; use `fetch_frame`
    only to pull 1-2 frames on a compile error or a key-visual check — images eat context.

---

## Two runtime modes ── decide at step 0 of every workflow

The skill supports two user scenarios, by whether Claude currently has the autolecture
MCP tools:

| Mode | Trigger | What it does |
|---|---|---|
| **mcp** (preferred) | the current tool list has the autolecture MCP tools (the `mcp.autolecture.ai/mcp` connector is attached) | Claude uses the MCP tools directly: cloud `create_project`, `write_file`/`edit_file` for tex+scene, `add_asset` to upload, `compile`+`get_status`, `fetch_frame`/`fetch_waveform` to inspect renders, `list_scene_versions`/`pick_scene_version` to roll back to a better past render, `fetch_asset_frame` to view raw-asset frames (replication reference / arrangement checks), `get_captions` for the aligned per-line subtitles (edit `{src}.transcript.txt` for footage, `\caption{}` for overlay scenes — both apply instantly without re-render) — end to end, and when a compile fails it inspects frames to debug |
| **zip** (default fallback) | no MCP, and the user doesn't want to connect (incl. **claude.ai web**) | **produce a zip only** for the user to drag onto [autolecture.ai](https://autolecture.ai); Claude can't query the user's state, so use `AskUserQuestion` or conservative defaults |

**Decide (step 0 of every workflow)**: is there an autolecture MCP tool in the list — yes
= **mcp**, no = **zip**. This is something Claude sees directly; no script, no local files.

Whenever Claude wants to build a project / write a file / compile / query user state /
view a cloud render → branch on mode first: **mcp calls the MCP tools, zip uses the local
fallback + packages a zip** (see [`reference/runtime-modes.md`](reference/runtime-modes.md)).

**Don't assume MCP is present** — many users (especially claude.ai web) can only go zip.

---

## Common building blocks (referenced by all workflows)

- **Two runtime modes cheat-sheet** (how each action is done in mcp / zip) →
  [`reference/runtime-modes.md`](reference/runtime-modes.md)
- **audio-first timing** (three-engine patterns) → [`reference/audio-first.md`](reference/audio-first.md)
- **Engine-selection decision tree** (which content uses Manim / HTML / Remotion /
  `\image`) → [`reference/engine-routing.md`](reference/engine-routing.md)
- **Visual palette + font stack** (consistent across the film) — two sets, **pick one**,
  one project uses only one:
  - [`reference/palette.md`](reference/palette.md) · **editorial dark** (dark ground +
    ocean blue), default. For personal vlog / paper explainer / editorial narratives where
    the content is the star.
  - [`reference/brand-style.md`](reference/brand-style.md) · **AutoLecture brand** (cream +
    navy + tan gradient, same register as the [autolecture.ai](https://autolecture.ai) site
    / Studio / watermark). Use when flying the AutoLecture banner — official demo / teaser /
    tutorial / homepage showcase / feature clip for beta users.
- **VideoTeX syntax cheat-sheet** → [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md)
  (online docs <https://autolecture.ai/docs/dsl>)
- **Supporting-asset anchor matching** (PDF figure / repo screenshot / local image) →
  [`reference/figure-matching.md`](reference/figure-matching.md)
- **Borrowable motion techniques** (skim before writing a new scene) →
  [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md)
- **Delivery** (MCP direct-drive / zip upload) → [`workflows/_delivery.md`](workflows/_delivery.md)

Working directory and output structure (shared by all workflows):
```
<work>/
  main.tex                     # main tex (may be renamed per project)
  <audio>.m4a(.whisper.json)   # audio mode
  paper.pdf                    # PDF mode (as asset)
  clip.mp4                     # live-action mode (as asset)
  scenes/  scene_NN_label.{tsx,html,py}   # hand-written visual source
  figures/                     # extracted figures / AI images / uploaded assets
  beat_plan.md                 # narrative structure + engine routing + anchor evidence
  transcript_corrections.md    # transcription typo-correction map (audio mode)
  README.md                    # "how to use" for the user
```

---

## Reference

### workflows/ (routed by primary input)
- [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) — plain text → generated explainer
- [`workflows/audio-upload.md`](workflows/audio-upload.md) — audio / podcast (rough / polished)
- [`workflows/pdf-paper.md`](workflows/pdf-paper.md) — PDF paper (A explain / B showcase the original)
- [`workflows/video.md`](workflows/video.md) — live-action video (overlay frosted-glass effects / edit-combine, no TTS)
- [`workflows/_delivery.md`](workflows/_delivery.md) — shared delivery (MCP / zip)

### reference/
- [`reference/audio-first.md`](reference/audio-first.md) — three-engine audio-first patterns (the iron law)
- [`reference/engine-routing.md`](reference/engine-routing.md) — engine-selection decision tree
- [`reference/palette.md`](reference/palette.md) — editorial dark palette (#0d1117 / #6ec1e4 / #f4d35e / #ee6c4d / #aab1c0)
- [`reference/brand-style.md`](reference/brand-style.md) — AutoLecture brand-light palette (cream #fefcf6 / navy #234976 / tan #d9b47b gradient, mirrors styles.css)
- [`reference/dsl-cheatsheet.md`](reference/dsl-cheatsheet.md) — VideoTeX syntax cheat-sheet
- [`reference/figure-matching.md`](reference/figure-matching.md) — supporting-asset anchor matching
- [`reference/pdf-showcase.md`](reference/pdf-showcase.md) — the two PDF flows + 4 react-pdf shots
- [`reference/typo-fixes.md`](reference/typo-fixes.md) — common Chinese Whisper typos
- [`reference/borrowed-techniques.md`](reference/borrowed-techniques.md) — 6 borrowable motion techniques
- [`reference/runtime-modes.md`](reference/runtime-modes.md) — mcp / zip cheat-sheet (how each action is done)
- [`reference/marketplace.md`](reference/marketplace.md) — marketplace path (entry ② "go to marketplace"): list genres → pick a template → pull the authoring card → clone the starting project → take over per the card (mcp only; incl. publishing your own template)
- [`reference/layout-spec.md`](reference/layout-spec.md) — the layout limits the harness checks (canvas / safe zone / char caps); read this to know the boundaries
- [`reference/hand-drawn-storybook.md`](reference/hand-drawn-storybook.md) — hand-drawn storybook style (inline-SVG stroke-draw animation + feTurbulence pen jitter + bob/sway micro-motion + brand colors); reusable across a whole fable / story-form explainer
- [`reference/compile-and-preview.md`](reference/compile-and-preview.md) — the counter-intuitive points of the compile / single-view preview / `fetch_frame` trio (cost scale, temporary single-view main.tex override, content_hash as scene_id, base64-to-disk decode, change resolution = full re-render)
- [`reference/resume-checklist.md`](reference/resume-checklist.md) — resume-task checklist: `get_snapshot` to align with cloud truth, `read_file` each to verify, clean up orphans, skeleton first

### templates/
- [`templates/main.tex.tpl`](templates/main.tex.tpl) · [`templates/README.md.tpl`](templates/README.md.tpl)
- [`templates/scene_remotion.tsx.tpl`](templates/scene_remotion.tsx.tpl) · [`templates/scene_html.html.tpl`](templates/scene_html.html.tpl) · [`templates/scene_manim.py.tpl`](templates/scene_manim.py.tpl)
- [`templates/scene_image_zoom.tsx.tpl`](templates/scene_image_zoom.tsx.tpl) — figure Ken Burns
- [`templates/scene_overlay.tsx.tpl`](templates/scene_overlay.tsx.tpl) — live-action transparent overlay (editorial dark · black glass)
- [`templates/scene_brand_lower_third.tsx.tpl`](templates/scene_brand_lower_third.tsx.tpl) — live-action transparent overlay (AutoLecture brand · paper glass + navy→tan gradient)
- [`templates/scene_screencast_pip.tsx.tpl`](templates/scene_screencast_pip.tsx.tpl) — Tella screencast + avatar fullscreen↔inset morph
- PDF real-page shots (Flow B): [`scene_pdf_overview`](templates/scene_pdf_overview.tsx.tpl) · [`scene_pdf_switch`](templates/scene_pdf_switch.tsx.tpl) · [`scene_pdf_focus`](templates/scene_pdf_focus.tsx.tpl) · [`scene_pdf_highlight`](templates/scene_pdf_highlight.tsx.tpl)

### scripts/
- [`scripts/transcribe.py`](scripts/transcribe.py) — Whisper word-level transcription
- [`scripts/find_beats.py`](scripts/find_beats.py) — anchor-phrase timestamp location
- [`scripts/extract_pdf_figures.py`](scripts/extract_pdf_figures.py) — PDF figure extraction (figures-only by default)
- [`scripts/clone_github_assets.py`](scripts/clone_github_assets.py) — repo image sparse-clone
- [`scripts/package_zip.py`](scripts/package_zip.py) — zip mode: validate + package a zip (mcp mode uses the MCP tools to write files + compile directly, no script)

### Key lessons (from demos actually run)
1. **Don't take a 70s+ single Manim scene for granted** — 1000+ frames + 40 dots + many
   FadeIns blow past the 300s render timeout; the same visual in Remotion DOM (CSS particles
   + transform) renders in <10s.
2. **Fixing transcription typos matters a lot** — using "高斯" misheard as "高撕", or "正则项"
   as "政策画像", verbatim turns a headline into garbage.
3. **Each scene independently designed ≠ inconsistent** — a unified palette + fonts + animation
   grammar (fade-up / pop / strike) gives consistency.
4. **HTML is the default first choice** — fast, stable, flexible; use Manim only when math /
   geometric precision truly matters; Remotion suits big numbers / timelines.
5. **`\imageFile` ≠ `\image`** — the former is an uploaded asset, the latter is AI image
   generation; usable together (fixed background `\imageFile`, special illustration `\image`).

### Upstream
- Main project <https://github.com/scao7/autolecture> · Remote MCP <https://mcp.autolecture.ai/mcp> · DSL docs <https://autolecture.ai/docs/dsl>
</content>
