"""Check registry. Each check is a module with a `run(workdir: Path) ->
list[Finding]` function. Register here so check.py can iterate."""
from __future__ import annotations

from . import (
    asset_references,
    caption_density,
    hardban_llm_macros,
    manimfile_retime,
    overlay_transparent_root,
    retired_macros,
    tts_length,
    voice_clone_consistency,
)

ALL_CHECKS = [
    tts_length,
    manimfile_retime,
    hardban_llm_macros,
    retired_macros,
    caption_density,
    asset_references,
    overlay_transparent_root,
    voice_clone_consistency,
]
