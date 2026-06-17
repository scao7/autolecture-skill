# Fable science · fable-science

> **genre**: fable science　**engine**: html (hand-drawn storybook)　**palette**: brand cream/navy/tan
> **source**: "Town of a Hundred Crafts / MCP fable" (hand-drawn storybook, 17-view verified) · distilled from a finished project

A **skill** (not a template to be cloned): describes what kind of video it makes + how to invoke it + the recipe to follow.
Select it, and the agent takes the user's concept and **makes a fresh new video right then**, following the recipe below; it's not cloning some project and filling placeholders.

---

## What this skill does

Tells an **abstract / technical concept** as a **fable**: the concept is personified into characters in a little world, the mechanism becomes events happening in the story, warm hand-drawn picture-book texture, **narration-driven** visuals.

- **Good for**: explaining principles / systems / protocols / algorithms / architectures, the kind of "invisible, intangible" things; wanting warm,
  memorable, non-PowerPoint popularization; aimed at a general audience or beginners.
- **Not for**: precise formula derivation (go the "math formula" skill), showing real UI/data (go screen-capture /
  data visualization), serious paper explanation (go pdf-paper). The fable is a **metaphor that lowers the barrier**, it doesn't chase rigor.

## How to invoke (invocation)

1. Select this skill → first ask the user three things (see "Input" below).
2. The agent makes a fresh video following the **Recipe**: concept→fable mapping → narration finalized → hand-drawn storybook visuals →
   incremental compile verification → delivery.
3. If this skill ships a starter skeleton, `use` it to scaffold the start first; if not, build from an empty project per the recipe.
4. Audio-driven + sample-first throughout — the same discipline as freestyle, only the **narrative and visuals are locked to the fable form**.

> Visual technique details are not repeated here; follow [`../reference/hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md) directly
> (stroke draw → paint flood → pen jitter → continuous micro-motion → entrance budget). This skill only covers how to build "the fable layer".

## Input (ask once at the start)

- **The concept/topic to explain** (required): e.g. "how the MCP protocol works", "TCP three-way handshake", "gradient descent".
- **Audience + tone**: children's picture book / warm adult popularization / lightly humorous — decides the narration voice.
- **Duration target**: the fable-science sweet spot is **40–90s** (5–9 views); longer tends to drag.

---

## Recipe

### 1 · Concept → fable mapping (most critical, do it first)

This step decides life or death. Break the technical concept into **personifiable parts**, mapping each into a **character / place / event** in the little world:

| The thing in the concept | Maps to | Example (MCP) |
|---|---|---|
| Entity / module / actor | a **character** (personified little creature/person/animal) | client = a little messenger running errands, server = a shopkeeper in town |
| Relation / channel / protocol | a **pact / road / token** between characters | MCP = a "passport" both sides recognize |
| Process / algorithm step | **events that happen in sequence** in the story | handshake = messenger hands over the passport, shopkeeper stamps it, both nod |
| State / data | the **thing in a character's hand / their expression** | connection established = the tokens match, the door opens |

Produce a **mapping table + one-line story line** (who, where, for what, what happened), get the user to **finalize** it, then go on.
Whether the fable holds up rests entirely on this table — don't force the mapping, one concept part to one story element, **1:1, don't pile up**.

### 2 · Narration script (finalize first)

Fable science is **telling a story**; the narration is the story itself, not a manual:

- **Story-voice tone**: "Once upon a time, in the Town of a Hundred Crafts, there lived a……" rather than "MCP is a protocol, it……".
- Each view's `\say{}` = the story advancing **one beat** + secretly hooking one technical point (story in the open, knowledge underneath).
- The closing view **lands the point**: pull the fable back to reality "——this, is XX".
- Write the full narration first → **get the user to finalize** → then assign visuals (audio is the spine of the timeline).
- `\say` ≤400 chars / view; captions off by default (need `burn=on` to burn); with a voice sample can use `[voice=mine]`.

### 3 · Visuals: hand-drawn storybook (do it by the technique)

One `\htmlFile{}` per view, strictly following [`hand-drawn-storybook.md`](../reference/hand-drawn-storybook.md):

- **Character consistency**: the same character looks the same throughout the video (same stroke shape/palette), only the pose/position/expression changes per view;
  don't redraw a new design each view (the fable builds memory hooks through character recurrence).
- One core action/event per view, ample whitespace, the brand trio cream/navy/tan doesn't drift.
- A different `seed` per scene (jitter doesn't repeat); one naming prefix (e.g. `fb_01..fb_NN`).
- Entrance drawn in ≤1.5s, after which only `bob/sway/spin` loop micro-motion remains (audio-first hard requirement).

### 4 · audio-first timing

Duration is driven by `\say`; HTML doesn't know how long the audio is → after the entrance animation runs it's a frozen frame. So run each view through
hand-drawn-storybook's "entrance budget self-check" trio: still moving after second 2? is the only thing moving the infinite micro-motion?
drawn within 1.5s of entrance? Only "yes" on all three is compliant. See [`../reference/audio-first.md`](../reference/audio-first.md).

### 5 · Mass-production discipline

- **Sample-first**: make **view 1** end-to-end first (create project → write 1 view → `compile` → `fetch_frame` to see the frame →
  user signs off "OK") → then batch. The character design must be nailed in the sample.
- **After writing each view, `compile` on the spot and check `block_errors` before the next view** (incremental compile, don't write all then compile).
- `main.tex` skeleton first: all views as placeholders compilable first, then fill view by view.
- Delivery goes via [`../workflows/_delivery.md`](../workflows/_delivery.md).

---

## Example view (a fable-form view looks like this)

```latex
\begin{view}
  \say{从前,在百巧城的城门口,住着一个跑腿的小信使。
       他想进城办事,可城里的店家谁也不认识他。}
  \htmlFile{scenes/fb_01_messenger.html}   % hand-drawn: city gate + little messenger (stroke→fill→bob micro-motion)
\end{view}
```

```latex
\begin{view}
  \say{直到有一天,两边都掏出了同一张通关文牒——
       从此,信使递一递,店家盖个章,门就开了。这,就是 MCP。}
  \htmlFile{scenes/fb_07_handshake.html}   % the same little messenger + shopkeeper, tokens match, door opens
\end{view}
```
(The `\say{}` example values above are kept in Chinese on purpose — they demonstrate fable-form narration for a Chinese-topic video; the skill still produces narration in the user's topic language.)

---

## Self-check (did this skill do it right)

1. Is there a **concept→fable mapping table**, and is it 1:1, not forced?
2. Is the narration **story-voice** or manual-voice? (manual-voice = not done right)
3. Does the character **recur as one design** throughout?
4. Are the visuals hand-drawn storybook, one consistent style throughout, passing the entrance budget self-check?
5. Does the ending **land the point**, pulling the fable back to the technical concept?
