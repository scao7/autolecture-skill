# Layout & Limit Spec — Claude-readable mirror

> **This file is the human-readable view of [`harness/spec/layout.yml`](../harness/spec/layout.yml).** Both this doc and the harness code load the same numbers from that yaml — when the value here disagrees with what you read here vs what the harness enforces, the YAML is truth (and one of these is stale; fix it by re-reading the yaml).
>
> Read this BEFORE writing scenes / `\say{}` / `\caption{}`. The harness will reject violations at delivery time.

## Why this exists

The skill's prose rules in [`SKILL.md`](../SKILL.md) and templates are advisory. The harness reads the numbers below and **mechanically rejects** projects that violate them. So Claude (you) — when generating a project — should write code that stays inside these limits from the start. Otherwise the harness rejects → you fix → re-check → eventually pass, burning extra turns.

---

## Canvas (`\aspect{}` → pixel dimensions)

The backend compiles every view block at the **canvas** picked by `\aspect{}`. The body grammar is:

```
\aspect{RATIO}            % short side = 720p (legacy default)
\aspect{RATIO, RES}       % short side = RES — 720p / 1080p / 1440p / 2k / 4k
```

So `\aspect{16:9}` → 1280×720, but `\aspect{16:9, 1080p}` → 1920×1080, and `\aspect{9:16, 4k}` → 2160×3840. **Every CSS / Remotion / Manim coordinate you write must stay inside the matching canvas.** No `top: 900` on a 720-tall canvas.

Below table assumes the **default short side (720p)**. For non-default resolutions multiply both axes by `RES / 720`.

| `\aspect{}` | Canvas at 720p (w × h) | When to use |
|---|---|---|
| `16:9`  | 1280 × 720  | Default — landscape, YouTube/B站 |
| `9:16`  | 720 × 1280  | Vertical — Reels / TikTok / 抖音 |
| `1:1`   | 720 × 720   | Square — IG feed |
| `4:3`   | 960 × 720   | Legacy slide format |
| `3:4`   | 720 × 960   | Vertical-ish, older social |
| `4:5`   | 720 × 900   | Instagram portrait |
| `21:9`  | 1680 × 720  | Cinematic wide |

**Resolution kicks in at compile time, not export.** Export just serves the file (optionally burning the watermark) — no scaling pass. So if the user asks for 4K, you write `\aspect{16:9, 4k}` and re-compile, not flip an export option.

## Safe zones (fraction of canvas height)

Don't paint important content into the bands the compositor reserves:

- **Top 8%** — used by some templates for kicker / mini-headline. Avoid putting unrelated text here.
- **Bottom 13%** — captions burn here. The brand watermark sits in the bottom-right corner of this band.
- **Middle 79%** (y from 8% to 87%) — where your main scene content should live.

For 9:16 (720 × 1280): top reserved ≤ y=102, bottom reserved ≥ y=1113. Main content goes y ∈ [102, 1113].

## `\say{body}` length (DashScope CosyVoice limit)

DashScope CosyVoice-v3-flash's WebSocket synth rejects requests above roughly 600 chars. The skill enforces:

| Threshold | Behavior |
|---|---|
| `say.max_chars = 600`  | HARD fail. Split into multiple `\say{}` with matching `\audio[start,end]` windows. |
| `say.warn_chars = 400` | Warning — still passes, but split for safety. |

If you're writing narration that exceeds 400 chars, break it at a sentence boundary (。/?/!) into multiple shorter `\say`. The `split_long_say` fixer can do this mechanically (`python -m harness.fix <work> --only split_long_say --apply`).

## `\caption{}` density

If a caption packs too much text into too little audio, Whisper word-alignment can't roll it; the whole block dumps on screen at once.

| Threshold | Behavior |
|---|---|
| `caption.max_chars_per_sec = 4`  | HARD fail (for views with derivable duration). |
| `caption.warn_chars_per_sec = 3` | Warning. |

