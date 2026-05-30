"""\\say{} consistency check for voice-clone usage.

CONSISTENCY-ONLY: if the project has ANY \\say with [voice=mine], ALL
\\say in the project should have it — mixing is almost always a typo.

The harness is fully offline and mode-independent: it does NOT query the
backend for whether the user has a registered voice sample. Whether a
sample actually exists is resolved at compile time (by the MCP server in
mcp mode, or the web UI in zip mode), not by the skill's local checks. So
this check never proactively fails — it only flags an inconsistency as a
warning.
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

CHECK_NAME = "voice_clone_consistency"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("voice_clone", {})
    if not cfg.get("enforce_when_sample_registered", True):
        return []

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    say_calls = find_macro_calls(tex, "say")
    if not say_calls:
        return []

    with_voice_mine = [c for c in say_calls if c.opt("voice") == "mine"]
    without_voice_mine = [c for c in say_calls if c.opt("voice") != "mine"]

    # A project that mixes voice=mine and plain \\say is almost always a
    # typo. Warn (never hard-fail).
    if with_voice_mine and without_voice_mine:
        for call in without_voice_mine:
            findings.append(Finding(
                check=CHECK_NAME, severity="warn",
                file=rel, line=call.line,
                message=(
                    f"This \\say lacks [voice=mine] but {len(with_voice_mine)} "
                    f"other \\say in this project have it. Mixing is almost "
                    f"always a typo — either add [voice=mine] to this one or "
                    f"remove it from the others."
                ),
                fixer="add_voice_clone",
                meta={"consistency_only": True, "span": call.span},
            ))
    return findings
