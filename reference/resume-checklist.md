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
   by the active root = orphans; treat them as discarded drafts by default and **don't continue writing on top of them.**

### Counter-example (the cost of copying the summary)

| Summary says | Cloud reality | Consequence |
|---|---|---|
| `scene_*` all 17 good | `scene_*` is an abandoned mixed html+tsx draft | mass-produced on a discarded draft |
| — | render is the previous session's `hd_*`, 16 of them, **missing `hd_03`** | missing view went unnoticed |
| "everything's written" | this session only wrote 1 sample | misjudged progress |

> Lesson: **summaries give leads, `read_file` gives truth.** Conclusory phrasing like "everything's written"
> only counts once you've personally verified every file.

---

## 2. Project hygiene: one naming scheme + archive orphans + MANIFEST

### 1. One naming prefix per project

A single project uses **one** prefix only (either all `hd_*` or all `scene_*`, never both side by side).
Two prefixes coexisting = "which set is canonical" becomes an archaeology problem.

### 2. Archive the old version when you replace it — don't leave orphans

When replacing an old version with a new one, clear the old one **on the spot**, don't defer:

```
# right after writing the new version, archive the file it supersedes
delete_file  scene_03.html          # just delete the discarded draft
move_file    scene_03.html  _archive/scene_03.html   # or archive to keep a backup
```

Orphan files left uncleaned across rounds → pile up → next resume you have to re-judge "which set is canonical" all over again.

### 3. Gaps in numbering amplify ambiguity

A gap in filenames (e.g. `hd_01 hd_02 hd_04`, missing `03`) makes it impossible to tell a **skipped write**
from a **rename**. Contiguous numbering + immediate archiving kills the ambiguity at the source.

---

## 3. MANIFEST convention: the single list of current canonical views

Every project needs **one** authoritative "current canonical views" list. Two approaches — pick either, but be explicit:

- **Preferred: rely on the view order in the active root source** — the view sequence inside `\begin{videotex}` IS
  the list. This keeps the list and the render **same-source**, so they can't drift. On resume, just read it.
- **Backup: a `MANIFEST.md` at the project root** — when view references and file intent aren't self-explanatory enough,
  use a table to pin down "view → file → status":

  ```markdown
  # MANIFEST — current canonical views (authoritative; all other files are orphans)

  | # | view | file | status |
  |---|------|------|--------|
  | 01 | opening | hd_01.html | finished |
  | 02 | character entrance | hd_02.html | finished |
  | 03 | conflict | hd_03.html | TODO (missing) |
  | … | … | … | … |
  ```

> Rule: **when the active root source's view order conflicts with `MANIFEST.md`, the active root wins**
> (it drives the actual compile). MANIFEST is just a human-facing guide, not a second source of truth.

---

## One-page recap

1. First action on resume = `get_state`, not writing code.
2. Truth = the cloud ProjectState shots + their scene code; summaries / memory = leads, `read_file` each scene file to verify.
3. Don't trust "everything's already written"; gaps in numbering, mixed drafts, orphan files all need personal verification.
4. One prefix per project; when replacing old versions, `delete_file` / `move_file` on the spot.
5. Canonical view list = active-root view order (preferred) or `MANIFEST.md` (backup; active root wins).
