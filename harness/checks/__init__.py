"""Check registry. Each check is a module with a `run(workdir: Path) ->
list[Finding]` function. Register here so check.py can iterate."""
from __future__ import annotations

from . import (
    asset_references,
    caption_density,
    hardban_llm_macros,
    html_overflow_render,
    html_text_overlap,
    manimfile_retime,
    overlay_transparent_root,
    retired_macros,
    tts_length,
    voice_clone_consistency,
)

# Ordering note: L1 (static) checks run first so they fail fast on cheap
# violations. L3 (render-based) checks run last because they're the
# slowest (~2s per scene Playwright session).
ALL_CHECKS = [
    # L1 — static / text-only
    tts_length,
    manimfile_retime,
    hardban_llm_macros,
    retired_macros,
    caption_density,
    asset_references,
    overlay_transparent_root,
    voice_clone_consistency,
    # L3 — Playwright local-render (skipped gracefully if comfyui env
    # unavailable; the per-scene WARN surfaces the skip).
    html_overflow_render,
    html_text_overlap,
]
