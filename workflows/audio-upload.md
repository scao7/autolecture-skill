# Workflow · User uploads audio recording → video (audio-driven)

**Entry**: user gives a piece of **audio** (mp3/wav/m4a). **Audio-driven**: the human voice is the spine of the timeline.
Transcribe first + fix typos + decide whether to restructure the script — this determines whether the audio is "keep the original audio and cut directly" or "voice clone re-synthesis".

---

## Steps

### 0 · Use the run mode already confirmed at the SKILL.md entry + decide voice clone handling

> **The run mode was already set at SKILL.md entry ①** (mcp / zip) — don't ask again here. The voice clone decision below branches by mode.

**Voice clone handling decision** (specific to this workflow, decides whether later `\say` writes `voice=mine`):

- **mcp**: check whether the user info from `whoami` (or related tools) has a voice sample; yes → plan writes "all `\say` carry `voice=mine`"; if you can't get it, ask the user as in zip.
- **zip**: `AskUserQuestion`, three choices: ① yes, use my cloned voice (whole video `voice=mine`) ② no / unsure (default speaker) ③ I want to keep the original audio, no TTS (go the `\audio[start,end]{}` + `\caption{}` path, no `\say` TTS).

Write the decision into `<work>/beat_plan.md`. **The whole video's `\say` uses one and the same handling, no mixing.** For the full fallback table of both modes per action, see [`../reference/runtime-modes.md`](../reference/runtime-modes.md).

### 1 · Prepare + transcribe
```bash
WORK=/tmp/autolecture_$(date +%s); mkdir -p $WORK/{scenes,figures}
python3 scripts/transcribe.py --audio <user.m4a> --out <work>/<user>.m4a.whisper.json
```
[`scripts/transcribe.py`](../scripts/transcribe.py) uses `whisper.base` with word-level timestamps, landing a sidecar JSON.

### 2 · Fix transcription typos (HARD BAN #3)
Read [`../reference/typo-fixes.md`](../reference/typo-fixes.md) ("高撕"→"高斯", "政策画像"→"正则项") + any newly found this run, go through sentence by sentence, record the correction mapping in `<work>/transcript_corrections.md`. (Those Whisper-typo example pairs are kept in Chinese on purpose — they're example values.) **The original audio is untouched**; typos only affect the visual text / restructured script.

### 3 · Analyze: clean voiceover or casually-recorded thoughts? → decide whether to restructure
- **Clean voiceover** (finished podcast / deliberately recorded coherent narration) → most likely **no restructure**, keep the original audio.
- **Casually-recorded thoughts** (off-topic, stumbling, repetitive, thinking out loud) → most likely **needs restructuring** the script.
- If unclear, ask the user via AskUserQuestion: "Keep your original audio and cut it directly, or let me reorganize the content and re-narrate it in your voice (voice clone)?"

---

## Route A · No restructure (keep original audio, cut directly)

Audio stays as-is; segment naturally by content, use `\audio[start=,end=]{}` to cut the original audio, assign a visual to each segment.

1. Search each segment's **anchor sentence** (the distinctive opening words) in the transcript, use [`scripts/find_beats.py`](../scripts/find_beats.py) to locate the start timestamp; between adjacent anchor sentences = one view's `[start, end]`. **Don't reorganize the narrative**, cut in the audio's natural order.
2. Assemble:
   ```latex
   \begin{view}
     \audio[start=32.34, end=37.48]{<user>.m4a}   % original audio segment
     \htmlFile{scenes/scene_02.html}               % the assigned visual
   \end{view}
   ```

## Route B · Restructure (voice clone + TTS re-narration)

Reorganize the content into a clear narrative, re-synthesize with the **user's own voice clone** (not the default TTS voice), then cut and write visuals by TTS duration.

1. **Rewrite the script**: re-organize the narrative from the corrected transcript (clear beginning/middle/end, cut redundancy, add connective sentences).
2. **voice clone**: have the user register a voice sample at <https://autolecture.ai/account> (use this recording as the sample); afterwards `\say[voice=mine]{...}` synthesizes with the cloned voice. State this step in the delivery note (without a registered sample it falls back to the default voice).
3. **Cut and write visuals by TTS duration**: each rewritten segment = one view's `\say[voice=mine]{}`; real durations are locked at compile time by TTS + audio-first (see [`../reference/audio-first.md`](../reference/audio-first.md)), estimates are only for layout.
   ```latex
   \begin{view}
     \say[voice=mine]{<this rewritten segment>}
     \remotionFile{scenes/scene_02.tsx}
   \end{view}
   ```

---

## Supporting assets (applies to both routes, if any)
The user also gave a PDF / repo / images → match them into the visuals per [`../reference/figure-matching.md`](../reference/figure-matching.md); each figure **must have anchor-sentence evidence** written into `beat_plan.md` (HARD BAN #8). To **show the original PDF** in the visuals → layer in [`pdf-paper.md`](pdf-paper.md)'s Flow B shots.

## Pick engine + hand-write scene
Read [`../reference/engine-routing.md`](../reference/engine-routing.md); the visual hooks each segment's voiceover point and meaning. Unified palette [`../reference/palette.md`](../reference/palette.md), each scene designed independently, ≤60s, named `scene_NN_label.<ext>`.

## README + delivery
`<audio>.m4a` + `.whisper.json` go into the included items (Route A needs them for caption alignment). Then → **delivery: see [`_delivery.md`](_delivery.md)**.
