"""Backend `\\text{}` was retired 2026-05-21 (use `\\caption{}`). Parser
still accepts it (warn-only) for back-compat. The skill considers this
a hard error — emit the modern primitive.

Also catches `\\say[mute=true]{...}` — deprecated caption-only \\say;
use `\\caption{...}` instead.
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

CHECK_NAME = "retired_macros"


def run(workdir: Path) -> list[Finding]:
    layout = load_layout()
    retired = layout.get("retired_macros", [])
    deprecated_opts = layout.get("deprecated_opts", [])

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    # Retired macros — flat-out forbidden in skill output.
    for entry in retired:
        macro = entry["macro"]
        replacement = entry.get("replacement", "(see backend spec)")
        since = entry.get("since", "")
        for call in find_macro_calls(tex, macro):
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=rel, line=call.line,
                message=(
                    f"\\{macro}{{...}} retired{f' {since}' if since else ''}. "
                    f"Replacement: {replacement}"
                ),
                fixer=None,
                meta={"macro": macro, "replacement": replacement,
                      "span": call.span},
            ))

    # Deprecated opts on otherwise-valid macros.
    for entry in deprecated_opts:
        macro = entry["macro"]
        bad_opt = entry["opt"]
        replacement = entry.get("replacement", "(see backend spec)")
        reason = entry.get("reason", "")
        for call in find_macro_calls(tex, macro):
            if call.has_opt(bad_opt):
                findings.append(Finding(
                    check=CHECK_NAME, severity="fail",
                    file=rel, line=call.line,
                    message=(
                        f"\\{macro}[{bad_opt}=...] deprecated. {reason} "
                        f"Replacement: {replacement}"
                    ),
                    fixer=None,
                    meta={"macro": macro, "opt": bad_opt,
                          "replacement": replacement, "span": call.span},
                ))
    return findings
