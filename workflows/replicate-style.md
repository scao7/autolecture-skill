# Visual replication — "copy" motion and layout by watching a reference video

Input: a reference video (YouTube link / local file / in-project asset) + your own content.
Output: present your content in the reference video's visual language (motion / layout / palette / rhythm).

> ⚠️ **Runtime boundary**: YouTube pulling (yt-dlp) is only done in **Claude Code local mode** —
> server-side proxy downloading violates YouTube ToS; never make it a platform feature or suggest the user go via zip/cloud.
> If the reference video is already a project asset, then cloud MCP mode can also do it (use `fetch_asset_frame` to view frames).
> Replicate a "style" for your own content; the boundary of shot-by-shot replicating someone else's complete work is for the user to judge.

## Flow

1. **Acquire material** (split by source)
   - YouTube (local only): `yt-dlp -f "bv*[height<=1080]" -o /tmp/ref.mp4 <url>`
   - Project asset: skip the download, later frame extraction uses MCP `fetch_asset_frame(project_id, rel_path, t)`

2. **Extract frames and watch the motion as a strip** — motion needs consecutive frames to read; a single frame only reads layout:
   - First coarse-scan to locate motion nodes: `ffmpeg -i /tmp/ref.mp4 -vf "fps=1,scale=320:-2,tile=10x6" /tmp/ref_contact.png` (a contact sheet, one image to overview the whole video)
   - For each target motion extract a strip of 8 frames per second: `ffmpeg -ss <t> -i /tmp/ref.mp4 -t 1 -vf "fps=8,scale=480:-2,tile=8x1" /tmp/fx_<name>.png`
   - Read each strip and **write down the conclusions**: entrance style (translate/scale/fade-in/mask-reveal), easing feel (spring bounce / ease-out hard stop / linear), stagger interval, dwell duration, exit style

3. **Distill style tokens**: palette (sample 3-5 main color hexes), font character (serif/sans/mono, weight), corner-radius/stroke/shadow language, safe-area habit. Write into the project's `\style{}` and scene constants.

4. **Hand-write scenes to replicate**: pick the closest skeleton from [`templates/`](../templates/), translate the step-2 conclusions into code parameters (remotion: `spring({damping})`/`interpolate+Easing`; html: CSS animation/SMIL). Settled reverse-engineered recipes are in [`reference/borrowed-techniques.md`](../reference/borrowed-techniques.md) — newly reverse-engineered good recipes should be written back there.

5. **Iterate against the reference**: compile → `fetch_frame` (rendered block) **side-by-side** with the reference frame strip → tune parameters and re-render. Check common gaps in order: easing type → duration → stagger → font size/tracking.

## Expectation management (tell the user up front)

Text / MG motion (titles, info cards, charts, transitions) can reach "very close"; easing and duration are perceptual-level approximations;
3D/particles/live-action compositing can only mimic the mood; no pixel-level frame-by-frame match.
