"""Optional disk cache for model calls, so demo rehearsals replay instantly and identically.

Off by default. Set AI_CACHE_DIR (e.g. ./ai_cache) to turn it on: the first run records each
model answer, and any later call with exactly the same input replays it. Keys are a hash of
the full input, so a different message or upload always goes to the live model.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


def _dir() -> Path | None:
    d = os.getenv("AI_CACHE_DIR")
    if not d:
        return None
    path = Path(d)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _key(kind: str, payload) -> str:
    raw = payload if isinstance(payload, bytes) else json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    return f"{kind}-{hashlib.sha256(raw).hexdigest()[:32]}.json"


def get(kind: str, payload):
    d = _dir()
    if d is None:
        return None
    f = d / _key(kind, payload)
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    except (OSError, json.JSONDecodeError):
        return None


def put(kind: str, payload, value) -> None:
    d = _dir()
    if d is not None:
        (d / _key(kind, payload)).write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
