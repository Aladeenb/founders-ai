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
