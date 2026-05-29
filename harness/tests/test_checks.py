"""Pytest for the harness — each fixture has an expected set of findings."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from harness.checks import ALL_CHECKS                       # noqa: E402
from harness.fixers import FIXERS                            # noqa: E402

FIXTURES = REPO / "harness" / "fixtures"


def _findings_by_check(workdir: Path) -> dict[str, list]:
    out: dict[str, list] = {}
    for mod in ALL_CHECKS:
        out[mod.CHECK_NAME] = mod.run(workdir)
    return out


# ── good_minimal: nothing should fire ─────────────────────────────

def test_good_minimal_no_findings():
    by_check = _findings_by_check(FIXTURES / "good_minimal")
    for name, findings in by_check.items():
        # Allow info-level findings; only fail/warn are notable.
        notable = [f for f in findings if f.severity in ("fail", "warn")]
        assert not notable, (
            f"good_minimal should have no fail/warn findings, but "
            f"{name} produced: {[f.message for f in notable]}"
        )


# ── bad_say_too_long: tts_length must FAIL ───────────────────────

def test_bad_say_too_long_fires_tts_length():
    by_check = _findings_by_check(FIXTURES / "bad_say_too_long")
    findings = by_check["tts_length"]
    fails = [f for f in findings if f.severity == "fail"]
    assert fails, (
        "bad_say_too_long should produce a tts_length FAIL, got: "
        f"{[(f.severity, f.message) for f in findings]}"
    )
    # Expect the fixer hint
    assert all(f.fixer == "split_long_say" for f in fails)


def test_bad_say_too_long_split_long_say_fixer_works(tmp_path: Path):
    """End-to-end: copy fixture, run fixer with --apply, re-check."""
    import shutil
    src = FIXTURES / "bad_say_too_long"
    dst = tmp_path / "fixture"
    shutil.copytree(src, dst)

    # Apply fixer.
    edits = FIXERS["split_long_say"].apply(dst, dry_run=False)
    real_edits = [e for e in edits if not e.get("skipped")]
    assert real_edits, f"fixer should have edited something, got {edits}"

    # Re-run tts_length check on the FIXED dir; no more FAIL findings.
    from harness.checks import tts_length
    new_findings = tts_length.run(dst)
    fails = [f for f in new_findings if f.severity == "fail"]
    assert not fails, (
        f"after split_long_say --apply, tts_length should not FAIL "
        f"anymore. Got: {[f.message for f in fails]}"
    )


# ── bad_no_retime: manimfile_retime must FAIL ─────────────────────

def test_bad_no_retime_fires_manimfile_retime():
    by_check = _findings_by_check(FIXTURES / "bad_no_retime")
    findings = by_check["manimfile_retime"]
    fails = [f for f in findings if f.severity == "fail"]
    assert fails, (
        f"bad_no_retime should produce a manimfile_retime FAIL, got: "
        f"{[(f.severity, f.message) for f in findings]}"
    )


# ── bad_hardcoded_macro: hardban_llm_macros must FAIL ──────────────

def test_bad_hardcoded_macro_fires_hardban():
    by_check = _findings_by_check(FIXTURES / "bad_hardcoded_macro")
    findings = by_check["hardban_llm_macros"]
    fails = [f for f in findings if f.severity == "fail"]
    # \manim and \show in the fixture → at least 2 fails
    assert len(fails) >= 2, (
        f"bad_hardcoded_macro should produce ≥2 hardban_llm_macros FAILs "
        f"(\\manim + \\show); got {[f.message for f in findings]}"
    )


# ── add_voice_clone fixer ────────────────────────────────────────

def test_add_voice_clone_fixer_idempotent(tmp_path: Path):
    """Apply twice → no extra voice=mine insertions."""
    import shutil
    src = FIXTURES / "good_minimal"
    dst = tmp_path / "vc_idem"
    shutil.copytree(src, dst)

    first  = FIXERS["add_voice_clone"].apply(dst, dry_run=False)
    second = FIXERS["add_voice_clone"].apply(dst, dry_run=False)
    # The good_minimal fixture has a single \say without voice=mine.
    # First pass should edit it. Second pass should be a no-op.
    assert len(first) == 1, f"first pass should edit 1 call, got {first}"
    assert len(second) == 0, f"second pass should be idempotent, got {second}"


# ── L3 render-based checks ───────────────────────────────────────
# These need Playwright in either base or comfyui env. Skip cleanly if
# absent so the test suite stays green on machines without the backend
# rendering stack installed.

def _playwright_available() -> bool:
    """True if the L3 probe can find Playwright (either in-process or via
    the comfyui subprocess fallback)."""
    from harness.checks._render_helper import get_bboxes
    # Minimal probe: render a 100×100 viewport on a tiny file.
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write("<html><body><div style='width:50px;height:50px'></div></body></html>")
        p = Path(f.name)
    try:
        bboxes = get_bboxes(p, 100, 100)
        return bboxes is not None
    finally:
        p.unlink(missing_ok=True)


_HAS_PLAYWRIGHT = _playwright_available()


@pytest.mark.skipif(not _HAS_PLAYWRIGHT, reason="Playwright unavailable")
def test_bad_html_overflow_fires_overflow_check():
    by_check = _findings_by_check(FIXTURES / "bad_html_overflow")
    findings = by_check["html_overflow_render"]
    fails = [f for f in findings if f.severity == "fail"]
    assert len(fails) >= 2, (
        f"bad_html_overflow has 2 out-of-canvas divs; expected ≥2 fails. "
        f"Got: {[f.message for f in findings]}"
    )
    edges = {tuple(sorted(e for e, _px in f.meta.get("overflow", [])))
             for f in fails}
    assert ("bottom",) in edges or ("right",) in edges or len(edges) >= 1, (
        f"expected edge labels in findings.meta, got {edges}"
    )


@pytest.mark.skipif(not _HAS_PLAYWRIGHT, reason="Playwright unavailable")
def test_bad_text_collision_fires_overlap_check():
    by_check = _findings_by_check(FIXTURES / "bad_text_collision")
    findings = by_check["html_text_overlap"]
    fails = [f for f in findings if f.severity == "fail"]
    assert fails, (
        f"bad_text_collision should produce ≥1 html_text_overlap FAIL, got "
        f"{[(f.severity, f.message) for f in findings]}"
    )
    # The synthetic fixture overlaps the two divs by ~85% of the smaller bbox.
    assert any(f.meta.get("overlap_frac", 0) > 0.3 for f in fails)


@pytest.mark.skipif(not _HAS_PLAYWRIGHT, reason="Playwright unavailable")
def test_good_minimal_no_l3_findings():
    """good_minimal has no \\htmlFile{} — L3 checks should no-op cleanly."""
    by_check = _findings_by_check(FIXTURES / "good_minimal")
    assert not by_check["html_overflow_render"]
    assert not by_check["html_text_overlap"]
