"""Invokes _render_probe.py inside the comfyui conda env via subprocess,
parses JSON output, caches per (html_path, canvas_w, canvas_h) so the
overflow check and the overlap check share one Playwright session per
scene file instead of paying ~2s twice.

The subprocess hop is needed because Playwright lives in the comfyui
env (same place the backend renders HTML scenes) while the harness's
top-level Python may not have it. If the in-process import works, we
skip the subprocess for speed; otherwise we shell out.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


# Per-session cache: (abs_path, w, h) → list of bbox dicts.
# Reset only between harness invocations (process restart).
_BBOX_CACHE: dict[tuple[str, int, int], list[dict[str, Any]] | None] = {}


def _try_in_process(html_path: Path, w: int, h: int) -> dict | None:
    """Fast path: if Playwright is available in this process, use it.

    Returns None — meaning "fall through to subprocess" — when Playwright
    isn't installed in THIS interpreter. The probe() helper catches that
    ImportError internally and returns an error dict, so we detect it by
    inspecting the error message string."""
    try:
        from . import _render_probe  # type: ignore
    except ImportError:
        return None
    try:
        result = _render_probe.probe(html_path, w, h)
    except Exception as e:
        return {"ok": False, "error": str(e)}
    # If the probe couldn't import playwright in THIS env, fall through
    # so the subprocess path gets a try with comfyui's Python.
    if not result.get("ok"):
        err = (result.get("error") or "").lower()
        if "playwright" in err and "not importable" in err:
            return None
    return result


def _conda_run_probe(html_path: Path, w: int, h: int,
                      env_name: str = "comfyui") -> dict:
    """Shell out to `conda run -n <env>` and invoke the probe."""
    # Locate conda binary. Prefer ~/anaconda3/bin/conda; fall back to PATH.
    conda = (
        os.path.expanduser("~/anaconda3/bin/conda")
        if os.path.isfile(os.path.expanduser("~/anaconda3/bin/conda"))
        else shutil.which("conda")
    )
    if conda is None:
        return {"ok": False, "error": "conda not found on PATH"}

    cmd = [
        conda, "run", "-n", env_name, "--no-capture-output",
        "python", "-m", "harness.checks._render_probe",
        str(html_path), str(w), str(h),
    ]
    # Run from the repo root so `python -m harness.checks._render_probe`
    # resolves. The repo root is two levels up from this file.
    repo_root = Path(__file__).resolve().parent.parent.parent
    try:
        r = subprocess.run(
            cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "render probe timed out (60s)"}

    if r.returncode != 0 and not r.stdout.strip():
        return {"ok": False,
                "error": f"render probe failed (rc={r.returncode}): "
                          f"{r.stderr.strip()[:300]}"}

    # The probe prints exactly one JSON line to stdout (success or failure).
    line = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    try:
        return json.loads(line)
    except json.JSONDecodeError as e:
        return {"ok": False,
                "error": f"render probe stdout was not JSON: {e}; "
                          f"raw={r.stdout[:200]!r} stderr={r.stderr[:200]!r}"}


def get_bboxes(html_path: Path, canvas_w: int, canvas_h: int) -> list[dict[str, Any]] | None:
    """Return list of bboxes for every visible element in `html_path` at
    the given viewport, or None if Playwright unavailable in any
    accessible env. Caller decides how to handle None (warn + skip vs
    hard fail).

    Cached per (path, w, h) for the current process lifetime.
    """
    key = (str(html_path.resolve()), canvas_w, canvas_h)
    if key in _BBOX_CACHE:
        return _BBOX_CACHE[key]

    # Try in-process first.
    result = _try_in_process(html_path, canvas_w, canvas_h)
    if result is None:
        # Playwright not importable here — shell out to comfyui.
        result = _conda_run_probe(html_path, canvas_w, canvas_h)

    if not result.get("ok"):
        # Cache None so we don't keep retrying for the same file in this
        # process. Caller will see None and emit a graceful skip.
        print(f"[harness] _render_helper: probe failed for {html_path}: "
              f"{result.get('error')}", file=sys.stderr)
        _BBOX_CACHE[key] = None
        return None

    _BBOX_CACHE[key] = result["elements"]
    return _BBOX_CACHE[key]


# ─── Canvas resolution from main.tex ──────────────────────────────

def canvas_dims_for_aspect(aspect: str) -> tuple[int, int]:
    """Map \\aspect{} body to (w, h) — mirrors backend's
    aspect_to_canvas() at compiler.py:1011. Falls back to 16:9 default
    when the aspect is unrecognized (so the check still runs, but
    overflow numbers may be slightly off)."""
    # Snapshot of the backend table — also lives in harness/spec/layout.yml,
    # this is the static mirror.
    table = {
        "16:9":  (1280, 720),
        "9:16":  (720, 1280),
        "1:1":   (720, 720),
        "4:3":   (960, 720),
        "3:4":   (720, 960),
        "4:5":   (720, 900),
        "21:9":  (1680, 720),
    }
    return table.get(aspect.strip(), (1280, 720))


def project_canvas(workdir: Path) -> tuple[int, int]:
    """Find `\\aspect{}` in the main.tex of `workdir` and return (w, h).
    Defaults to 16:9 (1280×720) if missing."""
    from ._common import find_macro_calls, find_main_tex, read_text, strip_comments
    try:
        main = find_main_tex(workdir)
    except FileNotFoundError:
        return (1280, 720)
    tex = strip_comments(read_text(main))
    aspect_calls = find_macro_calls(tex, "aspect")
    if not aspect_calls or aspect_calls[0].body is None:
        return (1280, 720)
    return canvas_dims_for_aspect(aspect_calls[0].body)
