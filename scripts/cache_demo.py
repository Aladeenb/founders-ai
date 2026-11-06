"""Run the three demo negotiations live and save good runs to data/demo_cache/.

    .venv/bin/python scripts/cache_demo.py            # run all three, save if clean
    .venv/bin/python scripts/cache_demo.py f-layla    # just one path
    .venv/bin/python scripts/cache_demo.py translate  # add Arabic memos to existing saved runs
    .venv/bin/python scripts/cache_demo.py f-layla --lang fusha      # save an Arabic run
    .venv/bin/python scripts/cache_demo.py presenter  # freeze demo matches and save a run for every one of them
"""

from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from core import matching, memo, negotiation, storage  # noqa: E402

PATHS = [("f-layla", "i-nadia"), ("i-omar", "f-yusuf"), ("t-sara", "f-karim")]
PRESENTER_PERSONAS = ["f-layla", "i-omar", "t-sara", "t-ravi"]


def main(only: list[str], lang: str = "en", pairs: list[tuple[str, str]] | None = None) -> None:
    negotiation.CACHE_DIR.mkdir(exist_ok=True)
    for a_id, b_id in pairs or PATHS:
        if only and a_id not in only:
            continue
        a, b = storage.get_profile(a_id), storage.get_profile(b_id)
        print(f"\n=== {a.display_name} -> {b.display_name}")
        result = None
        for kind, payload in negotiation.run(a, b, lang=lang):
            if kind == "turn":
                who = a if payload.speaker_id == a.id else b
                flag = " [LEAK CAUGHT, rewritten]" if payload.leak_caught else ""
                print(f"[{payload.stage:11s}] {who.display_name.split()[0]}: {payload.message}{flag}")
                print(f"{'':14s}(thought: {payload.private_thought})")
            elif kind == "done":
                result = payload
        # Never cache a run whose displayed text leaked anything.
        leaked = [t for t in result.turns
                  if negotiation.leaks(t.message, (a if t.speaker_id == a.id else b).secret_terms)]
        if result.status == "complete" and result.memo and not leaked:
            result.memo_ar = memo.translate_memo(result.memo, [*a.secret_terms, *b.secret_terms])
            negotiation.cache_path(a_id, b_id, lang).write_text(result.model_dump_json(indent=2), encoding="utf-8")
            print(f"--> saved {len(result.turns)} turns")
        else:
            print(f"--> NOT saved (status={result.status}, leaks={len(leaked)})")


def presenter() -> None:
    """Freeze matches for the presenter personas, then save a clean run for every match that lacks one."""
    data = matching.save_presenter_matches(PRESENTER_PERSONAS)
    for pid, ms in data.items():
        print(f"{pid}: " + ", ".join(f"{m['id']} {m['score']} {m['fit']}" for m in ms))
    missing = [(a, m["id"]) for a, ms in data.items() for m in ms if not negotiation.has_presenter_run(a, m["id"])]
    print(f"\nSaving {len(missing)} missing runs: {missing}")
    if missing:  # an empty list must not fall back to re-recording the default demo paths
        main([], "en", missing)


def translate_existing() -> None:
    for path in sorted(negotiation.CACHE_DIR.glob("*.json")):
        neg = negotiation.Negotiation.model_validate_json(path.read_text(encoding="utf-8"))
        if neg.memo is None or neg.memo_ar is not None:
            print(f"{path.name}: skipped")
            continue
        a, b = storage.get_profile(neg.profile_a_id), storage.get_profile(neg.profile_b_id)
        neg.memo_ar = memo.translate_memo(neg.memo, [*a.secret_terms, *b.secret_terms])
        path.write_text(neg.model_dump_json(indent=2), encoding="utf-8")
        print(f"{path.name}: {'translated' if neg.memo_ar else 'FAILED'}")


if __name__ == "__main__":
    if sys.argv[1:] == ["translate"]:
        translate_existing()
    elif sys.argv[1:] == ["presenter"]:
        presenter()
    else:
        args = sys.argv[1:]
        lang = "en"
        if "--lang" in args:
            i = args.index("--lang")
            lang, args = args[i + 1], args[:i] + args[i + 2:]
        main(args, lang)
