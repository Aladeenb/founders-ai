import pytest

from core import negotiation as neg
from core.numwords import words_to_digits


@pytest.mark.parametrize("text, secret", [
    # English words
    ("Our floor is ten million", "$10M"),
    ("we need at least one hundred and forty thousand", "$140k"),
    ("ninety-five thousand is the max", "$95k"),
    ("one and a half million", "$1.5M"),
    ("half a million", "$500k"),
    # Fusha
    ("لا يمكننا قبول أقل من عشرة ملايين دولار", "$10M"),
    ("الحد الأقصى خمسة عشر بالمئة", "15%"),
    ("نحتاج مئة وأربعين ألف دولار", "$140k"),
    # Egyptian
    ("إحنا مش هننزل عن عشرة مليون", "$10M"),
    ("أقل حاجة خمستاشر في المية", "15%"),
    ("المرتب لازم يكون خمسة وتسعين ألف", "$95k"),
    ("مليون ونص", "$1.5M"),
    ("تلتمية ألف", "$300k"),
    # Khaleeji
    ("ما نقدر ننزل عن عشر ملايين", "$10M"),
    ("نبي خمسطعش بالمية", "15%"),
    ("الراتب ما يقل عن مية وأربعين ألف", "$140k"),
    ("مليونين", "$2M"),
    # digits mixed with Arabic
    ("١٠ ملايين", "$10M"),
])
def test_spelled_numbers_are_caught(text, secret):
    assert neg.leaks(text, [secret]), (text, neg.normalize(text))


@pytest.mark.parametrize("text, secret", [
    ("Our public range is eight to twelve million", "$10M"),
    ("We raised twenty million", "$10M"),
    ("نطاقنا العام من ثمانية إلى اثني عشر مليون", "$10M"),
    ("someone often mentions tenacity", "$10M"),
    ("ده كويس جدا ومناسب لينا", "$10M"),
])
def test_no_false_positives(text, secret):
    assert not neg.leaks(text, [secret]), (text, neg.normalize(text))


def test_ordinary_words_untouched():
    assert words_to_digits("someone often listens") == "someone often listens"
