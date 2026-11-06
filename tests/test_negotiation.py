import pytest

from core import negotiation as neg
from core.schemas import AgentTurn


@pytest.mark.parametrize("msg", [
    "We can't go below $10M pre-money.", "Ten is the floor: 10 million.", "Floor is 10,000,000 USD",
    "our minimum is 10m", "We need $10.0M at least",
])
def test_leak_detects_number_formats(msg):
    assert neg.leaks(msg, ["$10M"]) == ["$10M"]


@pytest.mark.parametrize("msg", [
    "Our public range is $8M–$12M.", "We have $100M in pipeline", "Raising $1.5M seed", "That is workable.",
])
def test_leak_ignores_other_numbers(msg):
    assert neg.leaks(msg, ["$10M"]) == []


def test_leak_other_formats():
    assert neg.leaks("I need at least 140k", ["$140k"])
    assert neg.leaks("max 15 percent dilution", ["15%"])
    assert not neg.leaks("max 150% growth", ["15%"])
    assert neg.leaks("Needs a PILOT AGREEMENT first", ["pilot agreement"])
    assert neg.leaks("€95,000 is possible", ["€95k"])


def test_normalize_keeps_words():
    assert neg.normalize("Market rate, remote") == "market rate, remote"


def test_stop_rules():
    t = lambda end: AgentTurn(speaker_id="x", message="m", wants_to_end=end)
    assert not neg._should_stop([t(True)] * 3)
    assert neg._should_stop([t(False), t(False), t(True), t(True)])
    assert not neg._should_stop([t(False), t(False), t(False), t(True)])
    assert neg._should_stop([t(False)] * 8)


def test_stage_only_moves_forward():
    assert neg._stage_after("negotiating", "opening") == "negotiating"
    assert neg._stage_after("exploring", "verdict") == "verdict"


def test_failed_live_run_replays_cache(monkeypatch, tmp_path):
    from core import llm, storage
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    def boom(*a, **k):
        raise llm.LLMError("down")

    monkeypatch.setattr(neg, "agent_turn", boom)
    a, b = storage.get_profile("t-sara"), storage.get_profile("f-karim")
    monkeypatch.setattr(neg.time, "sleep", lambda s: None)
    events = list(neg.run(a, b))
    kinds = [k for k, _ in events]
    assert "fallback" in kinds and kinds[-1] == "done"
    done = events[-1][1]
    assert done.status == "complete" and done.turns
    assert storage.load_negotiation(done.id) is not None


def test_cached_runs_never_leak():
    from core import storage
    for path in neg.CACHE_DIR.glob("*.json"):
        cached = neg.Negotiation.model_validate_json(path.read_text())
        for t in cached.turns:
            assert not neg.leaks(t.message, storage.get_profile(t.speaker_id).secret_terms), path.name


def _done_neg():
    return neg.Negotiation(id="n-x", profile_a_id="a", profile_b_id="b", status="complete")


def test_double_opt_in(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    n = _done_neg()
    assert neg.thread_state(n, "a") == "waiting_you"
    n = neg.decide(n, "a", "approved")
    assert neg.thread_state(n, "a") == "waiting_them" and neg.thread_state(n, "b") == "waiting_you"
    n = neg.decide(n, "b", "approved")
    assert neg.thread_state(n, "a") == "connected" == neg.thread_state(n, "b")


def test_decline_is_final(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    n = neg.decide(_done_neg(), "b", "declined")
    n = neg.decide(n, "a", "approved")
    assert neg.thread_state(n, "a") == "declined" and n.decision_a == "pending"


def test_cannot_decide_running_or_outsider():
    with pytest.raises(ValueError):
        neg.decide(neg.Negotiation(id="n", profile_a_id="a", profile_b_id="b"), "a", "approved")
    with pytest.raises(ValueError):
        neg.side_of(_done_neg(), "zzz")


def test_fallback_memo_detects_hard_no():
    from core import memo, storage
    a, b = storage.get_profile("t-sara"), storage.get_profile("f-karim")
    turns = [AgentTurn(speaker_id="f-karim", message="On-site is non-negotiable, so this is not workable.")]
    assert memo.fallback_memo(a, b, turns).verdict == "not_fit"
    assert memo.fallback_memo(a, b, [AgentTurn(speaker_id="x", message="Sounds workable")]).verdict == "maybe_later"


def _memo(**kw):
    from core.schemas import DealMemo
    base = dict(verdict="worth_meeting", score=80, reasons=["a", "b", "c"], intro_message="hi")
    return DealMemo(**{**base, **kw})


def test_translation_keeps_verdict_and_score(monkeypatch):
    from core import llm, memo
    monkeypatch.setattr(llm, "chat_json", lambda m, schema, **k: (_memo(verdict="not_fit", score=5,
                        reasons=["أ", "ب", "ج"], intro_message="مرحبا"), "x"))
    ar = memo.translate_memo(_memo(), ["$10M"])
    assert ar.verdict == "worth_meeting" and ar.score == 80 and ar.reasons == ["أ", "ب", "ج"]


def test_translation_that_leaks_is_discarded(monkeypatch):
    from core import llm, memo
    monkeypatch.setattr(llm, "chat_json", lambda m, schema, **k: (_memo(intro_message="الحد ١٠ ملايين دولار"), "x"))
    assert memo.translate_memo(_memo(), ["$10M"]) is None


def test_repeat_detection():
    t = [AgentTurn(speaker_id="a", message="Your cheque size fits and we recommend a meeting this week.")]
    assert neg._repeats("Your cheque size fits and we recommend a meeting this week!", t)
    assert not neg._repeats("What is your timeline for closing the round?", t)


def test_dialect_cache_falls_back_to_english():
    assert neg.load_cached("i-omar", "f-yusuf", "fusha").language == "en"


def test_repeat_detection_covers_whole_conversation():
    old = AgentTurn(speaker_id="b", message="The valuation range is workable and we could lead the round.")
    later = [AgentTurn(speaker_id="a", message=f"Different point number {i}") for i in range(4)]
    assert neg._repeats("The valuation range is workable and we could lead the round!", [old, *later])


def test_presenter_replays_saved_run_without_llm(monkeypatch, tmp_path):
    from core import llm, storage
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr(neg.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm, "chat_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no LLM in presenter")))
    a, b = storage.get_profile("f-layla"), storage.get_profile("i-nadia")
    events = list(neg.run(a, b, presenter=True))
    done = events[-1][1]
    assert done.status == "complete" and done.memo and "fallback" not in [k for k, _ in events]


def test_presenter_needs_exact_language():
    assert neg.has_presenter_run("f-layla", "i-nadia", "fusha")
    assert not neg.has_presenter_run("i-omar", "f-yusuf", "fusha")  # only English is saved for Omar
    assert neg.load_cached("i-omar", "f-yusuf", "fusha") is not None  # normal fallback still uses English


def test_not_now_snoozes_then_approve_clears(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    n = neg.decide(_done_neg(), "a", "later")
    assert neg.thread_state(n, "a") == "later" and neg.thread_state(n, "b") == "waiting_you"
    n = neg.decide(n, "a", "approved", note="Keen to meet next week")
    assert neg.thread_state(n, "a") == "waiting_them" and n.notes["a"] == "Keen to meet next week"
    assert "a" in n.decided_at and n.snoozed == []


def test_decide_keeps_other_sides_newer_decision(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    stale = _done_neg()
    neg.storage.save_negotiation(stale)
    neg.decide(stale, "b", "approved")
    n = neg.decide(stale, "a", "approved")  # stale copy must not erase b's approval
    assert neg.thread_state(n, "a") == "connected"
