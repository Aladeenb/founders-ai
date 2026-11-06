"""One-off: turn each seed profile's written terms and private limits into structured terms.

Writes data/seed_terms.json ({id: {"terms": Terms, "offers": str}}). Seed profiles are not modified.
Run:  .venv/bin/python scripts/extract_seed_terms.py
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from pydantic import BaseModel  # noqa: E402

from core import llm, storage, terms  # noqa: E402
from core.terms import RawTerms  # noqa: E402

PROMPT = terms_prompt = """Turn this startup ecosystem member's terms into structured numbers for a deal-breaker check.
Use ONLY what is written. Use null when something is not stated. Numbers in full units (10M -> 10000000, 95k -> 95000).
Mark a bound *_private=true when it comes from private_limits, false when it comes from public_terms.

Role rules:
- founder: valuation.low = the lowest pre-money valuation or cap they accept (private floor if given, else the low end of
  their public range); valuation.high = null. hires = one entry per role they are hiring for (kind engineer or operator),
  with salary.high = the most they can pay (private stretch if given, else the public top), equity.high = the most equity
  offered, work = the role's work modes.
- investor: valuation.high = the highest valuation or cap they invest at (private ceiling); valuation.low = null.
- engineer / operator: salary.low = their minimum (private if given, else the public low end), equity.low = minimum equity
  percent if stated, work = the work modes they accept (remote, hybrid, onsite).
- Salaries are annual unless stated per month (then period="month"). Keep the currency as written (USD, EUR, QAR...).
- Equity is in percentage points: 1% -> 1, 0.5% -> 0.5, 1.5% -> 1.5. Never write 1% as 0.01.
- other: deal-breakers that are not numbers or work modes (e.g. "needs visa sponsorship", "wants a board seat").
- offers: one short sentence on what this person gives others (money, pilots, introductions, skills), from the profile.
Reply with JSON: {"terms": {"valuation": null, "hires": [], "salary": null, "equity": null, "work": [], "other": []},
"offers": ""}"""


class _Out(BaseModel):
    terms: RawTerms
    offers: str = ""


def extract(p) -> tuple[str, dict]:
    data = {"role": p.role, "headline": p.headline, "public_bio": p.public_bio, "looking_for": p.looking_for,
            "public_terms": p.public_terms, "private_limits": p.private_limits}
    out, _ = llm.chat_json([{"role": "system", "content": PROMPT},
                            {"role": "user", "content": json.dumps(data, ensure_ascii=False)}], _Out, max_tokens=700,
                           timeout=40)
    raw = terms.mark_private(out.terms, p.private_limits)
    return p.id, {"terms": terms.to_terms(raw).model_dump(), "offers": out.offers.strip()}


def main() -> None:
    seeds = storage.seed_profiles()
    with ThreadPoolExecutor(max_workers=8) as pool:
        result = dict(pool.map(extract, seeds))
    terms.SEED_TERMS_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Wrote {len(result)} entries to {terms.SEED_TERMS_FILE}")


if __name__ == "__main__":
    main()
