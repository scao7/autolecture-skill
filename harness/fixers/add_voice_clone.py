"""Auto-fixer for `voice_clone_consistency`: add `voice=mine` to every
`\\say{}` that lacks it.

In-place rewrite. Idempotent (won't double-add).
"""
from __future__ import annotations

import re
from pathlib import Path

from ..checks._common import (
    find_macro_calls,
    find_main_tex,
    read_text,
)

FIXER_NAME = "add_voice_clone"


def apply(workdir: Path, dry_run: bool = True) -> list[dict]:
    """Apply the fixer. Returns a list of edit-records (one per edited
    macro call) for the caller to report.

    If `dry_run`, no file is modified — record still emitted so the
    caller can preview.
    """
    main = find_main_tex(workdir)
    src = read_text(main)
    rel = main.relative_to(workdir).as_posix()

    # Find every \say without voice=mine. We re-find on the LIVE buffer
    # because each rewrite shifts the spans of later calls.
    edits: list[dict] = []
    buf = src
    while True:
        calls = [c for c in find_macro_calls(buf, "say")
                 if c.opt("voice") != "mine"]
        if not calls:
            break
        # Take the FIRST one each pass, rewrite, re-find. O(n) passes but
        # each is O(file size); fine for skill output (few hundred lines).
        call = calls[0]
        start, end = call.span
        original = buf[start:end]
        rewritten = _add_voice_mine_to_call(original, call.opts)
        if rewritten == original:
            # Defensive: avoid infinite loop if the rewrite somehow no-ops.
            break
        buf = buf[:start] + rewritten + buf[end:]
        edits.append({
            "file": rel,
            "line": call.line,
            "before": original[:60] + ("…" if len(original) > 60 else ""),
            "after":  rewritten[:60] + ("…" if len(rewritten) > 60 else ""),
        })

    if edits and not dry_run:
        main.write_text(buf, encoding="utf-8")
    return edits


def _add_voice_mine_to_call(call_src: str, existing_opts: dict[str, str]) -> str:
    """Given the source text of a single `\\say[…]{…}` (or `\\say{…}`),
    return the same with `voice=mine` injected into the opts."""
    # If there's already an [opts] block, splice voice=mine into it.
    if call_src.startswith("\\say[") or "[" in call_src.split("{", 1)[0]:
        # Find the opts brackets via re — same surface the parser used.
        m = re.match(r"(\\say)\[([^\]]*)\](.*)", call_src, re.DOTALL)
        if not m:
            return call_src  # malformed; bail
        head, opts_text, tail = m.group(1), m.group(2), m.group(3)
        opts_text = opts_text.strip()
        if opts_text:
            new_opts = f"voice=mine, {opts_text}"
        else:
            new_opts = "voice=mine"
        return f"{head}[{new_opts}]{tail}"
    # No [opts] block — insert one.
    return call_src.replace("\\say{", "\\say[voice=mine]{", 1)
