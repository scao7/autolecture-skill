# Delivery (the last step of every workflow)

**First determine the run mode → decide which path** (per [`reference/runtime-modes.md`](../reference/runtime-modes.md)):

Check the tool list for the autolecture MCP tools — present = **mcp** (path A), absent = **zip** (path B).

| Mode | Delivery path | Note |
|---|---|---|
| **mcp** (MCP tools present) | **Path A · MCP direct-drive** (preferred) | Claude authors the JSON shots via state ops + writes the per-shot scene code + renders + compiles in the cloud, end-to-end; on failure `render_shot` returns the still to inspect |
| **zip** (no MCP, incl. web client) | **Path B · zip** | Claude produces a project zip; the user drags it to autolecture.ai to upload |

---

## Path A · MCP direct-drive (preferred — when the autolecture MCP tools are in the tool list)

Claude authors the project as JSON shots via the state-op tools (see **AUTHORING
MODEL — v0.13** in SKILL.md) — all in the cloud, end-to-end.

> ⚠️ **Iron rule: incremental persistence — land every finished shot in the cloud immediately, NEVER pile it up for one final write.**
> A long project has a dozen-plus shots; if you hold them all in your head and only persist at the very end,
> then the moment you **hit the tool-use limit** mid-flow, disconnect, or a call fails, **it's all wasted**. Each `upsert_shot`
> is already in the cloud project, valid; to continue you first call `get_state` and see where you got to.

1. **Create + bootstrap the project** — `create_project` to get a project id, then
   `set_project(title, aspect_ratio, style)` (one call) to set the film's
   top-level fields. The cloud now holds a valid (empty-shots) project.

2. **Author shot by shot, incrementally (core loop — repeat per shot)**: each time you finish **one** shot, on the spot:
   a. If this shot uses uploaded assets, `add_asset` first.
   b. `upsert_shot(id, duration, description, engine, src, say_text)` — insert the
      shot (a base layer of `engine` + a code file `src`, plus the `say_text`
      narration). Then `write_file(src, …)` the scene code
      (`scenes/<id>.{py,tsx,html,svg}`). (For `engine='image'` omit `src` — the
      engine AI-generates from `description`.)
   c. (Recommended) `render_shot(id, storyboard=true)` — render just this shot's
      still on the spot, **catch errors on the spot** rather than piling up.
   → Each shot lands the moment it's authored. **Any interruption mid-flow loses nothing already written.**

3. **All shots authored → finalize + compile** — `set_project(phase='final')` →
   `compile` (whole project) → `get_status` poll to completion → `get_output` for
   the mp4 + Studio URL. (Shots already rendered in 2c hit cache, fast.)

4. **On failure, inspect and fix yourself** — `get_status` gives structured errors
   (which shot / category / offending source); `get_state` shows the current shots.
   Fix the scene code with `write_file(src, …)`, then `render_shot(id,
   storyboard=true)` — the returned still confirms the fix; re-`compile` (the rest
   hits cache). **At most 3 self-fixes per shot**; if that fails, escalate to the
   user with evidence (offending fragment + the shot's still + Studio URL).

5. **Deliver** — return the Studio URL + a one-line "how to use"; the user can keep editing in Studio / click ▶ Recompile.

> Tool-name prefixes vary by client (e.g. `autolecture:compile` / `mcp__autolecture__compile`). Parameter schemas follow the tool definitions you actually see — if unsure, first `list_projects` / `whoami` to probe.
> **Continuation**: after a conversation is interrupted and reconnected, first `get_state` to see which shots already exist, then keep `upsert_shot`-ing the missing ones; don't rebuild from scratch.

---

## Path B · Package zip (when no MCP / claude.ai web client)

```bash
python3 scripts/package_zip.py --work <work> --out <work>/autolecture_demo.zip
```

[`scripts/package_zip.py`](../scripts/package_zip.py) will:
- Pack all of `<work>` into one zip (`main.tex` + `scenes/` + assets)
- Verify every key file is present (every file referenced by `\manimFile` / `\htmlFile` / `\remotionFile` / `\imageFile` / `\audio` / `over=` / PDF exists), hard-exit if any is missing
- Output the zip path + file manifest

Reply to the user: zip path + "drag it to <https://autolecture.ai> to upload; it auto-detects main.tex and registers the assets; then edit the code / click ▶ Recompile in Studio". (Website from-zip is verified: auto-adds the `\begin{videotex}` shell, registers assets, `staticFile()` can grab the uploaded PDF / images / video.)

---

Both paths **both** charge through the AutoLecture compile (the skill code is free; compiling from any entry is charged).
Final reply to the user: the deliverable (Studio URL, or zip path) + a short one-line "how to use".
