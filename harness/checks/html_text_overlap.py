"""L3 layout check: text-element overlap detection.

For every `\\htmlFile{}` scene, fetch bboxes (reuses the cached Playwright
session from html_overflow_render) and check pairwise intersections
between elements that carry their OWN text node (not just descendant
text — we want the actual painted letters, not their wrapper). If
intersection_area / smaller_bbox_area exceeds `overlap_pct`, flag.

Catches the "文字和动画重叠" pain point — two absolutely-positioned text
spans rendering at the same screen region.
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

CHECK_NAME = "html_text_overlap"


def _rect_intersection_area(a: dict, b: dict) -> float:
    """Axis-aligned-rectangle intersection area in px²."""
    ax1, ay1 = a["x"], a["y"]
    ax2, ay2 = ax1 + a["w"], ay1 + a["h"]
    bx1, by1 = b["x"], b["y"]
    bx2, by2 = bx1 + b["w"], by1 + b["h"]
    iw = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    ih = max(0.0, min(ay2, by2) - max(ay1, by1))
    return iw * ih


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("html_render", {})
    overlap_pct_threshold = float(cfg.get("text_overlap_pct", 30)) / 100.0

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    canvas_w, canvas_h = project_canvas(workdir)

    for call in find_macro_calls(tex, "htmlFile"):
        scene_rel = (call.body or "").strip()
        if not scene_rel:
            continue
        scene_abs = workdir / scene_rel
        if not scene_abs.is_file():
            continue

        bboxes = get_bboxes(scene_abs, canvas_w, canvas_h)
        if bboxes is None:
            # html_overflow_render already emitted the "Playwright
            # unavailable" warn — don't repeat it here.
            continue

        # Filter to elements that paint actual text (own text node).
        text_elems = [el for el in bboxes if el.get("has_text_node")
                       and el.get("text", "").strip()]
        if len(text_elems) < 2:
            continue

        # Pairwise. O(n²) but n is small (handful of text spans per scene).
        seen_pairs: set[tuple[int, int]] = set()
        for i, a in enumerate(text_elems):
            for j, b in enumerate(text_elems):
                if j <= i:
                    continue
                # Different z_index → may be intentionally layered. Don't
                # flag (this is how a text-on-card design works).
                if a.get("z_index") != b.get("z_index"):
                    continue
                inter = _rect_intersection_area(a, b)
                if inter == 0:
                    continue
                smaller = min(a["w"] * a["h"], b["w"] * b["h"])
                if smaller == 0:
                    continue
                frac = inter / smaller
                if frac < overlap_pct_threshold:
                    continue
                if (i, j) in seen_pairs:
                    continue
                seen_pairs.add((i, j))
                ta = a.get("text", "")[:30]
                tb = b.get("text", "")[:30]
                findings.append(Finding(
                    check=CHECK_NAME, severity="fail",
                    file=scene_rel, line=None,
                    message=(
                        f"text '{ta}' overlaps text '{tb}' by {frac*100:.0f}% "
                        f"(>{overlap_pct_threshold*100:.0f}% threshold). "
                        f"Same z-index — move one element, change z-index "
                        f"on purpose, or shrink one of them."
                    ),
                    meta={
                        "scene": scene_rel,
                        "overlap_frac": round(frac, 3),
                        "a_bbox": [int(a["x"]), int(a["y"]),
                                   int(a["w"]), int(a["h"])],
                        "b_bbox": [int(b["x"]), int(b["y"]),
                                   int(b["w"]), int(b["h"])],
                        "a_text": ta, "b_text": tb,
                    },
                ))
    return findings