Per-view rule: if `len(caption) / view_duration_sec > 4`, split into more views with matching `\audio` windows so each caption fits.

Views with TTS-only audio (no `\audio[start,end]`) — duration set by TTS output at render time — are **skipped** by this check (we can't pre-compute duration).

## `\manimFile` MUST carry `[retime=true]` (HARD BAN #1)

Since 2026-05-22, `\manimFile{}` default does NOT scale internal animation time to the audio — the source `.py` renders at its natural speed and the compositor hold/trim-fits. This contradicts the skill's audio-first principle. **Every `\manimFile` you write must include `[retime=true]`.**

```latex
\manimFile[retime=true]{scenes/scene_01.py}    # ✓
\manimFile{scenes/scene_01.py}                  # ✗ harness fails
```

## Forbidden macros (HARD BAN #1)

Backend syntax allows LLM-prompt forms (`\manim{prompt}` / `\html{prompt}` / `\remotion{prompt}` / `\show{}`) — the skill **bans them**. Always write the `*File{path}` variant with hand-written source.

```latex
\manim{a spinning circle}                       # ✗ banned
\manimFile[retime=true]{scenes/circle.py}       # ✓
```

The one prompt-form allowed: `\image[engine=gemini]{prompt}` for AI raster image gen.

## Retired macros (do NOT write these)

| Retired | Use instead | Since |
|---|---|---|
| `\text{...}` | `\caption{...}` | 2026-05-21 |
| `\say[mute=true]{...}` | `\caption{...}` (when you want subtitle without TTS) | 2026-05-22 |

## Voice clone consistency

If the authenticated user has a registered voice sample (`/me/voice-sample`), every `\say{}` in the project should carry `[voice=mine]`. Mixed projects (some `voice=mine`, some not) are flagged by the harness — usually a typo.

```latex
\say[voice=mine, burn=on]{...}                  # ✓ when user has sample
```

When auth is unavailable (no env var, no cache), the harness degrades to a consistency-only check: if ANY `\say` has `voice=mine`, ALL should. No proactive check possible offline.

## Pre-cut footage forbidden (HARD BAN #11)

Don't `ffmpeg` cut/concat raw footage and dump segments into the work dir. Use `\video[start=, end=]{original.mp4}` to select segments — the compiler reads windows from the original.

Filenames matching these patterns trigger the `precut_check` (planned, not yet in MVP):

- `*_cut.mp4`
- `*_concat.mp4`
- `trimmed_*.mp4`
- `*_clipped.{mp4,m4a,wav}`

## Visual verification is server-side (no local render checks)

The old L3 Playwright render probes (`html_overflow_render` /
`html_text_overlap`) were removed 2026-06-09. To verify layout, render
on the server and LOOK at it:

1. `compile` (or `render_scene` for one scene)
2. `fetch_frame(project_id, scene_id, t)` → a PNG of the actual rendered
   frame — check for clipped text, overflow past the safe zone, collisions
3. Fix the scene file via `edit_file`, `render_scene` again

This is both more accurate (it's the real renderer, not a local Chromium
approximation) and the only path that works in every environment.
## How to invoke the harness yourself

```bash
# Pre-flight check — runs at the end of every workflow before delivery
python -m harness.check /tmp/your_work_dir

# Auto-fix the things that can be auto-fixed (\say splitting, voice=mine adding)
python -m harness.fix /tmp/your_work_dir --auto --apply

# Run a single check
python -m harness.check /tmp/your_work_dir --only tts_length

# Get JSON output for further processing
python -m harness.check /tmp/your_work_dir --json
```

`scripts/package_zip.py` calls this automatically — failing the check refuses to zip. In mcp mode, run the same harness check, then push to the cloud with the MCP tools `write_file` + `compile`.

## Full backend syntax surface

The full list of macros + opts that the AutoLecture backend accepts is in [`harness/spec/dsl.json`](../harness/spec/dsl.json). Regenerate from `backend/lecturetex/spec.py` via `scripts/regen_dsl_spec.py` (planned, not in MVP).
