# Delivery (the last step of every workflow)

**First determine the run mode → decide which path** (per [`reference/runtime-modes.md`](../reference/runtime-modes.md)):

Check the tool list for the autolecture MCP tools — present = **mcp** (path A), absent = **zip** (path B).

| Mode | Delivery path | Note |
|---|---|---|
| **mcp** (MCP tools present) | **Path A · MCP direct-drive** (preferred) | Claude uses MCP tools to build the project + write files + compile + get the mp4 in the cloud, end-to-end; on failure can `fetch_frame` to inspect frames and debug |
| **zip** (no MCP, incl. web client) | **Path B · zip** | Claude produces a project zip; the user drags it to autolecture.ai to upload |

---

## Path A · MCP direct-drive (preferred — when the autolecture MCP tools are in the tool list)

Claude uses autolecture's MCP tools to do it all in the cloud, end-to-end.

> ⚠️ **Iron rule: incremental persistence — land every finished view in the cloud immediately, NEVER pile it up for one final write.**
> A long project has a dozen-plus scenes; if you hold them all in your head / locally and only `write_file` everything at the very end,
> then the moment you **hit the tool-use limit** mid-flow, disconnect, or a call fails, **it's all wasted**. Write incrementally and: the views
> already written are already in the cloud project, valid, compilable; to continue you just `read_file("main.tex")` to see where you got to and keep going.

1. **Create project + write skeleton** — `create_project` (or `list_templates` to pick a template) to get a project id.
   Immediately `write_file("main.tex", …)` a **skeleton with only the toplevel macros + an empty body**, keeping `\end{videotex}` at the end as an anchor:
   ```
   \title{…}\aspect{…}\style{…}\voice{…}
   \begin{videotex}
   \end{videotex}
   ```
   At this point the cloud already holds a compilable (empty) project — afterwards every view is inserted before this anchor.

2. **Write view by view, incrementally (core loop — repeat per view)**: each time you finish **one** view, on the spot:
   a. `write_file("scenes/scene_NN.{html,tsx,py}", source)` — write this view's scene file.
   b. `edit_file("main.tex", old_string="\end{videotex}", new_string="<this view's \begin{view}…\end{view}>\n\end{videotex}")` — **append this view before the anchor**. `\end{videotex}` is unique and reusable; after inserting it's still there, the next view keeps inserting.
   c. If this view uses assets, `add_asset` to upload them.
   d. (Recommended) `compile` (render just this block) + `get_status` — **render it on the spot, catch errors on the spot**, rather than piling them up to blow up together at the end.
   → Each view lands on your platform the moment it's written. **Any interruption mid-flow loses nothing already written.**

3. **All views written → compile the whole video** — `compile` (whole project) → `get_status` poll to completion → `get_output` to get the mp4 + Studio URL. (If every block was rendered in step 2d, this step basically all hits cache, fast.)

4. **On failure, inspect frames and debug yourself** (the core value of MCP mode over zip) — `get_status` gives structured errors (which block / category / offending source) → `edit_file` to fix that file → `fetch_frame` to pull the PNG that view rendered and confirm → re-render only the changed block (`compile` with only-block, the rest hits cache). `fetch_waveform` to inspect the audio shape. **At most 3 self-fixes per block**; if that fails, escalate to the user with evidence (offending fragment + frame + Studio URL).

5. **Deliver** — return the Studio URL + a one-line "how to use"; the user can keep editing in Studio / click ▶ Recompile.

> Tool-name prefixes vary by client (e.g. `autolecture:compile` / `mcp__autolecture__compile`). Parameter schemas follow the tool definitions you actually see — if unsure, first `list_projects` / `whoami` to probe.
> **Continuation**: after a conversation is interrupted and reconnected, first `read_file("main.tex")` to see which views are already written, continue inserting before the `\end{videotex}` anchor, don't rewrite from scratch.

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
