from core import dialects


def test_fusha_slips_found():
    found = dict(dialects.slips("إحنا عايزين نعرف إزاي ده هيمشي", "fusha"))
    assert {"إحنا", "عايزين", "إزاي", "ده"} <= set(found)


def test_fusha_examples_are_clean():
    for line in dialects.STYLE["fusha"][1]:
        assert dialects.slips(line, "fusha") == [], line


def test_other_languages_unchecked():
    assert dialects.slips("anything goes", "en") == []
