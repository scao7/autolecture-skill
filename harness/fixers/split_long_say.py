"""Auto-fixer for `tts_length`: split overly-long `\\say{body}` calls
into multiple shorter ones along sentence boundaries.

⚠️ This is the more invasive of the two fixers. The naive split (just
chunking text) yields multiple `\\say{}` macros INSIDE THE SAME VIEW,
which DOES work — the backend treats them as a single TTS sequence. But
it does NOT split into multiple VIEWS (= multiple visual cuts) — the
view layer is unchanged. Whether the visual should follow the sentence
split is content-dependent; this fixer leaves visual layers untouched.

If the caller wants per-sentence view splits (different visual per
sentence), that's a content decision the harness shouldn't make
automatically — emit a warning instead and let Claude / the user
restructure.

Splitting rules:
- Prefer Chinese sentence terminators: 。 ! ? ; (in body order)
- Then English: . ! ? ;
- Break before each terminator at chunk size ≤ max_chars
- Preserve opts (voice/burn/etc.) on EACH new \\say
- If body has no sentence terminator, return original unchanged (no
  good place to split — surface as warning, user must restructure)
"""
from __future__ import annotations

import re
from pathlib import Path

from ..checks._common import (
    find_macro_calls,
    find_main_tex,
    load_layout,
    read_text,
)

FIXER_NAME = "split_long_say"

_SENTENCE_END = re.compile(r"([。!?;.!?;])")


def _chunk_at_sentences(text: str, limit: int) -> list[str]:
    """Greedy chunk: walk sentence terminators, start a new chunk when
    adding the next sentence would exceed `limit`. Each chunk ≤ limit."""
    # Tokenize into (sentence, terminator) pairs.
    parts = _SENTENCE_END.split(text)
    sentences: list[str] = []
    cur = ""
    for piece in parts:
        cur += piece
        if _SENTENCE_END.fullmatch(piece):
            sentences.append(cur)
            cur = ""
    if cur:
        sentences.append(cur)
    if not sentences:
        return [text]

    chunks: list[str] = []
    buf = ""
    for s in sentences:
        if len(buf) + len(s) <= limit or not buf:
            buf += s
        else:
            chunks.append(buf)
            buf = s
    if buf:
        chunks.append(buf)
    return chunks


def _rewrite_call(call_src: str, opts_text: str, chunks: list[str]) -> str:
    """Emit N copies of `\\say[opts]{chunk_i}` joined by \n."""
    if opts_text:
        head = f"\\say[{opts_text}]"
    else:
        head = "\\say"
    return "\n".join(f"{head}{{{c}}}" for c in chunks)


def apply(workdir: Path, dry_run: bool = True) -> list[dict]:
    max_chars = int(load_layout()["say"]["max_chars"])

    main = find_main_tex(workdir)
    src = read_text(main)
    rel = main.relative_to(workdir).as_posix()

    edits: list[dict] = []
    buf = src
    while True:
        calls = [c for c in find_macro_calls(buf, "say")
                 if c.body and len(c.body) > max_chars]
        if not calls:
            break
        call = calls[0]
        body = call.body or ""
        chunks = _chunk_at_sentences(body, max_chars)
        if len(chunks) <= 1:
            # No sentence terminator + body still too long — can't auto-split.
            # Emit a non-edit record so the caller knows.
            edits.append({
                "file": rel, "line": call.line,
                "skipped": True,
                "reason": "no sentence terminator found; please add periods "
                          "or restructure manually",
                "chars": len(body),
            })
            # Move past this call so we don't loop forever on it. Mark
            # span as "consumed" by inserting a sentinel comment? Simpler:
            # just break — let next harness.check pass surface it as a fail.
            break
        opts_text = ", ".join(f"{k}={v}" if v else k for k, v in call.opts.items())
        start, end = call.span
        original = buf[start:end]
        rewritten = _rewrite_call(original, opts_text, chunks)
        buf = buf[:start] + rewritten + buf[end:]
        edits.append({
            "file": rel, "line": call.line,
            "before_chars": len(body),
            "split_into": len(chunks),
            "chunk_sizes": [len(c) for c in chunks],
        })

    if edits and not dry_run and not all(e.get("skipped") for e in edits):
        main.write_text(buf, encoding="utf-8")
    return edits
