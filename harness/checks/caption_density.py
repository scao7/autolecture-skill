"""\\caption density check: if `chars / view_duration` exceeds the
threshold, Whisper word-alignment cannot keep up and the caption
renders all-at-once instead of progressively rolling.

Per-view scope: only views with both a caption AND a derivable
duration (\\audio[start,end] or \\video[start,end] or view-level
duration=) are checked. Captions on TTS-only views (\\say{...} without
\\audio) cannot be pre-checked — the actual duration is set by TTS
output length at render time.
"""
from __future__ import annotations

from pathlib import Path

from ._common import (
    Finding,
    estimate_view_duration,
    find_macro_calls,
    find_main_tex,
    find_view_blocks,
    load_layout,
    read_text,
    strip_comments,
)

CHECK_NAME = "caption_density"


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout()["caption"]
    max_rate = float(cfg.get("max_chars_per_sec", 4))
    warn_rate = float(cfg.get("warn_chars_per_sec", 3))

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    for v in find_view_blocks(tex):
        captions = find_macro_calls(v.body, "caption")
        if not captions:
            continue
        dur = estimate_view_duration(v)
        if dur is None or dur <= 0:
            # Can't compute rate without a known duration — skip silently.
            continue
        for cap in captions:
            body = cap.body or ""
            n = len(body)
            rate = n / dur
            if rate > max_rate:
                findings.append(Finding(
                    check=CHECK_NAME, severity="fail",
                    file=rel, line=v.line + cap.line - 1,
                    message=(
                        f"\\caption density {rate:.1f} chars/sec "
                        f"(>{max_rate}). Whisper align will fail — caption "
                        f"will dump on screen. Split this view into "
                        f"{int(n / max_rate / dur) + 1}+ shorter views with "
                        f"matching \\audio windows."
                    ),
                    meta={"chars": n, "duration": dur, "rate": round(rate, 2),
                          "limit": max_rate},
                ))
            elif rate > warn_rate:
                findings.append(Finding(
                    check=CHECK_NAME, severity="warn",
                    file=rel, line=v.line + cap.line - 1,
                    message=(
                        f"\\caption density {rate:.1f} chars/sec "
                        f"(>{warn_rate}, under hard {max_rate}). May drift."
                    ),
                    meta={"chars": n, "duration": dur, "rate": round(rate, 2)},
                ))
    return findings
