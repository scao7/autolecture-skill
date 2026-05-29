"""Every file path referenced by `\\manimFile{}` / `\\htmlFile{}` /
`\\remotionFile{}` / `\\imageFile{}` / `\\audio{}` / `\\video{}` must
exist in the work dir. Absorbs the validation that lived inline in
`scripts/package_zip.py` so both the zip and SDK paths get the same
check.
"""
from __future__ import annotations

from pathlib import Path

from ._common import (
    Finding,
    find_macro_calls,
    find_main_tex,
    read_text,
    strip_comments,
)

CHECK_NAME = "asset_references"

# Macros whose body is a path relative to the work dir.
_PATH_MACROS = (
    "manimFile", "htmlFile", "remotionFile", "imageFile",
    "audio", "video",
)


def run(workdir: Path) -> list[Finding]:
    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    for macro in _PATH_MACROS:
        for call in find_macro_calls(tex, macro):
            path = (call.body or "").strip()
            if not path:
                continue
            abs_path = workdir / path
            if not abs_path.is_file():
                findings.append(Finding(
                    check=CHECK_NAME, severity="fail",
                    file=rel, line=call.line,
                    message=(
                        f"\\{macro}{{{path}}} references a file that doesn't "
                        f"exist in the work dir. Either create it or fix "
                        f"the path."
                    ),
                    meta={"macro": macro, "missing": path, "span": call.span},
                ))
    return findings
