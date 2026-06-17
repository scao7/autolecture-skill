# Template marketplace path (marketplace)

This path runs when the user picks "② Find a dedicated template in the marketplace" at the entry. Each **genre**
in the marketplace is a server-side **dedicated authoring instruction pack** (agent card) — once a genre/template is
selected, it takes over how this video gets made: which engines, pacing, aspect, structure, voiceover style.

> **Design intent (cross-agent)**: marketplace content **lives entirely on the server**, pulled on demand via the
> autolecture MCP tools — it is not a locally installed skill. So any agent that can reach `mcp.autolecture.ai/mcp`
> (Claude / Codex / …) can consume the same set of templates directly, zero install, point-and-use.
> This playbook's logic depends only on MCP tool names, not on any client's proprietary capabilities.

> **Open/closed split (2026-06)**: `list_gallery_templates` / search **list official (curated) genres only** —
> fuzzy browsing always hits only the reviewed set, so the user's intent never lands on an unvetted community
> recipe. Templates the user **published themselves** (community templates) are **not in this list**; they can only
> be loaded by **exact slug** via `get_template_card(slug)` / `use_gallery_template(slug)`
> (these two tools resolve **any** id, official or community). So: when the user names a specific community
> template/link, **do NOT fuzzy-match** — ask for (or recall) its exact slug and pull it by id.

---

## Prerequisite: the marketplace is only available in mcp mode

The marketplace is a server-side gallery; **you must have the autolecture MCP tools** to browse/clone it.

- **mcp mode** → follow the steps below.
- **zip mode** (claude.ai web / no connector) → the marketplace is unavailable. Tell the user: either
  connect the `mcp.autolecture.ai/mcp` connector and come back, or go **freestyle**
  (see the freestyle branch under entry ② in SKILL.md, which doesn't depend on the marketplace).

---

## Flow (at most two questions, easy to use)

### 1 · List genres → let the user pick

Call `list_gallery_templates`; each item in the returned list carries `genre`, `slug`,
`title`, `description`, `engines`, `duration_sec`, `has_agent_card`.

- **Display grouped by `genre`** (e.g.: explainer / AI short drama / math formulas / product intro /
  data viz / talking-head sales…). The list is slim and **does not include the authoring-instruction body** — pull
  the body on demand to save context.
- Use `AskUserQuestion` (Claude) or an equivalent option prompt to have the user pick a **genre** first, then a
  **specific template (slug)** within it. If a genre has only one template, just settle on it.

### 2 · Pull the selected card's authoring instruction pack

For the user's chosen `slug`, call `get_template_card(slug)` (or `get_template_skill(slug)`,
if the server provides it) — it returns that template's **dedicated authoring instructions** (markdown): what it's for,
which scenes/assets are placeholders to be replaced, which knobs to tune, engine/pacing/structure/voiceover style, 1–2 example views.

- **Pull only the selected card**, don't pull every card's body into context (keep tokens controlled).
- After reading this card, **author per its recipe** going forward — it is the authoritative guide for this video.

### 3 · Clone the starting project

Call `use_gallery_template(slug)` — this clones the template's `main.tex` + scene files + assets as a whole
into a new project under the user's account, returning `project_id` + `studio_url`. These templates are all
**compile-verified real projects**; replacing placeholders on top of one is far faster than writing from scratch.

### 4 · Take over authoring per the card

From here it's the normal audio-first authoring loop, but **follow the card's recipe** (engine choice, pacing,
structure, voiceover style all per the card):

- Replace placeholder scenes / assets with the user's real content (HARD BAN 2: design each scene per its content,
  no filling different text into the same template).
- **For each view replaced/added, `compile` on the spot + check `block_errors` + fix** (HARD BAN 17,
  incremental compile); for key visuals, pull 1–2 frames with `fetch_frame` to verify.
- For multi-view tasks, do 1 sample and get sign-off before batching (HARD BAN 13).
- Delivery goes through [`../workflows/_delivery.md`](../workflows/_delivery.md).

---

## Gate / entitlement

A template may carry an `entitlement` (free / Pro / one-time unlock). If `get_template_card` /
`use_gallery_template` is blocked by the server on permissions (returns an auth-class error), **relay the upgrade/unlock
prompt to the user faithfully** — don't downgrade and force it through; the server is the sole arbiter.

---

## Relationship to freestyle

- Marketplace path = pick a genre, follow the dedicated recipe, skip designing an approach from scratch.
- Freestyle = take this when there's no suitable genre, or you want full customization; route by primary input type
  into `workflows/`, no marketplace dependency.
- Both converge on the same delivery step [`../workflows/_delivery.md`](../workflows/_delivery.md).

> **Publishing your own template**: once the user finishes a project they're happy with, they can solidify it into a new
> genre template and publish it to the marketplace (the agent reverse-engineers an authoring-instruction draft from the
> finished work → the user reviews and fills in genre/price → the server verifies the compile → it goes live). **Mind the
> open/closed split**: what the user publishes is a **community template** —
> `official=false` and `unlisted`, **loadable only by exact slug, not in fuzzy browse**
> (hand the slug to the user to keep). Getting it into the official curated catalog is a separate (seed/admin) path,
> not through this endpoint. See `publish_template` (enabled when the server provides that tool).
