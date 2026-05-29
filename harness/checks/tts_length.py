"""`\say{body}` length check — DashScope CosyVoice WebSocket synth rejects
overly long requests with cryptic mid-stream errors. Limit per
`harness/spec/layout.yml::say.max_chars`.

Suggests the `split_long_say` fixer when failing.
"""
from __future__ import annotations

from pathlib import Path

from ._common import (
    Finding,
    find_macro_calls,
    find_main_tex,
    load_layout,
    read_text,
    strip_comments,
)

CHECK_NAME = "tts_length"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout()["say"]
    max_chars = int(cfg.get("max_chars", 600))
    warn_chars = int(cfg.get("warn_chars", 400))

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    for call in find_macro_calls(tex, "say"):
        body = call.body or ""
        n = len(body)
        if n > max_chars:
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=rel, line=call.line,
                message=(
                    f"\\say body is {n} chars (limit {max_chars}). DashScope "
                    f"CosyVoice rejects this. Split into shorter \\say views, "
                    f"each ≤ {max_chars} chars, with matching \\audio windows."
                ),
                fixer="split_long_say",
                meta={"chars": n, "limit": max_chars, "span": call.span},
            ))
        elif n > warn_chars:
            findings.append(Finding(
                check=CHECK_NAME, severity="warn",
                file=rel, line=call.line,
                message=(
                    f"\\say body is {n} chars (>warn threshold {warn_chars}). "
                    f"Still under hard limit ({max_chars}) but worth splitting."
                ),
                fixer="split_long_say",
                meta={"chars": n, "warn": warn_chars, "span": call.span},
            ))
    return findings
