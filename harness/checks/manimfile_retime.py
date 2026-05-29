"""\\manimFile{} must carry [retime=true].

Backend default since 2026-05-22: \\manimFile renders source AS WRITTEN
(no time scaling). Without `[retime=true]`, hand-written Manim animation
ends at its natural duration and the compositor freeze-trims to the
audio — surprising for skill output where every visual is supposed to be
audio-first scaled. Skill HARD BAN #1 mandates `[retime=true]`.
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

CHECK_NAME = "manimfile_retime"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("manimfile", {})
    if not cfg.get("require_retime_true", True):
        return []

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    for call in find_macro_calls(tex, "manimFile"):
        retime = call.opt("retime")
        if retime != "true":
            actual = "missing" if retime is None else f"retime={retime!r}"
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=rel, line=call.line,
                message=(
                    f"\\manimFile must carry [retime=true]; got {actual}. "
                    f"Without it, the .py renders at source-natural speed "
                    f"and compositor hold/trim-fits (HARD BAN #1, see "
                    f"reference/audio-first.md)."
                ),
                fixer=None,  # not auto-fixed yet — the right move is for
                             # Claude to add [retime=true] in the same edit
                             # (low cost), keeps a human-in-loop on Manim
                meta={"current": retime, "expected": "true", "span": call.span},
            ))
    return findings
