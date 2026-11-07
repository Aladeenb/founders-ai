"""Matchmaker: search steps, deal-breakers, refinements, why-not answers and privacy, with models mocked."""

import json

import pytest

from core import intake, llm, matchmaker as mm, profiles, rerank
from core.terms import RawHire, RawRange, RawTerms, mark_private, to_terms

PRIVATE_FLOOR = "Valuation cannot go below $9M"


@pytest.fixture
def sid(monkeypatch):
    """A confirmed founder (Mariam) wanting an investor and an engineer, with a private $9M floor."""
    st = intake.start()
    s = intake.get_session(st["session_id"])
    s.role, s.confirmed = "founder", True
    s.draft = profiles.Draft(
        display_name="Mariam Saleh", headline="Founder, Rota: route optimisation for last-mile fleets",
        public_bio="Rota is SaaS for last-mile delivery fleets in the GCC.", looking_for="A logistics investor and a backend engineer.",
        seeking=["investor", "engineer"], tags=["logistics", "last-mile", "SaaS"], location="Doha, Qatar", stage="seed",
        private_limits=[PRIVATE_FLOOR])
    s.raw_terms = mark_private(RawTerms(valuation=RawRange(low=9e6),
                                        hires=[RawHire(kind="engineer", salary=RawRange(high=115000), work=["hybrid"])]),
                               s.draft.private_limits)
    s.terms = to_terms(s.raw_terms)
    return st["session_id"]


@pytest.fixture
def models(monkeypatch):
    """Fake reranker (keeps order) and fake LLM that records every prompt."""
    prompts = []
    monkeypatch.setattr(rerank, "scores", lambda q, ps: [1 - i * 0.05 for i in range(len(ps))])
    monkeypatch.setattr(mm.matching, "vectors", lambda p: None)          # tag-overlap ranking, no network

    def fake(messages, schema, max_tokens=0, timeout=0):
        prompts.append(json.dumps(messages, ensure_ascii=False))
        if schema is mm._Fits:
            ids = [c["id"] for c in json.loads(messages[1]["content"])["candidates"]]
            return schema(matches=[{"id": i, "fit": "strong", "reason": f"Reason for {i}."} for i in ids]), "fake"
        if schema is mm._Questions:
            return schema(questions=["q1", "q2", "q3"]), "fake"
        return schema.model_validate(fake.next), "fake"

    fake.next = {}
    monkeypatch.setattr(llm, "chat_json", fake)
    return fake, prompts


def run(gen):
    steps = list(gen)
    return steps, steps[-1][1]


def test_search_reports_real_counts_and_both_roles(sid, models):
    steps, done = run(mm.find(sid))
    kinds = [k for k, _ in steps]
    assert kinds[:2] == ["read", "scan"] and kinds[-1] == "done"
    for _, d in (s for s in steps if s[0] == "filter"):
        assert d["kept"] >= 0 and d["dropped"] >= 0
    roles = {m.profile.role for m in done["matches"]}
    assert roles == {"investor", "engineer"}        # each wanted role gets its share


def test_deal_breakers_remove_and_explain_safely(sid, models):
    fake, _ = models
    run(mm.find(sid))
    fake.next = {"action": "why_not", "person": "Maya"}       # Maya's private $8M cap < Mariam's $9M floor
    *_, (kind, data) = list(mm.chat(sid, "why not Maya?"))
    assert data["text"].endswith("Not a match based on their preferences.") and "8" not in data["text"]


def test_no_private_limits_in_any_prompt(sid, models):
    fake, prompts = models
    run(mm.find(sid))
    fake.next = {"action": "questions", "person": "Ali"}
    list(mm.chat(sid, "what should I ask Ali?"))
    blob = " ".join(prompts)
    assert "9M" not in blob and PRIVATE_FLOOR not in blob
    assert "Will not invest above" not in blob           # nobody else's private limits either


def test_refinement_narrows_on_top_of_deal_breakers(sid, models):
    fake, _ = models
    run(mm.find(sid))
    fake.next = {"action": "refine", "roles": ["investor"]}
    steps = list(mm.chat(sid, "only investors"))
    labels = [d["label"] for k, d in steps if k == "filter"]
    assert any("deal-breakers" in l for l in labels) and any("investors only" in l for l in labels)
    assert all(m["role"] == "investor" for m in steps[-1][1]["matches"])


def test_reranker_down_falls_back_to_embeddings(sid, models, monkeypatch):
    monkeypatch.setattr(rerank, "scores", lambda q, ps: None)
    steps, done = run(mm.find(sid))
    assert next(d for k, d in steps if k == "rerank")["by"] == "embeddings" and done["matches"]


def test_similar_excludes_the_anchor_and_keeps_its_role(sid, models):
    fake, _ = models
    run(mm.find(sid))
    fake.next = {"action": "similar", "person": "Ali Hassan"}
    *_, (kind, data) = list(mm.chat(sid, "more like Ali"))
    assert data["matches"] and all(m["id"] != "i-ali" and m["role"] == "investor" for m in data["matches"])


