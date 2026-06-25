# Render / preview / compile — gotcha cheat sheet (v0.13, JSON-canonical)

Don't do full compiles during development. Preview one shot at a time, then do a
single full compile at the end. Cost of ignoring it: burn a pile of credits.

> Applies to: **mcp** mode (has `render_shot` / `compile` / `get_state`). zip mode lacks these — skip.

---

## 1. Per-shot preview — `render_shot`, no override dance

There is a first-class single-shot entry point now: **`render_shot(shot_id,
storyboard=true)`** renders just that shot's cheap still and folds the artifact
into the shot's render state. No "temporarily override the active root and
restore" — that whole VideoTeX ritual is gone.

```
upsert_shot(id="s7", duration=4, description="…", engine="manim", src="scenes/s7.py")
write_file("scenes/s7.py", "<the scene code>")
render_shot(shot_id="s7", storyboard=true)     # renders the still on the spot
get_state()                                     # shots[].render.{status, still, mp4}
```

Iterate per shot: `upsert_shot` → `write_file` the code → `render_shot` →
read back with `get_state`. Saves 90%+ credits vs a full compile.

## 2. Inspect the result — read it from the state, no base64 decoding

`render_shot` folds the artifact path into the shot's `render` block, so you read
it back from `get_state()` → `shots[].render` → `still` (the storyboard PNG url)
or `mp4` (the clip), plus `status` (`ready` / `failed` / `rendering`) and
`stale`. No `fetch_frame`, no `content_hash`, no double-nested JSON / base64
decode — that's all retired. On `failed`, `get_status` carries the structured
compile error (which shot / category / offending source); fix the code with
`write_file` and `render_shot` again.

## 3. Full-compile cost — warn before compiling

A full `compile` is expensive and slow: per shot it synthesizes TTS + records
1080p in real time, cost scaling with narration length × resolution. A 17-shot
film ≈ a few hundred credits on the first full compile; a single shot ≈ that /
shot-count. So:
1. **During development, only `render_shot`** to iterate on visuals / timing.
2. **Full `compile` only once at the end** (after `set_project(phase='final')`).
3. **Before the full compile, warn the user about the cost magnitude** (shots ×
   narration length × resolution) — don't blindly burn credits.

## 4. Cache invalidates with the canvas — don't change resolution mid-iteration

`aspect` resolution takes effect per-shot at render time (manim/html/remotion
emit frames at this canvas), and the content hash mixes in project `style` +
`aspect` — so **changing resolution or style busts every shot's cache = full
re-render**. Fix `aspect_ratio` + `resolution` (and `style`) **from the start**
via `set_project`; if you really want 4K, lock the content first, then bump it
and accept the one full re-render.
