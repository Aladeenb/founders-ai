import pytest
from pydantic import ValidationError

from core import matching, storage
from core.schemas import AgentTurn, DealMemo, Negotiation, Profile


def prof(pid, role, **kw):
    return Profile(id=pid, display_name=pid, role=role, headline="", public_bio="", looking_for="x", **kw)


def test_seed_data_shape():
    seeds = storage.seed_profiles()
    roles = [p.role for p in seeds]
    assert len(seeds) == 61 and roles.count("founder") == 22 and roles.count("investor") == 19
    assert len({p.id for p in seeds}) == len(seeds)
    assert all(p.id[:2] in ("f-", "i-", "t-") for p in seeds)  # storage relies on these prefixes
    assert all(not s.startswith(("f-", "i-", "t-")) for s in ["u-x"])
    assert all(p.is_demo for p in seeds)


def test_allowed_pairs():
    f, i, e, o = prof("f", "founder"), prof("i", "investor"), prof("e", "engineer"), prof("o", "operator")
    assert matching.pair_allowed(f, i) and matching.pair_allowed(e, f) and matching.pair_allowed(f, o)
    assert not matching.pair_allowed(i, e) and not matching.pair_allowed(e, o) and not matching.pair_allowed(f, f)
    assert not matching.pair_allowed(prof("f2", "founder"), f)


def test_seeking_restricts_pairs():
    f = prof("f", "founder", seeking=["investor"])
    assert matching.pair_allowed(f, prof("i", "investor"))
    assert not matching.pair_allowed(f, prof("e", "engineer"))


def test_stage_mismatch_filtered():
    f = prof("f", "founder", stage="series a")
    i = prof("i", "investor", public_terms={"stages": "pre-seed, seed"})
    assert matching.clear_mismatch(f, i)
    assert not matching.clear_mismatch(prof("f", "founder", stage="seed"), i)


def test_rank_falls_back_without_embeddings(monkeypatch):
    monkeypatch.setattr(matching, "vectors", lambda p: None)
    layla = storage.get_profile("f-layla")
    ranked = matching.rank(layla)
    assert ranked and all(p.role == "investor" for p, _ in ranked)


def test_public_view_hides_private_fields():
    view = storage.get_profile("f-layla").public_view()
    assert "private_limits" not in view and "secret_terms" not in view


def test_storage_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    p = prof("u-1", "engineer", private_limits=["secret"])
    storage.save_profile(p)
    assert storage.get_profile("u-1") == p
    n = Negotiation(id="n-1", profile_a_id="u-1", profile_b_id="f-layla",
                    turns=[AgentTurn(speaker_id="u-1", message="hi")])
    storage.save_negotiation(n)
    assert storage.load_negotiation("n-1") == n
    assert not list(tmp_path.rglob("*.tmp"))
    storage.reset_demo_progress()
    assert storage.load_negotiation("n-1") is None


def test_seed_profiles_read_only():
    with pytest.raises(ValueError):
        storage.save_profile(storage.get_profile("f-layla"))


def test_llm_output_validation():
    assert AgentTurn.model_validate({"speaker_id": "a", "message": "hi", "stage": "opening"})
    with pytest.raises(ValidationError):
        AgentTurn.model_validate({"speaker_id": "a", "message": "hi", "stage": "bargaining"})
    with pytest.raises(ValidationError):
        DealMemo.model_validate({"verdict": "worth_meeting", "score": 140, "reasons": []})


def test_every_secret_term_appears_in_a_limit():
    from core import negotiation
    for p in storage.seed_profiles():
        limits = " ".join(p.private_limits)
        for term in p.secret_terms:
            assert negotiation.leaks(limits, [term]), (p.id, term)


def test_fit_check_drops_weak_and_caps_possible(monkeypatch):
    layla = storage.get_profile("f-layla")
    nadia, hamad, khalid = (storage.get_profile(i) for i in ("i-nadia", "i-hamad", "i-khalid"))
    monkeypatch.setattr(matching, "rank", lambda v, pool=None, k=3: [(nadia, 100), (khalid, 90), (hamad, 88)])
    monkeypatch.setattr(matching, "fit_check", lambda v, c: {
        "i-nadia": ("strong", "a"), "i-khalid": ("weak", ""), "i-hamad": ("possible", "c")})
    shown = matching.top_matches(layla)
    assert [m.profile.id for m in shown] == ["i-nadia", "i-hamad"]
    assert shown[0].score == 100 and shown[1].fit == "possible" and 50 <= shown[1].score <= 74


def test_score_bands_match_labels():
    assert matching.banded(47, "strong") >= 75 and matching.banded(100, "possible") == 74
    assert matching.banded(0, "possible") == 50


def test_strong_always_ranks_above_possible(monkeypatch):
    a, b = storage.get_profile("i-nadia"), storage.get_profile("i-hamad")
    monkeypatch.setattr(matching, "rank", lambda v, pool=None, k=3: [(a, 90), (b, 50)])
    monkeypatch.setattr(matching, "fit_check", lambda v, c: {"i-nadia": ("possible", "x"), "i-hamad": ("strong", "y")})
    assert [m.profile.id for m in matching.top_matches(storage.get_profile("f-layla"))] == ["i-hamad", "i-nadia"]


def test_fallback_fit_uses_tag_overlap():
    layla = storage.get_profile("f-layla")
    assert matching.fallback_fit(layla, storage.get_profile("i-nadia")) == "strong"
    assert matching.fallback_fit(layla, storage.get_profile("i-khalid")) == "weak"


def test_search_streams_every_step(monkeypatch):
    monkeypatch.setattr(matching, "fit_check", lambda v, c: {p.id: ("weak", "no") for p in c} | {"i-nadia": ("strong", "yes")})
    layla = storage.get_profile("f-layla")
    events = list(matching.search(layla))
    kinds = [k for k, _ in events]
    assert kinds[:2] == ["read", "scan"] and kinds.count("filter") == 3 and kinds[-1] == "done"
    scan = events[1][1]["total"]
    kept = [d["kept"] for k, d in events if k == "filter"]
    assert scan > kept[0] >= kept[1] >= kept[2]  # each filter only narrows the pool
    fits = [d for k, d in events if k == "fit"]
    assert len(fits) == len(events[kinds.index("ranked")][1]["shortlist"])
    assert [m.profile.id for m in events[-1][1]["matches"]] == ["i-nadia"]


def test_search_with_frozen_fits_makes_no_llm_call(monkeypatch):
    monkeypatch.setattr(matching, "fit_check", lambda v, c: (_ for _ in ()).throw(AssertionError("LLM called")))
    frozen = {"i-nadia": ("strong", "yes")}
    out = [d for k, d in matching.search(storage.get_profile("f-layla"), frozen_fits=frozen) if k == "done"][0]
    assert out["matches"][0].profile.id == "i-nadia"
