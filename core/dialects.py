"""Arabic (Modern Standard) style guide and a cheap check for slips into dialect.

The guide has a short instruction plus example sentences: examples steer register far
better than descriptions. slips() finds tell-tale dialect words so the agent can be
asked once to fix exactly those words.
"""

from __future__ import annotations

import re

STYLE = {
    # Examples use neutral topics (start dates, remote work, timing) so they never match a demo script.
    "fusha": (
        "Write the message in Modern Standard Arabic (الفصحى), in a formal, polite business register. "
        "Do not use dialect words.",
        ["شكرًا على التوضيح. هل يمكن أن يبدأ الدور عن بُعد ثم ننتقل إلى الحضور لاحقًا؟",
         "الجدول الزمني الذي ذكرتموه مناسب لنا، لكننا نحتاج إلى معرفة موعد اتخاذ القرار.",
         "يبدو أن هناك توافقًا جيدًا في أغلب النقاط. نقترح عقد اجتماع قصير لمناقشة ما تبقّى."]),
}

# dialect word -> Modern Standard replacement
SLIPS = {
    "fusha": {
        "مش": "ليس / لا", "عايز": "أريد", "عايزين": "نريد", "إزاي": "كيف", "شلون": "كيف", "وايد": "كثيرًا",
        "الحين": "الآن", "دلوقتي": "الآن", "ده": "هذا", "دي": "هذه", "إحنا": "نحن", "زين": "جيد",
        "نبي": "نريد", "مو": "ليس", "كده": "هكذا", "بتاع": "الخاص بـ", "شنو": "ماذا",
    },
}


def _word(w: str) -> re.Pattern:
    # Allow a leading و (and) or ب/ل/ف prefix, e.g. "وإحنا".
    return re.compile(rf"(?<!\w)[وفبل]?{re.escape(w)}(?!\w)")


_PATTERNS = {lang: [(w, _word(w), fix) for w, fix in words.items()] for lang, words in SLIPS.items()}


def slips(message: str, lang: str) -> list[tuple[str, str]]:
    """(dialect word, suggestion) pairs found in the message."""
    return [(w, fix) for w, pat, fix in _PATTERNS.get(lang, []) if pat.search(message)]


def instruction(lang: str) -> str:
    text, examples = STYLE[lang]
    return text + " Match the style of these examples (do not copy them): " + " | ".join(examples)


def fix_request(lang: str, found: list[tuple[str, str]]) -> str:
    swaps = "; ".join(f"{w} → {fix}" for w, fix in found)
    return (f"Some words in your message are dialect, not Modern Standard Arabic. Fix them: {swaps}. Keep the "
            "meaning, the numbers and everything else the same. Reply with the same JSON format.")
