"""Turn a free-text self-description (English or Arabic) into a structured profile draft."""

from __future__ import annotations

import json
import logging
import re
import uuid

from pydantic import BaseModel, Field, field_validator

from core import llm
from core.schemas import Profile, Role

log = logging.getLogger(__name__)

MAX_TEXT = 2000
ROLES = ("founder", "investor", "engineer", "operator")
STAGES = ("pre-seed", "seed", "series a", "series b")


class Draft(BaseModel):
    display_name: str = ""
    headline: str = ""
    public_bio: str = ""
    looking_for: str = ""
    seeking: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    location: str = ""
    stage: str | None = None
    public_terms: dict[str, str] = Field(default_factory=dict)
    private_limits: list[str] = Field(default_factory=list)
    secret_terms: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)

    @field_validator("public_terms", mode="before")
    @classmethod
    def _stringify_terms(cls, v):
        return {str(k): str(val) for k, val in (v or {}).items()} if isinstance(v, dict) else {}


SYSTEM = """You help people on Handshake, a startup matchmaking platform, set up the AI agent that will \
negotiate for them. Turn their self-description into a structured profile.

The person is a {role}. Split what they said into:
- PUBLIC fields other agents may read: headline, public_bio, looking_for, tags, location, stage, public_terms.
- PRIVATE limits their agent must protect: walk-away numbers, minimums, maximums, deal-breakers, anything they \
said is private or that they would not tell the other side up front. If they gave a public range AND a stricter \
private number, the range is public and the number is private.

Field rules:
- display_name: their name if they gave one, otherwise "". Never use a job title as a name.
- headline: one line, e.g. "Founder, Acme — payroll for Gulf SMEs".
- public_bio: 2-3 sentences, only facts they gave. Never invent traction, numbers or employers.
- looking_for: one sentence.
- seeking: roles they want to meet, from {roles}. Founders may seek several; everyone else seeks ["founder"].
- tags: 3-6 short keywords. location: city, country.
- stage: for founders one of {stages}, otherwise null.
- public_terms: short key/value strings appropriate to the role, e.g. for founders raising: raising, valuation, \
timeline; for investors: stages (comma list from {stages}), cheque_size, sectors, geography; for talent and hiring: \
role, salary, equity, work_style, start.
- private_limits: short sentences. secret_terms: the exact numbers or phrases inside private_limits that must never \
be said (e.g. "$10M", "15%"). Use Western digits. If they gave no private limits, return [] for both.
- follow_up_questions: at most 3 short questions about MISSING details that matter for negotiation for this role \
(for example cheque size, valuation, salary floor, remote or on-site, stage). Ask nothing already answered. \
Return [] if nothing important is missing.
- Write text fields in the same language the person used.

Reply with JSON only, with exactly these keys: display_name, headline, public_bio, looking_for, seeking, tags, \
location, stage, public_terms, private_limits, secret_terms, follow_up_questions."""

_AMOUNT = re.compile(
    r"[$€£]?\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|mn|bn|b|million|thousand|%|percent)?(?![a-z])", re.I)


def amounts_in(text: str) -> list[str]:
    """Money amounts and percentages in a sentence, e.g. '$10M', '15%', '140k'."""
    out = []
    from core.negotiation import _ARABIC_DIGITS  # shared digit table

    text = text.translate(_ARABIC_DIGITS)
    for m in _AMOUNT.finditer(text):
        token = m.group(0).strip()
        bare = re.sub(r"[^\d]", "", token)
        # Skip bare small integers like "2 days" or years: they are not limits worth guarding.
        if token == bare and (len(bare) < 3 or 1900 <= int(bare) <= 2100):
            continue
        out.append(token)
    return out


def split_terms(text: str) -> list[str]:
    """Split a comma-separated list without breaking numbers like $105,000."""
    return [t.strip() for t in re.split(r",(?!\d{3}(?!\d))", text or "") if t.strip()]


def derive_secret_terms(private_limits: list[str], extra: list[str] | None = None) -> list[str]:
    from core.negotiation import normalize

    terms = [*(extra or []), *(a for limit in private_limits for a in amounts_in(limit))]
    seen, out = set(), []
    for t in (t.strip() for t in terms):
        key = normalize(t)
        # Skip duplicates ($105,000 vs $105000) and fragments too short to guard safely.
        if not key or key in seen or (key.isdigit() and len(key) < 2) or len(key) < 2:
            continue
        seen.add(key)
        out.append(t)
    return out


