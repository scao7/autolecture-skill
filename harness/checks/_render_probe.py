"""Standalone Playwright bbox extractor — run as a subprocess in the
comfyui env (`conda run -n comfyui python -m harness.checks._render_probe ...`).

Why a subprocess: Playwright is installed in the comfyui conda env (the
backend already uses it for `\htmlFile{}` rendering). The harness's main
process runs under base anaconda where Playwright isn't installed. Rather
than copy Playwright across envs, we shell out: the helper script
(_render_helper.py) invokes this probe via conda-run + reads JSON from
stdout.

Usage:
    python -m harness.checks._render_probe <html_path> <canvas_w> <canvas_h>

Output (stdout, JSON):
    {
        "ok": true,
        "elements": [
            {tag, id, classes, x, y, w, h, text, has_text_node, visible},
            ...
        ]
    }

On failure: prints {"ok": false, "error": "..."} and exits non-zero.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


# Walk every element and emit its bbox + textContent. We do this in one
# page.evaluate() pass so we don't pay round-trip cost per element.
_BBOX_JS = """
() => {
  const elems = Array.from(document.querySelectorAll('*'));
  const out = [];
  for (const el of elems) {
    if (el.tagName === 'HTML' || el.tagName === 'BODY' ||
        el.tagName === 'STYLE' || el.tagName === 'SCRIPT' ||
        el.tagName === 'HEAD' || el.tagName === 'META' ||
        el.tagName === 'LINK' || el.tagName === 'TITLE') continue;
    const cs = window.getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') continue;
    if (parseFloat(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    // skip zero-area elements (they have no visible footprint).
    if (r.width < 1 || r.height < 1) continue;
    // Direct text node child? (not just descendant text — we want the
    // element that ACTUALLY contains a text node, so overlap check
    // doesn't false-positive on a wrapper around two text spans.)
    let hasOwnText = false;
    for (const node of el.childNodes) {
      if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
        hasOwnText = true;
        break;
      }
    }
    out.push({
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: el.className || null,
      x: r.x, y: r.y, w: r.width, h: r.height,
      text: (el.textContent || '').trim().slice(0, 80),
      has_text_node: hasOwnText,
      z_index: cs.zIndex === 'auto' ? 0 : (parseInt(cs.zIndex, 10) || 0),
    });
  }
  return out;
}
"""


def probe(html_path: Path, canvas_w: int, canvas_h: int) -> dict:
    """Open `html_path` in headless Chromium at the given viewport,
    return list of element bboxes via getBoundingClientRect()."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return {"ok": False, "error": f"playwright not importable in this env: {e}"}

    url = html_path.resolve().as_uri()  # file:///abs/path

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": canvas_w, "height": canvas_h})
            page.goto(url, wait_until="domcontentloaded")
            # Give CSS keyframe entrance animations a chance to settle.
            # The skill's HTML templates finish entrance in <2s; sample
            # at 2s so the rendered state is the "settled" frame.
            page.wait_for_timeout(2000)
            elements = page.evaluate(_BBOX_JS)
            return {"ok": True, "elements": elements,
                    "canvas": {"w": canvas_w, "h": canvas_h}}
        finally:
            browser.close()


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if len(argv) != 3:
        print(json.dumps({"ok": False,
                          "error": "usage: <html_path> <canvas_w> <canvas_h>"}),
              file=sys.stderr)
        return 2
    html_path = Path(argv[0])
    if not html_path.is_file():
        print(json.dumps({"ok": False,
                          "error": f"html not found: {html_path}"}))
        return 2
    try:
        canvas_w = int(argv[1])
        canvas_h = int(argv[2])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": f"bad canvas dim: {e}"}))
        return 2

    result = probe(html_path, canvas_w, canvas_h)
    print(json.dumps(result))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
