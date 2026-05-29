"""L3 layout check: open every `\\htmlFile{}` scene in Playwright at the
project canvas size, compute getBoundingClientRect for every visible
element, and flag elements whose rectangle escapes the viewport.

Catches the "HTML/SVG 出屏" pain point — Claude writes `top: 920px` on a
720-tall canvas → element renders off-screen.

Tolerance: a few-pixel anti-aliasing slack (`overflow_px_tolerance`)
because borders sometimes show subpixel bleed at the canvas edge.
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
from ._render_helper import get_bboxes, project_canvas

CHECK_NAME = "html_overflow_render"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("html_render", {})
    tol = int(cfg.get("overflow_px_tolerance", 2))

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel_tex = main.relative_to(workdir).as_posix()
    canvas_w, canvas_h = project_canvas(workdir)

    # Every \htmlFile{path} in main.tex
    for call in find_macro_calls(tex, "htmlFile"):
        scene_rel = (call.body or "").strip()
        if not scene_rel:
            continue
        scene_abs = workdir / scene_rel
        if not scene_abs.is_file():
            # asset_references will flag missing files; skip here.
            continue

        bboxes = get_bboxes(scene_abs, canvas_w, canvas_h)
        if bboxes is None:
            # Playwright unavailable / probe failed — graceful skip with
            # a single info-level note (not per-scene).
            findings.append(Finding(
                check=CHECK_NAME, severity="warn",
                file=scene_rel, line=None,
                message=(
                    "Playwright render probe unavailable — html_overflow_render "
                    "skipped. Static checks still ran. Install/repair Playwright "
                    "in the comfyui env to enable: `conda run -n comfyui "
                    "playwright install chromium`."
                ),
                meta={"scene": scene_rel, "canvas": [canvas_w, canvas_h]},
            ))
            continue

        for el in bboxes:
            x, y, w, h = el["x"], el["y"], el["w"], el["h"]
            rights = []
            if x + w > canvas_w + tol:
                rights.append(("right", int(x + w - canvas_w)))
            if y + h > canvas_h + tol:
                rights.append(("bottom", int(y + h - canvas_h)))
            if x < -tol:
                rights.append(("left", int(-x)))
            if y < -tol:
                rights.append(("top", int(-y)))
            if not rights:
                continue
            edges = ", ".join(f"{edge} by {px}px" for edge, px in rights)
            tag = el.get("tag", "?")
            ident = el.get("id") or el.get("classes") or ""
            text_preview = el.get("text", "")
            label_parts = [f"<{tag}>"]
            if ident:
                label_parts.append(f".{ident}" if not ident.startswith("#") else ident)
            if text_preview:
                label_parts.append(f'"{text_preview[:30]}"')
            label = " ".join(label_parts)
            findings.append(Finding(
                check=CHECK_NAME, severity="fail",
                file=scene_rel, line=None,
                message=(
                    f"{label} escapes canvas {canvas_w}×{canvas_h}: "
                    f"out at {edges}. Bbox @ ({int(x)}, {int(y)}) "
                    f"size {int(w)}×{int(h)}. Move it inside the safe zone "
                    f"or shrink it."
                ),
                meta={
                    "scene": scene_rel,
                    "canvas": [canvas_w, canvas_h],
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "overflow": rights,
                    "tag": tag, "id": el.get("id"),
                    "classes": el.get("classes"),
                    "text_preview": text_preview,
                    "manim_view_line": call.line,
                },
            ))
    return findings
