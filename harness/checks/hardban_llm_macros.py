"""Skill HARD BAN #1: prompt-form LLM macros (`\\manim{prompt}` /
`\\html{prompt}` / `\\remotion{prompt}` / `\\show{}`) are forbidden.

Backend still accepts these (they're how the web UI's natural-language
draft path works) but the skill demands hand-written file variants
(`\\manimFile` / `\\htmlFile` / `\\remotionFile`) because LLM codegen is
unstable, hard to cache-debug, and inflates compile time.

Distinguishing prompt-form vs file-form: file-form is referenced
exclusively via the `*File` macro variant. So `\\manim{...}` is ALWAYS
prompt-form (the file variant is `\\manimFile{...}`).
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

CHECK_NAME = "hardban_llm_macros"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("forbidden_macros", [])
    if not cfg:
        return []
    forbidden_names = [entry["macro"] for entry in cfg]
    reason_by_name = {entry["macro"]: entry.get("reason", "forbidden by skill")
                      for entry in cfg}

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    for name in forbidden_names:
        for call in find_macro_calls(tex, name):
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=rel, line=call.line,
                message=(
                    f"\\{name}{{...}} forbidden (HARD BAN #1). "
                    f"{reason_by_name[name]}"
                ),
                fixer=None,
                meta={"macro": name, "body": (call.body or "")[:80],
                      "span": call.span},
            ))
    return findings
