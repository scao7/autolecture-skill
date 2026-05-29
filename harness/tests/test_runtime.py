"""Pytest for harness.runtime — the single source of truth for "do we
have SDK creds available (dynamic) or not (static)?"."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from harness.runtime import _cache_path, auth_headers, detect


@pytest.fixture(autouse=True)
def isolated_env(tmp_path, monkeypatch):
    """Point XDG_CONFIG_HOME at a tmp dir AND clear any inherited
    AUTOLECTURE_* env vars so each test starts from a clean slate."""
    monkeypatch.delenv("AUTOLECTURE_API_KEY", raising=False)
    monkeypatch.delenv("AUTOLECTURE_BASE_URL", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    yield


def _write_cache(api_key: str, base_url: str = "https://autolecture.ai",
                  email: str = "user@example.com") -> Path:
    p = _cache_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "api_key": api_key, "base_url": base_url, "email": email,
        "label": "test", "key_id": "abc",
    }))
    return p


# ─── Static mode ────────────────────────────────────────────────

def test_no_env_no_cache_is_static():
    m = detect()
    assert m.mode == "static"
    assert m.base_url is None
    assert m.source == "none"
    assert m.email is None
    assert m.is_static()
    assert not m.is_dynamic()


def test_static_mode_has_no_auth_headers():
    assert auth_headers() is None


# ─── Dynamic via env ────────────────────────────────────────────

def test_env_key_alone_is_dynamic(monkeypatch):
    monkeypatch.setenv("AUTOLECTURE_API_KEY", "al_live_envkey_xxx")
    m = detect()
    assert m.is_dynamic()
    assert m.source == "env"
    assert m.base_url == "https://autolecture.ai"
    # email is not available from env (only from cache)
    assert m.email is None


def test_env_key_plus_base_url(monkeypatch):
    monkeypatch.setenv("AUTOLECTURE_API_KEY", "al_live_envkey_xxx")
    monkeypatch.setenv("AUTOLECTURE_BASE_URL", "http://localhost:8001")
    m = detect()
    assert m.is_dynamic()
    assert m.base_url == "http://localhost:8001"


# ─── Dynamic via cache ──────────────────────────────────────────

def test_cache_alone_is_dynamic():
    _write_cache("al_live_cachekey_yyy", base_url="https://dev.autolecture.ai",
                 email="codescao7@gmail.com")
    m = detect()
    assert m.is_dynamic()
    assert m.source == "cache"
    assert m.base_url == "https://dev.autolecture.ai"
    assert m.email == "codescao7@gmail.com"


def test_env_overrides_cache_for_base_url(monkeypatch):
    """If both env and cache exist, env wins for the key — and an env
    base_url overrides the cached one."""
    _write_cache("al_live_cachekey_yyy", base_url="https://autolecture.ai")
    monkeypatch.setenv("AUTOLECTURE_API_KEY", "al_live_envkey_xxx")
    monkeypatch.setenv("AUTOLECTURE_BASE_URL", "http://localhost:8001")
    m = detect()
    assert m.source == "env"               # env key wins
    assert m.base_url == "http://localhost:8001"


def test_malformed_cache_falls_back_to_static():
    p = _cache_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{ this is not json")
    m = detect()
    assert m.is_static()


def test_cache_without_api_key_field_is_static():
    p = _cache_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"base_url": "x", "email": "y"}))
    m = detect()
    assert m.is_static()


# ─── auth_headers() symmetry ────────────────────────────────────

def test_auth_headers_dynamic_env(monkeypatch):
    monkeypatch.setenv("AUTOLECTURE_API_KEY", "al_live_envkey_xxx")
    h = auth_headers()
    assert h == {"Authorization": "Bearer al_live_envkey_xxx"}


def test_auth_headers_dynamic_cache():
    _write_cache("al_live_cachekey_yyy")
    h = auth_headers()
    assert h == {"Authorization": "Bearer al_live_cachekey_yyy"}
