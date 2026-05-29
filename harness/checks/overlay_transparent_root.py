"""\\remotionFile[over=true]{path.tsx} must reference a scene whose root
`AbsoluteFill` has NO opaque background. Otherwise the alpha webm gets
rendered as opaque mp4 and the footage layer gets hidden — the most
common overlay bug.

Heuristic: search the .tsx for the pattern `AbsoluteFill style={{ ...
backgroundColor: ... }}`. If the value is `'transparent'`, an empty
string, or omitted entirely, pass. If it's any other color (hex / named
color / rgba with alpha=1), fail.

This is a static-source check — accurate when the root AbsoluteFill is
written inline (the way our scene_overlay.tsx.tpl template does it).
Doesn't catch indirection through a wrapper component. For those cases
the L3 Playwright check (future) would catch it via actual render.
"""
from __future__ import annotations

import re
from pathlib import Path

from ._common import (
    Finding,
    find_macro_calls,
    find_main_tex,
    read_text,
    strip_comments,
)

CHECK_NAME = "overlay_transparent_root"

# Match an AbsoluteFill JSX element with inline style + a backgroundColor
# key inside. Captures the backgroundColor value.
_ABS_FILL_BG_RE = re.compile(
    r"AbsoluteFill[^>]*?style=\{\{[^}]*?backgroundColor\s*:\s*([^,}\n]+)",
    re.DOTALL,
)

# Allowed values that DON'T paint the background opaque.
_TRANSPARENT_PATTERNS = (
    re.compile(r"^['\"]transparent['\"]$"),
    re.compile(r"^['\"]['\"]$"),                       # empty string
    re.compile(r"^['\"]rgba\([^)]*?,\s*0(\.0+)?\s*\)['\"]$"),  # rgba with alpha=0
)


def _is_transparent(value: str) -> bool:
    v = value.strip()
    return any(p.match(v) for p in _TRANSPARENT_PATTERNS)


def run(workdir: Path) -> list[Finding]:
    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    # Find all \remotionFile[over=true]{path.tsx}
    for call in find_macro_calls(tex, "remotionFile"):
        if call.opt("over") != "true":
            continue
        scene_path = (call.body or "").strip()
        if not scene_path:
            continue
        scene_abs = workdir / scene_path
        if not scene_abs.is_file():
            # asset_references will already flag missing file; skip here.
            continue

        scene_src = read_text(scene_abs)
        # Find every AbsoluteFill with a backgroundColor in style. Flag any
        # that's not transparent.
        for m in _ABS_FILL_BG_RE.finditer(scene_src):
            bg_value = m.group(1).strip().rstrip(",").strip()
            if _is_transparent(bg_value):
                continue
            line = scene_src.count("\n", 0, m.start()) + 1
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=scene_path, line=line,
                message=(
                    f"<AbsoluteFill> root has opaque backgroundColor "
                    f"({bg_value}). over=true overlays need transparent "
                    f"root — only graphic elements get backgrounds. See "
                    f"templates/scene_overlay.tsx.tpl's THREE HARD RULES."
                ),
                meta={"scene": scene_path, "bg_value": bg_value,
                      "manim_view_line": call.line},
            ))
    return findings
