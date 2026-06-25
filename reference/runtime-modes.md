# Two Runtime Modes — Claude Cheat Sheet

Every workflow must **branch explicitly**. This page lists, for each action, what to do under **mcp** (MCP tools available) vs **zip** (default / web).

> **Decision:** check whether the autolecture MCP tools are in Claude's current tool list (`create_project` / `set_project` / `upsert_shot` / `write_file` / `render_shot` / `compile`…).
> - **Present** → `mcp` mode (drive everything with the tools).
> - **Absent** → `zip` mode (produce a zip for the user to upload).
>
> This is a fact Claude can see directly — **don't run scripts, don't read local files, don't check auth**. When MCP tools are absent and you want to guide the user toward the connector, see SKILL.md entry ①.

---

## How each action works in the two modes

| Info/action | MCP (MCP tools available) | ZIP (none, incl. web) |
|---|---|---|
| **Create project / author shots / upload assets / render / get mp4** | MCP state ops end-to-end: `create_project` → `set_project` + `upsert_shot` per shot (+ `write_file` the scene code) → `add_asset` → `render_shot` per shot / `compile`+`get_status` → `get_output` | **Package a zip** for the user to drag onto [autolecture.ai](https://autolecture.ai) |
| **Render fails, Claude self-fixes once** | `get_status` structured error / `get_state` to see the shot → fix the scene code with `write_file` → `render_shot(id, storyboard=true)` to inspect → re-`compile` (the rest hit cache) | **Not possible** — user sees the error on the web; the skill ends with a hint on how to debug |
| **See how a shot actually renders** | `render_shot(id, storyboard=true)` then read `get_state()` → `shots[].render.still` | **Not possible** — local render as a substitute (L3 harness renders `\htmlFile{}`) |
| **Incremental render (only the changed shot)** | `render_shot(id)` / `compile` (unchanged shots hit cache) | **Not possible** — re-zip every time |
| **voice clone registration / ✦ balance / quota** | use info from `whoami`; if unavailable, ask the user (same as zip) | `AskUserQuestion` or a conservative default; README tells the user to self-check on the web |
| **Pre-upload cost estimate** | usually no dry-run tool → skip; README has the estimate | skip; README has the estimate |
| **harness check / L3 render** (local static analysis + Chromium) | run (mode-independent) | run |
| **harness `voice_clone_consistency`** | verify with `whoami` etc. if available; otherwise degrade to consistency-only | consistency-only: some `\say` have `voice=mine` and some don't → warning |

---

## Concise rules for Claude

**Step 0 of every workflow:** check the tool list for the autolecture MCP tools → present = **mcp**, absent = **zip**.

**For anything needing user state** (voice clone / balance / quota):
- **mcp** → use what `whoami` etc. give; if unavailable, ask the user (same as zip)
- **zip** → `AskUserQuestion` or a conservative default

**For anything needing cloud feedback** (actually render to see the result):
- **mcp** → `render_shot(id, storyboard=true)` + read `get_state()` → `shots[].render.still` (or `compile` + `get_status` for the full video)
- **zip** → local harness L3 render as a substitute (inspect the HTML render); if there's no substitute, drop this step

**Final delivery:**
- **mcp** → MCP tools end-to-end (_delivery.md path A), hand over the Studio URL
- **zip** → `package_zip.py` builds the zip, tell the user to drag it onto autolecture.ai (path B)

---

## Relationship to workflows/_delivery.md

- **Path A · MCP-driven** = the delivery path for mcp mode (preferred)
- **Path B · zip** = the delivery path for zip mode (only option without MCP / on web)

After the skill workflow completes, by mode:
- mcp → path A (MCP tools end-to-end, hand over the Studio URL)
- zip → path B is the only option
