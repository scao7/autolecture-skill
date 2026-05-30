"""Shared helpers for harness checks: spec loader, .tex macro parser, finding type.

The parser is a hand-rolled brace-balanced tokenizer (pylatexenc would be
heavier and overkill for the macro shapes the skill emits). It handles:

    \name              — no opts, no body
    \name{body}        — body with balanced braces (nested OK)
    \name[opts]{body}  — opts as `key=value, key=value, ...`
    \name[opts]        — opts only, no body (rare)

It does NOT handle: free-floating `[opts]` not attached to a macro, or
comments — those are filtered out by a `_strip_comments` pre-pass.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Re-used path constants. Both checks and fixers need them.
_HARNESS_DIR = Path(__file__).resolve().parent.parent
_SPEC_DIR = _HARNESS_DIR / "spec"


# ─── Spec loader ──────────────────────────────────────────────────

_layout_cache: dict | None = None
_dsl_cache: dict | None = None


def load_layout() -> dict:
    """Read harness/spec/layout.yml. Yaml because it's human-edited."""
    global _layout_cache
    if _layout_cache is not None:
        return _layout_cache
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            "harness requires PyYAML. Install: pip install pyyaml"
        ) from e
    _layout_cache = yaml.safe_load((_SPEC_DIR / "layout.yml").read_text("utf-8"))
    return _layout_cache


def load_dsl() -> dict:
    """Read harness/spec/dsl.json (backend VideoTeX surface snapshot)."""
    global _dsl_cache
    if _dsl_cache is not None:
        return _dsl_cache
    _dsl_cache = json.loads((_SPEC_DIR / "dsl.json").read_text("utf-8"))
    return _dsl_cache


# ─── Finding type ─────────────────────────────────────────────────

# Severity: "fail" (blocks delivery) vs "warn" (surface but don't block).
# Checks set this; check.py / fix.py drive flow based on it.

@dataclass
class Finding:
    check: str                        # e.g. "tts_length"
    severity: str                     # "fail" | "warn"
    file: str                         # relative to workdir, e.g. "main.tex"
    line: int | None = None           # 1-indexed; None if not localizable
    message: str = ""
    fixer: str | None = None          # name of an autofix to suggest
    meta: dict[str, Any] = field(default_factory=dict)  # check-specific extras

    def to_dict(self) -> dict:
        return {
            "check": self.check, "severity": self.severity,
            "file": self.file, "line": self.line,
            "message": self.message, "fixer": self.fixer,
            "meta": self.meta,
        }


# ─── .tex parser ──────────────────────────────────────────────────

_COMMENT_RE = re.compile(r"(?<!\\)%[^\n]*")


def strip_comments(tex: str) -> str:
    """Drop LaTeX `%`-to-EOL comments (but keep escaped `\\%`)."""
    return _COMMENT_RE.sub("", tex)


@dataclass
class MacroCall:
    name: str
    opts: dict[str, str]              # parsed [key=value, key=value, ...]
    body: str | None                  # raw {body} content; None if no body
    line: int                         # 1-indexed source line
    col: int                          # 1-indexed source column
    span: tuple[int, int]             # (start_offset, end_offset) into the source

    def has_opt(self, key: str) -> bool:
        return key in self.opts

    def opt(self, key: str, default: str | None = None) -> str | None:
        return self.opts.get(key, default)


def _line_col(text: str, offset: int) -> tuple[int, int]:
    """1-indexed line, col for the offset."""
    line = text.count("\n", 0, offset) + 1
    last_nl = text.rfind("\n", 0, offset)
    col = offset - last_nl
    return line, col


def _find_matching_brace(text: str, open_offset: int, open_ch: str, close_ch: str) -> int | None:
    """Find the offset of the closing brace that matches the one at
    `open_offset`. Handles nested braces. Returns offset of close char,
    or None if unbalanced. Skips escaped braces (`\\{` `\\}`)."""
    assert text[open_offset] == open_ch
    depth = 1
    i = open_offset + 1
    n = len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            i += 2  # skip escape sequence
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def _parse_opts(opts_text: str) -> dict[str, str]:
    """Parse `key=value, key=value, foo` into a dict. Bare keys → value="".
    Doesn't try to be a full LaTeX kvoptions parser — the skill's opts are
    all simple identifiers + scalar values, no nested braces in opts."""
    out: dict[str, str] = {}
    for piece in opts_text.split(","):
        piece = piece.strip()
        if not piece:
            continue
        if "=" in piece:
            k, v = piece.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[piece] = ""
    return out


