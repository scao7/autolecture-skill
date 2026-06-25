# Resume + project hygiene checklist — read this page before picking up any task

For any "continue / resume / pick up where we left off" task, **your first action is not writing code — it's verifying ground truth.**
Ground truth lives only in the cloud project (the canonical ProjectState — the actual shots + their scene code). Summaries / journals / memory
**are only leads, nothing more.**

> **One-line iron law**: the first tool call on resume MUST be `get_state`. **Do NOT trust "everything's already written."**

Consequences of violating this (it actually happened): followed the summary blindly → mass-produced a whole set of scenes
hanging off an abandoned draft → final render had missing views and clashing filenames; took an archaeology dig to figure out which set was canonical.

---

## 1. Resume iron law: ground truth is in the cloud, not the summary

Compaction summaries / journals / memory are **lossy**. They'll say "all 17 scenes written,
filenames `scene_*`" — but the cloud reality may be: this session only wrote 1 sample, the real render is the previous session's
`hd_*` (still missing one `hd_03`), and the `scene_*` the summary names is an even older, abandoned mixed draft.
**Trusting the summary = treating discarded drafts as canonical views and mass-producing on top of them.**

### Verification flow (step by step, no skipping)

1. **`get_state`** — pull the canonical ProjectState. This is the single source of truth, not local files, not memory.
2. **Read the shot list** — `get_state()` returns `shots[]` in order; that sequence IS the current canonical shot list.
   Which scene-code file does each shot reference (`shots[].layers[].src`, e.g. `scenes/s7.py`)? List them in order, and note each
   shot's `render.status` (`ready` / `failed` / `empty`).
3. **`read_file` each one to verify** — for every scene file a shot references:
   - Does the file **actually exist**? (is it in the snapshot's file list?)
   - Is the content a **finished render** or a **discarded draft**? (draft tells: mixed html+tsx, placeholder `TODO`,
     half-done animation, out of sync with the narration)
   - Be alert to gaps in numbering: `hd_01 hd_02 hd_04 …` missing `hd_03` — is it a skipped write, or a rename? Find out.
4. **Only continue on the confirmed canonical set after verifying each file**. Files in the snapshot not referenced
   by any shot in `get_state().shots[]` = orphans (inert — the shot list, not the file tree, decides what renders);
   treat them as discarded drafts by default and **don't continue writing on top of them.**

### Counter-example (the cost of copying the summary)

| Summary says | Cloud reality | Consequence |
|---|---|---|
| `scene_*` all 17 good | `scene_*` is an abandoned mixed html+tsx draft | mass-produced on a discarded draft |
| — | render is the previous session's `hd_*`, 16 of them, **missing `hd_03`** | missing view went unnoticed |
| "everything's written" | this session only wrote 1 sample | misjudged progress |

> Lesson: **summaries give leads, `read_file` gives truth.** Conclusory phrasing like "everything's written"
> only counts once you've personally verified every file.

---

## 2. Project hygiene: one naming scheme + the shot list is the manifest

### 1. One naming prefix per project

A single project uses **one** prefix only (either all `hd_*` or all `scene_*`, never both side by side).
Two prefixes coexisting = "which set is canonical" becomes an archaeology problem.

### 2. Replace a version in place — don't fork the source path

There is no `delete_file` / `move_file` in the JSON-canonical model, and you don't need them:

- **Revising a scene's code**: `write_file` the **same `src` path** — it overwrites in place, so no orphan is created.
- **Dropping a view entirely**: `remove_shot(id)` — the shot leaves `get_state().shots[]`, so it stops rendering
  immediately. Its old scene file may linger in the file tree but is now **inert** (no shot references it).

So an unreferenced file can't corrupt the render — only `shots[]` decides what renders. Still, keep one prefix and
overwrite-in-place so a later `read_file` browse isn't littered with dead drafts.

### 3. Gaps in numbering don't break anything — `shots[]` is the order

A gap in filenames (e.g. `hd_01 hd_02 hd_04`, missing `03`) is cosmetic: the canonical sequence is the **order of
`get_state().shots[]`**, not the filenames. Contiguous numbering is just for human readability; it's the shot list,
never the file names, that you trust.

---

## 3. The shot list IS the manifest

You don't maintain a separate "current canonical views" list — `get_state().shots[]` **is** that list, authoritative
by construction. Each shot's `layers[].src` points at its scene code; the array order is the play order. There is no
active-root `.tex` and no `MANIFEST.md` to drift out of sync — the render is driven by the same `shots[]` you read.

On resume, just `get_state()`: the shots in order, with each one's `render.status`, are the whole truth. Any file in the
snapshot not pointed at by some shot's `src` is an orphan draft.

---

## One-page recap

1. First action on resume = `get_state`, not writing code.
2. Truth = the cloud ProjectState shots + their scene code; summaries / memory = leads, `read_file` each scene file to verify.
3. Don't trust "everything's already written"; gaps in numbering, mixed drafts, orphan files all need personal verification.
4. One prefix per project; replace a version by overwriting the same `src` via `write_file`, or drop a view via `remove_shot`.
5. Canonical view list = the order of `get_state().shots[]` — it is the manifest; there is no separate root source or MANIFEST file.
