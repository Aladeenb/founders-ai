"""Spelled-out numbers -> digits, so the leak check catches "ten million" and "عشرة ملايين".

Covers English plus Modern Standard Arabic, Egyptian and Gulf forms for the numbers
people use in deal talk: 1-99, hundreds, halves, and duals like مليونين (two million).
Output keeps multiplier words ("million", "thousand") for normalize() to expand.
"""

from __future__ import annotations

import re

_W = r"(?<![\w])"   # word start (works for Arabic letters too)
_E = r"(?![\w])"    # word end

EN_UNITS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19}
EN_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}

# Arabic: MSA, Egyptian (EG) and Gulf (GU) spellings.
AR_WORDS = {
    1: ["واحد", "واحدة"],
    2: ["اثنين", "اثنان", "إثنين", "اتنين", "ثنين"],
    3: ["ثلاثة", "ثلاث", "تلاتة", "تلات", "ثلاثه"],
    4: ["أربعة", "اربعة", "أربع", "اربع", "اربعه"],
    5: ["خمسة", "خمس", "خمسه"],
    6: ["ستة", "ست", "سته"],
    7: ["سبعة", "سبع", "سبعه"],
    8: ["ثمانية", "ثماني", "ثمان", "تمانية", "تمنية", "تمن", "ثمن"],
    9: ["تسعة", "تسع", "تسعه"],
    10: ["عشرة", "عشر", "عشره"],
    11: ["أحد عشر", "احد عشر", "حداشر", "احدعش", "إحدعش"],
    12: ["اثنا عشر", "اثني عشر", "اتناشر", "اثنعش", "ثنعش"],
    13: ["ثلاثة عشر", "تلتاشر", "ثلطعش", "ثلاطعش"],
    14: ["أربعة عشر", "اربعة عشر", "اربعتاشر", "اربعطعش"],
    15: ["خمسة عشر", "خمستاشر", "خمسطعش", "خمسطاش"],
    16: ["ستة عشر", "ستاشر", "سطعش"],
    17: ["سبعة عشر", "سبعتاشر", "سبعطعش"],
    18: ["ثمانية عشر", "تمنتاشر", "ثمنطعش"],
    19: ["تسعة عشر", "تسعتاشر", "تسعطعش"],
    20: ["عشرين", "عشرون"],
    30: ["ثلاثين", "ثلاثون", "تلاتين"],
    40: ["أربعين", "اربعين", "أربعون"],
    50: ["خمسين", "خمسون"],
    60: ["ستين", "ستون"],
    70: ["سبعين", "سبعون"],
    80: ["ثمانين", "ثمانون", "تمانين"],
    90: ["تسعين", "تسعون"],
    100: ["مئة", "مائة", "مية", "ميه", "ميت"],
    200: ["مئتين", "مئتان", "مائتين", "ميتين"],
}
_AR_HUNDREDS = r"(تلت|ثلاث|ربع|اربع|أربع|خمس|ست|سبع|تمن|ثمان|تسع)(مية|مئة|مائة|ميه)"
_AR_HUNDRED_UNITS = {"تلت": 3, "ثلاث": 3, "ربع": 4, "اربع": 4, "أربع": 4, "خمس": 5, "ست": 6, "سبع": 7,
                     "تمن": 8, "ثمان": 8, "تسع": 9}


def _ar_word_pattern() -> list[tuple[re.Pattern, int]]:
    pairs = [(w, n) for n, words in AR_WORDS.items() for w in words]
    pairs.sort(key=lambda p: -len(p[0]))  # longest first: "خمسة عشر" before "خمسة"
    # Optional conjunction/preposition prefix: و (and), ب (with/for), بـال
    return [(re.compile(_W + r"(و|ب|ل)?" + re.escape(w) + _E), n) for w, n in pairs]


_AR_PATTERNS = _ar_word_pattern()


def _merge(t: str) -> str:
    """Join number pieces: 'five and ninety' -> 95, 'hundred and twenty' -> 120, 'ninety five' -> 95."""
    def ar_sum(m: re.Match) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        if (a < 10 and b % 10 == 0 and 20 <= b < 100) or (a % 100 == 0 and b < 100) or (a % 1000 == 0 and b < 1000):
            return str(a + b)
        return m.group(0)

    def en_sum(m: re.Match) -> str:
        a, b = int(m.group(1)), int(m.group(2))
        return str(a + b) if a % 10 == 0 and 20 <= a < 100 and b < 10 else m.group(0)

    for _ in range(3):
        t = re.sub(r"(\d+) و (\d+)", ar_sum, t)
        t = re.sub(r"(\d+)(?: and | )(\d+)(?!\d)", ar_sum, t)  # "100 and 20", "100 20"
        t = re.sub(r"(\d+)[ -](\d)(?!\d)", en_sum, t)
    return t


def words_to_digits(text: str) -> str:
    t = text

    # English
    t = re.sub(r"\bhalf a million\b", "500000", t)
    t = re.sub(r"\ba (million|thousand|hundred)\b", r"1 \1", t)
    for w, n in {**EN_UNITS, **EN_TENS}.items():
        t = re.sub(rf"\b{w}\b", str(n), t)
    t = re.sub(r"(\d+) hundred\b", lambda m: str(int(m.group(1)) * 100), t)
    t = re.sub(r"(\d+)(?: and a half| and half) (million|thousand)", lambda m: f"{int(m.group(1)) + 0.5:g} {m.group(2)}", t)

    # Arabic duals and glued hundreds
    t = re.sub(_W + r"(و|ب)?مليونين" + _E, lambda m: f" {'و ' if m.group(1) == 'و' else ''}2 مليون ", t)
    t = re.sub(_W + r"(و|ب)?(ألفين|الفين)" + _E, lambda m: f" {'و ' if m.group(1) == 'و' else ''}2 ألف ", t)
    t = re.sub(_W + r"(و|ب)?" + _AR_HUNDREDS + _E,
               lambda m: f" {'و ' if m.group(1) == 'و' else ''}{_AR_HUNDRED_UNITS[m.group(2)] * 100} ", t)
    for pattern, n in _AR_PATTERNS:
        t = pattern.sub(lambda m, n=n: f" {'و ' if m.group(1) == 'و' else ''}{n} ", t)

    # A bare "million"/"thousand" with no number in front means one; "and a half" adds 0.5.
    t = re.sub(r"(^|[^\d\s])\s*(مليون|ألف|الف)" + _E, r"\1 1 \2", t)
    t = re.sub(r"(\d+(?:\.\d+)?)\s*(مليون|ألف|الف)\s*و\s?(نص|نصف)" + _E,
               lambda m: f"{float(m.group(1)) + 0.5:g} {m.group(2)}", t)

    t = re.sub(r"\s+", " ", t)
    return _merge(t)
