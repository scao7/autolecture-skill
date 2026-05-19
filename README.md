# autolecture-skill

Claude Code skill that turns a script, audio recording, or podcast
(optionally + a PDF or GitHub repo) into a finished
[AutoLecture](https://autolecture.ai) video. Claude generates the
scenes, uploads them via the
[autolecture](https://github.com/scao7/autolecture-python) Python SDK,
compiles on the server, and saves the mp4 next to your input.

## Install

```bash
# 1. Clone the skill into Claude Code's skills directory
git clone https://github.com/scao7/autolecture-skill.git ~/.claude/skills/autolecture-skill

# 2. Install the Python SDK (required for every flow)
pip install autolecture

# 3. Mint an API key at https://autolecture.ai/account → 🔑 API Keys → Generate.
#    Copy the al_live_… value immediately — shown ONCE.
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
> "Turn this paper into an explainer video." `--include paper.pdf`

Claude reads [`SKILL.md`](SKILL.md), picks a mode (text / rough audio
/ polished audio), and runs the 10-step pipeline:

1. Pick mode + extract / transcribe the script
2. Plan beats (one beat ≈ one view)
3. Hand-write a `\manimFile` / `\htmlFile` / `\remotionFile` source
   per scene — **no LLM-codegen render macros**, the skill bans
   those (see SKILL.md HARD BANS)
4. Optionally match PDF figures or repo screenshots to specific
   beats with anchor-sentence evidence
5. Run [`scripts/upload_and_compile.py`](scripts/upload_and_compile.py)
   — creates a project, uploads the assets, PUTs the tex, polls the
   compile job block-by-block, downloads the mp4

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
IDE paths all read your local `~/.claude/skills/` so re-cloning the
repo is the upgrade path.

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
