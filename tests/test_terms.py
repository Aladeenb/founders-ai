"""Deal-breakers in code: currency conversion, private marking, compatibility, safe explanations."""

from core import storage, terms
from core.schemas import Hire, Profile, Range, Terms
from core.terms import RawRange, RawTerms


def person(pid, role, t, name="Test Person"):
    return Profile(id=pid, display_name=name, role=role, headline="h", public_bio="", looking_for="x", terms=t)


def test_pegged_currencies_and_monthly_salary():
    r = terms.to_range(RawRange(low=27000, currency="QAR", period="month"))
    assert r.currency == "USD" and round(r.low) == round(27000 * 12 / 3.64)
    assert terms.to_range(RawRange(high=37500, currency="SAR")).high == 10000
    eur = terms.to_range(RawRange(low=80000, currency="EUR"))
    assert eur.currency == "EUR" and eur.low == 80000          # not pegged: kept, never compared with USD


def test_private_bounds_are_marked_by_code():
    raw = RawTerms(valuation=RawRange(low=10_000_000), salary=RawRange(low=90_000, high=120_000))
    terms.mark_private(raw, ["Will not accept below $10M", "Minimum $90k"])
    assert raw.valuation.low_private and raw.salary.low_private and not raw.salary.high_private


def test_work_modes_are_normalised():
    raw = RawTerms.model_validate({"work": ["Remote-friendly", "On-site", "something else"]})
    assert raw.work == ["remote", "onsite"]


def test_valuation_floor_vs_ceiling():
    f = person("f1", "founder", Terms(valuation=Range(low=10e6, low_private=True)), "Layla A")
    ok = person("i1", "investor", Terms(valuation=Range(high=14e6, high_private=True)), "Nadia B")
    low = person("i2", "investor", Terms(valuation=Range(high=8e6, high_private=True)), "Maya C")
    assert terms.conflicts(f, ok) == []
    (c,) = terms.conflicts(f, low)
    assert terms.explain(c) == "Not a match based on their preferences."   # Maya's ceiling is private


def test_public_reason_is_explained():
    talent = person("t1", "engineer", Terms(salary=Range(low=105e3, low_private=True)), "Ravi M")
    founder = person("f2", "founder", Terms(hires=[Hire(kind="engineer", salary=Range(high=100e3))]), "Ahmed R")
    (c,) = terms.conflicts(talent, founder)
    assert "Ahmed's role offers up to $100k" in terms.explain(c)
    # From the founder's side, Ravi's minimum is private, so it is never explained.
    (c2,) = terms.conflicts(founder, talent)
    assert terms.explain(c2) == "Not a match based on their preferences."


def test_any_matching_role_is_enough():
    talent = person("t2", "engineer", Terms(salary=Range(low=120e3), work=["remote"]))
    founder = person("f3", "founder", Terms(hires=[
        Hire(kind="engineer", salary=Range(high=100e3), work=["remote"]),
        Hire(kind="engineer", salary=Range(high=150e3), work=["remote"])]))
    assert terms.conflicts(talent, founder) == []


def test_unknown_terms_never_rule_out():
    a = person("t3", "engineer", Terms(salary=Range(low=80e3, currency="EUR")))
    b = person("f4", "founder", Terms(hires=[Hire(kind="engineer", salary=Range(high=50e3))]))
    assert terms.conflicts(a, b) == []                                    # EUR vs USD: not compared
    assert terms.conflicts(a, person("f5", "founder", None)) == []


def test_seed_demo_pairs():
    g = storage.get_profile
    assert terms.conflicts(g("f-layla"), g("i-nadia")) == []
    assert terms.conflicts(g("t-ravi"), g("f-reem")) == []
    fields = {c.field for c in terms.conflicts(g("t-sara"), g("f-karim"))}
    assert "work" in fields
    assert all(terms.explain(c) != c.detail for c in terms.conflicts(g("f-layla"), g("i-maya")))


def test_units_are_fixed_from_the_members_words():
    raw = RawTerms(hires=[{"kind": "engineer", "salary": {"high": 35000}}], salary=RawRange(low=27000))
    terms.fix_units(raw, "For the engineer I can pay up to 35,000 riyals a month", "Doha, Qatar")
    assert raw.hires[0].salary.currency == "QAR" and raw.hires[0].salary.period == "month"
    terms.fix_units(raw, "لن أقبل بأقل من 27 ألف ريال شهريًا", "Doha, Qatar")
    assert raw.salary.currency == "QAR" and raw.salary.period == "month"
    usd = RawTerms(salary=RawRange(low=140000))
    terms.fix_units(usd, "Minimum salary $140,000 a year")
    assert usd.salary.currency == "USD" and usd.salary.period is None
    sar = RawTerms(salary=RawRange(low=20000))
    terms.fix_units(sar, "at least 20k riyals per month", "Riyadh, Saudi Arabia")
    assert sar.salary.currency == "SAR"
