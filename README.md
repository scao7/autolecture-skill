# autolecture-skill

Claude Code skill that turns your material into a finished
[AutoLecture](https://autolecture.ai) video. The entry point asks what
kind of video you want, then routes to the matching workflow:

- **plain text / topic** → generated narration + hand-written visuals
- **audio recording / podcast** → transcribe → match visuals (rough re-synth or keep your voice)
- **PDF paper** → *explain it* (extract figures) or *show it* (render the real pages with react-pdf, zoom + locate + highlight — technique borrowed from [pdf2video](https://github.com/DangJin/pdf2video))
- **real footage** → overlay transparent motion graphics on top (`over=`)

Claude generates the scenes, then either packages a zip you upload, or
uploads + compiles + downloads the mp4 via the
[autolecture](https://github.com/scao7/autolecture-python) Python SDK.

## Install

```bash
# 1. Add the skill to your agent — one line, works with Claude Code,
#    Cursor, Codex, and 12+ other agents. Add -g for a global install.
npx skills add scao7/autolecture-skill

# 2. Install the Python SDK (used by the one-click upload+compile flow)
pip install autolecture
```

`npx skills` is [Vercel Labs' open agent-skills tool](https://github.com/vercel-labs/skills);
it clones this repo into your agent's skills dir (`~/.claude/skills/` for
Claude Code). Prefer git? Clone it yourself:

```bash
git clone https://github.com/scao7/autolecture-skill.git ~/.claude/skills/autolecture-skill
```

**Sign in** — the SDK handles auth for you. The first compile prints a
`/connect?code=…` link; approve it in your browser (OAuth device flow)
and the token is cached to `~/.config/autolecture/auth.json`. For CI /
headless runs, set an API key instead (mint at
<https://autolecture.ai/account> → 🔑 API Keys → Generate; the
`al_live_…` value is shown once):

```bash
export AUTOLECTURE_API_KEY='al_live_…'
```

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
> "做个 autolecture demo" `--include recording.mp3`
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
delivery step [`workflows/_delivery.md`](workflows/_delivery.md): package
a zip, or run [`scripts/upload_and_compile.py`](scripts/upload_and_compile.py)
to create a project, upload assets, PUT the tex, poll the compile job
block-by-block, and download the mp4.

Typical session ends like:

```
== compile succeeded — 6 ✦ spent in 42.1s
   downloading final mp4 → ./out.mp4
[done]
  open in Studio: https://autolecture.ai/studio?id=…
```

Open `out.mp4` locally, or follow the Studio URL to keep tweaking in
the web editor (regenerate individual scenes, swap voices, add BGM,
re-render).

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

- **`AUTOLECTURE_API_KEY env var not set`** — see Install step 3.
- **`Missing the autolecture SDK`** — confirm the venv Claude Code is
  using has it: `which python && python -c "import autolecture; print(autolecture.__version__)"`.
- **Compile fails** — the script exits 1 and prints the error-log tail.
  Open the Studio URL it prints, inspect the failed block (it'll have
  a red icon), iterate on its source, re-run.
- **`(429) rate_limited` or `(402) insufficient_credits`** — the
  message includes window + limit + your current balance. Top up at
  <https://autolecture.ai/account> or wait for the daily reset.
- **Target a different backend** —
  `export AUTOLECTURE_BASE_URL=https://dev.autolecture.ai` (default
  is `https://autolecture.ai`).
- **Missing system binary** (ffmpeg / pdftoppm / git) — the helper
  scripts hard-exit with the install command. Follow the message.

## Links

- Skill spec — [SKILL.md](SKILL.md) (authoritative; read this if
  you're extending the skill)
- Python SDK — <https://github.com/scao7/autolecture-python> · `pip install autolecture`
- AutoLecture web app — <https://autolecture.ai>
- VideoTeX DSL reference — <https://autolecture.ai/docs/dsl>

## License

MIT — see [LICENSE](LICENSE).
