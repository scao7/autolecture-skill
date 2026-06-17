# Compile / Preview / Frame-grab — gotcha cheat sheet

Don't do full compiles during development. This page nails down four gotchas: single-view preview, fetch_frame decoding, compile cost, and cache invalidation.
Cost of ignoring it: burn a pile of credits, fail to grab frames, re-render the whole video just to change resolution.

> Applies to: **mcp** mode (has `get_snapshot` / `compile` / `fetch_frame` tools). zip mode lacks these tools — skip.

---

## 1. Single-view preview — no native entry point, override main.tex

AutoLecture has **no** "compile only view N" entry point. To preview a single view during development, the only way is to
**temporarily override main.tex with a document containing just that one view**, compile, inspect, then restore.

⚠️ Child tex (the fragments pulled in via `\input{}`) **must be body fragments**:
- No preamble (`\title` / `\aspect` / `\style` / `\voice`).
- No `\begin{videotex}` / `\end{videotex}`.
- Just a bare `\begin{view}...\end{view}` inside.

So you can't compile a child tex directly — you have to wrap it in a full document. Steps:

1. **Back up** the real main.tex first (`get_snapshot` to save its content, or keep a local copy).
2. **Override main.tex** with a single-view document (copy the preamble from the real video; body keeps only the target view):
   ```latex
   \title{preview}
   \aspect{16:9}                 % match the real video, don't change resolution here (see section 4)
   \style{...same as the real video...}
   \voice{...same as the real video...}

   \begin{videotex}
   \begin{view}[title=scene_07]
     \say{narration for this view, copied verbatim}
     \htmlFile{scenes/hd_07.html}
   \end{view}
   \end{videotex}
   ```
   Write it back to main.tex with `write_file` / `edit_file`.
3. `compile` → `get_status` until done → `fetch_frame` to inspect frames (see section 2).
4. **Restore main.tex immediately after** to the backed-up full-video version. Don't leave the single-view document in the cloud as the real video
   (resume will mistake it for the truth — see SKILL.md "the truth lives in the cloud" rule).

> When iterating on multiple views: per view, override → compile → frame-grab → restore, loop. Saves 90%+ credits vs a full compile.

---

## 2. fetch_frame — three counterintuitive points, follow them

`fetch_frame` grabs a PNG at a given moment of a given view. Three gotchas each cause empty grabs:

### (a) scene_id takes the `content_hash`, not the view's title

`fetch_frame`'s scene_id parameter must be **that block's `content_hash`**,
taken from `get_snapshot`'s `blocks[].content_hash`. **Not** the view's `title`,
**not** the index, **not** the filename.

```python
snap = get_snapshot(project_id)        # MCP tool
block = snap["blocks"][6]              # view 7 (0-based)
scene_id = block["content_hash"]       # ← pass this
# fetch_frame(scene_id=scene_id, t=1.5)
```

### (b) The return is a huge JSON, written out to `/mnt/user-data/tool_results/...json`

The PNG is base64 stuffed inside the JSON, which is large, so the tool result isn't inlined back into the conversation but is
**written out** to `/mnt/user-data/tool_results/<some-hash>.json`. What you get is this **file path**.

### (c) The base64 lives in `inner["image"]["data"]`, you decode it to .png yourself

The written-out JSON is doubly nested. The outer level is a list; element 0's `text` field
is a **JSON string** that needs another `json.loads` to reach `inner`, where the PNG base64 lives at
`inner["image"]["data"]`. Decode:

```python
import json, base64, pathlib

results_json = "/mnt/user-data/tool_results/<that file>.json"   # path returned by fetch_frame
outer = json.loads(pathlib.Path(results_json).read_text())
inner = json.loads(outer[0]["text"])          # note: loads one more level
png_b64 = inner["image"]["data"]              # base64 string
pathlib.Path("/tmp/frame.png").write_bytes(base64.b64decode(png_b64))
# then Read /tmp/frame.png to view it
```

Once decoded, Read that .png to eyeball how this view rendered.

---

## 3. Compile cost magnitude — must warn before compiling

A full compile is expensive and slow: **per view it synthesizes Chinese TTS + records 1080p in real time**, cost scaling with narration length and
resolution. Reference magnitudes:

| Scale | First full-compile cost |
|---|---|
| 17 views (TTS + 1080p recording each) | ≈ **375 credits** |

**Single view** ≈ full / view-count, much smaller in magnitude → so iterate view-by-view during development.

Rules:
1. **During development, only use single-view preview** (section 1) to iterate on visuals / timing.
2. **Do a full compile only once at the end** to produce the render.
3. **Before each full compile, warn the user about the cost magnitude** (estimate by views × narration length × resolution),
   don't blindly burn credits.

---

## 4. Cache invalidates with the canvas — don't change resolution mid-iteration

`\aspect{}`'s resolution **takes effect per-block at compile time**: each view block natively renders to the target size
(manim / html / remotion all emit frames at this canvas).

So **changing resolution = changing the canvas = every block's content_hash changes = full cache miss = re-render the whole video**.
There's no such thing as "just switch the resolution and reuse old frames."

Rules:
- Fix the resolution (the `1080p` in `\aspect{16:9, 1080p}`) **from the start**, don't touch it during iteration.
- Keep the `\aspect` in single-view preview (section 1) consistent with the real video too — changing resolution in the preview document
  both pollutes the cache and makes the preview inconsistent with the finished video.
- If you really want 4K, lock the content first, then bump `\aspect{16:9, 4k}` and do **that one** full compile,
  accepting the cost of re-rendering the whole video.
