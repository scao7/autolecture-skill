"""\\say{} consistency check for voice clone usage.

Behavior depends on whether auth credentials are available:

  • Online (env AUTOLECTURE_API_KEY or ~/.config/autolecture/auth.json):
    GET /api/v2/me/voice-sample. If user has a registered sample, every
    \\say in the project MUST carry [voice=mine]. Missing → fail with
    fixer="add_voice_clone".

  • Offline (no creds): degrades to a CONSISTENCY-ONLY check — if the
    project has ANY \\say with voice=mine, ALL \\say in the project should
    have it (mixing is almost always a mistake). No proactive check.

This is the one check in the MVP that benefits from auth — but it never
HARD-fails offline. Skips gracefully.
"""
from __future__ import annotations

from pathlib import Path

from ..runtime import auth_headers, detect
from ._common import (
    Finding,
    find_macro_calls,
    find_main_tex,
    load_layout,
    read_text,
    strip_comments,
)

CHECK_NAME = "voice_clone_consistency"


def _user_has_voice_sample(base_url: str) -> bool | None:
    """GET /api/v2/me/voice-sample → True if sample registered, False if
    not, None on network error / wrong key.

    Uses harness.runtime.auth_headers() so the auth resolution chain
    matches the SDK + the rest of the skill exactly."""
    headers = auth_headers()
    if headers is None:
        return None
    try:
        import httpx  # type: ignore
    except ImportError:
        return None
    try:
        r = httpx.get(
            f"{base_url.rstrip('/')}/api/v2/me/voice-sample",
            headers=headers,
            timeout=8.0,
        )
        if r.status_code == 200:
            data = r.json()
            return bool(data.get("filename") or data.get("voice_sample_path"))
        return False if r.status_code == 404 else None
    except Exception:
        return None


def run(workdir: Path) -> list[Finding]:
    cfg = load_layout().get("voice_clone", {})
    if not cfg.get("enforce_when_sample_registered", True):
        return []

    findings: list[Finding] = []
    main = find_main_tex(workdir)
    tex = strip_comments(read_text(main))
    rel = main.relative_to(workdir).as_posix()

    say_calls = find_macro_calls(tex, "say")
    if not say_calls:
        return []

    with_voice_mine = [c for c in say_calls if c.opt("voice") == "mine"]
    without_voice_mine = [c for c in say_calls if c.opt("voice") != "mine"]

    mode = detect()
    if mode.is_dynamic() and mode.base_url:
        # Online mode — ask the backend whether the user has a sample.
        has_sample = _user_has_voice_sample(mode.base_url)
        if has_sample is True:
            for call in without_voice_mine:
                findings.append(Finding(
                    check=CHECK_NAME, severity="fail",
                    file=rel, line=call.line,
                    message=(
                        "Your account has a registered voice sample, but "
                        "this \\say lacks [voice=mine]. It will synthesize "
                        "with the default speaker instead of cloning your "
                        "voice. Add [voice=mine] (or remove your sample if "
                        "intentional)."
                    ),
                    fixer="add_voice_clone",
                    meta={"online": True, "span": call.span},
                ))
            return findings
        if has_sample is False:
            # User has no sample. If their .tex uses voice=mine anyway,
            # that's a future-error — at render time the backend will
            # fail "no sample registered". Warn early.
            for call in with_voice_mine:
                findings.append(Finding(
                    check=CHECK_NAME, severity="warn",
                    file=rel, line=call.line,
                    message=(
                        "\\say[voice=mine] but your account has no registered "
                        "voice sample. Upload one at /account → Voice clone "
                        "OR drop [voice=mine] from this \\say."
                    ),
                    meta={"online": True, "span": call.span},
                ))
            return findings
        # has_sample is None — fall through to offline behavior.

    # Offline (or online but couldn't resolve sample state) — consistency
    # check only. If the file mixes voice=mine and no-voice say, flag.
    if with_voice_mine and without_voice_mine:
        for call in without_voice_mine:
            findings.append(Finding(
                check=CHECK_NAME, severity="warn",
                file=rel, line=call.line,
                message=(
                    f"This \\say lacks [voice=mine] but {len(with_voice_mine)} "
                    f"other \\say in this project have it. Mixing is almost "
                    f"always a typo — either add [voice=mine] to this one or "
                    f"remove it from the others."
                ),
                fixer="add_voice_clone",
                meta={"online": False, "consistency_only": True,
                      "span": call.span},
            ))
    return findings
