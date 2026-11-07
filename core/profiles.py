"""Turn a free-text self-description (English or Arabic) into a structured profile draft."""

from __future__ import annotations

import json
import logging
import re
import uuid

from pydantic import BaseModel, Field, field_validator

from core import llm
from core.schemas import Profile, Role, Terms
from core.terms import _MONTH, RawTerms, _mentions, fix_units, mark_private, to_terms

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


class FormDraft(Draft):
    """What the profile form extracts: the Draft plus what the matcher indexes beyond it."""
    offers: str = ""
    terms: RawTerms | None = None


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
- follow_up_questions: at most 3 short questions TO this person about their OWN situation as a {role}, about \
MISSING details that matter for negotiation. Ask in the second person ("What's your…?"). Fitting topics: \
{question_topics}. Never ask a question meant for the other side (an engineer is not hiring; an investor is not \
raising). Ask nothing already answered. Return [] if nothing important is missing.
- offers: one sentence on what they give others (capital, pilots, introductions, skills), ONLY if they stated it. \
Do not infer it. "" if not stated.
- terms: the numbers behind their terms and deal-breakers, as written (amounts in full units: 9M -> 9000000; equity \
in percentage points: 1% -> 1; currency as they wrote it, never assumed to be USD; period "month" for monthly pay). \
{terms_rule} work: ONLY a stated requirement ("remote only"), never a preference. other: short phrases for any \
other requirement, e.g. "must be profitable". Use null or [] for anything not stated.
- Write text fields in the same language the person used.

Reply with JSON only, with exactly these keys: display_name, headline, public_bio, looking_for, seeking, tags, \
location, stage, public_terms, private_limits, secret_terms, follow_up_questions, offers, terms. terms has the keys \
valuation, hires, salary, equity, work, other; a range is {{"low", "high", "currency", "period"}}."""

QUESTION_TOPICS = {
    "founder": "how much you're raising, your valuation floor, roles you're hiring and what you can pay, timeline",
    "investor": "cheque size, stages, sectors, geography, your valuation ceiling",
    "engineer": "your salary floor, equity you'd want, remote or on-site, when you can start",
    "operator": "the role you want, your salary floor, equity you'd want, remote or on-site, when you can start",
}

TERMS_RULE = {
    "founder": "valuation.low = the lowest valuation they accept; hires = one entry per role they hire "
               "({\"kind\": \"engineer\" or \"operator\", \"title\", \"salary\": {\"high\": most they can pay}, "
               "\"equity\", \"work\"}).",
    "investor": "valuation.high = the highest valuation they invest at.",
    "engineer": "salary.low = their minimum; equity.low = the least equity they accept.",
    "operator": "salary.low = their minimum; equity.low = the least equity they accept.",
}

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


def structured_terms(raw: RawTerms | None, said: str, private_limits: list[str], location: str = "") -> Terms | None:
    """The numbers the matcher checks in code: units fixed from the member's words, converted to USD per year.

    Every bound is marked private: the member's own numbers are never quoted to anyone else.
    """
    if raw is None:
        return None
    said = "\n".join([said, *private_limits])
    for r in (raw.salary, *(h.salary for h in raw.hires)):
        # Models sometimes call a salary monthly unprompted, which multiplies it by 12. Only the member's own
        # words decide: keep "month" only if they wrote it next to that number.
        if r is not None and r.period == "month" and not any(
                any(m in w for m in _MONTH) for v in (r.low, r.high) if v is not None for w in _mentions(v, said)):
            r.period = None
    t = to_terms(fix_units(mark_private(raw, private_limits), said, location))
    for r in [t.valuation, t.salary, t.equity] + [r for h in t.hires for r in (h.salary, h.equity)]:
        if r is not None:
            r.low_private = r.high_private = True
    empty = not (t.valuation or t.salary or t.equity or t.hires or t.work or t.other)
    return None if empty else t


def _money(v: float, cur: str) -> str:
    sym = {"USD": "$", "EUR": "€"}.get(cur, cur + " ")
    return f"{sym}{v / 1e6:g}M" if v >= 1e6 else f"{sym}{v / 1e3:,.0f}k"


def _checks(t: Terms | None) -> list[tuple[str, list[float], str]]:
    """(plain-language line, the numbers it holds, kind) for everything the matcher checks exactly."""
    if t is None:
        return []
    out = []
    if t.valuation and t.valuation.low is not None:
        out.append((f"Valuation of at least {_money(t.valuation.low, t.valuation.currency)}", [t.valuation.low], "num"))
    if t.valuation and t.valuation.high is not None:
        out.append((f"Valuation of at most {_money(t.valuation.high, t.valuation.currency)}", [t.valuation.high], "num"))
    if t.salary and t.salary.low is not None:
        out.append((f"Salary of at least {_money(t.salary.low, t.salary.currency)} a year", [t.salary.low], "num"))
    if t.equity and t.equity.low is not None:
        out.append((f"Equity of at least {t.equity.low:g}%", [t.equity.low], "num"))
    for h in t.hires:
        what = h.title or f"the {h.kind} role"
        if h.salary and h.salary.high is not None:
            out.append((f"Pay up to {_money(h.salary.high, h.salary.currency)} a year for {what}", [h.salary.high], "num"))
        if h.equity and h.equity.high is not None:
            out.append((f"Equity up to {h.equity.high:g}% for {what}", [h.equity.high], "num"))
        if h.work:
            out.append((f"{what[0].upper() + what[1:]}: {' or '.join(h.work)}", [], "work"))
    if t.work:
        out.append(("Work: " + " or ".join(t.work) + " only", [], "work"))
    return out + [(o, [], "other") for o in t.other]


def checked_lines(t: Terms | None) -> list[str]:
    """Plain-language list of what the matcher checks exactly, for the member's own eyes."""
    return [line for line, _, _ in _checks(t)]


