# autolecture-skill

Claude Code skill that turns a script / audio recording / podcast
(optionally + a PDF or GitHub repo) into a finished
[AutoLecture](https://autolecture.ai) video. End-to-end: generate the
project, upload it via the [Python SDK](https://github.com/scao7/autolecture-python),
compile, download the mp4.

## Install

### 1. Drop the skill into `~/.claude/skills/`

```bash
# If you used the predecessor scao7/autolecture-skill, remove the
# old folder first to avoid two copies loading:
rm -rf ~/.claude/skills/autolecture-demo

git clone https://github.com/scao7/autolecture-skill.git ~/.claude/skills/autolecture-skill
```

### 2. Install the SDK (always required)

```bash
pip install autolecture
```

That's enough for the **text-script → video** and **audio → video**
flows when you let the server transcribe the audio (the default
behavior for short clips).

### 3. (Optional) Install per-scenario extras

The skill's helper scripts only run when their use case applies, and
each guards its own dependency at runtime — so install only what you'll
use:

| Scenario | `pip install` | system binaries |
|---|---|---|
| Local Whisper (faster iteration, no upload) | `openai-whisper` | `ffmpeg` |
| PDF paper with figure callouts | `pdfplumber Pillow` | `pdftoppm` |
| GitHub repo demo (sparse-clone screenshots) | — | `git` |

System binaries come from your package manager — e.g. on Ubuntu:
`sudo apt install ffmpeg poppler-utils git` (`poppler-utils` provides
`pdftoppm`). On macOS: `brew install ffmpeg poppler git`.

### 4. Mint an API key

<https://autolecture.ai/account> → 🔑 **API Keys** → **Generate API key**.
Copy immediately — the secret is shown ONCE.

```bash
export AUTOLECTURE_API_KEY='al_live_…'
```

## Use

Open Claude Code anywhere, attach your input file, and ask:

> "做个 autolecture demo" `--include recording.mp3`
>
> "Make me an explainer video from this paper." `--include paper.pdf`

Claude reads `SKILL.md`, generates scenes, runs
`scripts/upload_and_compile.py`, and prints `out.mp4` + a Studio URL
when it's done.

## License

MIT