def _clean(draft: Draft, role: str) -> Draft:
    seeking = [r.lower().rstrip("s") for r in draft.seeking]
    seeking = [r for r in seeking if r in ROLES and r != role] if role == "founder" else ["founder"]
    stage = (draft.stage or "").lower().replace("-", " ").replace("pre seed", "pre-seed").strip() or None
    draft.seeking = seeking or (["investor", "engineer", "operator"] if role == "founder" else ["founder"])
    draft.stage = stage if role == "founder" and stage in STAGES else None
    draft.tags = [t.strip() for t in draft.tags if t.strip()][:6]
    draft.private_limits = [x.strip() for x in draft.private_limits
                            if x.strip() and not re.search(r"\b(no|none)\b.*\blimit|^none\.?$|^n/?a$", x.strip(), re.I)]
    draft.secret_terms = derive_secret_terms(draft.private_limits, draft.secret_terms)
    draft.follow_up_questions = [q.strip() for q in draft.follow_up_questions if q.strip()][:3]
    return draft


def extract(role: str, text: str, name: str = "", answers: dict[str, str] | None = None) -> Draft:
    """Raises llm.LLMError if the model is unavailable."""
    text = (text or "")[:MAX_TEXT]
    user = {"role": role, "name": name or None, "self_description": text}
    if answers:
        user["answers_to_follow_up_questions"] = {q: a[:500] for q, a in answers.items() if a.strip()}
        user["note"] = "Use the answers. Only ask new follow-up questions if something important is still missing."
    messages = [
        {"role": "system", "content": SYSTEM.format(role=role, roles=list(ROLES), stages=list(STAGES))},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]
    draft, _ = llm.chat_json(messages, Draft, max_tokens=900)
    if name and not draft.display_name:
        draft.display_name = name
    return _clean(draft, role)


# ---------- editable card text <-> profile ----------

def terms_to_text(terms: dict[str, str]) -> str:
    return "\n".join(f"{k}: {v}" for k, v in terms.items())


def text_to_terms(text: str) -> dict[str, str]:
    out = {}
    for line in (text or "").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            if k.strip() and v.strip():
                out[k.strip()[:40]] = v.strip()[:200]
    return out


def lines(text: str) -> list[str]:
    return [x.strip(" -•\t") for x in (text or "").splitlines() if x.strip(" -•\t")]


def build_profile(*, profile_id: str | None, role: str, display_name: str, headline: str, public_bio: str,
                  looking_for: str, seeking: list[str], tags: str, location: str, stage: str | None,
                  public_terms: str, private_limits: str, secret_terms: str,
                  hub_username: str | None = None, hub_evidence: list[str] | None = None) -> Profile:
    """Build and validate a Profile from the editable cards. Raises ValueError with a friendly message."""
    missing = [label for label, v in (("your name", display_name), ("a headline", headline),
                                      ("what you're looking for", looking_for)) if not (v or "").strip()]
    if role not in ROLES:
        missing.insert(0, "your role")
    if missing:
        raise ValueError("Please add " + ", ".join(missing) + ".")
    limits = lines(private_limits)
    extra = split_terms(secret_terms)
    role_typed: Role = role  # type: ignore[assignment]
    return Profile(
        id=profile_id or "s-" + uuid.uuid4().hex[:10],
        display_name=display_name.strip()[:80], role=role_typed, headline=headline.strip()[:160],
        public_bio=(public_bio or "").strip()[:MAX_TEXT], looking_for=looking_for.strip()[:400],
        seeking=[s for s in seeking if s in ROLES and s != role] if role == "founder" else ["founder"],
        tags=[t.strip() for t in (tags or "").split(",") if t.strip()][:8],
        location=(location or "").strip()[:80],
        stage=(stage or None) if role == "founder" else None,
        public_terms=text_to_terms(public_terms), private_limits=limits,
        secret_terms=derive_secret_terms(limits, extra),
        hub_username=hub_username, hub_evidence=hub_evidence or [], is_demo=False,
    )