_WORK_WORDS = ("remote", "on-site", "onsite", "on site", "office", "hybrid", "عن بعد", "مكتب")


def limits_with_checks(private_limits: list[str], t: Terms | None) -> list[tuple[str, bool]]:
    """The member's limits in their own words, each flagged if the matcher checks it exactly, then any exact
    check no limit already says (e.g. "remote only" written in the bio). Nothing is listed twice."""
    from core.terms import _amount

    checks, used, out = _checks(t), set(), []
    for limit in private_limits:
        nums = [v for v in (_amount(a) for a in amounts_in(limit)) if v is not None]
        low = limit.lower()
        hit = None
        for i, (_, values, kind) in enumerate(checks):
            if kind == "num" and any(abs(v - n) <= 0.01 * max(1.0, n) for v in values for n in nums):
                hit = i
            elif kind == "work" and any(w in low for w in _WORK_WORDS):
                hit = i
            elif kind == "other" and checks[i][0].lower() in low:
                hit = i
            if hit is not None:
                break
        if hit is not None:
            used.add(hit)
        out.append((limit, hit is not None))
    return out + [(line, True) for i, (line, _, _) in enumerate(checks) if i not in used]


_TERMS_ONLY = """Read a member's terms and private deal-breakers on Handshake, a startup matchmaking platform. \
The member is a {role}. Extract the numbers behind them.

{rules}

Reply with JSON only: {{"valuation": null, "hires": [], "salary": null, "equity": null, "work": [], "other": []}}. \
A range is {{"low", "high", "currency", "period"}}. Use null or [] for anything not stated."""


def extract_terms(role: str, public_terms: str, private_limits: list[str], location: str = "") -> Terms | None:
    """Re-read the numbers from the edited cards. Raises llm.LLMError if the model is unavailable."""
    said = "\n".join([public_terms or "", *private_limits]).strip()
    if not said:
        return None
    rules = SYSTEM.split("- terms:", 1)[1].split("\n- Write text", 1)[0].format(terms_rule=TERMS_RULE[role])
    messages = [{"role": "system", "content": _TERMS_ONLY.format(role=role, rules="terms:" + rules)},
                {"role": "user", "content": json.dumps({"public_terms": public_terms, "private_limits": private_limits,
                                                        "location": location}, ensure_ascii=False)}]
    raw, _ = llm.chat_json(messages, RawTerms, max_tokens=500)
    return structured_terms(raw, said, private_limits, location)


def extract(role: str, text: str, name: str = "", answers: dict[str, str] | None = None) -> FormDraft:
    """Raises llm.LLMError if the model is unavailable."""
    text = (text or "")[:MAX_TEXT]
    user = {"role": role, "name": name or None, "self_description": text}
    if answers:
        user["answers_to_follow_up_questions"] = {q: a[:500] for q, a in answers.items() if a.strip()}
        user["note"] = "Use the answers. Only ask new follow-up questions if something important is still missing."
    messages = [
        {"role": "system", "content": SYSTEM.format(role=role, roles=list(ROLES), stages=list(STAGES),
                                                    terms_rule=TERMS_RULE[role], question_topics=QUESTION_TOPICS[role])},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)},
    ]
    draft, _ = llm.chat_json(messages, FormDraft, max_tokens=1200)
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
                  public_terms: str, private_limits: str, secret_terms: str, offers: str = "",
                  terms: Terms | None = None,
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
        offers=(offers or "").strip()[:400], terms=terms,
    )
