"""JSON file storage: one file per profile and per negotiation.

Seed profiles are read-only and live in the repo. Runtime data lives in DATA_DIR
(./runtime_data locally, /data on the Space).
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
from functools import lru_cache
from pathlib import Path

from core.schemas import Negotiation, Profile

REPO_DATA = Path(__file__).resolve().parent.parent / "data"
SEED_FILE = REPO_DATA / "seed_profiles.json"

_lock = threading.Lock()


def data_dir() -> Path:
    path = Path(os.getenv("DATA_DIR") or "./runtime_data")
    for sub in ("profiles", "negotiations"):
        (path / sub).mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, payload: dict) -> None:
    """Write to a temp file in the same directory, then rename (atomic on POSIX)."""
    with _lock:
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise


def _read_dir(sub: str) -> list[dict]:
    out = []
    for p in sorted((data_dir() / sub).glob("*.json")):
        try:
            out.append(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue  # skip a half-written or corrupt file rather than crash
    return out


# ---- seed data (read-only) ----

@lru_cache(maxsize=1)
def _seed_profiles() -> tuple[Profile, ...]:
    raw = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    return tuple(Profile.model_validate({**p, "is_demo": True}) for p in raw)


def seed_profiles() -> list[Profile]:
    return list(_seed_profiles())


# ---- profiles ----

def save_profile(profile: Profile) -> None:
    if profile.is_demo:
        raise ValueError("Seed profiles are read-only.")
    _write_json(data_dir() / "profiles" / f"{profile.id}.json", profile.model_dump())


def user_profiles() -> list[Profile]:
    return [Profile.model_validate(p) for p in _read_dir("profiles")]


def all_profiles() -> list[Profile]:
    """The matching pool: seed profiles plus saved (signed-in) users."""
    return seed_profiles() + user_profiles()


# Unsaved profiles from visitors who are not signed in. They live only in memory,
# can run negotiations, and never join the matching pool.
_session_profiles: dict[str, Profile] = {}


def register_session_profile(profile: Profile) -> None:
    _session_profiles[profile.id] = profile


def get_profile(profile_id: str) -> Profile | None:
    if profile_id in _session_profiles:
        return _session_profiles[profile_id]
    if not profile_id.startswith(("f-", "i-", "t-")):
        path = data_dir() / "profiles" / f"{profile_id}.json"
        if path.exists():
            return Profile.model_validate_json(path.read_text(encoding="utf-8"))
    return next((p for p in seed_profiles() if p.id == profile_id), None)


# ---- negotiations ----

def save_negotiation(neg: Negotiation) -> None:
    _write_json(data_dir() / "negotiations" / f"{neg.id}.json", neg.model_dump())


def load_negotiation(neg_id: str) -> Negotiation | None:
    path = data_dir() / "negotiations" / f"{neg_id}.json"
    if not path.exists():
        return None
    return Negotiation.model_validate_json(path.read_text(encoding="utf-8"))


def all_negotiations() -> list[Negotiation]:
    return [Negotiation.model_validate(n) for n in _read_dir("negotiations")]


def negotiations_for(profile_id: str) -> list[Negotiation]:
    return [n for n in all_negotiations() if profile_id in (n.profile_a_id, n.profile_b_id)]


def reset_demo_progress() -> None:
    """Hidden admin action: remove runtime negotiations. Seed data is untouched."""
    with _lock:
        for p in (data_dir() / "negotiations").glob("*.json"):
            p.unlink(missing_ok=True)


def stats() -> dict[str, int]:
    negs = all_negotiations()
    return {
        "people": len(all_profiles()),
        "negotiations": len(negs),
        "intros": sum(n.decision_a == "approved" and n.decision_b == "approved" for n in negs),
    }
