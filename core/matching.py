"""Matching: allowed-pair filter, public mismatch filter, E5 cosine ranking, bonuses.

If embeddings are unavailable the ranking falls back to tag overlap, so Discover
always works.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

import numpy as np
from typing import Literal

from pydantic import BaseModel

from core import llm, storage
from core.schemas import Match, Profile

log = logging.getLogger(__name__)

EMBED_FILE = storage.REPO_DATA / "seed_embeddings.npz"
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-large"

# Founders can meet anyone; everyone else meets founders.
ALLOWED_PAIRS = {
    frozenset({"founder", "investor"}),
    frozenset({"founder", "engineer"}),
    frozenset({"founder", "operator"}),
}


# ---------- filters ----------

def pair_allowed(a: Profile, b: Profile) -> bool:
    if a.id == b.id or frozenset({a.role, b.role}) not in ALLOWED_PAIRS:
        return False
    # Each side must want to meet the other's role (empty seeking = open to all).
    return (not a.seeking or b.role in a.seeking) and (not b.seeking or a.role in b.seeking)


ALL_STAGES = ("pre-seed", "seed", "series a", "series b")


def _stages(text: str) -> set[str]:
    """Investor stages from plain words: 'early stage' -> pre-seed + seed, 'growth' -> series b, 'any' -> all.

    Words we can't read give an empty set, which callers treat as unknown (never a mismatch).
    """
    t = (text or "").lower().replace("-", " ").replace("_", " ")
    out = set()
    if any(w in t for w in ("any stage", "all stage", "stage agnostic", "agnostic")):
        return set(ALL_STAGES)
    if "pre seed" in t or "preseed" in t or "angel" in t:
        out.add("pre-seed")
    if "early" in t:
        out |= {"pre-seed", "seed"}
    if "seed" in t.replace("pre seed", "").replace("preseed", ""):
        out.add("seed")
    if "series a" in t or " a round" in t or t.strip() == "a":
        out.add("series a")
    if "series b" in t or "growth" in t or "later stage" in t:
        out.add("series b")
    return out


def clear_mismatch(a: Profile, b: Profile) -> bool:
    """Obvious mismatches visible from public fields alone."""
    roles = {a.role: a, b.role: b}
    founder, investor = roles.get("founder"), roles.get("investor")
    if founder and investor and founder.stage and investor.public_terms.get("stages"):
        stages = _stages(investor.public_terms["stages"])
        if stages and founder.stage.lower() not in stages:
            return True
    return False


def candidates(viewer: Profile, pool: list[Profile]) -> list[Profile]:
    return [p for p in pool if pair_allowed(viewer, p) and not clear_mismatch(viewer, p)]


# ---------- embeddings ----------

def passage_text(p: Profile) -> str:
    offers = f"Offers: {p.offers} " if p.offers else ""
    return (f"passage: {p.role}. {p.headline}. {p.public_bio} Looking for: {p.looking_for} "
            f"{offers}Tags: {', '.join(p.tags)}. Location: {p.location}.")


def query_text(p: Profile) -> str:
    return f"query: {p.looking_for} Tags: {', '.join(p.tags)}. Location: {p.location}."


def embed(texts: list[str]) -> np.ndarray:
    """Normalised embeddings, shape (n, dim). Raises on failure."""
    from huggingface_hub import InferenceClient

    client = InferenceClient(token=os.getenv("HF_TOKEN"), timeout=20)
    model = os.getenv("EMBEDDING_MODEL") or DEFAULT_EMBEDDING_MODEL
    vecs = np.asarray(client.feature_extraction(texts, model=model), dtype=np.float32)
    if vecs.ndim == 3:  # some backends return token embeddings; mean-pool them
        vecs = vecs.mean(axis=1)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


@lru_cache(maxsize=1)
def _seed_vectors() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    if not EMBED_FILE.exists():
        log.warning("No seed embeddings at %s; run scripts/seed.py", EMBED_FILE)
        return {}
    data = np.load(EMBED_FILE)
    return {pid: (q, p) for pid, q, p in zip(data["ids"], data["query"], data["passage"])}


_live_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}


def vectors(p: Profile) -> tuple[np.ndarray, np.ndarray] | None:
    """(query_vec, passage_vec) for a profile, or None if unavailable."""
    seed = _seed_vectors()
    if p.id in seed:
        return seed[p.id]
    key = query_text(p) + "\n" + passage_text(p)
    if key not in _live_cache:
        try:
            q, ps = embed([query_text(p), passage_text(p)])
            _live_cache[key] = (q, ps)
        except Exception as exc:
            log.warning("Embedding failed for %s: %s", p.id, exc)
            return None
    return _live_cache[key]


def index(p: Profile) -> bool:
    """Embed a profile now, so it is searchable (and its own search is fast) right after saving.

    False means embeddings are unavailable; matching then falls back to tag overlap.
    """
    return vectors(p) is not None


# ---------- ranking ----------

def _tags(p: Profile) -> set[str]:
    return {t.lower() for t in p.tags}


def _place(p: Profile) -> set[str]:
    return {part.strip().lower() for part in p.location.split(",") if part.strip()}


def bonus(a: Profile, b: Profile) -> float:
    shared = len(_tags(a) & _tags(b))
    score = min(shared, 4) * 0.01
    if _place(a) & _place(b):
        score += 0.02
    roles = {a.role: a, b.role: b}
    if "founder" in roles and "investor" in roles and roles["founder"].stage:
        score += 0.02  # stage already passed the filter, so it fits
    return score


def _tag_similarity(a: Profile, b: Profile) -> float:
    ta, tb = _tags(a), _tags(b)
    return len(ta & tb) / len(ta | tb) if ta | tb else 0.0


def _display_score(sim: float, embedded: bool) -> int:
    # E5 cosines for related texts sit roughly in 0.75–0.92; stretch that to 0–100.
    if embedded:
        return int(np.clip((sim - 0.74) / 0.20 * 100, 0, 100))
    return int(np.clip(40 + sim * 100, 0, 100))


MIN_SCORE = 35  # below this we show "No obvious match"


def rank(viewer: Profile, pool: list[Profile] | None = None, k: int = 3) -> list[tuple[Profile, int]]:
    pool = candidates(viewer, pool if pool is not None else storage.all_profiles())
    if not pool:
        return []
    v = vectors(viewer)
    scored = []
    for c in pool:
        cv = vectors(c) if v is not None else None
        if v is not None and cv is not None:
            sim = (float(v[0] @ cv[1]) + float(cv[0] @ v[1])) / 2
            scored.append((c, _display_score(sim + bonus(viewer, c), True)))
        else:
            scored.append((c, _display_score(_tag_similarity(viewer, c) + bonus(viewer, c), False)))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(c, s) for c, s in scored[:k] if s >= MIN_SCORE]


# ---------- fit check + reasons ----------

SHORTLIST = 6  # candidates sent to the fit check; the best 3 that survive are shown

FitLevel = Literal["strong", "possible", "weak"]


class _Fit(BaseModel):
    id: str
    fit: FitLevel = "possible"
    reason: str


class _Fits(BaseModel):
    matches: list[_Fit]


FIT_PROMPT = (
    "You screen startup matches for the viewer. For each candidate decide how well they fit what the viewer is "
    "looking for, using only the public profiles:\n"
    "- strong: the core need lines up (sector or skills, stage, what each side is looking for).\n"
    "- possible: real overlap, but one important thing is unclear or only partly aligned.\n"
    "- weak: the core need does not line up (for example a different sector focus, or a role that needs "
    "different skills).\n"
    "Judge only the core need. Do NOT mark a candidate weak because of negotiable terms such as salary, equity, "
    "valuation, remote or on-site work, location or timing: the agents negotiate those later.\n"
    "For strong and possible candidates write ONE sentence (max 22 words) telling the viewer why this person is "
    "worth a conversation, leading with the strongest genuine overlap. Address the viewer as 'you' and refer to "
    "the candidate by first name, never by pronoun. Do not invent facts. For weak candidates write a short "
    "'why not' (max 10 words), for example 'Focuses on deep tech, not fintech.'\n"
    'Reply with JSON: {"matches": [{"id": "<candidate id>", "fit": "strong|possible|weak", "reason": "<sentence>"}]}'
)


def fallback_reason(a: Profile, b: Profile) -> str:
    mine = _tags(a)
    shared = [t for t in b.tags if t.lower() in mine]
    if shared:
        return f"You share a focus on {', '.join(shared[:2])}, and {b.display_name.split()[0]} is looking for {b.looking_for[0].lower()}{b.looking_for[1:]}"
    return f"{b.display_name.split()[0]} is looking for {b.looking_for[0].lower()}{b.looking_for[1:]}"


def fallback_fit(a: Profile, b: Profile) -> FitLevel:
    """Without the LLM: shared tags suggest the core need lines up."""
    shared = len(_tags(a) & _tags(b))
    return "strong" if shared >= 2 else "possible" if shared == 1 else "weak"


_fit_cache: dict[tuple, dict[str, tuple[str, str]]] = {}


def fit_check(viewer: Profile, candidates_: list[Profile]) -> dict[str, tuple[str, str]]:
    """One LLM call: {candidate id: (fit level, reason)}. Never raises."""
    key = (viewer.model_dump_json(), tuple(c.id for c in candidates_))
    if key in _fit_cache:
        return _fit_cache[key]
    out = {c.id: (fallback_fit(viewer, c), fallback_reason(viewer, c)) for c in candidates_}
    if not candidates_:
        return out
    import json

    data = {"viewer": viewer.public_view(), "candidates": [c.public_view() for c in candidates_]}
    messages = [{"role": "system", "content": FIT_PROMPT},
                {"role": "user", "content": json.dumps(data, ensure_ascii=False)}]
    try:
        result, _ = llm.chat_json(messages, _Fits, max_tokens=500)
        for m in result.matches:
            if m.id in out:
                out[m.id] = (m.fit, m.reason.strip() or out[m.id][1])
        _fit_cache[key] = out
    except llm.LLMError as exc:
        log.warning("Fit check fell back to tag overlap: %s", exc)
    return out


# Shown score bands: strong matches show 75-100, possible ones 50-74, so the number agrees with the label.
_FIT_BAND = {"strong": (75, 100), "possible": (50, 74)}
_FIT_ORDER = {"strong": 0, "possible": 1}


def banded(score: int, level: str) -> int:
    lo, hi = _FIT_BAND[level]
    return round(lo + (hi - lo) * max(0, min(100, score)) / 100)


ROLE_PLURAL = {"founder": "founders", "investor": "investors", "engineer": "engineers", "operator": "operators"}


def _roles_label(roles: list[str]) -> str:
    names = [ROLE_PLURAL[r] for r in roles]
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def search(viewer: Profile, k: int = 3, frozen_fits: dict[str, tuple[str, str]] | None = None):
    """The agent's search, step by step, so the UI can show it working.

    Yields (kind, data):
      ("read",    {"wants", "tags", "seeking"})        what the agent is looking for
      ("scan",    {"total"})                           everyone in the ecosystem
      ("filter",  {"label", "kept", "dropped"})        one filter step
      ("ranked",  {"considered", "shortlist": [(Profile, score)]})
      ("fit",     {"id", "level", "reason"})           close look at one candidate
      ("done",    {"matches": [Match]})
    frozen_fits replaces the LLM fit check (presenter mode).
    """
    pool = [p for p in storage.all_profiles() if p.id != viewer.id]
    allowed_roles = [r for r in ROLE_PLURAL if frozenset({viewer.role, r}) in ALLOWED_PAIRS]
    seeking = [r for r in (viewer.seeking or allowed_roles) if r in allowed_roles]
    yield ("read", {"wants": viewer.looking_for, "tags": viewer.tags[:5], "seeking": _roles_label(seeking)})
    yield ("scan", {"total": len(pool)})

    step = [p for p in pool if p.role in seeking]
    yield ("filter", {"label": f"Kept {_roles_label(seeking)}", "kept": len(step), "dropped": len(pool) - len(step)})
    wants_me = [p for p in step if not p.seeking or viewer.role in p.seeking]
    yield ("filter", {"label": f"Kept those who want to meet {ROLE_PLURAL[viewer.role]}", "kept": len(wants_me),
                      "dropped": len(step) - len(wants_me)})
    fits_stage = [p for p in wants_me if not clear_mismatch(viewer, p)]
    if "investor" in seeking or viewer.role == "investor":  # stage only matters between founders and investors
        label = ("Removed investors who don't invest at your stage" if viewer.role == "founder"
                 else "Removed founders outside your stages")
        yield ("filter", {"label": label, "kept": len(fits_stage), "dropped": len(wants_me) - len(fits_stage)})

    shortlist = rank(viewer, pool=fits_stage, k=SHORTLIST)
    yield ("ranked", {"considered": len(fits_stage), "shortlist": shortlist})

    fits = frozen_fits if frozen_fits is not None else fit_check(viewer, [p for p, _ in shortlist])
    kept = []
    for p, score in shortlist:
        level, reason = fits.get(p.id) or (fallback_fit(viewer, p), fallback_reason(viewer, p))
        yield ("fit", {"id": p.id, "level": level, "reason": reason})
        if level != "weak":
            kept.append(Match(profile=p, score=banded(score, level), reason=reason, fit=level))
    kept.sort(key=lambda m: (_FIT_ORDER[m.fit], -m.score))
    yield ("done", {"matches": kept[:k]})


def top_matches(viewer: Profile, k: int = 3) -> list[Match]:
    """Rank by embeddings, let the fit check drop weak candidates, return the best k."""
    result: list[Match] = []
    for kind, data in search(viewer, k=k):
        if kind == "done":
            result = data["matches"]
    return result


def warm(profile_ids: list[str]) -> None:
    """Pre-compute matches for demo personas so Discover opens instantly on stage."""
    for pid in profile_ids:
        p = storage.get_profile(pid)
        if p is not None:
            try:
                top_matches(p)
            except Exception:
                log.exception("Warm-up failed for %s", pid)


# ---------- presenter mode ----------

PRESENTER_MATCHES = storage.REPO_DATA / "demo_matches.json"


def save_presenter_matches(profile_ids: list[str]) -> dict[str, list[dict]]:
    """Freeze each demo persona's search (fit verdicts for the shortlist) so every rehearsal looks the same.

    Returns {persona id: shown matches} for convenience.
    """
    import json

    frozen, shown = {}, {}
    for pid in profile_ids:
        viewer = storage.get_profile(pid)
        shortlist = rank(viewer, pool=candidates(viewer, storage.all_profiles()), k=SHORTLIST)
        fits = fit_check(viewer, [p for p, _ in shortlist])
        frozen[pid] = {"fits": {cid: list(v) for cid, v in fits.items()}}
        matches = [d["matches"] for k_, d in search(viewer, frozen_fits=fits) if k_ == "done"][0]
        shown[pid] = [m.model_dump(exclude={"profile"}) | {"id": m.profile.id} for m in matches]
        frozen[pid]["matches"] = shown[pid]
    PRESENTER_MATCHES.write_text(json.dumps(frozen, ensure_ascii=False, indent=2), encoding="utf-8")
    return shown


def presenter_fits(viewer: Profile) -> dict[str, tuple[str, str]] | None:
    """Frozen fit verdicts for a demo persona's shortlist, or None."""
    import json

    if not PRESENTER_MATCHES.exists():
        return None
    try:
        saved = json.loads(PRESENTER_MATCHES.read_text(encoding="utf-8")).get(viewer.id)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(saved, dict) or "fits" not in saved:
        return None
    return {cid: (v[0], v[1]) for cid, v in saved["fits"].items()}
