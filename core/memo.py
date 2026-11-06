"""Deal memo and intro draft, written by a judge that sees only public data.

The judge prompt never contains private limits. As a second line of defence the
finished memo is leak-checked against both sides' secret terms.
"""

from __future__ import annotations

import json
import logging
from datetime import date

from core import llm
from core.schemas import AgentTurn, DealMemo, Profile

log = logging.getLogger(__name__)

JUDGE = """You are a neutral judge on Handshake, a startup matchmaking platform. Two AI agents just held a \
short screening conversation on behalf of two people. Using ONLY the public profiles and the transcript, \
decide whether the humans should meet.

Rules:
- The transcript may be in Arabic. Always write the memo in English.
- Base every reason on something actually said in the transcript or stated in a public profile.
- Do not invent facts, numbers, names or commitments.
- verdict: "worth_meeting" if the key terms look workable, "maybe_later" if promising but blocked by timing \
or open questions, "not_fit" if a hard mismatch was stated.
- score: 0-100 fit. worth_meeting is usually 70+, maybe_later 40-69, not_fit below 40.
- reasons: exactly 3 short sentences.
- agreed: points both agents said were workable. open_questions: what is still unresolved.
- meeting_questions: 2-3 questions the humans should ask each other.
- intro_message: a warm 2-3 sentence intro addressed to both people by first name, written as if from Handshake. \
For not_fit, write a short polite note instead.

Reply with JSON only:
{"verdict": "...", "score": 0, "reasons": ["", "", ""], "agreed": [], "open_questions": [], \
"meeting_questions": [], "intro_message": ""}"""

_NO_WORDS = ("not workable", "non-negotiable", "cannot proceed", "not a fit", "isn't a fit", "not feasible",
             "غير ممكن", "غير مناسب", "لا يمكن", "مش ممكن", "مش مناسب", "مينفعش", "ما يصلح", "ما يناسب", "ما نقدر")


def _prompt(a: Profile, b: Profile, turns: list[AgentTurn]) -> list[dict]:
    names = {a.id: a.display_name, b.id: b.display_name}
    data = {
        "person_a": a.public_view(),
        "person_b": b.public_view(),
        "transcript": [{"agent_of": names.get(t.speaker_id, "?"), "message": t.message} for t in turns],
        "today": date.today().strftime("%d %B %Y"),
    }
    return [{"role": "system", "content": JUDGE},
            {"role": "user", "content": json.dumps(data, ensure_ascii=False)}]


def _text(memo: DealMemo) -> str:
    return " ".join([*memo.reasons, *memo.agreed, *memo.open_questions, *memo.meeting_questions, memo.intro_message])


def fallback_memo(a: Profile, b: Profile, turns: list[AgentTurn]) -> DealMemo:
    """Rule-based memo used when the judge model is unavailable."""
    hard_no = any(w in t.message.lower() for t in turns for w in _NO_WORDS)
    fa, fb = a.display_name.split()[0], b.display_name.split()[0]
    if hard_no:
        return DealMemo(
            verdict="not_fit", score=25,
            reasons=["The agents found a requirement that one side said was not workable.",
                     "They stopped early instead of negotiating around it.",
                     "A fast no saves both people a meeting."],
            open_questions=["Whether the blocking requirement could change in future."],
            intro_message=f"Thanks {fa} and {fb}. Your agents found a blocker this time, so no intro for now.")
    return DealMemo(
        verdict="maybe_later", score=55,
        reasons=["The agents covered the main topics without a hard blocker.",
                 "Some terms were described as workable.",
                 "Details still need a human conversation."],
        open_questions=["Exact terms, which the agents did not settle."],
        meeting_questions=[f"{fa}, what matters most to you in this partnership?",
                           f"{fb}, what would make this a clear yes for you?"],
        intro_message=f"{fa}, meet {fb}. Your agents think there is enough overlap for a short call.")


def write_memo(a: Profile, b: Profile, turns: list[AgentTurn]) -> DealMemo:
    """Never raises: returns the judge's memo, or a rule-based fallback."""
    secrets = [*a.secret_terms, *b.secret_terms]
    from core.negotiation import leaks  # local import avoids a cycle

    messages = _prompt(a, b, turns)
    for _ in range(2):
        try:
            memo, _ = llm.chat_json(messages, DealMemo, max_tokens=600)
        except llm.LLMError as exc:
            log.warning("Judge failed, using fallback memo: %s", exc)
            break
        memo.reasons = memo.reasons[:3]
        if not leaks(_text(memo), secrets):
            return memo
        log.info("Memo contained a secret term, regenerating")
    return fallback_memo(a, b, turns)


TRANSLATE = """Translate this startup deal memo into clear Modern Standard Arabic for a Gulf business audience.
- Translate every string value. Keep the JSON keys, the "verdict" value and the "score" number unchanged.
- Keep people's names, company names and amounts (like $1.5M) exactly as written, in Latin script.
- Keep the same number of items in every list. Do not add or remove information.
Reply with the translated JSON only."""


def translate_memo(memo: DealMemo, secret_terms: list[str]) -> DealMemo | None:
    """Arabic version of a memo, or None if the model fails or the translation leaks a secret."""
    from core.negotiation import leaks

    messages = [{"role": "system", "content": TRANSLATE},
                {"role": "user", "content": memo.model_dump_json()}]
    try:
        ar, _ = llm.chat_json(messages, DealMemo, max_tokens=1200)
    except llm.LLMError as exc:
        log.warning("Memo translation failed: %s", exc)
        return None
    # The structure must survive translation; the verdict and score are never translated.
    ar = ar.model_copy(update={"verdict": memo.verdict, "score": memo.score})
    if leaks(_text(ar), secret_terms):
        log.warning("Arabic memo contained a secret term; discarded")
        return None
    return ar
