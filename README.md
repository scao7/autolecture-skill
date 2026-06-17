# autolecture-skill

Claude Code skill that turns your material into a finished
[AutoLecture](https://autolecture.ai) video. The entry point asks what
kind of video you want, then routes to the matching workflow:

- **plain text / topic** → generated narration + hand-written visuals
- **audio recording / podcast** → transcribe → match visuals (rough re-synth or keep your voice)
- **PDF paper** → *explain it* (extract figures) or *show it* (render the real pages with react-pdf, zoom + locate + highlight — technique borrowed from [pdf2video](https://github.com/DangJin/pdf2video))
- **real footage** → overlay transparent motion graphics on top (`over=`)

Claude generates the scenes, then — if you've connected the AutoLecture
**MCP connector** — builds the project and compiles it in the cloud
directly via MCP tools; otherwise it packages a zip you upload at
[autolecture.ai](https://autolecture.ai).

## Install

```bash
# Add the skill to your agent — one line, works with Claude Code,
# Cursor, Codex, and 12+ other agents. Add -g for a global install.
npx skills add scao7/autolecture-skill
```

`npx skills` is [Vercel Labs' open agent-skills tool](https://github.com/vercel-labs/skills);
it clones this repo into your agent's skills dir (`~/.claude/skills/` for
Claude Code). Prefer git? Clone it yourself:

```bash
git clone https://github.com/scao7/autolecture-skill.git ~/.claude/skills/autolecture-skill
```

**To let Claude compile in the cloud** (so you get a finished video
without touching the web UI), connect the AutoLecture **MCP connector**
in your agent: Settings → Connectors → Add →
`https://mcp.autolecture.ai/mcp` → approve in the browser. Then Claude
creates the project, writes the files, and compiles via MCP tools end to
end. Without a connector the skill just packages a project **zip** you
upload at [autolecture.ai](https://autolecture.ai) — the path most
**claude.ai web** users take.

**Per-input-type extras** — install only what your input needs:

| If your input is | also install |
|---|---|
| audio (mp3 / wav / m4a) | `pip install openai-whisper` + system `ffmpeg` |
| PDF paper with figures | `pip install pdfplumber Pillow` + system `pdftoppm` |
| a GitHub repo | system `git` |
| plain text script | nothing extra |

System binaries: `sudo apt install ffmpeg poppler-utils git` (Ubuntu) /
`brew install ffmpeg poppler git` (macOS).

> Migrating from an older copy of this skill?  Wipe the old folder
> before cloning the new one: `rm -rf ~/.claude/skills/autolecture-demo
> ~/.claude/skills/autolecture-claude-skill`.

## Use

Open Claude Code in any working directory and ask it to do the thing,
optionally attaching an input file:

> "Use the autolecture skill to make a 30-second explainer on Bayes theorem."
>
> "Make an autolecture video from my recording." `--include recording.mp3`
>
> "Show this paper in the video — flip pages, zoom, highlight." `--include paper.pdf`
>
> "Overlay lower-thirds and callouts on my footage." `--include clip.mp4`

Claude reads [`SKILL.md`](SKILL.md) — a **router** — figures out which
input you have (asking if unclear), then opens the matching playbook in
[`workflows/`](workflows/) and follows it:

| Input | Workflow |
|---|---|
| plain text / topic | [`workflows/text-to-lecture.md`](workflows/text-to-lecture.md) |
| audio / podcast | [`workflows/audio-upload.md`](workflows/audio-upload.md) |
| PDF paper | [`workflows/pdf-paper.md`](workflows/pdf-paper.md) |
| real footage | [`workflows/video.md`](workflows/video.md) |

Every workflow hand-writes a `\manimFile` / `\htmlFile` /
`\remotionFile` source per scene (**no LLM-codegen render macros** — the
skill bans those; see SKILL.md HARD BANS), then converges on the shared
delivery step [`workflows/_delivery.md`](workflows/_delivery.md): with the
MCP connector, Claude creates the project, writes the files, uploads
assets, compiles in the cloud, and fixes failing scenes by fetching
frames — all via MCP tools. Without it, Claude packages a zip you upload.

With the MCP connector on, a session ends like:

```
✓ compiled — 6 ✦ spent
  open in Studio: https://autolecture.ai/studio?id=…
```

Follow the Studio URL to play it or keep tweaking (regenerate scenes,
swap voices, add BGM, re-render). In zip mode you get a zip to drop on
[autolecture.ai](https://autolecture.ai) instead.

## Where this runs

| Surface | Works? | How |
|---|---|---|
| Claude Code CLI (`claude` in a terminal) | ✓ | reads `~/.claude/skills/` |
| Claude Code desktop app (Mac / Windows) | ✓ | same |
| Claude Code IDE extensions (VS Code / JetBrains) | ✓ | same |
| **claude.ai web** → Customize → Skills → **+** | ✓ | upload this repo as a Personal Skill (zip or git URL) |

The web upload keeps a copy on Anthropic's side; the CLI / desktop /
IDE paths all read your local `~/.claude/skills/`. Upgrade with
`npx skills update` (or re-clone if you installed via git).

## Troubleshooting

- **No cloud compile happening?** — Claude only compiles when the
  AutoLecture **MCP connector** is connected (Settings → Connectors).
  Without it the skill produces a zip for you to upload at autolecture.ai.
- **Compile fails** — Claude inspects the failing scene (fetches a frame
  via MCP), fixes its source, and re-renders just that block. If it can't,
  it hands you the Studio URL — open it, fix the red block, recompile.
- **`(429) rate_limited` or `(402) insufficient_credits`** — the
  message includes window + limit + your current balance. Top up at
  <https://autolecture.ai/account> or wait for the daily reset.
- **Missing system binary** (ffmpeg / pdftoppm / git) — the helper
  scripts hard-exit with the install command. Follow the message.

## Links

- Skill spec — [SKILL.md](SKILL.md) (authoritative; read this if
  you're extending the skill)
- Remote MCP — <https://mcp.autolecture.ai/mcp> (connect it in your agent for cloud compile)
- AutoLecture web app — <https://autolecture.ai>
- VideoTeX DSL reference — <https://autolecture.ai/docs/dsl>

## License

MIT — see [LICENSE](LICENSE).