def find_macro_calls(tex: str, macro_name: str) -> list[MacroCall]:
    """Find all `\macro_name` calls in `tex`. Captures optional `[opts]` and
    optional `{body}` (with balanced-brace nesting).

    `tex` should be the comment-stripped source (call `strip_comments` first
    if you got it from disk). The returned MacroCall.line is 1-indexed
    against the comment-stripped string — for source-line accuracy on
    files where comments matter, pass the original tex and accept that
    line numbers are approximate.
    """
    out: list[MacroCall] = []
    # \name not followed by an alphanumeric (avoid matching \say in \saying).
    pattern = re.compile(rf"\\{re.escape(macro_name)}(?![A-Za-z0-9])")
    n = len(tex)
    for m in pattern.finditer(tex):
        start = m.start()
        cursor = m.end()
        opts: dict[str, str] = {}
        body: str | None = None

        # Optional [opts]
        if cursor < n and tex[cursor] == "[":
            close = _find_matching_brace(tex, cursor, "[", "]")
            if close is None:
                continue
            opts = _parse_opts(tex[cursor + 1 : close])
            cursor = close + 1

        # Optional {body}
        if cursor < n and tex[cursor] == "{":
            close = _find_matching_brace(tex, cursor, "{", "}")
            if close is None:
                continue
            body = tex[cursor + 1 : close]
            cursor = close + 1

        line, col = _line_col(tex, start)
        out.append(MacroCall(
            name=macro_name, opts=opts, body=body,
            line=line, col=col, span=(start, cursor),
        ))
    return out


# ─── Project walker (for checks that need to enumerate scene files) ──

def find_main_tex(workdir: Path) -> Path:
    """Pick the main .tex file (the project's entry tex)."""
    for name in ("main.tex", "index.tex", "video.tex", "script.tex"):
        p = workdir / name
        if p.is_file():
            return p
    txs = sorted(workdir.glob("*.tex"))
    if txs:
        return txs[0]
    txs = sorted(workdir.rglob("*.tex"))
    if txs:
        return txs[0]
    raise FileNotFoundError(f"no .tex in {workdir}")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


# ─── View extraction (rough — for caption_density / per-view checks) ──

_VIEW_BLOCK_RE = re.compile(
    r"\\begin\{view\}(\[[^\]]*\])?(.*?)\\end\{view\}",
    re.DOTALL,
)


@dataclass
class ViewBlock:
    opts: dict[str, str]
    body: str
    line: int
    span: tuple[int, int]


def find_view_blocks(tex: str) -> list[ViewBlock]:
    """Locate all `\\begin{view}[opts]...\\end{view}` blocks."""
    out: list[ViewBlock] = []
    for m in _VIEW_BLOCK_RE.finditer(tex):
        opts_raw = m.group(1) or ""
        if opts_raw.startswith("[") and opts_raw.endswith("]"):
            opts = _parse_opts(opts_raw[1:-1])
        else:
            opts = {}
        line, _ = _line_col(tex, m.start())
        out.append(ViewBlock(
            opts=opts, body=m.group(2),
            line=line, span=(m.start(), m.end()),
        ))
    return out


def estimate_view_duration(view: ViewBlock) -> float | None:
    """Best-effort: derive a view's audio-driven duration from its
    `\\audio[start=,end=]` / `\\video[start=,end=]` layers, or its explicit
    `duration=` opt. Returns seconds, or None if unknown.

    Audio-first means: the view length = the audio's window length.
    For \\say-only views without an \\audio file (TTS-only), we have no
    pre-render guess — return None so per-view checks know to skip.
    """
    # Explicit view-level duration= (rare but supported)
    if "duration" in view.opts:
        try:
            return float(view.opts["duration"])
        except ValueError:
            pass
    # Audio/video window
    for macro in ("audio", "video"):
        for call in find_macro_calls(view.body, macro):
            s = call.opt("start")
            e = call.opt("end")
            if s is not None and e is not None:
                try:
                    return max(0.0, float(e) - float(s))
                except ValueError:
                    continue
    return None
