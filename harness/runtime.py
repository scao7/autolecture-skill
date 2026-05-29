"""Runtime-mode detector — single source of truth for "is the skill
running with SDK auth available (dynamic) or no (static, zip-only)?".

Used by:
- Workflows: skill prose tells Claude to call `python -m scripts.runtime_mode`
  at step 0 and branch on the result.
- harness/checks/voice_clone_consistency.py: derives whether to do an
  online /me/voice-sample query vs offline consistency-only check.
- scripts/upload_and_compile.py: already calls Client() which has the
  same fallback chain — this module is the explicit-detection counterpart.

Resolution chain (matches the SDK's Client() resolution exactly):
  1. AUTOLECTURE_API_KEY env var → dynamic, base_url from
     AUTOLECTURE_BASE_URL env var or default prod
  2. ~/.config/autolecture/auth.json cache (chmod 600, written by
     `autolecture login` / `Client.login()`) → dynamic, base_url from
     cache or env override
  3. Neither → static (zip-only path)
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Mode:
    """Runtime mode + resolved auth context.

    `mode == "dynamic"` means the SDK has credentials to call the
    backend (proactive voice-sample query, estimate_compile, balance
    check, rerender_block, etc. are all available).

    `mode == "static"` means we can only produce a zip the user
    uploads manually — no /me lookups, no per-block introspection.
    Workflows MUST handle both branches; the skill's reference docs
    list the per-feature fallbacks.
    """
    mode: Literal["dynamic", "static"]
    base_url: str | None              # set only when mode == "dynamic"
    source: Literal["env", "cache", "none"]    # how we resolved (or didn't)
    email: str | None = None          # available only from cache, not env

    def is_dynamic(self) -> bool:
        return self.mode == "dynamic"

    def is_static(self) -> bool:
        return self.mode == "static"


_DEFAULT_BASE_URL = "https://autolecture.ai"


def _cache_path() -> Path:
    """Mirrors the SDK's `_auth_cache.cache_path()` so we don't have to
    import autolecture (which may not be installed in static mode)."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return Path(base) / "autolecture" / "auth.json"


def _load_cache() -> dict | None:
    p = _cache_path()
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def detect() -> Mode:
    """Resolve runtime mode. Pure function — no network calls, no
    backend health check. Validates only that creds EXIST, not that
    they're still accepted by the backend (a stale token would still
    return dynamic; first SDK call would fail with 401)."""
    key = os.environ.get("AUTOLECTURE_API_KEY")
    base_env = os.environ.get("AUTOLECTURE_BASE_URL")
    if key:
        return Mode(
            mode="dynamic",
            base_url=base_env or _DEFAULT_BASE_URL,
            source="env",
        )
    cache = _load_cache()
    if cache and cache.get("api_key"):
        return Mode(
            mode="dynamic",
            base_url=base_env or cache.get("base_url") or _DEFAULT_BASE_URL,
            source="cache",
            email=cache.get("email"),
        )
    return Mode(mode="static", base_url=None, source="none")


def auth_headers() -> dict[str, str] | None:
    """For workflows / harness checks that want to make a one-off
    authenticated request without instantiating the full SDK Client.
    Returns None in static mode."""
    key = os.environ.get("AUTOLECTURE_API_KEY")
    if not key:
        cache = _load_cache()
        if not cache:
            return None
        key = cache.get("api_key")
        if not key:
            return None
    return {"Authorization": f"Bearer {key}"}
