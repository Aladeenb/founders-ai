import pytest

from core import negotiation as neg
from core import profiles


def test_arabic_numbers_are_caught():
    assert neg.leaks("We can't accept below 6 million", ["٦ ملايين دولار"])
    assert neg.leaks("لن نقبل أقل من ٦ ملايين دولار", ["$6M"])
    assert neg.leaks("الحد الأدنى ١٥٪", ["15%"])
    assert not neg.leaks("We raised 16 million", ["٦ ملايين دولار"])


def test_amounts_in():
    assert profiles.amounts_in("Won't go below $90k and need 0.5% equity") == ["$90k", "0.5%"]
    assert profiles.amounts_in("Minimum €95,000") == ["€95,000"]
    assert profiles.amounts_in("On-site 2 days a week from 2027") == []


def test_derive_secret_terms_dedupes():
    assert profiles.derive_secret_terms(["Floor is $10M", "max 15%"], ["$10M"]) == ["$10M", "15%"]


def test_clean_drops_placeholder_limits():
    d = profiles._clean(profiles.Draft(private_limits=["No private limits specified."], seeking=["investors"]), "founder")
    assert d.private_limits == [] and d.seeking == ["investor"]


def test_non_founders_only_seek_founders():
    d = profiles._clean(profiles.Draft(seeking=["investor"], stage="seed"), "engineer")
    assert d.seeking == ["founder"] and d.stage is None


def test_terms_round_trip():
    terms = {"salary": "$80k–$100k", "work_style": "Hybrid: Doha"}
    assert profiles.text_to_terms(profiles.terms_to_text(terms)) == terms


def test_build_profile_validates_and_derives():
    with pytest.raises(ValueError, match="your name"):
        profiles.build_profile(profile_id=None, role="engineer", display_name="", headline="x", public_bio="",
                               looking_for="y", seeking=[], tags="", location="", stage=None, public_terms="",
                               private_limits="", secret_terms="")
    p = profiles.build_profile(profile_id="u-huda", role="engineer", display_name="Huda", headline="Engineer",
                               public_bio="", looking_for="A fintech", seeking=["investor"], tags="go, fintech",
                               location="Doha", stage="seed", public_terms="salary: $90k–$110k",
                               private_limits="Won't go below $95k", secret_terms="")
    assert p.secret_terms == ["$95k"] and p.seeking == ["founder"] and p.stage is None and not p.is_demo
    assert p.public_terms == {"salary": "$90k–$110k"} and p.tags == ["go", "fintech"]


def test_split_terms_keeps_thousands():
    assert profiles.split_terms("$105,000, 0.5%, pilot agreement") == ["$105,000", "0.5%", "pilot agreement"]


def test_secret_terms_dedupe_formats_and_drop_fragments():
    assert profiles.derive_secret_terms(["Minimum $105,000"], ["$105000", "0", "000"]) == ["$105000"]


# ---------- the profile form makes indexer-ready profiles ----------

from core import llm, matching, terms  # noqa: E402


def test_structured_terms_converts_and_marks_private():
    raw = terms.RawTerms.model_validate({"salary": {"low": 27000, "currency": "QAR"}, "work": ["remote only"]})
    t = profiles.structured_terms(raw, "I won't take less than 27k riyals a month", ["Not below 27k QAR a month"], "Doha")
    assert t.salary.low == round(27000 / 3.64 * 12, 2) and t.salary.currency == "USD"
    assert t.salary.low_private and t.salary.high_private and t.work == ["remote"]
    assert profiles.structured_terms(terms.RawTerms(), "", []) is None


def test_checked_lines_say_what_is_enforced():
    t = profiles.structured_terms(terms.RawTerms.model_validate(
        {"valuation": {"low": 10_000_000}, "hires": [{"title": "CTO", "salary": {"high": 150_000}}],
         "other": ["must be profitable"]}), "", [])
    assert profiles.checked_lines(t) == ["Valuation of at least $10M", "Pay up to $150k a year for CTO",
                                         "must be profitable"]
    assert profiles.checked_lines(None) == []


def test_extract_returns_offers_and_terms(monkeypatch):
    def fake(messages, schema, **_):
        assert "terms" in messages[0]["content"] and "offers" in messages[0]["content"]
        return schema.model_validate({"display_name": "Omar", "looking_for": "Seed healthtech", "offers":
                                      "Intros to Gulf hospitals", "terms": {"valuation": {"high": 12_000_000}}}), "m"
    monkeypatch.setattr(llm, "chat_json", fake)
    d = profiles.extract("investor", "I'm Omar, I back seed healthtech. Never above $12M valuation.")
    assert d.offers == "Intros to Gulf hospitals" and d.terms.valuation.high == 12_000_000


def test_extract_terms_rereads_edited_cards(monkeypatch):
    monkeypatch.setattr(llm, "chat_json", lambda m, schema, **_: (schema.model_validate({"salary": {"low": 95000}}), "m"))
    t = profiles.extract_terms("engineer", "salary: $90k–$110k", ["Won't go below $95k"])
    assert t.salary.low == 95000 and t.salary.low_private
    assert profiles.extract_terms("engineer", "", []) is None


def test_build_profile_keeps_offers_and_terms_for_the_matcher():
    t = profiles.structured_terms(terms.RawTerms.model_validate({"salary": {"low": 95000}}), "", [])
    p = profiles.build_profile(profile_id="u-huda", role="engineer", display_name="Huda", headline="Engineer",
                               public_bio="", looking_for="A fintech", seeking=[], tags="go", location="Doha",
                               stage=None, public_terms="", private_limits="", secret_terms="",
                               offers="  Payments infrastructure  ", terms=t)
    assert p.offers == "Payments infrastructure" and terms.terms_for(p) == t
    assert "Offers: Payments infrastructure" in matching.passage_text(p)
    assert "offers" in p.public_view() and "terms" not in p.public_view()


def test_salary_is_only_monthly_when_the_member_said_so():
    raw = lambda: terms.RawTerms.model_validate({"salary": {"low": 90000, "period": "month"}})
    t = profiles.structured_terms(raw(), "Privately, I won't go below $90k.", ["Minimum salary is $90,000."])
    assert t.salary.low == 90000
    t = profiles.structured_terms(raw(), "", ["At least 90,000 a month"])
    assert t.salary.low == 90000 * 12


def test_limits_and_checks_are_listed_once():
    t = profiles.structured_terms(terms.RawTerms.model_validate({"salary": {"low": 90000}, "work": ["remote"]}), "", [])
    assert profiles.limits_with_checks(["I won't go below $90k salary.", "No crypto companies"], t) == [
        ("I won't go below $90k salary.", True), ("No crypto companies", False), ("Work: remote only", True)]
    assert profiles.limits_with_checks(["Remote only"], t) == [("Remote only", True), ("Salary of at least $90k a year", True)]
    assert profiles.limits_with_checks([], None) == []