def test_why_not_unknown_and_shown(sid, models):
    fake, _ = models
    _, done = run(mm.find(sid))
    fake.next = {"action": "why_not", "person": "Zebedee Nobody"}
    assert "couldn't find" in list(mm.chat(sid, "why not Zebedee?"))[-1][1]["text"]
    first = done["matches"][0].profile.display_name
    fake.next = {"action": "why_not", "person": first}
    assert "already on your list" in list(mm.chat(sid, f"why not {first}?"))[-1][1]["text"]


def test_draft_intro_is_short(sid, models):
    fake, _ = models
    run(mm.find(sid))
    fake.next = {"intro": "word " * 200}
    assert len(mm.draft_intro(sid, "i-ali").split()) <= 120


def test_chat_failure_is_polite(sid, models, monkeypatch):
    run(mm.find(sid))
    monkeypatch.setattr(llm, "chat_json", lambda *a, **k: (_ for _ in ()).throw(llm.LLMError("busy")))
    assert "trouble reaching the AI service" in list(mm.chat(sid, "hmm"))[-1][1]["text"]
    # Common requests still work from code while the model is down.
    assert "I looked at" in list(mm.chat(sid, "why these?"))[-1][1]["text"]
    assert "Maya" in list(mm.chat(sid, "why not Maya?"))[-1][1]["text"]


def test_cache_replays_identical_calls(tmp_path, monkeypatch):
    from core import cache
    monkeypatch.setenv("AI_CACHE_DIR", str(tmp_path))
    calls = []

    class FakeClient:
        pass

    monkeypatch.setattr(llm, "_client", lambda timeout=0: FakeClient())
    monkeypatch.setattr(llm, "_complete", lambda *a, **k: calls.append(1) or '{"questions": ["a", "b", "c"]}')
    msgs = [{"role": "user", "content": "same input"}]
    first, _ = llm.chat_json(msgs, mm._Questions)
    second, _ = llm.chat_json(msgs, mm._Questions)
    assert first == second and len(calls) == 1
    llm.chat_json([{"role": "user", "content": "different"}], mm._Questions)
    assert len(calls) == 2


def test_plain_english_stages():
    from core.matching import _stages
    assert _stages("early stage") == {"pre-seed", "seed"}
    assert _stages("software") == set()          # unreadable -> unknown, never a mismatch


def investor_sid(stages="early stage", must=None):
    st = intake.start()
    s = intake.get_session(st["session_id"])
    s.role, s.confirmed = "investor", True
    s.draft = profiles.Draft(display_name="Mohamed", headline="VC in Qatar", looking_for="Early-stage software startups.",
                             seeking=["founder"], tags=["software", "SaaS"], location="Doha, Qatar",
                             public_terms={"stages": stages, "cheque_size": "$1M"})
    s.raw_terms = RawTerms(other=must or [])
    s.terms = to_terms(s.raw_terms)
    return st["session_id"]


def test_early_stage_investor_finds_founders(models):
    _, done = run(mm.find(investor_sid()))
    assert done["matches"] and not done["message"]


def test_zero_results_are_explained_and_widen_relaxes_stage(models):
    fake, _ = models
    sid = investor_sid(stages="series b")                    # no seed founder is at Series B
    _, done = run(mm.find(sid))
    assert not done["matches"] and "emptied the list" in done["message"] and "other stages" in done["message"]
    fake.next = {"action": "widen"}
    *_, (kind, data) = list(mm.chat(sid, "yes widen it"))
    assert data["matches"] and "other stages" in data["text"]


def test_must_haves_reach_the_fit_check(models):
    _, prompts = models
    run(mm.find(investor_sid(must=["MRR of at least $30k", "must be profitable"])))
    assert any("must be profitable" in p and "viewer_must_haves" in p for p in prompts)


def test_empty_refinement_never_prints_empty_brackets(models):
    fake, _ = models
    sid = investor_sid(stages="series b")
    run(mm.find(sid))
    fake.next = {"action": "refine"}
    text = list(mm.chat(sid, "founders please"))[-1][1]["text"]
    assert "()" not in text


def test_must_have_cap_is_enforced_in_code():
    assert mm._cap("strong", "not_stated", True) == "possible"
    assert mm._cap("strong", "not_met", True) == "weak"
    assert mm._cap("strong", "met", True) == "strong"
    assert mm._cap("strong", "none", False) == "strong"


def test_false_number_comparisons_are_caught():
    assert mm._false_comparison("His typical cheque size ($1M–$2M) is larger than your $1.5M round.")
    assert mm._false_comparison("Cheque of $1M-$2M may exceed your $1.5M seed target.")
    assert not mm._false_comparison("The $2M raise is above your $500k-$1M cheque range.")     # true claim
    assert not mm._false_comparison("Salary range is $100k–$130k and he prefers Doha.")       # no comparison
    assert mm._clean_summary(["a", "Cheque $1M–$2M is larger than your $1.5M round.", "c"])[1] == \
        "Nothing obvious from the profiles."
